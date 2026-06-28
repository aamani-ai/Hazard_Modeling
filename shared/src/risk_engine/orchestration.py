"""Per-cell M2–M4 orchestration: coupled events in (p_hit + conditional loss + frequency), metrics out.

Generic over peril/asset. The driver supplies the per-event hit probabilities, the per-event conditional
losses (USD), the cell frequency ``λ_cell``, the asset TIV + capacity, an RNG, and the return-period
ladder; this runs the Monte Carlo, the conditional-loss summaries, the exceedance metrics, and the QA
checks **exactly** as the worked hail×solar smoke did (sections 5–6). Reused by every driver (the CONUS
grid and the future deep-per-asset), so the per-cell risk math lives in one place.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from risk_engine.engine import exceedance_metrics, run_cell_mc, weighted_quantile


def run_cell_risk(
    p_hit,
    conditional_loss_usd,
    lambda_cell: float,
    n_years: int,
    tiv_usd: float,
    capacity_kwp: float,
    rng,
    return_periods,
) -> dict[str, Any]:
    """Run M2–M4 for one cell × severity policy and return the engine-computed metrics dict.

    The returned dict is the ``exceedance_metrics`` output merged with the coupling/conditional-loss
    summaries and the QA-check results. The driver wraps it with identity/provenance/QA-flag fields.

    Handles the zero-event cell (empty ``p_hit``): ``run_cell_mc`` with ``λ=0`` yields all-zero loss
    vectors, and the summaries collapse to 0 / NaN exactly as the smoke's empty branch did.
    """
    p_hit = np.asarray(p_hit, dtype="float64")
    conditional_loss_usd = np.asarray(conditional_loss_usd, dtype="float64")

    aep, oep, aep_uncapped, counts = run_cell_mc(
        p_hit=p_hit,
        conditional_loss_usd=conditional_loss_usd,
        lambda_cell=lambda_cell,
        n_years=n_years,
        tiv_usd=tiv_usd,
        rng=rng,
    )

    if p_hit.size == 0:
        mean_p_hit = 0.0
        lambda_asset = 0.0
        cond_loss_mean = float("nan")
        cond_loss_p50 = float("nan")
        cond_loss_p95 = float("nan")
        cond_loss_p99 = float("nan")
        cond_loss_max = float("nan")
        analytic_uncapped_eal = 0.0
    else:
        mean_p_hit = float(np.mean(p_hit))
        lambda_asset = lambda_cell * mean_p_hit
        cond_loss_mean = float(np.average(conditional_loss_usd, weights=p_hit)) if p_hit.sum() > 0 else float("nan")
        cond_loss_p50 = weighted_quantile(conditional_loss_usd, p_hit, 0.50)
        cond_loss_p95 = weighted_quantile(conditional_loss_usd, p_hit, 0.95)
        cond_loss_p99 = weighted_quantile(conditional_loss_usd, p_hit, 0.99)
        cond_loss_max = float(np.max(conditional_loss_usd))
        analytic_uncapped_eal = lambda_cell * float(np.mean(p_hit * conditional_loss_usd))

    metric = exceedance_metrics(
        aep,
        oep,
        tiv_usd,
        capacity_kwp=capacity_kwp,
        return_periods=return_periods,
    )

    uncapped_mc_eal = float(np.mean(aep_uncapped))
    cap_binding_fraction = float(np.mean(aep_uncapped > tiv_usd))
    uncapped_eal_rel_error = (
        abs(uncapped_mc_eal - analytic_uncapped_eal) / analytic_uncapped_eal
        if analytic_uncapped_eal > 0
        else abs(uncapped_mc_eal - analytic_uncapped_eal)
    )
    zero_loss_expected = math.exp(-lambda_asset) if lambda_asset > 0 else 1.0
    zero_tolerance = 0.03 if lambda_asset > 0 else 1e-12
    eal_tolerance = 0.05 if analytic_uncapped_eal > 0 else 1e-12
    qa_checks_pass = bool(
        (aep + 1e-9 >= oep).all()
        and uncapped_eal_rel_error <= eal_tolerance
        and metric["eal_usd"] <= uncapped_mc_eal + 1e-6
        and abs(float(np.mean(aep == 0)) - zero_loss_expected) <= zero_tolerance
    )

    result: dict[str, Any] = dict(metric)
    result.update(
        {
            "mean_p_hit": mean_p_hit,
            "lambda_asset": lambda_asset,
            "cond_loss_mean_usd": cond_loss_mean,
            "cond_loss_p50_usd": cond_loss_p50,
            "cond_loss_p95_usd": cond_loss_p95,
            "cond_loss_p99_usd": cond_loss_p99,
            "cond_loss_max_usd": cond_loss_max,
            "analytic_uncapped_eal_usd": analytic_uncapped_eal,
            "mc_uncapped_eal_usd": uncapped_mc_eal,
            "cap_binding_fraction": cap_binding_fraction,
            "qa_checks_pass": qa_checks_pass,
            "qa_uncapped_eal_rel_error": uncapped_eal_rel_error,
            "qa_zero_loss_expected_poisson_thinning": zero_loss_expected,
        }
    )
    return result
