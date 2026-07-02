# 04 - Selected Pilot-Cell Lock

Goal: turn the reviewed MRMS-derived candidate cells into the small selected-cell manifest consumed by the
hail M1 pilot.

Notebook record:

- `01_lock_selected_cells.ipynb` - executed notebook with acceptance checks embedded.
- `01_lock_selected_cells.py` - paired jupytext source.

Inputs:

```text
data/hazard_conus_grid/hail/pilot_cell_candidates_mrms_202404_202406.csv
data/hazard_conus_grid/hail/pilot_cell_report_qa_hydronos_1996_2024.csv
data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

Outputs:

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.json
```

This lock is only for the selected-cell M1 pilot. It does not create the hail M1 hazard layer and it does
not authorize full-CONUS fanout.

## What The Pilot-Cell Lock Asks

```text
pilot-cell lock asks:
  which candidate cells are accepted for the small M1 pilot?
  what role does each selected cell play?
  do all selected cells join to the benchmark grid?
  are the selected cells saved in one manifest that M1 can consume?
```

It does not ask whether the full-CONUS grid is ready. It only freezes the tiny pilot input list.
