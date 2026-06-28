# CONUS Grid Learnings

*Transferable lessons from building the fixed-grid hazard product and the common source-qualification work
that feeds it.*

This subfolder holds learnings that matter to the CONUS grid workstream: fixed `cell_id` semantics,
canonical cell-level assets, source-to-grid alignment, full-CONUS fanout, per-cell QA patterns, and the
parts of gridded source qualification that become visible through a grid adapter.

The numbering is local to this thread:

```text
CG-01, CG-02, ...
```

Root learning-log numbers remain the global chronology. This folder keeps the CONUS-grid thread easier to
scan as it grows.

## Index

| # | Title | Type | Sourced from | Applies to |
|---|---|---|---|---|
| [CG-01](01_exact_cell_alignment_and_neighborhood_qa.md) | Exact cell alignment is stricter than hazard nearby | method / anti-pattern | common hail M0 / MYRORSS source qualification with grid selected-cell adapter | any grid hazard layer that maps raw evidence onto fixed cells |
| [CG-02](02_raw_gridded_sources_need_batch_denominators.md) | Raw gridded sources need batch denominators | execution / data-contract | common hail M0 / MYRORSS source qualification with grid selected-cell adapter | gridded hazard sources scanned from raw files |
