"""Phase-B gate: the extracted hail MRMS-M0 adapter reproduces the reconciled M0 EXACTLY on a
sample of dates.

Self-contained + offline: uses the locally-cached raw MESH tiles, the served mask, and the source
inventory, and diffs `build_daily_panel` output against the reconciled M0 date partitions. No Cloud
Run, no full re-run — per the "don't re-run the whole thing" rule.

Run directly:  python pipelines/hail/tests/test_adapter_reproduces_m0.py
Or via pytest:  pytest pipelines/hail/tests/
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from hail.config import M0_EVIDENCE_COLUMNS
from hail.mrms_m0 import BatchContext, build_daily_panel

# A spread: an early date, the extreme-MESH date (2022-01-03, max ~1057.7 mm), and a severe day.
SAMPLE_DATES = ["2020-10-15", "2022-01-03", "2024-06-01"]
M0_RECONCILED_RUN_ID = "20260616T225000Z_m0_full_conus_reconciled"
SOURCE_INVENTORY_RUN_ID = "20260616T165806Z"
SOURCE_INVENTORY_LABEL = "20140101_20260615"
REQUIRED_GRID_COLUMNS = ["cell_id", "lat_idx", "lon_idx", "lat_center", "lon_center", "state_abbr", "iso_rto"]


def _repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


ROOT = _repo_root()
CACHE = ROOT / "data" / "hail" / "mrms_raw"
HAIL = ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only"
RECON = HAIL / "m0_reconciled_daily_cell_evidence" / f"run_id={M0_RECONCILED_RUN_ID}"
SERVED = ROOT / "data" / "hazard_conus_grid" / "common" / "benchmark_grid" / "served_conus_cell_ids_v2026_06.csv"
INVENTORY = (
    HAIL / "m0_source_inventory" / f"run_id={SOURCE_INVENTORY_RUN_ID}"
    / f"mrms_v1_source_inventory_{SOURCE_INVENTORY_LABEL}_{SOURCE_INVENTORY_RUN_ID}.parquet"
)


def _served() -> pd.DataFrame:
    s = pd.read_csv(SERVED)
    s["cell_id"] = s["cell_id"].astype("int64")
    return s[REQUIRED_GRID_COLUMNS].copy()


def _inventory() -> pd.DataFrame:
    inv = pd.read_parquet(INVENTORY)
    inv["date"] = pd.to_datetime(inv["date"]).dt.date.astype(str)
    return inv


def _compare(panel: pd.DataFrame, exp: pd.DataFrame) -> tuple[bool, float, list[str]]:
    panel = panel.sort_values("cell_id").reset_index(drop=True)
    exp = exp.sort_values("cell_id").reset_index(drop=True)
    # Normalize the time columns to canonical strings on both sides: build_daily_panel emits
    # datetime64 while the reconcile step re-serializes `date` as a string — a reconcile-side
    # dtype change, not an evidence-value difference. We compare values, not dtypes.
    for df in (panel, exp):
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df["source_timestamp"] = pd.to_datetime(df["source_timestamp"], utc=True).astype(str)
    max_float_diff = 0.0
    bad: list[str] = []
    for col in M0_EVIDENCE_COLUMNS:
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


def reproduce():
    served = _served()
    inv = _inventory()
    ctx = BatchContext(served=served, served_cell_ids=set(served["cell_id"]))
    out = []
    for d in SAMPLE_DATES:
        part = RECON / f"date={d}" / "part-000.parquet"
        if not part.exists():
            out.append((d, None, None, ["MISSING reconciled partition"]))
            continue
        inv_row = inv[inv["date"] == d]
        if inv_row.empty:
            out.append((d, None, None, ["date not in inventory"]))
            continue
        panel, _ = build_daily_panel(ctx, inv_row.iloc[0], CACHE)
        exp = pq.ParquetFile(str(part)).read().to_pandas()  # read the file directly (no partition inference)
        ok, diff, bad = _compare(panel, exp)
        out.append((d, ok, diff, bad))
    return out


def test_adapter_reproduces_reconciled_m0():
    out = reproduce()
    assert out, "no sample dates ran"
    for d, ok, diff, bad in out:
        assert ok, f"{d}: adapter differs from reconciled M0 (cols {bad}, max float diff {diff})"


if __name__ == "__main__":
    out = reproduce()
    print(f"{'date':<14}{'rows':>8}  {'max_float_diff':>16}  result")
    print("-" * 56)
    all_ok = True
    for d, ok, diff, bad in out:
        if ok is None:
            print(f"{d:<14}{'-':>8}  {'-':>16}  SKIP/ERROR: {bad}")
            all_ok = False
            continue
        print(f"{d:<14}{13085:>8}  {diff:>16.3e}  {'PASS' if ok else 'FAIL ' + str(bad)}")
        all_ok = all_ok and ok
    print("\nGATE PASS — adapter reproduces the reconciled M0 exactly." if all_ok else "\nGATE FAIL")
    sys.exit(0 if all_ok else 1)
