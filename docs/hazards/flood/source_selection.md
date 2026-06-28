# Flood Source Selection — Branch Preview

Flood has a stronger source-selection story than most hazards because the branch work already compared
sub-peril evidence sources and built end-to-end notebooks. This page summarizes that choice from main.

**Status:** preview from the `flood` branch · written 2026-06-26 · **Applies to:** flood M0/M1 source
selection for riverine, pluvial, and coastal sub-perils. The branch plan/registers remain the authority until
the flood branch lands on main.

---

## Decision In One Screen

Flood is one peril, but source selection happens by sub-peril:

| Sub-peril | Selected source pattern | Confidence |
|---|---|---|
| **Riverine [R]** | FEMA BLE depth grids where available; NFHL/SFHA + 3DEP bathtub fallback; USGS gauges / ratings for densification and checks. | Best / engineering-grade where BLE exists. |
| **Pluvial [F]** | NOAA Atlas 14 rainfall-frequency -> SCS Curve Number runoff -> lidar-grounded ponding/depth proxy. | Screening-grade; no free national pluvial depth grid. |
| **Coastal [C]** | NOAA SLOSH MOM surge-by-category + RAFT/HURDAT2 storm-frequency context. | Envelope-grade; useful, but not per-event hydrodynamics. |

The source decision follows the physics:

```text
riverine:
  river water surface / floodplain depth
  -> use hydraulic depth grids when available

pluvial:
  rainfall ponding outside mapped floodplain
  -> no public depth grid, so model depth from rainfall + terrain

coastal:
  storm surge by hurricane category / event family
  -> use surge envelopes and bind to hurricane events later
```

## Source Roles

| Source | Evidence type | Current role | Why not more? | Revisit trigger |
|---|---|---|---|---|
| **FEMA BLE** | Engineering-grade depth grids, often 100/500-year. | Riverine preferred source. | Coverage is incomplete; lower return periods often need densification. | Broader BLE/FFRD coverage or better local hydraulic data. |
| **NFHL / SFHA + 3DEP** | Floodplain extents plus terrain. | Riverine fallback / bathtub approximation where BLE absent. | Extent is not full depth; bathtub is softer than hydraulic modeling. | Replace with BLE, local HEC-RAS, or commercial depth grids. |
| **USGS gauges / ratings** | Observed stage/discharge context. | Densification and validation support. | Point/network evidence, not complete asset depth field alone. | Better local rating curves or high-water-mark validation. |
| **USGS FIM / NWC FIM** | Inundation maps / operational flood extent-depth evidence. | Validation, local upgrade candidate, and fallback pressure-test source. | Not yet treated as a clean national probabilistic depth-frequency spine. | Side-by-side tests show it improves fallback sites and supplies stable RP/depth framing. |
| **NOAA Atlas 14** | Rainfall-frequency depths. | Pluvial rainfall input. | Rainfall is not flood depth; routing/ponding must be modeled. | Atlas 15 or public national pluvial depth product. |
| **Lidar / terrain data** | Local elevation and ponding geometry. | Pluvial grounding and depth caps; M2 depth/elevation logic. | Terrain does not supply event frequency or runoff by itself. | Better drainage, stormwater, or owner/site survey data. |
| **NOAA SLOSH MOM** | Surge envelope by storm category/basin. | Coastal surge depth source. | MOM is worst-case envelope, not per-event hydrodynamic surge. | ADCIRC/per-event surge model, higher-fidelity storm-tide products. |
| **NOAA CO-OPS / coastal scenario tools** | Tide-gauge extremes, coastal water-level context, SLR/scenario screening. | Coastal validation and scenario support. | Not the storm-resolved surge-depth catalog M1 needs. | Per-event coastal water-level product with asset/grid depth and event identity. |
| **RAFT / HURDAT2** | Synthetic/observed tropical cyclone event context. | Coastal frequency/event-family context and hurricane join. | Needs careful double-count guard with hurricane wind. | Unified hurricane wind+surge+rain event loop. |
| **FFRD / First Street / Fathom** | Probabilistic depth/frequency grids or frameworks. | Deferred benchmark or swap-in candidate. | FFRD is not national/production yet; First Street/Fathom require licensing/provenance review. | Reportable underwriting need exceeds public-source confidence or FFRD becomes production-grade. |

## Pressure-Test Status And Caveats

**Pressure-test status:** branch-preview. The deeper reasoning now lives in
[`discussion/flood/01_source_selection_pressure_test.md`](../../extra/discussion/flood/01_source_selection_pressure_test.md);
this main-branch page summarizes the selection so the hazard docs stay navigable before the branch lands.

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| FEMA BLE riverine depth grids | Return-period water depth / water surface evidence. | Best public fit for riverine because it is already a hydraulic depth product near the damage-curve input. | **Preferred riverine source where available.** | Coverage incomplete; often only 100/500-year anchors, lower RPs need densification. |
| NFHL / SFHA + 3DEP bathtub fallback | Riverine screening and approximate depth where BLE is absent. | Passes fallback test only: gives extent + terrain, not a hydraulic depth surface. | **Fallback / screening source.** | Bathtub depths are softer than HEC-RAS/BLE and must be labeled. |
| USGS gauges / ratings / regression | Lower-return-period densification and validation. | Useful to interpolate between/under BLE anchors, but point/network evidence is not a full depth grid. | **Support source.** | Rating/regression uncertainty affects EAL more than anchor PML. |
| NOAA Atlas 14 rainfall frequency | Pluvial event frequency / rainfall intensity. | Passes rainfall-frequency test, fails depth test: rainfall is not inundation depth. | **Selected pluvial input.** | Depth is modeled through runoff and terrain; pluvial remains screening-grade. |
| Lidar / DEM / 3DEP terrain | Ground elevation and ponding geometry. | Required for depth-at-asset, but cannot provide event frequency or runoff alone. | **Required site-condition input.** | DEM resolution, drainage, grading, walls, culverts, and equipment elevations can dominate results. |
| NOAA SLOSH MOM | Coastal surge depth envelope by basin/category. | Practical public surge source, but MOM is an envelope, not per-storm hydrodynamic surge. | **Selected coastal envelope source.** | Conservative / envelope-grade; per-event surge timing and tide/wave details are not resolved. |
| RAFT / HURDAT2 storm context | Storm family identity and frequency for coastal joins. | Needed to bind coastal surge to hurricane wind and avoid double-counting; not a flood-depth product by itself. | **Event-family support.** | Unified hurricane wind + surge + rain loop is still deferred. |
| FFRD / First Street / Fathom | Broader RP depth grids and national depth coverage. | Potentially stronger depth products, but FFRD rollout and commercial licensing/provenance keep them out of public V1. | **Deferred benchmark / swap-in.** | Revisit if FFRD becomes production-grade or vendor source clears access/provenance review. |

### Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| BLE coverage is incomplete. | Not every asset has a high-quality hydraulic depth grid. | Dispatch by site: BLE where available, fallback otherwise; carry source-quality flag. | Broader BLE/FFRD coverage or local HEC-RAS/commercial depth grid. |
| BLE often anchors only selected RPs. | EAL depends on frequent/lower-RP depths, not only 100/500-year PML anchors. | Densify lower RPs with gauge/regression/rating logic and label EAL softer than anchored PML. | More complete depth-frequency surface. |
| NFHL/SFHA is extent, not depth. | Treating zone membership as depth would overstate precision. | Use as screen/fallback context; pair with DEM/bathtub only when BLE absent. | Depth grids replace fallback. |
| Pluvial has no free national depth grid. | Atlas 14 gives rainfall, not ponding depth at equipment. | Model depth from rainfall, runoff, and terrain; label pluvial screening-grade. | Atlas 15 plus public pluvial depth grid / drainage-aware model. |
| Site conditions can dominate flood loss. | Ground elevation, pads, equipment height, walls, levees, drainage, and river/coastal proximity change depth-at-asset. | Treat flood as site-conditioned; M2 compares water level/depth to local critical elevation. | Owner survey, equipment elevation, drainage, wall/levee data. |
| SLOSH MOM is a surge envelope. | It can be conservative and not event-specific. | Label coastal envelope-grade; use for screening and event-family joining, not precise per-storm hydrodynamics. | ADCIRC/per-event surge or validated storm-tide product. |
| Flood/hurricane double-count risk. | Surge/rain and wind can come from the same tropical cyclone. | Coastal flood joins hurricane by `event_family_id`; unified storm loop deferred. | Main-branch hurricane+flood combined event model. |

### Surprising Findings / Watchlist

Compact carry-forward findings; full reasoning lives in
[`discussion/flood/01_source_selection_pressure_test.md`](../../extra/discussion/flood/01_source_selection_pressure_test.md).

- Flood has one damage axis, depth, but no single V1 source: riverine, pluvial, and coastal need different evidence
  objects.
- Riverine confidence is geography-dependent: BLE-backed sites are stronger than NFHL/DEM fallback sites.
- NFHL/SFHA is extent, not depth; it cannot directly drive a depth-damage curve.
- Pluvial is the biggest public-data gap because Atlas 14 gives rainfall frequency, not inundation depth.
- NWC FIM and USGS FIM are the most important public fallback/validation candidates from the reference doc; they
  should be pressure-tested, but they do not replace BLE/Atlas/SLOSH as V1 spines today.
- Coastal surge is event-linked but envelope-grade; SLOSH MOM supports screening and joins, not per-storm hydraulics.

## Access And Dependency Profile

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| FEMA BLE | FEMA engineering/depth-grid products where available. | Public where released; coverage varies by geography. | Raster/depth grids by return period; site-specific availability. | Preferred riverine source; dependency is coverage discovery and local extraction. |
| NFHL / SFHA + 3DEP | FEMA NFHL plus USGS 3DEP elevation products. | Public. | Floodplain polygons plus DEM/elevation rasters. | Fallback riverine path; requires bathtub/depth approximation logic. |
| USGS gauges / ratings | USGS public gauge/stage/discharge services and records. | Public. | Time series / station tables. | Densification and validation support, not standalone depth field. |
| USGS FIM / NWC FIM | USGS FIM library and NOAA/NWC operational inundation services. | Public. | Inundation maps / forecast or event layers; coverage and method vary. | Validation and fallback-upgrade candidate; not V1 runtime spine. |
| NOAA Atlas 14 | NOAA precipitation-frequency products. | Public. | Rainfall-frequency tables/grids. | Pluvial input; must be transformed through runoff/terrain modeling. |
| Lidar / terrain data | Public lidar/DEM products where available. | Public, source-dependent. | High-resolution elevation rasters; can be large by geography. | Needed for local ponding/depth/equipment-elevation logic. |
| NOAA SLOSH MOM | NOAA SLOSH/MOM surge products. | Public. | Surge envelope rasters/grids by basin/category. | Coastal envelope source; not per-event hydrodynamics. |
| NOAA CO-OPS / coastal scenario tools | NOAA tide gauges, extreme water-level products, SLR/coastal exposure tools. | Public. | Point water-level records and scenario layers. | Coastal validation/scenario support, not storm-resolved M1 spine. |
| RAFT / HURDAT2 | Synthetic and observed tropical cyclone catalog sources. | Public/source-dependent. | Track/event tables/catalogs. | Coastal/hurricane event-family linkage; double-count guard required. |
| FFRD / First Street / Fathom | FEMA/USACE emerging public framework or licensed vendor grids. | FFRD public/emerging; vendor products licensed. | Multi-RP probabilistic flood-depth products/frameworks. | Deferred benchmark or replacement candidate after coverage/provenance/access review. |

Flood's access burden is uneven: riverine may be a direct depth-grid extraction where BLE exists, pluvial is a
model chain assembled from public rainfall and terrain products, and coastal uses public envelope products
plus storm-event context. The source-selection record should keep those operational dependencies separate.

## Product Grain And Runtime Flow

Flood is not one source grain. The V1/branch-preview source grain changes by sub-peril:

```text
riverine:
  selected source grain: return-period depth / water-surface evidence
  preferred product:     FEMA BLE depth grids where available
  fallback product:      NFHL/SFHA extent + 3DEP terrain, with bathtub/depth approximation

pluvial:
  selected source grain: rainfall-frequency plus local terrain/runoff transform
  product inputs:        NOAA Atlas 14 + SCS Curve Number + lidar/DEM
  important caveat:      rainfall frequency is not flood depth

coastal:
  selected source grain: surge envelope by basin/category plus storm-family context
  product inputs:        NOAA SLOSH MOM + RAFT/HURDAT2 event context
  important caveat:      SLOSH MOM is an envelope, not per-storm hydrodynamics
```

The runtime flow is a dispatch by sub-peril:

```text
riverine source products
  FEMA BLE depth grids where available
  NFHL/SFHA + 3DEP fallback where BLE is absent
    |
    v
M0 coverage discovery + local extraction
    |
    v
derived riverine profile
  return period -> inundation depth at asset/cell
  source-quality flag: BLE / fallback / densified
```

```text
pluvial source products
  NOAA Atlas 14 rainfall-frequency
  soil/runoff assumptions
  lidar / DEM terrain
    |
    v
M0 rainfall-to-ponding transform
    |
    v
derived pluvial profile
  return period -> modeled ponding depth
  confidence flag: screening-grade
```

```text
coastal source products
  NOAA SLOSH MOM surge envelopes
  RAFT / HURDAT2 storm-family context
    |
    v
M0 category / basin / site extraction
    |
    v
derived coastal profile
  storm/category -> surge depth envelope
  event_family_id hook for hurricane wind join
```

The storage boundary is the same idea as the other hazards: provider rasters/catalogs remain source artifacts;
the model persists the compact derived profile by sub-peril: depth-vs-return-period vectors, source-quality
flags, site/cell extraction manifests, and cross-peril event-family keys where coastal joins hurricane.

## Why Riverine Is The Strongest Flood Source

Riverine flood has the cleanest public evidence because FEMA BLE is close to the thing the damage curve needs:

```text
return period -> water depth / water surface at location
```

That is why riverine is treated as the best-supported flood sub-peril. The weak points are coverage gaps and
lower-return-period densification, not the basic source concept.

## Why Pluvial Is Screening-Grade

Pluvial flood is the source-selection problem child.

There is no free national product that simply gives:

```text
10/25/50/100/500-year pluvial depth at every asset
```

So the branch uses available public pieces:

```text
rainfall frequency
  -> runoff estimate
  -> terrain/ponding proxy
  -> screening depth
```

This is honest but lower confidence. It is still useful because pluvial can matter outside mapped riverine
floodplains, but its magnitude should not be read with the same confidence as BLE-backed riverine depth.

## Why Coastal Uses SLOSH As An Envelope

Coastal flooding is tied to tropical cyclone surge. SLOSH is public and practical, but the MOM product is an
envelope:

```text
storm category / basin -> maximum-of-maximum surge envelope
```

That means it is suitable for a conservative source-selection branch and for linking surge to hurricane
event families, but it is not the same as a per-storm hydrodynamic simulation.

## QA/QC Burden

```text
[x] split flood into riverine / pluvial / coastal before source selection
[x] riverine source preference follows depth-grid quality
[x] pluvial explicitly labeled modeled-depth / screening-grade
[x] coastal explicitly labeled envelope-grade
[x] flood coupling remains site-conditioned: depth vs equipment/ground elevation
[ ] final main-branch decisions/registers land when the flood branch is merged
[ ] unified hurricane wind + surge + rain event loop deferred
```

## What This Page Prevents

```text
Mistake 1:
  "Flood has one data source."
  -> wrong; the three sub-perils need different evidence.

Mistake 2:
  "Atlas 14 rainfall is flood depth."
  -> wrong; rainfall must pass through runoff/terrain/ponding logic.

Mistake 3:
  "SLOSH MOM is a per-event surge simulation."
  -> wrong; it is an envelope by storm category.

Mistake 4:
  "NFHL floodplain means we know depth."
  -> not by itself; extent and depth are different objects.
```

## Deep References

- Flood anchor: [`README.md`](README.md).
- Flood fundamentals: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Source pressure-test discussion:
  [`01_source_selection_pressure_test.md`](../../extra/discussion/flood/01_source_selection_pressure_test.md).
- Flood branch code: [`Notebooks/flood/`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood).
- Flood branch plans: [`docs/plans/flood/`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/docs/plans/flood).
- Flood branch layer-0 source reasoning:
  [`Notebooks/flood/layer0/01_hazard_definition.py`](https://github.com/aamani-ai/Hazard_Modeling/blob/flood/Notebooks/flood/layer0/01_hazard_definition.py).
- Flood branch M0 site/data work:
  [`Notebooks/flood/m0_input_data/`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood/m0_input_data).
- Flood branch M1 source forks:
  [`riverine`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood/m1_catalog/riverine),
  [`pluvial`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood/m1_catalog/pluvial), and
  [`coastal`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood/m1_catalog/coastal).
- Cross-hazard site-condition rule: [`LL15`](../../learning_logs/15_site_conditioned_is_not_one_thing.md).
