#!/usr/bin/env python3
"""
Run selected-cell MYRORSS chronological batches from the committed batch plan.

This is a notebook-support utility, not production code. It wraps the executed notebook
`03_selected_cell_full_record_batches.ipynb`, passes one planned date window at a time through environment
variables, and skips batches whose metadata artifact already exists.

Examples:
  .venv/bin/python scripts/run_myrorss_selected_cell_batches.py --dry-run --max-batches 3
  .venv/bin/python scripts/run_myrorss_selected_cell_batches.py --start-batch 3 --max-batches 1
  .venv/bin/python scripts/run_myrorss_selected_cell_batches.py --start-batch 3 --end-batch 8
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_VERSION = "v2026_06_16"
PLAN_CSV = ROOT / "data" / "hazard_conus_grid" / "hail" / f"myrorss_m0_selected_cell_full_record_batch_plan_{OUTPUT_VERSION}.csv"
NOTEBOOK = (
    ROOT
    / "Notebooks"
    / "hail"
    / "m0_input_data"
    / "03_myrorss_reanalysis_source_qualification"
    / "03_selected_cell_full_record_batches.ipynb"
)
HAIL_DATA_DIR = ROOT / "data" / "hazard_conus_grid" / "hail"


@dataclass(frozen=True)
class Batch:
    batch_number: int
    batch_id: str
    batch_start: str
    batch_end: str
    n_days: int

    @property
    def label(self) -> str:
        return f"{self.batch_start.replace('-', '')}_{self.batch_end.replace('-', '')}"

    @property
    def metadata_path(self) -> Path:
        return HAIL_DATA_DIR / f"myrorss_m0_selected_cell_full_record_metadata_{self.label}_{OUTPUT_VERSION}.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-csv", type=Path, default=PLAN_CSV, help="Batch plan CSV produced by notebook 03.")
    parser.add_argument("--notebook", type=Path, default=NOTEBOOK, help="Notebook to execute for each batch.")
    parser.add_argument("--start-batch", type=int, default=1, help="1-based batch number to start from.")
    parser.add_argument("--end-batch", type=int, default=None, help="1-based batch number to stop at, inclusive.")
    parser.add_argument("--max-batches", type=int, default=None, help="Maximum number of not-yet-complete batches to run.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without executing notebooks.")
    parser.add_argument("--force", action="store_true", help="Re-run even if the metadata artifact already exists.")
    return parser.parse_args()


def load_batches(plan_csv: Path) -> list[Batch]:
    with plan_csv.open(newline="") as f:
        rows = list(csv.DictReader(f))
    batches: list[Batch] = []
    for row in rows:
        batch_id = row["batch_id"]
        try:
            batch_number = int(batch_id.rsplit("_", 1)[-1])
        except ValueError as exc:
            raise ValueError(f"Could not parse batch number from {batch_id}") from exc
        batches.append(
            Batch(
                batch_number=batch_number,
                batch_id=batch_id,
                batch_start=row["batch_start"],
                batch_end=row["batch_end"],
                n_days=int(row["n_days"]),
            )
        )
    return batches


def validate_metadata(batch: Batch) -> dict[str, object]:
    metadata = json.loads(batch.metadata_path.read_text())
    execution = metadata.get("execution_batch", {})
    coverage = metadata.get("scan_coverage", {})
    expected = {
        "batch_label": batch.label,
        "start": batch.batch_start,
        "end": batch.batch_end,
        "n_days": batch.n_days,
    }
    for key, value in expected.items():
        if execution.get(key) != value:
            raise ValueError(
                f"Metadata mismatch for {batch.batch_id}: execution_batch.{key}="
                f"{execution.get(key)!r}, expected {value!r}"
            )
    if coverage.get("n_read_failures_total") != 0:
        raise RuntimeError(f"{batch.batch_id} completed with read failures: {coverage.get('n_read_failures_total')}")
    return metadata


def run_batch(batch: Batch, notebook: Path, dry_run: bool) -> str:
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--execute",
        "--ExecutePreprocessor.timeout=-1",
        "--to",
        "notebook",
        "--inplace",
        str(notebook.relative_to(ROOT)),
    ]
    env = os.environ.copy()
    env["MYRORSS_BATCH_START"] = batch.batch_start
    env["MYRORSS_BATCH_END"] = batch.batch_end

    command_text = " ".join(cmd)
    print(f"[batch] RUN {batch.batch_id}: {batch.batch_start} to {batch.batch_end} ({batch.n_days} days)", flush=True)
    print(f"[batch] env MYRORSS_BATCH_START={batch.batch_start} MYRORSS_BATCH_END={batch.batch_end}", flush=True)
    print(f"[batch] cmd {command_text}", flush=True)

    if dry_run:
        return "dry_run"

    subprocess.run(cmd, cwd=ROOT, env=env, check=True)
    metadata = validate_metadata(batch)
    coverage = metadata["scan_coverage"]
    print(
        "[batch] DONE "
        f"{batch.batch_id}: source_files={coverage['n_source_files_total']} "
        f"empty={coverage['n_empty_source_files_total']} "
        f"read_failures={coverage['n_read_failures_total']}",
        flush=True,
    )
    return "ran"


def main() -> int:
    args = parse_args()
    plan_csv = args.plan_csv.resolve()
    notebook = args.notebook.resolve()

    if not plan_csv.exists():
        raise FileNotFoundError(plan_csv)
    if not notebook.exists():
        raise FileNotFoundError(notebook)

    batches = load_batches(plan_csv)
    selected = [
        batch
        for batch in batches
        if batch.batch_number >= args.start_batch and (args.end_batch is None or batch.batch_number <= args.end_batch)
    ]

    completed = skipped = ran = dry = 0
    for batch in selected:
        exists = batch.metadata_path.exists()
        if exists and not args.force:
            try:
                validate_metadata(batch)
            except Exception as exc:  # noqa: BLE001 - existing artifact is incomplete/dirty; rerun it
                print(
                    f"[batch] RETRY {batch.batch_id}: existing metadata failed validation: {type(exc).__name__}: {exc}",
                    flush=True,
                )
            else:
                skipped += 1
                print(
                    f"[batch] SKIP {batch.batch_id}: clean metadata exists at {batch.metadata_path.relative_to(ROOT)}",
                    flush=True,
                )
                continue
        if args.max_batches is not None and completed >= args.max_batches:
            break
        status = run_batch(batch, notebook, args.dry_run)
        completed += 1
        if status == "dry_run":
            dry += 1
        elif status == "ran":
            ran += 1

    print(
        f"[batch] summary selected={len(selected)} skipped_existing={skipped} "
        f"ran={ran} dry_run={dry}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
