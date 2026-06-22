# Notes — Coastal × wind (detail · metrics · env)

## The all-three site search (scout)
`scripts/explore_coastal_wind_site.py` — pulls USWTDB by coastal bbox (county filter fails: `t_county` has a
" County" suffix), groups into projects, tests surge onset (NOAA CFEM `identify`) + per-turbine NFHL zone mix
(riverine A/AE vs coastal V/VE). All-three = surge-exposed AND has riverine Zone-A turbines (pluvial automatic outside
the PNW). Result, full US onshore coastal-wind belt:

| site | region | surge-exposed | riverine Zone A | turbines |
|---|---|---|---|---|
| **Amazon Wind US East** | Perquimans Co **NC** | **79/104 = 76%** (Cat-3) | 11/104 = 11% | 104 / 208 MW |
| Peyton Creek | Matagorda Co TX | 2/48 = 4% (Cat-3) | 8/48 = 17% | 48 / 151 MW |

(Single-turbine municipal installs like Crisfield WWTP were filtered out.) Amazon wins — the Albemarle Sound funnels
hurricane surge inland, so most of the farm sits in the surge zone despite being "onshore."

## Validation metrics (all reproduced / new)
| layer | result |
|---|---|
| M0 | Amazon: 76% surge (Cat-3) · 11% Zone A · collector 230 kV in-hull, surge-exposed · $291M TIV |
| M1 riverine | Amazon gauge 0204382800 (Pasquotank, 30 peaks, log-skew 0.96, Q100=2946); Green River unchanged (Q100=7055) |
| M1 pluvial | Amazon 100yr runoff 0.18 m (auto-picked up) |
| M1 coastal | Amazon 24 storms (cats 1:21,2:2,3:1), λ=0.0116; **Discovery 117 preserved**, λ=0.0289 |
| M2 coastal | Cat-3 → 64 turbines flooded (61.5%, pad-gated), substation 0.307 m; Cat-4 all turbines; Cat-5 +substation |
| M2 riverine | Amazon 13 turbines @100yr (12.5%); Green River unchanged (22 @100yr, sub 0.885 m) |
| M3 coastal | Amazon Cat-3 5.98% (turb 4.25% + sub 1.73%) → Cat-4 19.33% → Cat-5 23.22% of TIV |
| M3 riverine | Green River 100yr 10.89% → 500yr 11.41% of TIV (unchanged) |
| M4 inland | Green River EAL 1.276% (NRI 13.2× county avg, freq ≈ annual-max); Amazon inland computed |

**Asset contrast:** Green River = riverine-dominated; Amazon = coastal-dominated (but surge is spatially broad and
*temporally rare* — needs Cat-3+, ~1/2000 yr at this NC latitude; the catalog maxes at Cat-3 = 1 storm).

## Env split (important)
- **hazard env** (`/Users/limjunga/opt/anaconda3/envs/hazard/bin/python`, py3.11) — runs everything *now*, including
  the unified wind M2, because SLOSH is read via GDAL-decompress (gdal_translate is present in the env).
- **base anaconda** (`/Users/limjunga/opt/anaconda3/bin/python`, py3.9, has `imagecodecs`) — still needed for **solar's**
  coastal M2 (`02_coastal_coupling`), which reads SLOSH with tifffile directly. Unchanged this session.
- Regen: `REGEN_KERNEL=hazard <hazard-python> scripts/regen_ipynb.py <file.py ...>` (jupytext not installed).

## Key manifest shapes (for the M4 resume)
- `flood_m1_catalog_manifest.json` (riverine) — `field` rows method-tagged (`ble_image`/`sfha_bathtub`/`dry`),
  `gauges` map (slug→gauge), each bathtub field row also has `rec["gauge"]`.
- `flood_coastal_m1_catalog_manifest.json` — `sites` list (both assets, exposed flag) + back-compat `high_site`
  (Discovery) / `baseline_site` (Hayhurst).
- `flood_wind_m3_damage_manifest.json` — `rp_rows` (riverine+pluvial), **`coastal_event_rows`** (per-storm: storm_ID,
  event_family_id, category, cond_loss_frac_tiv, …), `sites` (back-compat = rp_rows).
- `amazon_wind_us_east_flood_wind_m2_coastal_coupling.parquet` — per-storm node-flood summary (event_family_id-keyed).

## How the M4 resume will work (once hurricane × wind-farm exists)
Mirror solar's `02_coastal_compound`: join the surge per-storm loss (above) to hurricane × wind-farm's per-storm,
per-subsystem wind DR on `event_family_id`; per subsystem `combined_DR = max(wind_DR, surge_DR)` on shared subsystems
(additive on single-peril ones); compound-Poisson MC at λ → EAL/PML. Then fold into the unified wind M4 alongside the
inland annual-max engine.
