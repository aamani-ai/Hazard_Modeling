"""Hail M2 coupling — map reconciled-M0 severe cell-day evidence to the areal hit probability.

Hail is an **areal** peril: the severe-MESH footprint inside the cell (``severe_area_km2_approx``) is the
strike footprint F, the observed native-pixel count is the bucket area A (a 1-pixel ≈ 1-km² proxy), and
the asset footprint s comes from the driver. The geometry lives in ``risk_engine.exposure.couple_areal``;
this module owns only the hail field mapping + the source-specific clips (F ≥ 0, A ≥ 1 pixel).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from risk_engine.exposure import couple_areal

COUPLING_BASIS = "Minkowski areal hit probability inside 0.25 degree grid cell"


def hail_event_p_hit(events: pd.DataFrame, asset_area_km2: float):
    """Per-severe-cell-day hit probability for an areal asset.

    Args:
        events: severe cell-day rows (``hail_day_flag`` already True), with ``severe_area_km2_approx``
            and ``n_native_pixels_observed``. Row order is preserved (the driver date-sorts per cell so
            the Monte-Carlo event sampling is reproducible).
        asset_area_km2: the asset footprint s.

    Returns:
        ``(p_hit, footprint_km2, bucket_km2_proxy)`` — float64 ndarrays aligned to ``events`` rows.
    """
    footprint = events["severe_area_km2_approx"].astype(float).clip(lower=0.0).to_numpy(dtype="float64")
    bucket = events["n_native_pixels_observed"].astype(float).clip(lower=1.0).to_numpy(dtype="float64")
    p_hit = couple_areal(footprint, asset_area_km2, bucket)
    return p_hit, footprint, bucket
