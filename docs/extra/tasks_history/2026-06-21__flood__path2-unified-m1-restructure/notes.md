# Notes — Flood Path 2 (implementation detail · verification · metrics)

## Final flood notebook tree
```
Notebooks/flood/
  layer0/01_hazard_definition
  m0_input_data/            01_site_screen_and_geometry · 02_depth_grids_and_dem · 03_coastal_site_screen   (solar)
                            04_wind_screening_sweep · 05_wind_site_screen_and_geometry                       (wind)
  m1_catalog/  riverine/01_catalog · pluvial/01_catalog · coastal/01_catalog        (shared, all sites)
  solar/       m2_coupling/{01,02_coastal} · m3_damage/{01,02_coastal} · m4_loss_metrics/{01,02_coastal_compound}
  wind_farm/   m2_coupling/01 · m3_damage/01 · m4_loss_metrics/01                    (M2–M4 only)
```

## Shared M1 manifest schemas (the M2 contract)
- **`flood_m1_catalog_manifest.json`** (riverine): top-level `field` = list of per-site records, each with
  `method` ∈ {`ble_image`,`sfha_bathtub`,`dry`} and `asset`. `ble_image` rows carry `eia` + `rasters`{100,500,10ext};
  `sfha_bathtub` rows carry `slug` + `flood_area_wkt` + `wse_contour`. Plus `flow_frequency` (ble sites, NSS) and
  `gauge` (bathtub sites, Log-Pearson) blocks.
- **`flood_pluvial_m1_field_manifest.json`** (pluvial): `field` = per-site/RP `runoff_m`, tagged `asset`;
  `depth_source.return_periods_yr` + `retention_r_for_M2`.
- **M2 filtering:** solar M2 keeps `method=="ble_image"` (riverine) and `asset=="solar"` (pluvial); wind M2 keeps
  `asset=="wind_farm"` for both. Coastal M2 unchanged.

## Verification metrics (all reproduced, chain re-run green)
| Layer | Site | Key number |
|---|---|---|
| M1 riverine | Hayhurst / Elizabeth | BLE field ~2 / ~3 m/px; NSS Q100=854, Q500~1184 cfs |
| M1 riverine | Green River | sfha_bathtub 60% SFHA; gauge 42-yr peaks, log-skew −1.07, Q100=7055 cfs |
| M1 pluvial | Green River / Shepherds Flat | runoff 100yr 0.1134 m / 0 (PNW, no Atlas 14) |
| M2 solar | Elizabeth | 100yr exposure 0.177 / cond-depth 0.433 m (JD-FL-18 full-res) |
| M2 wind | Green River | 100yr 22 turbines wet (29.7%), substation 0.885 m |
| M3/M4 solar | Elizabeth | EAL **0.163%**; modeled depths inside observed high-water-mark range |
| M3/M4 wind | Green River | riverine 100yr 10.89%→500yr 11.41% TIV; **EAL 1.27%**, 13.2× county avg, NRI-validated |

## Key insights
- **Method choice is a property of the site's data, not the asset** — that's why unifying riverine into one
  method-dispatching notebook is *more* faithful to the convention than splitting by asset.
- **Pluvial unifies trivially** (one method); **riverine is the hard merge** (per-site method). Did pluvial first as
  the pattern-prover.
- **M3 should read M2, never M1** — the wind-M3 RP-list dependency on M1 was a leftover; deriving RPs from the M2
  depth columns removes it cleanly.

## Tooling
- `scripts/regen_ipynb.py` — splits a percent-`.py` on `# %%`, builds nbformat cells, executes via nbclient, writes
  the sibling `.ipynb`. Kernel from `REGEN_KERNEL` env var (default portable `python3`). On this laptop:
  `REGEN_KERNEL=hazard` + the `hazard` conda env python (3.11.14, has tifffile/geopandas/skimage/nbclient).
- HTTP responses are disk-cached under `data/flood/raw/http_cache/` + `raw/ble_field/`, so re-runs are fast/offline.

## Gotchas for the reviewer
- `data/flood/` has many modified manifests/PNGs (regenerated) — expected.
- `.ipynb_checkpoints/` may linger under `m0_input_data/` — gitignored noise.
- Two M1 *data* manifests were deleted (orphaned) — if you see a stale reference anywhere, it's a miss; grep
  `flood_wind_m1_catalog`.
