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
# # Hail V1 - Full MRMS M0 Cloud Output Review
#
# **Peril:** hail - **Layer:** M0 daily cell evidence - **Product:** `hazard_conus_grid` V1
#
# This notebook reviews the **full reconciled MRMS-only M0 layer** produced after the task-indexed Cloud Run
# fanout. It does not build M1 and does not compute asset losses. Its job is to answer:
#
# ```text
# Did the cloud/reconciled M0 output land cleanly, and is it sane enough to feed M1?
# ```
#
# Plan references:
#
# - `docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`
# - `docs/plans/hazard_conus_grid/hail/m0_m1_scaleout_execution.md`
# - `docs/plans/hazard_conus_grid/common/gcp_execution_and_storage_conventions.md`
# - `docs/principles/notebook_work/exploratory_data_notebooks.md`

# %% [markdown]
# ## 0 - Scope and controls
#
# Inputs:
#
# ```text
# raw Cloud Run batch root:
#   gs://infrasure-benchmark/.../m0_daily_cell_evidence/run_id=20260616T220624Z_m0_full_conus_task_indexed/
#
# reconciled M0 root reviewed here:
#   gs://infrasure-benchmark/.../m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
# ```
#
# This notebook reads the local mirror of the reconciled root. The metadata carries the GCS address, and the
# review artifacts can be uploaded to a small GCS review prefix when `HAZARD_CONUS_GRID_UPLOAD_TO_GCS=1`.

# %%
from __future__ import annotations

import json
import os
import base64
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display
from matplotlib.colors import LogNorm

plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130})


def repo_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise FileNotFoundError("repo root not found")


ROOT = repo_root()
RECONCILED_RUN_ID = os.environ.get("MRMS_M0_RECONCILED_RUN_ID", "20260616T225000Z_m0_full_conus_reconciled")
CLOUD_RUN_RUN_ID = os.environ.get("MRMS_M0_CLOUD_RUN_ID", "20260616T220624Z_m0_full_conus_task_indexed")
REVIEW_RUN_ID = os.environ.get(
    "HAZARD_CONUS_GRID_REVIEW_RUN_ID",
    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_m0_review"),
)
UPLOAD_TO_GCS = os.environ.get("HAZARD_CONUS_GRID_UPLOAD_TO_GCS", "0").lower() in {"1", "true", "yes"}
FORCE_REVIEW_OUTPUT = os.environ.get("HAZARD_CONUS_GRID_FORCE_REVIEW_OUTPUT", "0").lower() in {"1", "true", "yes"}

HAIL_GRID_DIR = ROOT / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only"
RECONCILED_ROOT = HAIL_GRID_DIR / "m0_reconciled_daily_cell_evidence" / f"run_id={RECONCILED_RUN_ID}"
REVIEW_ROOT = HAIL_GRID_DIR / "m0_review" / f"run_id={REVIEW_RUN_ID}"
MAP_DIR = REVIEW_ROOT / "maps"
TABLE_DIR = REVIEW_ROOT / "tables"
DIAGNOSTIC_DIR = REVIEW_ROOT / "diagnostics"
INTERACTIVE_MAP_DIR = REVIEW_ROOT / "interactive_maps"

RECONCILED_GCS_ROOT = (
    "gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/"
    f"m0_reconciled_daily_cell_evidence/run_id={RECONCILED_RUN_ID}"
)
REVIEW_GCS_ROOT = (
    "gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/"
    f"m0_review/run_id={REVIEW_RUN_ID}"
)

METADATA_JSON = RECONCILED_ROOT / f"metadata_{RECONCILED_RUN_ID}.json"
BATCH_MANIFEST_CSV = RECONCILED_ROOT / f"mrms_v1_m0_reconciled_batch_manifest_{RECONCILED_RUN_ID}.csv"
DATE_COVERAGE_CSV = RECONCILED_ROOT / f"mrms_v1_m0_reconciled_date_coverage_{RECONCILED_RUN_ID}.csv"
STATUS_SUMMARY_CSV = RECONCILED_ROOT / f"mrms_v1_m0_reconciled_status_summary_{RECONCILED_RUN_ID}.csv"

print("repo root:", ROOT)
print("cloud run batch run:", CLOUD_RUN_RUN_ID)
print("reconciled run:", RECONCILED_RUN_ID)
print("reconciled local root:", RECONCILED_ROOT.relative_to(ROOT))
print("reconciled gcs root:", RECONCILED_GCS_ROOT)
print("review run:", REVIEW_RUN_ID)
print("review local root:", REVIEW_ROOT.relative_to(ROOT))
print("review gcs root:", REVIEW_GCS_ROOT)
print("upload to gcs:", UPLOAD_TO_GCS)

# %% [markdown]
# ## 1 - Load sidecars and interpret the output contract
#
# The reconciled root is the M0 object that M1 should consume. Individual Cloud Run batch prefixes remain
# audit/debug material. The row contract is:
#
# ```text
# one row = one served benchmark cell_id on one accepted MRMS source date
# ```
#
# Important fields surfaced downstream:
#
# | field | unit/base | meaning | use decision |
# |---|---:|---|---|
# | `cell_id` | benchmark 0.25 degree cell | stable grid identifier | primary join key |
# | `date` | accepted MRMS source date | one daily `MESH_Max_1440min` tile | daily denominator |
# | `n_native_pixels_observed` | native MRMS pixels inside cell | coverage evidence | coverage QA |
# | `n_native_pixels_positive` | native pixels with `MESH > 0` | sub-severe or severe hail signal | M1 context |
# | `n_native_pixels_severe` | native pixels with `MESH >= 25.4 mm` | severe hail signal | M1 frequency spine |
# | `mesh_max_mm` | mm | max raw MRMS MESH inside the cell/date | size evidence; not de-biased |
# | `coverage_status` | category | no-data/no-hail/sub-severe/severe state | M0 QA and M1 input |
#
# MRMS MESH is a radar estimate, not ground truth hail size. This review checks raw evidence sanity; it does
# not de-bias MESH or fit tails.

# %%
for required_path in [METADATA_JSON, BATCH_MANIFEST_CSV, DATE_COVERAGE_CSV, STATUS_SUMMARY_CSV]:
    if not required_path.exists():
        raise FileNotFoundError(required_path)

metadata = json.loads(METADATA_JSON.read_text())
batch_manifest = pd.read_csv(BATCH_MANIFEST_CSV)
date_coverage = pd.read_csv(DATE_COVERAGE_CSV)
status_summary = pd.read_csv(STATUS_SUMMARY_CSV)
date_coverage["date"] = pd.to_datetime(date_coverage["date"])
status_summary["date"] = pd.to_datetime(status_summary["date"])

contract_summary = pd.DataFrame(
    [
        ("metadata_status", metadata["status"], "status", "must pass before M1"),
        ("input_batches", metadata["n_input_batches"], "batches", "expected 148"),
        ("date_start", metadata["date_start"], "date", "first accepted source date"),
        ("date_end", metadata["date_end"], "date", "last accepted source date"),
        ("accepted_dates", metadata["n_dates"], "dates", "M0 time denominator"),
        ("served_cells_per_date", metadata["n_served_cells"], "cells/date", "M0 spatial denominator"),
        ("expected_rows", metadata["expected_rows"], "rows", "dates x cells"),
        ("n_output_rows", metadata["n_output_rows"], "rows", "actual rows"),
        ("duplicate_cell_date_rows", metadata["duplicate_cell_date_rows"], "rows", "must be 0"),
        ("failed_date_row_counts", len(metadata.get("failed_date_row_counts", [])), "dates", "must be 0"),
        ("qa_flags", ", ".join(metadata.get("qa_flags", [])) or "none", "flags", "review before M1"),
    ],
    columns=["item", "value", "unit/base", "interpretation"],
)
display(contract_summary)

# %% [markdown]
# **Takeaway.** The sidecars are the fast way to verify the full cloud run. They should agree with the
# metadata before we scan daily parquet partitions.

# %%
sidecar_checks = pd.DataFrame(
    [
        ("batch_manifest_rows", len(batch_manifest), metadata["n_input_batches"]),
        ("batch_manifest_dates_sum", int(batch_manifest["n_dates"].sum()), metadata["n_dates"]),
        ("batch_manifest_rows_sum", int(batch_manifest["n_rows"].sum()), metadata["n_output_rows"]),
        ("date_coverage_dates", int(date_coverage["date"].nunique()), metadata["n_dates"]),
        ("date_coverage_rows_sum", int(date_coverage["n_rows"].sum()), metadata["n_output_rows"]),
        ("date_coverage_failed_dates", int((date_coverage["row_count_status"] != "pass").sum()), 0),
        ("status_summary_cells_sum", int(status_summary["n_cells"].sum()), metadata["n_output_rows"]),
    ],
    columns=["check", "observed", "expected"],
)
sidecar_checks["status"] = np.where(sidecar_checks["observed"].eq(sidecar_checks["expected"]), "pass", "fail")
display(sidecar_checks)

if not sidecar_checks["status"].eq("pass").all():
    raise AssertionError("sidecar checks failed")

# %% [markdown]
# ## 2 - Daily denominator and severe-cell-day time series
#
# This section uses only compact sidecars. It confirms the daily row denominator and shows when large hail
# patterns happened in the record.

# %%
daily_wide = date_coverage.copy()
for col in ["observed_no_hail", "observed_sub_severe_hail", "observed_severe_hail", "no_native_pixel_coverage"]:
    if col not in daily_wide.columns:
        daily_wide[col] = 0
    daily_wide[col] = daily_wide[col].fillna(0).astype(int)

daily_max_mesh = status_summary.groupby("date")["max_mesh_mm"].max().rename("daily_max_mesh_mm").reset_index()
daily_wide = daily_wide.merge(daily_max_mesh, on="date", how="left")

daily_summary_path = TABLE_DIR / f"m0_review_daily_summary_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.csv"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
daily_wide.to_csv(daily_summary_path, index=False)

display(daily_wide.head())
display(
    daily_wide[["observed_severe_hail", "observed_sub_severe_hail", "daily_max_mesh_mm"]]
    .describe(percentiles=[0.5, 0.9, 0.95, 0.99])
    .T
)

# %%
MAP_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(daily_wide["date"], daily_wide["observed_severe_hail"], linewidth=0.9, color="#9c1b12")
ax.set_title("MRMS V1 M0 - severe cell-day count by accepted source date")
ax.set_xlabel("Accepted MRMS source date")
ax.set_ylabel("served cells with >= 1 severe native pixel")
fig.tight_layout()
daily_severe_plot = MAP_DIR / f"m0_review_daily_severe_cell_count_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
fig.savefig(daily_severe_plot, bbox_inches="tight")
plt.show()

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(daily_wide["date"], daily_wide["daily_max_mesh_mm"], linewidth=0.9, color="#4c2c92")
ax.axhline(300, color="#b2182b", linestyle="--", linewidth=1, label="300 mm QA flag threshold")
ax.set_title("MRMS V1 M0 - daily max raw MESH")
ax.set_xlabel("Accepted MRMS source date")
ax.set_ylabel("max MESH in any served cell, mm")
ax.legend(loc="upper right")
fig.tight_layout()
daily_max_plot = MAP_DIR / f"m0_review_daily_max_mesh_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
fig.savefig(daily_max_plot, bbox_inches="tight")
plt.show()

# %% [markdown]
# **Takeaway.** Date coverage is complete after reconciliation. Spikes in severe-cell-day count are expected
# because MRMS records storm days as gridded fields; the extreme MESH spike needs a separate record-level QA
# check below.

# %% [markdown]
# ## 3 - Stream daily partitions into a cell-level review table
#
# Reading the full 27.1M-row M0 layer into memory at once is not needed for QA. We stream one daily parquet
# partition at a time and accumulate per-cell counts. This mirrors the M1 direction without creating the M1
# artifact yet.

# %%
partition_paths = sorted(RECONCILED_ROOT.glob("date=*/part-000.parquet"), key=lambda p: p.parent.name)
if len(partition_paths) != metadata["n_dates"]:
    raise AssertionError(f"expected {metadata['n_dates']} partitions, found {len(partition_paths)}")

sample = pd.read_parquet(partition_paths[0])
required_columns = [
    "cell_id",
    "date",
    "lat_center",
    "lon_center",
    "state_abbr",
    "iso_rto",
    "n_native_pixels_observed",
    "n_native_pixels_positive",
    "n_native_pixels_severe",
    "mesh_max_mm",
    "coverage_status",
    "source_key",
    "source_timestamp",
]
missing_columns = sorted(set(required_columns) - set(sample.columns))
if missing_columns:
    raise ValueError(f"M0 partitions missing columns: {missing_columns}")

cell_base = sample[["cell_id", "lat_center", "lon_center", "state_abbr", "iso_rto"]].sort_values("cell_id").reset_index(drop=True)
if not cell_base["cell_id"].is_unique:
    raise AssertionError("sample partition has duplicate cell_id rows")

cell_to_pos = pd.Series(np.arange(len(cell_base), dtype=np.int64), index=cell_base["cell_id"]).to_dict()
n_cells = len(cell_base)

observed_days = np.zeros(n_cells, dtype=np.int32)
no_coverage_days = np.zeros(n_cells, dtype=np.int32)
no_hail_days = np.zeros(n_cells, dtype=np.int32)
sub_severe_days = np.zeros(n_cells, dtype=np.int32)
severe_days = np.zeros(n_cells, dtype=np.int32)
positive_pixels_total = np.zeros(n_cells, dtype=np.int64)
severe_pixels_total = np.zeros(n_cells, dtype=np.int64)
max_mesh = np.full(n_cells, np.nan, dtype=np.float32)
extreme_rows: list[pd.DataFrame] = []

scan_t0 = time.perf_counter()
for i, path in enumerate(partition_paths, start=1):
    day = pd.read_parquet(path, columns=required_columns)
    if len(day) != metadata["n_served_cells"]:
        raise AssertionError(f"{path}: expected {metadata['n_served_cells']} rows, got {len(day)}")
    if not day["cell_id"].is_unique:
        raise AssertionError(f"{path}: duplicate cell_id rows")

    pos = day["cell_id"].map(cell_to_pos).to_numpy()
    if np.isnan(pos).any():
        raise AssertionError(f"{path}: cell_id not in base cell index")
    pos = pos.astype(np.int64)

    status = day["coverage_status"].to_numpy()
    observed_days[pos] += (day["n_native_pixels_observed"].to_numpy() > 0).astype(np.int32)
    no_coverage_days[pos] += (status == "no_native_pixel_coverage").astype(np.int32)
    no_hail_days[pos] += (status == "observed_no_hail").astype(np.int32)
    sub_severe_days[pos] += (status == "observed_sub_severe_hail").astype(np.int32)
    severe_days[pos] += (status == "observed_severe_hail").astype(np.int32)
    positive_pixels_total[pos] += day["n_native_pixels_positive"].to_numpy(dtype=np.int64)
    severe_pixels_total[pos] += day["n_native_pixels_severe"].to_numpy(dtype=np.int64)

    values = day["mesh_max_mm"].to_numpy(dtype=np.float32)
    previous = np.nan_to_num(max_mesh[pos], nan=-np.inf)
    current = np.nan_to_num(values, nan=-np.inf)
    max_mesh[pos] = np.maximum(previous, current)
    max_mesh[np.isneginf(max_mesh)] = np.nan

    extreme = day[day["mesh_max_mm"].ge(300, fill_value=False)].copy()
    if not extreme.empty:
        extreme_rows.append(extreme)

    if i == 1 or i % 250 == 0 or i == len(partition_paths):
        print(f"scanned {i:,}/{len(partition_paths):,} daily partitions")

scan_elapsed = time.perf_counter() - scan_t0
print(f"partition scan elapsed seconds: {scan_elapsed:.2f}")

# %%
observed_years = metadata["n_dates"] / 365.25
cell_summary = cell_base.copy()
cell_summary["n_source_days"] = int(metadata["n_dates"])
cell_summary["n_observed_days"] = observed_days
cell_summary["n_no_coverage_days"] = no_coverage_days
cell_summary["n_no_hail_days"] = no_hail_days
cell_summary["n_sub_severe_days"] = sub_severe_days
cell_summary["n_severe_hail_days"] = severe_days
cell_summary["observed_day_fraction"] = observed_days / metadata["n_dates"]
cell_summary["severe_hail_day_rate_per_year_raw"] = severe_days / observed_years
cell_summary["n_positive_native_pixels_total"] = positive_pixels_total
cell_summary["n_severe_native_pixels_total"] = severe_pixels_total
cell_summary["max_mesh_mm"] = max_mesh
cell_summary["max_mesh_mm_for_map_clipped_150"] = np.minimum(cell_summary["max_mesh_mm"], 150)
cell_summary["qa_extreme_mesh_ge_300mm"] = cell_summary["max_mesh_mm"].ge(300).fillna(False)

cell_summary_path = TABLE_DIR / f"m0_review_cell_summary_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.parquet"
cell_summary_csv = TABLE_DIR / f"m0_review_cell_summary_top_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.csv"
cell_summary.to_parquet(cell_summary_path, index=False)
cell_summary.sort_values(["n_severe_hail_days", "max_mesh_mm"], ascending=False).head(250).to_csv(cell_summary_csv, index=False)

display(
    cell_summary[
        [
            "n_observed_days",
            "n_severe_hail_days",
            "severe_hail_day_rate_per_year_raw",
            "max_mesh_mm",
            "observed_day_fraction",
        ]
    ].describe(percentiles=[0.5, 0.9, 0.95, 0.99]).T
)
display(cell_summary.sort_values(["n_severe_hail_days", "max_mesh_mm"], ascending=False).head(10))

# %% [markdown]
# **Takeaway.** The cell summary is the right bridge into M1, but this artifact is still a review output. The
# annualized rate is a raw observed frequency proxy over the MRMS source window, not a finalized hazard model.

# %% [markdown]
# ## 4 - Extreme raw MESH QA
#
# The reconciled metadata carries `extreme_mesh_ge_300mm`. This is a raw MRMS QA flag. It does not
# automatically mean the row is wrong, but M1/M2 should know whether the extreme is isolated or systematic.

# %%
if extreme_rows:
    extreme_records = pd.concat(extreme_rows, ignore_index=True)
else:
    extreme_records = pd.DataFrame(columns=required_columns)

extreme_records = extreme_records.sort_values("mesh_max_mm", ascending=False).reset_index(drop=True)
extreme_records_path = TABLE_DIR / f"m0_review_extreme_mesh_records_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.csv"
extreme_records.to_csv(extreme_records_path, index=False)

extreme_summary = pd.DataFrame(
    [
        ("extreme_record_count", len(extreme_records), "cell-days", "mesh_max_mm >= 300"),
        ("extreme_cell_count", int(extreme_records["cell_id"].nunique()) if not extreme_records.empty else 0, "cells", "unique cells with an extreme record"),
        ("extreme_date_count", int(pd.to_datetime(extreme_records["date"]).dt.date.nunique()) if not extreme_records.empty else 0, "dates", "unique dates with an extreme record"),
        ("max_mesh_mm", None if extreme_records.empty else float(extreme_records["mesh_max_mm"].max()), "mm", "largest raw MESH in M0"),
    ],
    columns=["item", "value", "unit/base", "interpretation"],
)
display(extreme_summary)
display(extreme_records.head(25))

severity_qa_status = (
    "severity_requires_qa_filter_or_sensitivity"
    if len(extreme_records) > 0
    else "raw_mesh_severity_has_no_ge_300mm_extreme_records"
)
m0_row_contract_status = "passed"
m1_readiness = (
    "frequency_ready_after_review; severity_size_distribution_needs_extreme_mesh_rule"
    if len(extreme_records) > 0
    else "frequency_and_observed_size_ready_after_review"
)

review_recommendation = pd.DataFrame(
    [
        ("M0 row contract", m0_row_contract_status, "row counts, date coverage, and duplicate checks passed"),
        (
            "raw MESH severity",
            severity_qa_status,
            "extreme raw MESH records are not a GCP failure, but should not silently feed severity/loss",
        ),
        (
            "M1 next step",
            m1_readiness,
            "frequency can use severe-day flags; empirical size summaries need a named QA/capping decision",
        ),
    ],
    columns=["area", "status", "interpretation"],
)
display(review_recommendation)

# %% [markdown]
# **Takeaway.** The extreme-MESH issue is not a cloud-output failure. The M0 row contract passed. But because
# the extreme records are repeated across multiple cells/dates, raw MESH severity should not silently feed
# empirical size distributions or loss metrics. Frequency can proceed from the severe-day flag after review;
# severity/size needs a named QA rule or sensitivity.

# %% [markdown]
# ## 5 - Raw MESH tail diagnostics
#
# The purpose of this section is to keep two ideas separate:
#
# ```text
# event signal:      did the cell/day likely contain severe convection or hail evidence?
# severity magnitude: how large should the hail-size value be allowed to be in modeling?
# ```
#
# A very large raw MESH value can still be useful as an **event-signal candidate**. What is not acceptable is
# silently treating physically implausible values, such as 1,000+ mm, as literal hail size in empirical severity
# distributions or downstream loss.

# %%
DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)

mesh_threshold_interpretation = pd.DataFrame(
    [
        (
            ">= 25.4 mm",
            "severe-day occurrence threshold",
            "usable for M0 frequency after row/coverage QA",
        ),
        (
            "150 mm display clip",
            "visualization scale only",
            "keeps maps readable; does not change raw data",
        ),
        (
            ">= 300 mm",
            "extreme raw-MESH QA flag",
            "candidate event evidence, but not trusted as literal size without validation/capping/sensitivity",
        ),
        (
            "1,000+ mm",
            "physically implausible hail-size magnitude",
            "strong source/algorithm/processing artifact signal for severity; still inspect date/cell context",
        ),
    ],
    columns=["range_or_rule", "meaning", "modeling_use"],
)
display(mesh_threshold_interpretation)

diagnostic_paths: list[Path] = []

positive_mesh = cell_summary.loc[cell_summary["max_mesh_mm"].fillna(0) > 0, "max_mesh_mm"].copy()
tail_hist_path = DIAGNOSTIC_DIR / f"m0_review_raw_mesh_tail_distribution_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
if not positive_mesh.empty:
    lower = max(float(positive_mesh.min()), 1.0)
    upper = float(positive_mesh.max())
    bins = np.geomspace(lower, upper, 70) if upper > lower else 20
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.hist(positive_mesh, bins=bins, color="#4c78a8", edgecolor="white", linewidth=0.25)
    ax.set_xscale("log")
    ax.set_yscale("log")
    for threshold, label, color in [
        (25.4, "severe threshold 25.4 mm", "#2b8cbe"),
        (150.0, "display clip 150 mm", "#fdae61"),
        (300.0, "QA flag 300 mm", "#d7191c"),
    ]:
        ax.axvline(threshold, color=color, linestyle="--", linewidth=1.1, label=label)
    ax.set_title("MRMS V1 M0 - raw max-MESH tail by served cell")
    ax.set_xlabel("cell max raw MESH over source window (mm, log scale)")
    ax.set_ylabel("served cells (log count)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(tail_hist_path, bbox_inches="tight")
    plt.show()
    diagnostic_paths.append(tail_hist_path)

mesh_vs_frequency_path = DIAGNOSTIC_DIR / f"m0_review_mesh_tail_vs_frequency_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
plot_frame = cell_summary[cell_summary["max_mesh_mm"].fillna(0) > 0].copy()
if not plot_frame.empty:
    fig, ax = plt.subplots(figsize=(10, 5.4))
    background = plot_frame[~plot_frame["qa_extreme_mesh_ge_300mm"]]
    flagged = plot_frame[plot_frame["qa_extreme_mesh_ge_300mm"]]
    ax.scatter(
        background["max_mesh_mm"],
        background["n_severe_hail_days"] + 1,
        s=10,
        c="#2b8cbe",
        alpha=0.45,
        linewidths=0,
        label="max MESH < 300 mm",
    )
    if not flagged.empty:
        ax.scatter(
            flagged["max_mesh_mm"],
            flagged["n_severe_hail_days"] + 1,
            s=24,
            c="#d7191c",
            alpha=0.78,
            linewidths=0.35,
            edgecolors="#4d0000",
            label="max MESH >= 300 mm QA flag",
        )
    ax.axvline(25.4, color="#2b8cbe", linestyle="--", linewidth=1.0)
    ax.axvline(150.0, color="#fdae61", linestyle="--", linewidth=1.0)
    ax.axvline(300.0, color="#d7191c", linestyle="--", linewidth=1.0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("MRMS V1 M0 - raw MESH tail versus severe-day frequency")
    ax.set_xlabel("cell max raw MESH over source window (mm, log scale)")
    ax.set_ylabel("severe hail days + 1 (log scale)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(mesh_vs_frequency_path, bbox_inches="tight")
    plt.show()
    diagnostic_paths.append(mesh_vs_frequency_path)

if extreme_records.empty:
    extreme_by_date = pd.DataFrame(
        columns=[
            "date",
            "n_extreme_cell_days",
            "n_extreme_cells",
            "max_mesh_mm",
            "states",
            "min_lon",
            "max_lon",
            "min_lat",
            "max_lat",
        ]
    )
else:
    extreme_records_for_grouping = extreme_records.copy()
    extreme_records_for_grouping["date"] = pd.to_datetime(extreme_records_for_grouping["date"]).dt.date.astype(str)
    extreme_by_date = (
        extreme_records_for_grouping.groupby("date", as_index=False)
        .agg(
            n_extreme_cell_days=("cell_id", "size"),
            n_extreme_cells=("cell_id", "nunique"),
            max_mesh_mm=("mesh_max_mm", "max"),
            states=("state_abbr", lambda values: ",".join(sorted(values.dropna().astype(str).unique())[:12])),
            min_lon=("lon_center", "min"),
            max_lon=("lon_center", "max"),
            min_lat=("lat_center", "min"),
            max_lat=("lat_center", "max"),
        )
        .sort_values(["n_extreme_cell_days", "max_mesh_mm"], ascending=False)
        .reset_index(drop=True)
    )

extreme_by_date_path = TABLE_DIR / f"m0_review_extreme_mesh_by_date_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.csv"
extreme_by_date.to_csv(extreme_by_date_path, index=False)
display(extreme_by_date.head(20))

top_extreme_dates_path = DIAGNOSTIC_DIR / f"m0_review_top_extreme_mesh_dates_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
if not extreme_by_date.empty:
    top_dates = extreme_by_date.head(15).sort_values("n_extreme_cell_days", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.barh(top_dates["date"], top_dates["n_extreme_cell_days"], color="#d7191c", alpha=0.85)
    ax.set_title("MRMS V1 M0 - top dates with raw MESH >= 300 mm")
    ax.set_xlabel("extreme cell-days")
    ax.set_ylabel("source date")
    for _, row in top_dates.iterrows():
        ax.text(
            row["n_extreme_cell_days"] + max(top_dates["n_extreme_cell_days"]) * 0.01,
            row["date"],
            f"max {row['max_mesh_mm']:.0f} mm",
            va="center",
            fontsize=8,
        )
    fig.tight_layout()
    fig.savefig(top_extreme_dates_path, bbox_inches="tight")
    plt.show()
    diagnostic_paths.append(top_extreme_dates_path)

# %% [markdown]
# **Diagnostic interpretation.** The extreme tail should be treated as a split signal:
#
# - It can remain useful for **occurrence/context**: the date/cell likely deserves severe-convective review.
# - It should not be used as literal **hail-size severity** until we decide a QA rule.
# - The next M1 design should therefore carry both fields: raw/provenance values for audit, and a separate
#   QC modeling value for empirical size distributions.

# %% [markdown]
# ## 6 - CONUS review maps
#
# These are quick QA maps, not cartographic release figures. They answer:
#
# - where did severe hail happen most often in the MRMS window?
# - where are the largest raw MESH values?
# - did every served cell have full daily coverage?
# - where are the extreme MESH records?

# %%
def base_map(ax: plt.Axes, title: str) -> None:
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(-125.5, -66.0)
    ax.set_ylim(24.0, 50.5)
    ax.set_aspect("equal", adjustable="box")


def plot_positive_metric(
    frame: pd.DataFrame,
    metric: str,
    title: str,
    output_name: str,
    colorbar_label: str,
    *,
    cmap: str = "viridis",
    log_scale: bool = False,
) -> Path:
    path = MAP_DIR / output_name
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.scatter(frame["lon_center"], frame["lat_center"], s=2.2, c="#d9d9d9", linewidths=0, alpha=0.55)
    plotted = frame[frame[metric].fillna(0) > 0].copy()
    norm = None
    if log_scale and not plotted.empty:
        norm = LogNorm(vmin=max(float(plotted[metric].min()), 1.0), vmax=float(plotted[metric].max()))
    scatter = ax.scatter(
        plotted["lon_center"],
        plotted["lat_center"],
        s=5,
        c=plotted[metric],
        cmap=cmap,
        norm=norm,
        linewidths=0,
        alpha=0.9,
    )
    if not plotted.empty:
        cbar = fig.colorbar(scatter, ax=ax, shrink=0.78)
        cbar.set_label(colorbar_label)
    base_map(ax, title)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.show()
    return path


def plot_metric_all_cells(
    frame: pd.DataFrame,
    metric: str,
    title: str,
    output_name: str,
    colorbar_label: str,
    *,
    cmap: str = "viridis",
    vmin: float | None = None,
    vmax: float | None = None,
) -> Path:
    path = MAP_DIR / output_name
    fig, ax = plt.subplots(figsize=(11, 6.2))
    scatter = ax.scatter(
        frame["lon_center"],
        frame["lat_center"],
        s=5,
        c=frame[metric],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        linewidths=0,
        alpha=0.9,
    )
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.78)
    cbar.set_label(colorbar_label)
    base_map(ax, title)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.show()
    return path


severe_count_map = plot_positive_metric(
    cell_summary,
    "n_severe_hail_days",
    "MRMS V1 M0 - severe hail-day count by served cell",
    f"m0_review_map_severe_hail_day_count_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png",
    "severe hail days",
    cmap="magma",
    log_scale=True,
)

rate_map = plot_positive_metric(
    cell_summary,
    "severe_hail_day_rate_per_year_raw",
    "MRMS V1 M0 - raw annualized severe hail-day rate proxy",
    f"m0_review_map_severe_hail_day_rate_raw_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png",
    "severe hail days per year, raw observed",
    cmap="plasma",
)

max_mesh_map = plot_positive_metric(
    cell_summary,
    "max_mesh_mm_for_map_clipped_150",
    "MRMS V1 M0 - max raw MESH by served cell (clipped at 150 mm for map)",
    f"m0_review_map_max_mesh_clipped_150mm_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png",
    "max MESH mm, clipped at 150",
    cmap="inferno",
)

coverage_map = plot_metric_all_cells(
    cell_summary,
    "observed_day_fraction",
    "MRMS V1 M0 - observed native-pixel coverage fraction by served cell",
    f"m0_review_map_observed_day_fraction_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png",
    "observed days / source days",
    cmap="viridis",
    vmin=0.0,
    vmax=1.0,
)

extreme_map = MAP_DIR / f"m0_review_map_extreme_mesh_cells_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.png"
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.scatter(cell_summary["lon_center"], cell_summary["lat_center"], s=2.2, c="#d9d9d9", linewidths=0, alpha=0.55)
extreme_cells = cell_summary[cell_summary["qa_extreme_mesh_ge_300mm"]]
if not extreme_cells.empty:
    ax.scatter(
        extreme_cells["lon_center"],
        extreme_cells["lat_center"],
        s=28,
        c="#d7191c",
        linewidths=0.4,
        edgecolors="#4d0000",
        label=f"cells with max MESH >= 300 mm ({len(extreme_cells):,})",
    )
    ax.legend(loc="lower left", frameon=True)
base_map(ax, "MRMS V1 M0 - cells with extreme raw MESH QA flag")
fig.tight_layout()
fig.savefig(extreme_map, bbox_inches="tight")
plt.show()

map_paths = [daily_severe_plot, daily_max_plot, severe_count_map, rate_map, max_mesh_map, coverage_map, extreme_map]

# %% [markdown]
# ### How to read the cell maps
#
# The maps serve different review purposes:
#
# - **Observed native-pixel coverage fraction** is the denominator/coverage check. Near-1.0 means the MRMS
#   daily source produced usable native pixels for that served cell on nearly every reviewed source day.
# - **Severe hail-day count** is the main M0 frequency QA map. It counts days where at least one native MRMS
#   pixel in the 0.25 degree cell crossed the severe hail threshold.
# - **Raw annualized severe hail-day rate proxy** is the same count divided by the MRMS source-window length.
#   It is useful for visual comparison, but it is not yet a finalized climatological frequency model.
# - **Max raw MESH by cell** is a severity screening map. It is clipped at 150 mm only for visualization, so
#   the color scale stays readable.
# - **Extreme raw MESH cells** are a QA flag where raw `max_mesh_mm >= 300`. Circular/ring-like clusters in
#   this layer are treated as source-severity artifacts until separately validated. They do not invalidate the
#   M0 row contract, but they should not feed M1 size distributions or M2-M4 loss severity without an explicit
#   capping/filter/sensitivity rule.
#
# In short: use the coverage map to confirm the denominator, the severe-day count/rate maps for frequency
# review, and the max-MESH/extreme maps to decide the severity QA rule.

# %% [markdown]
# ### In-notebook map gallery
#
# The PNG files are saved because they are durable artifacts and easy to upload/share. But review should not
# require opening separate files one by one, so this cell embeds the key maps directly in the notebook.

# %%
gallery_items = [
    ("Daily severe cell count", daily_severe_plot),
    ("Daily max raw MESH", daily_max_plot),
    ("Severe hail-day count by cell", severe_count_map),
    ("Raw annualized severe-day rate proxy", rate_map),
    ("Max raw MESH by cell, clipped at 150 mm", max_mesh_map),
    ("Observed day fraction", coverage_map),
    ("Extreme raw MESH cells", extreme_map),
]


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


gallery_blocks = []
for title, path in gallery_items:
    gallery_blocks.append(
        f"""
        <section style="margin: 0 0 22px 0;">
          <h4 style="margin: 0 0 6px 0;">{title}</h4>
          <img src="{image_data_uri(path)}" style="max-width: 100%; border: 1px solid #ddd;" />
          <div style="font-size: 12px; color: #555; margin-top: 4px;">{path.name}</div>
        </section>
        """
    )

gallery_html = f"""
<div>
  <h3>MRMS V1 M0 Review Map Gallery</h3>
  <p>
    Static in-notebook map gallery for the reconciled M0 review run
    <code>{REVIEW_RUN_ID}</code>. These are QA views, not release cartography.
  </p>
  {''.join(gallery_blocks)}
</div>
"""
display(HTML(gallery_html))

gallery_html_path = REVIEW_ROOT / f"m0_review_map_gallery_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.html"
gallery_html_path.write_text(gallery_html)
print("wrote map gallery:", gallery_html_path.relative_to(ROOT))

# %% [markdown]
# **Takeaway.** The review maps show a plausible severe-day corridor and complete served-cell coverage. The
# clipped max-MESH map is intentionally clipped for readability; the extreme-record table carries true values.

# %% [markdown]
# ### Interactive map views
#
# These Plotly maps are for notebook review: pan, zoom, and hover over each served cell. They deliberately use
# lon/lat axes instead of external map tiles, so they work without API tokens or a tile service. The standalone
# HTML files use Plotly from CDN; if offline, use the static PNG gallery above.

# %%
INTERACTIVE_MAP_DIR.mkdir(parents=True, exist_ok=True)

plotly_config = {
    "displaylogo": False,
    "scrollZoom": True,
    "toImageButtonOptions": {"format": "png", "scale": 2},
}
interactive_hover_columns = [
    "cell_id",
    "state_abbr",
    "iso_rto",
    "n_severe_hail_days",
    "severe_hail_day_rate_per_year_raw",
    "max_mesh_mm",
    "observed_day_fraction",
]


def add_lonlat_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=650,
        margin={"l": 55, "r": 25, "t": 70, "b": 55},
        dragmode="pan",
        xaxis={
            "title": "Longitude",
            "range": [-125.5, -66.0],
            "showgrid": True,
            "zeroline": False,
        },
        yaxis={
            "title": "Latitude",
            "range": [24.0, 50.5],
            "scaleanchor": "x",
            "scaleratio": 1,
            "showgrid": True,
            "zeroline": False,
        },
    )
    return fig


def make_interactive_metric_map(
    frame: pd.DataFrame,
    metric: str,
    title: str,
    output_name: str,
    colorbar_title: str,
    *,
    colorscale: str,
    clip_max: float | None = None,
    color_transform: str | None = None,
) -> tuple[go.Figure, Path]:
    values = frame[metric].fillna(0).astype(float)
    color_title = colorbar_title
    if clip_max is not None:
        values = values.clip(upper=clip_max)
        color_title = f"{colorbar_title}<br>(clipped at {clip_max:g})"
    if color_transform == "log1p":
        color_values = np.log10(values + 1.0)
        color_title = f"log10({colorbar_title} + 1)"
    else:
        color_values = values

    fig = go.Figure(
        go.Scattergl(
            x=frame["lon_center"],
            y=frame["lat_center"],
            mode="markers",
            marker={
                "size": 5,
                "color": color_values,
                "colorscale": colorscale,
                "colorbar": {"title": color_title},
                "opacity": 0.88,
                "line": {"width": 0},
            },
            customdata=frame[interactive_hover_columns].to_numpy(),
            hovertemplate=(
                "cell_id=%{customdata[0]}<br>"
                "state=%{customdata[1]}<br>"
                "iso_rto=%{customdata[2]}<br>"
                "lon=%{x:.2f}, lat=%{y:.2f}<br>"
                "severe_days=%{customdata[3]:,}<br>"
                "raw_rate=%{customdata[4]:.3f}/yr<br>"
                "max_mesh=%{customdata[5]:.1f} mm<br>"
                "observed_fraction=%{customdata[6]:.3f}<extra></extra>"
            ),
        )
    )
    add_lonlat_layout(fig, title)
    output_path = INTERACTIVE_MAP_DIR / output_name
    fig.write_html(output_path, include_plotlyjs="cdn", full_html=True, config=plotly_config)
    return fig, output_path


def make_interactive_extreme_map(frame: pd.DataFrame, output_name: str) -> tuple[go.Figure, Path]:
    background = frame[~frame["qa_extreme_mesh_ge_300mm"]]
    extreme = frame[frame["qa_extreme_mesh_ge_300mm"]]
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=background["lon_center"],
            y=background["lat_center"],
            mode="markers",
            marker={"size": 4, "color": "#d9d9d9", "opacity": 0.45, "line": {"width": 0}},
            customdata=background[interactive_hover_columns].to_numpy(),
            hovertemplate=(
                "cell_id=%{customdata[0]}<br>"
                "state=%{customdata[1]}<br>"
                "max_mesh=%{customdata[5]:.1f} mm<extra>non-extreme</extra>"
            ),
            name="non-extreme",
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=extreme["lon_center"],
            y=extreme["lat_center"],
            mode="markers",
            marker={"size": 8, "color": "#d7191c", "opacity": 0.9, "line": {"width": 0.5, "color": "#4d0000"}},
            customdata=extreme[interactive_hover_columns].to_numpy(),
            hovertemplate=(
                "cell_id=%{customdata[0]}<br>"
                "state=%{customdata[1]}<br>"
                "iso_rto=%{customdata[2]}<br>"
                "lon=%{x:.2f}, lat=%{y:.2f}<br>"
                "severe_days=%{customdata[3]:,}<br>"
                "max_mesh=%{customdata[5]:.1f} mm<extra>max MESH >= 300 mm</extra>"
            ),
            name=f"max MESH >= 300 mm ({len(extreme):,} cells)",
        )
    )
    add_lonlat_layout(fig, "MRMS V1 M0 - interactive extreme raw MESH cells")
    output_path = INTERACTIVE_MAP_DIR / output_name
    fig.write_html(output_path, include_plotlyjs="cdn", full_html=True, config=plotly_config)
    return fig, output_path


interactive_specs = [
    (
        "Severe hail-day count",
        "n_severe_hail_days",
        "MRMS V1 M0 - interactive severe hail-day count by cell",
        "m0_review_interactive_severe_hail_day_count.html",
        "severe days",
        "Magma",
        None,
        "log1p",
    ),
    (
        "Raw annualized severe-day rate proxy",
        "severe_hail_day_rate_per_year_raw",
        "MRMS V1 M0 - interactive raw annualized severe-day rate proxy",
        "m0_review_interactive_severe_hail_day_rate_raw.html",
        "severe days/year",
        "Plasma",
        None,
        None,
    ),
    (
        "Max raw MESH, clipped at 150 mm",
        "max_mesh_mm",
        "MRMS V1 M0 - interactive max raw MESH by cell",
        "m0_review_interactive_max_mesh_clipped_150mm.html",
        "max MESH mm",
        "Inferno",
        150.0,
        None,
    ),
    (
        "Observed day fraction",
        "observed_day_fraction",
        "MRMS V1 M0 - interactive observed native-pixel coverage fraction",
        "m0_review_interactive_observed_day_fraction.html",
        "observed fraction",
        "Viridis",
        None,
        None,
    ),
]

interactive_map_paths: list[Path] = []
interactive_sections = []
for label, metric, title, output_name, colorbar_title, colorscale, clip_max, color_transform in interactive_specs:
    fig, html_path = make_interactive_metric_map(
        cell_summary,
        metric,
        title,
        f"{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}_{output_name}",
        colorbar_title,
        colorscale=colorscale,
        clip_max=clip_max,
        color_transform=color_transform,
    )
    interactive_map_paths.append(html_path)
    interactive_sections.append(f"<h4>{label}</h4>{fig.to_html(include_plotlyjs='cdn', full_html=False, config=plotly_config)}")

extreme_fig, extreme_interactive_path = make_interactive_extreme_map(
    cell_summary,
    f"{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}_m0_review_interactive_extreme_mesh_cells.html",
)
interactive_map_paths.append(extreme_interactive_path)
interactive_sections.append(
    f"<h4>Extreme raw MESH cells</h4>{extreme_fig.to_html(include_plotlyjs='cdn', full_html=False, config=plotly_config)}"
)

interactive_gallery_html = f"""
<div>
  <h3>Interactive MRMS V1 M0 Review Maps</h3>
  <p>
    Pan, zoom, box-select, and hover over served cells. Color fields are review aids; they are not release
    cartography. Plotly is loaded from CDN for notebook size control.
  </p>
  {''.join(interactive_sections)}
</div>
"""
display(HTML(interactive_gallery_html))

interactive_gallery_path = REVIEW_ROOT / f"m0_review_interactive_map_gallery_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.html"
interactive_gallery_path.write_text(interactive_gallery_html)
print("wrote interactive map gallery:", interactive_gallery_path.relative_to(ROOT))

# %% [markdown]
# ## 7 - Write review metadata and optional GCS upload

# %%
review_metadata = {
    "artifact_family": "mrms_v1_m0_full_reconciliation_review",
    "status": "review_artifact_created",
    "review_run_id": REVIEW_RUN_ID,
    "reconciled_run_id": RECONCILED_RUN_ID,
    "cloud_run_batch_run_id": CLOUD_RUN_RUN_ID,
    "input_reconciled_local_root": str(RECONCILED_ROOT),
    "input_reconciled_gcs_root": RECONCILED_GCS_ROOT,
    "review_local_root": str(REVIEW_ROOT),
    "review_gcs_root": REVIEW_GCS_ROOT,
    "n_input_batches": int(metadata["n_input_batches"]),
    "n_dates": int(metadata["n_dates"]),
    "n_served_cells": int(metadata["n_served_cells"]),
    "n_output_rows": int(metadata["n_output_rows"]),
    "sidecar_checks": sidecar_checks.to_dict(orient="records"),
    "daily_summary": {
        "max_daily_severe_cell_count": int(daily_wide["observed_severe_hail"].max()),
        "median_daily_severe_cell_count": float(daily_wide["observed_severe_hail"].median()),
        "max_daily_raw_mesh_mm": float(daily_wide["daily_max_mesh_mm"].max()),
    },
    "cell_summary": {
        "cells_with_any_severe_hail_day": int((cell_summary["n_severe_hail_days"] > 0).sum()),
        "max_cell_severe_hail_days": int(cell_summary["n_severe_hail_days"].max()),
        "max_cell_raw_annualized_severe_hail_day_rate": float(cell_summary["severe_hail_day_rate_per_year_raw"].max()),
        "max_cell_mesh_mm": float(cell_summary["max_mesh_mm"].max()),
        "cells_with_extreme_mesh_ge_300mm": int(cell_summary["qa_extreme_mesh_ge_300mm"].sum()),
    },
    "extreme_mesh": {
        "record_count": int(len(extreme_records)),
        "cell_count": int(extreme_records["cell_id"].nunique()) if not extreme_records.empty else 0,
        "date_count": int(pd.to_datetime(extreme_records["date"]).dt.date.nunique()) if not extreme_records.empty else 0,
        "max_mesh_mm": None if extreme_records.empty else float(extreme_records["mesh_max_mm"].max()),
    },
    "review_recommendation": {
        "m0_row_contract_status": m0_row_contract_status,
        "raw_mesh_severity_status": severity_qa_status,
        "m1_readiness": m1_readiness,
    },
    "outputs": {
        "daily_summary_csv": str(daily_summary_path),
        "cell_summary_parquet": str(cell_summary_path),
        "cell_summary_top_csv": str(cell_summary_csv),
        "extreme_records_csv": str(extreme_records_path),
        "extreme_by_date_csv": str(extreme_by_date_path),
        "diagnostics": [str(path) for path in diagnostic_paths],
        "map_gallery_html": str(gallery_html_path),
        "interactive_map_gallery_html": str(interactive_gallery_path),
        "interactive_maps": [str(path) for path in interactive_map_paths],
        "maps": [str(path) for path in map_paths],
    },
    "allowed_use": [
        "M0 QA review",
        "input checklist before M1 build",
    ],
    "not_allowed_use": [
        "reportable EAL/PML/VaR/TVaR",
        "final M1 hazard layer",
    ],
    "caveats": [
        "Raw MRMS MESH is radar-estimated and not de-biased.",
        "Annualized rates shown here are raw observed-frequency review proxies.",
        "Max-MESH map is clipped at 150 mm for readability; tail diagnostics and extreme-record CSV carry true values.",
        "Extreme raw MESH is preserved as audit/context evidence but should not be treated as literal size without a QA rule.",
    ],
}

REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
review_metadata_json = REVIEW_ROOT / f"metadata_m0_review_{RECONCILED_RUN_ID}_{REVIEW_RUN_ID}.json"
review_metadata_json.write_text(json.dumps(review_metadata, indent=2) + "\n")
print("wrote review metadata:", review_metadata_json.relative_to(ROOT))


def is_gcs_uri(value: str) -> bool:
    return value.startswith("gs://")


def split_gcs_uri(uri: str) -> tuple[str, str]:
    rest = uri[5:]
    bucket, _, blob = rest.partition("/")
    if not bucket or not blob:
        raise ValueError(f"invalid GCS URI: {uri}")
    return bucket, blob


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
    return any(storage.Client().bucket(bucket_name).list_blobs(prefix=prefix, max_results=1))


def upload_file(local_path: Path, destination_uri: str) -> None:
    try:
        from google.cloud import storage  # type: ignore
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", str(local_path), destination_uri], check=True)
        return

    bucket_name, blob_name = split_gcs_uri(destination_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(local_path)


def upload_tree(local_root: Path, gcs_root: str) -> list[str]:
    if gcs_prefix_exists(gcs_root) and not FORCE_REVIEW_OUTPUT:
        raise FileExistsError(f"GCS review prefix already exists: {gcs_root}")

    uploaded: list[str] = []
    for path in sorted(p for p in local_root.rglob("*") if p.is_file()):
        rel = path.relative_to(local_root).as_posix()
        destination = f"{gcs_root.rstrip('/')}/{rel}"
        upload_file(path, destination)
        uploaded.append(destination)
    return uploaded


if UPLOAD_TO_GCS:
    uploaded = upload_tree(REVIEW_ROOT, REVIEW_GCS_ROOT)
    review_metadata["upload_status"] = "uploaded"
    review_metadata["uploaded_gcs_outputs"] = uploaded
else:
    review_metadata["upload_status"] = "skipped"
    review_metadata["uploaded_gcs_outputs"] = []

review_metadata_json.write_text(json.dumps(review_metadata, indent=2) + "\n")
if UPLOAD_TO_GCS:
    upload_file(review_metadata_json, f"{REVIEW_GCS_ROOT.rstrip('/')}/{review_metadata_json.name}")

display(
    pd.DataFrame(
        [
            ("review_status", review_metadata["status"]),
            ("upload_status", review_metadata["upload_status"]),
            ("review_local_root", str(REVIEW_ROOT.relative_to(ROOT))),
            ("review_gcs_root", REVIEW_GCS_ROOT),
            ("cell_summary_rows", len(cell_summary)),
            ("extreme_record_count", len(extreme_records)),
        ],
        columns=["item", "value"],
    )
)

# %% [markdown]
# ## 8 - Review conclusion
#
# M0 passes the mechanical row-contract checks:
#
# ```text
# 148 input batches
# 2,071 accepted MRMS dates
# 13,085 served cells per date
# 27,099,035 cell-day rows
# 0 duplicate cell-date rows
# 0 failed date row counts
# ```
#
# The remaining M0 issue is not a cloud-output failure; it is a raw-source severity QA issue:
# `extreme_mesh_ge_300mm`. In this run it is broad enough that raw MESH severity should get a named
# downstream QA/capping rule or sensitivity before empirical size summaries or loss metrics use it.
#
# If accepted, the next step is M1 frequency plus a severity-QA decision:
#
# ```text
# reconciled M0 root
#   -> per-cell severe hail-day frequency
#   -> empirical MESH size summaries
#   -> sparse/QA/provenance flags
# ```
