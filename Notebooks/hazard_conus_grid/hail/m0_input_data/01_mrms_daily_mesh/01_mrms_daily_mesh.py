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
# # Hazard CONUS Grid · Hail M0 · MRMS Daily MESH to Benchmark Cells
#
# **Peril:** hail · **Layer:** M0 input evidence · **Product:** `hazard_conus_grid`
#
# This notebook is the grid-product counterpart to
# [`Notebooks/hail/m0_input_data/02_mrms_aws.py`](../../../../../Notebooks/hail/m0_input_data/02_mrms_aws.py). It keeps
# the same exploratory-data discipline, but changes the exposure from a 50-mile region around one real asset
# to the platform's 0.25 degree benchmark grid.
#
# The job here is not to make the final hail model. It is to meet MRMS in the grid context, prove the native
# pixel -> benchmark `cell_id` aggregation, and produce a small evidence-backed candidate list for the
# selected-cell pilot. The M1 layer comes later.
#
# **Hard rule for this notebook:** do not use legacy risk outputs, old model artifacts, or unexplained GCS
# deliveries to choose cells. Pilot candidates must come from canonical grid inputs and MRMS evidence.
#
# ## Step back - what are we doing here?
#
# The end goal is **not** this notebook and not this short MRMS window. The end goal is to prove the whole
# CONUS-grid hazard process on a tiny, inspectable set of cells before scaling to every served CONUS cell.
#
# ```text
# Full future process:
#
# MRMS / MYRORSS gridded hail evidence
#   -> per-cell hail frequency + size distribution
#   -> provenance / QA flags
#   -> canonical grid asset assumption, such as 100 MW solar
#   -> damage / loss
#   -> EAL, VaR, PML, TVaR
# ```
#
# We are **not ready to do that for all cells yet**, so this notebook picks four pilot candidates:
#
# ```text
# high hail cell       - stress frequent / severe behavior
# medium hail cell     - body-case behavior
# low hail cell        - sparse / quiet-control behavior
# Hayhurst cell        - bridge back to the completed hail x solar pipeline
# ```
#
# The Apr-Jun 2024 MRMS window is deliberately small. Its purpose is only to:
#
# 1. prove that MRMS native ~1 km pixels can be assigned to benchmark `cell_id`;
# 2. produce a defensible high / medium / low / reference candidate set;
# 3. create the first daily evidence shape the selected-cell M1 pilot will consume.
#
# It does **not** estimate final annual hail frequency. It does **not** replace the completed Hayhurst
# hail x solar pipeline. It is the grid-generalization pickup step before running the full process on four
# cells.
#
# Plan links:
# - [`docs/plans/hazard_conus_grid/hail/pilot.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot.md)
# - [`docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md)
# - [`docs/extra/discussion/conus_grid/hail/02_m1_build_flow.md`](../../../../../docs/extra/discussion/conus_grid/hail/02_m1_build_flow.md)
# - [`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../../../../docs/principles/notebook_work/exploratory_data_notebooks.md)

# %% [markdown]
# ## 0 · Scope and non-goals
#
# This notebook does three things:
#
# 1. Load and interpret the pinned benchmark grid / served CONUS mask.
# 2. Decode MRMS `MESH_Max_1440min` and document its grid, units, fill values, and caveats.
# 3. Run a bounded MRMS scan to produce **pilot-cell candidates**: high, medium, low, and Hayhurst/reference.
#
# It deliberately does **not**:
#
# - build the final full-CONUS hail M1 layer;
# - use MYRORSS yet;
# - bias-correct MESH;
# - fit EVT tails;
# - treat Apr-Jun 2024 as a climatology;
# - write EAL, PML, VaR, or TVaR.
#
# The selected-cell candidates were the practical input for the V0 pilot. They are not a final hazard map and
# are not the active V1 full-grid path.

# %%
from __future__ import annotations

import gzip
import json
import math
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
from shapely import wkb
from shapely.geometry import Point

plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 110})


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
SELECTION_WINDOW = ("2024-04-01", "2024-06-30")
SAMPLE_DATE = "20240601"
WRITE_CANDIDATE_MANIFEST = True

HAYHURST = {
    "asset_name": "Hayhurst Texas Solar",
    "lat": 31.815992,
    "lon": -104.0853,
    "source": "Notebooks/hail/m0_input_data/02_mrms_aws.py",
}

print("repo root:", ROOT)
print("selection window:", SELECTION_WINDOW, "(bounded pilot-selection evidence, not final climatology)")
print("MRMS cache:", MRMS_CACHE)

# %% [markdown]
# ## 1 · Benchmark grid and served CONUS mask
#
# The grid source is already pinned by the plan:
#
# ```text
# gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet
# ```
#
# The current served CONUS mask is the 13,085-cell set in:
#
# ```text
# data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
# ```
#
# This mask is the valid universe for the grid pilot. Every selected `cell_id` must join to it.

# %%
served = pd.read_csv(GRID_DIR / "served_conus_cell_ids_v2026_06.csv")
served_cell_ids = set(served["cell_id"].astype(int))

grid_fields = pd.DataFrame(
    [
        ("cell_id", "integer join key", "cell", "YES - durable grid key"),
        ("lat_idx", "global ERA5 latitude index", "index", "YES - provenance / formula checks"),
        ("lon_idx", "global ERA5 longitude index", "index", "YES - provenance / formula checks"),
        ("lat_center", "benchmark cell center latitude", "degrees", "YES - map / candidate review"),
        ("lon_center", "benchmark cell center longitude", "degrees", "YES - map / candidate review"),
        ("state_abbr", "cell context label", "state code", "context only"),
        ("iso_rto", "cell electricity-market context label", "string", "context only"),
    ],
    columns=["field", "what it is", "units / base", "how we use it"],
)

print(f"served mask rows: {len(served):,}")
print(f"unique cell_id: {served.cell_id.is_unique}")
print(
    "lat range:",
    (served.lat_center.min(), served.lat_center.max()),
    "| lon range:",
    (served.lon_center.min(), served.lon_center.max()),
)
grid_fields

# %% [markdown]
# **Takeaway.** The grid is not being invented in this notebook. We are using the pinned benchmark key and
# mask, then aggregating MRMS native pixels upward to that key.

# %% [markdown]
# ## 2 · MRMS source, cache, and bounded window
#
# `MESH_Max_1440min` is a raw gridded radar-estimated hail-size field. It is not a frequency field, not a size
# distribution, and not bias-corrected.
#
# Source and cache:
#
# ```text
# public source: https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MESH_Max_1440min_00.50/<YYYYMMDD>/
# local cache : data/hail/mrms_raw/
# ```
#
# The window here is deliberately bounded: **Apr-Jun 2024**. It is one hail-season slice used to choose pilot
# candidates and prove the grid aggregation. It excludes the rest of the MRMS record, so it must not be read
# as a climatology or a final rate estimate.

# %%
mrms_fields = pd.DataFrame(
    [
        ("MESH", "Maximum Estimated Size of Hail", "mm", "YES - gridded hail size estimate"),
        ("Max_1440min", "trailing 24-hour maximum", "minutes", "YES - one daily max tile per date"),
        ("valid_time", "tile valid timestamp", "UTC", "YES - daily evidence timestamp"),
        ("latitude", "native grid coordinate", "degrees, ~0.01", "YES - native pixel to benchmark cell"),
        ("longitude", "native grid coordinate", "0-360 degrees, ~0.01", "YES - convert to benchmark lon"),
        ("values < 0", "no-hail / fill sentinels", "unitless sentinel", "MASK before every statistic"),
        (">= 25.4", "NWS severe-hail threshold", "mm", "YES - first-pass severe hail-day flag"),
    ],
    columns=["field", "what it is", "units / base", "how we use it"],
)
mrms_fields

# %% [markdown]
# **Gotchas to keep visible.**
#
# - MESH is a radar estimate and is known to over-predict. It needs later bias correction / validation.
# - Longitude is 0-360 in the native MRMS tile, while the benchmark mask stores longitudes as -180 to 180.
# - Negative values are not hail sizes. They are fill/no-hail sentinels and are excluded from stats.
# - `MESH_Max_1440min` has many files per day; this notebook uses the last cached tile for each date as the
#   daily max evidence, matching the current single-site MRMS precedent.

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
        self.manifest_path.write_text(json.dumps(self.manifest))
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
print("cached dates in manifest:", len(mrms.manifest))
print("sample tile:", mrms.get_day(SAMPLE_DATE))

# %% [markdown]
# ## 3 · Decode one tile and inspect the actual grid
#
# This is the "what one record literally looks like" step from the notebook-work principle. A tile is a full
# national image of hail-size estimates.

# %%
sample_path = mrms.get_day(SAMPLE_DATE)
sample_da = read_mrms_grib(sample_path)
sample_arr = sample_da.values.astype("float32")

tile_summary = pd.DataFrame(
    [
        ("shape", f"{sample_da.shape[0]} x {sample_da.shape[1]}", "native MRMS rows x columns"),
        ("native cells", f"{sample_da.size:,}", "one value per ~1 km pixel"),
        ("lat range", f"{float(sample_da.latitude.min()):.3f} to {float(sample_da.latitude.max()):.3f}", "degrees"),
        ("lon range", f"{float(sample_da.longitude.min()):.3f} to {float(sample_da.longitude.max()):.3f}", "0-360 degrees"),
        ("min raw value", float(np.nanmin(sample_arr)), "negative sentinel, not hail size"),
        ("max raw value", float(np.nanmax(sample_arr)), "mm"),
        ("positive pixels", int((sample_arr > 0).sum()), "hail signal, not necessarily severe"),
        ("severe pixels", int((sample_arr >= THRESHOLD_MM).sum()), f">= {THRESHOLD_MM} mm"),
    ],
    columns=["item", "value", "meaning"],
)
tile_summary

# %% [markdown]
# **Takeaway.** A single tile has 24.5M native values. Most are negative no-hail/fill sentinels. Severe hail
# pixels are the small subset with `MESH >= 25.4 mm`.

# %%
full = np.where(sample_arr < 0, np.nan, sample_arr)
peak_r, peak_c = np.unravel_index(np.nanargmax(full), full.shape)
r0, c0 = max(peak_r - 5, 0), max(peak_c - 5, 0)
block = sample_arr[r0 : r0 + 10, c0 : c0 + 10]
with np.printoptions(precision=1, suppress=True, linewidth=140):
    print(
        f"10 x 10 raw MESH block around peak cell "
        f"(lat {float(sample_da.latitude.values[peak_r]):.2f}, "
        f"lon {float(sample_da.longitude.values[peak_c]) - 360:.2f}):"
    )
    print(np.where(block < 0, -1.0, block))

# %% [markdown]
# ## 4 · Native pixel to benchmark `cell_id`
#
# MRMS native pixels are finer than the serving grid. For the pilot we assign each native pixel center to the
# nearest 0.25 degree benchmark center:
#
# ```text
# lat_idx = round((90 - native_lat) / 0.25)
# lon_idx = round(native_lon_0_360 / 0.25)
# cell_id = lat_idx * 1440 + lon_idx
# ```
#
# That is equivalent to using benchmark cells with center +/- 0.125 degree bounds, except for exact boundary
# cases. The selected pilot output still proves each resulting `cell_id` joins to the served mask.

# %%
def native_points_to_cell_id(lat: np.ndarray, lon360: np.ndarray) -> np.ndarray:
    lat_idx = np.rint((90.0 - lat) / 0.25).astype("int64")
    lon_idx = (np.rint(lon360 / 0.25).astype("int64") % 1440)
    return lat_idx * 1440 + lon_idx


def native_observed_counts_for_served_cells(da: xr.DataArray, served_mask: pd.DataFrame) -> pd.DataFrame:
    lat_native_idx = np.rint((90.0 - da.latitude.values) / 0.25).astype("int64")
    lon_native_idx = (np.rint(da.longitude.values / 0.25).astype("int64") % 1440)
    lat_counts = pd.Series(lat_native_idx).value_counts().rename("n_native_rows")
    lon_counts = pd.Series(lon_native_idx).value_counts().rename("n_native_cols")

    counts = served_mask[["cell_id", "lat_idx", "lon_idx"]].copy()
    counts["n_native_rows"] = counts["lat_idx"].map(lat_counts).fillna(0).astype("int64")
    counts["n_native_cols"] = counts["lon_idx"].map(lon_counts).fillna(0).astype("int64")
    counts["n_native_pixels_observed"] = counts["n_native_rows"] * counts["n_native_cols"]
    return counts[["cell_id", "n_native_pixels_observed"]]


native_observed_counts = native_observed_counts_for_served_cells(sample_da, served)
native_observed_count_by_cell = native_observed_counts.set_index("cell_id")["n_native_pixels_observed"].to_dict()
native_observed_counts["n_native_pixels_observed"].describe()

# %% [markdown]
# **Takeaway.** Each benchmark cell has a stable count of native MRMS pixel centers that fall into it. This
# gives the severe-pixel count a denominator and keeps us from treating a raw count as if it had no base.

# %%
DAILY_EVIDENCE_COLUMNS = [
    "hazard",
    "cell_id",
    "date",
    "source_product",
    "source_timestamp",
    "threshold_mm",
    "n_native_pixels_observed",
    "n_native_pixels_severe",
    "severe_area_km2_approx",
    "mesh_max_mm",
    "mesh_mean_severe_mm",
    "mesh_p50_mm",
    "mesh_p90_mm",
    "mesh_p95_mm",
    "hail_day_flag",
    "qa_flags",
]


def empty_daily_evidence() -> pd.DataFrame:
    return pd.DataFrame(columns=DAILY_EVIDENCE_COLUMNS)


def aggregate_mrms_tile_to_cells(
    da: xr.DataArray,
    date: pd.Timestamp,
    threshold_mm: float,
    source_timestamp: pd.Timestamp | None = None,
) -> pd.DataFrame:
    arr = da.values.astype("float32")
    y, x = np.where(arr >= threshold_mm)
    if len(y) == 0:
        return empty_daily_evidence()

    cell_ids = native_points_to_cell_id(da.latitude.values[y], da.longitude.values[x])
    severe = pd.DataFrame({"cell_id": cell_ids, "mesh_mm": arr[y, x]})
    severe = severe[severe["cell_id"].isin(served_cell_ids)]
    if severe.empty:
        return empty_daily_evidence()

    out = (
        severe.groupby("cell_id")["mesh_mm"]
        .agg(
            n_native_pixels_severe="size",
            mesh_max_mm="max",
            mesh_mean_severe_mm="mean",
            mesh_p50_mm=lambda s: s.quantile(0.50),
            mesh_p90_mm=lambda s: s.quantile(0.90),
            mesh_p95_mm=lambda s: s.quantile(0.95),
        )
        .reset_index()
    )
    out.insert(0, "date", pd.Timestamp(date))
    out.insert(0, "hazard", "hail")
    out["source_product"] = PRODUCT
    out["source_timestamp"] = source_timestamp if source_timestamp is not None else pd.Timestamp(date)
    out["threshold_mm"] = float(threshold_mm)
    out["n_native_pixels_observed"] = out["cell_id"].map(native_observed_count_by_cell).astype("Int64")
    out["severe_area_km2_approx"] = out["n_native_pixels_severe"].astype(float)
    out["hail_day_flag"] = True
    out["qa_flags"] = "raw_mrms_mesh;negative_values_masked;native_pixel_area_approx"
    return out[DAILY_EVIDENCE_COLUMNS]


sample_cell_evidence = aggregate_mrms_tile_to_cells(
    sample_da,
    pd.Timestamp(SAMPLE_DATE),
    THRESHOLD_MM,
    mrms_source_timestamp(sample_path),
)
sample_top = (
    sample_cell_evidence.merge(served, on="cell_id", how="left")
    .sort_values(["n_native_pixels_severe", "mesh_max_mm"], ascending=False)
    .head(10)
)
sample_top

# %% [markdown]
# **Takeaway.** One daily MRMS tile now becomes a compact daily cell-evidence table: one row per benchmark cell
# with severe native pixels that day. This is the M0 evidence shape the selected-cell pilot needs.

# %% [markdown]
# ## 5 · Bounded selection scan
#
# The scan below uses all cached daily tiles in the stated Apr-Jun 2024 window. It is a selection exercise,
# not the final frequency model:
#
# - `n_hail_days` means days in this window with at least one severe native pixel assigned to the cell.
# - `total_native_pixels_severe` is a rough area/coverage proxy, not equal-area exactness.
# - `mesh_max_mm` is raw radar-estimated MESH and can be biased high.
#
# The full M1 later needs MYRORSS, de-biasing, Storm Events anchoring, sparse-cell pooling, and EVT tail work.

# %%
def scan_mrms_window(start: str, end: str) -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    rows: list[pd.DataFrame] = []
    skipped: list[tuple[str, str]] = []
    dates = [d.strftime("%Y%m%d") for d in pd.date_range(start, end, freq="D")]

    for i, ymd in enumerate(dates, start=1):
        try:
            path = mrms.get_day(ymd)
            if path is None:
                skipped.append((ymd, "no tile"))
                continue
            da = read_mrms_grib(path)
            daily = aggregate_mrms_tile_to_cells(
                da,
                pd.Timestamp(ymd),
                THRESHOLD_MM,
                mrms_source_timestamp(path),
            )
            if not daily.empty:
                rows.append(daily)
        except Exception as exc:
            skipped.append((ymd, str(exc)[:100]))

        if i % 10 == 0:
            print(f"processed {i}/{len(dates)} days")

    if not rows:
        return pd.DataFrame(), skipped
    return pd.concat(rows, ignore_index=True), skipped


daily_evidence, skipped_days = scan_mrms_window(*SELECTION_WINDOW)
print("daily evidence rows:", len(daily_evidence))
print("skipped days:", skipped_days[:5], "count:", len(skipped_days))

# %%
cell_summary = (
    daily_evidence.groupby("cell_id")
    .agg(
        n_hail_days=("date", "nunique"),
        total_native_pixels_severe=("n_native_pixels_severe", "sum"),
        mesh_max_mm=("mesh_max_mm", "max"),
        mean_daily_severe_pixels=("n_native_pixels_severe", "mean"),
    )
    .reset_index()
    .merge(served, on="cell_id", how="left")
)

print(f"served cells with severe MRMS evidence in window: {len(cell_summary):,}")
print("hail-day quantiles among nonzero cells:")
print(cell_summary["n_hail_days"].quantile([0.10, 0.25, 0.50, 0.75, 0.90, 0.95]).to_string())
cell_summary.sort_values(["n_hail_days", "total_native_pixels_severe", "mesh_max_mm"], ascending=False).head(15)

# %% [markdown]
# **Takeaway.** This table is enough to choose pilot candidates, but it is not enough to declare final
# per-cell rates. The pilot only needs a small explainable spread of cells.

# %% [markdown]
# ## 6 · Candidate selection policy
#
# We select candidates from the bounded MRMS evidence with guardrails:
#
# - **High hail:** must be in a broad Plains/TX-OK-KS-style hail corridor and score high on both hail-days and
#   severe-pixel area. This avoids choosing a tiny noisy cell only because it appeared on many days.
# - **Medium hail:** nonzero evidence near the body of the distribution, preferably in a transition/upper
#   Midwest region.
# - **Low hail:** no severe MRMS pixels in the window, in a broad low-hail western/Pacific region, with MRMS
#   coverage present.
# - **Hayhurst/reference:** assigned directly from the documented Hayhurst coordinates.
#
# This is intentionally a policy, not magic. If the candidates look wrong, change the policy in the notebook
# and rerun.

# %%
def hayhurst_cell(served_mask: pd.DataFrame) -> tuple[int, str]:
    full_grid_path = GRID_DIR / "_scratch" / "era5_us_grid_v2026_1.parquet"
    point = Point(HAYHURST["lon"], HAYHURST["lat"])

    if full_grid_path.exists():
        full_grid = pd.read_parquet(full_grid_path)
        for row in full_grid.itertuples(index=False):
            geom = wkb.loads(row.geometry)
            if geom.contains(point) or geom.touches(point):
                return int(row.cell_id), "benchmark grid polygon containment"

    lon360 = HAYHURST["lon"] + 360 if HAYHURST["lon"] < 0 else HAYHURST["lon"]
    lat_idx = int(round((90.0 - HAYHURST["lat"]) / 0.25))
    lon_idx = int(round(lon360 / 0.25)) % 1440
    cell_id = lat_idx * 1440 + lon_idx
    if cell_id not in set(served_mask["cell_id"]):
        nearest = served_mask.assign(
            _d2=(served_mask["lat_center"] - HAYHURST["lat"]) ** 2
            + (served_mask["lon_center"] - HAYHURST["lon"]) ** 2
        ).sort_values("_d2")
        cell_id = int(nearest.iloc[0]["cell_id"])
    return int(cell_id), "nearest benchmark center fallback"


def row_for_cell(cell_id: int, role: str, rationale: str, selection_basis: str) -> dict:
    base = served.loc[served["cell_id"] == cell_id].iloc[0].to_dict()
    stat = cell_summary.loc[cell_summary["cell_id"] == cell_id]
    if stat.empty:
        metrics = {
            "n_hail_days": 0,
            "total_native_pixels_severe": 0,
            "mesh_max_mm": np.nan,
            "mean_daily_severe_pixels": 0.0,
        }
    else:
        metrics = stat.iloc[0][
            ["n_hail_days", "total_native_pixels_severe", "mesh_max_mm", "mean_daily_severe_pixels"]
        ].to_dict()

    return {
        "role": role,
        "cell_id": int(cell_id),
        "lat_center": float(base["lat_center"]),
        "lon_center": float(base["lon_center"]),
        "state_abbr": base["state_abbr"],
        "iso_rto": base["iso_rto"],
        "selection_basis": selection_basis,
        "selection_window": f"{SELECTION_WINDOW[0]} to {SELECTION_WINDOW[1]}",
        "selection_metric": "MRMS hail-days + severe native pixels in bounded window",
        "selection_metric_value": (
            f"n_hail_days={int(metrics['n_hail_days'])}; "
            f"total_native_pixels_severe={int(metrics['total_native_pixels_severe'])}; "
            f"mesh_max_mm={metrics['mesh_max_mm']}"
        ),
        "n_hail_days": int(metrics["n_hail_days"]),
        "total_native_pixels_severe": int(metrics["total_native_pixels_severe"]),
        "mesh_max_mm": metrics["mesh_max_mm"],
        "served_mask_join_status": "joined",
        "rationale": rationale,
        "qa_notes": "Candidate only; Storm Events/climatology QA still required before final pilot lock.",
    }


def choose_candidate_cells() -> pd.DataFrame:
    high_states = {"TX", "OK", "KS", "NE", "SD", "CO", "NM"}
    high_pool = cell_summary[cell_summary["state_abbr"].isin(high_states)].copy()
    high_pool = high_pool[
        (high_pool["n_hail_days"] >= cell_summary["n_hail_days"].quantile(0.75))
        & (high_pool["total_native_pixels_severe"] >= cell_summary["total_native_pixels_severe"].quantile(0.75))
    ]
    high = high_pool.sort_values(
        ["n_hail_days", "total_native_pixels_severe", "mesh_max_mm"], ascending=False
    ).iloc[0]

    medium_states = {"WI", "MN", "IA", "MO", "CO", "PA", "NY"}
    nonzero = cell_summary[cell_summary["n_hail_days"] > 0].copy()
    median_days = float(nonzero["n_hail_days"].median())
    median_pixels = float(nonzero["total_native_pixels_severe"].median())
    medium_pool = nonzero[nonzero["state_abbr"].isin(medium_states)].copy()
    medium_pool["_score"] = (
        (medium_pool["n_hail_days"] - median_days).abs()
        + 0.01 * (medium_pool["total_native_pixels_severe"] - median_pixels).abs()
    )
    medium = medium_pool.sort_values(["_score", "cell_id"]).iloc[0]

    severe_cells = set(cell_summary["cell_id"].astype(int))
    low_pool = served[
        (~served["cell_id"].isin(severe_cells))
        & (served["state_abbr"].isin(["WA", "OR", "CA"]))
        & (served["lat_center"].between(34, 49))
    ].copy()
    low_target = {"lat": 47.25, "lon": -120.75}
    low_pool["_d2"] = (low_pool["lat_center"] - low_target["lat"]) ** 2 + (
        low_pool["lon_center"] - low_target["lon"]
    ) ** 2
    low = low_pool.sort_values("_d2").iloc[0]

    h_cell, h_method = hayhurst_cell(served)

    candidates = pd.DataFrame(
        [
            row_for_cell(
                int(high["cell_id"]),
                "high_hail",
                "High Plains/TX-OK-KS corridor candidate with strong MRMS hail-day and severe-pixel evidence.",
                "MRMS bounded-window scan plus broad high-hail-corridor anchor",
            ),
            row_for_cell(
                int(medium["cell_id"]),
                "medium_hail",
                "Nonzero body-case candidate near the bounded-window median evidence level.",
                "MRMS bounded-window scan plus transition-region anchor",
            ),
            row_for_cell(
                int(low["cell_id"]),
                "low_hail",
                "Western low-hail control with no severe MRMS pixels in the bounded window; MRMS coverage is present.",
                "MRMS bounded-window zero-severe evidence plus broad low-hail-region anchor",
            ),
            row_for_cell(
                h_cell,
                "hayhurst_reference",
                "Benchmark-grid cell containing the completed hail x solar reference asset.",
                h_method,
            ),
        ]
    )
    return candidates


candidate_cells = choose_candidate_cells()
candidate_cells

# %% [markdown]
# **Takeaway.** These are candidate cells from canonical evidence, not old outputs. The low cell is explicitly
# a no-severe-in-window control, not a no-data cell.

# %% [markdown]
# ## 7 · Candidate manifest and carried-forward artifact
#
# The candidate manifest is small and reviewable. It is **not** the final M1 layer and it does not contain
# loss metrics. It is an input list for the selected-cell daily evidence pilot.
#
# The daily cell evidence parquet is intentionally ignored by git because it is a build artifact. It is also
# a **sparse positive-evidence table**: rows exist only where a served benchmark cell had at least one severe
# native MRMS pixel that day. The selected-cell M1 pilot must materialize the full candidate-cell x date panel
# and write `hail_day_flag = False` rows explicitly for zero-severe days.
#
# The small CSV/JSON candidate manifest can be committed for review.

# %%
HAIL_GRID_DIR.mkdir(parents=True, exist_ok=True)
evidence_dir = HAIL_GRID_DIR / "m0_daily_cell_evidence"
evidence_dir.mkdir(parents=True, exist_ok=True)

window_tag = f"{SELECTION_WINDOW[0][:7].replace('-', '')}_{SELECTION_WINDOW[1][:7].replace('-', '')}"
daily_evidence_path = evidence_dir / f"mrms_cell_day_evidence_{window_tag}.parquet"
candidate_csv = HAIL_GRID_DIR / f"pilot_cell_candidates_mrms_{window_tag}.csv"
candidate_json = HAIL_GRID_DIR / f"pilot_cell_candidates_mrms_{window_tag}.json"

if WRITE_CANDIDATE_MANIFEST:
    daily_evidence.to_parquet(daily_evidence_path, index=False)
    candidate_cells.to_csv(candidate_csv, index=False)
    candidate_json.write_text(
        json.dumps(
            {
                "artifact": candidate_csv.name,
                "status": "candidate_pilot_cells_pending_report_side_qa",
                "selection_window": {"start": SELECTION_WINDOW[0], "end": SELECTION_WINDOW[1]},
                "source_product": PRODUCT,
                "threshold_mm": THRESHOLD_MM,
                "daily_evidence_artifact": str(daily_evidence_path.relative_to(ROOT)),
                "served_mask": "data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv",
                "candidate_roles": candidate_cells[["role", "cell_id", "state_abbr", "lat_center", "lon_center"]]
                .to_dict(orient="records"),
                "caveats": [
                    "Apr-Jun 2024 is a bounded pilot-selection window, not final climatology.",
                    "Raw MRMS MESH is radar-estimated and can over-predict hail.",
                    "Storm Events and broader climatology QA are required before final pilot-cell lock.",
                    "No legacy risk-output artifacts were used for selection.",
                ],
            },
            indent=2,
        )
    )
    print("wrote ignored daily evidence:", daily_evidence_path)
    print("wrote candidate manifest:", candidate_csv)
    print("wrote candidate metadata:", candidate_json)
else:
    print("WRITE_CANDIDATE_MANIFEST is False; no files written")

# %% [markdown]
# ## 8 · Recap and next checks
#
# What this notebook established:
#
# - MRMS daily MESH can be decoded as a full national 0.01 degree grid.
# - Negative/native fill values are masked before statistics.
# - Severe native pixels can be assigned to benchmark `cell_id`.
# - A bounded Apr-Jun 2024 MRMS window produces a defensible candidate spread for selected-cell testing.
# - The candidate file is marked as pending report-side QA; it is not a final model product.
#
# What comes next:
#
# 1. Review the candidate cells on a map and against broad hail climatology.
# 2. Add Storm Events / SPC report-side checks for the candidate cells or surrounding areas.
# 3. Lock the selected-cell manifest only after that QA.
# 4. Build the selected-cell M1 pilot from the daily evidence: `lambda_cell`, frequency family, size summary,
#    sparse flags, provenance, and QA flags.
