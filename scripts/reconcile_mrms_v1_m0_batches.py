#!/usr/bin/env python3
"""
Reconcile MRMS-only V1 M0 daily cell evidence batches.

This utility accepts explicit batch roots, validates batch metadata and row-level
contracts, and writes a reconciled partial/full M0 panel. It is intentionally
batch-root driven: M1 must consume reconciled M0, not arbitrary batch outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_ROOT = ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only" / "m0_reconciled_daily_cell_evidence"
DEFAULT_GCS_OUTPUT_ROOT = (
    "gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence"
)
ALLOWED_STATUSES = {
    "observed_no_hail",
    "observed_sub_severe_hail",
    "observed_severe_hail",
    "no_native_pixel_coverage",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-root-uri", action="append", required=True, help="Local or gs:// batch root.")
    parser.add_argument(
        "--run-id",
        default=os.environ.get("HAZARD_CONUS_GRID_RUN_ID", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")),
    )
    parser.add_argument("--local-root", type=Path, default=DEFAULT_LOCAL_ROOT)
    parser.add_argument("--gcs-output-root", default=os.environ.get("MRMS_M0_RECONCILED_GCS_ROOT", DEFAULT_GCS_OUTPUT_ROOT))
    parser.add_argument("--expected-cells", type=int, default=13085)
    parser.add_argument("--max-mesh-warning-mm", type=float, default=300.0)
    parser.add_argument("--upload", action="store_true", default=os.environ.get("HAZARD_CONUS_GRID_UPLOAD_TO_GCS") == "1")
    parser.add_argument("--force", action="store_true", help="Replace an existing local reconciliation output.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def is_gcs_uri(value: str | Path) -> bool:
    return str(value).startswith("gs://")


def split_gcs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError(f"not a gs:// URI: {uri}")
    rest = uri[5:]
    bucket, _, blob = rest.partition("/")
    if not bucket or not blob:
        raise ValueError(f"invalid gs:// URI: {uri}")
    return bucket, blob


def list_uri_files(root_uri: str) -> list[str]:
    if not is_gcs_uri(root_uri):
        root = Path(root_uri)
        return sorted(str(path) for path in root.rglob("*") if path.is_file())

    result = subprocess.run(
        ["gcloud", "storage", "ls", "-r", f"{root_uri.rstrip('/')}/**"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return sorted(line.strip() for line in result.stdout.splitlines() if line.strip().startswith("gs://"))


def download_uri(uri: str, local_dir: Path) -> Path:
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / Path(uri).name
    if not is_gcs_uri(uri):
        return Path(uri)

    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", uri, str(local_path)], check=True)
        return local_path

    bucket_name, blob_name = split_gcs_uri(uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(local_path)
    return local_path


def upload_file_to_gcs(local_path: Path, destination_uri: str) -> None:
    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", str(local_path), destination_uri], check=True)
        return

    bucket_name, blob_name = split_gcs_uri(destination_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(local_path)


def gcs_prefix_exists(uri: str) -> bool:
    result = subprocess.run(
        ["gcloud", "storage", "ls", f"{uri.rstrip('/')}/**"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def upload_tree(local_root: Path, gcs_root: str) -> list[str]:
    if gcs_prefix_exists(gcs_root):
        raise FileExistsError(f"GCS destination already has objects: {gcs_root}")

    uploaded: list[str] = []
    for path in sorted(p for p in local_root.rglob("*") if p.is_file()):
        rel = path.relative_to(local_root).as_posix()
        destination = f"{gcs_root.rstrip('/')}/{rel}"
        upload_file_to_gcs(path, destination)
        uploaded.append(destination)
    return uploaded


def one_matching(files: list[str], contains: str, suffix: str) -> str:
    matches = [path for path in files if contains in Path(path).name and path.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one *{contains}*{suffix}, got {len(matches)}: {matches}")
    return matches[0]


def load_batch(root_uri: str, temp_dir: Path, expected_cells: int, max_mesh_warning_mm: float) -> tuple[pd.DataFrame, dict[str, Any]]:
    files = list_uri_files(root_uri)
    metadata_uri = one_matching(files, "metadata_", ".json")
    panel_uri = one_matching(files, "mrms_v1_m0_daily_cell_evidence_", ".parquet")

    metadata_path = download_uri(metadata_uri, temp_dir)
    panel_path = download_uri(panel_uri, temp_dir)
    metadata = json.loads(metadata_path.read_text())
    panel = pd.read_parquet(panel_path)

    required_columns = {"hazard", "cell_id", "date", "source_product", "threshold_mm", "coverage_status", "mesh_max_mm"}
    missing = sorted(required_columns - set(panel.columns))
    if missing:
        raise ValueError(f"{root_uri}: panel missing columns {missing}")

    panel["date"] = pd.to_datetime(panel["date"]).dt.date.astype(str)
    unknown_statuses = sorted(set(panel["coverage_status"]) - ALLOWED_STATUSES)
    if unknown_statuses:
        raise ValueError(f"{root_uri}: unknown coverage statuses {unknown_statuses}")
    if panel.duplicated(["cell_id", "date"]).any():
        raise ValueError(f"{root_uri}: duplicate cell_id/date rows inside batch")

    per_date_rows = panel.groupby("date")["cell_id"].size()
    bad_dates = per_date_rows[per_date_rows != expected_cells]
    if not bad_dates.empty:
        raise ValueError(f"{root_uri}: date row counts differ from {expected_cells}: {bad_dates.to_dict()}")

    expected_rows = int(metadata.get("expected_rows", len(panel)))
    if len(panel) != expected_rows:
        raise ValueError(f"{root_uri}: metadata expected_rows={expected_rows}, panel rows={len(panel)}")

    max_mesh = panel["mesh_max_mm"].max(skipna=True)
    qa_flags: list[str] = []
    if pd.notna(max_mesh) and float(max_mesh) >= max_mesh_warning_mm:
        qa_flags.append(f"extreme_mesh_ge_{max_mesh_warning_mm:g}mm")

    manifest = {
        "batch_root_uri": root_uri.rstrip("/"),
        "metadata_uri": metadata_uri,
        "panel_uri": panel_uri,
        "source_run_id": metadata.get("run_id"),
        "batch_label": metadata.get("batch_label"),
        "batch_start_date": min(panel["date"]),
        "batch_end_date": max(panel["date"]),
        "n_dates": int(panel["date"].nunique()),
        "n_rows": int(len(panel)),
        "expected_rows": expected_rows,
        "n_served_cells": int(expected_cells),
        "severe_cell_days": int((panel["coverage_status"] == "observed_severe_hail").sum()),
        "sub_severe_cell_days": int((panel["coverage_status"] == "observed_sub_severe_hail").sum()),
        "no_hail_cell_days": int((panel["coverage_status"] == "observed_no_hail").sum()),
        "no_coverage_cell_days": int((panel["coverage_status"] == "no_native_pixel_coverage").sum()),
        "max_mesh_mm": None if pd.isna(max_mesh) else float(max_mesh),
        "qa_flags": ";".join(qa_flags) if qa_flags else "",
    }
    return panel, manifest


def main() -> int:
    args = parse_args()
    t0 = time.perf_counter()
    local_run_dir = args.local_root / f"run_id={args.run_id}"

    print(f"[mrms-m0-reconcile] run_id={args.run_id}", flush=True)
    print(f"[mrms-m0-reconcile] batches={len(args.batch_root_uri)}", flush=True)
    print(f"[mrms-m0-reconcile] local_run_dir={local_run_dir}", flush=True)
    for root in args.batch_root_uri:
        print(f"[mrms-m0-reconcile] input={root}", flush=True)

    if args.dry_run:
        return 0

    if local_run_dir.exists():
        if not args.force:
            raise FileExistsError(f"local reconciliation dir exists; pass --force: {local_run_dir}")
        shutil.rmtree(local_run_dir)
    local_run_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        panels: list[pd.DataFrame] = []
        manifests: list[dict[str, Any]] = []
        for root in args.batch_root_uri:
            panel, manifest = load_batch(root, temp_dir, args.expected_cells, args.max_mesh_warning_mm)
            panels.append(panel)
            manifests.append(manifest)

    reconciled = pd.concat(panels, ignore_index=True).sort_values(["date", "cell_id"]).reset_index(drop=True)
    if reconciled.duplicated(["cell_id", "date"]).any():
        duplicate_dates = sorted(reconciled.loc[reconciled.duplicated(["cell_id", "date"], keep=False), "date"].unique())
        raise ValueError(f"duplicate cell_id/date rows across batches; affected dates={duplicate_dates[:10]}")

    date_rows = reconciled.groupby("date")["cell_id"].size().rename("n_rows").reset_index()
    date_status = (
        reconciled.groupby(["date", "coverage_status"])["cell_id"]
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    date_coverage = date_rows.merge(date_status, on="date", how="left")
    date_coverage["expected_rows"] = args.expected_cells
    date_coverage["row_count_status"] = date_coverage["n_rows"].eq(args.expected_cells).map({True: "pass", False: "fail"})

    status_summary = (
        reconciled.groupby(["date", "coverage_status"])
        .agg(
            n_cells=("cell_id", "size"),
            n_positive_pixels=("n_native_pixels_positive", "sum"),
            n_severe_pixels=("n_native_pixels_severe", "sum"),
            max_mesh_mm=("mesh_max_mm", "max"),
        )
        .reset_index()
        .sort_values(["date", "coverage_status"])
    )

    label = f"{min(reconciled['date']).replace('-', '')}_{max(reconciled['date']).replace('-', '')}"
    panel_path = local_run_dir / f"mrms_v1_m0_reconciled_daily_cell_evidence_{label}_{args.run_id}.parquet"
    manifest_csv = local_run_dir / f"mrms_v1_m0_reconciled_batch_manifest_{label}_{args.run_id}.csv"
    date_coverage_csv = local_run_dir / f"mrms_v1_m0_reconciled_date_coverage_{label}_{args.run_id}.csv"
    status_summary_csv = local_run_dir / f"mrms_v1_m0_reconciled_status_summary_{label}_{args.run_id}.csv"
    metadata_json = local_run_dir / f"metadata_{label}_{args.run_id}.json"

    reconciled.to_parquet(panel_path, index=False)
    pd.DataFrame(manifests).to_csv(manifest_csv, index=False)
    date_coverage.to_csv(date_coverage_csv, index=False)
    status_summary.to_csv(status_summary_csv, index=False)

    for date_str, day_panel in reconciled.groupby("date"):
        partition_dir = local_run_dir / f"date={date_str}"
        partition_dir.mkdir(parents=True, exist_ok=True)
        day_panel.to_parquet(partition_dir / "part-000.parquet", index=False)

    qa_flags = sorted({flag for m in manifests for flag in str(m["qa_flags"]).split(";") if flag})
    metadata: dict[str, Any] = {
        "artifact_family": "mrms_v1_m0_reconciled_daily_cell_evidence",
        "status": "partial_reconciliation",
        "execution_type": "local_reconciliation",
        "run_id": args.run_id,
        "hazard": "hail",
        "variant": "v1_mrms_only",
        "layer": "m0_reconciled_daily_cell_evidence",
        "input_batch_roots": [root.rstrip("/") for root in args.batch_root_uri],
        "n_input_batches": int(len(args.batch_root_uri)),
        "date_start": min(reconciled["date"]),
        "date_end": max(reconciled["date"]),
        "n_dates": int(reconciled["date"].nunique()),
        "n_served_cells": int(args.expected_cells),
        "expected_rows": int(args.expected_cells * reconciled["date"].nunique()),
        "n_output_rows": int(len(reconciled)),
        "duplicate_cell_date_rows": int(reconciled.duplicated(["cell_id", "date"]).sum()),
        "coverage_status_counts": reconciled["coverage_status"].value_counts().to_dict(),
        "qa_flags": qa_flags,
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
        "local_run_dir": str(local_run_dir),
        "gcs_run_root": f"{args.gcs_output_root.rstrip('/')}/run_id={args.run_id}",
        "upload_requested": bool(args.upload),
        "outputs": {
            "reconciled_panel_parquet": str(panel_path),
            "batch_manifest_csv": str(manifest_csv),
            "date_coverage_csv": str(date_coverage_csv),
            "status_summary_csv": str(status_summary_csv),
            "metadata_json": str(metadata_json),
        },
        "allowed_use": [
            "M0 reconciliation proof",
            "QA of multiple M0 batch prefixes",
        ],
        "not_allowed_use": [
            "M1 production input until full accepted denominator is reconciled",
            "reportable EAL/PML/VaR/TVaR input",
        ],
        "caveats": [
            "Partial non-contiguous proof if input batches are not the full accepted denominator.",
            "Raw MRMS MESH is radar-estimated and not de-biased.",
        ],
    }
    metadata_json.write_text(json.dumps(metadata, indent=2) + "\n")

    if args.upload:
        gcs_run_root = f"{args.gcs_output_root.rstrip('/')}/run_id={args.run_id}"
        uploaded = upload_tree(local_run_dir, gcs_run_root)
        metadata["upload_status"] = "uploaded"
        metadata["uploaded_gcs_outputs"] = uploaded
    else:
        metadata["upload_status"] = "skipped"
        metadata["uploaded_gcs_outputs"] = []
    metadata_json.write_text(json.dumps(metadata, indent=2) + "\n")

    if args.upload:
        upload_file_to_gcs(metadata_json, f"{args.gcs_output_root.rstrip('/')}/run_id={args.run_id}/{metadata_json.name}")

    print(
        "[mrms-m0-reconcile] DONE "
        f"rows={len(reconciled)} dates={reconciled['date'].nunique()} "
        f"duplicates=0 qa_flags={qa_flags} upload_status={metadata['upload_status']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
