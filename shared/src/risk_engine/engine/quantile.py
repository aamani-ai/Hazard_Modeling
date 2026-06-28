"""Weighted quantile — extracted verbatim from the hail x solar smoke notebook (L484)."""

from __future__ import annotations

import numpy as np


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Value at weighted quantile ``q`` of ``values`` (NaN if no valid mass).

    Behaviour-preserving copy of the smoke-notebook helper: mask non-finite / non-positive
    weights, sort by value, and search the cumulative-weight position.
    """
    values = np.asarray(values, dtype="float64")
    weights = np.asarray(weights, dtype="float64")
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return float("nan")
    values = values[mask]
    weights = weights[mask]
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cumulative = np.cumsum(weights)
    cutoff = q * cumulative[-1]
    return float(values[np.searchsorted(cumulative, cutoff, side="left")])
