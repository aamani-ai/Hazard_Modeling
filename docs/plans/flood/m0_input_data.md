# M0 — Input data (the plan)

*Phase 1 of the flood build. The deliverable is **understanding**, not a model: meet the raw flood
evidence at every site, field-dictionary every layer, and lock the high sites — before any M1 math.* Per the
per-phase loop ([feature_workflow](../../workflows/feature_workflow.md)): Questions → Research → Detailed Plan →
Execute → Feedback → Document.

> **⚠️ Built state vs original plan.** M0 is **built** as two notebooks — `01_solar_sites` (Hayhurst dry · Elizabeth
> riverine · Discovery coastal · LA3 all-three) and `02_wind_sites` (Green River IL · Shepherds Flat OR · Amazon Wind
> Farm US East NC). The **depth-grid spine is FEMA BLE** (+ SFHA-bathtub for Zone-A wind sites + NLDI→NSS / gauge
> `Q(T)`), settled in **[JD-FL-6](decisions.md)** — which **supersedes [JD-FL-2](decisions.md)'s Fathom plan** (Fathom
> is now only a future commercial swap-in). The "Questions / Detailed plan" sections below record the **original**
> Fathom-spine / two-solar-site planning; lines stated as current fact are corrected or marked superseded.

> **Two sides reminder.** M0 is *Side 1* — meet the data. The model (M1→M4) is *Side 2*. Notebooks land in
> [`../../../Notebooks/flood/m0_input_data/`](../../../Notebooks/flood). Sites + frequency path are settled
> ([JD-FL-6](decisions.md), [JD-FL-3](decisions.md)); M0 *confirms the data exists and is sane* at every site.

---

## Questions (what M0 must resolve before M1)

1. **Which depth-grid product** covers **both** sites with the needed return periods (10/50/100/200/500-yr) and a
   usable resolution? Candidates: **Fathom-US 2.0** (CONUS, fluvial+pluvial, ~30 m / 1 arc-sec) · **FEMA Risk MAP
   depth grids** (only where studies exist) · licensed **First Street**. Confirm the access path — *this is the one
   real data dependency* (see below).
2. **Datum / units / CRS** — depth as *water depth above ground* (m vs ft); DEM vertical datum (NAVD88); grid CRS +
   resolution. Pin these once so M2's `depth − DEM` is unambiguous.
3. **Riverine-only vs riverine + pluvial for the *first* notebook** ([JD-FL-1](decisions.md) revisit) — pluvial adds
   a separate path (NOAA Atlas 14 / radar). Recommend **riverine first**, pluvial as a fast-follow.
4. **Asset geometry** — real plant-boundary polygon (OSM/EIA `powerplants_enriched_v2`) vs the **capacity→radius
   fallback** (`r≈69√MW_DC`) that Hayhurst used for hail/wildfire (it's not in the boundary dataset). Same fallback
   expected here for Hayhurst; the high site may have a true polygon.
5. **DEM source/resolution** for the elevation offset — **USGS 3DEP** (10 m seamless; 1 m where available). Is 10 m
   fine enough vs the asset's pad-to-pad relief? (A21's per-sub-cluster point.)
6. **The null-vs-zero trap** (wildfire's legacy null-BP→0): distinguish *"no depth-grid coverage here"* from
   *"genuinely zero flood depth."* Hayhurst (desert) should read **true zero**, not missing.

## Data sources to meet

| Source | What it is | Role | Access |
|--------|-----------|------|--------|
| **FEMA BLE** *(the built M1 spine)* | riverine RP depth grids (100/500-yr + 10% extent) — local-HEC-RAS quality, free, NAVD88 | **M1 spine** ([JD-FL-6](decisions.md), supersedes JD-FL-2) | public REST (USGS EBFE service) |
| **Fathom-US 2.0** | CONUS fluvial+pluvial **RP depth grids** (~30 m, multiple return periods) | **future commercial swap-in only** — *not* the V1 spine | commercial — optional |
| **FEMA NFHL** | Flood **zones** (SFHA 1% / 0.2%) — national | sanity overlay / scope check | public REST/WMS |
| **FEMA Risk MAP / FRD depth grids** | Depth rasters where Risk MAP studies exist | cross-check vs Fathom where available | public (patchy) |
| **USGS 3DEP** | Bare-earth **DEM** (10 m / 1 m) | **M2 elevation offset** `depth − ground_elev` | public |
| **USGS NWIS** | Annual peak streamflow at gauges | **validation cross-check** (the Log-Pearson III alternative, JD-FL-2) | public |
| **NOAA Atlas 14** | Precip-frequency (pluvial) | only if pluvial enters the first notebook | public |
| **`powerplants_enriched_v2`** (~8.8k EIA) | National solar registry + boundary polygons | **the flood screen** + asset geometry | **dependency** (national set, not the in-repo 66-site portfolio) |

## Detailed plan — two notebooks

**`01_solar_sites`** — *lock the high site + meet the assets.*
1. Load the **national** `powerplants_enriched_v2`; filter utility-scale solar.
2. **Flood-screen** every asset by a flood metric (FEMA SFHA membership / Fathom 100-yr depth at the footprint),
   targeting the **Lower-Mississippi alluvial plain** — pick the standout (wildfire-Matrix method). Report the top-N
   with their screen scores (no silent truncation).
3. Fix the pair: **Hayhurst (low, reused)** + the screened **high site**. Pull geometry — real boundary polygon
   where available, else the capacity→radius circle (note which, per asset).
4. **Known-answer check:** Hayhurst screens ~zero flood; the high site screens materially higher (the low-vs-high
   contrast, like wildfire's ~107× BP).

**`02` (built as `02_wind_sites`)** — *meet the flood hazard.* (Originally planned as a second solar-only "meet the
hazard" notebook; **built** as the wind-site screen + geometry notebook, which also carries the hazard-probe steps.)
1. Fetch the **RP depth grids** (FEMA BLE) clipped to each site; tabulate available **return periods**,
   resolution, **datum/units**, CRS.
2. Fetch the **3DEP DEM** at each site; record vertical datum + resolution.
3. **Field-dictionary** every layer (value · meaning · datum · units · reference base).
4. **Depth-at-asset preview** — compute `depth_grid − DEM` at the footprint for a couple of return periods (a *look*,
   not the M2 model) to confirm signs/magnitudes are sane.
5. Pull **USGS gauges** near the high site (for the later M1 cross-check) and **FEMA NFHL** zones as an overlay.
6. **Known-answer checks:** RP labels map to AEP (100-yr = 1% AEP); Hayhurst depths ≈ 0 at all RPs (true zero, not
   null — the null-vs-zero trap); high-site depth rises with return period (monotone).

## Verification checklist (basics-spot-on)

- [ ] Depth-grid product confirmed to **cover both sites** at the needed return periods + resolution.
- [ ] Datum / units / CRS pinned and consistent across depth grid + DEM.
- [ ] Hayhurst reads **genuine zero** flood (not missing) — null-vs-zero distinguished.
- [ ] High site shows **material, monotone-in-RP** depth — the low-vs-high contrast is real.
- [ ] `depth − DEM` preview has sane signs/magnitudes.
- [ ] Asset geometry recorded per site (true polygon vs radius fallback).
- [ ] Every layer field-dictionaried; sources + licenses logged in [`01_references.md`](01_references.md).

## Dependencies (external data)

Two inputs aren't in-repo: (1) the **national** `powerplants_enriched_v2` registry (the in-repo
`site_registry.csv` is the 66-site AIG portfolio — no MS/LA), and (2) a commercial depth-grid product (Fathom-US 2.0).
**The depth dependency is now resolved with public data:** the built spine is **FEMA BLE** (+ SFHA-bathtub + NLDI→NSS /
gauge `Q(T)`, JD-FL-6), with EIA-860 for the screen and 3DEP DEM for context. So no commercial feed is required. Fathom
/ First Street remain an **optional future swap-in**, not a gate.

## On greenlight

Once the depth-grid product + national registry are confirmed: create
[`../../../Notebooks/flood/m0_input_data/`](../../../Notebooks/flood) and build `01` first (screen → lock the high
site), then `02` (meet the hazard). Document outcomes back here + in [`01_references.md`](01_references.md); fold any
surprises into [`assumptions.md`](assumptions.md).
