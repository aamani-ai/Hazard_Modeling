# Moved — MYRORSS Source Qualification

The MYRORSS notebooks were moved out of the grid notebook tree because this work is **common hail M0
source qualification**, not a CONUS-grid-only build step.

Canonical location:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/
```

Grid-specific selected-cell artifacts still write to:

```text
data/hazard_conus_grid/hail/
```

That is intentional: the notebooks qualify the gridded radar source once, and the selected-cell output is
the current grid adapter proof. Do not add new MYRORSS source-understanding notebooks here; add them under
the common hail M0 folder and document the adapter role in the grid plan.
