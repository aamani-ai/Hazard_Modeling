# Hazard CONUS Grid — Decisions Log

Running record of product-wide decisions for the CONUS gridded hazard-risk workstream. Hazard-specific
decisions live in each hazard subfolder.

---

## DD-G9 · Use task-indexed Cloud Run fanout for hail MRMS M0 full denominator

**Date:** 2026-06-16 · **Status:** decided for hail V1 scale-out.

**Context.** The durable GitHub Actions / Artifact Registry / Cloud Run Job path now works from
`aamani-ai/Hazard_Modeling`. A single 7-day durable-image proof succeeded, and the earlier 14-day bootstrap
proof showed a normal inventory-generated batch fits comfortably inside Cloud Run limits. The full accepted
MRMS denominator is 148 planned batch-spec rows.

**Decision.** Use one Cloud Run Job in **task-indexed mode** for the full M0 fanout:

```text
Cloud Run task index 0 -> batch_spec row 0 -> batch_0001
Cloud Run task index 1 -> batch_spec row 1 -> batch_0002
...
Cloud Run task index 147 -> batch_spec row 147 -> batch_0148
```

All tasks share one full-run `run_id`. Each task writes the existing M0 batch artifact shape under its own
`batch=YYYYMMDD_YYYYMMDD` prefix. The runner reads the batch-spec CSV from GCS and uses
`CLOUD_RUN_TASK_INDEX` to choose `date_start` and `date_end`.

**Why.** This avoids 148 manual job updates while keeping the batch contract unchanged. It also keeps the run
auditable: the batch spec is the control file, the `run_id` is the execution address, and each task writes a
normal batch that can be reconciled by the existing M0 reconciliation script.

**Guardrails.**

- keep the inventory-generated 14-day batch windows for the first full run;
- use bounded `parallelism`, not all 148 tasks at once;
- write no QA maps during full fanout;
- do not overwrite existing `run_id/batch=` prefixes;
- reconcile the full batch set before M1 consumes anything.

**Execution result.** Completed on 2026-06-16:

```text
Cloud Run run id:      20260616T220624Z_m0_full_conus_task_indexed
GitHub Actions run:    27651275076
Cloud Run execution:   hazard-conus-grid-mrms-m0-54dm7
tasks / parallelism:   148 / 8
task result:           148 succeeded, 0 failed
batch output root:     gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T220624Z_m0_full_conus_task_indexed/
```

The full run was then reconciled in streaming mode:

```text
reconciled run id:     20260616T225000Z_m0_full_conus_reconciled
reconciled root:       gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
dates:                 2,071
served cells/date:     13,085
rows:                  27,099,035
duplicate cell-dates:  0
status:                streaming_reconciliation_passed_row_contract
```

**Implementation pointer.** See
[`hail/m0_m1_scaleout_execution.md`](hail/m0_m1_scaleout_execution.md) and
[`common/gcp_execution_and_storage_conventions.md`](common/gcp_execution_and_storage_conventions.md).

---

## DD-G8 · Defer canonical asset coupling finalization until full M0/M1 cell comparisons

**Date:** 2026-06-16 · **Status:** decided for hail V1 sequencing.

**Context.** The single-site Hayhurst hail pipeline used a 50-mile collection radius because it answered a
site-specific question: what hail evidence happened near one real asset? The CONUS grid answers a different
question: what hail evidence belongs to each benchmark `cell_id`? For M0/M1, using a 50-mile radius around
every cell would blur neighboring cells and double-count spatial evidence.

**Decision.** Keep M0/M1 exact-cell:

```text
MRMS native pixels
  -> benchmark cell_id
  -> cell-day evidence
  -> per-cell frequency + observed size distribution
```

Do not finalize the M2-M4 canonical 100 MW solar coupling rule until after the full M0/M1 layer exists and
representative cells can be compared. The starting assumption is that the canonical asset is placed inside
the cell and uses that cell's hazard evidence. Any neighborhood/radius alternative must be a named M2
coupling scenario with its own fields, QA flags, and caveats.

**Why.** M0/M1 should stay a clean reusable hazard layer. Asset footprint, hit probability, and any smoothing
or neighborhood assumption belong in M2 coupling, where they can be tested without corrupting the raw hazard
evidence.

**Revisit gate.** After full M0/M1, compare at least:

```text
high-hail corridor cell
medium-hail cell
low-hail cell
Hayhurst/reference cell
sparse or weird QA cell
```

Then decide whether canonical solar M2 uses exact cell only, footprint-within-cell, neighboring cells, or a
separate radius/neighborhood scenario.

**Implementation pointer.** See
[`hail/m0_m1_hazard_layer.md`](hail/m0_m1_hazard_layer.md) and
[`output_schema.md`](output_schema.md).

---

## DD-G7 · Choose the full-run executor only after a measured M0 evidence batch

**Date:** 2026-06-16 · **Status:** decided for hail V1 scale-out.

**Context.** Cloud Run Jobs is available as an execution option, but we have not yet measured full-grid M0
daily-evidence runtime, memory, output size, or retry behavior. The current successful work proves the row
contract and source-inventory/upload contract, not the cost profile of reading MRMS and writing full-grid
daily evidence across multiple dates.

**Decision.** Do not set up the full Cloud Run path before the small M0 evidence batch. The next execution
gates are:

```text
full intended MRMS source inventory
  -> small full-grid M0 evidence batch, 7-14 accepted dates
  -> runner decision from measured facts
  -> scaled M0 evidence batches
```

Use Cloud Run Jobs if the small batch is stateless, finishes comfortably within service limits, and has simple
retry/fanout behavior. Use Cloud Batch or a VM runner if the batch is too long, too memory-heavy, or needs more
resource/checkpoint control.

**Why.** The runner must not drive the model design. The batch contract should be runner-agnostic; executor
choice should come from observed workload behavior.

**Implementation pointer.** See
[`hail/m0_m1_scaleout_execution.md`](hail/m0_m1_scaleout_execution.md).

**Implementation update.** The full intended MRMS source inventory completed in run `20260616T165806Z`. It
requested `2014-01-01` to `2026-06-15`, accepted 2,071 continuous source days from `2020-10-14` through
`2026-06-15`, recorded zero list failures, and wrote 148 planned 14-day M0 batches. The next gate is the
small full-grid M0 evidence batch.

**Implementation update.** The small full-grid M0 evidence batch completed locally in run `20260616T172929Z`
for `2024-06-01` to `2024-06-07`. It wrote 91,595 rows, produced seven daily CONUS maps, had zero duplicate
`cell_id/date` rows, and took 7.535 seconds locally with cached source files. After reauthentication, the
same batch uploaded 19 objects to the GCS dev prefix, so the small-batch remote write path is confirmed.

**Revisit trigger.** The small M0 evidence batch proves Cloud Run is a poor fit, or platform constraints
require a specific InfraSure runner.

---

## DD-G6 · Hazard CONUS grid uses `infrasure-benchmark/hazard_conus_grid` as the durable GCS root

**Date:** 2026-06-16 · **Status:** decided for active V1 work.

**Context.** The neighboring `model-gpr` repo treats GCS as the durable deep lake, keeps local data as a
development mirror, writes manifest sidecars, and guards against accidental overwrites. The benchmark-grid
repo already uses `gs://infrasure-benchmark` for canonical grid sources and delivery artifacts.

**Decision.** Use a dedicated product prefix in the existing benchmark bucket:

```text
gs://infrasure-benchmark/hazard_conus_grid/
```

Active development outputs go under:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/
```

QA-accepted product artifacts are later promoted under:

```text
gs://infrasure-benchmark/hazard_conus_grid/releases/
```

For hail MRMS-only V1, the active root is:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/
```

**Why.** This keeps hazard-grid artifacts near the benchmark grid they key against, but avoids colliding with
the existing `sources/` and `deliveries/` prefixes. The `dev/` vs `releases/` split lets us run inventories
and batch attempts without pretending every intermediate output is a product release.

**Implementation pointer.** See
[`common/storage_artifacts.md`](common/storage_artifacts.md).

**Operational note.** Local `gcloud` bucket listing works with active account `divy@aamani.ai`. The current
configured local project is `vertexai-models`; do not assume that is the final execution/billing project.
The write/read/delete probe under `hazard_conus_grid/_access_checks/` passed, and the first MRMS source
inventory proof uploaded to:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

That proof upload confirms path/write mechanics only; it is not a product release.

**Revisit trigger.** Benchmark-grid owners request a different prefix, a separate hazard bucket is created,
or serving workflows require `deliveries/` promotion semantics.

---

## DD-G5 · Hail V1 grid build is MRMS-only

**Date:** 2026-06-16 · **Status:** decided for V1.

**Context.** The selected-cell pilot proved the MRMS interface and downstream solar smoke path. MYRORSS work
has started, but it is still source qualification: public access, sparse decode, selected-cell adapter proof,
batching, retry, and partial reconciliation. It has not yet passed the promotion gates needed for M1 use:
coverage denominator, MRMS/MYRORSS comparability, exact-target interpretation, MESH bias treatment, frequency
definition, and tail treatment.

**Decision.** The first full-grid hail product is:

```text
MRMS_ONLY V1
  -> full served-CONUS daily cell evidence
  -> MRMS-only per-cell M1 hazard layer
  -> canonical solar risk layer with provisional-tail flags
```

MYRORSS is excluded from V1. NOAA/SPC reports and broad hail climatology are validation/sanity checks only.
FEMA NRI remains downstream QA only. Murillo & Homeyer-style de-biasing and EVT tail fitting are V1.5/V2
work.

**Why.** V1 should be a clean, auditable grid contract before it is a longer or more sophisticated
climatology. Adding MYRORSS now would increase apparent record length while importing unresolved source-era
and product-homogeneity risk.

**Implementation pointer.** See
[`hail/v1_mrms_only_grid_build.md`](hail/v1_mrms_only_grid_build.md).

**Implementation update.** The first MRMS-only full-grid proof has run for `2024-06-01`:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  02_mrms_v1_full_grid_one_day_proof.ipynb
```

It produced a complete one-day served-CONUS panel with 13,085 rows. The seven-day source-inventory proof and
the full intended MRMS source inventory have also run and uploaded to the GCS dev prefix. The next
implementation step is a small full-grid M0 daily-evidence batch from the accepted denominator.

**Revisit trigger.** MYRORSS passes the source-promotion gate and a documented MRMS/MYRORSS homogeneity check,
or V1 fails QA in a way that cannot be addressed from MRMS alone.

---

## DD-G4 · Hail starts with a selected-cell pilot before full CONUS

**Date:** 2026-06-15 · **Status:** decided for first implementation pass.

**Context.** Hail M1 is the hard case because no public source hands us a clean per-cell frequency
distribution plus hail-size distribution. MRMS/MYRORSS are raw gridded evidence, so we must build the M1
artifact ourselves.

**Decision.** Start with a selected-cell MRMS pilot before running full CONUS. The pilot is not a separate
product. It is a contract test for the full pipeline:

```text
MRMS daily MESH
  -> threshold >= 25.4 mm
  -> join/aggregate to benchmark cell_id
  -> daily cell evidence table
  -> initial frequency + size summaries
  -> QA against reports / known hail regimes
```

Exact pilot `cell_id` values are now pinned for the selected-cell M1 pilot in:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
```

They were selected through a documented step using the pinned benchmark grid, MRMS evidence, NOAA/NRI
report-side QA, and map / broad-role review. The selection protocol is
[`hail/pilot_cell_selection.md`](hail/pilot_cell_selection.md). Unexplained legacy delivery outputs are not an
acceptable basis for this selection.

**Why.** The expensive/fragile parts are not the final loss math; they are source interpretation, cell joins,
thresholding, sparse-cell behavior, and QA. A handful of representative cells catches those mistakes before a
full-CONUS run makes them harder to debug.

**Revisit trigger.** Completed: the selected-cell artifact drove a solar M2-M4 smoke run. The next decision is
DD-G5: expand to MRMS-only full-grid V1 before adding MYRORSS/long-record extensions.

**Superseded path note.** Earlier wording implied full CONUS and MYRORSS were adjacent next steps. DD-G5
separates them: full-grid V1 first, MYRORSS later.

---

## DD-G3 · Grid notebooks and data live under a dedicated product root

**Date:** 2026-06-15 · **Status:** decided as planning convention.

**Decision.** Use dedicated grid roots when implementation starts:

```text
Notebooks/hazard_conus_grid/
data/hazard_conus_grid/
```

**Why.** Existing notebooks are `peril -> asset` for deep asset risk. The CONUS grid is a product-level fanout
with shared benchmark grid, canonical assets, storage contracts, and validation. Keeping it separate avoids
mixing single-asset assumptions with grid assumptions.

**Revisit trigger.** If implementation proves the product can be cleanly expressed inside the existing
`Notebooks/<hazard>/` tree without confusion, revisit. Current evidence points the other way.

---

## DD-G2 · Store two durable products: hazard layer first, risk layer second

**Date:** 2026-06-15 · **Status:** decided.

**Decision.** The grid build persists two layers:

1. **M1 hazard-distribution layer:** per-cell frequency distribution, severity/size distribution,
   provenance, and QA.
2. **M2-M4 risk-metrics layer:** per-cell EAL, AEP/OEP curves, PML, VaR, TVaR, exceedance probabilities,
   dollars, `%TIV`, and QA.

**Why.** The hazard layer is reusable across assets and makes validation possible before damage/loss modeling.
The risk layer is what the platform/map consumes.

**Revisit trigger.** A storage or performance constraint proves the two-layer artifact is too expensive.

---

## DD-G1 · Canonical grid source = `benchmark-grid-dataset`

**Date:** 2026-06-15 · **Status:** decided; exact artifact path and served CONUS mask validated locally.

**Decision.** Use the ERA5 native 0.25° benchmark grid from:

```text
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/
```

The canonical join key is the integer `cell_id` from the benchmark grid spec:

```text
cell_id = lat_idx * 1440 + lon_idx
```

The validated full-grid artifact is:

```text
gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet
```

It has **17,543 cells**. The served CONUS mask is the **13,085-cell** `cell_id` set from
`gs://infrasure-benchmark/deliveries/wildfire_risk_layer_conus.parquet`, cross-checked as identical to
`gs://infrasure-benchmark/deliveries/solar_revenue_layer_conus.parquet`.

Committed mask:

```text
data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

Note: `gs://infrasure-benchmark-public/v2026_06/grid_common.parquet` has **13,011** rows and is a subset of
the 13,085 mask. It is an app-serving common table, not the canonical hazard/revenue mask.

**Why.** This keeps the hazard product aligned with the platform benchmark grid and gives a stable key that
survives future regional expansion. We should not create a second hazard-only grid.

**Important caveat.** The older `hazard_analysis/tools/benchmark/` folder is cautionary history, not a source
of truth. It uses an older string-like cell key such as `25.00_-81.00`. Do not adopt that key, its outputs,
or its assumptions in this product unless a specific migration/validation step requires it.

**Revisit trigger.** The benchmark-grid product changes its canonical key/grid, a newer delivery changes the
13,085 served mask, or the app-serving 13,011 subset becomes the intended map surface.
