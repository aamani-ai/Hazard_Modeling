# Decisions — Coastal × wind (indexes `docs/plans/flood/decisions.md`)

## Unify M3/M4 per-asset once that asset has a co-located all-three site (JD-FL-17, execution rule)
Canonical: the JD-FL-17 block in [`docs/plans/flood/decisions.md`](../../../plans/flood/decisions.md).
- **Wind leads now** — Amazon Wind US East (NC) is the wind all-three site → wind builds **unified single M2/M3** here
  (M2 unified too, beyond M3/M4, because the user asked and it's clean). M4 unifies once the wind leg exists.
- **Solar follows** — coastal × solar keeps its `01`/`02` split until **LA3 West Baton Rouge** (the solar all-three
  site already named in JD-FL-17) is built. The split is principled (a function of site coverage), not drift.

## M4 coastal compound — DONE; the hurricane × wind-farm wind leg already existed (2026-06-21)
Briefly paused thinking we needed to build hurricane × wind-farm first — but on checking, **it was already built and
purpose-built for this exact join**: `data/hurricane/tc_windfarm_m3_damage.parquet` (per-storm, per-subsystem wind DR
at Amazon; its M3 header states the deliverable IS the flood-coastal × wind M4 input). Same site, λ=0.0116, **24 storms
with 0 `event_family_id` mismatch**, same 7-subsystem capex split. So M4 §2c joins surge ↔ wind on `event_family_id`,
per subsystem `combined_DR = max(wind_DR, surge_DR)` (shared = electrical+substation; wind-only = rotor+nacelle;
surge-only = foundation+civil; JD-FL-12), compound-Poisson MC at λ. §2d total flood = inland annual-max + coastal
compound. **MC detail:** one shared storm draw across wind/surge/compound streams (independent draws gave MC noise that
broke `compound ≥ each leg`). The JD-FL-17 *inland-event-ification* blocker (full per-storm three-way Level-1) remains
deferred — inland + coastal are summed as independent streams.

## Per-site gauge — shipped as a notebook-correctness fix (not the deferred production generalization)
The `sfha_bathtub` branch previously used one hardcoded gauge → a 2nd bathtub site (Amazon) would have inherited Green
River's IL hydrology. Fixed with a small hand-picked `GAUGE_BY_SITE` map (Amazon → Pasquotank NC gauge), mirroring how
M0 sites are hand-picked. **The broader production work** (asset-blind `select_method`, *auto* nearest-gauge discovery,
national BLE catalog) **stays deferred to the post-notebooks production phase** — see the JD-FL-19 must-fix list.

## SLOSH in the hazard env — GDAL-decompress, no env change
SLOSH MOM tiles are LZW (need `imagecodecs`, absent from the `hazard` env). The unified wind M2 reads them via a
one-time `gdal_translate` LZW→DEFLATE copy (cached, `raw/slosh/deflate/`), which tifffile reads without imagecodecs.
This let M2 be **one file runnable in the user's env**. Solar's coastal M2 was left on tifffile/base-anaconda (wind
leads; solar untouched).

## Still open (carried from prior sessions, unchanged)
- **Production generalization** (post-notebooks): asset-blind dispatch + auto gauge discovery + national BLE catalog.
- **Pre-commit #5**: de-inline Green River's `flood_area_wkt` (1.8 MB) out of the tracked riverine manifest into `raw/`.
