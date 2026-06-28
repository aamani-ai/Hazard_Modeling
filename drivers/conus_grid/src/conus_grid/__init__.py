"""CONUS grid driver — canonical-asset-at-every-cell driver of the shared risk engine.

One of the *two drivers* of the same engine (DD-G11): this one places a canonical asset at every served
grid cell; the future deep-per-asset driver places one real asset. Off-grid == on-grid.
"""

from conus_grid.canonical_assets import CANONICAL_SOLAR, MC_YEARS_DEFAULT, SEED, SEVERITY_POLICIES
from conus_grid.grid_driver import load_severe_events, run_grid

__all__ = [
    "CANONICAL_SOLAR",
    "SEVERITY_POLICIES",
    "SEED",
    "MC_YEARS_DEFAULT",
    "load_severe_events",
    "run_grid",
]
