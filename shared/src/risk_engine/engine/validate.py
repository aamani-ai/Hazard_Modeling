"""Known-answer QA checks on a cell's Monte-Carlo run.

Extracted verbatim (behaviour-preserving) from the smoke notebook's inline QA block (L648-666).
This is *basics-spot-on* as code: the engine self-checks against analytic identities before any
metric is trusted.
"""

from __future__ import annotations

import math

import numpy as np


def validate_cell_mc(
    aep: np.ndarray,
    oep: np.ndarray,
    aep_uncapped: np.ndarray,
    capped_eal_usd: float,
    analytic_uncapped_eal_usd: float,
    lambda_asset: float,
) -> dict[str, object]:
    """Verify a cell's MC against known answers; returns the checks + an overall pass flag.

    Checks: (1) AEP >= OEP every year; (2) uncapped MC EAL matches the analytic
    ``lambda * mean(p_hit * conditional_loss)``; (3) capped EAL <= uncapped EAL;
    (4) zero-loss-year fraction matches Poisson thinning ``exp(-lambda_asset)``.
    """
    uncapped_mc_eal = float(np.mean(aep_uncapped))
    uncapped_eal_rel_error = (
        abs(uncapped_mc_eal - analytic_uncapped_eal_usd) / analytic_uncapped_eal_usd
        if analytic_uncapped_eal_usd > 0
        else abs(uncapped_mc_eal - analytic_uncapped_eal_usd)
    )
    zero_loss_expected = math.exp(-lambda_asset) if lambda_asset > 0 else 1.0
    zero_tolerance = 0.03 if lambda_asset > 0 else 1e-12
    eal_tolerance = 0.05 if analytic_uncapped_eal_usd > 0 else 1e-12
    zero_loss_observed = float(np.mean(aep == 0))
    aep_ge_oep = bool((aep + 1e-9 >= oep).all())

    qa_checks_pass = bool(
        aep_ge_oep
        and uncapped_eal_rel_error <= eal_tolerance
        and capped_eal_usd <= uncapped_mc_eal + 1e-6
        and abs(zero_loss_observed - zero_loss_expected) <= zero_tolerance
    )
    return {
        "uncapped_mc_eal_usd": uncapped_mc_eal,
        "uncapped_eal_rel_error": uncapped_eal_rel_error,
        "zero_loss_expected": zero_loss_expected,
        "zero_loss_observed": zero_loss_observed,
        "aep_ge_oep": aep_ge_oep,
        "qa_checks_pass": qa_checks_pass,
    }
