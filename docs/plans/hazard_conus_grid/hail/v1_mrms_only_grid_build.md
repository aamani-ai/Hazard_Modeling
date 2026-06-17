# Hail V1 Grid Build - MRMS Only

Status: active plan-of-record for the first full-grid hail build. The one-day full-grid proof, seven-day
source-inventory/GCS upload proof, full intended MRMS source inventory, first local seven-day full-grid M0
daily-evidence batch, Cloud Run seven-day M0 proof, Cloud Run 14-day M0 proof, and first two-batch
reconciliation proof have run. The full accepted source-date denominator has now completed through
task-indexed Cloud Run fanout and streaming reconciliation under
`run_id=20260616T225000Z_m0_full_conus_reconciled`.

## Decision

Hail V1 uses **MRMS daily MESH only** for the gridded hazard evidence layer.

MYRORSS is excluded from V1. It remains common source qualification and can enter a later V1.5/V2 only after
the promotion gates in [`../common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md)
are answered.

## V1 Purpose

V1 is a comparable CONUS screening layer:

```text
MRMS daily MESH
  -> 0.25 degree benchmark cell daily evidence
  -> MRMS-only per-cell frequency + observed size summaries
  -> canonical solar risk metrics with provisional-tail flags
```

V1 is not final insured-loss climatology. It should be honest, reproducible, and internally consistent before
we add longer records, MESH de-biasing, or EVT tails.

## Source Roles In V1

| Source | V1 role | V1 non-role |
|---|---|---|
| MRMS daily MESH | Sole gridded hazard evidence source for frequency and observed conditional size. | Not assumed to be unbiased true hail size. |
| NOAA Storm Events / SPC | Report-side validation and date/context checks. | Not raw grid truth and not exact-cell frequency. |
| Murillo & Homeyer / hail climatology | Broad spatial sanity check: corridor shape, relative high/low geography, obvious map artifacts. | Not a cell-by-cell calibration input in V1. |
| FEMA NRI | Downstream coarse sanity check after risk metrics. | Not M1, not size distribution, not direct loss input. |
| MYRORSS | Excluded from V1; source qualification only. | Not a V1 frequency/size input. |
| Das & Allen / EVT tail | Later tail-method reference. | Not required for V1 observed-body grid. |

## V1 Hazard Definition

| Item | V1 definition |
|---|---|
| Target | Served CONUS benchmark `cell_id` set, currently 13,085 cells. |
| Event unit | Severe-hail cell-day. |
| Threshold | `mesh_max_mm >= 25.4`. |
| Frequency | Annual severe-hail-day rate from observed MRMS days per cell. |
| Frequency distribution | Poisson default for V1; compute annual-count dispersion diagnostics where the record supports it, but do not overfit sparse cells. |
| Severity / size | Empirical observed MRMS MESH size summaries conditional on severe cell-days. |
| Tail | Provisional/observed-only; deep-tail metrics must carry a tail warning until EVT/fitted severity lands. |
| No-data vs zero | Separate source/coverage no-data from observed no-hail and observed sub-severe hail. |

## V1 Artifacts

Large artifacts should be parquet/partitioned and usually gitignored. Small manifests, schemas, and QA
summaries should be kept.

```text
data/hazard_conus_grid/hail/
  m0_mrms_daily_cell_evidence_v1/          <- large partitioned parquet
  m0_mrms_daily_cell_evidence_v1_manifest.json
  m1_mrms_only_hazard_layer_v1.parquet     <- large, one row per cell
  m1_mrms_only_hazard_layer_v1_summary.csv
  m1_mrms_only_hazard_layer_v1_metadata.json
  qa/
    mrms_v1_spatial_sanity_summary.csv
    mrms_v1_report_side_validation_summary.csv
```

Final naming can use the project date/version suffix, but every artifact must carry:

- source product and source window;
- benchmark grid version;
- served mask version;
- threshold;
- aggregation rule;
- coverage/no-data policy;
- allowed use and not-allowed use.

## Build Steps

### 0. Freeze V1 Contract

Before scale:

- confirm the served CONUS mask to use: 13,085-cell hazard/revenue mask unless the user explicitly chooses
  the smaller app-serving subset;
- confirm the MRMS product name and daily field used;
- define the exact source inventory window from actual accessible MRMS files, not assumed dates;
- define output roots for local and later GCS artifacts.

### 1. Local Full-Grid Proof

Run a tiny local proof before GCP:

```text
one MRMS day
  -> all served CONUS cells
  -> daily evidence row count / coverage status
  -> top-cell and map QA
```

This proves the full-grid aggregation logic without pretending we have the full record.

Status: **done for `2024-06-01`** in:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  02_mrms_v1_full_grid_one_day_proof.ipynb
```

The proof wrote one row for each of the 13,085 served CONUS cells:

| Coverage status | Cells |
|---|---:|
| `observed_no_hail` | 10,802 |
| `observed_sub_severe_hail` | 1,991 |
| `observed_severe_hail` | 292 |

The source tile had 14,773 native severe pixels. The served CONUS mask captured 12,529 of them; the rest were
outside the served mask, which is expected for a CONUS-serving subset.

### 2. MRMS Source Inventory

Build an inventory of accessible MRMS daily files:

- date;
- source path;
- product/version;
- file size;
- read status;
- cache path or GCS source URI;
- checksum if cheap enough;
- skip/failure reason.

This inventory defines the observed source-date denominator for V1. It is not M0 daily cell evidence: it
lists source files and accepted daily tiles, but it does not read GRIB contents or aggregate pixels to
benchmark cells.

Status: **done** in:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  03_mrms_v1_source_inventory.ipynb
```

Proof run:

| Item | Value |
|---|---:|
| `run_id` | `20260616T154907Z` |
| requested source dates | 7 |
| accepted source dates | 7 |
| listed source files | 336 |
| source files per day | 48 |

The proof wrote local artifacts and uploaded the same small inventory artifacts to GCS:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

This is not the final source denominator. It proves listing, accepted-tile selection, batch-spec output, and
GCS dev-prefix upload.

Full V1 source-denominator run:

| Item | Value |
|---|---:|
| `run_id` | `20260616T165806Z` |
| requested source window | `2014-01-01` to `2026-06-15` |
| requested source dates | 4,549 |
| accepted source dates | 2,071 |
| no-source dates | 2,478 |
| list-failed dates | 0 |
| first accepted source date | `2020-10-14` |
| last accepted source date | `2026-06-15` |
| missing accepted dates after first accepted | 0 |
| listed source files | 99,313 |
| planned 14-day M0 batches | 148 |

Full-run local and GCS artifacts:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

The requested window deliberately started before the currently visible public files for this MRMS product.
`accepted_for_v1 = true` defines the usable denominator for V1. The accepted denominator is continuous from
`2020-10-14` through `2026-06-15`.

Planned GCS output root:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/
```

Local development mirror:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/
```

### 3. Full-Grid M0 Daily Evidence

For each accepted MRMS date:

```text
read daily MESH
  -> normalize lon/lat/grid conventions
  -> aggregate native pixels to benchmark cell_id
  -> materialize coverage/no-data/severe flags
  -> write partitioned daily cell evidence
```

The output must distinguish:

- source day missing;
- source read failed;
- observed no hail;
- observed sub-severe hail;
- observed severe hail.

Planned GCS output root:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
```

### 4. M1 MRMS-Only Hazard Layer

From M0 daily evidence:

- compute observed years / observed days per cell;
- compute severe-hail-day count;
- compute `lambda_cell`;
- compute empirical conditional size summaries;
- assign `freq_dist = poisson_v1` unless diagnostics justify only a flag, not a more complex model;
- assign QA flags for sparse cells, short record, no-data, and provisional tail.

### 5. Validation / QA

Validation checks patterns, not hidden calibration:

- NOAA/SPC: report-side date/context and obvious contradiction checks;
- Murillo & Homeyer / climatology: broad hail-corridor shape and relative high/low geography;
- NRI: downstream sanity after loss metrics only;
- Hayhurst bridge: confirm no interface drift against the deep hail x solar reference.

### 6. Canonical Solar Risk Layer

Run the canonical solar M2-M4 layer from the MRMS-only M1 artifact.

Metrics can be emitted, but the metadata must say:

```text
source_set = MRMS_ONLY
tail_status = provisional_observed_only
not_allowed_use = final insured-loss pricing or final deep-tail claims
```

## What Is Deferred To V1.5 / V2

| Deferred item | Why deferred |
|---|---|
| MYRORSS record extension | Needs source promotion gates and MRMS/MYRORSS homogeneity checks. |
| MESH de-biasing | Needs method decision and validation against hail climatology/reports. |
| EVT / fitted severity tail | Needed before high-return-period metrics become final. |
| NegBin / shrinkage model as default | Needs enough annual observations and sparse-cell policy. |
| Site-specific source adapter | Useful, but separate from grid V1. |

## GCP / GCS Scale-Out State

The local proof is done and `gcloud` bucket listing works. Current known choices:

| Item | Current choice / status |
|---|---|
| Durable bucket | `gs://infrasure-benchmark` |
| Product prefix | `hazard_conus_grid/` |
| Active V1 dev root | `gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/` |
| Source strategy for V1 | Read NOAA public MRMS directly; write derived inventory/evidence outputs to InfraSure GCS. Do not mirror raw MRMS unless later needed. |
| Local active account | `divy@aamani.ai` from `gcloud auth list` |
| Local configured project | `vertexai-models`; this is not yet the selected execution/billing project. |
| Bucket list access | Verified for `gs://infrasure-benchmark/` and `gs://infrasure-benchmark/sources/grid/`. |
| Product prefix existence | Created by the source-inventory proof upload. |
| GCS write/delete probe | Passed under `hazard_conus_grid/_access_checks/`. |
| First dev upload | Source-inventory proof run `20260616T154907Z` uploaded 7 small artifacts. |
| Full source-denominator upload | Run `20260616T165806Z` uploaded 7 full-window inventory artifacts. |
| Small M0 evidence batch | Run `20260616T172929Z`, batch `20240601_20240607`, wrote 91,595 rows and 7 QA maps; uploaded 19 GCS objects. |
| Cloud Run M0 evidence proof | Run `20260616T205852Z_cloudrun_bootstrap_7d`, batch `20240601_20240607`, wrote 91,595 rows; matched local proof counts. |
| Cloud Run 14-day proof | Run `20260616T211247Z_m0_batch0001_14d_cloud_proof`, batch `20201014_20201027`, wrote 183,190 rows. |
| M0 reconciliation proof | Run `20260616T211844Z_m0_reconcile_2batch_proof`, reconciled 2 batch prefixes, 21 dates, 274,785 rows, duplicate `cell_id/date` rows = 0. |
| Durable image / Cloud Run Job proof | GitHub Actions run `27649989510` deployed `hazard-conus-grid-mrms-m0`; execution `hazard-conus-grid-mrms-m0-lcqqg` wrote 91,595 rows for `20240601_20240607`. |
| Task-indexed fanout proof | GitHub Actions run `27650904912`; execution `hazard-conus-grid-mrms-m0-bn9lk`; task count 2; wrote 366,380 rows across two adjacent 14-day batches. |
| Full task-indexed M0 run | GitHub Actions run `27651275076`; execution `hazard-conus-grid-mrms-m0-54dm7`; task count 148, parallelism 8; all tasks succeeded. |
| Full M0 reconciliation | Run `20260616T225000Z_m0_full_conus_reconciled`; 148 input batches, 2,071 dates, 27,099,035 rows, duplicate `cell_id/date` rows = 0, row-count failures = 0. |
| Full M0 review | Run `20260616T232500Z_m0_review`; row contract passed; 613 records / 585 cells / 38 dates have `mesh_max_mm >= 300`, so raw MESH severity needs a named QA filter or sensitivity before empirical size/loss use. |

Current main output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/
  run_id=20260616T225000Z_m0_full_conus_reconciled/
```

This is the first full-grid M0 layer. It is partitioned by date, with JSON metadata plus flat CSV sidecars
for batch manifest, date coverage, and status summary. Individual Cloud Run batch outputs are audit/debug
material; M1 should consume the reconciled root.

Current review output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_review/
  run_id=20260616T232500Z_m0_review/
```

Review result:

- M0 row contract: **passed**;
- dates: 2,071;
- rows: 27,099,035;
- cells with any severe hail day: 12,111;
- max severe hail days in one cell: 255;
- raw annualized severe-day proxy max: 44.97 days/year;
- extreme raw MESH records: 613 cell-days, 585 cells, 38 dates;
- max raw MESH: 1,437.4 mm.

Interpretation: the GCP output/reconciliation is mechanically usable. The raw severity values are not ready
to feed empirical size summaries or losses without a named extreme-MESH QA/capping rule. M1 frequency can
proceed from severe-day flags after review; M1 size summaries need the QA decision.

See [`../common/storage_artifacts.md`](../common/storage_artifacts.md) for the full path contract and
[`../common/gcp_execution_and_storage_conventions.md`](../common/gcp_execution_and_storage_conventions.md)
for Cloud Run, run-id, GCS, and metadata conventions.

## Immediate Implementation Step

The next implementation step is **not** more selected-cell or MYRORSS work, and the local and Cloud Run small
M0 evidence proofs are now complete:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T172929Z/batch=20240601_20240607/
```

Measured result:

| Item | Value |
|---|---:|
| dates | 7 |
| output rows | 91,595 |
| duplicate `cell_id/date` rows | 0 |
| severe cell-days | 1,450 |
| sub-severe cell-days | 21,134 |
| no-hail cell-days | 69,011 |
| QA maps | 7 |
| local elapsed time | 7.535 seconds |
| combined parquet size | 0.512 MB |

GCS path:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

The immediate operational task is no longer a permissions or fanout fix. Cloud Run Jobs, GCS writes, the
durable GitHub Actions image path, task indexing, and full-run reconciliation are proven.

Next:

1. Define the V1 extreme-MESH severity rule: cap, exclude, or produce named raw/capped sensitivity fields.
2. Build M1 frequency from the reconciled M0 severe-day flags.
3. Build M1 empirical MESH-size summaries only with the severity QA rule made explicit.
4. Only after M1 review, resume M2-M4 solar coupling and loss metrics.

Use [`m0_m1_scaleout_execution.md`](m0_m1_scaleout_execution.md) as the execution guide.
