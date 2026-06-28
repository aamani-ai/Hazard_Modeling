"""Canonical exposure profiles + run constants for the CONUS grid driver.

The canonical asset is the grid's exposure input — the *only* thing that differs from the deep-per-asset
driver (DD-G11). Verbatim from the worked hail×solar smoke (§0): a fixed 100 MW solar plant placed at
every served cell, so cells are comparable on identical exposure.
"""

from __future__ import annotations

CANONICAL_SOLAR: dict = {
    "asset_type": "solar",
    "capacity_mw": 100.0,
    "asset_area_km2": 1.5,
    "tiv_usd_per_kwp": 1483.0,
}
CANONICAL_SOLAR["tiv_usd"] = CANONICAL_SOLAR["capacity_mw"] * 1000.0 * CANONICAL_SOLAR["tiv_usd_per_kwp"]

# Severity policies (the raw-vs-capped sensitivity axis). The cap is a diagnostic, NOT a calibration.
SEVERITY_POLICIES: dict = {
    "raw_mrms": {"cap_mm": None, "description": "raw MRMS MESH; preserved for audit, provisional for loss"},
    "cap_100mm_sensitivity": {
        "cap_mm": 100.0,
        "description": "diagnostic cap at 100 mm to test whether metrics are tail artifacts",
    },
}

# Monte-Carlo run constants (match the worked smoke so the gate reproduces bit-for-bit).
SEED = 20260618
MC_YEARS_DEFAULT = 250000
