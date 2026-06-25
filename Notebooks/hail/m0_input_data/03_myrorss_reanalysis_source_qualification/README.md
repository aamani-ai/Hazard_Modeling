# 03 - MYRORSS Reanalysis Source Qualification

Purpose: qualify the long-record MYRORSS gridded hail evidence source in the common hail M0 layer before
any site-specific or CONUS-grid workflow uses it.

This folder is intentionally outside `Notebooks/hazard_conus_grid/`. The reader, retry, sparse-grid
decoding, batching, metadata, and reconciliation mechanics are shared gridded-radar source qualification.
The current selected-cell outputs are a **grid adapter proof** because they aggregate the source to
benchmark `cell_id`s and write under `data/hazard_conus_grid/hail/`; the source understanding itself is not
grid-only.

Source-role framing:

| Source | Window | Role |
|---|---:|---|
| NOAA Storm Events / SPC reports | 1996-2024+ for current QA pulls | Date context and report-side validation only. |
| MYRORSS | 1998-2011 | Older gridded radar reanalysis to extend the evidence record. |
| MRMS MESH | 2014-present operational era | Current selected-cell pilot spine and operational-era baseline. |
| FEMA NRI | Current product, with 1996-2019 hail loss-rate inputs | Downstream sanity check only, not M1 input. |

The full sourcing decision lives in
`docs/extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md`, and the shared/grid boundary is documented
in `docs/plans/hazard_conus_grid/common/gridded_radar_source_qualification.md`. This folder should only
create MYRORSS evidence with the same contract as the MRMS pilot; it should not blend in report or NRI data
as hazard truth.

The first meet-the-data notebook has been executed:

```text
01_myrorss_meet_data.ipynb
```

It verifies the public MYRORSS bucket layout, decodes one MESH netCDF file, documents the sparse-grid
variables/attributes, reconstructs latitude/longitude, aggregates one active sample day to the 0.25 degree
benchmark grid, and writes small sample artifacts.

Sample day:

```text
2010-06-16
```

Outputs:

```text
data/hazard_conus_grid/hail/myrorss_m0_sample_day_top_cells_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cells_sample_day_20100616_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_source_probe_v2026_06_16.json
```

These are M0 source-understanding outputs only. They are not a final MYRORSS climatology and do not replace
the MRMS-only selected-cell M1 pilot.

The second selected-cell scan notebook has also been executed:

```text
02_selected_cell_record_scan.ipynb
```

It uses cached NOAA Storm Events only to choose stress-test dates, then scans MYRORSS for the four locked
selected cells plus each cell's 3x3 neighborhood. The NOAA dates are a sampling aid only; MYRORSS remains the
gridded evidence source.

Outputs:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_scan_dates_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_summary_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_report_guided_metadata_v2026_06_16.json
```

Result:

- 9 unique scan dates, 36 selected-cell panel rows.
- 2,671 MYRORSS source files listed/read across the scanned dates.
- 53 zero-byte source files on `2006-07-05`; recorded as `n_empty_source_files`, not decoder failures.
- 0 exact selected-cell severe MYRORSS days in this bounded sample.
- Hayhurst has severe MYRORSS evidence in its 3x3 neighborhood on `2010-06-16`
  (`neighbor_3x3_max_mesh_mm = 37.829437`), while the exact selected cell remains sub-severe.

Interpretation: the report-guided sample is useful for scanner QA and spatial-mismatch diagnosis, but it is
not an unbiased frequency sample and must not enter M1 as a rate estimate.

## Expected Contract

The MYRORSS notebook should produce the same logical daily cell evidence contract as the MRMS notebook:

- `hazard = hail`;
- `cell_id`;
- `date`;
- source product and timestamp;
- threshold used for severe hail;
- observed native pixel count or coverage measure;
- severe native pixel count or severe area proxy;
- hail-day flag;
- observed size summaries where the source supports them;
- coverage / no-data flags;
- provenance and QA notes.

Once this exists, M1 can harmonize MRMS and MYRORSS by source role instead of treating one as an unexplained
replacement for the other.

## What We Learned

- MYRORSS is available from the public `noaa-oar-myrorss-pds` bucket.
- The record years visible from the bucket are 1998-2011.
- MESH lives under `YYYY/MM/DD/MESH/00.25/`.
- Files can be `.netcdf.gz` or older plain `.netcdf`, so the reader must handle both.
- MESH files are sparse lat/lon grids, not dense rasters.
- Coordinate reconstruction uses file attributes plus `pixel_x` / `pixel_y`.
- One-day aggregation can produce the same logical daily-cell evidence shape as MRMS.
- Full-record selected-cell scanning is file-count dominated because MYRORSS has no cell-level spatial
  index; use chronological batches and the raw-byte cache.

## Non-Goals

- Do not use MYRORSS to overwrite the MRMS pilot silently.
- Do not use Storm Events, NRI, or legacy risk outputs as a substitute for gridded evidence.
- Do not produce final PML/VaR/TVaR metrics from this source until MESH bias and tail treatment are
  documented.

## Chronological Batch Notebook

The third MYRORSS notebook has been executed:

```text
03_selected_cell_full_record_batches.ipynb
```

It creates a 357-row 14-day batch plan for the `1998-05-01` to `2011-12-31` MYRORSS candidate window and
executes a small chronological proof batch:

```text
1998-05-01 to 1998-05-02
```

Outputs:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_batch_plan_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_day_manifest_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_daily_panel_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_summary_19980501_19980502_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_metadata_19980501_19980502_v2026_06_16.json
```

Result:

- 2 chronological days scanned, not report-guided.
- 592 MYRORSS MESH files listed/read.
- 0 empty source files and 0 read failures.
- 8 selected-cell daily rows written.
- 0 exact selected-cell severe MYRORSS days in this proof batch.
- 1 low-hail 3x3-neighborhood day with sub-severe sparse MESH context (`neighbor_3x3_max_mesh_mm = 9.123694`).

The first planned 14-day batch has also been executed:

```text
1998-05-01 to 1998-05-14
```

Outputs:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_day_manifest_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_daily_panel_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_summary_19980501_19980514_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_full_record_metadata_19980501_19980514_v2026_06_16.json
```

Result:

- 14 chronological days scanned, not report-guided.
- 4,144 MYRORSS MESH files listed/read.
- 0 empty source files and 0 read failures.
- 56 selected-cell daily rows written.
- 0 exact selected-cell severe MYRORSS days in this batch.
- 1 exact low-hail selected-cell day with sub-severe sparse MESH (`mesh_max_mm = 6.3018`).
- 2 low-hail 3x3-neighborhood days with sub-severe sparse MESH context (`neighbor_3x3_max_mesh_mm = 9.123694`).

Two more planned batches have also been executed:

```text
1998-05-15 to 1998-05-28
1998-05-29 to 1998-06-11
```

Combined clean planned-batch state:

- 42 chronological days scanned.
- 12,432 MYRORSS MESH files listed/read.
- 0 empty source files and 0 read failures after retrying one transient S3 `503` in batch 0003.
- 168 selected-cell daily rows written.
- 0 exact selected-cell severe MYRORSS days.
- 1 Hayhurst 3x3-neighborhood severe day in batch 0002 (`neighbor_3x3_max_mesh_mm = 33.943497`).

The local/backend runner is:

```text
scripts/run_myrorss_selected_cell_batches.py
```

It skips batches with clean metadata and retries batches whose metadata fails validation. Next: execute batch
0004 (`1998-06-12` to `1998-06-25`) only after the source promotion gates are documented. Do not move to a
larger compute/orchestration setup just because the local runner works.

## Reconciliation Notebook

The fourth MYRORSS notebook has been executed:

```text
04_reconcile_selected_cell_batches.ipynb
```

It reads completed batch metadata, accepts only clean planned batches, skips the overlapping proof batch, and
writes one partial selected-cell MYRORSS panel.

Outputs:

```text
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_batch_manifest_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_date_coverage_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_daily_panel_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_summary_partial_19980501_19980611_v2026_06_16.csv
data/hazard_conus_grid/hail/myrorss_m0_selected_cell_reconciled_metadata_partial_19980501_19980611_v2026_06_16.json
```

Result:

- 3 clean planned batches accepted: 0001-0003.
- 42 chronological days reconciled: `1998-05-01` to `1998-06-11`.
- 168 selected-cell daily rows written.
- 12,432 MYRORSS MESH files represented.
- 0 read failures, 0 missing dates, 0 duplicate `cell_id` / `date` rows.
- 0 exact selected-cell severe MYRORSS days.
- 1 Hayhurst 3x3-neighborhood severe QA day.

Next: document the source-promotion gate before running more batches through
`scripts/run_myrorss_selected_cell_batches.py`. After additional approved batches, rerun this reconciliation
notebook before using widened MYRORSS evidence in any M1 comparison.
