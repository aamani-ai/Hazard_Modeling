# Flood — peril overview

The **flood** hazard, organized `peril → asset`. This folder holds the **shared flood catalog** (asset-independent);
each per-asset pipeline (coupling → damage → loss) lives in its asset subfolder. Driven by the plan in
[`../../docs/plans/flood/`](../../docs/plans/flood/README.md). Kernel: `.venv` (`hazard_modeling`).

> **Flood = ONE peril, a FAMILY of THREE sub-perils** — **riverine [R]** (river-network overflow, the classic
> floodplain), **pluvial / flash [F]** (intense-rainfall surface ponding, *often outside the floodplain* — the "blind
> spot"), and **coastal / surge [C]** (storm-surge inundation at the coast). They share **one damage driver — inundation
> depth (ft above ground)** — but each has a **different magnitude basis** and a **different data source** (the reason
> flood needs a layer-0). Riverine and pluvial are **indexed by annual return period** (10–500-yr, annual-maximum
> frame); coastal surge is **event-based, indexed by hurricane category** (per storm). **Coastal is cross-linked to the
> hurricane peril** via the `event_family_id` key (one surge source, counted once): it consumes the hurricane RAFT
> catalog, adds a SLOSH-MOM surge layer, and combines the storm's **surge + wind** at M4 without double-counting
> (JD-FL-12/14/15/16).

```
flood/
  layer0/          ← the hazard definition / orientation (depth driver · 3 sub-perils · magnitude+source per [R/F/C])  ┐ the PERIL
  m0_input_data/   ← raw evidence, BOTH assets: 01_solar_sites (screen+geometry+depth+coastal+all-three) · 02_wind_sites (sweep+geometry+coastal+all-three)  │ (asset-
  m1_catalog/      ← per-SUB-PERIL FIELD, ALL sites of both assets: riverine/ (method-per-site: ble_image / sfha_bathtub / dry) · pluvial/ (Atlas 14→SCS-CN) · coastal/ (SLOSH-MOM + RAFT + HURDAT2)  ┘ independent)
  solar/           ← flood × SOLAR — M2 coupling · M3 damage · M4 loss & metrics (one notebook each, all three sub-perils)  ✅ built end-to-end
  wind_farm/       ← flood × WIND FARM — M2 per-node coupling · M3 greenfield curve · M4 loss (one notebook each, all three sub-perils)  ✅ built end-to-end
```

> **Convention (JD-FL-19):** `m0_input_data/` and `m1_catalog/` are **shared at the peril level over both assets** (one
> M1 notebook per sub-peril, processing *every* site of both assets); the asset only matters at **M2–M4**, which live in
> `solar/` and `wind_farm/`. M1 = the asset-independent hazard **field**; M2 = the coupling that samples it at the asset
> (areal footprint for solar, per-node for wind). Riverine's method is chosen **per site by data availability** (BLE
> depth grid → `ble_image`; Zone-A only → `sfha_bathtub`; mapped-dry → `dry`), not by asset.

> **New here?** Read the orientation in **[`layer0/`](layer0/README.md)** (what we measure per sub-peril, and exactly
> where each number comes from), skim the shared catalog below (M0 → M1), then open **[`solar/`](solar/README.md)** for
> the first full M2 → M3 → M4 worked example and the headline risk numbers.

---

## Layer-0 — the hazard definition / orientation  ·  [📖 folder README](layer0/README.md)

Hail/wildfire inherited a self-evident event; wind had to **author** one. Flood is a third case — its events *are*
inherited (one product per sub-peril), but it is a **fragmented family**, so layer-0 **orients** it: the **magnitude
observable + exact source, per sub-peril**, and the **two thresholds** the rest of the pipeline hangs on — here on the
**depth** axis:

| | Threshold | Governs | Lives in |
|---|---|---|---|
| **flood event basis** | the year's worst flood, indexed by AEP (10 / 100 / 500-yr depth); coastal by hurricane category per storm | what the **catalog counts** (annual-max loss inland; compound-Poisson coastal) | M1 |
| **asset damage-onset depth** | component pad / `x0` height (inverter ≈ 0.75 ft · turbine pad ≈ 0.30 m) | where the **damage curve leaves zero** | M3 |

Far apart → the depth-damage curve is **anchored** (`DR(depth ≤ onset) ≈ 0`; most shallow flooding barely scratches
well-sited equipment). Notebook: `layer0/01_hazard_definition` ✅.

## The shared hazard catalog (M0 → M1) — built once, reused by every asset

The flood hazard over a site is the same regardless of what sits on it, so M0/M1 live at the **peril** level over
**both assets** — each M1 notebook processes every site, and only M2–M4 specialize per asset (JD-FL-19).

### M0 — input data  ·  *(both assets; field-dictionary per `docs/principles/notebook_work/`)*

| Notebook | Source | What / grain | Status |
|---|---|---|---|
| `m0_input_data/01_solar_sites` | **EIA-860** + FEMA **NFHL**/**BLE** + USGS **3DEP** + NOAA **CFEM** + **OSM** | locks **all solar flood sites**: national SFHA screen → Hayhurst (dry) + Elizabeth (riverine); DEM/geometry/zone context; Gulf/Atlantic surge → Discovery (coastal); register LA3 (all-three) | ✅ built |
| `m0_input_data/02_wind_sites` | **USWTDB** + FEMA **NFHL** + **OSM**/HIFLD + NOAA **CFEM** | locks **all wind flood sites**: SFHA-fraction sweep → Green River + Shepherds Flat (dry), per-turbine geometry + collector substation + TIV; coastal → Amazon (all-three) | ✅ built |

### M1 — event catalog + frequency  ·  [📖 folder README](m1_catalog/README.md)

**Flood forks the catalog by *sub-peril* (at M1)** — different data per sub-peril, one shared depth driver
(JD-FL-10). *(Contrast: convective-wind forks at **M2** — same catalog, two couplings. Flood diverges earlier, at the
**data**, then re-converges at depth→damage.)* Each sub-peril is **one notebook over all sites of both assets**; M1
emits the asset-independent **field** (no footprint/per-node reduction — that is M2's job, JD-FL-19).

| | **Riverine [R]** | **Pluvial / flash [F]** | **Coastal / surge [C]** |
|---|---|---|---|
| **magnitude** | flood depth (ft above ground) at return period | flood depth (ft above ground) at return period | surge depth (ft above ground) per storm, by hurricane category |
| **basis** | annual-maximum, AEP-indexed (10–500-yr) | annual-maximum, AEP-indexed (10–500-yr) | event-based, compound-Poisson (λ × category mix) |
| **source** | **method-per-site** (by data availability, JD-FL-6): `ble_image` = FEMA **BLE** depth grid at native resolution (JD-FL-18); `sfha_bathtub` = NFHL 1% flood-area + **3DEP** boundary WSE + per-site **USGS NWIS** gauge (JD-FL-W4); `dry` | NOAA **Atlas 14** 24-hr rainfall → **SCS Curve-Number** runoff (no free pluvial depth grid exists), one method everywhere | NOAA **SLOSH MOM** surge-by-category + **RAFT** close-passage tracks (≤50 km, ≥64 kt) + observed **λ** from **HURDAT2** |
| **field emitted** | depth raster (`ble_image`) or flood-area polygon + WSE contour + gauge `Q(T)` (`sfha_bathtub`) for M2's lower-RP densification / ΔWSE (JD-FL-8/W5) | SCS-CN **runoff `Q`** per site/RP (JD-FL-9); ponding `f`/depth is per-asset terrain → deferred to M2 | per-storm catalog `{event_family_id, category, surge_depth_ft, min_dist_km}`, `event_family_id` switched on |
| **confidence** | best-supported (BLE = HEC-RAS quality) | the "blind spot" — softer/wider (flagged) | screening-grade — MOM is a per-category worst-case envelope |

Riverine + pluvial emit a **field manifest** tagged `sub_peril` (+ `asset` per row, `method` per riverine site), with a
reserved `event_family_id` (JD-FL-4); their two depths combine **worse-source-wins** at M4 (JD-FL-11). **Coastal is the
deliberate exception** (JD-FL-12/15): its partner is the **compound-Poisson hurricane engine**, so it emits an
**event-based catalog** with the `event_family_id` cross-link switched on, and M4 joins surge ↔ wind on the *same
storm*. Notebooks: `m1_catalog/riverine/01_catalog` + `m1_catalog/pluvial/01_catalog` + `m1_catalog/coastal/01_catalog` ✅.

```text
   FEMA BLE / NFHL+3DEP+gauge (R)     NOAA Atlas 14 rainfall (F)       SLOSH MOM + RAFT + HURDAT2 (C)
   measured depth / Zone-A bathtub    frequency only — NO depth grid   per-category surge + observed λ
            │                                  │                                  │
            ▼  read + densify (JD-FL-8/W5)      ▼  SCS-CN runoff → ponding (FL-9)   ▼  event catalog, event_family_id on
   ┌──────────────────────────────────────────────────────────────────────────────────────────┐
   │  M1 CATALOG  (per sub-peril field)  →  M2/M3/M4 contract (areal solar · per-node wind)       │
   └──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## The per-asset pipelines

### ✅ Solar — [`solar/`](solar/README.md)

**Four solar sites, all three sub-perils.** **Hayhurst TX** (dry baseline) · **Elizabeth Solar LA** (riverine + pluvial)
· **Discovery Solar FL** (coastal) · **LA3 West Baton Rouge LA** (the all-three site, where `max(riverine,pluvial)` +
coastal compound actually combine). A solar farm is a **dense areal polygon** → flood couples **areally** (inundated
fraction × conditional depth). One unified M2/M3/M4 notebook each. Headline **total flood EAL**: LA3 **0.761%** of TIV
(inland 0.653 riverine-dominated + coastal compound 0.107) · Discovery 0.338% (coastal-only) · Elizabeth 0.163%
(inland-only) · Hayhurst 0.030%. Open [`solar/README.md`](solar/README.md) for the walkthrough.

### ✅ Wind farm — [`wind_farm/`](wind_farm/README.md)

**Three wind sites, all three sub-perils.** **Green River IL** (~60% turbines in SFHA, riverine + pluvial) ·
**Shepherds Flat OR** (mapped-dry baseline) · **Amazon Wind US East NC** (the all-three site). A wind farm is a
**sparse turbine point-cloud** → flood couples **per-node** (each pad vs the flood surface), not areal. One unified
M2/M3/M4 notebook each. Headline **total flood EAL**: Green River **1.276%** of TIV (riverine-dominated — the collector
substation floods; FEMA-NRI-validated) · Amazon 0.069% (inland 0.056 + coastal compound 0.013; surge is spatially broad
but rare) · Shepherds Flat 0.

> **Each asset has its OWN all-three site** (LA3 solar, Amazon wind), where `max(riverine,pluvial) + coastal` truly
> combines. The disjoint single-peril sites (Elizabeth, Discovery, Green River, Shepherds Flat) remain as references;
> absent sub-perils enter the M4 engine as 0.

---

## Production path (peril-level)
**Atlas 15** (climate-aware rainfall, ~Sept 2026) + a free **pluvial depth grid** / **FFRD** national → harden the
blind-spot pluvial · live **StreamStats + OWP-HAND** depth where BLE is absent (the national spine) ·
**duration / business-interruption** (Gen-2, physical loss only today). The `revisit trigger` rows in the
[assumptions register](../../docs/plans/flood/assumptions.md) are the backlog. Method provenance:
[`docs/references/`](../../docs/references/README.md).
