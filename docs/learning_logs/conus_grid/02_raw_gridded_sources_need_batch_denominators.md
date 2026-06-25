# Raw Gridded Sources Need Batch Denominators

*Why selected-cell scope does not make a raw gridded source cheap if the source has no spatial index, and
why batch windows are part of the evidence contract.*

**Status:** v1.1 · written 2026-06-16 · **Sourced from:** common hail M0 / MYRORSS source qualification with
CONUS-grid selected-cell adapter proof · **Applies to:** gridded hazard sources that must be scanned from
raw files before they become target evidence.

---

## Where this came from

The MYRORSS source-qualification work widened from a report-guided stress scan to the first chronological
selected-cell grid-adapter batch:

```text
03_selected_cell_full_record_batches.ipynb
  batch: 1998-05-01 to 1998-05-02
  selected cells: 4
  neighborhood QA: 3x3 around each selected cell
  MYRORSS MESH files listed/read: 592
  read failures: 0

first planned batch:
  batch: 1998-05-01 to 1998-05-14
  MYRORSS MESH files listed/read: 4,144
  selected-cell daily rows written: 56
  read failures: 0

first three planned batches:
  window: 1998-05-01 to 1998-06-11
  MYRORSS MESH files listed/read: 12,432
  selected-cell daily rows written: 168
  final read failures: 0 after retrying one transient S3 503

first reconciliation gate:
  accepted planned batches: 0001-0003
  skipped overlapping proof batch
  reconciled panel rows: 168
  missing dates / duplicate keys / read failures: 0
```

Even though the output is only eight selected-cell rows, the scanner still had to list, download/cache, and
decode every MESH file in each source day. MYRORSS sparse files do not expose a cell-level index that says
"this file touches cell 329354." The only honest way to know whether the selected cells have evidence on a
day is to inspect the day.

## The lesson

> **The lesson.** For raw gridded sources without a spatial index, the execution denominator is the source
> file/day batch, not the number of output cells. Make the batch window, source-file count, empty/read-failure
> counts, and raw-cache path first-class artifacts.

This prevents two mistakes:

- assuming "four cells" means "cheap enough to scan the whole record interactively";
- treating missing sparse pixels as zero hazard without proving the source day was actually listed/read.

The practical artifact shape that worked:

| Artifact / field | Meaning |
|---|---|
| `batch_plan` | planned chronological windows across the source era |
| `batch_label`, `batch_start`, `batch_end` | exact execution denominator for a run |
| `day_manifest` | source files listed/read per date, with empty/read-failure counts |
| `coverage_status` | distinguishes no source day, no sparse pixel, sub-severe, severe, and failures |
| `raw_cache_dir` | reproducibility and rerun speed for remote source bytes |
| batch runner metadata validation | prevents transient source/API failures from being mistaken for a clean completed batch |
| reconciliation notebook | converts clean batch artifacts into one partial panel and proves date/cell completeness before scale |

## How this changes the plan

The right widening sequence is:

```text
small chronological proof batch
  -> source-promotion gate: coverage, target base, source-era comparability, bias, frequency, tail
  -> approved wider selected-cell chronological batches
  -> reconcile clean batches into a partial panel
  -> concatenate/reconcile selected-cell MYRORSS-era panel
  -> compare MYRORSS-era behavior with MRMS pilot
  -> only then consider full-CONUS fanout
```

Do not jump from a selected-cell proof to full CONUS just because the output panel is small. For sources like
MYRORSS, the cost lives in raw source inspection.

Operational trigger: if we move from a few batches to many months or the full 357-batch MYRORSS plan, local
manual execution is no longer the right control plane. At that point, move the same batch contract to
GCP/Cloud Run or another managed runner with explicit artifact checks.
