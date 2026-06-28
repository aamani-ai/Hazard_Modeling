"""Compound-Poisson Monte Carlo for one cell x asset.

Extracted verbatim (behaviour-preserving) from the hail x solar smoke notebook ``run_cell_mc``
(L500-526). The only change is decoupling from DataFrame column names: the per-event hit
probabilities and conditional losses are passed as plain arrays, so the engine is peril-/
asset-agnostic. The RNG draw order (poisson -> integers -> random) is preserved exactly, so the
result is bit-identical to the original given the same arrays and generator.

The discipline this enforces (the rule the old model broke): draw a stochastic hit/miss per event
and add the FULL conditional loss on a hit — never ``p_hit * loss``.
"""

from __future__ import annotations

import numpy as np


def run_cell_mc(
    p_hit: np.ndarray,
    conditional_loss_usd: np.ndarray,
    lambda_cell: float,
    n_years: int,
    tiv_usd: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simulate ``n_years`` of annual loss for one cell x asset.

    Returns ``(aep, oep, aep_uncapped, counts)``:
      - ``aep``           annual aggregate loss, capped at ``tiv_usd``
      - ``oep``           largest single-event (occurrence) loss in the year
      - ``aep_uncapped``  annual aggregate loss before the TIV cap
      - ``counts``        Poisson event counts per year
    """
    p_evt = np.asarray(p_hit, dtype="float64")
    loss_evt = np.asarray(conditional_loss_usd, dtype="float64")

    counts = rng.poisson(max(lambda_cell, 0.0), n_years)
    total = int(counts.sum())
    if total == 0 or p_evt.size == 0:
        z = np.zeros(n_years, dtype="float64")
        return z, z, z, counts

    idx = rng.integers(0, p_evt.size, total)
    hit = rng.random(total) < p_evt[idx]
    hit_loss = np.where(hit, loss_evt[idx], 0.0)
    year_id = np.repeat(np.arange(n_years), counts)

    aep_uncapped = np.bincount(year_id, weights=hit_loss, minlength=n_years)
    aep = np.minimum(aep_uncapped, tiv_usd)
    oep = np.zeros(n_years, dtype="float64")
    np.maximum.at(oep, year_id, hit_loss)
    return aep, oep, aep_uncapped, counts
