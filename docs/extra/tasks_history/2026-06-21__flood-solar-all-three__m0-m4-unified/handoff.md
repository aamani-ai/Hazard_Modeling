# Handoff — Solar all-three (LA3): M0→M4 unified, all three sub-perils (2026-06-21)

> **Read me first.** Built **LA3 West Baton Rouge Solar (EIA 61646, LA)** as the **all-three solar site** — the solar
> analogue of Amazon (wind) — and **unified solar's M2/M3/M4 into one notebook each** (collapsed `01`+`02_coastal`).
> Both assets are now on the unified form, each triggered by its own all-three site (JD-FL-17 "solar follows" =
> realised). Existing sites preserved (Elizabeth 0.163%, Discovery 0.338%). Nothing committed (flood branch held).
>
> **LA3 result:** total flood **0.761%** of TIV = inland 0.653 (riverine, BLE Lower Grand) + coastal compound 0.107
> (surge × hurricane wind). PML100 7.0% · PML500 12.2%.

## 60-second summary

- **Site:** LA3 West Baton Rouge (LA, 50 MW). All-three verified live: **riverine Zone A / FEMA BLE "Lower Grand"**
  (→ `ble_image` + NSS densification, Q100=2610) · **coastal Cat-3** SLOSH (11 RAFT storms, λ=0.0173; Gulf surge up the
  Mississippi, Cat-5 footprint 14.5 ft — deeper than Discovery's 12.4) · **pluvial** Atlas-14 (100yr 0.25 m).
- **M0** — `m0_input_data/07_all_three_solar_site`: registers LA3 in **three** rosters (`flood_m0_sites.json` inland,
  `flood_m0_dem_context.json` boundary_wkt for BLE, `flood_coastal_m0_sites.json` coastal). Run after `01`/`02`/`03`.
- **Hurricane × solar extended to LA3** (the compound wind leg): added LA3 to `data/hurricane/tc_m0_sites.json`,
  re-ran hurricane **M1/M2/M3** → LA3 in `tc_m3_damage.parquet` (51 storms, gust to 140 mph). Discovery/Everglades
  preserved.
- **Flood M1** — riverine/pluvial/coastal all auto-pick-up LA3 from the rosters (no M1 code change beyond extending the
  NSS-densification condition to `all-three` roles).
- **Solar M2/M3/M4 UNIFIED** — one file each (riverine + pluvial + coastal). SLOSH read via GDAL-decompress so it runs
  in the hazard env. `02_coastal_*` deleted. The MW dict now reads both rosters (no hardcode).

## The general engine (each site carries whatever it has — absent = 0)

| Site | inland (max riv,pluv) | coastal compound | total EAL | note |
|---|---|---|---|---|
| **LA3** | 0.653 | 0.107 | **0.761%** | all-three |
| Discovery | 0 | 0.338 | 0.338% | coastal-only |
| Elizabeth | 0.163 | 0 | **0.163%** | inland-only (preserved) |
| Hayhurst | 0.030 | 0 | 0.030% | dry baseline |

Total flood = inland annual-max **+** coastal compound-Poisson (independent streams; full per-storm three-way Level-1
still deferred — JD-FL-17 inland-event-ify blocker).

## Repro (hazard env)

```bash
PY=/Users/limjunga/opt/anaconda3/envs/hazard/bin/python
cd Notebooks/flood/m0_input_data && $PY 07_all_three_solar_site.py     # register LA3
cd ../../hurricane/m1_catalog && $PY 01_event_catalog.py        # then solar/m2,m3 — LA3 gust/damage
cd ../../flood/m1_catalog/riverine && $PY 01_catalog.py                 # + pluvial, coastal — LA3 picked up
cd ../../solar/m2_coupling && $PY 01_coupling.py                        # UNIFIED (riverine+pluvial+coastal)
cd ../m3_damage && $PY 01_damage.py
cd ../m4_loss_metrics && $PY 01_loss_metrics.py                          # LA3 total 0.761%; Elizabeth 0.163% preserved
```
Regen .ipynb: `REGEN_KERNEL=hazard $PY scripts/regen_ipynb.py <file.py …>`.

## Don't-trip-on-these

- **Hurricane peril was touched** — LA3 added to `tc_m0_sites.json` and hurricane M1/M2/M3 re-run. Existing hurricane
  sites (Discovery/Everglades/Hayhurst) reproduce; if you re-run hurricane, keep LA3 in `tc_m0_sites.json`.
- TIV is consistent across legs ($1,483,000/MW both flood + hurricane), so the compound combine scales one TIV.
- `vectors` dict in solar M4 has `<site>` + `<site>__total` keys; the persist loop strips `__total`.
- Solar's disjoint Elizabeth (inland) / Discovery (coastal) remain as single-peril reference sites — that's correct,
  not a gap. LA3 is the combine site.
- Nothing committed. Pre-commit: the #5 manifest de-inline already done (bathtub polygons → gitignored raw/).
