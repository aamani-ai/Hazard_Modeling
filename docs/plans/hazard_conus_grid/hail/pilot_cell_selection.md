# Hail — Pilot Cell Selection Protocol

This file exists to prevent shortcuts. The selected-cell pilot needs a few cells, but those cells must be
chosen from defensible evidence, not from old risk outputs or unexplained delivery artifacts.

## Status

Final hail pilot `cell_id` values are pinned for the selected-cell M1 pilot:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.json
```

This lock is only for the selected-cell M1 pilot. It is not a production CONUS hail climatology and not a
final reportable risk output.

Selected cells:

| Role | Candidate `cell_id` | Location | Bounded MRMS evidence |
|---|---:|---|---|
| `high_hail` | 329354 | TX, 33.00, -101.50 | 12 hail days; 636 severe native pixels; max MESH 105.8 mm. |
| `medium_hail` | 261700 | MN, 44.75, -95.00 | 2 hail days; 40 severe native pixels; max MESH 37.3 mm. |
| `low_hail` | 247197 | WA, 47.25, -120.75 | 0 hail days in the bounded window; MRMS coverage present. |
| `hayhurst_reference` | 336544 | TX, 31.75, -104.00 | Hayhurst coordinate containment; 2 hail days; 16 severe native pixels; max MESH 33.3 mm. |

Candidate/provenance artifacts:

```text
data/hazard_conus_grid/hail/pilot_cell_candidates_mrms_202404_202406.csv
data/hazard_conus_grid/hail/pilot_cell_candidates_mrms_202404_202406.json
```

Source notebook:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/01_mrms_daily_mesh.ipynb
```

The paired jupytext source is `01_mrms_daily_mesh.py`.

The selected-cell lock was written after MRMS candidate selection, NOAA/NRI report-side QA, and a lightweight
map / broad-role review. Apr-Jun 2024 MRMS remains a pilot-selection window only, not a final climatology.

Report-side QA artifacts:

```text
data/hazard_conus_grid/hail/pilot_cell_report_qa_hydronos_1996_2024.csv
data/hazard_conus_grid/hail/pilot_cell_report_qa_hydronos_1996_2024.json
```

Report-side QA result, using NOAA Storm Events within 25 miles plus NRI hail fields:

| Role | NOAA reports/yr | NOAA reports in MRMS window | NRI hail rating | QA recommendation |
|---|---:|---:|---|---|
| `high_hail` | 10.690 | 8 | Very High | selected for M1 pilot |
| `medium_hail` | 9.828 | 3 | Relatively Moderate | selected for M1 pilot |
| `low_hail` | 0.310 | 0 | Very Low | selected for M1 pilot |
| `hayhurst_reference` | 2.241 | 1 | Relatively High | selected for M1 pilot |

NOAA reports remain validation evidence only; they are not added as grid events. NRI remains a broad regional
sanity check only; its loss-ratio/EAL fields are not M1 inputs.

## Goal

Choose a small set of benchmark-grid cells that can test the MRMS-to-M1 contract before full CONUS:

| Role | Purpose |
|---|---|
| `high_hail` | Frequent-hail stress case for count, size, and tail behavior. |
| `medium_hail` | Body-case cell where hail exists but is not an extreme hotspot. |
| `low_hail` | Sparse-cell / quiet-control behavior, with no-data ruled out. |
| `hayhurst_reference` | Bridge to the completed hail x solar notebooks. |

The point is not to optimize the cells. The point is to pick a small, explainable set that catches source,
join, threshold, sparse-data, and QA mistakes before full fanout.

## Allowed Inputs

Use only inputs whose role is clear:

| Input | Allowed role |
|---|---|
| Pinned benchmark grid and served CONUS mask | Defines valid `cell_id` universe and joins. |
| MRMS daily MESH | Primary evidence for first-pass hail-day counts and observed MESH sizes. |
| Murillo & Homeyer / documented hail climatology | Broad high/medium/low region anchor and bias context. |
| Storm Events / SPC | Report-side sanity check for candidate cells, not the grid truth. |
| Existing Hayhurst hail notebooks | Source for the Hayhurst point coordinates and comparison context. |

Do **not** use old model outputs, legacy risk layers, unexplained GCS delivery files, or old repo artifacts to
select cells. Those can be historical/cautionary context only after their specific assumptions are validated.

## Minimum Selection Flow

1. Load the pinned 13,085-cell served CONUS mask.
2. Assign the Hayhurst/reference cell from the documented Hayhurst coordinates by benchmark-grid polygon
   containment or an explicitly stated nearest-cell rule.
3. Run a bounded MRMS exploratory scan or use already-documented MRMS evidence to estimate rough severe-hail
   activity by cell.
4. Cross-check candidate regions against broad hail climatology/research and Storm Events reports.
5. Pick one high, one medium, one low, and the Hayhurst/reference cell.
6. Write a small candidate manifest only after the evidence is shown.
7. Lock the selected-cell manifest only after report-side / climatology QA.

## Manifest Contract

The selected-cell manifest is committed under:

```text
data/hazard_conus_grid/hail/
```

Minimum fields:

```text
role
cell_id
lat_center
lon_center
state_abbr
iso_rto
selection_basis
selection_window
selection_metric
selection_metric_value
served_mask_join_status
rationale
qa_notes
```

The manifest is not an M1 output. It is only the input list for the selected-cell MRMS/M1 pilot.

## Acceptance Criteria

- Every selected `cell_id` joins to the served CONUS mask.
- High/medium/low labels are backed by the stated selection evidence.
- The low cell distinguishes true low hail from missing MRMS coverage.
- Hayhurst/reference assignment is reproducible from coordinates.
- No legacy or unexplained risk-output artifact is used as selection evidence.
