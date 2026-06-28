"""Hail M3 damage — load the canonical hail×solar curve artifact and emit conditional loss.

Thin peril/asset wrapper over ``risk_engine.vulnerability``: load the vendored capex-weighted curve,
apply the framework to the (policy-capped) MESH, and scale by TIV. The curve **subsystems** carry the
hail×solar specifics (PV array + tracker logistic params, capex weights); the math is the shared
framework.

The curve is **vendored** at ``data/hail/damage_curves/hail_solar_asset_capex_weighted.json`` (copied
from the legacy ``infrasure-damage-curves`` repo, with provenance in its metadata). V1 reads it
directly; once ``damage_modeling`` stabilizes a versioned ``damage_code()`` contract this swaps to an
import with zero behaviour change (the engine only needs the subsystem list).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from risk_engine.vulnerability import capex_weighted_damage_ratio, curve_cap

DEFAULT_CURVE_RELPATH = "data/hail/damage_curves/hail_solar_asset_capex_weighted.json"


def load_curve(path: str | Path) -> dict[str, Any]:
    """Load the curve artifact JSON (a dict with a ``subsystems`` list)."""
    return json.loads(Path(path).read_text())


def hail_damage_ratio(size_mm, curve: dict[str, Any]):
    """Asset damage ratio at the given MESH size(s), per the curve's capex-weighted subsystems."""
    return capex_weighted_damage_ratio(size_mm, curve["subsystems"])


def hail_curve_cap(curve: dict[str, Any]) -> float:
    """The curve's asymptotic max damage ratio (Σ capex_weight · L)."""
    return curve_cap(curve["subsystems"])
