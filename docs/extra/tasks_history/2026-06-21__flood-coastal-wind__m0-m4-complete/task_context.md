# Task context — Coastal × wind (M0→M3 built, M4 paused)

## Objective
Add the **coastal `[C]`** sub-peril to **flood × wind-farm**, at a site that has **all three** flood sub-perils
(riverine + pluvial + coastal), so the wind cell's **M3/M4 unify into one notebook each** (realizing JD-FL-17, which
was waiting for a co-located all-three site). Reuse solar's exact coastal methods; wind leads, solar unifies later.

## Background / how we got here
- Followed the Path 2 (JD-FL-19) refactor session. Flood's M1 is now unified per sub-peril over both assets; M0/M1
  shared at top; M2–M4 per asset.
- User wanted the wind cell's M3/M4 to be ONE notebook each (not solar's `01`+`02_coastal` split). That's only
  meaningful with a co-located all-three site → had to find one.

## What we did
1. **Scout (`scripts/explore_coastal_wind_site.py`)** — surveyed US onshore coastal wind (S/C Texas, upper TX/SW LA,
   NE North Carolina, VA) for surge ∩ riverine-SFHA (pluvial is automatic outside the PNW). Nationally only two real
   farms have all three: **Amazon Wind US East (NC)** and Peyton Creek (TX). Amazon is far stronger (76% surge-exposed
   via the Albemarle funnel vs Peyton's 4%).
2. **M0** — `06_coastal_wind_site_screen`: USWTDB cloud + hull + CFEM surge + NFHL SFHA + collector substation (OSM
   `substation=generation` in-hull, 230 kV, surge-exposed) + TIV; per-turbine R+C tags; **idempotently appended Amazon
   to `flood_wind_m0_sites.json`** (run after `05`; now 3 wind sites).
3. **M1** (all three unified/asset-aware):
   - *pluvial* — unified M1 **auto-picked up Amazon** (Atlas-14 NC; no code change), 100yr runoff 0.18 m.
   - *riverine* — Amazon routes to `sfha_bathtub`; gave it a **per-site NC gauge** (Pasquotank 0204382800, 30 peaks,
     Q100=2946) via a `GAUGE_BY_SITE` map. **Green River unchanged** (05447000, Q100=7055). Manifest now carries
     per-site `gauges` + `rec["gauge"]`.
   - *coastal* — rewrote `m1_catalog/coastal/01_catalog` to read coastal-exposed sites from **both** assets; Amazon 24
     storms (λ=0.0116). **Kept `high_site`/`baseline_site` (Discovery/Hayhurst)** so the validated solar coastal M2 is
     byte-for-byte unaffected (verified: Discovery still 117 storms, SLOSH ladder unchanged).
4. **M2** — merged `02_coastal_coupling` into `01_coupling` → **one unified M2** (riverine + pluvial + coastal,
   per-node). Switched the SLOSH read to **GDAL-decompress (LZW→DEFLATE, cached)** so the whole file runs in the
   **hazard env** (no imagecodecs). Per-site gauge read moved inside the riverine loop. Deleted `02`.
5. **M3** — unified `01_damage` to run the **source-agnostic** curve over all three sub-perils; coastal added as
   per-storm (event-based) loss. Coastal is Amazon's material sub-peril (Cat-3 5.98% → Cat-5 23.22% of TIV).
6. **M4** — **UNIFIED, all three.** Inland (riverine+pluvial) annual-max + coastal **compound combine** (surge ×
   hurricane wind, per-subsystem `max(wind_DR, surge_DR)` on `event_family_id`, JD-FL-12) + total flood. The hurricane ×
   wind-farm wind leg (`data/hurricane/tc_windfarm_m3_damage.parquet`) **already existed, purpose-built** for this join
   (same site / λ / 24 storms / capex split, 0 efid mismatch) — so the pause wasn't actually needed.

## Status
✅ **Coastal × wind COMPLETE, M0→M4, all three sub-perils, validated.** Amazon coastal compound EAL 0.013% / total
flood 0.069%; Green River 1.276% (inland, NRI-validated). Full per-storm three-way still deferred (JD-FL-17). **Not
committed.**

## Files touched
```
NEW   Notebooks/flood/m0_input_data/06_coastal_wind_site_screen.{py,ipynb}
NEW   scripts/explore_coastal_wind_site.py                      (site scout, one-off)
EDIT  Notebooks/flood/m1_catalog/riverine/01_catalog.{py,ipynb} (per-site gauge: GAUGE_BY_SITE)
RWRT  Notebooks/flood/m1_catalog/coastal/01_catalog.{py,ipynb}  (unified asset-aware; back-compat high_site)
re-ran Notebooks/flood/m1_catalog/pluvial/01_catalog.*          (auto-picked up Amazon)
EDIT  Notebooks/flood/wind_farm/m2_coupling/01_coupling.{py,ipynb} (UNIFIED + coastal + GDAL SLOSH + per-site gauge)
DEL   Notebooks/flood/wind_farm/m2_coupling/02_coastal_coupling.*  (merged into 01)
EDIT  Notebooks/flood/wind_farm/m3_damage/01_damage.{py,ipynb}   (UNIFIED + coastal)
EDIT  docs/plans/flood/decisions.md                              (JD-FL-17: unify rule, coastal×wind status, blocker)
DATA  data/flood/: flood_wind_m0_sites.json (3 sites); flood_m1_catalog_manifest.json (5 sites, per-site gauges);
      flood_pluvial_m1_field_manifest.json (5 sites); flood_coastal_m1_catalog_manifest.json (unified);
      amazon_wind_us_east_* (geometry, coastal_m1_catalog, m2 riverine/pluvial/coastal depths + coastal_coupling);
      flood_wind_m2_coupling_manifest.json (+coastal); flood_wind_m3_damage_manifest.json (+coastal_event_rows);
      raw/slosh/deflate/cat{1..5}_deflate.tif (new SLOSH cache); raw/gauge_QT_0204382800.json
```

## Files touched (M4, added this session)
```
EDIT  Notebooks/flood/wind_farm/m4_loss_metrics/01_loss_metrics.{py,ipynb}  (UNIFIED — +§2c coastal compound, §2d total)
DATA  data/flood/flood_wind_m4_metrics_manifest.json (+coastal_compound, +total_flood); *_m4_annual_vectors_total.parquet
READ  data/hurricane/tc_windfarm_m3_damage.parquet  (the wind leg — pre-existing, joined on event_family_id)
```

## Next steps
1. **Flood is now complete for both assets** (solar M0→M4 incl. coastal; wind M0→M4 incl. coastal compound). Remaining
   before the eventual commit: the pre-commit **#5 manifest de-inline** (Green River `flood_area_wkt` out of the tracked
   riverine manifest); optionally a final full-chain re-run.
2. **Deferred (own efforts):** JD-FL-17 full per-storm three-way Level-1 combine (needs inland event-ification);
   the production generalization (asset-blind dispatch, auto gauge discovery, national BLE catalog); solar M3/M4 unify
   when LA3 West Baton Rouge is built.
