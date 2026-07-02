# M0 — Input Data (raw flood hazard evidence)

*The first layer: meet the raw flood hazard data and **understand** it, before any modeling. "What flood hazard does
the public record say exists at the flood sites, and what do we really know about it?" Method-neutral — understanding,
not the model. M0 is **shared at the peril level over both assets** (JD-FL-19): `01_solar_sites` (all solar sites) and `02_wind_sites` (all wind sites) co-live here; only M2–M4 split per asset.*

**Where this sits:** layer-0 (definition) → **M0 (evidence)** → M1 catalog → M2 coupling → M3 damage → M4 loss &
metrics. No losses, no events-as-objects yet — just the *evidence*, each source explored on its own terms. Plan:
[`docs/plans/flood/m0_input_data.md`](../../../docs/plans/flood/m0_input_data.md) · Principles:
[`docs/principles/notebook_work/`](../../../docs/principles/notebook_work/README.md).

## The structural twist — flood M0 meets **screening + depth, self-serve**

The hard truth: *the good national probabilistic depth model is
**commercial** (First Street / Fathom); the public equivalent (FFRD) is still pilot.* So M0 builds on the **free
self-serve stack** — **FEMA NFHL** zones for screening + **FEMA BLE** depth grids (HEC-RAS quality where studies
exist) + **USGS 3DEP** DEM for ground + **NOAA CFEM** (SLOSH-derived) for coastal surge onset — and pins the
**null-vs-zero** trap (a desert site reads *true zero*, not "missing coverage").

| Notebook | Source | What it is | Role | Status |
|---|---|---|---|---|
| [`01_solar_sites`](01_solar_sites.ipynb) | **EIA-860** fleet + FEMA **NFHL** + **BLE** + USGS **3DEP** + NOAA **CFEM** + **OSM** | locks **all solar flood sites** in four parts: national fleet SFHA screen → Hayhurst (dry baseline) + Elizabeth (riverine); 3DEP DEM, geometry & flood-zone context; Gulf/Atlantic surge screen → Discovery (coastal); register LA3 West Baton Rouge (all-three) | solar site selection + geometry | ✅ **built** |
| [`02_wind_sites`](02_wind_sites.ipynb) | **USWTDB** turbines + FEMA **NFHL** + **OSM**/HIFLD + NOAA **CFEM** | locks **all wind flood sites** in three parts: SFHA-fraction sweep (selection evidence) → Green River + Shepherds Flat (dry) with per-turbine geometry + convex hull + collector substation + TIV; coastal screen → Amazon Wind US East (all-three) with per-turbine riverine + surge tags | wind site selection + geometry | ✅ **built** |

## The sites — low-vs-high contrast + the all-three combine sites

| asset | role | site | where | what it proves |
|---|---|---|---|---|
| solar | baseline | **Hayhurst Texas Solar** | Texas — Culberson Co; Chihuahuan desert | the engine returns a correctly-small number (genuine dry control, not null) |
| solar | riverine | **Elizabeth Solar Plant** (~143 MW) | Louisiana — Allen Parish; Lower-Mississippi alluvial plain | the riverine high end registers (footprint straddles the SFHA, BLE-confirmed) |
| solar | coastal | **Discovery Solar Center** (~75 MW) | Florida — Brevard Co; Cape Canaveral coast | Cat-1 surge onset (the weakest hurricane already inundates it) |
| solar | **all-three** | **LA3 West Baton Rouge** | Louisiana — West Baton Rouge Parish | riverine Zone A + pluvial + Cat-3 surge up the Mississippi all land at one site |
| wind | high | **Green River IL** | Illinois — Lee Co; Green River valley | ~60% of turbines in the SFHA; the collector substation sits in the valley |
| wind | baseline | **Shepherds Flat OR** | Oregon — Gilliam/Morrow Co | mapped-dry (0% in SFHA); dry control |
| wind | **all-three** | **Amazon Wind US East NC** | North Carolina — Perquimans Co; Albemarle Sound | 76% turbines surge-exposed Cat-3 + 11% in Zone A + pluvial |

## What the M0 notebooks found (built)

- **Riverine screen + geometry (`01_solar_sites`, parts 1–2):** the national `powerplants_enriched_v2` / EIA-860 screen targets the
  **Lower-Mississippi plain** and locks **Elizabeth Solar** (a real ~3.9 km² OSM polygon *and* the deepest BLE flood of
  the polygon-bearing candidates, [JD-FL-3](../../../docs/plans/flood/decisions.md)) against the reused **Hayhurst**
  dry control. **FEMA BLE** ("Estimated BFE", free, NAVD88, local-HEC-RAS quality) carries **1% (100-yr) + 0.2%
  (500-yr) depth/WSE + 10% extent** at Elizabeth — the riverine **depth spine**
  ([JD-FL-6](../../../docs/plans/flood/decisions.md)). **3DEP DEM** gives ground; `depth = WSE − ground` has sane
  signs/magnitudes (feet, not tens of metres) with the datum reconciled to NAVD88 (NOAA VDatum, AFL-13). The
  **null-vs-zero trap holds** — Hayhurst reads **true zero** at all RPs.
- **Coastal solar screen (`01_solar_sites`, part 3):** screening the EIA-860 Gulf/Atlantic fleet on **surge onset category** locks
  **Discovery Solar Center** (Cat-1 surge onset, real 1.31 km² OSM polygon, squarely in the hurricane footprint so M4
  can exercise the surge+wind combine, [JD-FL-12](../../../docs/plans/flood/decisions.md)). Surge source = **NOAA
  Coastal Flood Hazard Composite** point-`identify` (SLOSH-derived, category-resolved), source-tagged
  `NOAA_CFEM_composite` so the `US_SLOSH_MOM_Inundation_v4` raster is a one-place swap
  ([JD-FL-14](../../../docs/plans/flood/decisions.md)). Hayhurst screens `None` (no coastline) → a **structural** zero.
- **Wind screen + geometry (`02_wind_sites`, parts 1–2):** the SFHA-fraction sweep across the **USWTDB** fleet locks **Green River IL**
  (~60% of 74 turbines in the SFHA, Lee Co) + reused **Shepherds Flat OR** (mapped-dry); per-turbine geometry, convex
  hull, the farm's own west-edge collector substation node, and TIV ($/kW). Most wind projects sit ~0% in the SFHA —
  flood is a minor wind peril ([JD-FL-W2](../../../docs/plans/flood/decisions.md)).
- **Coastal wind screen (`02_wind_sites`, part 3):** locks **Amazon Wind US East NC** (Perquimans Co, ~138 MW, 104 turbines) — **76%
  surge-exposed at Cat-3** as the Albemarle Sound funnels surge inland, plus 11% in Zone A — the all-three wind site.
- **All-three solar site (`01_solar_sites`, part 4):** locks **LA3 West Baton Rouge** (West Baton Rouge Parish, real ~0.61 km² OSM polygon)
  — riverine Zone A (BLE Lower Grand), pluvial (Atlas-14), and Cat-3 surge up the Mississippi all material at one site.

**M0 is complete** — the flood hazard is understood across the self-serve stack (NFHL screen · BLE depth · 3DEP DEM ·
SLOSH-derived coastal surge screen) for both assets, including each asset's all-three combine site.

## Inputs → outputs

EIA-860 / USWTDB / OSM / FEMA NFHL + BLE (ArcGIS REST) + USGS 3DEP + NOAA CFEM → solar roster
`data/flood/flood_solar_m0_sites.json` + coastal solar roster `flood_solar_coastal_m0_sites.json` + wind roster
`flood_wind_m0_sites.json` (carrying per-node riverine + coastal tags) + screen scores (`*_site_screen.csv`) +
`flood_solar_m0_dem_context.json` + zone maps. Raw cache under `data/flood/raw/` (gitignored).

## Key decisions & assumptions (this layer)

[JD-FL-3](../../../docs/plans/flood/decisions.md) (solar sites = Hayhurst + national-screen high site) ·
[JD-FL-6](../../../docs/plans/flood/decisions.md) (BLE-preferred depth) ·
[JD-FL-13/14](../../../docs/plans/flood/decisions.md) (coastal screen + CFEM source) ·
[JD-FL-17](../../../docs/plans/flood/decisions.md) (all-three combine sites) ·
[JD-FL-W2](../../../docs/plans/flood/decisions.md) (wind site evidence). Assumptions **AFL-5** (self-serve public
data), **AFL-10** (national EIA screen, not the in-repo portfolio), **AFL-6** (BLE depth source), **AFL-13** (datum
via VDatum). Full register: [`assumptions.md`](../../../docs/plans/flood/assumptions.md).

**Next → M1 (catalog):** fork per sub-peril, one shared notebook each over **both assets** — **riverine** =
method-per-site field (`ble_image` depth raster / `sfha_bathtub` flood-area + WSE + gauge / `dry`) + `Q(T)` for M2
densification; **pluvial** = Atlas 14 → SCS-CN runoff `Q`; **coastal** = SLOSH MOM + RAFT + HURDAT2 event catalog. M1
emits the asset-independent **field**; the footprint/per-node reduction is M2's job (JD-FL-19).

## Method In Plain English

M0 is the evidence-gathering layer. It answers: "Which sites should we model, what geometry do we trust, and what flood
data actually exists around those sites?" It does not calculate damage or annual loss.

```text
M0 workflow

1. Start from asset rosters
   solar: EIA / OSM plant polygons
   wind:  USWTDB turbine points + project hulls

2. Screen for flood contact
   FEMA NFHL SFHA polygons -> is the site in a mapped floodplain?
   NOAA coastal screen     -> can surge reach the site?

3. Pull supporting evidence
   FEMA BLE depth/WSE where available
   USGS 3DEP / lidar ground elevation
   OSM / HIFLD substations and geometry

4. Lock model sites
   high-exposure site
   dry baseline site
   all-three site where riverine + pluvial + coastal can combine

5. Emit rosters and source tags
   no M3 damage
   no M4 annual simulation
```

The SFHA screen is only a first pass:

```text
SFHA contact = "public FEMA mapping says flood hazard reaches here"
SFHA contact != depth
SFHA contact != loss
outside SFHA != impossible flood
```

For riverine flood, the useful M0 evidence is the combination of water and ground:

```text
water surface elevation (WSE)
minus
ground elevation from DEM
equals
flood depth above ground
```

For a raster cell, the value represents the flood product's depth estimate for that cell location. In the BLE image path
used here, the notebook decodes symbolized depth bands from FEMA's service into depth-band midpoints. That is good
enough for a transparent V1 model, but it should be treated as banded engineering evidence, not a perfect continuous
survey of every square meter.

The null-vs-zero check is important:

```text
true zero:
  source coverage exists and the site is dry in that source

missing/null:
  the source does not cover the site or the layer cannot answer
```

M0 tries not to confuse those. A dry baseline must be dry because evidence says so, not because the pipeline failed to
find data.

## What M0 Asks

```text
M0 asks:
  which assets are candidates for flood modeling?
  which site is the high-exposure example?
  which site is the dry baseline?
  which site exercises all three sub-perils?
  what polygon, turbine cloud, or substation geometry is trusted?
  which public flood products cover the site?
  is the source saying wet, dry, or no answer?
```

M0 does not ask:

```text
  what is the annual loss?
  what is the damage ratio?
  how much of the footprint floods at each return period?
```

Those are M2-M4 questions. M0 only makes sure the later notebooks are standing on named sources and defensible site
geometry.
