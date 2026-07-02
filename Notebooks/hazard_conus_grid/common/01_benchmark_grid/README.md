# 01 — Benchmark Grid Contract

Goal: verify and document the ERA5 0.25° benchmark grid before any hazard data is aggregated to it.

Plan reference:
[`docs/plans/hazard_conus_grid/common/benchmark_grid.md`](../../../../docs/plans/hazard_conus_grid/common/benchmark_grid.md).

## Pinned Source

```text
gs://infrasure-benchmark/sources/grid/era5_us_grid_v2026_1.parquet
```

Source repo:

```text
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/
```

Local sample checked:

```text
/Users/divy/code/work/infrasure_git_codes/benchmark-grid-dataset/data/samples/era5_30km_sample.parquet
```

The validated full grid has:

```text
17,543 rows
cell_id, lat_idx, lon_idx, lat_center, lon_center, geometry
```

The served CONUS hazard/revenue mask has:

```text
13,085 rows
data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

## First Notebook Should Do

1. Re-run the full grid validation when the benchmark-grid delivery changes.
2. Confirm required columns and unique integer `cell_id`.
3. Confirm CRS/geometry behavior.
4. Reproduce or load the CONUS served-cell mask = 13,085 rows.
5. Decide whether the first map surface uses the 13,085 mask or the 13,011 public app-serving subset.

## Current Note

The contributor-spec path `gs://infrasure-benchmark/grid/era5_us_grid_v2026.1.parquet` returned `404` during
validation. Use the `sources/grid/` path above.

## What The Benchmark Grid Contract Asks

```text
benchmark grid asks:
  what is the authoritative cell_id universe?
  are cell_id values unique and stable?
  what CRS and geometry convention applies?
  which cells are in the served CONUS mask?
  what grid artifact path should every hazard adapter use?
```

It does not ask any hazard question yet. It only fixes the spatial contract that later hazard layers must obey.
