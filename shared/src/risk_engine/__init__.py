"""risk_engine — the shared hazard risk engine (M2-M4).

A peer of the per-peril pipelines (it imports no peril). It consumes a hazard-distribution
object + an exposure input and emits the per-cell risk-metrics object. The CONUS grid and the
(future) deep per-asset run are two *drivers* of this one engine (DD-G11).

This is the Phase-A extraction: the M4 Monte-Carlo + metrics + QA, lifted verbatim (behaviour-
preserving) from the hail x solar selected-cell smoke notebook, with the asset/peril leaks
parameterized away (array inputs; ladders + capacity as arguments).

See: docs/plans/hazard_conus_grid/architecture/ (README, contracts, migration_plan).
"""

from .engine import (
    run_cell_mc,
    exceedance_metrics,
    weighted_quantile,
    validate_cell_mc,
)

__all__ = [
    "run_cell_mc",
    "exceedance_metrics",
    "weighted_quantile",
    "validate_cell_mc",
]
