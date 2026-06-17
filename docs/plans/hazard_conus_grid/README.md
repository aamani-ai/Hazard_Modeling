# Plan: Hazard CONUS Grid

> **Status: initial plan-of-record.** This is the planning home for the CONUS gridded hazard-risk product.
> The detailed reasoning still lives in [`docs/extra/discussion/conus_grid/`](../../extra/discussion/conus_grid/);
> this folder records the pieces that have graduated into a build shape.

## What this workstream is

`hazard_conus_grid` is the **breadth product** for the hazard engine: run the same M0→M4 hazard-loss method
over the 0.25° CONUS benchmark grid, using fixed canonical assets at each cell.

It is not a separate lower-quality model. It is the same engine with a different exposure input:

| Use case | Exposure | Output |
|---|---|---|
| **Deep asset risk** | real asset, true geometry, asset-specific assumptions | one asset-level loss distribution |
| **CONUS grid risk** | fixed canonical asset at every grid cell | comparable per-cell risk layers |

The grid build has two durable products:

1. **Per-cell hazard-distribution layer** from M0/M1: frequency + severity/size + provenance/QA.
2. **Per-cell risk-metrics layer** from M2–M4: EAL, AEP/OEP curves, PML, VaR, TVaR, exceedance probabilities,
   all in dollars and `% of TIV`, for canonical solar and wind.

## Why this gets its own folder

The per-asset notebooks are organized by `peril → asset` because M0/M1 are shared by peril and M2–M4 specialize
by asset. The CONUS grid keeps that same seam, but it adds cross-cutting concerns:

- one shared benchmark grid;
- one canonical exposure definition;
- one per-cell output schema;
- shared raw-grid/cache conventions;
- shared validation rules so point and grid products cannot drift.

So the CONUS grid deserves one product-level folder, with per-hazard subfolders inside it.

## Planning layout

This is the current docs shape:

```text
docs/plans/hazard_conus_grid/
  README.md                    <- this file: product overview + read order
  decisions.md                 <- DD-G*: product-wide decisions
  assumptions.md               <- G*: canonical assets, grid, reporting, MC depth
  output_schema.md             <- final per-cell risk metrics contract
  common/
    benchmark_grid.md          <- source, shape, join keys, no-data rules
    gcp_execution_and_storage_conventions.md <- Cloud Run, service accounts, run ids, GCS paths, artifact formats
    gridded_radar_source_qualification.md <- common radar-source boundary: source qualification vs grid/site adapters
    storage_artifacts.md       <- durable layer naming and versioning
    validation.md              <- grid-vs-point and external-anchor checks
  hail/
    README.md
    m0_m1_hazard_layer.md      <- raw radar -> per-cell M1 artifact
    m0_m1_scaleout_execution.md <- gated full-inventory/M0/M1 execution strategy
    pilot.md                   <- selected-cell pilot plan
    pilot_cell_selection.md    <- how selected cells are chosen without legacy shortcuts
  wildfire/
    README.md
    m0_m1_hazard_layer.md      <- FSim/WRC -> per-cell M1 artifact
```

The files are intentionally light right now. They pin the product shape and leave implementation details to
the first grid notebooks.

## Reasoning Sources and Principles

The plan files are the build-facing record. The discussion docs remain the deeper reasoning source, especially:

- [`docs/extra/discussion/conus_grid/01_ideal_architecture_compute_and_grid.md`](../../extra/discussion/conus_grid/01_ideal_architecture_compute_and_grid.md)
- [`docs/extra/discussion/conus_grid/02_per_cell_output_schema.md`](../../extra/discussion/conus_grid/02_per_cell_output_schema.md)
- [`docs/extra/discussion/conus_grid/03_exposure_granularity.md`](../../extra/discussion/conus_grid/03_exposure_granularity.md)
- [`docs/extra/discussion/conus_grid/hail/`](../../extra/discussion/conus_grid/hail/)

Before related implementation work, check the repo principles and apply them directly:

| Principle | What it means for `hazard_conus_grid` |
|---|---|
| [`Standard interface, not standard physics`](../../principles/hazard_asset_specificity.md) | Hail, wildfire, and wind can have different M1 physics, but they must emit the same hazard-distribution interface. |
| [`Modular from day one`](../../principles/modularity_and_scaling.md) | Build the common grid/artifact contracts once; add hazards by implementing the interface, not by editing a shared monolith. |
| [`Basics spot-on`](../../principles/basics_spot_on.md) | AEP/OEP, VaR/PML, `%TIV`, no-data vs zero, and stochastic loss aggregation must be validated before map outputs are trusted. |
| [`Exploratory data notebooks`](../../principles/notebook_work/exploratory_data_notebooks.md) | MRMS/MYRORSS/WRC notebooks must explain source meaning, units, grid conventions, fill values, sampling windows, and what is carried forward. |

This is why the first hail step was a selected-cell MRMS pilot: it verifies the source interpretation and
interface before full-CONUS scale. Source qualification that can serve both site-specific and grid workflows
belongs in the common peril notebooks; the grid notebooks hold adapters, selected-cell proofs, and grid
artifacts.

## Proposed notebook layout

When we start exploratory notebooks, keep grid-product notebooks under a dedicated grid folder, but keep
shared source qualification under the common peril notebooks:

```text
Notebooks/hail/
  m0_input_data/
    03_myrorss_reanalysis_source_qualification/ <- shared MYRORSS source qualification

Notebooks/hazard_conus_grid/
  common/
    01_benchmark_grid/         <- load/inspect 0.25° grid, no-data flags, cell areas
    02_canonical_assets/       <- solar/wind canonical exposure definitions
  hail/
    m0_input_data/             <- grid adapters / selected-cell provenance only
      01_mrms_daily_mesh/      <- selected-cell proof + MRMS-only V1 full-grid proof
      02_myrorss_reanalysis/   <- redirect to shared MYRORSS source qualification
      03_storm_events_anchor/  <- report-side validation/calibration
    m1_hazard_layer/
      01_selected_cell_pilot/  <- V0 pilot M1 artifact
      02_full_conus_build/     <- MRMS-only V1, after M0 inventory/evidence batches
    solar/
      m2_m4_risk_metrics/
    wind/
      m2_m4_risk_metrics/
  wildfire/
    m0_input_data/
    m1_hazard_layer/
    solar/
    wind/
```

Reasoning:

- `common/` owns grid and canonical exposure work shared by every hazard.
- `hail/`, `wildfire/`, and later `wind/` own their hazard-specific M0/M1 layer.
- asset folders remain downstream because coupling/damage/loss specialize by asset.
- exploratory data notebooks should follow the existing style from
  [`Notebooks/hail/m0_input_data/`](../../../Notebooks/hail/m0_input_data/): meet the source, explain the
  variables, show plots/tables, then decide how to use it.
- grid notebooks consume or adapt that source evidence; they should not become the only place where a
  reusable raw data source is understood.

## Proposed data/artifact layout

Do not commit heavy rasters/parquets. Keep raw cache and large build products gitignored, but keep manifests,
schemas, and small summaries.

Durable GCS root:

```text
gs://infrasure-benchmark/hazard_conus_grid/
```

Active development runs use `dev/`; QA-accepted product artifacts later promote to `releases/`. See
[`common/storage_artifacts.md`](common/storage_artifacts.md).

```text
data/hazard_conus_grid/
  common/
    benchmark_grid/            <- local copy or manifest for the 0.25° grid
  hail/
    raw/                       <- MRMS/MYRORSS cache, gitignored
    m0_daily_cell_evidence/    <- large parquet, gitignored
    m1_hazard_layer/           <- large parquet, gitignored; manifest kept
    m2_m4_risk_metrics/        <- large parquet, gitignored; summaries kept
  wildfire/
    raw/
    m1_hazard_layer/
    m2_m4_risk_metrics/
```

Local `data/` is the development mirror. GCS is the durable lake once an artifact is larger than a small
manifest/summary or needs to be consumed by another workflow.

Operational cloud execution conventions live in
[`common/gcp_execution_and_storage_conventions.md`](common/gcp_execution_and_storage_conventions.md). In short:

- row-level layers are parquet;
- nested authoritative metadata is JSON;
- CSV is only for flat summaries/manifests meant for human QA;
- Cloud Run work uses Jobs, not Services;
- `project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com` is the current runtime service
  account;
- the full hail M0 denominator is not running until the full-run gate is explicitly cleared.

## First build target: hail MRMS-only V1

Start with hail because it is the hard case and already has the deepest research.

The selected-cell MRMS pilot and solar smoke test have already served their purpose: they proved source
interpretation, cell joins, the tiny M1 interface, and the downstream M2-M4 metric interface. They are V0
contract evidence, not the main product path.

The active build is now:

```text
MRMS daily MESH
  -> served-CONUS daily cell evidence
  -> MRMS-only per-cell M1 hazard layer
  -> canonical solar risk layer with provisional-tail flags
```

Current status: the MRMS-only full-grid one-day proof has run for `2024-06-01`, the seven-day
source-inventory/GCS upload proof has run for `2024-06-01` to `2024-06-07`, the full intended MRMS source
inventory has run, and the first seven-day full-grid M0 evidence batch has run locally.

```text
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

The full inventory requested `2014-01-01` to `2026-06-15` and accepted 2,071 continuous MRMS source days from
`2020-10-14` through `2026-06-15`; earlier requested dates are explicit no-source rows, not zero-hail days.

The first M0 batch wrote 91,595 rows (`7 x 13,085`), produced 7 CONUS QA maps, and uploaded 19 objects to:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

Current cloud status: the first full MRMS-only M0 denominator has completed and reconciled. The task-indexed
Cloud Run fanout used `run_id=20260616T220624Z_m0_full_conus_task_indexed`; the accepted reconciled M0 root is:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
```

It contains 2,071 accepted MRMS dates, 13,085 served CONUS cells per date, and 27,099,035 cell-day rows with
zero duplicate `cell_id/date` rows and zero date row-count failures. The M0 review run
`20260616T232500Z_m0_review` confirmed the row contract, but found repeated extreme raw MESH values
(`613` cell-days, `585` cells, `38` dates, max `1,437.4 mm`). Next build target: define the V1
extreme-MESH severity rule, then build M1 frequency from the reconciled root. Empirical size summaries must
carry the raw/capped/filter decision explicitly. MYRORSS, Murillo & Homeyer de-biasing, EVT tail, and more
complex sparse-cell/frequency modeling remain V1.5/V2 after the MRMS-only grid contract is clean.

## Cross-read/source map

These are the useful places to read before implementation. Treat this as a map of canonical sources,
validated implementation references, cautionary historical context, and active reasoning.

| Area | Status | Pointer | How to use it |
|---|---|---|---|
| 0.25° benchmark grid source | **canonical source** | `/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/` | Use its ERA5 grid spec, stable integer `cell_id`, and GCS manifest as the starting point for the grid artifact. |
| Benchmark grid spec | **canonical source** | `/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/grid/GRID_SPEC.md` | Defines `cell_id = lat_idx * 1440 + lon_idx`, `lat_center`, `lon_center`, WGS84 geometry, and the NetCDF/TIGER build process. |
| Benchmark storage/versioning | **canonical source** | `/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/data/versions.yaml` and `/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/config/storage.yaml` | Shows the `infrasure-benchmark` GCS bucket and release pattern. Validated full grid is under `sources/grid/`. |
| Older ERA5 benchmark machinery | cautionary historical context | [`hazard_analysis/tools/benchmark/`](../../../hazard_analysis/tools/benchmark/) | Use only to understand old assumptions and migration issues. Do **not** copy keys, outputs, methods, or data contracts without independent validation. |
| Legacy wildfire repo | cautionary historical context | [`_legacy_wildfire/`](../../../_legacy_wildfire/) | Use only to understand past choices and source names. It is not a source of truth for CONUS grid methods, outputs, or assumptions. |
| Existing CONUS grid discussion | active reasoning | [`docs/extra/discussion/conus_grid/`](../../extra/discussion/conus_grid/) | Current design reasoning before graduation into this plan folder. |
| Hail grid research and flow | active reasoning | [`docs/extra/discussion/conus_grid/hail/`](../../extra/discussion/conus_grid/hail/) | Hail M1 sourcing, MRMS/MYRORSS flow, pilot logic, and open hail decisions. |
| Existing hail MRMS notebooks | implementation reference | [`Notebooks/hail/m0_input_data/`](../../../Notebooks/hail/m0_input_data/) | Style and source-handling reference for MRMS; the grid version should be its own notebook path. |
| Common gridded-radar source qualification | active boundary note | [`docs/plans/hazard_conus_grid/common/gridded_radar_source_qualification.md`](common/gridded_radar_source_qualification.md) | Defines what is common source qualification versus grid/site-specific extraction before GCP scale-out. |
| Existing wildfire source notebooks | validated implementation reference | [`Notebooks/wildfire/m0_input_data/`](../../../Notebooks/wildfire/m0_input_data/) | WRC/FSim source handling from this rebuild; adapt to per-cell grid artifact instead of real asset footprint. |
| Single-asset hail plan | plan dependency | [`docs/plans/hail/`](../hail/) | Reuse method decisions where they generalize; avoid copying single-site assumptions blindly. |
| Wildfire completed M0–M4 plan | plan dependency | [`docs/plans/wildfire/`](../wildfire/) | Reuse the FSim/WRC M1 logic and asset-loss chain, with grid exposure replacing real-asset geometry. |
| Wind route-zero | later dependency | [`docs/plans/wind/`](../wind/) | Needed when the grid adds wind, especially sparse turbine-density exposure. |
| Damage curves | model dependency | [`infrasure-damage-curves/`](../../../infrasure-damage-curves/) | Source for M3 fragility/damage functions by peril × asset/component. |
| Learning on pre-integrated vs raw catalog | method principle | [`docs/learning_logs/09_pre_integrated_vs_extracted_catalog.md`](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) | Explains why wildfire M1 is easier than hail M1. |
| Learning on collection-region cancellation | method principle | [`docs/learning_logs/06_collection_region_size_cancels.md`](../../learning_logs/06_collection_region_size_cancels.md) | Important for hail frequency scaling and canonical exposure size. |
| Learning on MC effective sample size | method principle | [`docs/learning_logs/10_monte_carlo_effective_sample_size.md`](../../learning_logs/10_monte_carlo_effective_sample_size.md) | Sets expectations for grid-scale simulation depth and tail metrics. |
| renewablesinfo grid-region context | platform context | [`renewablesinfo_org`](../../../renewablesinfo_org) | Useful for platform labels/region semantics, not the hazard-grid artifact itself. |

## Open decisions before code

1. **Mask surface:** decide whether first map delivery uses the full 13,085 hazard/revenue mask or the
   narrower 13,011 public app-serving `grid_common` subset.
2. **Hail gating decisions:** resolve `DEC-H1`–`DEC-H5` from
   [`hail/01_m1_sourcing_triage.md`](../../extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md) for
   V1.5/V2. For V1, [`decisions.md`](decisions.md) pins MRMS-only.

## Near-term read order

1. [`common/benchmark_grid.md`](common/benchmark_grid.md)
2. [`common/gridded_radar_source_qualification.md`](common/gridded_radar_source_qualification.md)
3. [`assumptions.md`](assumptions.md)
4. [`decisions.md`](decisions.md)
5. [`output_schema.md`](output_schema.md)
6. [`hail/pilot.md`](hail/pilot.md)
7. [`hail/pilot_cell_selection.md`](hail/pilot_cell_selection.md)
8. [`hail/m0_m1_scaleout_execution.md`](hail/m0_m1_scaleout_execution.md)
9. [`hail/m0_m1_hazard_layer.md`](hail/m0_m1_hazard_layer.md)
10. [`docs/extra/discussion/conus_grid/01_ideal_architecture_compute_and_grid.md`](../../extra/discussion/conus_grid/01_ideal_architecture_compute_and_grid.md)
11. [`docs/principles/README.md`](../../principles/README.md)
12. [`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../principles/notebook_work/exploratory_data_notebooks.md)
13. [`Notebooks/hazard_conus_grid/common/01_benchmark_grid/`](../../../Notebooks/hazard_conus_grid/common/01_benchmark_grid/)
14. [`Notebooks/hail/m0_input_data/02_mrms_aws.py`](../../../Notebooks/hail/m0_input_data/02_mrms_aws.py)
