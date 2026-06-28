"""Phase-A gate: the extracted ``risk_engine`` must reproduce the persisted hail x solar
selected-cell smoke metrics EXACTLY.

This is a behaviour-preservation test, not a recomputation of the science. It loads the prior
smoke run's persisted ``event_set`` (the per-event ``p_hit_solar`` + ``conditional_loss_usd`` — the
M4 input) and ``metrics`` (the ground truth), re-runs the extracted engine with the same RNG seeds
and ``MC_YEARS``, and asserts the metrics match to floating-point precision. Self-contained: needs
only the local prior-run CSVs, no M0/M1 recompute.

Run directly:  python shared/tests/test_engine_reproduces_smoke.py
Or via pytest: pytest shared/tests/
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from risk_engine.engine import run_cell_mc, exceedance_metrics

PRIOR_RUN = "20260618T045301Z_m2_m4_selected_cell_smoke"
SEED = 20260618
MC_YEARS = 250_000
CAPACITY_MW = 100.0
TIV_USD = CAPACITY_MW * 1000.0 * 1483.0      # 148,300,000 — canonical solar
CAPACITY_KWP = CAPACITY_MW * 1000.0
POLICY_SEED_OFFSET = {"raw_mrms": 0, "cap_100mm_sensitivity": 10_000_000}

# Metric columns that exist in both the persisted CSV and the engine output dict.
CHECK_COLS = [
    "eal_usd", "eal_pct_tiv",
    "var99_usd", "var99_pct_tiv",
    "pml100_usd", "pml100_pct_tiv",
    "pml250_pct_tiv", "pml500_pct_tiv",
    "tvar99_pct_tiv", "zero_loss_fraction",
]


def _repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


def _prior_tables_dir() -> Path:
    return (
        _repo_root()
        / "data" / "hazard_conus_grid" / "hail" / "solar" / "v1_mrms_only"
        / "m2_m4_selected_cell_smoke" / f"run_id={PRIOR_RUN}" / "tables"
    )


def reproduce():
    d = _prior_tables_dir()
    metrics = pd.read_csv(d / f"mrms_v1_solar_smoke_metrics_{PRIOR_RUN}.csv")
    events = pd.read_csv(d / f"mrms_v1_solar_smoke_event_set_{PRIOR_RUN}.csv")
    cols = [c for c in CHECK_COLS if c in metrics.columns]

    results = []
    max_rel = 0.0
    for _, r in metrics.iterrows():
        cell_id = int(r["cell_id"])
        policy = str(r["severity_policy"])
        lambda_cell = float(r["lambda_cell"])

        ev = events[(events["cell_id"] == cell_id) & (events["severity_policy"] == policy)]
        p_hit = ev["p_hit_solar"].to_numpy("float64")
        loss = ev["conditional_loss_usd"].to_numpy("float64")

        rng = np.random.default_rng(SEED + cell_id + POLICY_SEED_OFFSET[policy])
        aep, oep, aep_unc, counts = run_cell_mc(p_hit, loss, lambda_cell, MC_YEARS, TIV_USD, rng)
        m = exceedance_metrics(aep, oep, TIV_USD, CAPACITY_KWP)

        ok = True
        for c in cols:
            got, exp = float(m[c]), float(r[c])
            rel = abs(got - exp) / max(abs(exp), 1.0)
            max_rel = max(max_rel, rel)
            if not np.isclose(got, exp, rtol=1e-9, atol=1e-12):
                ok = False
        results.append({
            "role": r["role"], "policy": policy,
            "eal_new": m["eal_pct_tiv"], "eal_old": float(r["eal_pct_tiv"]),
            "pml100_new": m["pml100_pct_tiv"], "pml100_old": float(r["pml100_pct_tiv"]),
            "var99_new": m["var99_pct_tiv"], "var99_old": float(r["var99_pct_tiv"]),
            "ok": ok,
        })
    return results, max_rel, cols


def test_engine_reproduces_persisted_smoke_metrics():
    results, max_rel, _ = reproduce()
    assert all(x["ok"] for x in results), "extracted engine did not reproduce persisted smoke metrics"
    assert max_rel < 1e-9, f"max relative diff {max_rel:.3e} exceeds 1e-9"


if __name__ == "__main__":
    results, max_rel, cols = reproduce()
    print(f"checked {len(cols)} metric columns x {len(results)} (cell x policy) rows\n")
    hdr = f"{'role':<26}{'policy':<24}{'EAL% new/old':<24}{'PML100% new/old':<26}{'VaR99% new/old':<26}ok"
    print(hdr)
    print("-" * len(hdr))
    for x in results:
        print(
            f"{x['role']:<26}{x['policy']:<24}"
            f"{x['eal_new']:.6f}/{x['eal_old']:.6f}{'':<4}"
            f"{x['pml100_new']:.6f}/{x['pml100_old']:.6f}{'':<6}"
            f"{x['var99_new']:.6f}/{x['var99_old']:.6f}{'':<6}"
            f"{'PASS' if x['ok'] else 'FAIL'}"
        )
    print(f"\nmax relative diff across all checked metrics: {max_rel:.3e}")
    if all(x["ok"] for x in results) and max_rel < 1e-9:
        print("GATE PASS — extracted risk_engine reproduces the persisted smoke metrics exactly.")
        sys.exit(0)
    print("GATE FAIL")
    sys.exit(1)
