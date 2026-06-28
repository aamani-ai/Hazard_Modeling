"""MRMS hail M0 source adapter: raw MESH tile -> per-cell-day evidence.

Extracted verbatim (behaviour-preserving) from scripts/run_mrms_v1_m0_daily_evidence_batch.py.
The single change from the original: the raw-tile cache directory is an explicit ``cache_dir``
argument instead of a module global, so the package carries no repo-relative path. Given the same
raw tile + served mask, the output is byte-identical to the original (proven by
tests/test_adapter_reproduces_m0.py).
"""

from __future__ import annotations

import gzip
import os
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
import xarray as xr

from .config import (
    THRESHOLD_MM,
    PRODUCT,
    GRID_RESOLUTION_DEG,
    N_LON,
    COVERAGE_NO_COVERAGE,
    COVERAGE_NO_HAIL,
    COVERAGE_SUB_SEVERE,
    COVERAGE_SEVERE,
    QA_FLAG_NO_COVERAGE,
    QA_FLAGS_OBSERVED,
    M0_EVIDENCE_COLUMNS,
)


@dataclass
class BatchContext:
    served: pd.DataFrame
    served_cell_ids: set[int]


def source_timestamp_from_name(path_or_key: str) -> pd.Timestamp:
    match = re.search(r"_(\d{8})-(\d{6})\.grib2\.gz$", Path(path_or_key).name)
    if not match:
        raise ValueError(f"cannot parse MRMS timestamp from {path_or_key}")
    return pd.to_datetime(f"{match.group(1)}{match.group(2)}", format="%Y%m%d%H%M%S", utc=True)


def fetch_inventory_source(row: pd.Series, cache_dir: Path) -> Path:
    """Return the local raw MESH tile for an inventory row, downloading + caching if absent."""
    key = str(row["selected_source_key"])
    uri = str(row["selected_source_uri_https"])
    cache_dir = Path(cache_dir)
    local = cache_dir / Path(key).name
    cache_dir.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.stat().st_size > 0:
        return local

    response = requests.get(uri, timeout=180)
    response.raise_for_status()
    local.write_bytes(response.content)
    return local


def read_mrms_grib(gz_path: Path) -> xr.DataArray:
    raw = gzip.decompress(Path(gz_path).read_bytes())
    with tempfile.NamedTemporaryFile(suffix=".grib2", delete=False) as tf:
        tf.write(raw)
        tmp = tf.name
    try:
        ds = xr.open_dataset(tmp, engine="cfgrib", backend_kwargs={"indexpath": ""})
        ds.load()
        da = ds[list(ds.data_vars)[0]].copy()
        ds.close()
        return da
    finally:
        os.unlink(tmp)


def native_points_to_cell_id(lat: np.ndarray, lon360: np.ndarray) -> np.ndarray:
    lat_idx = np.rint((90.0 - lat) / GRID_RESOLUTION_DEG).astype("int64")
    lon_idx = np.rint(lon360 / GRID_RESOLUTION_DEG).astype("int64") % N_LON
    return lat_idx * N_LON + lon_idx


def native_observed_counts_for_served_cells(mrms_da: xr.DataArray, served_mask: pd.DataFrame) -> pd.DataFrame:
    lat_native_idx = np.rint((90.0 - mrms_da.latitude.values) / GRID_RESOLUTION_DEG).astype("int64")
    lon_native_idx = np.rint(mrms_da.longitude.values / GRID_RESOLUTION_DEG).astype("int64") % N_LON
    lat_counts = pd.Series(lat_native_idx).value_counts().rename("n_native_rows")
    lon_counts = pd.Series(lon_native_idx).value_counts().rename("n_native_cols")

    counts = served_mask[["cell_id", "lat_idx", "lon_idx"]].copy()
    counts["n_native_rows"] = counts["lat_idx"].map(lat_counts).fillna(0).astype("int64")
    counts["n_native_cols"] = counts["lon_idx"].map(lon_counts).fillna(0).astype("int64")
    counts["n_native_pixels_observed"] = counts["n_native_rows"] * counts["n_native_cols"]
    return counts[["cell_id", "n_native_pixels_observed"]]


def aggregate_pixels_to_cells(
    context: BatchContext,
    mrms_da: xr.DataArray,
    values: np.ndarray,
    mask: np.ndarray,
    value_name: str,
) -> pd.DataFrame:
    y, x = np.where(mask)
    if len(y) == 0:
        return pd.DataFrame(columns=["cell_id"])

    cell_ids = native_points_to_cell_id(mrms_da.latitude.values[y], mrms_da.longitude.values[x])
    pixel_df = pd.DataFrame({"cell_id": cell_ids, value_name: values[y, x]})
    pixel_df = pixel_df[pixel_df["cell_id"].isin(context.served_cell_ids)]
    return pixel_df


def build_daily_panel(context: BatchContext, row: pd.Series, cache_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Transform one accepted MRMS source date into one row per served cell (+ read stats)."""
    date_str = str(row["date"])
    t0 = time.perf_counter()
    source_path = fetch_inventory_source(row, cache_dir)
    da = read_mrms_grib(source_path)
    arr = da.values.astype("float32")
    source_timestamp = source_timestamp_from_name(source_path.name)

    observed_counts = native_observed_counts_for_served_cells(da, context.served)
    positive_pixels = aggregate_pixels_to_cells(context, da, arr, arr > 0, "mesh_mm")
    severe_pixels = aggregate_pixels_to_cells(context, da, arr, arr >= THRESHOLD_MM, "mesh_mm")

    positive_agg = (
        positive_pixels.groupby("cell_id")["mesh_mm"]
        .agg(n_native_pixels_positive="size", mesh_max_mm="max", mesh_mean_positive_mm="mean")
        .reset_index()
        if not positive_pixels.empty
        else pd.DataFrame(columns=["cell_id", "n_native_pixels_positive", "mesh_max_mm", "mesh_mean_positive_mm"])
    )

    severe_agg = (
        severe_pixels.groupby("cell_id")["mesh_mm"]
        .agg(
            n_native_pixels_severe="size",
            mesh_mean_severe_mm="mean",
            mesh_p50_severe_mm=lambda s: s.quantile(0.50),
            mesh_p90_severe_mm=lambda s: s.quantile(0.90),
            mesh_p95_severe_mm=lambda s: s.quantile(0.95),
        )
        .reset_index()
        if not severe_pixels.empty
        else pd.DataFrame(
            columns=[
                "cell_id",
                "n_native_pixels_severe",
                "mesh_mean_severe_mm",
                "mesh_p50_severe_mm",
                "mesh_p90_severe_mm",
                "mesh_p95_severe_mm",
            ]
        )
    )

    panel = (
        context.served.merge(observed_counts, on="cell_id", how="left")
        .merge(positive_agg, on="cell_id", how="left")
        .merge(severe_agg, on="cell_id", how="left")
    )

    for col in ["n_native_pixels_observed", "n_native_pixels_positive", "n_native_pixels_severe"]:
        panel[col] = panel[col].fillna(0).astype("int64")

    panel["hazard"] = "hail"
    panel["date"] = pd.Timestamp(date_str)
    panel["source_product"] = PRODUCT
    panel["source_key"] = row["selected_source_key"]
    panel["source_uri_https"] = row["selected_source_uri_https"]
    panel["source_timestamp"] = source_timestamp
    panel["threshold_mm"] = THRESHOLD_MM
    panel["severe_area_km2_approx"] = panel["n_native_pixels_severe"].astype(float)
    panel["hail_day_flag"] = panel["n_native_pixels_severe"] > 0

    panel["coverage_status"] = np.select(
        [
            panel["n_native_pixels_observed"] == 0,
            panel["n_native_pixels_severe"] > 0,
            panel["n_native_pixels_positive"] > 0,
        ],
        [COVERAGE_NO_COVERAGE, COVERAGE_SEVERE, COVERAGE_SUB_SEVERE],
        default=COVERAGE_NO_HAIL,
    )

    panel["qa_flags"] = np.where(
        panel["coverage_status"] == COVERAGE_NO_COVERAGE,
        QA_FLAG_NO_COVERAGE,
        QA_FLAGS_OBSERVED,
    )

    panel = panel[M0_EVIDENCE_COLUMNS].sort_values("cell_id").reset_index(drop=True)

    if len(panel) != len(context.served):
        raise AssertionError(f"{date_str}: expected {len(context.served)} rows, got {len(panel)}")
    if not panel["cell_id"].is_unique:
        raise AssertionError(f"{date_str}: duplicate cell_id rows")

    stats = {
        "date": date_str,
        "source_path": str(source_path),
        "source_key": row["selected_source_key"],
        "source_timestamp": source_timestamp.isoformat(),
        "source_size_bytes": int(source_path.stat().st_size),
        "read_status": "ok",
        "native_grid_shape": f"{da.shape[0]}x{da.shape[1]}",
        "native_positive_pixel_count": int((arr > 0).sum()),
        "native_severe_pixel_count": int((arr >= THRESHOLD_MM).sum()),
        "served_positive_pixel_count": int(panel["n_native_pixels_positive"].sum()),
        "served_severe_pixel_count": int(panel["n_native_pixels_severe"].sum()),
        "served_severe_cell_count": int((panel["coverage_status"] == COVERAGE_SEVERE).sum()),
        "served_sub_severe_cell_count": int((panel["coverage_status"] == COVERAGE_SUB_SEVERE).sum()),
        "served_no_hail_cell_count": int((panel["coverage_status"] == COVERAGE_NO_HAIL).sum()),
        "served_no_coverage_cell_count": int((panel["coverage_status"] == COVERAGE_NO_COVERAGE).sum()),
        "max_mesh_mm": None if pd.isna(panel["mesh_max_mm"].max()) else float(panel["mesh_max_mm"].max()),
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
    }
    return panel, stats
