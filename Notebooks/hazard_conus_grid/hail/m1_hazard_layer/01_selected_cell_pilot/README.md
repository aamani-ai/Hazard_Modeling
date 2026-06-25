# 01 — Selected-Cell Hail M1 Pilot

Goal: turn the selected-cell MRMS daily evidence table into a tiny M1 hazard-distribution layer.

Plan reference:
[`docs/plans/hazard_conus_grid/hail/pilot.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot.md).
Selection protocol:
[`docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md`](../../../../../docs/plans/hazard_conus_grid/hail/pilot_cell_selection.md).

## Input

Output from:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
Notebooks/hazard_conus_grid/hail/m0_input_data/03_storm_events_anchor/
Notebooks/hazard_conus_grid/hail/m0_input_data/04_pilot_cell_lock/
```

Selected-cell manifest:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
```

Candidate and QA files are provenance. The M1 pilot should consume the selected manifest.

## Output

A small M1 layer with one row per selected `cell_id`, carrying:

- `hazard = hail`;
- `cell_id`;
- `lambda_cell`;
- `freq_dist`;
- `fano_phi` or sparse-cell fallback flag;
- empirical MESH size distribution summary;
- `n_hail_days`;
- `record_span`;
- `sparse_cell_flag`;
- provenance and QA flags.

Current executed outputs:

```text
data/hazard_conus_grid/hail/m1_selected_cell_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.json
```

These are selected-cell interface artifacts only. They use MRMS daily MESH from 2024-04-01 to
2024-06-30, with explicit zero-severe days materialized for all four selected cells. The annualized
`lambda_cell` field is a pilot-window interface value, not a final climatological hail rate.

## Source Flow

This pilot uses only MRMS as the gridded evidence source. Other data sources join later at named stages:

| Source | Status in this notebook | Later join point |
|---|---|---|
| MRMS daily MESH | used | Current gridded spine for daily severe-hail evidence. |
| MYRORSS | deferred | `Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/`, normalized to the same daily cell evidence contract before any M1 harmonization. |
| NOAA Storm Events / SPC | referenced through QA provenance | validation/calibration, not raw grid truth. |
| Murillo & Homeyer / climatology research | deferred | broad pattern validation and MESH de-biasing before full CONUS claims. |
| Das & Allen / EVT tail work | deferred | size-tail modeling before high-return-period PML/TVaR readouts. |
| FEMA NRI | sanity check only | downstream coarse QA, not M1 and not loss input. |

## Success Criteria

- Selected cells join cleanly to the benchmark grid.
- High/medium/low cells rank in the expected direction based on the documented selection evidence.
- Hayhurst/reference cell is directionally consistent with the deep hail x solar work.
- No-data, no-hail, and zero-risk states are represented separately.
- The tiny M1 layer can drive one solar M2-M4 risk run.

## Non-Goals

- Full CONUS processing.
- MYRORSS extension.
- EVT tail fitting.
- Final PML500/TVaR99 reporting.
