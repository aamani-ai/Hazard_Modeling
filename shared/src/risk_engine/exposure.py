"""M2 exposure coupling — hazard event × asset → hit probability (DD-G13 coupling-type dispatch).

The coupling type is one of the five blanks a peril×asset fills: ``areal`` (footprint overlap),
``field`` (intensity field at a point), or ``site`` (site-conditioned). V1 implements ``areal`` — the
regime for hail/wildfire on a gridded canonical asset. This module is peril/asset-agnostic: areas in,
a probability out; the peril pipeline supplies the field mapping and the driver supplies the asset.

**Areal hit-or-miss (Minkowski).** An asset of footprint area ``s`` placed uniformly at random inside a
hazard bucket of area ``A`` is struck by a hazard footprint of area ``F`` with probability
``(√F + √s)² / A``, capped at 1. The ``√s`` edge term dominates when ``F`` is small — exactly the grid
regime — so this is materially different from the naive ``F/A``.
"""

from __future__ import annotations

import numpy as np


def couple_areal(footprint_area, asset_area, bucket_area):
    """Minkowski areal hit probability ``min((√F + √s)² / A, 1)``.

    Args:
        footprint_area: hazard strike footprint ``F`` (array or scalar; same length as ``bucket_area``).
        asset_area: asset footprint ``s`` (scalar).
        bucket_area: hazard bucket area ``A`` (array or scalar).

    Inputs are assumed already sanitized by the caller (``F ≥ 0``, ``A > 0``) — the peril pipeline owns
    those clips because the floors are source-specific (e.g. hail's 1-pixel ≈ 1-km² bucket floor).

    Returns:
        ``p_hit`` as a float64 ndarray in [0, 1].
    """
    footprint_area = np.asarray(footprint_area, dtype="float64")
    bucket_area = np.asarray(bucket_area, dtype="float64")
    p_hit = (np.sqrt(footprint_area) + np.sqrt(float(asset_area))) ** 2 / bucket_area
    return np.minimum(p_hit, 1.0)


# Coupling-type dispatch. V1 knows ``areal``; ``field`` / ``site`` slot in here for other perils.
_COUPLERS = {"areal": couple_areal}


def couple(coupling_type, **kwargs):
    """Dispatch to the named coupling type. Raises on an unknown type."""
    try:
        coupler = _COUPLERS[coupling_type]
    except KeyError as exc:
        raise ValueError(f"unknown coupling_type {coupling_type!r}; known: {sorted(_COUPLERS)}") from exc
    return coupler(**kwargs)
