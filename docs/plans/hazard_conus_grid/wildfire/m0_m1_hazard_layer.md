# Wildfire — M0/M1 Hazard Layer Plan

Goal: build a reusable per-cell wildfire hazard-distribution layer for the benchmark grid.

## Target Layer

One row per `cell_id` that captures annual burn likelihood and conditional intensity/severity distribution.

The layer should answer:

```text
For this 0.25° cell, what is the annual burn probability/frequency,
and what is the flame-length or intensity distribution conditional on burning?
```

## Source Roles

| Source | Role |
|---|---|
| FSim native probabilistic wildfire output | Preferred severity spine when using BP + FLP1-6 consistently. |
| WRC | Useful public/service access and validation context; must respect vintage/product caveats. |
| Existing wildfire notebooks | Reference implementation for source handling and data caveats. |
| `_legacy_wildfire/` | Historical/cautionary context only; do not copy assumptions or methods without revalidation. |

## Why Wildfire Is Easier Than Hail

FSim/WRC already ran the wildfire simulation and publishes model-integrated spatial fields. For CONUS grid
work, that means M1 starts from an existing hazard field and focuses on consistent aggregation to `cell_id`.

Hail starts from raw radar-estimated MESH grids and must create event frequency, size distribution, sparse-cell
rules, and validation/de-biasing itself.

## Build Stages

1. Pin source product/vintage and benchmark grid.
2. Aggregate burn probability and severity/intensity fields to `cell_id`.
3. Preserve source caveats in provenance.
4. Write M1 wildfire hazard layer.
5. Run canonical solar and wind M2-M4 fanout.
