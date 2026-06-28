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
# # Hail V1 - MRMS Source Inventory
#
# **Peril:** hail - **Layer:** M0 source inventory - **Product:** `hazard_conus_grid` V1
#
# This notebook starts the MRMS-only V1 scale-out path after the full-grid one-day proof:
#
# ```text
# MRMS public source listing
#   -> one source-inventory row per date
#   -> accepted daily source denominator
#   -> initial batch contract for full-grid M0 evidence
#   -> local mirror, optional GCS dev upload
# ```
#
# It deliberately does **not** read every GRIB tile, aggregate pixels to cells, compute frequency, use
# MYRORSS, or produce reportable risk metrics.
#
# Plan references:
#
# - `docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`
# - `docs/plans/hazard_conus_grid/common/storage_artifacts.md`
# - `docs/plans/hazard_conus_grid/decisions.md` / DD-G6

# %% [markdown]
# ## 0 - Scope and controls
#
# Default execution is intentionally small: `2024-06-01` through `2024-06-07`.
# Override with environment variables when scaling:
#
# ```bash
# MRMS_INVENTORY_START=YYYY-MM-DD
# MRMS_INVENTORY_END=YYYY-MM-DD
# HAZARD_CONUS_GRID_UPLOAD_TO_GCS=1
# HAZARD_CONUS_GRID_RUN_ID=YYYYMMDDTHHMMSSZ
# ```
#
# The GCS upload flag only uploads the small inventory artifacts from this notebook. It does not mirror raw
# MRMS files.
#
# Saved validated run to keep visible in the notebook:
#
# ```text
# run_id: 20260616T165806Z
# requested window: 2014-01-01 to 2026-06-15
# accepted V1 denominator: 2,071 continuous source days, 2020-10-14 to 2026-06-15
# no-source dates: 2,478
# list failures: 0
# source files listed: 99,313
# planned M0 batches: 148
# GCS: gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
# ```

# %%
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from IPython.display import display


def _repo_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise FileNotFoundError("repo root not found")


ROOT = _repo_root()

PRODUCT = "CONUS/MESH_Max_1440min_00.50"
THRESHOLD_MM = 25.4
SOURCE_BUCKET_HTTP = "https://noaa-mrms-pds.s3.amazonaws.com"
SOURCE_BUCKET_S3 = "s3://noaa-mrms-pds"

DEFAULT_START_DATE = "2024-06-01"
DEFAULT_END_DATE = "2024-06-07"

START_DATE = os.environ.get("MRMS_INVENTORY_START", DEFAULT_START_DATE)
END_DATE = os.environ.get("MRMS_INVENTORY_END", DEFAULT_END_DATE)
RUN_ID = os.environ.get(
    "HAZARD_CONUS_GRID_RUN_ID",
    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
)
RUN_PURPOSE = os.environ.get("MRMS_INVENTORY_RUN_PURPOSE")
if not RUN_PURPOSE:
    is_default_window = START_DATE == DEFAULT_START_DATE and END_DATE == DEFAULT_END_DATE
    RUN_PURPOSE = "source_inventory_proof" if is_default_window else "v1_source_denominator_inventory"
UPLOAD_TO_GCS = os.environ.get("HAZARD_CONUS_GRID_UPLOAD_TO_GCS", "0").lower() in {
    "1",
    "true",
    "yes",
}
PROGRESS_EVERY_DAYS = int(os.environ.get("MRMS_INVENTORY_PROGRESS_EVERY_DAYS", "100"))
LIST_RETRIES = int(os.environ.get("MRMS_INVENTORY_LIST_RETRIES", "3"))
LIST_RETRY_SLEEP_S = float(os.environ.get("MRMS_INVENTORY_LIST_RETRY_SLEEP_S", "1.0"))

LOCAL_RUN_DIR = (
    ROOT
    / "data"
    / "hazard_conus_grid"
    / "hail"
    / "v1_mrms_only"
    / "m0_source_inventory"
    / f"run_id={RUN_ID}"
)
GCS_RUN_ROOT = (
    "gs://infrasure-benchmark/"
    f"hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id={RUN_ID}"
)

DATE_LABEL = f"{pd.Timestamp(START_DATE).strftime('%Y%m%d')}_{pd.Timestamp(END_DATE).strftime('%Y%m%d')}"
INVENTORY_PARQUET = LOCAL_RUN_DIR / f"mrms_v1_source_inventory_{DATE_LABEL}_{RUN_ID}.parquet"
INVENTORY_CSV = LOCAL_RUN_DIR / f"mrms_v1_source_inventory_{DATE_LABEL}_{RUN_ID}.csv"
SOURCE_FILES_PARQUET = LOCAL_RUN_DIR / f"mrms_v1_source_files_manifest_{DATE_LABEL}_{RUN_ID}.parquet"
SOURCE_FILES_CSV = LOCAL_RUN_DIR / f"mrms_v1_source_files_manifest_{DATE_LABEL}_{RUN_ID}.csv"
BATCH_SPEC_CSV = LOCAL_RUN_DIR / f"mrms_v1_m0_daily_evidence_batch_spec_{DATE_LABEL}_{RUN_ID}.csv"
SUMMARY_CSV = LOCAL_RUN_DIR / f"mrms_v1_source_inventory_summary_{DATE_LABEL}_{RUN_ID}.csv"
METADATA_JSON = LOCAL_RUN_DIR / f"metadata_{DATE_LABEL}_{RUN_ID}.json"

print("repo root:", ROOT)
print("inventory window:", START_DATE, "to", END_DATE)
print("run_id:", RUN_ID)
print("run_purpose:", RUN_PURPOSE)
print("local run dir:", LOCAL_RUN_DIR.relative_to(ROOT))
print("gcs run root:", GCS_RUN_ROOT)
print("upload_to_gcs:", UPLOAD_TO_GCS)
print("progress_every_days:", PROGRESS_EVERY_DAYS)
print("list_retries:", LIST_RETRIES)

# %% [markdown]
# ## 1 - Source listing client
#
# MRMS public files are listed through the NOAA public S3-compatible XML API. The inventory stores both the
# full file manifest and a date-level accepted-source row. For daily V1, the accepted source tile is the latest
# listed tile for that date, matching the one-day proof reader.

# %%
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
REQUEST_SESSION = requests.Session()


@dataclass
class MRMSListResult:
    date: pd.Timestamp
    prefix: str
    files: list[dict[str, Any]]
    list_status: str
    http_status: int | None = None
    error: str | None = None


def _text_or_none(parent: ET.Element, tag: str) -> str | None:
    elem = parent.find(S3_NS + tag)
    return None if elem is None else elem.text


def parse_source_timestamp(key: str) -> pd.Timestamp | None:
    match = re.search(r"_(\d{8})-(\d{6})\.grib2\.gz$", key)
    if not match:
        return None
    return pd.to_datetime(f"{match.group(1)}{match.group(2)}", format="%Y%m%d%H%M%S", utc=True)


def list_mrms_day(date: pd.Timestamp, timeout_s: int = 45) -> MRMSListResult:
    ymd = date.strftime("%Y%m%d")
    prefix = f"{PRODUCT}/{ymd}/"
    last_error: str | None = None
    last_http_status: int | None = None

    for attempt in range(1, LIST_RETRIES + 1):
        files: list[dict[str, Any]] = []
        continuation_token: str | None = None

        try:
            while True:
                params: dict[str, str | int] = {
                    "list-type": "2",
                    "prefix": prefix,
                    "max-keys": 1000,
                }
                if continuation_token:
                    params["continuation-token"] = continuation_token

                response = REQUEST_SESSION.get(
                    SOURCE_BUCKET_HTTP + "/",
                    params=params,
                    timeout=timeout_s,
                )
                last_http_status = response.status_code
                response.raise_for_status()
                root = ET.fromstring(response.text)

                for item in root.findall(S3_NS + "Contents"):
                    key = _text_or_none(item, "Key")
                    if not key:
                        continue
                    timestamp = parse_source_timestamp(key)
                    files.append(
                        {
                            "date": date.date().isoformat(),
                            "source_product": PRODUCT,
                            "source_key": key,
                            "source_uri_s3": f"{SOURCE_BUCKET_S3}/{key}",
                            "source_uri_https": f"{SOURCE_BUCKET_HTTP}/{key}",
                            "source_timestamp_utc": None if timestamp is None else timestamp.isoformat(),
                            "last_modified": _text_or_none(item, "LastModified"),
                            "size_bytes": int(_text_or_none(item, "Size") or 0),
                            "etag": (_text_or_none(item, "ETag") or "").strip('"'),
                        }
                    )

                is_truncated = (_text_or_none(root, "IsTruncated") or "").lower() == "true"
                continuation_token = _text_or_none(root, "NextContinuationToken")
                if not is_truncated or not continuation_token:
                    break

            status = "ok" if files else "no_source_files"
            return MRMSListResult(
                date=date,
                prefix=prefix,
                files=files,
                list_status=status,
                http_status=last_http_status,
            )
        except Exception as exc:
            last_error = repr(exc)
            if attempt < LIST_RETRIES:
                time.sleep(LIST_RETRY_SLEEP_S)

    return MRMSListResult(
        date=date,
        prefix=prefix,
        files=[],
        list_status="list_failed",
        http_status=last_http_status,
        error=last_error,
    )


dates = pd.date_range(START_DATE, END_DATE, freq="D")
print("n_dates_requested:", len(dates))

# %% [markdown]
# ## 2 - Build date-level inventory and source-file manifest

# %%
results: list[MRMSListResult] = []
for i, date in enumerate(dates, start=1):
    result = list_mrms_day(date)
    results.append(result)

    if i == 1 or i % PROGRESS_EVERY_DAYS == 0 or i == len(dates):
        status_counts = pd.Series([r.list_status for r in results]).value_counts().to_dict()
        accepted_so_far = sum(1 for r in results if r.list_status == "ok" and r.files)
        print(
            f"[{i:,}/{len(dates):,}] listed through {date.date()} "
            f"accepted={accepted_so_far:,} status_counts={status_counts}",
            flush=True,
        )

source_files = pd.DataFrame([row for result in results for row in result.files])
if source_files.empty:
    source_files = pd.DataFrame(
        columns=[
            "date",
            "source_product",
            "source_key",
            "source_uri_s3",
            "source_uri_https",
            "source_timestamp_utc",
            "last_modified",
            "size_bytes",
            "etag",
        ]
    )

inventory_rows: list[dict[str, Any]] = []
for result in results:
    date_iso = result.date.date().isoformat()
    files = pd.DataFrame(result.files)
    row: dict[str, Any] = {
        "hazard": "hail",
        "source_set": "MRMS_ONLY",
        "date": date_iso,
        "source_product": PRODUCT,
        "source_prefix": result.prefix,
        "list_status": result.list_status,
        "http_status": result.http_status,
        "n_files_listed": int(len(files)),
        "total_listed_bytes": int(files["size_bytes"].sum()) if not files.empty else 0,
        "accepted_for_v1": False,
        "selected_source_key": None,
        "selected_source_uri_s3": None,
        "selected_source_uri_https": None,
        "selected_source_timestamp_utc": None,
        "selected_size_bytes": None,
        "selected_etag": None,
        "skip_or_failure_reason": result.error,
        "qa_flags": RUN_PURPOSE,
    }

    if result.list_status == "ok" and not files.empty:
        files = files.copy()
        files["source_timestamp_sort"] = pd.to_datetime(
            files["source_timestamp_utc"], errors="coerce", utc=True
        )
        selected = files.sort_values(["source_timestamp_sort", "source_key"]).iloc[-1]
        row.update(
            {
                "accepted_for_v1": True,
                "selected_source_key": selected["source_key"],
                "selected_source_uri_s3": selected["source_uri_s3"],
                "selected_source_uri_https": selected["source_uri_https"],
                "selected_source_timestamp_utc": selected["source_timestamp_utc"],
                "selected_size_bytes": int(selected["size_bytes"]),
                "selected_etag": selected["etag"],
                "skip_or_failure_reason": None,
                "qa_flags": f"accepted_latest_tile;{RUN_PURPOSE}",
            }
        )
    elif result.list_status == "no_source_files":
        row["skip_or_failure_reason"] = "no source files listed for date"

    inventory_rows.append(row)

inventory = pd.DataFrame(inventory_rows)

summary = (
    inventory.groupby(["list_status", "accepted_for_v1"], dropna=False)
    .agg(
        n_dates=("date", "size"),
        n_files_listed=("n_files_listed", "sum"),
        total_listed_bytes=("total_listed_bytes", "sum"),
    )
    .reset_index()
)

if len(inventory) <= 30:
    display(inventory)
else:
    display(pd.concat([inventory.head(10), inventory.tail(10)], ignore_index=True))
display(summary)

# %% [markdown]
# ## 3 - Initial batch contract
#
# The inventory is the denominator. The batch spec only includes dates accepted by the source inventory. Later
# full-grid M0 evidence jobs should read this accepted date list rather than inventing the denominator.

# %%
BATCH_SIZE_DAYS = int(os.environ.get("MRMS_INVENTORY_BATCH_SIZE_DAYS", "14"))
accepted_dates = inventory.loc[inventory["accepted_for_v1"], "date"].sort_values().tolist()

batch_rows: list[dict[str, Any]] = []
for batch_idx, start in enumerate(range(0, len(accepted_dates), BATCH_SIZE_DAYS), start=1):
    chunk = accepted_dates[start : start + BATCH_SIZE_DAYS]
    if not chunk:
        continue
    batch_rows.append(
        {
            "run_id": RUN_ID,
            "batch_id": f"batch_{batch_idx:04d}",
            "date_start": chunk[0],
            "date_end": chunk[-1],
            "n_accepted_source_days": len(chunk),
            "source_inventory_path_local": str(INVENTORY_PARQUET.relative_to(ROOT)),
            "planned_m0_output_root_gcs": (
                "gs://infrasure-benchmark/"
                "hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/"
                f"run_id={RUN_ID}/"
            ),
            "status": "planned_from_inventory",
        }
    )

batch_spec = pd.DataFrame(batch_rows)
if len(batch_spec) <= 30:
    display(batch_spec)
else:
    display(pd.concat([batch_spec.head(10), batch_spec.tail(10)], ignore_index=True))

# %% [markdown]
# ## 4 - Write local artifacts

# %%
LOCAL_RUN_DIR.mkdir(parents=True, exist_ok=True)

inventory.to_parquet(INVENTORY_PARQUET, index=False)
inventory.to_csv(INVENTORY_CSV, index=False)
source_files.to_parquet(SOURCE_FILES_PARQUET, index=False)
source_files.to_csv(SOURCE_FILES_CSV, index=False)
batch_spec.to_csv(BATCH_SPEC_CSV, index=False)
summary.to_csv(SUMMARY_CSV, index=False)

accepted_date_index = pd.DatetimeIndex(pd.to_datetime(accepted_dates)) if accepted_dates else pd.DatetimeIndex([])
if len(accepted_date_index) > 0:
    expected_accepted_span = pd.date_range(accepted_date_index.min(), accepted_date_index.max(), freq="D")
    missing_after_first_accepted = expected_accepted_span.difference(accepted_date_index)
else:
    missing_after_first_accepted = pd.DatetimeIndex([])

list_status_counts = {
    str(k): int(v)
    for k, v in inventory["list_status"].value_counts(dropna=False).sort_index().items()
}
allowed_use = [
    "batch contract for full-grid M0 daily evidence",
    "GCS path contract if upload_to_gcs is true",
]
not_allowed_use = [
    "M0 daily cell evidence",
    "M1 frequency or size distribution",
    "reportable EAL/PML/VaR/TVaR input",
]
caveats = [
    "Accepted source tile is the latest listed daily tile, matching the one-day proof convention.",
    "This notebook lists source files but does not validate GRIB readability.",
    "Raw MRMS files are not mirrored into InfraSure GCS.",
]
if RUN_PURPOSE == "source_inventory_proof":
    allowed_use.insert(0, "MRMS V1 source denominator proof")
    not_allowed_use.insert(0, "final MRMS record denominator")
    caveats.insert(0, "Default date window is intentionally small unless overridden.")
else:
    allowed_use.insert(0, "MRMS V1 accepted source-date denominator")
    caveats.insert(
        0,
        "Requested window can include dates before public files are available; accepted_for_v1 defines the denominator.",
    )

metadata = {
    "artifact_family": "mrms_v1_source_inventory",
    "status": RUN_PURPOSE,
    "hazard": "hail",
    "source_set": "MRMS_ONLY",
    "source_product": PRODUCT,
    "threshold_mm_for_downstream_m0": THRESHOLD_MM,
    "run_id": RUN_ID,
    "requested_start_date": START_DATE,
    "requested_end_date": END_DATE,
    "n_requested_dates": int(len(dates)),
    "n_accepted_source_dates": int(inventory["accepted_for_v1"].sum()),
    "n_no_source_dates": int((inventory["list_status"] == "no_source_files").sum()),
    "n_list_failed_dates": int((inventory["list_status"] == "list_failed").sum()),
    "n_source_files_listed": int(len(source_files)),
    "list_status_counts": list_status_counts,
    "first_accepted_source_date": None if not accepted_dates else accepted_dates[0],
    "last_accepted_source_date": None if not accepted_dates else accepted_dates[-1],
    "missing_accepted_dates_after_first_count": int(len(missing_after_first_accepted)),
    "batch_size_days": BATCH_SIZE_DAYS,
    "n_batches_planned": int(len(batch_spec)),
    "source_bucket_http": SOURCE_BUCKET_HTTP,
    "source_bucket_s3": SOURCE_BUCKET_S3,
    "local_run_dir": str(LOCAL_RUN_DIR.relative_to(ROOT)),
    "gcs_run_root": GCS_RUN_ROOT,
    "upload_to_gcs": UPLOAD_TO_GCS,
    "local_outputs": {
        "inventory_parquet": str(INVENTORY_PARQUET.relative_to(ROOT)),
        "inventory_csv": str(INVENTORY_CSV.relative_to(ROOT)),
        "source_files_parquet": str(SOURCE_FILES_PARQUET.relative_to(ROOT)),
        "source_files_csv": str(SOURCE_FILES_CSV.relative_to(ROOT)),
        "batch_spec_csv": str(BATCH_SPEC_CSV.relative_to(ROOT)),
        "summary_csv": str(SUMMARY_CSV.relative_to(ROOT)),
        "metadata_json": str(METADATA_JSON.relative_to(ROOT)),
    },
    "planned_gcs_outputs": {
        "inventory_parquet": f"{GCS_RUN_ROOT}/{INVENTORY_PARQUET.name}",
        "inventory_csv": f"{GCS_RUN_ROOT}/{INVENTORY_CSV.name}",
        "source_files_parquet": f"{GCS_RUN_ROOT}/{SOURCE_FILES_PARQUET.name}",
        "source_files_csv": f"{GCS_RUN_ROOT}/{SOURCE_FILES_CSV.name}",
        "batch_spec_csv": f"{GCS_RUN_ROOT}/{BATCH_SPEC_CSV.name}",
        "summary_csv": f"{GCS_RUN_ROOT}/{SUMMARY_CSV.name}",
        "metadata_json": f"{GCS_RUN_ROOT}/{METADATA_JSON.name}",
    },
    "allowed_use": allowed_use,
    "not_allowed_use": not_allowed_use,
    "caveats": caveats,
}
METADATA_JSON.write_text(json.dumps(metadata, indent=2) + "\n")

print("wrote inventory parquet:", INVENTORY_PARQUET.relative_to(ROOT))
print("wrote source files parquet:", SOURCE_FILES_PARQUET.relative_to(ROOT))
print("wrote batch spec:", BATCH_SPEC_CSV.relative_to(ROOT))
print("wrote metadata:", METADATA_JSON.relative_to(ROOT))

# %% [markdown]
# ## 5 - Optional GCS upload
#
# Upload is disabled by default. When enabled, this writes only the small inventory artifacts to the run-scoped
# dev prefix and refuses to overwrite existing objects.

# %%
def gcs_object_exists(uri: str) -> bool:
    result = subprocess.run(
        ["gcloud", "storage", "ls", uri],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def upload_one(local_path: Path, gcs_root: str) -> str:
    destination = f"{gcs_root}/{local_path.name}"
    if gcs_object_exists(destination):
        raise FileExistsError(f"GCS destination already exists: {destination}")
    subprocess.run(
        ["gcloud", "storage", "cp", str(local_path), destination],
        check=True,
    )
    return destination


uploaded: list[str] = []
if UPLOAD_TO_GCS:
    for path in [
        INVENTORY_PARQUET,
        INVENTORY_CSV,
        SOURCE_FILES_PARQUET,
        SOURCE_FILES_CSV,
        BATCH_SPEC_CSV,
        SUMMARY_CSV,
    ]:
        uploaded.append(upload_one(path, GCS_RUN_ROOT))
    metadata["uploaded_gcs_outputs"] = uploaded + [f"{GCS_RUN_ROOT}/{METADATA_JSON.name}"]
    METADATA_JSON.write_text(json.dumps(metadata, indent=2) + "\n")
    uploaded.append(upload_one(METADATA_JSON, GCS_RUN_ROOT))
    print("uploaded artifacts:")
    for uri in uploaded:
        print("-", uri)
else:
    print("UPLOAD_TO_GCS is false; no remote artifacts written.")

# %% [markdown]
# ## 6 - Notebook result recap
#
# This is the key result table for the current execution. For the accepted V1 source-denominator run, it
# should show `run_purpose = v1_source_denominator_inventory`, 2,071 accepted source days, zero list failures,
# and 148 planned M0 batches.

# %%
result_recap = pd.DataFrame(
    [
        {
            "run_id": RUN_ID,
            "run_purpose": RUN_PURPOSE,
            "requested_start_date": START_DATE,
            "requested_end_date": END_DATE,
            "requested_dates": int(len(dates)),
            "accepted_source_dates": int(inventory["accepted_for_v1"].sum()),
            "no_source_dates": int((inventory["list_status"] == "no_source_files").sum()),
            "list_failed_dates": int((inventory["list_status"] == "list_failed").sum()),
            "first_accepted_source_date": None if not accepted_dates else accepted_dates[0],
            "last_accepted_source_date": None if not accepted_dates else accepted_dates[-1],
            "accepted_date_gaps_after_first": int(len(missing_after_first_accepted)),
            "source_files_listed": int(len(source_files)),
            "planned_m0_batches": int(len(batch_spec)),
            "local_run_dir": str(LOCAL_RUN_DIR.relative_to(ROOT)),
            "gcs_run_root": GCS_RUN_ROOT,
        }
    ]
)
display(result_recap)

# %% [markdown]
# ## 7 - Saved V1 checkpoint
#
# Validated full-run checkpoint from 2026-06-16:
#
# | Item | Value |
# |---|---:|
# | `run_id` | `20260616T165806Z` |
# | requested source window | `2014-01-01` to `2026-06-15` |
# | requested source dates | 4,549 |
# | accepted source dates | 2,071 |
# | no-source dates | 2,478 |
# | list-failed dates | 0 |
# | first accepted source date | `2020-10-14` |
# | last accepted source date | `2026-06-15` |
# | accepted-date gaps after first accepted | 0 |
# | source files listed | 99,313 |
# | planned 14-day M0 batches | 148 |
#
# Local and GCS artifacts:
#
# ```text
# data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
# gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
# ```
#
# Interpretation: the wider requested window intentionally records earlier no-source dates. The V1 denominator
# is the continuous accepted source-date set from `2020-10-14` through `2026-06-15`. These rows are source
# availability only, not hail/no-hail cell evidence.

# %% [markdown]
# ## 8 - Recap and next step
#
# This notebook proves the source-inventory shape:
#
# - one row per requested date;
# - full listed-source-file manifest;
# - accepted daily source tile per date;
# - batch spec for future M0 daily-cell evidence jobs;
# - run-scoped local/GCS paths.
#
# Next implementation step:
#
# ```text
# if proof run:
#   full intended MRMS source inventory
# if V1 denominator run:
#   small full-grid M0 daily evidence batch from accepted dates
# ```
