# Common - Gridded Radar Source Qualification

Status: boundary note before gridded-radar scale-out.

This note clarifies what the MYRORSS/MRMS work actually is. It started inside the CONUS-grid hail pilot, but
the core work is not grid-only. It is **gridded radar source qualification**: proving that a raw radar source
can be listed, fetched, cached, decoded, QA'd, batched, retried, and reconciled before any modeling layer
uses it.

That work should serve both:

| Consumer | Target geometry | Example output |
|---|---|---|
| Deep site-specific analysis | real asset footprint, radius, or local region | daily site/region hail evidence |
| CONUS grid analysis | fixed `cell_id` set or full grid | daily cell evidence |

The consumer changes the extraction target. It should not change the source qualification contract.

## Why This Exists

The recent MYRORSS selected-cell work produced more steps than the original site-specific hail x solar
notebooks:

```text
source probe
  -> selected-cell scan
  -> chronological batches
  -> runner / retry
  -> reconciliation gate
```

That can look like over-engineering if viewed as "grid modeling." Viewed correctly, most of it is source
qualification for a raw gridded radar record:

```text
raw gridded radar source
  -> source-qualified daily evidence
  -> site adapter OR grid adapter
  -> M1 hazard layer
  -> asset loss/risk
```

The extra steps are justified only if they become reusable source infrastructure. They should not remain a
hail-grid-only local workflow.

## Notebook Placement Rule

Reusable source qualification belongs with the common peril notebooks:

```text
Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/
```

The old grid location is now only a redirect:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/02_myrorss_reanalysis/
```

Use the grid notebook tree for adapters and product artifacts:

- benchmark-grid joins;
- selected-cell or full-grid target manifests;
- grid M1/M2-M4 interfaces;
- grid-specific QA/reporting.

Do not add new MYRORSS source-understanding notebooks under the grid tree unless the notebook is explicitly
testing a grid-only adapter behavior.

## Layer Boundary

### A. Source Qualification Layer

This layer is source-native and consumer-neutral.

It answers:

```text
Can we trust this radar source enough to extract evidence from it?
```

For MYRORSS/MRMS, this includes:

| Responsibility | Meaning |
|---|---|
| Source inventory | public bucket/source path, product name, record window, date layout |
| Raw-byte access | list, fetch, cache, retry transient failures |
| Decode | parse source files, units, fill values, coordinates, timestamps |
| Batch denominator | explicit date/window/source-file counts |
| Coverage QA | source day listed, no source day, zero-byte files, read failures |
| Metadata validation | no batch is accepted unless its metadata is clean |
| Reconciliation | clean batches become one partial or full source evidence panel |

This layer does **not** decide asset loss, frequency model, MESH bias correction, or tail modeling.

### B. Extraction Adapter Layer

This layer applies the qualified source to a target geometry.

| Adapter | Target | Output key | Example QA |
|---|---|---|---|
| Site adapter | asset footprint, buffer, or homogeneous local collection region | `asset_id`, `date` or `region_id`, `date` | region mask, footprint overlap, site radius, local homogeneity |
| Grid adapter | benchmark grid cells | `cell_id`, `date` | exact-cell evidence, served-mask join, 3x3 neighborhood context |

The current CONUS-grid MYRORSS notebooks prove the **grid adapter** for four selected cells. They do not
replace a site adapter.

### C. Modeling Layer

This layer consumes daily evidence and fits hazard distributions.

It answers:

```text
Given qualified evidence for a target, what is the annual frequency and conditional severity distribution?
```

For hail, the still-open modeling questions are:

- MRMS/MYRORSS source homogeneity;
- MESH bias/de-biasing against reports and climatology;
- hail-day versus connected-event definition;
- sparse-cell pooling/shrinkage;
- EVT/tail treatment for high-return-period losses.

Those are common hail modeling questions. They should not be hidden inside grid-specific batching code.

## What The Current MYRORSS Work Proved

The current MYRORSS source-qualification work with the grid selected-cell adapter proved these facts:

| Proven item | Status |
|---|---|
| MYRORSS public access | proven from `noaa-oar-myrorss-pds` |
| Layout | `YYYY/MM/DD/MESH/00.25/` |
| Record candidate window | current working window `1998-05-01` to `2011-12-31` |
| File encodings | both `.netcdf` and `.netcdf.gz` handled |
| Sparse-grid decode | coordinates reconstructed from attributes + `pixel_x` / `pixel_y` |
| Batch contract | 14-day planned batches, explicit source-file counts |
| Retry/validation | transient S3 `503` caught, rerun cleanly |
| Reconciliation | clean batches 0001-0003 reconciled into a 42-day partial panel |
| Grid adapter | exact `cell_id` and 3x3-neighborhood QA fields produced |

It did **not** prove:

- final MYRORSS climatology;
- MRMS/MYRORSS homogeneity;
- MESH is true hail size;
- final per-cell frequency;
- final EAL/PML/VaR/TVaR;
- site-specific MYRORSS extraction.

## Promotion Gate

A gridded radar source is not allowed into M1 just because some batches ran. Before promotion into either
site-specific or grid M1, document:

| Gate | Required answer |
|---|---|
| Coverage denominator | Which dates/source files/targets were observable, missing, empty, or failed? |
| Target reference base | Is the target a grid `cell_id`, site footprint, buffer, or local region? |
| Exact target vs context | Which fields are model inputs, and which are neighborhood/report QA only? |
| Source-era comparability | How do MRMS and MYRORSS differ in period, product behavior, and reliability? |
| Bias treatment | Is raw MESH used directly, de-biased, or marked unfit for size/severity? |
| Frequency definition | Hail-day, connected event, or other event object? |
| Tail treatment | Is observed size enough, or is EVT/climatology required before PML/VaR/TVaR? |
| Provenance status | Which notebook, data window, version, and QA status produced the artifact? |

If any gate is unresolved, the artifact remains source qualification or adapter proof, not a reportable M1
hazard layer.

## How This Applies To Site-Specific Analysis

For the completed hail x solar site workflow, the old shape was:

```text
MRMS around Hayhurst region
  -> local event catalog
  -> site coupling
  -> damage/loss metrics
```

The common source qualification layer would let the same source handling support:

```text
MYRORSS/MRMS source-qualified daily files
  -> site adapter: asset footprint or local collection region
  -> daily site/region hail evidence
  -> M1 frequency/severity for that site
```

The site adapter should have different QA than the grid adapter:

| Site-specific QA | Why |
|---|---|
| asset footprint or collection region definition | target geometry drives coupling and frequency |
| local homogeneity check | collection-region cancellation depends on homogeneous local regime |
| footprint/region mask validation | no cell-id grid join, but still a spatial reference-base issue |
| report radius interpretation | reports validate/contextualize, not grid or site truth |

So yes: before full CONUS scale-out, it is reasonable to ask whether MYRORSS/MRMS source qualification should
also be used to improve site-specific hail analyses. The answer is **yes**, but through a site adapter, not
by copying grid `cell_id` logic.

## How This Applies To CONUS Grid

For the grid product, the extraction target is the fixed benchmark grid:

```text
MYRORSS/MRMS source-qualified daily files
  -> grid adapter: native pixel to 0.25 degree `cell_id`
  -> daily cell evidence
  -> M1 per-cell frequency/severity
```

Grid-specific logic includes:

- `cell_id = lat_idx * 1440 + lon_idx`;
- served CONUS mask join;
- one row per `cell_id` per date;
- exact-cell event definition;
- 3x3 neighborhood QA as context only;
- future full-CONUS fanout.

That logic should remain grid-specific. It should not be imposed on site-specific analyses.

## GCP Implication

Before moving to GCP, the compute target should be framed as a **common gridded-radar source batch job with
adapter config**, not a hard-coded grid-only job.

Minimum job configuration:

| Config item | Example |
|---|---|
| `source` | `MYRORSS` or `MRMS` |
| `product` | `MESH/00.25` or MRMS daily MESH |
| `date_start`, `date_end` | one batch window |
| `target_type` | `grid_cells`, `site_region`, later `full_grid` |
| `target_manifest` | selected cell CSV, asset footprint/region file, or full grid mask |
| `output_root` | local or GCS path |
| `batch_label` | deterministic date-window label |
| `qa_policy` | fail on read failures, retry transient source errors |

Minimum output contract:

| Output | Meaning |
|---|---|
| day/source manifest | source-file counts, empty files, read failures |
| target daily panel | one row per target/date with evidence and coverage status |
| summary | target-level rollup for the batch |
| metadata JSON | source, target, batch window, QA status, output paths |

This lets the same GCP execution pattern run a site-specific MYRORSS batch or a grid selected-cell batch.

## Recommended Next Step

Do **not** scale MYRORSS into the hail V1 grid layer yet. The active V1 scale target is MRMS-only:

```text
1. Keep source-qualification notebooks in the common hail M0 folder.
2. Keep grid notebooks focused on benchmark-cell adapters and grid products.
3. Use the completed MRMS V1 one-day proof as the local row-contract check.
4. Use the completed seven-day MRMS source-inventory proof as the source-denominator/upload-contract check.
5. Use the completed full MRMS source inventory (`run_id=20260616T165806Z`) as the accepted V1 source-date
   denominator: 2,071 continuous days from `2020-10-14` through `2026-06-15`.
6. Use the completed local small full-grid M0 daily-evidence batch (`run_id=20260616T172929Z`,
   `2024-06-01` to `2024-06-07`) as the row/output-size/runtime proof; the same batch is uploaded to the GCS
   dev prefix.
7. Choose the execution project/runner before large M0 daily-evidence batches.
```

When compute scales, the preferred architecture is still a common source job with adapter config:

```text
source-qualified radar batch
  -> grid adapter OR site adapter
  -> target daily evidence
```

That prevents us from scaling the wrong shape while still preserving momentum on the CONUS grid work. For V1,
that means MRMS full-grid daily evidence. For MYRORSS, it means no more scale-out until the source-promotion
gate is explicitly answered.

## Cross-References

- [`docs/plans/hazard_conus_grid/hail/m0_m1_hazard_layer.md`](../hail/m0_m1_hazard_layer.md)
- [`docs/learning_logs/conus_grid/02_raw_gridded_sources_need_batch_denominators.md`](../../../learning_logs/conus_grid/02_raw_gridded_sources_need_batch_denominators.md)
- [`docs/principles/notebook_work/exploratory_data_notebooks.md`](../../../principles/notebook_work/exploratory_data_notebooks.md)
- [`docs/learning_logs/06_collection_region_size_cancels.md`](../../../learning_logs/06_collection_region_size_cancels.md)
- [`docs/plans/hail/assumptions.md`](../../hail/assumptions.md)
