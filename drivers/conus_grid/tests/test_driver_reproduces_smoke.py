"""Gate: the CONUS grid driver, restricted to the 5 smoke cells, reproduces the persisted smoke metrics.

This is the correctness oracle for the whole M2–M4 driver chain (coupling → damage → engine). Same
seeds (``SEED + cell_id + {0|10M}``), same MC_YEARS (250k), same RP ladder — so every engine-computed
metric must match the worked smoke CSV bit-for-bit. Offline (local M1 + reconciled M0 + curve); no full
13,085-cell run, no Cloud Run.

Run directly:  python drivers/conus_grid/tests/test_driver_reproduces_smoke.py
Or via pytest:  pytest drivers/conus_grid/tests/test_driver_reproduces_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from conus_grid.canonical_assets import CANONICAL_SOLAR, MC_YEARS_DEFAULT, SEED, SEVERITY_POLICIES
from conus_grid.grid_driver import load_severe_events, run_grid
from hail.damage import load_curve
from risk_engine.config import CANONICAL_RETURN_PERIODS

SMOKE_RUN_ID = "20260618T045301Z_m2_m4_selected_cell_smoke"
M1_RUN_ID = "20260618T040000Z_m1_mrms_only"
M0_RECONCILED_RUN_ID = "20260616T225000Z_m0_full_conus_reconciled"
SMOKE_CELLS = [302001, 276114, 306280, 273305, 281823]


def _repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


ROOT = _repo_root()
HAIL = ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only"
M1_PARQUET = HAIL / "m1_hazard_layer" / f"run_id={M1_RUN_ID}" / "tables" / f"mrms_v1_m1_hazard_layer_{M1_RUN_ID}.parquet"
RECON = HAIL / "m0_reconciled_daily_cell_evidence" / f"run_id={M0_RECONCILED_RUN_ID}"
CURVE = ROOT / "data" / "hail" / "damage_curves" / "hail_solar_asset_capex_weighted.json"
SMOKE_METRICS = (
    ROOT / "data" / "hazard_conus_grid" / "hail" / "solar" / "v1_mrms_only" / "m2_m4_selected_cell_smoke"
    / f"run_id={SMOKE_RUN_ID}" / "tables" / f"mrms_v1_solar_smoke_metrics_{SMOKE_RUN_ID}.csv"
)

# Metrics the driver must reproduce (engine output + coupling/loss summaries + lambda input).
GATE_COLUMNS = [
    "lambda_cell", "mean_p_hit", "lambda_asset",
    "eal_usd", "eal_pct_tiv", "eal_usd_per_kwp_yr", "zero_loss_fraction",
    "var99_pct_tiv", "var95_pct_tiv", "tvar99_pct_tiv", "tvar95_pct_tiv",
    "pml100_pct_tiv", "pml250_pct_tiv", "pml500_pct_tiv",
    "aep_loss_rp100_pct_tiv", "aep_loss_rp200_pct_tiv", "oep_loss_rp100_pct_tiv",
    "cond_loss_mean_usd", "cond_loss_p95_usd", "cond_loss_max_usd",
    "cond_loss_mean_pct_tiv", "cond_loss_p99_pct_tiv",
    "analytic_uncapped_eal_usd", "mc_uncapped_eal_usd", "cap_binding_fraction",
    "qa_uncapped_eal_rel_error", "qa_zero_loss_expected_poisson_thinning",
]


def reproduce() -> dict:
    m1 = pd.read_parquet(M1_PARQUET)
    m1_5 = m1.loc[m1["cell_id"].isin(SMOKE_CELLS)].copy()
    events = load_severe_events(RECON, cell_ids=set(SMOKE_CELLS))
    curve = load_curve(CURVE)

    out = run_grid(
        m1_5,
        events,
        CANONICAL_SOLAR,
        curve,
        severity_policies=SEVERITY_POLICIES,
        mc_years=MC_YEARS_DEFAULT,
        seed=SEED,
        return_periods=CANONICAL_RETURN_PERIODS,
    )
    smoke = pd.read_csv(SMOKE_METRICS)

    key = ["cell_id", "severity_policy"]
    merged = out.merge(smoke, on=key, suffixes=("_drv", "_smk"), validate="one_to_one")
    assert len(merged) == len(SMOKE_CELLS) * len(SEVERITY_POLICIES), f"join produced {len(merged)} rows"

    # The compute is bit-identical (same engine, seeds, inputs); the oracle is a CSV, so $-magnitude
    # columns carry ~1 ULP round-trip noise. Assert machine-epsilon agreement: relative for large
    # magnitudes, absolute for small — caught by allclose(rtol=1e-9, atol=1e-6), far below any real bug.
    max_abs = 0.0
    max_rel = 0.0
    worst = ""
    bad: list[str] = []
    for col in GATE_COLUMNS:
        a = merged[f"{col}_drv"].to_numpy("float64")
        b = merged[f"{col}_smk"].to_numpy("float64")
        d = np.abs(a - b)
        abs_diff = float(np.nanmax(d)) if len(d) else 0.0
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(np.abs(b) > 1.0, d / np.abs(b), 0.0)
        rel_diff = float(np.nanmax(rel)) if len(rel) else 0.0
        if abs_diff > max_abs:
            max_abs, worst = abs_diff, col
        max_rel = max(max_rel, rel_diff)
        if not np.allclose(a, b, rtol=1e-9, atol=1e-6, equal_nan=True):
            bad.append(f"{col}(abs={abs_diff:.2e}, rel={rel_diff:.2e})")

    # QA must pass on every driver row, matching the smoke.
    qa_all_pass = bool(out["qa_checks_pass"].all())
    return {
        "rows": len(merged),
        "max_abs": max_abs,
        "max_rel": max_rel,
        "worst_col": worst,
        "bad": bad,
        "qa_all_pass": qa_all_pass,
        "out": out,
        "merged": merged,
    }


def test_driver_reproduces_smoke():
    r = reproduce()
    assert r["qa_all_pass"], "driver QA checks did not all pass"
    assert not r["bad"], f"driver diverges from smoke on: {r['bad']} (max abs {r['max_abs']:.3e} at {r['worst_col']})"
    assert r["max_rel"] < 1e-9, f"relative reproduction worse than machine epsilon: {r['max_rel']:.3e}"


if __name__ == "__main__":
    r = reproduce()
    print("\n=== CONUS grid driver reproduction gate (5 smoke cells × 2 policies) ===")
    print(f"joined rows      : {r['rows']} / {len(SMOKE_CELLS) * len(SEVERITY_POLICIES)}")
    print(f"QA all pass      : {r['qa_all_pass']}")
    print(f"max abs diff     : {r['max_abs']:.3e}  (worst column: {r['worst_col']}, $-magnitude)")
    print(f"max rel diff     : {r['max_rel']:.3e}  (machine-epsilon = exact reproduction)")
    print(f"diverging columns: {r['bad'] if r['bad'] else 'none'}")
    cols = ["role", "cell_id", "severity_policy"] if "role" in r["merged"].columns else ["cell_id", "severity_policy"]
    show = r["merged"][[*cols, "eal_pct_tiv_drv", "eal_pct_tiv_smk", "pml100_pct_tiv_drv", "pml100_pct_tiv_smk"]]
    print("\nspot check (driver vs smoke):")
    print(show.to_string(index=False))
    ok = r["qa_all_pass"] and not r["bad"] and r["rows"] == len(SMOKE_CELLS) * len(SEVERITY_POLICIES)
    print("\nGATE PASS — driver reproduces the smoke metrics exactly." if ok else "\nGATE FAIL")
    sys.exit(0 if ok else 1)
