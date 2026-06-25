# 03 - Storm Events / NRI Candidate QA

Goal: validate the MRMS-derived pilot-cell candidates against independent report-side evidence before the
cells are locked for the selected-cell M1 pilot.

Notebook record:

- `01_candidate_report_qa.ipynb` - executed notebook with QA outputs embedded.
- `01_candidate_report_qa.py` - paired jupytext source.

Inputs:

```text
data/hazard_conus_grid/hail/pilot_cell_candidates_mrms_202404_202406.csv
data/hazard_conus_grid/hail/m0_daily_cell_evidence/mrms_cell_day_evidence_202404_202406.parquet
Hydronos NOAA Storm Events endpoint
Hydronos NRI risk endpoint
```

Outputs:

```text
data/hazard_conus_grid/hail/pilot_cell_report_qa_hydronos_1996_2024.csv
data/hazard_conus_grid/hail/pilot_cell_report_qa_hydronos_1996_2024.json
```

The raw Hydronos response cache is written under `data/hazard_conus_grid/hail/report_qa_raw/` as `.json.gz`
files and remains gitignored.

This notebook is a QA gate, not the M1 layer. NOAA reports and NRI are not used as the per-cell grid truth.
