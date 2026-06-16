# Common — Benchmark Grid

This file pins the grid source for `hazard_conus_grid`.

## Decision

Use the ERA5 native 0.25° benchmark grid from:

```text
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/
```

Core source files:

```text
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/grid/GRID_SPEC.md
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/grid/grid_utils.py
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/contributors/data_contributor_spec.md
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/data/versions.yaml
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/config/storage.yaml
```

## Pinned Artifacts

From the GCS bucket listing and validation in this repo:

| Artifact | Path | Role | Status in this repo |
|---|---|---|---|
| Full grid | `gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet` | full ERA5 US land grid, **17,543 cells** | downloaded and validated locally |
| Sample grid | `gs://infrasure-benchmark/sources/grid/era5_30km_sample.parquet` | 200-cell sample for testing | downloaded and validated locally |
| Local sample copy | `/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/data/samples/era5_30km_sample.parquet` | local contract check | read successfully with repo `.venv` |

The full grid has **17,543 rows**, unique integer `cell_id`, CRS `EPSG:4326`, and these columns:

```text
cell_id, lat_idx, lon_idx, lat_center, lon_center, geometry
```

The older contributor-spec path `gs://infrasure-benchmark/grid/era5_us_grid_v2026.1.parquet` returned `404`
during validation and should be treated as stale.

## Served CONUS Mask

The served CONUS mask is pinned from the current delivery layer, cross-checked against the solar revenue
delivery:

| Mask/source | Rows | Validation |
|---|---:|---|
| `gs://infrasure-benchmark/deliveries/wildfire_risk_layer_conus.parquet` | `13,085` | primary mask source |
| `gs://infrasure-benchmark/deliveries/solar_revenue_layer_conus.parquet` | `13,085` | same `cell_id` set as wildfire |
| `gs://infrasure-benchmark-public/v2026_06/grid_common.parquet` | `13,011` | subset of the 13,085 mask; app-serving filter excludes 74 cells |

Committed mask file:

```text
data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

Manifest:

```text
data/hazard_conus_grid/common/benchmark_grid/benchmark_grid_manifest.json
```

Future hail pilot-cell manifests must prove that selected cells join cleanly to this 13,085-cell served mask.

## Grid Contract

| Item | Contract |
|---|---|
| Grid | ERA5 native 0.25° latitude/longitude grid |
| CRS | WGS84 / EPSG:4326 |
| Geometry | cell polygon |
| Center columns | `lat_center`, `lon_center` |
| Join key | integer `cell_id` |
| Formula | `cell_id = lat_idx * 1440 + lon_idx` |
| Global longitude columns | `1440` |
| Global latitude rows | `720` |
| Full benchmark artifact rows | `17,543` US land cells (CONUS + Alaska) |
| Served CONUS hazard/revenue rows | `13,085` cells, from wildfire risk delivery and solar revenue delivery |
| Public app-serving common rows | `13,011` cells, a subset of the 13,085 mask |
| Scope for this product | valued CONUS cells first; retain compatibility with wider US/Alaska grid where needed |

The `cell_id` is derived from global grid position, not from a regional extract. That is the key reason it is
safe for this product.

## What Still Needs Pinning Before Code

- Whether the hazard layer should retain Alaska/no-data rows or write only valued CONUS rows.
- Why the public app-serving `grid_common` excludes 74 cells from the 13,085 served CONUS mask.
- Whether the grid product should use the full 13,085 hazard/revenue mask or the narrower 13,011 app-serving
  common mask for its first map delivery.

## Important Non-Canonical References

`hazard_analysis/tools/benchmark/` is cautionary history, not a source of truth. It has older ERA5 benchmark
machinery and county/cell mapping files, but its `era5_us_grid.csv` uses string-style cell identifiers such as:

```text
25.00_-81.00
```

Do not use that as the durable join key for this workstream. Do not copy old outputs, assumptions, or methods
from that repo without an explicit validation step. If old artifacts need to be compared, build an explicit
migration/crosswalk to the integer `cell_id`.

`_legacy_wildfire/` is only historical context for past choices and source names. It is not the grid source of
truth, and it should not be used to set CONUS grid assumptions or methods unless the specific item is
independently revalidated in this repo.
