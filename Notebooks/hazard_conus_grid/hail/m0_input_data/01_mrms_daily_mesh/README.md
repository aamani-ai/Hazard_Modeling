# 01 — MRMS Daily MESH to Benchmark Cells

Goal: meet MRMS daily MESH in the grid context, prove native-pixel-to-benchmark-cell aggregation, and
produce evidence-backed pilot-cell candidates.

This is the grid-product counterpart to:
[`Notebooks/hail/m0_input_data/02_mrms_aws.py`](../../../../../Notebooks/hail/m0_input_data/02_mrms_aws.py).

Plan reference:
[`docs/plans/hazard_conus_grid/hail/pilot.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot.md).
Selection protocol:
[`docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md).

Notebook record:

- `01_mrms_daily_mesh.ipynb` — notebook for the bounded MRMS candidate scan; artifacts are materialized
  under `data/hazard_conus_grid/hail/`.
- `01_mrms_daily_mesh.py` — paired jupytext source.
- `02_mrms_v1_full_grid_one_day_proof.ipynb` — executed one-day proof across the served CONUS mask before
  any full-record/GCP run.
- `02_mrms_v1_full_grid_one_day_proof.py` — paired jupytext source.
- `03_mrms_v1_source_inventory.ipynb` — executed seven-day MRMS source-inventory proof and full intended
  MRMS source inventory with local artifacts and GCS dev upload.
- `03_mrms_v1_source_inventory.py` — paired jupytext source.
- `04_mrms_v1_m0_daily_evidence_batch.ipynb` — executed seven-day full-grid M0 daily-evidence batch with
  embedded CONUS map gallery and local artifacts.
- `04_mrms_v1_m0_daily_evidence_batch.py` — paired jupytext source.
- `05_mrms_v1_full_m0_review.ipynb` — full reconciled M0 cloud-output review: row-contract sidecars,
  per-cell severe-day summaries, static and interactive CONUS QA map galleries, and extreme-MESH record check.
- `05_mrms_v1_full_m0_review.py` — paired jupytext source.

## Prerequisites

1. Benchmark grid artifact path pinned:
   `gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet`.
2. Full grid locally validated: 17,543 rows, unique `cell_id`, EPSG:4326 geometry.
3. Served CONUS mask/crosswalk pinned: 17,543 full US cells -> 13,085 CONUS rows.
4. Pilot-cell selection is documented from canonical inputs following `pilot_cell_selection.md`. This can be
   the first section of the notebook: choose high, medium, low, and Hayhurst/reference cells using the pinned
   grid, MRMS evidence, and hail climatology/research anchors.

## First Notebook Scope

The first notebook is MRMS-only and candidate-selection focused:

```text
MRMS daily MESH
  -> threshold >= 25.4 mm
  -> aggregate native ~1 km pixels to benchmark 0.25° cell_id
  -> daily evidence rows by cell for a bounded window
  -> reviewable candidate manifest for high / medium / low / Hayhurst cells
```

The candidate manifest is not the final selected-cell lock. It remains pending report-side / climatology QA.
The daily evidence parquet is a sparse positive-evidence table; the selected-cell M1 pilot must expand it to
a complete candidate-cell x date panel before fitting frequency.

## What A Grid M0 Row Means

The single-site Hayhurst run used a 50-mile collection region around one real asset. The CONUS grid M0 layer
does not do that. It assigns native MRMS pixels to their matching 0.25 degree benchmark `cell_id` and writes
one row per served cell per accepted date.

Each row means:

```text
On this date, for this grid cell:
  did MRMS cover it?
  did it have no hail, sub-severe hail, or severe hail?
  how many native MRMS pixels were severe?
  what was the max / distribution of MESH size in that cell?
  which source file did this come from?
```

Later M2-M4 canonical solar/wind runs will place a fixed canonical asset inside each cell and use this
per-cell hazard evidence. They should not silently switch back to a 50-mile collection radius.

## V1 Full-Grid Proof Scope

The second MRMS notebook is full-grid but tiny in time:

```text
one accepted MRMS daily MESH file
  -> all served CONUS cell_ids
  -> coverage/no-data/no-hail/sub-severe/severe status
  -> daily evidence row contract
  -> manifest and QA summary
```

This proves the grid-wide aggregation and output contract. It is not the full MRMS record and should not
produce annual frequencies.

Executed proof:

```text
date: 2024-06-01
served cells: 13,085
observed_no_hail: 10,802
observed_sub_severe_hail: 1,991
observed_severe_hail: 292
```

Outputs:

```text
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/
  mrms_v1_one_day_full_grid_daily_panel_20240601_v2026_06_16.parquet
  mrms_v1_one_day_status_summary_20240601_v2026_06_16.csv
  mrms_v1_one_day_top_cells_20240601_v2026_06_16.csv
  mrms_v1_one_day_metadata_20240601_v2026_06_16.json
data/hazard_conus_grid/hail/qa/
  mrms_v1_one_day_status_map_20240601_v2026_06_16.png
```

## V1 Source Inventory Proof

The third MRMS notebook proves and then materializes the source-denominator and batch-contract shape:

```text
NOAA MRMS public listing
  -> one row per requested date
  -> full listed-source-file manifest
  -> accepted latest daily tile per date
  -> initial batch spec for full-grid M0 evidence
  -> local mirror + GCS dev upload
```

Executed proof:

```text
window: 2024-06-01 to 2024-06-07
run_id: 20260616T154907Z
requested dates: 7
accepted source dates: 7
listed source files: 336
selected tile convention: latest listed tile per date, 23:30 UTC for this proof window
```

Local outputs:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

GCS outputs:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

This is not the final MRMS denominator. It proves the inventory and upload contract before scanning the full
intended V1 record window.

## V1 Source Inventory Full Run

The same notebook has also been executed over the intended V1 source-inventory request window:

```text
window requested: 2014-01-01 to 2026-06-15
run_id: 20260616T165806Z
requested dates: 4,549
accepted source dates: 2,071
no-source dates: 2,478
list-failed dates: 0
first accepted source date: 2020-10-14
last accepted source date: 2026-06-15
accepted-date gaps after first accepted: 0
listed source files: 99,313
planned 14-day M0 batches: 148
```

Local outputs:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

GCS outputs:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

Interpretation: the requested window includes earlier dates with no visible public files for this MRMS daily
MESH product. The V1 denominator is the `accepted_for_v1 = true` set, continuous from `2020-10-14` through
`2026-06-15`. These rows define source availability only; they are not hail/no-hail cell evidence.

## V1 M0 Daily Evidence Batch

The fourth MRMS notebook has been executed as the first multi-day full-grid M0 evidence batch:

```text
window: 2024-06-01 to 2024-06-07
run_id: 20260616T172929Z
accepted source dates: 7
served cells: 13,085
output rows: 91,595
duplicate cell/date rows: 0
observed_no_hail rows: 69,011
observed_sub_severe_hail rows: 21,134
observed_severe_hail rows: 1,450
daily QA maps: 7
local elapsed time: 7.535 seconds
combined panel parquet: 0.512 MB
```

Local outputs:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

This run was executed in-place, so the notebook contains visible result tables and a CONUS map gallery. GCS
upload is complete with 19 objects written to:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

Next: choose the scaled runner and remote execution plan.

## V1 Full M0 Review

The fifth MRMS notebook reviews the first full task-indexed Cloud Run M0 output after reconciliation:

```text
raw Cloud Run batches:
  run_id=20260616T220624Z_m0_full_conus_task_indexed

reconciled M0:
  run_id=20260616T225000Z_m0_full_conus_reconciled
```

It checks:

- sidecar row contracts;
- daily severe-cell count and daily max raw MESH;
- per-cell severe hail-day count;
- raw annualized severe hail-day proxy;
- max raw MESH by cell;
- observed native-pixel coverage fraction;
- records causing `extreme_mesh_ge_300mm`.

The notebook includes inline static maps and Plotly pan/zoom/hover maps. Both are also written as review
artifacts so the notebook is the primary review surface and GCS remains the durable artifact store.

This notebook creates review artifacts under:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_review/
```

It does not build M1. If accepted, M1 starts from the reconciled M0 root, not from individual Cloud Run batch
prefixes.

Current review result: the M0 row contract passed, but the raw MESH severity field has repeated
`mesh_max_mm >= 300` records. Treat this as a raw-source severity QA issue before using empirical size
summaries or loss metrics; the severe-day frequency spine can proceed after review.

## Required Interpretation

Per the exploratory notebook principle, document:

- source product and AWS path pattern;
- record/window selected and what is excluded;
- grid/CRS/lon convention;
- units: MESH in mm;
- fill/no-hail/no-data behavior;
- threshold decision: `>= 25.4 mm`;
- native-pixel-to-benchmark-cell aggregation method;
- candidate-cell selection method and why each cell was chosen;
- QA plots/tables and written takeaway for each.

## Carried-Forward Evidence Columns

Minimum expected daily evidence fields:

- `hazard`;
- `cell_id`;
- `date`;
- `source_product`;
- `source_timestamp`;
- `n_native_pixels_observed`;
- `n_native_pixels_severe`;
- `severe_area_km2` or equivalent;
- `mesh_max_mm`;
- `mesh_p50_mm`, `mesh_p90_mm`, `mesh_p95_mm`, where meaningful;
- `hail_day_flag`;
- QA flags.

## What MRMS Grid M0 Asks

```text
MRMS grid M0 asks:
  for each accepted date:
    which MRMS files exist?
    which benchmark cells are covered?
    how many native pixels map to each cell?
    did the cell have severe MESH >= 25.4 mm?
    what max and summary MESH values are carried?
    what no-data or source-quality flags are needed?
```

It does not ask:

```text
  what is the final cell climatology?
  what solar loss does the cell imply?
  what should the deep-tail severity distribution be?
```

Those are M1 and downstream risk-layer questions.
