"""Phase-B gate: the extracted M1 hazard-layer build reproduces the persisted full-CONUS M1 EXACTLY.

Unlike the M0 adapter gate (which can sample dates), M1 is a per-cell aggregation over EVERY accepted
source date, so this streams all 2,071 reconciled-M0 daily partitions (~27M cell-days) through
`build_m1_hazard_layer` and diffs the 52-column M1 contract against the persisted hazard layer. It also
proves the persisted parquet's incidental 53rd column (`max_mesh_mm_log1p_display`) is exactly the
notebook map section's `log1p(max_mesh_mm_raw_any_day)` display transform.

Self-contained + offline: uses the locally-reconciled M0. No Cloud Run, no re-run of M0/the notebook.

Run directly:  python pipelines/hail/tests/test_m1_reproduces.py   (heavy: full-CONUS scan)
Or via pytest:  pytest pipelines/hail/tests/test_m1_reproduces.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from hail.m1_hazard_layer import M1_HAZARD_LAYER_COLUMNS, build_m1_hazard_layer

M1_RUN_ID = "20260618T040000Z_m1_mrms_only"
RECONCILED_RUN_ID = "20260616T225000Z_m0_full_conus_reconciled"
DISPLAY_COLUMN = "max_mesh_mm_log1p_display"


def _repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


ROOT = _repo_root()
HAIL = ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only"
RECON = HAIL / "m0_reconciled_daily_cell_evidence" / f"run_id={RECONCILED_RUN_ID}"
RECON_META = RECON / f"metadata_{RECONCILED_RUN_ID}.json"
DATE_COVERAGE = RECON / f"mrms_v1_m0_reconciled_date_coverage_{RECONCILED_RUN_ID}.csv"
M1_PARQUET = (
    HAIL / "m1_hazard_layer" / f"run_id={M1_RUN_ID}" / "tables" / f"mrms_v1_m1_hazard_layer_{M1_RUN_ID}.parquet"
)


def _compare(panel: pd.DataFrame, exp: pd.DataFrame) -> tuple[bool, float, list[str]]:
    panel = panel.sort_values("cell_id").reset_index(drop=True)
    exp = exp.sort_values("cell_id").reset_index(drop=True)
    max_float_diff = 0.0
    bad: list[str] = []
    for col in M1_HAZARD_LAYER_COLUMNS:
        a, b = panel[col], exp[col]
        if pd.api.types.is_float_dtype(a) or pd.api.types.is_float_dtype(b):
            av, bv = a.to_numpy("float64"), b.to_numpy("float64")
            diff = float(np.nanmax(np.abs(av - bv))) if len(av) else 0.0
            max_float_diff = max(max_float_diff, diff)
            ok = bool(np.allclose(av, bv, rtol=0.0, atol=1e-9, equal_nan=True))
        else:
            ok = bool((a.astype(str).to_numpy() == b.astype(str).to_numpy()).all())
        if not ok:
            bad.append(col)
    return (len(bad) == 0), max_float_diff, bad


def reproduce() -> dict:
    reconciled_metadata = json.loads(RECON_META.read_text())
    date_coverage = pd.read_csv(DATE_COVERAGE)
    partition_paths = sorted(RECON.glob("date=*/part-000.parquet"))

    hazard_layer, diagnostics = build_m1_hazard_layer(
        partition_paths,
        date_coverage,
        reconciled_metadata,
        m1_run_id=M1_RUN_ID,
        reconciled_run_id=RECONCILED_RUN_ID,
    )

    exp = pd.read_parquet(M1_PARQUET)
    ok, diff, bad = _compare(hazard_layer, exp)

    # The persisted parquet's 53rd column is a display-only log1p of max_mesh_mm_raw_any_day.
    display_expected = np.log1p(exp["max_mesh_mm_raw_any_day"].fillna(0).to_numpy("float64"))
    display_ok = bool(
        np.allclose(exp[DISPLAY_COLUMN].to_numpy("float64"), display_expected, rtol=0.0, atol=1e-9, equal_nan=True)
    )

    return {
        "rows_built": len(hazard_layer),
        "rows_expected": len(exp),
        "cols_built": len(hazard_layer.columns),
        "cols_expected": len(exp.columns),
        "ok": ok,
        "max_float_diff": diff,
        "bad_cols": bad,
        "display_col_ok": display_ok,
        "diagnostics": diagnostics,
    }


def test_m1_reproduces_persisted_layer():
    r = reproduce()
    assert r["rows_built"] == r["rows_expected"] == 13085, r
    assert r["ok"], f"M1 differs from persisted layer (cols {r['bad_cols']}, max float diff {r['max_float_diff']})"
    assert r["display_col_ok"], "max_mesh_mm_log1p_display is not log1p(max_mesh_mm_raw_any_day)"


if __name__ == "__main__":
    r = reproduce()
    print("\n=== M1 reproduction gate ===")
    print(f"rows built/expected : {r['rows_built']:,} / {r['rows_expected']:,}")
    print(f"cols built/expected : {r['cols_built']} / {r['cols_expected']}  (persisted carries +1 display col)")
    print(f"streamed cell-days  : {r['diagnostics']['streamed_rows']:,}")
    print(f"severe cell-days    : {r['diagnostics']['severe_cell_day_samples']:,}")
    print(f"scan elapsed (s)    : {r['diagnostics']['scan_elapsed_seconds']}")
    print(f"max float diff      : {r['max_float_diff']:.3e}")
    print(f"display col == log1p : {r['display_col_ok']}")
    ok = r["ok"] and r["display_col_ok"] and r["rows_built"] == 13085
    print("\nGATE PASS — M1 build reproduces the persisted hazard layer exactly." if ok else f"\nGATE FAIL: {r['bad_cols']}")
    sys.exit(0 if ok else 1)
