# Exact Cell Alignment Is Stricter Than Hazard Nearby

*Why a report within 25 miles, or a storm in the adjacent cell, is not the same thing as a selected-cell
hazard event - and why neighborhood diagnostics belong in QA, not in the event definition.*

**Status:** v1.0 · written 2026-06-16 · **Sourced from:** hazard CONUS grid · hail M0 / MYRORSS selected-cell scan · **Applies to:** every grid hazard layer that maps raw evidence onto fixed cells.

---

## Where this came from

The hail CONUS-grid pilot selected four 0.25 degree cells, then tested MYRORSS as the longer-record gridded
evidence source:

- `01_myrorss_meet_data.ipynb` proved source access, sparse netCDF decoding, coordinate reconstruction, and
  one-day aggregation to the benchmark `cell_id`.
- `02_selected_cell_record_scan.ipynb` scanned 9 report-guided MYRORSS-era stress dates for the four locked
  selected cells and each selected cell's 3x3 neighborhood.

The bounded selected-cell scan produced an uncomfortable but useful result:

```text
exact selected-cell severe MYRORSS days: 0
Hayhurst 3x3 neighborhood severe MYRORSS days: 1
Hayhurst 3x3 max MESH on 2010-06-16: 37.829437 mm
Hayhurst exact-cell max MESH on 2010-06-16: 16.107588 mm
```

It also flagged 53 zero-byte MYRORSS files on `2006-07-05`, which reinforced that coverage/QA flags need to
travel beside every daily grid row.

## Why it looked fine - the trap

The plausible shortcut is:

> "NOAA reports say hail happened near this cell, and MYRORSS shows hail nearby, so count it for the cell."

That sounds reasonable because the evidence is directionally consistent: a report radius, a storm footprint,
and a 0.25 degree grid cell are all spatially close. But they do not have the same reference base.

- A NOAA 25-mile query answers: "Was there a reported hail observation within a broad radius of the cell
  center?"
- A MYRORSS 3x3 diagnostic answers: "Did the storm show up in the selected cell or an adjacent cell?"
- The grid event definition answers: "Did the selected `cell_id` itself have severe gridded evidence?"

Those are related, but not interchangeable. Treating them as the same silently widens the asset footprint
and inflates frequency for the selected cell. Ignoring them entirely loses the QA signal that a "miss" may be
spatial alignment rather than source failure.

## The lesson

> **The lesson.** For fixed-grid hazard layers, keep **exact-cell evidence** and **nearby-hazard QA** as
> separate fields. The exact `cell_id` is the event definition; neighborhoods and report radii are diagnostics
> that explain alignment, not events that can be counted directly.

`[REF]` The benchmark-grid contract defines a durable integer `cell_id` and a 0.25 degree grid, and the
exploratory-notebook principle says every variable needs its reference base. `[OURS]` The MYRORSS scan added
the practical alignment rule: an exact-cell zero can coexist with nearby severe hail, so the pipeline needs
both `hail_day_flag` and `neighbor_3x3_hail_day_flag` rather than one ambiguous "hail nearby" flag.

The practical shape that worked:

| Field family | Meaning | Model role |
|---|---|---|
| `hail_day_flag` | severe gridded evidence inside the selected `cell_id` | candidate event definition |
| `mesh_max_mm` | exact selected-cell max MESH | candidate severity evidence |
| `neighbor_3x3_hail_day_flag` | severe evidence in selected cell plus adjacent 8 cells | QA / spatial mismatch diagnostic |
| `neighbor_3x3_mesh_max_mm` | nearby max MESH | QA / map-review prompt |
| `report_guided_*` | report-side context used to choose stress dates | context only; not grid truth |
| `coverage_status`, `n_empty_source_files` | source-read / source-availability state | coverage QA; prevents silent zeros |

## How to recognize it next time

The trigger is any fixed grid product where input evidence is not natively the same spatial unit as the
output cell:

- point reports around a cell center;
- storm footprints crossing cell boundaries;
- sparse gridded pixels whose severe core lands just outside the selected cell;
- asset-specific work being generalized to a canonical grid asset;
- raster evidence with no-data/coverage gaps that could be mistaken for true zero hazard.

When the phrase "near the cell" appears, split it into two questions:

1. Did the event hit the exact output unit?
2. If not, did nearby evidence explain why the exact unit missed?

Only the first should feed frequency. The second should feed QA, source alignment, and possible future
exposure-footprint refinement.

## Caveats and limits

- The exact-cell definition is correct for the current comparative grid product, where every cell gets the
  same canonical asset assumption. A later asset-footprint model may legitimately use a larger footprint or a
  different spatial coupling rule, but that should be explicit.
- A 3x3 neighborhood is a QA choice, not a physical law. It is useful because it is small, interpretable, and
  aligned to the grid. It should not become a hidden frequency multiplier.
- Report-guided dates are stress tests. They are not an unbiased sample and cannot estimate annual
  `lambda_cell`.
- A zero exact-cell hit is not automatically "low hazard." It may mean report bias, source mismatch, spatial
  offset, threshold behavior, or coverage/no-data issues.

## Cross-references

- **Principle served:** [`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../principles/notebook_work/exploratory_data_notebooks.md) - every variable needs value, meaning, units/base, and use decision.
- **Grid contract:** [`docs/plans/hazard_conus_grid/common/benchmark_grid.md`](../../plans/hazard_conus_grid/common/benchmark_grid.md).
- **Plan/source role:** [`docs/plans/hazard_conus_grid/hail/m0_m1_hazard_layer.md`](../../plans/hazard_conus_grid/hail/m0_m1_hazard_layer.md).
- **Worked notebooks:** [`01_myrorss_meet_data.ipynb`](../../../Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/01_myrorss_meet_data.ipynb) and [`02_selected_cell_record_scan.ipynb`](../../../Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/02_selected_cell_record_scan.ipynb).
- **Related learning:** [`03_meet_complex_raw_data_from_scratch.md`](../03_meet_complex_raw_data_from_scratch.md) and [`04_two_datasets_one_peril_decompose.md`](../04_two_datasets_one_peril_decompose.md).
