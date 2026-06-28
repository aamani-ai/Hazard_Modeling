"""Validate the V1 plausibility QC against the real M1 hazard layer.

Asserts the decided rule: severity summary capped at the physical ceiling (203.2 mm), >=300 mm hard
artifacts flagged (585 cells), frequency-spike cells flagged + held out — and crucially that the raw
severity columns AND every frequency column are left untouched (QC is additive).

Run directly:  python pipelines/hail/tests/test_plausibility_qc.py
Or via pytest:  pytest pipelines/hail/tests/test_plausibility_qc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from hail.plausibility_qc import (
    HARD_ARTIFACT_MM,
    SEVERITY_CAP_MAP,
    US_RECORD_HAIL_MM,
    apply_plausibility_qc,
)

M1_RUN_ID = "20260618T040000Z_m1_mrms_only"
FREQUENCY_COLUMNS_UNTOUCHED = [
    "n_observed_days", "observed_years", "n_severe_hail_days", "lambda_cell_raw",
    "n_no_hail_days", "n_sub_severe_days",
]


def _repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


ROOT = _repo_root()
M1_PARQUET = (
    ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only" / "m1_hazard_layer"
    / f"run_id={M1_RUN_ID}" / "tables" / f"mrms_v1_m1_hazard_layer_{M1_RUN_ID}.parquet"
)


def run():
    raw = pd.read_parquet(M1_PARQUET)
    qc, summary = apply_plausibility_qc(raw)
    return raw, qc, summary


def _series_equal(a: pd.Series, b: pd.Series) -> bool:
    av, bv = a.to_numpy(), b.to_numpy()
    if pd.api.types.is_float_dtype(a) or pd.api.types.is_float_dtype(b):
        return bool(np.array_equal(av.astype("float64"), bv.astype("float64"), equal_nan=True))
    return bool((av == bv).all())


def test_plausibility_qc():
    raw, qc, summary = run()

    # (1) additive: raw severity + every frequency column untouched.
    for col in list(SEVERITY_CAP_MAP) + FREQUENCY_COLUMNS_UNTOUCHED:
        assert _series_equal(raw[col], qc[col]), f"QC modified raw column {col}"

    # (2) cap correctness: capped = min(raw, cap); capped never exceeds the ceiling.
    cap = US_RECORD_HAIL_MM
    for raw_col, capped_col in SEVERITY_CAP_MAP.items():
        r = raw[raw_col].to_numpy("float64")
        c = qc[capped_col].to_numpy("float64")
        assert np.array_equal(c, np.minimum(r, cap), equal_nan=True), f"{capped_col} != min(raw, cap)"
        finite = c[~np.isnan(c)]
        assert (finite <= cap + 1e-9).all(), f"{capped_col} exceeds the cap"

    # (3) the headline: raw max is the 1,437 mm artifact; capped max is the physical ceiling.
    assert summary["max_raw_mesh_mm"] > 1000.0
    assert abs(summary["max_capped_mesh_mm"] - cap) < 1e-6

    # (4) hard-artifact flag matches the proven >=300 flag (expected 585 cells).
    assert summary["n_hard_artifact"] == int(raw["extreme_mesh_ge_300mm_flag"].sum())
    assert summary["n_severity_capped"] >= summary["n_hard_artifact"]  # cap net is wider than 300

    # (5) frequency-spike: a small flagged tail; held-out + eligible partition the cells exactly.
    assert 0 < summary["n_frequency_spike"] < summary["n_cells"]
    assert summary["n_reportable_eligible"] == summary["n_cells"] - summary["n_frequency_spike"]
    assert np.isfinite(summary["spike_threshold_lambda"])


if __name__ == "__main__":
    raw, qc, summary = run()
    lam = raw["lambda_cell_raw"].to_numpy("float64")
    nz = lam[lam > 0]
    print("\n=== Plausibility QC on the real M1 hazard layer ===")
    print(f"cells: {summary['n_cells']:,}   raw cols: {raw.shape[1]} -> qc cols: {qc.shape[1]} (+{qc.shape[1]-raw.shape[1]})")
    print("\n-- MAGNITUDE --")
    print(f"raw max MESH      : {summary['max_raw_mesh_mm']:.1f} mm  (the artifact)")
    print(f"capped max MESH   : {summary['max_capped_mesh_mm']:.1f} mm  (US record ceiling = {US_RECORD_HAIL_MM} mm)")
    print(f"cells capped      : {summary['n_severity_capped']:,}  (raw severity > {US_RECORD_HAIL_MM} mm)")
    print(f"hard artifacts    : {summary['n_hard_artifact']:,}  (>= {HARD_ARTIFACT_MM:.0f} mm; matches extreme_mesh_ge_300mm_flag)")
    print("\n-- FREQUENCY (rate untouched; flag + hold-out only) --")
    print(f"lambda percentiles (nonzero cells): p50={np.percentile(nz,50):.2f}  p90={np.percentile(nz,90):.2f}  p99={np.percentile(nz,99):.2f}  p99.5={np.percentile(nz,99.5):.2f}  max={nz.max():.2f}  (severe days/yr)")
    print(f"spike threshold   : lambda > {summary['spike_threshold_lambda']:.2f}/yr  (p{summary['spike_percentile']} of nonzero cells)")
    print(f"spike cells flagged: {summary['n_frequency_spike']:,}  -> held out of reportable loss")
    print(f"reportable eligible: {summary['n_reportable_eligible']:,}")
    print("\n-- status breakdown --")
    print(qc["plausibility_qc_status"].value_counts().to_string())
    # quick invariants
    ok = (
        abs(summary["max_capped_mesh_mm"] - US_RECORD_HAIL_MM) < 1e-6
        and summary["n_hard_artifact"] == int(raw["extreme_mesh_ge_300mm_flag"].sum())
        and _series_equal(raw["lambda_cell_raw"], qc["lambda_cell_raw"])
    )
    print("\nQC VALIDATED — severity capped, frequency untouched, artifacts flagged." if ok else "\nQC CHECK FAILED")
    sys.exit(0 if ok else 1)
