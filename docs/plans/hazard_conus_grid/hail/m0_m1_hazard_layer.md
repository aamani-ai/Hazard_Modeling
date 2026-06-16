# Hail — M0/M1 Hazard Layer Plan

Goal: build a reusable per-cell hail hazard-distribution layer for the benchmark grid.

## Target Layer

One row per `cell_id` in the summary artifact, backed by daily evidence rows.

The layer should answer:

```text
For this 0.25° cell, what is the annual severe-hail event frequency distribution,
and what is the hail-size distribution conditional on a severe hail day?
```

## Single-Site Radius vs Grid Cell

The single-site Hayhurst hail pipeline used a 50-mile collection region because it answered a site-specific
question:

```text
For this one real asset, what hail evidence happened near the asset?
```

The CONUS grid V1 does not reuse a 50-mile circle around every grid cell. Each 0.25 degree benchmark cell is
the hazard bucket:

```text
MRMS native pixels
  -> assign each pixel to its matching benchmark cell_id
  -> summarize evidence inside that cell only
  -> save one row per cell_id x date
```

So an M0 daily evidence row means:

```text
On this date, for this grid cell:
  did MRMS cover it?
  did it have no hail, sub-severe hail, or severe hail?
  how many native MRMS pixels were severe?
  what was the max / distribution of MESH size in that cell?
  which source file did this come from?
```

The 50-mile idea can still exist as a **site-specific collection radius** or as a future smoothing/validation
experiment, but it is not the default V1 grid hazard definition. Reusing it silently would blur neighboring
cells and double-count spatial evidence.

For later M2-M4, the canonical 100 MW plant is placed conceptually **inside the cell**. Asset coupling should
use the per-cell hazard evidence plus the canonical asset footprint/exposure assumption. It should not
silently switch back to a 50-mile collection region unless a separate, named decision says so.
The revisit gate is documented as
[`DD-G8`](../decisions.md#dd-g8--defer-canonical-asset-coupling-finalization-until-full-m0m1-cell-comparisons).

## Source Roles

| Source | Role |
|---|---|
| MRMS daily MESH | **V1 spine** for severe-hail-day evidence, footprint/area, and observed radar-estimated sizes. |
| MYRORSS | **Excluded from V1**; later long-record radar/reanalysis extension after source promotion gates and MRMS/MYRORSS homogeneity checks. |
| Storm Events | V1 report-side validation/date context and later calibration anchor; not the raw grid truth. |
| Murillo & Homeyer / climatology research | V1 broad spatial sanity check; later MESH bias/de-biasing anchor. |
| FEMA NRI | Downstream sanity check only; not an M1 hazard input. |

Source rule: each data source must enter through a named stage with a stated role. Do not silently blend
report data, climatology products, or legacy outputs into the MRMS grid layer.

The compact hail source timeline is documented in
[`docs/extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md`](../../../extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md):
NOAA reports are report-side validation/date context, MYRORSS is the 1998-2011 older gridded reanalysis,
MRMS is the newer gridded operational-era spine, and FEMA NRI is downstream sanity only. The current full
MRMS source inventory requested `2014-01-01` to `2026-06-15`, but public files for the selected daily MESH
product are accepted from `2020-10-14` forward in this run. Keep earlier no-source dates explicit rather
than treating them as zero-hail days.

Boundary note: the MYRORSS/MRMS reader, retry, batch, metadata, and reconciliation mechanics are **common
gridded-radar source qualification**, not grid-only modeling. The grid-specific part is the `cell_id`
extraction adapter. See
[`common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md) before any
GCP/full-scale processing.

## Build Stages

V0 selected-cell contract work is done. V1 is now MRMS-only full-grid.

1. Pin benchmark grid and served CONUS mask. **Done.**
2. Select pilot cells through [`pilot_cell_selection.md`](pilot_cell_selection.md), with evidence and join proof. **Done.**
3. Build MRMS selected-cell daily evidence. **Done.**
4. Fit/summary selected-cell frequency and empirical size distribution. **Done for interface pilot only.**
5. Run one solar M2-M4 pass from that layer. **Done for selected-cell smoke test only.**
6. Prove **MRMS-only V1 full-grid M0 daily evidence** on one accepted MRMS day. **Done.**
7. Prove the MRMS source-inventory and GCS upload contract on a small date window. **Done.**
8. Build the MRMS source inventory and batch contract for the intended V1 record window. **Done.**
9. Build **MRMS-only V1 full-grid M0 daily evidence**.
10. Build **MRMS-only V1 per-cell M1 hazard layer**.
11. Validate V1 against Storm Events and broad hail climatology; use NRI only downstream.
12. Run canonical solar M2-M4 from the MRMS-only V1 layer with provisional-tail flags.
13. Defer MYRORSS, MESH de-biasing, EVT tail, and more complex frequency/shrinkage to V1.5/V2.

The detailed V1 path is:
[`v1_mrms_only_grid_build.md`](v1_mrms_only_grid_build.md).

The gated execution plan is:
[`m0_m1_scaleout_execution.md`](m0_m1_scaleout_execution.md).

Current selected-cell state: **selected pilot cells are pinned for the M1 pilot**:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
```

The selected-cell M1 pilot consumed this file, not the candidate/QA provenance files directly. Do not use
unexplained legacy delivery outputs as a shortcut.

Current selected-cell M1 state: **MRMS-only pilot layer has been produced**:

```text
data/hazard_conus_grid/hail/m1_selected_cell_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hazard_conus_grid/hail/m1_hazard_layer/01_selected_cell_pilot/01_m1_selected_cell_pilot.ipynb
```

This layer is only a selected-cell interface pilot. It uses MRMS daily MESH for 2024-04-01 to 2024-06-30,
materializes zero-severe days, and computes pilot-window frequency and empirical size summaries. It is not
final climatology, not full CONUS, and not a reportable EAL/PML/VaR/TVaR input.

Current downstream solar state: **selected-cell M2-M4 smoke metrics have been produced**:

```text
data/hazard_conus_grid/hail/solar/m2_solar_smoke_event_set_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.json
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/01_selected_cell_solar_smoke.ipynb
```

These outputs prove the downstream schema and engine connection only. They inherit the same M1 caveats and
are not reportable risk numbers.

The Hayhurst bridge status is `pass_for_interface_bridge_not_calibration`: the reference cell comparison is
explainable and shows no immediate interface drift, but it does not calibrate the grid metrics.

Current MYRORSS state: **common M0 source qualification has started**:

MYRORSS notebooks now live under the common hail M0 notebook root because reader/decoder/batch/reconciliation
work is reusable source qualification. The grid-specific piece is the selected-cell `cell_id` adapter and
the output location under `data/hazard_conus_grid/hail/`.

```text
data/hazard_conus_grid/hail/myrorss_m0_sample_day_top_cells_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cells_sample_day_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_source_probe_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/01_myrorss_meet_data.ipynb
```

This probe confirms public MYRORSS access, the `YYYY/MM/DD/MESH/00.25/` layout, sparse netCDF decoding,
coordinate reconstruction, and one-day aggregation to the benchmark `cell_id`. It is source-understanding
only. It is not a final MYRORSS climatology, not an MRMS replacement, and not a reportable risk input.

Current MYRORSS selected-cell scan state: **report-guided bounded scan has been produced**:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_scan_dates_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_summary_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_metadata_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/02_selected_cell_record_scan.ipynb
```

This scan used cached NOAA reports only to choose stress dates, then scanned MYRORSS for the exact selected
cells plus each cell's 3x3 neighborhood. It found zero exact selected-cell severe MYRORSS days in the bounded
sample, but did find nearby severe MYRORSS evidence for the Hayhurst neighborhood on `2010-06-16`. It also
flagged 53 zero-byte source files on `2006-07-05`. This is scanner QA and spatial-mismatch evidence, not a
frequency estimate.

Current MYRORSS full-record batch state: **chronological selected-cell batch contract has been produced and
the first three planned batches have been executed**:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_batch_plan_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_day_manifest_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_daily_panel_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_summary_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_metadata_19980501_19980502_v2026_06_16.json
```

Completed clean planned-batch labels:

```text
19980501_19980514
19980515_19980528
19980529_19980611
```

The producing notebook is:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/03_selected_cell_full_record_batches.ipynb
```

The first proof batch scanned `1998-05-01` to `1998-05-02`, listed/read 592 MYRORSS MESH files, recorded zero
read failures, and wrote one row per selected cell per scanned date. The first three planned 14-day batches
now cover `1998-05-01` to `1998-06-11`, listed/read 12,432 MYRORSS MESH files, recorded zero read failures
after retrying a transient S3 `503` in batch 0003, and wrote 168 selected-cell daily rows. They found zero
exact selected-cell severe MYRORSS days. Batch 0002 found one Hayhurst 3x3-neighborhood severe day
(`neighbor_3x3_max_mesh_mm = 33.943497`) while the exact selected cell remained non-severe. These are batch
QA outputs, not MYRORSS frequency estimates. The batch plan currently divides the `1998-05-01` to
`2011-12-31` candidate window into 357 14-day batches.

The local/backend runner is:

```text
scripts/run_myrorss_selected_cell_batches.py
```

It reads the batch plan, skips batches with clean metadata, retries batches whose metadata fails validation,
and executes notebook `03_selected_cell_full_record_batches.ipynb` with `MYRORSS_BATCH_START` /
`MYRORSS_BATCH_END`.

Current MYRORSS reconciled-batch state: **partial selected-cell panel has been produced from clean planned
batches**:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_batch_manifest_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_date_coverage_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_daily_panel_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_summary_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_metadata_partial_19980501_19980611_v2026_06_16.json
```

The producing notebook is:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/04_reconcile_selected_cell_batches.ipynb
```

This reconciliation accepted planned batches 0001-0003, skipped the overlapping two-day proof batch, checked
continuous date coverage, verified one row per selected cell per date, and wrote a 42-day partial panel
covering `1998-05-01` to `1998-06-11`. The panel has 168 selected-cell daily rows, 12,432 source files,
zero read failures, zero duplicate cell/date rows, zero missing dates, zero exact selected-cell severe
MYRORSS days, and one Hayhurst 3x3-neighborhood severe day. It is still partial source evidence, not a final
MYRORSS climatology.

## Where Other Sources Join

| Stage | Added source | Purpose |
|---|---|---|
| `Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/` | MYRORSS | Common source probe, report-guided scan, chronological batches, runner, and partial reconciliation done. Grid selected-cell outputs are adapter proof only; do not treat them as the grid M1 layer. |
| validation/calibration | NOAA Storm Events / SPC | Check report consistency and later calibrate/report bias; do not use as grid truth. |
| M1 de-biasing / climatology validation | Murillo & Homeyer and related hail climatology research | Check spatial pattern and decide whether/how to de-bias raw MESH size. |
| tail modeling | Das & Allen / EVT work | Extend observed size distribution for high-return-period loss metrics. |
| downstream QA | FEMA NRI | Coarse sanity check only; never a direct M1 or loss input. |

## Key Open Decisions

These are inherited from the discussion docs. V1 resolves the first item as MRMS-only; the rest remain open
for V1.5/V2 or for how V1 is labeled.

- MRMS-only first versus immediate MRMS+MYRORSS: **decided for V1 = MRMS-only**.
- Hail-day versus connected-event definition.
- Per-cell sparse-data pooling/shrinkage rule.
- MESH de-biasing approach.
- EVT tail source and timing.

## Immediate Next Step

Do not move back to MYRORSS, wider selected-cell batches, or model complexity. The MRMS-only V1 one-day
full-grid proof has run:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  02_mrms_v1_full_grid_one_day_proof.ipynb
```

It processed `2024-06-01` across all 13,085 served CONUS cells and wrote a complete one-day panel with
explicit no-hail/sub-severe/severe states.

The MRMS V1 source-inventory proof also ran for `2024-06-01` to `2024-06-07`:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  03_mrms_v1_source_inventory.ipynb
```

It accepted 7 source days, listed 336 files, wrote a one-batch spec, and uploaded the small proof artifacts
to the GCS dev prefix.

The full MRMS V1 source inventory has also run:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

It requested `2014-01-01` to `2026-06-15`, accepted 2,071 continuous source days from `2020-10-14` through
`2026-06-15`, recorded 2,478 explicit no-source dates, recorded zero list failures, listed 99,313 source
files, and wrote 148 planned 14-day M0 batches.

The first local multi-day M0 daily-evidence batch has also run:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T172929Z/batch=20240601_20240607/
```

It wrote 91,595 rows for 7 accepted dates x 13,085 served cells, produced 7 daily CONUS QA maps, and had zero
duplicate `cell_id/date` rows. The same batch uploaded 19 objects to the GCS dev prefix. The next step is to
choose the scaled runner and remote execution plan.

MYRORSS remains available as source qualification only and should not enter the V1 grid layer.
