#!/usr/bin/env python3
"""
Run MRMS-only V1 full-grid M0 daily cell evidence batches.

This is a notebook-support utility, not production code. It is the script form of:

  Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
    04_mrms_v1_m0_daily_evidence_batch.ipynb

It reads an accepted MRMS source inventory, processes one explicit date window, writes one
row per served CONUS cell per accepted date, and optionally uploads the batch tree to GCS.
For Cloud Run fanout it can also choose its date window from the inventory batch-spec CSV
using CLOUD_RUN_TASK_INDEX.

Examples:
  .venv/bin/python scripts/run_mrms_v1_m0_daily_evidence_batch.py --dry-run \
    --batch-start 2024-06-01 --batch-end 2024-06-07

  .venv/bin/python scripts/run_mrms_v1_m0_daily_evidence_batch.py \
    --batch-start 2024-06-01 --batch-end 2024-06-07 \
    --run-id 20260616T172929Z --upload
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import xarray as xr


ROOT = Path(__file__).resolve().parents[1]
GRID_DIR = ROOT / "data" / "hazard_conus_grid" / "common" / "benchmark_grid"
HAIL_GRID_DIR = ROOT / "data" / "hazard_conus_grid" / "hail"
MRMS_CACHE = Path(os.environ.get("MRMS_CACHE_ROOT", str(ROOT / "data" / "hail" / "mrms_raw")))

THRESHOLD_MM = 25.4
PRODUCT = "CONUS/MESH_Max_1440min_00.50"
DEFAULT_SOURCE_INVENTORY_RUN_ID = "20260616T165806Z"
DEFAULT_SOURCE_INVENTORY_LABEL = "20140101_20260615"
DEFAULT_GCS_OUTPUT_ROOT = "gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence"
DEFAULT_BATCH_SPEC_URI = (
    "gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/"
    "run_id=20260616T165806Z/"
    "mrms_v1_m0_daily_evidence_batch_spec_20140101_20260615_20260616T165806Z.csv"
)


def env_int(*names: str) -> int | None:
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ""):
            return int(value)
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-start", default=os.environ.get("MRMS_M0_BATCH_START", "2024-06-01"))
    parser.add_argument("--batch-end", default=os.environ.get("MRMS_M0_BATCH_END", "2024-06-07"))
    parser.add_argument(
        "--source-inventory-run-id",
        default=os.environ.get("MRMS_SOURCE_INVENTORY_RUN_ID", DEFAULT_SOURCE_INVENTORY_RUN_ID),
    )
    parser.add_argument(
        "--source-inventory-uri",
        default=os.environ.get("MRMS_SOURCE_INVENTORY_URI"),
        help="Local or gs:// source inventory parquet. Defaults to the committed local run path.",
    )
    parser.add_argument(
        "--served-mask-uri",
        default=os.environ.get("MRMS_SERVED_MASK_URI"),
        help="Local or gs:// served CONUS cell CSV. Defaults to the local benchmark grid artifact.",
    )
    parser.add_argument(
        "--batch-spec-uri",
        default=os.environ.get("MRMS_M0_BATCH_SPEC_URI"),
        help=(
            "Local or gs:// M0 batch-spec CSV. Required for --task-indexed unless the default local "
            "inventory batch spec exists."
        ),
    )
    parser.add_argument(
        "--task-indexed",
        action="store_true",
        default=os.environ.get("MRMS_M0_TASK_INDEXED") == "1",
        help="Resolve batch-start/end from batch-spec row CLOUD_RUN_TASK_INDEX instead of explicit dates.",
    )
    parser.add_argument(
        "--task-index",
        type=int,
        default=env_int("MRMS_M0_TASK_INDEX", "CLOUD_RUN_TASK_INDEX"),
        help="Zero-based batch-spec row index. Defaults to MRMS_M0_TASK_INDEX or CLOUD_RUN_TASK_INDEX.",
    )
    parser.add_argument(
        "--task-count",
        type=int,
        default=env_int("MRMS_M0_TASK_COUNT", "CLOUD_RUN_TASK_COUNT"),
        help="Declared task count for metadata/validation. Defaults to MRMS_M0_TASK_COUNT or CLOUD_RUN_TASK_COUNT.",
    )
    parser.add_argument(
        "--run-id",
        default=os.environ.get("HAZARD_CONUS_GRID_RUN_ID", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")),
    )
    parser.add_argument("--local-root", type=Path, default=HAIL_GRID_DIR / "v1_mrms_only" / "m0_daily_cell_evidence")
    parser.add_argument("--gcs-output-root", default=os.environ.get("MRMS_M0_GCS_OUTPUT_ROOT", DEFAULT_GCS_OUTPUT_ROOT))
    parser.add_argument("--upload", action="store_true", default=os.environ.get("HAZARD_CONUS_GRID_UPLOAD_TO_GCS") == "1")
    parser.add_argument("--force", action="store_true", help="Allow replacing an existing local batch directory.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print planned paths only.")
    parser.add_argument(
        "--skip-maps",
        action="store_true",
        default=os.environ.get("MRMS_M0_SKIP_MAPS") == "1",
        help="Skip per-day QA PNG maps. Use this for full scale-out runs; keep maps for proof batches.",
    )
    return parser.parse_args()


def is_gcs_uri(value: str | Path) -> bool:
    return str(value).startswith("gs://")


def split_gcs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError(f"not a gs:// URI: {uri}")
    rest = uri[5:]
    bucket, _, blob = rest.partition("/")
    if not bucket or not blob:
        raise ValueError(f"invalid gs:// URI: {uri}")
    return bucket, blob


def download_gcs_uri(uri: str, local_path: Path) -> Path:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", uri, str(local_path)], check=True)
        return local_path

    bucket_name, blob_name = split_gcs_uri(uri)
    client = storage.Client()
    client.bucket(bucket_name).blob(blob_name).download_to_filename(local_path)
    return local_path


def upload_file_to_gcs(local_path: Path, destination_uri: str) -> None:
    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", str(local_path), destination_uri], check=True)
        return

    bucket_name, blob_name = split_gcs_uri(destination_uri)
    client = storage.Client()
    client.bucket(bucket_name).blob(blob_name).upload_from_filename(local_path)


def gcs_prefix_exists(uri: str) -> bool:
    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        result = subprocess.run(
            ["gcloud", "storage", "ls", f"{uri.rstrip('/')}/**"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode == 0

    bucket_name, prefix = split_gcs_uri(uri.rstrip("/") + "/_probe")
    prefix = prefix.rsplit("/", 1)[0].rstrip("/") + "/"
    client = storage.Client()
    return any(client.bucket(bucket_name).list_blobs(prefix=prefix, max_results=1))


def resolve_source_inventory(args: argparse.Namespace) -> Path:
    if args.source_inventory_uri:
        uri = args.source_inventory_uri
        if is_gcs_uri(uri):
            local = Path(tempfile.gettempdir()) / Path(uri).name
            return download_gcs_uri(uri, local)
        return Path(uri)

    local = (
        HAIL_GRID_DIR
        / "v1_mrms_only"
        / "m0_source_inventory"
        / f"run_id={args.source_inventory_run_id}"
        / f"mrms_v1_source_inventory_{DEFAULT_SOURCE_INVENTORY_LABEL}_{args.source_inventory_run_id}.parquet"
    )
    if local.exists():
        return local

    raise FileNotFoundError(
        "source inventory not found. Pass --source-inventory-uri, or create the default local artifact: "
        f"{local}"
    )


def resolve_served_mask(args: argparse.Namespace) -> Path:
    if args.served_mask_uri:
        uri = args.served_mask_uri
        if is_gcs_uri(uri):
            local = Path(tempfile.gettempdir()) / Path(uri).name
            return download_gcs_uri(uri, local)
        return Path(uri)
    return GRID_DIR / "served_conus_cell_ids_v2026_06.csv"


def resolve_batch_spec(args: argparse.Namespace) -> Path:
    if args.batch_spec_uri:
        uri = args.batch_spec_uri
        if is_gcs_uri(uri):
            local = Path(tempfile.gettempdir()) / uri.rstrip("/").rsplit("/", 1)[-1]
            return download_gcs_uri(uri, local)
        return Path(uri)

    local = (
        HAIL_GRID_DIR
        / "v1_mrms_only"
        / "m0_source_inventory"
        / f"run_id={args.source_inventory_run_id}"
        / f"mrms_v1_m0_daily_evidence_batch_spec_{DEFAULT_SOURCE_INVENTORY_LABEL}_{args.source_inventory_run_id}.csv"
    )
    if local.exists():
        return local

    return download_gcs_uri(DEFAULT_BATCH_SPEC_URI, Path(tempfile.gettempdir()) / DEFAULT_BATCH_SPEC_URI.rsplit("/", 1)[-1])


def resolve_batch_control(args: argparse.Namespace) -> dict[str, Any]:
    if not args.task_indexed:
        return {
            "execution_mode": "single_batch",
            "batch_start": args.batch_start,
            "batch_end": args.batch_end,
            "batch_id": None,
            "batch_spec_path": None,
            "batch_spec_uri": None,
            "task_index": None,
            "task_count": args.task_count,
            "cloud_run_task_attempt": os.environ.get("CLOUD_RUN_TASK_ATTEMPT"),
        }

    if args.task_index is None:
        raise ValueError("--task-indexed requires --task-index, MRMS_M0_TASK_INDEX, or CLOUD_RUN_TASK_INDEX")
    if args.task_index < 0:
        raise ValueError(f"task index must be non-negative, got {args.task_index}")

    batch_spec_path = resolve_batch_spec(args)
    batch_spec = pd.read_csv(batch_spec_path)
    required_columns = {"batch_id", "date_start", "date_end", "n_accepted_source_days"}
    missing = sorted(required_columns - set(batch_spec.columns))
    if missing:
        raise ValueError(f"batch spec missing columns: {missing}")
    if args.task_index >= len(batch_spec):
        raise IndexError(f"task index {args.task_index} outside batch spec with {len(batch_spec)} rows")

    row = batch_spec.iloc[int(args.task_index)].to_dict()
    return {
        "execution_mode": "task_indexed",
        "batch_start": str(row["date_start"]),
        "batch_end": str(row["date_end"]),
        "batch_id": str(row["batch_id"]),
        "n_accepted_source_days": int(row["n_accepted_source_days"]),
        "batch_spec_path": str(batch_spec_path),
        "batch_spec_uri": args.batch_spec_uri or DEFAULT_BATCH_SPEC_URI,
        "batch_spec_rows": int(len(batch_spec)),
        "task_index": int(args.task_index),
        "task_count": None if args.task_count is None else int(args.task_count),
        "cloud_run_task_attempt": os.environ.get("CLOUD_RUN_TASK_ATTEMPT"),
        "batch_spec_row": row,
    }


def source_timestamp_from_name(path_or_key: str) -> pd.Timestamp:
    match = re.search(r"_(\d{8})-(\d{6})\.grib2\.gz$", Path(path_or_key).name)
    if not match:
        raise ValueError(f"cannot parse MRMS timestamp from {path_or_key}")
    return pd.to_datetime(f"{match.group(1)}{match.group(2)}", format="%Y%m%d%H%M%S", utc=True)


def fetch_inventory_source(row: pd.Series) -> Path:
    key = str(row["selected_source_key"])
    uri = str(row["selected_source_uri_https"])
    local = MRMS_CACHE / Path(key).name
    MRMS_CACHE.mkdir(parents=True, exist_ok=True)
    if local.exists() and local.stat().st_size > 0:
        return local

    response = requests.get(uri, timeout=180)
    response.raise_for_status()
    local.write_bytes(response.content)
    return local


def read_mrms_grib(gz_path: Path) -> xr.DataArray:
    raw = gzip.decompress(gz_path.read_bytes())
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


@dataclass
class BatchContext:
    served: pd.DataFrame
    served_cell_ids: set[int]


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


def build_daily_panel(context: BatchContext, row: pd.Series) -> tuple[pd.DataFrame, dict[str, Any]]:
    date_str = str(row["date"])
    t0 = time.perf_counter()
    source_path = fetch_inventory_source(row)
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
        ["no_native_pixel_coverage", "observed_severe_hail", "observed_sub_severe_hail"],
        default="observed_no_hail",
    )

    panel["qa_flags"] = np.where(
        panel["coverage_status"] == "no_native_pixel_coverage",
        "no_native_pixel_coverage",
        "raw_mrms_mesh;negative_values_masked;v1_m0_batch",
    )

    ordered_columns = [
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
    panel = panel[ordered_columns].sort_values("cell_id").reset_index(drop=True)

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
        "served_severe_cell_count": int((panel["coverage_status"] == "observed_severe_hail").sum()),
        "served_sub_severe_cell_count": int((panel["coverage_status"] == "observed_sub_severe_hail").sum()),
        "served_no_hail_cell_count": int((panel["coverage_status"] == "observed_no_hail").sum()),
        "served_no_coverage_cell_count": int((panel["coverage_status"] == "no_native_pixel_coverage").sum()),
        "max_mesh_mm": None if pd.isna(panel["mesh_max_mm"].max()) else float(panel["mesh_max_mm"].max()),
        "elapsed_seconds": round(time.perf_counter() - t0, 3),
    }
    return panel, stats


STATUS_COLORS = {
    "observed_no_hail": "#d0d0d0",
    "observed_sub_severe_hail": "#fdae61",
    "observed_severe_hail": "#d7191c",
    "no_native_pixel_coverage": "#2b2b2b",
}


def write_status_map(panel: pd.DataFrame, date_str: str, run_id: str, qa_map_dir: Path) -> Path:
    qa_map_dir.mkdir(parents=True, exist_ok=True)
    png_path = qa_map_dir / f"mrms_v1_m0_status_map_{date_str.replace('-', '')}_{run_id}.png"
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for status, group in panel.groupby("coverage_status"):
        ax.scatter(
            group["lon_center"],
            group["lat_center"],
            s=7 if status != "observed_severe_hail" else 16,
            c=STATUS_COLORS.get(status, "#888888"),
            label=f"{status} ({len(group):,})",
            alpha=0.8,
            linewidths=0,
        )
    ax.set_title(f"MRMS V1 M0 status by served CONUS cell - {date_str}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    fig.tight_layout()
    fig.savefig(png_path, bbox_inches="tight")
    plt.close(fig)
    return png_path


def upload_tree(local_root: Path, gcs_root: str, exclude_paths: set[Path] | None = None) -> list[str]:
    if gcs_prefix_exists(gcs_root):
        raise FileExistsError(f"GCS destination already has objects: {gcs_root}")

    excluded = {path.resolve() for path in (exclude_paths or set())}
    uploaded: list[str] = []
    for path in sorted(p for p in local_root.rglob("*") if p.is_file()):
        if path.resolve() in excluded:
            continue
        rel = path.relative_to(local_root).as_posix()
        destination = f"{gcs_root.rstrip('/')}/{rel}"
        upload_file_to_gcs(path, destination)
        uploaded.append(destination)
    return uploaded


def load_inputs(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, Path, Path]:
    inventory_path = resolve_source_inventory(args)
    served_path = resolve_served_mask(args)

    served = pd.read_csv(served_path)
    served["cell_id"] = served["cell_id"].astype("int64")
    required_grid_columns = ["cell_id", "lat_idx", "lon_idx", "lat_center", "lon_center", "state_abbr", "iso_rto"]
    missing = sorted(set(required_grid_columns) - set(served.columns))
    if missing:
        raise ValueError(f"served mask missing columns: {missing}")
    if not served["cell_id"].is_unique:
        raise ValueError("served mask cell_id is not unique")
    served = served[required_grid_columns].copy()

    inventory = pd.read_parquet(inventory_path)
    inventory["date"] = pd.to_datetime(inventory["date"]).dt.date.astype(str)
    return served, inventory, served_path, inventory_path


def main() -> int:
    args = parse_args()
    batch_control = resolve_batch_control(args)
    args.batch_start = batch_control["batch_start"]
    args.batch_end = batch_control["batch_end"]
    batch_label = f"{pd.Timestamp(args.batch_start).strftime('%Y%m%d')}_{pd.Timestamp(args.batch_end).strftime('%Y%m%d')}"
    local_run_dir = args.local_root / f"run_id={args.run_id}" / f"batch={batch_label}"
    qa_map_dir = local_run_dir / "qa" / "maps"
    gcs_run_root = f"{args.gcs_output_root.rstrip('/')}/run_id={args.run_id}/batch={batch_label}"

    served, inventory, served_path, inventory_path = load_inputs(args)
    batch_dates = pd.date_range(args.batch_start, args.batch_end, freq="D").strftime("%Y-%m-%d").tolist()
    batch_inventory = inventory[inventory["date"].isin(batch_dates)].copy().sort_values("date")

    missing_dates = sorted(set(batch_dates) - set(batch_inventory["date"]))
    not_accepted = batch_inventory.loc[~batch_inventory["accepted_for_v1"], ["date", "list_status", "skip_or_failure_reason"]]
    if missing_dates:
        raise ValueError(f"batch dates missing from source inventory: {missing_dates}")
    if not not_accepted.empty:
        raise ValueError(f"batch contains dates not accepted for V1:\n{not_accepted.to_string(index=False)}")
    expected_source_days = batch_control.get("n_accepted_source_days")
    if expected_source_days is not None and len(batch_inventory) != int(expected_source_days):
        raise ValueError(
            "batch-spec accepted source day count does not match inventory rows: "
            f"batch_id={batch_control.get('batch_id')} "
            f"spec={expected_source_days} inventory={len(batch_inventory)}"
        )

    expected_rows = len(served) * len(batch_inventory)
    print(f"[mrms-m0] run_id={args.run_id} batch={batch_label}", flush=True)
    print(
        "[mrms-m0] "
        f"execution_mode={batch_control['execution_mode']} "
        f"batch_id={batch_control.get('batch_id')} "
        f"task_index={batch_control.get('task_index')} "
        f"task_count={batch_control.get('task_count')}",
        flush=True,
    )
    if batch_control.get("batch_spec_path"):
        print(f"[mrms-m0] batch_spec={batch_control['batch_spec_path']}", flush=True)
    print(f"[mrms-m0] source_inventory={inventory_path}", flush=True)
    print(f"[mrms-m0] served_mask={served_path}", flush=True)
    print(f"[mrms-m0] dates={len(batch_inventory)} served_cells={len(served)} expected_rows={expected_rows}", flush=True)
    print(f"[mrms-m0] local_run_dir={local_run_dir}", flush=True)
    print(f"[mrms-m0] gcs_run_root={gcs_run_root}", flush=True)

    if args.dry_run:
        return 0

    if local_run_dir.exists():
        if not args.force:
            raise FileExistsError(f"local batch directory exists; pass --force to replace: {local_run_dir}")
        shutil.rmtree(local_run_dir)
    local_run_dir.mkdir(parents=True, exist_ok=True)
    qa_map_dir.mkdir(parents=True, exist_ok=True)

    context = BatchContext(served=served, served_cell_ids=set(served["cell_id"]))
    daily_panels: list[pd.DataFrame] = []
    manifest_rows: list[dict[str, Any]] = []
    map_paths: list[Path] = []

    batch_start_time = time.perf_counter()
    for idx, (_, inv_row) in enumerate(batch_inventory.iterrows(), start=1):
        date_str = str(inv_row["date"])
        print(f"[mrms-m0] [{idx}/{len(batch_inventory)}] processing {date_str}", flush=True)
        day_panel, stats = build_daily_panel(context, inv_row)

        date_partition_dir = local_run_dir / f"date={date_str}"
        date_partition_dir.mkdir(parents=True, exist_ok=True)
        date_partition_path = date_partition_dir / "part-000.parquet"
        day_panel.to_parquet(date_partition_path, index=False)

        map_path = None if args.skip_maps else write_status_map(day_panel, date_str, args.run_id, qa_map_dir)
        stats["partition_path"] = str(date_partition_path)
        stats["status_map_path"] = None if map_path is None else str(map_path)
        manifest_rows.append(stats)
        daily_panels.append(day_panel)
        if map_path is not None:
            map_paths.append(map_path)

    batch_panel = pd.concat(daily_panels, ignore_index=True)
    if len(batch_panel) != expected_rows:
        raise AssertionError(f"expected {expected_rows} rows, got {len(batch_panel)}")
    if batch_panel.duplicated(["cell_id", "date"]).any():
        raise AssertionError("batch panel has duplicate cell_id/date rows")

    batch_manifest = pd.DataFrame(manifest_rows)
    daily_status_summary = (
        batch_panel.groupby(["date", "coverage_status"])
        .agg(
            n_cells=("cell_id", "size"),
            n_positive_pixels=("n_native_pixels_positive", "sum"),
            n_severe_pixels=("n_native_pixels_severe", "sum"),
            max_mesh_mm=("mesh_max_mm", "max"),
        )
        .reset_index()
        .sort_values(["date", "coverage_status"])
    )
    top_cells = (
        batch_panel.sort_values(["n_native_pixels_severe", "mesh_max_mm"], ascending=False)
        .groupby("date", group_keys=False)
        .head(25)
        .sort_values(["date", "n_native_pixels_severe", "mesh_max_mm"], ascending=[True, False, False])
    )

    combined_panel_parquet = local_run_dir / f"mrms_v1_m0_daily_cell_evidence_{batch_label}_{args.run_id}.parquet"
    batch_manifest_csv = local_run_dir / f"mrms_v1_m0_batch_manifest_{batch_label}_{args.run_id}.csv"
    daily_status_summary_csv = local_run_dir / f"mrms_v1_m0_daily_status_summary_{batch_label}_{args.run_id}.csv"
    top_cells_csv = local_run_dir / f"mrms_v1_m0_top_cells_{batch_label}_{args.run_id}.csv"
    metadata_json = local_run_dir / f"metadata_{batch_label}_{args.run_id}.json"

    batch_panel.to_parquet(combined_panel_parquet, index=False)
    batch_manifest.to_csv(batch_manifest_csv, index=False)
    daily_status_summary.to_csv(daily_status_summary_csv, index=False)
    top_cells.to_csv(top_cells_csv, index=False)

    artifact_sizes = {
        "combined_panel_parquet_bytes": int(combined_panel_parquet.stat().st_size),
        "batch_manifest_csv_bytes": int(batch_manifest_csv.stat().st_size),
        "daily_status_summary_csv_bytes": int(daily_status_summary_csv.stat().st_size),
        "top_cells_csv_bytes": int(top_cells_csv.stat().st_size),
        "qa_map_total_bytes": int(sum(path.stat().st_size for path in map_paths)),
    }

    metadata: dict[str, Any] = {
        "artifact_family": "mrms_v1_m0_daily_cell_evidence_batch",
        "status": "batch_run",
        "hazard": "hail",
        "source_set": "MRMS_ONLY",
        "source_product": PRODUCT,
        "threshold_mm": THRESHOLD_MM,
        "run_id": args.run_id,
        "batch_label": batch_label,
        "batch_start_date": args.batch_start,
        "batch_end_date": args.batch_end,
        "source_inventory_run_id": args.source_inventory_run_id,
        "source_inventory_parquet": str(inventory_path),
        "served_mask_csv": str(served_path),
        "execution_mode": batch_control["execution_mode"],
        "task_index": batch_control.get("task_index"),
        "task_count": batch_control.get("task_count"),
        "cloud_run_task_attempt": batch_control.get("cloud_run_task_attempt"),
        "batch_id": batch_control.get("batch_id"),
        "batch_spec_uri": batch_control.get("batch_spec_uri"),
        "batch_spec_path": batch_control.get("batch_spec_path"),
        "batch_spec_rows": batch_control.get("batch_spec_rows"),
        "batch_spec_row": batch_control.get("batch_spec_row"),
        "n_dates": int(len(batch_inventory)),
        "n_served_cells": int(len(served)),
        "expected_rows": int(expected_rows),
        "n_output_rows": int(len(batch_panel)),
        "coverage_status_counts": batch_panel["coverage_status"].value_counts().to_dict(),
        "daily_manifest": manifest_rows,
        "local_run_dir": str(local_run_dir),
        "gcs_run_root": gcs_run_root,
        "upload_requested": bool(args.upload),
        "maps_written": not bool(args.skip_maps),
        "elapsed_seconds": round(time.perf_counter() - batch_start_time, 3),
        "artifact_sizes": artifact_sizes,
        "outputs": {
            "combined_panel_parquet": str(combined_panel_parquet),
            "batch_manifest_csv": str(batch_manifest_csv),
            "daily_status_summary_csv": str(daily_status_summary_csv),
            "top_cells_csv": str(top_cells_csv),
            "metadata_json": str(metadata_json),
            "daily_partitions_root": str(local_run_dir),
            "qa_maps": [str(path) for path in map_paths],
        },
        "allowed_use": [
            "MRMS V1 full-grid M0 batch run",
            "input to M0 batch reconciliation",
        ],
        "not_allowed_use": [
            "M1 frequency or size distribution before reconciliation",
            "reportable EAL/PML/VaR/TVaR input",
        ],
        "caveats": [
            "Raw MRMS MESH is radar-estimated and not de-biased.",
            "No NOAA/SPC validation is joined here.",
            "No MYRORSS evidence is used in V1.",
            "Native-pixel area is approximated by pixel count for this M0 run.",
        ],
    }
    metadata_json.write_text(json.dumps(metadata, indent=2) + "\n")

    if args.upload:
        uploaded = upload_tree(local_run_dir, gcs_run_root, exclude_paths={metadata_json})
        metadata_uri = f"{gcs_run_root}/{metadata_json.name}"
        metadata["upload_status"] = "uploaded"
        metadata["uploaded_gcs_outputs"] = uploaded + [metadata_uri]
    else:
        metadata["upload_status"] = "skipped"
        metadata["uploaded_gcs_outputs"] = []
    metadata_json.write_text(json.dumps(metadata, indent=2) + "\n")

    if args.upload:
        upload_file_to_gcs(metadata_json, f"{gcs_run_root}/{metadata_json.name}")

    print(
        "[mrms-m0] DONE "
        f"rows={len(batch_panel)} severe_cell_days="
        f"{int((batch_panel['coverage_status'] == 'observed_severe_hail').sum())} "
        f"elapsed_seconds={metadata['elapsed_seconds']} upload_status={metadata['upload_status']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
