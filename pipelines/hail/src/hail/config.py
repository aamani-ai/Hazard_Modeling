"""Hail MRMS-M0 source config — constants lifted verbatim from the M0 ingest script.

These are the hail/MRMS-specific parameters that the generic engine/orchestration must NOT bake in
(they become a new peril's config under the five-blank adapter contract).
"""

from __future__ import annotations

# Severe-hail threshold (1 inch) and the MRMS product key.
THRESHOLD_MM = 25.4
PRODUCT = "CONUS/MESH_Max_1440min_00.50"

# The 0.25-degree benchmark grid mapping: cell_id = lat_idx * N_LON + lon_idx.
GRID_RESOLUTION_DEG = 0.25
N_LON = 1440

# coverage_status enum. The first four are the reconcile contract's ALLOWED_STATUSES.
COVERAGE_NO_COVERAGE = "no_native_pixel_coverage"
COVERAGE_NO_HAIL = "observed_no_hail"
COVERAGE_SUB_SEVERE = "observed_sub_severe_hail"
COVERAGE_SEVERE = "observed_severe_hail"
COVERAGE_STATUSES = (
    COVERAGE_NO_COVERAGE,
    COVERAGE_NO_HAIL,
    COVERAGE_SUB_SEVERE,
    COVERAGE_SEVERE,
)

# qa_flags strings written per cell-day.
QA_FLAG_NO_COVERAGE = "no_native_pixel_coverage"
QA_FLAGS_OBSERVED = "raw_mrms_mesh;negative_values_masked;v1_m0_batch"

# The exact column order of one M0 daily cell-evidence row.
M0_EVIDENCE_COLUMNS = [
    "hazard",
    "cell_id",
    "date",
    "source_product",
    "source_key",
    "source_uri_https",
    "source_timestamp",
    "threshold_mm",
    "lat_center",
    "lon_center",
    "state_abbr",
    "iso_rto",
    "n_native_pixels_observed",
    "n_native_pixels_positive",
    "n_native_pixels_severe",
    "severe_area_km2_approx",
    "mesh_max_mm",
    "mesh_mean_positive_mm",
    "mesh_mean_severe_mm",
    "mesh_p50_severe_mm",
    "mesh_p90_severe_mm",
    "mesh_p95_severe_mm",
    "hail_day_flag",
    "coverage_status",
    "qa_flags",
]
