# Hazard CONUS Grid — Hail Notebooks

Grid-specific hail notebooks. These adapt the completed hail method to the benchmark grid; they should reuse
the deep/common hail notebooks where useful, but should not inherit Hayhurst-only assumptions.

Shared hail source qualification lives under `Notebooks/hail/m0_input_data/`. This folder should hold only
grid adapters, selected-cell pilots, product contracts, and grid-specific provenance.

Plan:
[`docs/plans/hazard_conus_grid/hail/`](../../../docs/plans/hazard_conus_grid/hail/README.md).

## Active Build Path

The active hail-grid path is **MRMS-only full-grid V1**:

```text
MRMS daily MESH
  -> served-CONUS daily cell evidence
  -> MRMS-only per-cell M1 hazard layer
  -> canonical solar risk metrics with provisional-tail flags
```

The selected-cell notebooks are V0 contract proofs. The MYRORSS notebooks are common source qualification.
Neither is the main V1 grid build.

## Layout

```text
hail/
  m0_input_data/                 <- grid adapters, pilot provenance, and MRMS V1 M0 proofs
    01_mrms_daily_mesh/
    02_myrorss_reanalysis/       <- redirect to common hail M0 MYRORSS source qualification
    03_storm_events_anchor/
    04_pilot_cell_lock/
  m1_hazard_layer/
    01_selected_cell_pilot/
    02_full_conus_build/
  solar/
    m2_m4_risk_metrics/
```

Future folders:

```text
  wind/
    m2_m4_risk_metrics/
```

## Gate Before Processing

Do not run a full hail grid build until the benchmark grid artifact is locally validated:

```text
gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet
```

The 13,085-cell served CONUS mask is pinned at:

```text
data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

The selected-cell hail pilot now has a pinned selected-cell manifest:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
```

Use that file as the input to the M1 pilot. Candidate and QA files are provenance, not the M1 input list.

The selected-cell M1 pilot has now been executed:

```text
Notebooks/hazard_conus_grid/hail/m1_hazard_layer/01_selected_cell_pilot/01_m1_selected_cell_pilot.ipynb
```

It produced:

```text
data/hazard_conus_grid/hail/m1_selected_cell_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.json
```

This is an MRMS-only selected-cell interface pilot. The next full-grid build is MRMS-only V1, documented in
`docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`. MYRORSS, MESH de-biasing, EVT tail, and
long-record extensions are later stages, not part of V1.

The first MRMS-only V1 full-grid proof has now been executed:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/02_mrms_v1_full_grid_one_day_proof.ipynb
```

It produced:

```text
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/mrms_v1_one_day_full_grid_daily_panel_20240601_v2026_06_16.parquet
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/mrms_v1_one_day_status_summary_20240601_v2026_06_16.csv
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/mrms_v1_one_day_top_cells_20240601_v2026_06_16.csv
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/mrms_v1_one_day_metadata_20240601_v2026_06_16.json
data/hazard_conus_grid/hail/qa/mrms_v1_one_day_status_map_20240601_v2026_06_16.png
```

This proof is not annual climatology. It exists to validate the all-served-cell aggregation and status
contract before MRMS inventory / full-record batching.

The first MRMS-only V1 source-inventory proof has also been executed:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/03_mrms_v1_source_inventory.ipynb
```

It produced local and GCS-dev artifacts for `2024-06-01` to `2024-06-07`:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

This proof accepted 7 source days, listed 336 MRMS files, and wrote a one-batch spec for later M0 daily-cell
evidence. It is not the final full-record denominator.

The first selected-cell hail x solar M2-M4 smoke test has also been executed:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/01_selected_cell_solar_smoke.ipynb
```

It produced:

```text
data/hazard_conus_grid/hail/solar/m2_solar_smoke_event_set_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.json
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.json
```

This output proves the downstream metric interface only. It is not a reportable hail risk layer because the
M1 rate and size distribution are still bounded-window, MRMS-only pilot inputs.

The first **full-M1 selected-cell** hail x solar M2-M4 smoke test has also been executed:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/
  03_full_m1_selected_cell_solar_smoke.ipynb

data/hazard_conus_grid/hail/solar/v1_mrms_only/m2_m4_selected_cell_smoke/
  run_id=20260618T045301Z_m2_m4_selected_cell_smoke/

gs://infrasure-benchmark/hazard_conus_grid/dev/hail/solar/v1_mrms_only/m2_m4_selected_cell_smoke/
  run_id=20260618T045301Z_m2_m4_selected_cell_smoke/
```

This run consumes the full-CONUS M1 artifact, selects five smoke cells, emits raw and capped-sensitivity
severity-policy rows, and produces provisional EAL / VaR / PML / TVaR metric columns. It proves the M2-M4
shape for full-M1 inputs, but it is still labeled `provisional_selected_cell_smoke_not_reportable`.

The bridge notebook:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/02_hayhurst_reference_bridge.ipynb
```

returns `pass_for_interface_bridge_not_calibration`: the grid Hayhurst-reference row differs from the deep
Hayhurst asset run for explainable reasons, and this is not a calibration claim.

The first MYRORSS M0 meet-the-data notebook has also been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/01_myrorss_meet_data.ipynb
```

It produced source-understanding and one-day aggregation samples:

```text
data/hazard_conus_grid/hail/myrorss_m0_sample_day_top_cells_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cells_sample_day_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_source_probe_v2026_06_16.json
```

These prove MYRORSS access, sparse-grid decoding, and native-pixel to benchmark-cell aggregation for one
active sample day. They are not final MYRORSS climatology and do not replace the MRMS-only M1 pilot.

The second MYRORSS M0 selected-cell scan has also been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/02_selected_cell_record_scan.ipynb
```

It produced report-guided scanner-QA artifacts:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_scan_dates_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_summary_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_metadata_v2026_06_16.json
```

This scan uses NOAA reports only to choose stress dates. It found zero exact selected-cell severe MYRORSS days
in the bounded sample, but it found severe MYRORSS in the Hayhurst 3x3 neighborhood on `2010-06-16`. Use it
for source QA and spatial-mismatch diagnosis only, not as a frequency estimate.

The third MYRORSS M0 selected-cell batch notebook has also been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/03_selected_cell_full_record_batches.ipynb
```

It produced a chronological batch plan and a two-day proof batch:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_batch_plan_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_day_manifest_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_daily_panel_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_summary_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_metadata_19980501_19980502_v2026_06_16.json
```

The proof batch scanned `1998-05-01` to `1998-05-02`, listed/read 592 MYRORSS MESH files, recorded zero read
failures, and wrote one selected-cell row per scanned date.

The first planned 14-day batch has also been executed:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_day_manifest_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_daily_panel_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_summary_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_metadata_19980501_19980514_v2026_06_16.json
```

It scanned `1998-05-01` to `1998-05-14`, listed/read 4,144 MYRORSS MESH files, recorded zero read failures,
and wrote 56 selected-cell rows. It is still a partial MYRORSS-era batch and not a final frequency estimate.

Two additional planned batches have been executed through the local/backend runner:

```text
1998-05-15 to 1998-05-28
1998-05-29 to 1998-06-11
```

Together the first three planned batches cover 42 chronological days, list/read 12,432 MYRORSS MESH files,
write 168 selected-cell daily rows, and have zero final read failures after retrying one transient S3 `503`.
Use `scripts/run_myrorss_selected_cell_batches.py` only after the source-promotion gates in
`docs/plans/hazard_conus_grid/common/gridded_radar_source_qualification.md` are answered. Do not treat the
next chronological MYRORSS batch as a V1 grid-build step.

The fourth MYRORSS M0 notebook has also been executed:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/04_reconcile_selected_cell_batches.ipynb
```

It produced the first partial reconciled selected-cell panel:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_batch_manifest_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_date_coverage_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_daily_panel_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_summary_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_metadata_partial_19980501_19980611_v2026_06_16.json
```

It accepted clean planned batches 0001-0003, skipped the overlapping proof batch, and validated complete
date/cell coverage for `1998-05-01` to `1998-06-11`.

Next step: run the full intended MRMS source inventory and freeze the accepted-date denominator for full-grid
V1. Keep MYRORSS as common source qualification until promotion gates are answered.

## What The Hail Grid Folder Asks

```text
hail grid asks:
  how does MRMS daily MESH become cell-day evidence?
  which selected cells prove the interface before full-CONUS fanout?
  what MRMS-only V1 layer can screen risk now?
  what QA flags mark frequency spikes or raw-MESH severity problems?
  what later stages are needed before reportable loss?
```

It does not ask:

```text
  how should Hayhurst-only assumptions be copied to every cell?
  how should MYRORSS be silently mixed into V1?
  how should deep-tail PML be trusted before tail treatment exists?
```

The V1 grid is a screening layer first; source extension and tail modeling are later accuracy stages.
