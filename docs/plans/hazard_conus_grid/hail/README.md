# Hazard CONUS Grid — Hail

Hail is the first and hardest CONUS grid hazard because the M1 layer must be built from raw gridded evidence.
There is no FSim-equivalent public product that already gives both per-cell event frequency and hail-size
distribution.

Read order:

1. [`pilot.md`](pilot.md) — selected-cell pilot and why it exists.
2. [`pilot_cell_selection.md`](pilot_cell_selection.md) — how selected cells are chosen without legacy shortcuts.
3. [`v1_mrms_only_grid_build.md`](v1_mrms_only_grid_build.md) — V1 full-grid path: MRMS-only, MYRORSS excluded.
4. [`m0_m1_scaleout_execution.md`](m0_m1_scaleout_execution.md) — gated execution plan, Cloud Run decision point, and M0-M4 sequence.
5. [`../common/gcp_execution_and_storage_conventions.md`](../common/gcp_execution_and_storage_conventions.md) — Cloud Run, GCS, run-id, and artifact-format rules.
6. [`m0_m1_hazard_layer.md`](m0_m1_hazard_layer.md) — broader hail hazard-layer build and later stages.
7. Discussion source: [`docs/extra/discussion/conus_grid/hail/`](../../../extra/discussion/conus_grid/hail/).
8. Notebook principle: [`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../../principles/notebook_work/exploratory_data_notebooks.md).

## Notebook Roots

```text
Notebooks/hail/m0_input_data/
  03_myrorss_reanalysis_source_qualification/ <- shared MYRORSS source qualification

Notebooks/hazard_conus_grid/hail/
  m0_input_data/                 <- grid adapters / pilot-cell provenance only
    01_mrms_daily_mesh/
    02_myrorss_reanalysis/       <- redirect to shared MYRORSS source qualification
    03_storm_events_anchor/
    04_pilot_cell_lock/
  m1_hazard_layer/
    01_selected_cell_pilot/
    02_full_conus_build/
  solar/
    m2_m4_risk_metrics/
  wind/
    m2_m4_risk_metrics/
```

Existing hail notebooks under [`Notebooks/hail/`](../../../../Notebooks/hail/) remain the method/reference
source for the deep asset build and the common source-qualification home. Grid notebooks should reuse ideas
and helper patterns where useful, but should not inherit Hayhurst-specific assumptions by accident or turn a
shared raw-source investigation into a grid-only artifact.

## Current Pilot Cells

Selected pilot cells are pinned under `data/hazard_conus_grid/hail/`:

```text
selected_pilot_cells_v2026_06_16.csv
selected_pilot_cells_v2026_06_16.json
```

These are selected for the M1 pilot only. They are not a production hail climatology or reportable risk
output.

## Current M1 Pilot Layer

The selected-cell MRMS-only M1 pilot layer has been produced under `data/hazard_conus_grid/hail/`:

```text
m1_selected_cell_daily_panel_v2026_06_16.csv
m1_selected_cell_hazard_layer_v2026_06_16.csv
m1_selected_cell_hazard_layer_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hazard_conus_grid/hail/m1_hazard_layer/01_selected_cell_pilot/01_m1_selected_cell_pilot.ipynb
```

This artifact proves the selected-cell M1 interface only. It is based on MRMS daily MESH from 2024-04-01
through 2024-06-30 and should not be treated as final climatology or reportable risk output.

## Current V1 Direction

The first full-grid hail build is **MRMS-only V1**:

```text
MRMS daily MESH
  -> served-CONUS daily cell evidence
  -> MRMS-only per-cell M1 hazard layer
  -> canonical solar risk layer with provisional-tail flags
```

MYRORSS, MESH de-biasing, and EVT tail fitting are V1.5/V2 work. See
[`v1_mrms_only_grid_build.md`](v1_mrms_only_grid_build.md).

The first V1 full-grid proof has run:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  02_mrms_v1_full_grid_one_day_proof.ipynb
```

It processed one MRMS daily MESH file for `2024-06-01`, wrote one row for each of the 13,085 served CONUS
cells, and produced explicit `observed_no_hail`, `observed_sub_severe_hail`, and `observed_severe_hail`
states.

The first source-inventory proof and the full V1 source inventory have also run:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  03_mrms_v1_source_inventory.ipynb
```

The proof listed MRMS files for `2024-06-01` to `2024-06-07`, accepted 7 source days, listed 336 source
files, wrote a one-batch spec, and uploaded the proof artifacts under:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

The full inventory requested `2014-01-01` to `2026-06-15`, accepted 2,071 continuous source days from
`2020-10-14` through `2026-06-15`, recorded 2,478 explicit no-source dates, recorded zero list failures,
listed 99,313 source files, and wrote 148 planned 14-day M0 batches under:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

The first multi-day full-grid M0 evidence batch has also run locally:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  04_mrms_v1_m0_daily_evidence_batch.ipynb

data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T172929Z/batch=20240601_20240607/
```

It processed 7 accepted source dates, wrote 91,595 rows (`7 x 13,085`), recorded zero duplicate
`cell_id/date` rows, and produced 7 CONUS QA maps embedded in the executed notebook. It uploaded 19 objects
to:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

The next build step is to choose the scaled runner and remote execution plan. The execution gates and runner
decision are documented in
[`m0_m1_scaleout_execution.md`](m0_m1_scaleout_execution.md).

The first Cloud Run proof has also succeeded:

```text
job:    hazard-conus-grid-mrms-m0-bootstrap
run_id: 20260616T205852Z_cloudrun_bootstrap_7d
batch:  2024-06-01 to 2024-06-07
gcs:    gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T205852Z_cloudrun_bootstrap_7d/batch=20240601_20240607/
```

A second 14-day Cloud Run proof has also succeeded:

```text
job:    hazard-conus-grid-mrms-m0-bootstrap
run_id: 20260616T211247Z_m0_batch0001_14d_cloud_proof
batch:  2020-10-14 to 2020-10-27
gcs:    gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T211247Z_m0_batch0001_14d_cloud_proof/batch=20201014_20201027/
```

The 7-day proof wrote 91,595 rows and matched the local proof counts exactly. The 14-day proof wrote 183,190
rows. These are `cloud_proof` outputs, not the full historical CONUS run.

The durable GitHub Actions / Artifact Registry / Cloud Run Job path has also succeeded after moving the repo
under the `aamani-ai` organization:

```text
workflow:  Deploy Hazard CONUS Grid MRMS M0 Job
run:       27649989510
job:       hazard-conus-grid-mrms-m0
execution: hazard-conus-grid-mrms-m0-lcqqg
run_id:    20260616T214036Z_wif_deploy_probe
batch:     2024-06-01 to 2024-06-07
gcs:       gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T214036Z_wif_deploy_probe/batch=20240601_20240607/
```

This proves the durable image path. Future repeated Cloud Run batches should use
`hazard-conus-grid-mrms-m0`, not the earlier bootstrap job, unless debugging specifically needs the bootstrap
fallback.

The first reconciliation proof has also succeeded:

```text
script: scripts/reconcile_mrms_v1_m0_batches.py
run_id: 20260616T211844Z_m0_reconcile_2batch_proof
gcs:    gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/run_id=20260616T211844Z_m0_reconcile_2batch_proof/
```

It reconciled 2 non-overlapping Cloud Run batches, 21 dates, and 274,785 rows with zero duplicate
`cell_id/date` rows. It flagged `extreme_mesh_ge_300mm` because the 14-day batch contains one extreme raw MESH
value.

The first full task-indexed Cloud Run run and full streaming reconciliation have now succeeded:

```text
Cloud Run run_id:      20260616T220624Z_m0_full_conus_task_indexed
GitHub Actions run:    27651275076
Cloud Run execution:   hazard-conus-grid-mrms-m0-54dm7
tasks / parallelism:   148 / 8
task result:           148 succeeded, 0 failed

reconciled run_id:     20260616T225000Z_m0_full_conus_reconciled
reconciled gcs:        gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
dates:                 2,071
served cells/date:     13,085
rows:                  27,099,035
duplicate cell-dates:  0
row-count failures:    0
qa flags:              extreme_mesh_ge_300mm
```

This reconciled root is the active M0 input for M1 after QA review. Do not build M1 from individual raw
`m0_daily_cell_evidence/run_id=.../batch=...` prefixes.

The first full M0 review artifact has also been produced:

```text
review run_id:         20260616T232500Z_m0_review
review gcs:            gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_review/run_id=20260616T232500Z_m0_review/
row contract status:   passed
extreme raw MESH:      613 cell-days, 585 cells, 38 dates, max 1,437.4 mm
recommendation:        frequency can proceed after review; empirical size/loss severity needs a named
                       extreme-MESH QA/capping rule or sensitivity
```

## Artifact Organization

Treat current hail grid outputs in three groups:

| Group | Examples | Meaning |
|---|---|---|
| Research / selected-cell proof | `selected_pilot_cells_*`, `m1_selected_cell_*`, MYRORSS selected-cell scans, solar smoke outputs | Interface and source-learning evidence only. |
| M0 proof outputs | `m0_mrms_v1_one_day_proof/`, `run_id=20260616T172929Z`, `run_id=20260616T205852Z_cloudrun_bootstrap_7d`, `run_id=20260616T214036Z_wif_deploy_probe` | Row contract, remote execution, durable image, and GCS write proof. |
| Main V1 build | `run_id=20260616T225000Z_m0_full_conus_reconciled` under `m0_reconciled_daily_cell_evidence/` | Active M0 input to M1 after QA review. |

The full MRMS denominator, reconciled M0 layer, and M0 review artifact now exist. The next hail grid step is
to define the V1 extreme-MESH severity rule, then build M1 frequency from the reconciled root. Empirical
size-distribution summaries must carry the raw/capped/filter decision explicitly.

## Current Solar Smoke Test

The selected-cell hail x canonical-solar M2-M4 smoke test has been produced under
`data/hazard_conus_grid/hail/solar/`:

```text
m2_solar_smoke_event_set_v2026_06_16.csv
m4_solar_smoke_risk_metrics_v2026_06_16.csv
m4_solar_smoke_risk_metrics_v2026_06_16.json
hayhurst_reference_bridge_v2026_06_16.csv
hayhurst_reference_bridge_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/01_selected_cell_solar_smoke.ipynb
```

This smoke test proves that the M1 selected-cell layer can feed the canonical solar coupling, damage, annual
loss, and metric interface. It is not reportable hail risk because the M1 frequency and severity inputs are
still MRMS-only and bounded to 2024-04-01 through 2024-06-30.

The Hayhurst reference bridge has also run:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/02_hayhurst_reference_bridge.ipynb
```

Status: `pass_for_interface_bridge_not_calibration`. The bridge explains why the grid smoke Hayhurst row is
lower than the deep Hayhurst asset run: canonical exposure, short M1 window, clipped cell-day footprint proxy,
Poisson placeholder, and only two low-severity hail-day samples.

## Current MYRORSS M0 Source Qualification

MYRORSS is common hail source qualification. The current outputs are grid selected-cell adapter proofs, so
they live under `data/hazard_conus_grid/hail/`, but the notebooks live under common hail M0.

The first MYRORSS meet-the-data notebook has been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/01_myrorss_meet_data.ipynb
```

It produced:

```text
myrorss_m0_sample_day_top_cells_20100616_v2026_06_16.csv
myrorss_m0_selected_cells_sample_day_20100616_v2026_06_16.csv
myrorss_m0_source_probe_v2026_06_16.json
```

This proves MYRORSS public-bucket access, sparse netCDF decoding, coordinate reconstruction, and one-day
native-pixel to benchmark-cell aggregation. It is not a 1998-2011 climatology and is excluded from V1 until
source-promotion gates and MRMS/MYRORSS consistency checks are complete.

The selected-cell report-guided scan has also been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/02_selected_cell_record_scan.ipynb
```

It produced:

```text
myrorss_m0_selected_cell_scan_dates_v2026_06_16.csv
myrorss_m0_selected_cell_report_guided_daily_panel_v2026_06_16.csv
myrorss_m0_selected_cell_report_guided_summary_v2026_06_16.csv
myrorss_m0_selected_cell_report_guided_metadata_v2026_06_16.json
```

This scan is report-guided and bounded: 9 unique dates, 36 selected-cell rows, 2,671 MYRORSS source files,
53 zero-byte source files flagged, and no read failures. It found no exact selected-cell severe MYRORSS days,
but found severe MYRORSS in the Hayhurst 3x3 neighborhood on `2010-06-16`. It is scanner QA and
spatial-mismatch context only, not a frequency estimate.

The chronological batch and reconciliation notebooks have also been executed for the first three clean
planned MYRORSS batches:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/03_selected_cell_full_record_batches.ipynb
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/04_reconcile_selected_cell_batches.ipynb
```

They currently cover `1998-05-01` to `1998-06-11`, with 42 chronological days, 168 selected-cell daily rows,
12,432 source files represented, zero read failures after retry, zero exact selected-cell severe days, and
one Hayhurst 3x3-neighborhood severe QA day. This is still partial source evidence, not a MYRORSS climatology.

MRMS-derived candidate/provenance artifacts also exist:

```text
pilot_cell_candidates_mrms_202404_202406.csv
pilot_cell_candidates_mrms_202404_202406.json
```

They were generated through [`pilot_cell_selection.md`](pilot_cell_selection.md) using the pinned benchmark
grid, MRMS daily MESH evidence, the Hayhurst coordinate assignment, NOAA/NRI report-side QA, and a lightweight
map / broad-role review.

For MRMS/MYRORSS exploration, the notebook deliverable is not just plots. It must document source provenance,
grid/CRS/unit/fill conventions, sampling windows, field meanings, QA caveats, and the carried-forward M1
artifact.
