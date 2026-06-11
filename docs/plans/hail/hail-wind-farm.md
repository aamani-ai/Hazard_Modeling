# Plan: Hail × Wind Farm Notebook Cell

> **Status:** planning · **Date:** 2026-06-11. Build this as a notebook-first architecture showcase that
> reuses the shared hail catalog and demonstrates per-turbine point-cloud coupling. Do **not** treat the
> first result as platform-ready production risk.

## Goal

Add the next asset cell under the existing hail peril:

```text
Notebooks/hail/
  m0_input_data/     shared hail evidence
  m1_catalog/        shared hail event catalog
  solar/             built
  wind/              planned: hail × onshore wind farm
```

The purpose is to prove the architecture generalizes:

```text
hail × solar      -> dense areal polygon -> Minkowski areal hit-or-miss
hail × wind farm  -> sparse turbine points -> per-turbine hit-or-miss
```

## Scope

Reuse the existing M0/M1 hail catalog. Start new work at M2.

Build a `Notebooks/hail/wind/` notebook set:

```text
wind/
  README.md
  m2_coupling/01_coupling.py + .ipynb
  m3_damage/01_damage.py + .ipynb
  m4_loss_metrics/01_loss_metrics.py + .ipynb
```

This is a **notebook demonstration** until the turbine coordinates, value allocation, and damage curve are
source-locked.

## Modeling Approach

### M2 — Per-Turbine Hail Coupling

Use the M1 hail footprint polygons and turbine coordinates.

```text
for each hail event:
    for each turbine point:
        hit = turbine point inside event footprint polygon
    n_hit_turbines = sum(hit)
    hit_fraction = n_hit_turbines / n_turbines
```

Recommended v1 choices:

- Model each turbine as a point sub-asset.
- Do not use the wind-farm lease / bounding polygon as the primary exposure geometry.
- Carry event `peak_intensity_in` from M1 as the v1 hail intensity for all hit turbines.
- If the raster is available in the M1 bundle, add a later refinement to sample local MESH at each hit
  turbine instead of using the region/event peak.

### M3 — Turbine Hail Damage

Use a provisional turbine-specific damage representation, not the solar PV damage curve.

Recommended v1 choices:

- Start with turbines only.
- Allocate value equally per turbine unless turbine-specific values are available.
- Keep substations, collection systems, O&M buildings, and other balance-of-plant assets out of v1 unless
  they have known coordinates and separate vulnerability assumptions.
- Do not model unknown non-turbine assets as "one more turbine."

If no defensible hail-on-turbine curve is available, keep M3 explicitly experimental and focus the notebook
on M2 geometry.

### M4 — Farm-Level Loss Metrics

Aggregate turbine-level losses to event and annual farm losses using the same frame rules as hail × solar:

- event loss = sum of hit-turbine conditional losses;
- AEP = annual aggregate loss;
- OEP = annual max single-event loss;
- no `p_hit * loss` shortcut inside event losses;
- report all results as experimental until M3 is source-locked.

## Required Inputs

- M1 hail catalog: `data/hail/hayhurst_hail_m1_catalog.parquet`.
- Wind farm asset record: name, capacity, value/TIV basis, and turbine count.
- Turbine lat/lon coordinates.
- Value allocation: equal per turbine for v1, turbine-specific if available.
- Hail damage curve or placeholder for turbine/blade hail damage.

## Outputs

Use separate wind-farm output names so solar artifacts remain untouched:

```text
data/hail/<asset_slug>_wind_hail_m2_coupled.parquet
data/hail/<asset_slug>_wind_hail_m2_summary.json
data/hail/<asset_slug>_wind_hail_m3_damage.parquet
data/hail/<asset_slug>_wind_hail_m3_summary.json
data/hail/<asset_slug>_wind_hail_m4_annual_vectors.parquet
data/hail/<asset_slug>_wind_hail_m4_metrics.json
```

## Success Criteria

- M0/M1 are reused exactly; no duplicated hail catalog.
- M2 shows a clear per-turbine intersection table and map.
- The notebook contrasts wind-farm point-cloud coupling against the rejected bounding-polygon shortcut.
- M3 states whether turbine hail vulnerability is curated or placeholder.
- M4 metrics are labeled as experimental unless all asset and damage inputs are source-locked.

## Open Questions

- Which wind farm is the worked asset, and where are its turbine coordinates?
- Do we have a credible source for turbine/blade hail vulnerability, or is this M2-only until then?
- Should non-turbine assets be excluded in v1 or included as separately labeled approximate points?
- Should local MESH be sampled at each turbine in v1, or is event peak sufficient for the first notebook?

Discussion note: [`discussion/hail-wind-farm-exposure-model.md`](discussion/hail-wind-farm-exposure-model.md).
