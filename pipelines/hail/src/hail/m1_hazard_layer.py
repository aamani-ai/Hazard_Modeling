"""M1 hazard-layer build for hail (asset-free).

Collapses the reconciled M0 cell-day evidence (one row per served `cell_id` x accepted MRMS source
date) into ONE M1 hazard row per served `cell_id`: severe-hail-day frequency + raw/provisional MESH
severity summaries + explicit severity-tail QA flags.

This is the **peril** side of the M0/M1 vs M2-M4 boundary — no asset, no coupling, no loss. It emits
the typed hazard-layer object the shared `risk_engine` consumes downstream.

Lifted behaviour-preserving from the full-CONUS build notebook
(`Notebooks/hazard_conus_grid/hail/m1_hazard_layer/02_full_conus_build/01_mrms_v1_full_grid_hazard_layer.py`),
sections 2-3. The notebook's QA maps, artifact writing, and GCS upload stay in the notebook/driver.

`max_mesh_mm_log1p_display` is **not** part of the M1 contract: it is a log1p display transform of
`max_mesh_mm_raw_any_day` that the notebook's map section adds in place before writing, so it leaks
into the persisted parquet. The 52 columns in `M1_HAZARD_LAYER_COLUMNS` are the contract; the driver
may add display columns afterwards.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# The 52-column M1 hazard-layer contract, in order (the persisted parquet additionally carries the
# notebook map section's incidental `max_mesh_mm_log1p_display` as column 52).
M1_HAZARD_LAYER_COLUMNS = [
    "hazard",
    "m1_run_id",
    "cell_id",
    "lat_center",
    "lon_center",
    "state_abbr",
    "iso_rto",
    "source_set",
    "input_m0_reconciled_run_id",
    "source_product",
    "threshold_mm",
    "record_span_start",
    "record_span_end",
    "n_source_dates",
    "n_observed_days",
    "n_no_coverage_days",
    "n_no_hail_days",
    "n_sub_severe_days",
    "n_severe_hail_days",
    "observed_day_fraction",
    "observed_years",
    "lambda_cell_raw",
    "freq_dist",
    "freq_fit_status",
    "annual_count_years_for_diagnostics",
    "annual_count_mean_complete_years",
    "annual_count_variance_complete_years",
    "fano_phi_complete_years",
    "fano_phi_status",
    "sparse_cell_flag",
    "zero_hail_flag",
    "n_observed_native_pixels_total",
    "n_positive_native_pixels_total",
    "n_severe_native_pixels_total",
    "max_severe_native_pixels_single_day",
    "extreme_mesh_ge_300mm_flag",
    "extreme_mesh_cell_day_count",
    "max_mesh_mm_raw_any_day",
    "n_severe_days_with_size_sample",
    "mesh_max_mm_raw",
    "mesh_mean_mm_raw_on_severe_days",
    "mesh_p50_mm_raw_on_severe_days",
    "mesh_p90_mm_raw_on_severe_days",
    "mesh_p95_mm_raw_on_severe_days",
    "mesh_p99_mm_raw_on_severe_days",
    "mean_daily_severe_native_pixels_when_hail",
    "max_daily_severe_native_pixels_when_hail",
    "severity_magnitude_status",
    "size_dist_status",
    "qa_flags",
    "allowed_use",
    "not_allowed_use",
]

# Columns each reconciled-M0 daily partition must carry (the M0 -> M1 input contract).
REQUIRED_M0_COLUMNS = {
    "cell_id",
    "date",
    "lat_center",
    "lon_center",
    "state_abbr",
    "iso_rto",
    "coverage_status",
    "n_native_pixels_observed",
    "n_native_pixels_positive",
    "n_native_pixels_severe",
    "mesh_max_mm",
    "mesh_mean_severe_mm",
    "hail_day_flag",
    "threshold_mm",
}

# A raw MESH cell-day at or above this is flagged as a severity-tail QA case (not treated as a literal
# hail size). It is physically implausible as one-day max hail size and must not silently drive loss.
EXTREME_MESH_THRESHOLD_MM = 300.0


def build_m1_hazard_layer(
    partition_paths: list[Path],
    date_coverage: pd.DataFrame,
    reconciled_metadata: dict[str, Any],
    *,
    m1_run_id: str,
    reconciled_run_id: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Stream the reconciled M0 daily partitions into the one-row-per-cell M1 hazard layer.

    Args:
        partition_paths: sorted reconciled-M0 ``date=YYYY-MM-DD/part-000.parquet`` paths (the
            frequency denominator — one per accepted MRMS source date).
        date_coverage: the reconciled date-coverage sidecar (must have a ``date`` column).
        reconciled_metadata: the reconciled-M0 metadata dict (``n_dates``, ``n_served_cells``,
            ``n_output_rows``, ``source_product``).
        m1_run_id: the M1 run id stamped into the ``m1_run_id`` column.
        reconciled_run_id: the input M0 run id stamped into ``input_m0_reconciled_run_id``.

    Returns:
        ``(hazard_layer, diagnostics)`` where ``hazard_layer`` is the 52-column
        :data:`M1_HAZARD_LAYER_COLUMNS` contract (one row per served ``cell_id``) and ``diagnostics``
        holds scan provenance the notebook/driver writes into metadata.
    """
    expected_dates = int(reconciled_metadata["n_dates"])
    expected_cells = int(reconciled_metadata["n_served_cells"])
    expected_rows = int(reconciled_metadata["n_output_rows"])

    if len(partition_paths) != expected_dates:
        raise AssertionError(f"found {len(partition_paths)} daily partitions, expected {expected_dates}")
    if len(date_coverage) != expected_dates:
        raise AssertionError(f"date coverage rows {len(date_coverage)} != expected {expected_dates}")
    if expected_rows != expected_dates * expected_cells:
        raise AssertionError("metadata row contract does not equal dates x cells")

    # --- Stream daily partitions into cell-level accumulators -------------------------------------
    t0 = time.perf_counter()
    first = pd.read_parquet(partition_paths[0])

    missing_columns = sorted(REQUIRED_M0_COLUMNS - set(first.columns))
    if missing_columns:
        raise ValueError(f"input partition missing required columns: {missing_columns}")

    cell_base = (
        first[["cell_id", "lat_center", "lon_center", "state_abbr", "iso_rto"]]
        .drop_duplicates("cell_id")
        .sort_values("cell_id")
        .reset_index(drop=True)
    )
    if len(cell_base) != expected_cells:
        raise AssertionError(f"first partition cells {len(cell_base)} != expected {expected_cells}")
    if not cell_base["cell_id"].is_unique:
        raise AssertionError("cell_id is not unique in cell_base")

    cell_id_to_pos = {int(cell_id): i for i, cell_id in enumerate(cell_base["cell_id"].astype(int))}
    n_cells = len(cell_base)

    n_observed_days = np.zeros(n_cells, dtype=np.int32)
    n_no_coverage_days = np.zeros(n_cells, dtype=np.int32)
    n_no_hail_days = np.zeros(n_cells, dtype=np.int32)
    n_sub_severe_days = np.zeros(n_cells, dtype=np.int32)
    n_severe_hail_days = np.zeros(n_cells, dtype=np.int32)
    n_positive_native_pixels_total = np.zeros(n_cells, dtype=np.int64)
    n_severe_native_pixels_total = np.zeros(n_cells, dtype=np.int64)
    n_observed_native_pixels_total = np.zeros(n_cells, dtype=np.int64)
    max_mesh_mm_raw = np.full(n_cells, np.nan, dtype=np.float64)
    extreme_mesh_cell_day_count = np.zeros(n_cells, dtype=np.int32)
    max_severe_native_pixels_single_day = np.zeros(n_cells, dtype=np.int32)

    years = sorted(pd.to_datetime(date_coverage["date"]).dt.year.unique().tolist())
    complete_years = [year for year in years if 2021 <= int(year) <= 2025]
    year_to_col = {int(year): i for i, year in enumerate(complete_years)}
    annual_severe_counts = np.zeros((n_cells, len(complete_years)), dtype=np.int16)

    severe_rows: list[pd.DataFrame] = []
    row_count = 0
    duplicate_cell_date_count = 0
    bad_daily_row_counts: list[dict[str, Any]] = []

    for i, path in enumerate(partition_paths, start=1):
        day = pd.read_parquet(path)
        row_count += len(day)
        date_value = str(day["date"].iloc[0])
        if len(day) != expected_cells:
            bad_daily_row_counts.append({"date": date_value, "rows": len(day), "expected": expected_cells})
        if day.duplicated(["cell_id", "date"]).any():
            duplicate_cell_date_count += int(day.duplicated(["cell_id", "date"]).sum())

        positions = day["cell_id"].map(cell_id_to_pos).to_numpy()
        if np.isnan(positions).any():
            raise ValueError(f"unmapped cell_id in {path}")
        positions = positions.astype(np.int64)

        status = day["coverage_status"].astype(str)
        no_coverage = status.eq("no_native_pixel_coverage").to_numpy()
        no_hail = status.eq("observed_no_hail").to_numpy()
        sub_severe = status.eq("observed_sub_severe_hail").to_numpy()
        severe = status.eq("observed_severe_hail").to_numpy()
        observed = ~no_coverage

        n_observed_days[positions] += observed.astype(np.int32)
        n_no_coverage_days[positions] += no_coverage.astype(np.int32)
        n_no_hail_days[positions] += no_hail.astype(np.int32)
        n_sub_severe_days[positions] += sub_severe.astype(np.int32)
        n_severe_hail_days[positions] += severe.astype(np.int32)
        n_positive_native_pixels_total[positions] += day["n_native_pixels_positive"].fillna(0).to_numpy(dtype=np.int64)
        n_severe_native_pixels_total[positions] += day["n_native_pixels_severe"].fillna(0).to_numpy(dtype=np.int64)
        n_observed_native_pixels_total[positions] += day["n_native_pixels_observed"].fillna(0).to_numpy(dtype=np.int64)
        max_severe_native_pixels_single_day[positions] = np.maximum(
            max_severe_native_pixels_single_day[positions],
            day["n_native_pixels_severe"].fillna(0).to_numpy(dtype=np.int32),
        )

        mesh = day["mesh_max_mm"].astype("float64").to_numpy()
        current = max_mesh_mm_raw[positions]
        max_mesh_mm_raw[positions] = np.fmax(current, mesh)
        extreme_mask = np.nan_to_num(mesh, nan=-np.inf) >= EXTREME_MESH_THRESHOLD_MM
        extreme_mesh_cell_day_count[positions] += extreme_mask.astype(np.int32)

        year = pd.Timestamp(date_value).year
        if year in year_to_col:
            annual_severe_counts[positions, year_to_col[year]] += severe.astype(np.int16)

        severe_day = day[severe].copy()
        if not severe_day.empty:
            severe_rows.append(
                severe_day[
                    [
                        "cell_id",
                        "date",
                        "mesh_max_mm",
                        "mesh_mean_severe_mm",
                        "n_native_pixels_severe",
                        "source_key",
                    ]
                ]
            )

        if i == 1 or i % 250 == 0 or i == len(partition_paths):
            print(f"processed {i:,}/{len(partition_paths):,} daily partitions")

    scan_elapsed = time.perf_counter() - t0
    print(f"streaming scan elapsed seconds: {scan_elapsed:.2f}")

    if row_count != expected_rows:
        raise AssertionError(f"streamed rows {row_count} != expected {expected_rows}")
    if duplicate_cell_date_count:
        raise AssertionError(f"duplicate cell-date rows found: {duplicate_cell_date_count}")
    if bad_daily_row_counts:
        raise AssertionError(f"bad daily row counts: {bad_daily_row_counts[:5]}")

    severe_samples = pd.concat(severe_rows, ignore_index=True) if severe_rows else pd.DataFrame()

    # --- Build one-row-per-cell M1 layer ----------------------------------------------------------
    observed_years = np.divide(
        n_observed_days,
        365.25,
        out=np.zeros_like(n_observed_days, dtype=np.float64),
        where=n_observed_days > 0,
    )
    lambda_cell_raw = np.divide(
        n_severe_hail_days,
        observed_years,
        out=np.zeros_like(observed_years, dtype=np.float64),
        where=observed_years > 0,
    )
    observed_day_fraction = n_observed_days / expected_dates

    if severe_samples.empty:
        size_summary = pd.DataFrame(columns=["cell_id"])
    else:
        size_summary = (
            severe_samples.groupby("cell_id")
            .agg(
                n_severe_days_with_size_sample=("mesh_max_mm", "count"),
                mesh_max_mm_raw=("mesh_max_mm", "max"),
                mesh_mean_mm_raw_on_severe_days=("mesh_max_mm", "mean"),
                mesh_p50_mm_raw_on_severe_days=("mesh_max_mm", lambda s: s.quantile(0.50)),
                mesh_p90_mm_raw_on_severe_days=("mesh_max_mm", lambda s: s.quantile(0.90)),
                mesh_p95_mm_raw_on_severe_days=("mesh_max_mm", lambda s: s.quantile(0.95)),
                mesh_p99_mm_raw_on_severe_days=("mesh_max_mm", lambda s: s.quantile(0.99)),
                mean_daily_severe_native_pixels_when_hail=("n_native_pixels_severe", "mean"),
                max_daily_severe_native_pixels_when_hail=("n_native_pixels_severe", "max"),
            )
            .reset_index()
        )

    annual_mean_complete_years = (
        annual_severe_counts.mean(axis=1) if len(complete_years) else np.full(n_cells, np.nan, dtype=np.float64)
    )
    annual_variance_complete_years = (
        annual_severe_counts.var(axis=1, ddof=1) if len(complete_years) > 1 else np.full(n_cells, np.nan, dtype=np.float64)
    )
    fano_phi_complete_years = np.divide(
        annual_variance_complete_years,
        annual_mean_complete_years,
        out=np.full(n_cells, np.nan, dtype=np.float64),
        where=annual_mean_complete_years > 0,
    )

    hazard_layer = cell_base.copy()
    hazard_layer.insert(0, "hazard", "hail")
    hazard_layer.insert(1, "m1_run_id", m1_run_id)
    hazard_layer["source_set"] = "MRMS_ONLY"
    hazard_layer["input_m0_reconciled_run_id"] = reconciled_run_id
    hazard_layer["source_product"] = reconciled_metadata.get("source_product", "CONUS/MESH_Max_1440min_00.50")
    hazard_layer["threshold_mm"] = 25.4
    hazard_layer["record_span_start"] = str(pd.to_datetime(date_coverage["date"]).min().date())
    hazard_layer["record_span_end"] = str(pd.to_datetime(date_coverage["date"]).max().date())
    hazard_layer["n_source_dates"] = expected_dates
    hazard_layer["n_observed_days"] = n_observed_days
    hazard_layer["n_no_coverage_days"] = n_no_coverage_days
    hazard_layer["n_no_hail_days"] = n_no_hail_days
    hazard_layer["n_sub_severe_days"] = n_sub_severe_days
    hazard_layer["n_severe_hail_days"] = n_severe_hail_days
    hazard_layer["observed_day_fraction"] = observed_day_fraction
    hazard_layer["observed_years"] = observed_years
    hazard_layer["lambda_cell_raw"] = lambda_cell_raw
    hazard_layer["freq_dist"] = "poisson_v1_default"
    hazard_layer["freq_fit_status"] = "poisson_default_no_cellwise_overfit"
    hazard_layer["annual_count_years_for_diagnostics"] = ",".join(str(year) for year in complete_years)
    hazard_layer["annual_count_mean_complete_years"] = annual_mean_complete_years
    hazard_layer["annual_count_variance_complete_years"] = annual_variance_complete_years
    hazard_layer["fano_phi_complete_years"] = fano_phi_complete_years
    hazard_layer["fano_phi_status"] = np.where(
        np.isfinite(fano_phi_complete_years),
        "diagnostic_complete_years_only",
        "not_available_zero_or_sparse_complete_year_counts",
    )
    hazard_layer["sparse_cell_flag"] = n_severe_hail_days < 5
    hazard_layer["zero_hail_flag"] = n_severe_hail_days == 0
    hazard_layer["n_observed_native_pixels_total"] = n_observed_native_pixels_total
    hazard_layer["n_positive_native_pixels_total"] = n_positive_native_pixels_total
    hazard_layer["n_severe_native_pixels_total"] = n_severe_native_pixels_total
    hazard_layer["max_severe_native_pixels_single_day"] = max_severe_native_pixels_single_day
    hazard_layer["extreme_mesh_ge_300mm_flag"] = extreme_mesh_cell_day_count > 0
    hazard_layer["extreme_mesh_cell_day_count"] = extreme_mesh_cell_day_count
    hazard_layer["max_mesh_mm_raw_any_day"] = max_mesh_mm_raw

    hazard_layer = hazard_layer.merge(size_summary, on="cell_id", how="left")

    size_columns = [
        "n_severe_days_with_size_sample",
        "mesh_max_mm_raw",
        "mesh_mean_mm_raw_on_severe_days",
        "mesh_p50_mm_raw_on_severe_days",
        "mesh_p90_mm_raw_on_severe_days",
        "mesh_p95_mm_raw_on_severe_days",
        "mesh_p99_mm_raw_on_severe_days",
        "mean_daily_severe_native_pixels_when_hail",
        "max_daily_severe_native_pixels_when_hail",
    ]
    for col in size_columns:
        if col not in hazard_layer.columns:
            hazard_layer[col] = np.nan

    hazard_layer["n_severe_days_with_size_sample"] = hazard_layer["n_severe_days_with_size_sample"].fillna(0).astype("int64")
    hazard_layer["severity_magnitude_status"] = np.select(
        [
            hazard_layer["n_severe_hail_days"].eq(0),
            hazard_layer["extreme_mesh_ge_300mm_flag"],
        ],
        [
            "no_severe_days",
            "raw_mesh_tail_requires_qa",
        ],
        default="raw_mesh_body_only",
    )
    hazard_layer["size_dist_status"] = np.select(
        [
            hazard_layer["n_severe_hail_days"].eq(0),
            hazard_layer["extreme_mesh_ge_300mm_flag"],
        ],
        [
            "no_observed_severe_days",
            "raw_empirical_size_provisional_tail_flag",
        ],
        default="raw_empirical_size_body_available",
    )
    hazard_layer["qa_flags"] = (
        "mrms_only_v1;raw_mrms_mesh;frequency_ready_after_m0_review;"
        + np.where(hazard_layer["sparse_cell_flag"], "sparse_cell;", "")
        + np.where(hazard_layer["zero_hail_flag"], "zero_hail_cell;", "")
        + np.where(hazard_layer["extreme_mesh_ge_300mm_flag"], "severity_tail_requires_qa;", "")
    )
    hazard_layer["allowed_use"] = "full_conus_screening_and_m2_m4_smoke_with_tail_warnings"
    hazard_layer["not_allowed_use"] = "reportable_loss_metrics_or_final_calibrated_hail_climatology"

    hazard_layer = hazard_layer[M1_HAZARD_LAYER_COLUMNS]

    diagnostics: dict[str, Any] = {
        "expected_dates": expected_dates,
        "expected_cells": expected_cells,
        "expected_rows": expected_rows,
        "partition_files": len(partition_paths),
        "streamed_rows": int(row_count),
        "duplicate_cell_date_rows": int(duplicate_cell_date_count),
        "bad_daily_row_counts": bad_daily_row_counts,
        "severe_cell_day_samples": int(len(severe_samples)),
        "complete_years": complete_years,
        "scan_elapsed_seconds": round(scan_elapsed, 3),
    }
    return hazard_layer, diagnostics
