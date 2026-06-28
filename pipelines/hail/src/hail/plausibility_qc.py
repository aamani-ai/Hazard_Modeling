"""Plausibility QC for the hail M1 hazard layer (asset-free) — the decided V1 rule.

Spec: docs/extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md (distilled from the 04 MESH-nature
research). Two plausibility failures in the raw MRMS-MESH signal, handled WITHOUT touching frequency:

  MAGNITUDE artifact   raw MESH up to 1,437 mm; 585 CONUS cells >= 300 mm  -> corrupts SEVERITY
  FREQUENCY artifact   lambda_cell up to ~45 severe days/yr                -> corrupts FREQUENCY

The rule (M0/M1, asset-free):
  - MAGNITUDE: physical cap + flag at the US record (Vivian, SD 2010 = 8.0 in = 203.2 mm; the rule's
    "~200 mm"). Anything above has no physical precedent -> cap the severity SUMMARY at the ceiling,
    keep the raw value beside it, flag it. >= 300 mm = hard artifact. Never delete.
  - FREQUENCY: flag suspicious high-rate cells (OUR owned heuristic -- no literature standard, so a
    percentile cut on lambda; spatial pooling/shrinkage deferred to V1.5) and hold them out of
    reportable loss. The rate itself is NOT changed.

This step is **additive**: the raw severity columns and ALL frequency columns are preserved unchanged
(the M1 reproduction gate stays valid); QC adds the capped twins, the flags, and a reportable-eligibility
label. For SOLAR loss the M3 100 mm curve clamp already neutralizes the magnitude tail -- this M1 cap
does a different job: keeping the asset-free hazard layer physically honest and protecting future assets
that saturate above 100 mm.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# Physical ceiling: US hailstone DIAMETER record, Vivian SD 2010 = 8.0 in = 203.2 mm (NCEI/NWS).
# The decided rule states this as "~200 mm"; we use the exact record value.
US_RECORD_HAIL_MM = 203.2
# At/above this, the value is a hard artifact (no real hailstone) -- flagged, never deleted.
HARD_ARTIFACT_MM = 300.0
# Frequency-spike heuristic (OURS; no literature standard): flag the extreme tail of the per-cell
# severe-day rate among cells that have any severe day. Tunable; pooling/shrinkage is the deferred fix.
FREQUENCY_SPIKE_PERCENTILE = 99.5

# Raw M1 severity-summary fields -> their physically-capped twins (raw is preserved).
SEVERITY_CAP_MAP = {
    "max_mesh_mm_raw_any_day": "max_mesh_mm_capped_any_day",
    "mesh_max_mm_raw": "mesh_max_mm_capped",
    "mesh_mean_mm_raw_on_severe_days": "mesh_mean_mm_capped_on_severe_days",
    "mesh_p50_mm_raw_on_severe_days": "mesh_p50_mm_capped_on_severe_days",
    "mesh_p90_mm_raw_on_severe_days": "mesh_p90_mm_capped_on_severe_days",
    "mesh_p95_mm_raw_on_severe_days": "mesh_p95_mm_capped_on_severe_days",
    "mesh_p99_mm_raw_on_severe_days": "mesh_p99_mm_capped_on_severe_days",
}

# Columns added by QC (the contract extension on top of the 52 raw M1 columns).
QC_COLUMNS = [
    *SEVERITY_CAP_MAP.values(),
    "physical_cap_mm",
    "severity_capped_flag",
    "hard_artifact_flag",
    "frequency_spike_threshold_lambda",
    "frequency_spike_flag",
    "reportable_loss_eligible",
    "plausibility_qc_status",
]


def apply_plausibility_qc(
    hazard_layer: pd.DataFrame,
    *,
    cap_mm: float = US_RECORD_HAIL_MM,
    hard_artifact_mm: float = HARD_ARTIFACT_MM,
    spike_percentile: float = FREQUENCY_SPIKE_PERCENTILE,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply the V1 plausibility QC to an M1 hazard layer; return (qc'd layer, summary).

    Additive and non-destructive: raw severity + frequency columns are untouched. ``np.minimum``
    propagates NaN, so capped twins are NaN exactly where the raw summary is NaN (no-severity cells).
    """
    hl = hazard_layer.copy()

    # --- MAGNITUDE: cap the severity summary at the physical ceiling (raw preserved) ---
    for raw_col, capped_col in SEVERITY_CAP_MAP.items():
        raw = hl[raw_col].to_numpy(dtype="float64")
        hl[capped_col] = np.minimum(raw, cap_mm)

    max_raw = hl["max_mesh_mm_raw_any_day"].to_numpy(dtype="float64")
    hl["physical_cap_mm"] = cap_mm
    hl["severity_capped_flag"] = max_raw > cap_mm
    # >= 300 mm hard artifact -- reuse the proven M1 flag (equivalent to max_raw >= 300; never delete).
    hl["hard_artifact_flag"] = hl["extreme_mesh_ge_300mm_flag"].astype(bool)

    # --- FREQUENCY: flag the extreme-rate tail among cells with any severe day (rate NOT changed) ---
    lam = hl["lambda_cell_raw"].to_numpy(dtype="float64")
    nonzero = lam[lam > 0.0]
    spike_threshold = float(np.percentile(nonzero, spike_percentile)) if nonzero.size else float("inf")
    hl["frequency_spike_threshold_lambda"] = spike_threshold
    hl["frequency_spike_flag"] = lam > spike_threshold

    # --- HOLD-OUT: frequency-spike cells are not eligible for reportable loss (V1 rule) ---
    hl["reportable_loss_eligible"] = ~hl["frequency_spike_flag"].to_numpy(dtype=bool)

    # --- additive QC status label ---
    hl["plausibility_qc_status"] = np.select(
        [hl["hard_artifact_flag"].to_numpy(dtype=bool), hl["severity_capped_flag"].to_numpy(dtype=bool)],
        ["hard_artifact_capped", "physically_capped"],
        default="within_physical_range",
    )

    summary: dict[str, Any] = {
        "physical_cap_mm": float(cap_mm),
        "hard_artifact_mm": float(hard_artifact_mm),
        "spike_percentile": float(spike_percentile),
        "spike_threshold_lambda": spike_threshold,
        "n_cells": int(len(hl)),
        "n_severity_capped": int(hl["severity_capped_flag"].sum()),
        "n_hard_artifact": int(hl["hard_artifact_flag"].sum()),
        "n_frequency_spike": int(hl["frequency_spike_flag"].sum()),
        "n_reportable_eligible": int(hl["reportable_loss_eligible"].sum()),
        "max_raw_mesh_mm": float(np.nanmax(max_raw)),
        "max_capped_mesh_mm": float(np.nanmax(hl["max_mesh_mm_capped_any_day"].to_numpy(dtype="float64"))),
    }
    return hl, summary
