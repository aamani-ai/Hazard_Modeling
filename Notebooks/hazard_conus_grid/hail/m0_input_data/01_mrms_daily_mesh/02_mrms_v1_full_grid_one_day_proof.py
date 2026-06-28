# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Hazard (.venv 3.12)
#     language: python
#     name: hazard_modeling
# ---

# %% [markdown]
# # Hail V1 - MRMS Full-Grid One-Day Proof
#
# **Peril:** hail - **Layer:** M0 daily cell evidence - **Product:** `hazard_conus_grid` V1
#
# This notebook is the first implementation step for the MRMS-only V1 grid build:
#
# ```text
# one MRMS daily MESH tile
#   -> every served CONUS benchmark cell
#   -> explicit coverage/no-hail/sub-severe/severe status
#   -> proof artifact + QA summary
# ```
#
# It deliberately does **not** estimate annual frequency, use MYRORSS, de-bias MESH, fit tails, or run
# loss metrics. Its job is to prove the all-cell M0 evidence contract before a full-record/GCP run.
#
# Plan reference:
#
# - `docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`
# - `docs/plans/hazard_conus_grid/decisions.md` / DD-G5
# - `docs/principles/notebook_work/exploratory_data_notebooks.md`

# %% [markdown]
# ## 0 - Scope and non-goals
#
# This notebook does:
#
# 1. Load the pinned served CONUS benchmark cell mask.
# 2. Read one cached MRMS `MESH_Max_1440min` daily tile.
# 3. Aggregate native MRMS pixels to benchmark `cell_id`.
# 4. Materialize **one row per served cell**.
# 5. Write proof artifacts and QA metadata.
#
# It does not:
#
# - run the full MRMS record;
# - compute `lambda_cell`;
# - promote any MYRORSS evidence into V1;
# - use NOAA/SPC reports or NRI as model inputs;
# - produce reportable EAL/PML/VaR/TVaR.

# %%
from __future__ import annotations

import gzip
import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import xarray as xr
from IPython.display import Image, display

plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 120})


def _repo_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise FileNotFoundError("repo root not found")


ROOT = _repo_root()
GRID_DIR = ROOT / "data" / "hazard_conus_grid" / "common" / "benchmark_grid"
HAIL_GRID_DIR = ROOT / "data" / "hazard_conus_grid" / "hail"
MRMS_CACHE = ROOT / "data" / "hail" / "mrms_raw"

THRESHOLD_MM = 25.4
PRODUCT = "CONUS/MESH_Max_1440min_00.50"
PROOF_DATE = "20240601"
OUTPUT_VERSION = "v2026_06_16"

PROOF_DIR = HAIL_GRID_DIR / "m0_mrms_v1_one_day_proof"
QA_DIR = HAIL_GRID_DIR / "qa"
DAILY_PANEL_PARQUET = PROOF_DIR / f"mrms_v1_one_day_full_grid_daily_panel_{PROOF_DATE}_{OUTPUT_VERSION}.parquet"
SUMMARY_CSV = PROOF_DIR / f"mrms_v1_one_day_status_summary_{PROOF_DATE}_{OUTPUT_VERSION}.csv"
TOP_CELLS_CSV = PROOF_DIR / f"mrms_v1_one_day_top_cells_{PROOF_DATE}_{OUTPUT_VERSION}.csv"
METADATA_JSON = PROOF_DIR / f"mrms_v1_one_day_metadata_{PROOF_DATE}_{OUTPUT_VERSION}.json"
STATUS_MAP_PNG = QA_DIR / f"mrms_v1_one_day_status_map_{PROOF_DATE}_{OUTPUT_VERSION}.png"

print("repo root:", ROOT)
print("proof date:", PROOF_DATE)
print("source product:", PRODUCT)
print("threshold_mm:", THRESHOLD_MM)

# %% [markdown]
# ## 1 - Benchmark grid and row contract
#
# V1 uses the served CONUS mask already pinned in the grid plan. The proof must produce exactly one row for
# every served `cell_id`.

# %%
served = pd.read_csv(GRID_DIR / "served_conus_cell_ids_v2026_06.csv")
served["cell_id"] = served["cell_id"].astype("int64")

required_grid_columns = ["cell_id", "lat_idx", "lon_idx", "lat_center", "lon_center", "state_abbr", "iso_rto"]
missing = sorted(set(required_grid_columns) - set(served.columns))
if missing:
    raise ValueError(f"served mask missing columns: {missing}")
if not served["cell_id"].is_unique:
    raise ValueError("served mask cell_id is not unique")

served = served[required_grid_columns].copy()
served_cell_ids = set(served["cell_id"])

grid_summary = pd.DataFrame(
    [
        ("served_rows", len(served), "cells", "must equal output rows"),
        ("unique_cell_id", served["cell_id"].is_unique, "bool", "join-key integrity"),
        ("lat_range", f"{served.lat_center.min():.2f} to {served.lat_center.max():.2f}", "degrees", "map check"),
        ("lon_range", f"{served.lon_center.min():.2f} to {served.lon_center.max():.2f}", "degrees", "map check"),
    ],
    columns=["item", "value", "unit/base", "why it matters"],
)
display(grid_summary)

# %% [markdown]
# **Takeaway.** The expected output denominator is the served mask: currently 13,085 rows. A sparse severe-only
# table is not enough for V1 because zero-hail days and no-data states would be ambiguous.

# %% [markdown]
# ## 2 - MRMS source reader
#
# This reuses the proven reader from the selected-cell MRMS notebook, but the output contract changes from
# sparse positive rows to a full served-cell panel.

# %%
@dataclass
class MRMSDailyMesh:
    product: str
    cache_dir: Path

    bucket: str = "https://noaa-mrms-pds.s3.amazonaws.com"
    ns: str = "{http://s3.amazonaws.com/doc/2006-03-01/}"

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.cache_dir / "_manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}

    def list_day(self, ymd: str) -> list[str]:
        response = requests.get(
            self.bucket + "/",
            timeout=40,
            params={"list-type": "2", "prefix": f"{self.product}/{ymd}/", "max-keys": "1000"},
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
        return sorted(e.find(self.ns + "Key").text for e in root.findall(self.ns + "Contents"))

    def get_day(self, ymd: str) -> Path | None:
        """Return local path to the day's last tile; download only if missing."""
        cached = self.manifest.get(ymd)
        if cached and (self.cache_dir / cached).exists():
            return self.cache_dir / cached

        local_candidates = sorted(self.cache_dir.glob(f"*{ymd}*.grib2.gz"))
        if local_candidates:
            local = local_candidates[-1]
            self.manifest[ymd] = local.name
            self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n")
            return local

        keys = self.list_day(ymd)
        if not keys:
            return None

        key = keys[-1]
        local = self.cache_dir / key.split("/")[-1]
        if not local.exists():
            response = requests.get(f"{self.bucket}/{key}", timeout=120)
            response.raise_for_status()
            local.write_bytes(response.content)

        self.manifest[ymd] = local.name
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n")
        return local


def read_mrms_grib(gz_path: Path) -> xr.DataArray:
    raw = gzip.decompress(gz_path.read_bytes())
    with tempfile.NamedTemporaryFile(suffix=".grib2", delete=False) as tf:
        tf.write(raw)
        tmp = tf.name
    try:
        ds = xr.open_dataset(tmp, engine="cfgrib", backend_kwargs={"indexpath": ""})
        ds.load()
        return ds[list(ds.data_vars)[0]]
    finally:
        os.unlink(tmp)


def mrms_source_timestamp(gz_path: Path) -> pd.Timestamp:
    match = re.search(r"_(\d{8})-(\d{6})\.grib2\.gz$", gz_path.name)
    if not match:
        raise ValueError(f"cannot parse MRMS timestamp from {gz_path.name}")
    return pd.to_datetime(f"{match.group(1)}{match.group(2)}", format="%Y%m%d%H%M%S", utc=True)


mrms = MRMSDailyMesh(PRODUCT, MRMS_CACHE)
source_path = mrms.get_day(PROOF_DATE)
if source_path is None:
    raise FileNotFoundError(f"no MRMS tile found for {PROOF_DATE}")

source_timestamp = mrms_source_timestamp(source_path)
print("source file:", source_path.relative_to(ROOT))
print("source timestamp:", source_timestamp)

# %%
da = read_mrms_grib(source_path)
arr = da.values.astype("float32")

source_summary = pd.DataFrame(
    [
        ("shape", f"{da.shape[0]} x {da.shape[1]}", "native rows x cols"),
        ("native_cells", f"{da.size:,}", "native MRMS pixels"),
        ("lat_range", f"{float(da.latitude.min()):.3f} to {float(da.latitude.max()):.3f}", "degrees"),
        ("lon_range", f"{float(da.longitude.min()):.3f} to {float(da.longitude.max()):.3f}", "0-360 degrees"),
        ("min_raw_value", float(np.nanmin(arr)), "negative sentinel / no-hail convention"),
        ("max_raw_value", float(np.nanmax(arr)), "mm"),
        ("positive_pixels", int((arr > 0).sum()), "native pixels with positive MESH"),
        ("severe_pixels", int((arr >= THRESHOLD_MM).sum()), f"native pixels >= {THRESHOLD_MM} mm"),
    ],
    columns=["item", "value", "unit/base"],
)
display(source_summary)

# %% [markdown]
# **Takeaway.** The source denominator is the full MRMS native grid, but V1 stores evidence at the benchmark
# cell denominator. Negative values are not hail sizes and are not allowed into size statistics.

# %% [markdown]
# ## 3 - Native-pixel aggregation helpers
#
# V1 status is based on each served cell's observed native pixels:
#
# - `observed_severe_hail`: at least one native pixel `>= 25.4 mm`;
# - `observed_sub_severe_hail`: positive MESH exists, but no severe native pixel;
# - `observed_no_hail`: native pixels exist, but no positive MESH;
# - `no_native_pixel_coverage`: no native pixel center maps to the served cell.

# %%
def native_points_to_cell_id(lat: np.ndarray, lon360: np.ndarray) -> np.ndarray:
    lat_idx = np.rint((90.0 - lat) / 0.25).astype("int64")
    lon_idx = (np.rint(lon360 / 0.25).astype("int64") % 1440)
    return lat_idx * 1440 + lon_idx


def native_observed_counts_for_served_cells(mrms_da: xr.DataArray, served_mask: pd.DataFrame) -> pd.DataFrame:
    lat_native_idx = np.rint((90.0 - mrms_da.latitude.values) / 0.25).astype("int64")
    lon_native_idx = (np.rint(mrms_da.longitude.values / 0.25).astype("int64") % 1440)
    lat_counts = pd.Series(lat_native_idx).value_counts().rename("n_native_rows")
    lon_counts = pd.Series(lon_native_idx).value_counts().rename("n_native_cols")

    counts = served_mask[["cell_id", "lat_idx", "lon_idx"]].copy()
    counts["n_native_rows"] = counts["lat_idx"].map(lat_counts).fillna(0).astype("int64")
    counts["n_native_cols"] = counts["lon_idx"].map(lon_counts).fillna(0).astype("int64")
    counts["n_native_pixels_observed"] = counts["n_native_rows"] * counts["n_native_cols"]
    return counts[["cell_id", "n_native_pixels_observed"]]


def aggregate_pixels_to_cells(
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
    pixel_df = pixel_df[pixel_df["cell_id"].isin(served_cell_ids)]
    return pixel_df


observed_counts = native_observed_counts_for_served_cells(da, served)
display(observed_counts["n_native_pixels_observed"].describe().to_frame("n_native_pixels_observed"))

# %% [markdown]
# ## 4 - Build the complete one-day panel

# %%
positive_pixels = aggregate_pixels_to_cells(da, arr, arr > 0, "mesh_mm")
severe_pixels = aggregate_pixels_to_cells(da, arr, arr >= THRESHOLD_MM, "mesh_mm")

positive_agg = (
    positive_pixels.groupby("cell_id")["mesh_mm"]
    .agg(
        n_native_pixels_positive="size",
        mesh_max_mm="max",
        mesh_mean_positive_mm="mean",
    )
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
    served.merge(observed_counts, on="cell_id", how="left")
    .merge(positive_agg, on="cell_id", how="left")
    .merge(severe_agg, on="cell_id", how="left")
)

count_columns = ["n_native_pixels_observed", "n_native_pixels_positive", "n_native_pixels_severe"]
for col in count_columns:
    panel[col] = panel[col].fillna(0).astype("int64")

panel["hazard"] = "hail"
panel["date"] = pd.Timestamp(PROOF_DATE)
panel["source_product"] = PRODUCT
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
    [
        "no_native_pixel_coverage",
        "observed_severe_hail",
        "observed_sub_severe_hail",
    ],
    default="observed_no_hail",
)

panel["qa_flags"] = np.where(
    panel["coverage_status"] == "no_native_pixel_coverage",
    "no_native_pixel_coverage",
    "raw_mrms_mesh;negative_values_masked;v1_one_day_proof",
)

ordered_columns = [
    "hazard",
    "cell_id",
    "date",
    "source_product",
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
panel = panel[ordered_columns].sort_values("cell_id").reset_index(drop=True)

if len(panel) != len(served):
    raise AssertionError(f"expected {len(served)} rows, got {len(panel)}")
if not panel["cell_id"].is_unique:
    raise AssertionError("proof panel has duplicate cell_id rows")

display(panel.head())
display(panel["coverage_status"].value_counts().rename_axis("coverage_status").reset_index(name="n_cells"))

# %% [markdown]
# **Takeaway.** This is the V1 M0 row shape we need before scale: complete target denominator first, then hail
# status and size summaries. Severe-only rows are still useful for selected-cell work, but V1 needs explicit
# zero and no-data states.

# %% [markdown]
# ## 5 - QA summaries and map

# %%
status_summary = (
    panel.groupby("coverage_status")
    .agg(
        n_cells=("cell_id", "size"),
        n_positive_pixels=("n_native_pixels_positive", "sum"),
        n_severe_pixels=("n_native_pixels_severe", "sum"),
        max_mesh_mm=("mesh_max_mm", "max"),
    )
    .reset_index()
    .sort_values("coverage_status")
)

top_cells = panel.sort_values(["n_native_pixels_severe", "mesh_max_mm"], ascending=False).head(25)

display(status_summary)
display(top_cells[["cell_id", "state_abbr", "lat_center", "lon_center", "n_native_pixels_severe", "mesh_max_mm"]])

# %%
status_colors = {
    "observed_no_hail": "#d0d0d0",
    "observed_sub_severe_hail": "#fdae61",
    "observed_severe_hail": "#d7191c",
    "no_native_pixel_coverage": "#2b2b2b",
}

fig, ax = plt.subplots(figsize=(10, 5.5))
for status, group in panel.groupby("coverage_status"):
    ax.scatter(
        group["lon_center"],
        group["lat_center"],
        s=7 if status != "observed_severe_hail" else 16,
        c=status_colors.get(status, "#888888"),
        label=f"{status} ({len(group):,})",
        alpha=0.8,
        linewidths=0,
    )
ax.set_title(f"MRMS V1 one-day proof status by served CONUS cell - {PROOF_DATE}")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend(loc="lower left", fontsize=8, frameon=True)
fig.tight_layout()

QA_DIR.mkdir(parents=True, exist_ok=True)
fig.savefig(STATUS_MAP_PNG, bbox_inches="tight")
plt.close(fig)

print("wrote status map:", STATUS_MAP_PNG.relative_to(ROOT))
display(Image(filename=str(STATUS_MAP_PNG)))

# %% [markdown]
# **Takeaway.** The map is not a climatology. It is a QA view for one source day that should quickly reveal
# impossible coverage holes, shifted longitude handling, or obviously broken cell assignment.

# %% [markdown]
# ### Saved Map Preview
#
# This is the saved CONUS-cell status map from the validated one-day proof:
#
# ![MRMS V1 one-day proof CONUS status map](../../../../../data/hazard_conus_grid/hail/qa/mrms_v1_one_day_status_map_20240601_v2026_06_16.png)
#
# The full source inventory notebook does not have a CONUS map because it only lists source-date/file
# availability. CONUS maps start once we have `cell_id x date` M0 evidence.

# %% [markdown]
# ## 6 - Write proof artifacts

# %%
PROOF_DIR.mkdir(parents=True, exist_ok=True)

panel.to_parquet(DAILY_PANEL_PARQUET, index=False)
status_summary.to_csv(SUMMARY_CSV, index=False)
top_cells.to_csv(TOP_CELLS_CSV, index=False)

metadata = {
    "artifact": DAILY_PANEL_PARQUET.name,
    "status": "mrms_v1_one_day_full_grid_proof",
    "hazard": "hail",
    "source_set": "MRMS_ONLY",
    "source_product": PRODUCT,
    "source_path": str(source_path.relative_to(ROOT)),
    "source_timestamp": source_timestamp.isoformat(),
    "proof_date": PROOF_DATE,
    "threshold_mm": THRESHOLD_MM,
    "benchmark_grid": "data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv",
    "n_served_cells": int(len(served)),
    "n_output_rows": int(len(panel)),
    "native_grid_shape": [int(da.shape[0]), int(da.shape[1])],
    "native_pixel_count": int(da.size),
    "native_positive_pixel_count": int((arr > 0).sum()),
    "native_severe_pixel_count": int((arr >= THRESHOLD_MM).sum()),
    "served_observed_pixel_count": int(panel["n_native_pixels_observed"].sum()),
    "served_positive_pixel_count": int(panel["n_native_pixels_positive"].sum()),
    "served_severe_pixel_count": int(panel["n_native_pixels_severe"].sum()),
    "severe_pixel_count_outside_served_mask": int((arr >= THRESHOLD_MM).sum())
    - int(panel["n_native_pixels_severe"].sum()),
    "coverage_status_counts": panel["coverage_status"].value_counts().to_dict(),
    "max_mesh_mm": None if pd.isna(panel["mesh_max_mm"].max()) else float(panel["mesh_max_mm"].max()),
    "outputs": {
        "daily_panel": str(DAILY_PANEL_PARQUET.relative_to(ROOT)),
        "status_summary": str(SUMMARY_CSV.relative_to(ROOT)),
        "top_cells": str(TOP_CELLS_CSV.relative_to(ROOT)),
        "status_map": str(STATUS_MAP_PNG.relative_to(ROOT)),
    },
    "allowed_use": [
        "MRMS V1 full-grid aggregation proof",
        "M0 daily evidence schema QA",
        "input contract check before MRMS full-record or GCP processing",
    ],
    "not_allowed_use": [
        "annual hail frequency estimate",
        "final M1 hazard layer",
        "reportable EAL/PML/VaR/TVaR input",
        "MYRORSS source promotion",
    ],
    "caveats": [
        "One source day only.",
        "Raw MRMS MESH is radar-estimated and not de-biased.",
        "No NOAA/SPC validation is joined here.",
        "No MYRORSS evidence is used in V1 proof.",
        "Native-pixel area is approximated by pixel count for this proof.",
    ],
}
METADATA_JSON.write_text(json.dumps(metadata, indent=2) + "\n")

print("wrote daily panel:", DAILY_PANEL_PARQUET.relative_to(ROOT))
print("wrote status summary:", SUMMARY_CSV.relative_to(ROOT))
print("wrote top cells:", TOP_CELLS_CSV.relative_to(ROOT))
print("wrote metadata:", METADATA_JSON.relative_to(ROOT))

# %% [markdown]
# ## 7 - Recap and next step
#
# This notebook proves the V1 M0 full-grid row contract for one MRMS day:
#
# - one row per served CONUS `cell_id`;
# - explicit coverage/no-hail/sub-severe/severe status;
# - source timestamp, threshold, and raw-MRMS caveats carried with the artifact;
# - small QA outputs that can be reviewed before scale.
#
# Next implementation step:
#
# ```text
# MRMS source inventory over the intended V1 record window
#   -> full-grid daily evidence batches
#   -> MRMS-only V1 M1 hazard layer
# ```
#
# Ask for GCP bucket/project details only after this local proof artifact is accepted.
