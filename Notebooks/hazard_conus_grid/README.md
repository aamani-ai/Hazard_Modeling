# Hazard CONUS Grid Notebooks

Exploratory/build notebooks for the CONUS gridded hazard-risk product.

This notebook tree is separate from the existing deep-asset notebooks because it has product-level concerns:
the benchmark grid, canonical assets, per-cell artifact contracts, adapters, and grid-scale validation.
Shared source-understanding work stays in the common peril notebooks unless it is truly grid-specific.

Plan-of-record:
[`docs/plans/hazard_conus_grid/`](../../docs/plans/hazard_conus_grid/README.md).

## Layout

```text
hazard_conus_grid/
  common/
    01_benchmark_grid/
  hail/
    m0_input_data/             <- grid adapters / selected-cell provenance only
      01_mrms_daily_mesh/
      02_myrorss_reanalysis/   <- redirect to common hail source qualification
      03_storm_events_anchor/
      04_pilot_cell_lock/
    m1_hazard_layer/
      01_selected_cell_pilot/
    solar/
      m2_m4_risk_metrics/
  wildfire/
```

Start with [`common/01_benchmark_grid/`](common/01_benchmark_grid/), then the grid adapter/provenance
notebooks under `hail/m0_input_data/`, then
[`hail/m1_hazard_layer/01_selected_cell_pilot/`](hail/m1_hazard_layer/01_selected_cell_pilot/), then
[`hail/solar/m2_m4_risk_metrics/`](hail/solar/m2_m4_risk_metrics/).

## Working Rule

Follow the exploratory notebook principle:
[`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../docs/principles/notebook_work/exploratory_data_notebooks.md).

For every source, document provenance, units, grid conventions, fill/no-data values, sampling windows, QA
caveats, and the carried-forward artifact.

The current hail M1 pilot is MRMS-only. MYRORSS source qualification now lives in the common hail M0
notebooks:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/
```

Those notebooks normalize MYRORSS into the same daily cell evidence contract before any grid M1 layer uses
it. Grid-specific selected-cell outputs remain under `data/hazard_conus_grid/hail/` because they prove the
benchmark-cell adapter.

## What This Notebook Tree Asks

```text
grid foundation asks:
  what benchmark cell contract does every hazard use?
  what cells are served in the CONUS hazard product?
  what cell_id / geometry / mask is authoritative?

hazard M0 grid adapters ask:
  how does a native source pixel or report map to a benchmark cell?
  what daily cell evidence is written?
  what no-data / no-hail / severe-hail states are explicit?

hazard M1 grid layers ask:
  for each cell, what frequency and severity summary is carried?
  what QA flags prevent false precision?
  what artifacts are product inputs vs provenance?

asset risk layers ask:
  can a canonical asset consume the grid hazard layer?
  do M2-M4 metrics use the same stochastic discipline as deep assets?
  which outputs are smoke tests, screening layers, or reportable layers?
```

This tree is about scalable contracts. It should not silently inherit single-site assumptions from the deep Hayhurst
notebooks.
