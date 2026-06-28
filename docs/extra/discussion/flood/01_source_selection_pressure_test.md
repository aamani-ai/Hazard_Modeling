# Flood Source-Selection Pressure Test

**Status:** discussion note, previewing the `flood` branch. This records the deeper source-choice reasoning that
should sit between the Drive references and the M0/M1 notebooks. The flood branch plans and notebooks remain the
authority until that branch lands on main.

Flood source selection is not one decision. It is three decisions:

```text
flood
  |
  +-- riverine [R]  -> water surface / floodplain depth
  +-- pluvial  [F]  -> rainfall-runoff ponding depth
  +-- coastal  [C]  -> storm-surge depth tied to hurricane event identity
```

The shared damage driver is **inundation depth at the asset**, but each sub-peril reaches that depth through a
different evidence path.

## What M1 Needs

Flood M1 needs depth-frequency or storm-depth objects that M2 can sample against site/equipment elevations:

| Sub-peril | M1 needs | Best source object |
|---|---|---|
| Riverine | Return period -> water depth / water surface at site or cell. | Hydraulic depth grid where available. |
| Pluvial | Return period -> ponding depth from rainfall/runoff/terrain. | Rainfall-frequency plus runoff/terrain transform, because no free national pluvial depth grid is available. |
| Coastal | Storm/category -> surge depth, with event-family identity for hurricane joins. | Surge envelope/product plus tropical-cyclone event context. |

This is the core rule:

```text
Do not confuse event frequency evidence with depth evidence.
Do not confuse flood-zone extent with flood depth.
Do not confuse surge envelopes with per-storm hydrodynamic simulations.
```

## Candidate Pressure Test

| Candidate | What it provides | Pass/fail against M1 object | V1 / branch role |
|---|---|---|---|
| **FEMA BLE depth grids** | Hydraulic depth grids / water-surface evidence, commonly 1% and 0.2% annual-chance anchors. | **Pass for riverine where available.** Close to the actual depth input damage curves need. | Preferred riverine source. |
| **NFHL / SFHA + 3DEP** | Floodplain extent plus ground elevation. | Passes fallback/screening test only. Extent is not depth; DEM can support bathtub approximation. | Riverine fallback where BLE absent. |
| **USGS gauges / ratings / regression** | Stage/discharge evidence and lower-RP support. | Support source. Good for densifying/checking, not a full national depth field alone. | Densification and validation support. |
| **NOAA Atlas 14** | Precipitation-frequency depths by duration/return period. | Passes rainfall-frequency test, fails depth test by itself. | Selected pluvial rainfall input. |
| **NOAA Atlas 15** | Future precipitation-frequency product with seamless national / non-stationary framing. | Strong future replacement candidate, but not the current branch input. | Watch item / future pluvial rainfall input. |
| **DEM / lidar / 3DEP** | Ground elevation and ponding geometry. | Required site-condition input, not a frequency source. | Required pluvial/flood coupling support. |
| **USGS FIM / high-water marks** | Observed inundation grids, event surveys, and calibration evidence where available. | Strong validation/calibration source, but not nationally complete enough for V1 spine. | Validation / local upgrade source. |
| **NOAA National Water Center FIM / NWPS** | Operational inundation extent/depth from National Water Model + HAND. | Promising free national-ish layer, but forecast/HAND-oriented and not a clean probabilistic depth-frequency spine. | Priority candidate for fallback validation / future upgrade. |
| **NOAA SLOSH MOM** | Maximum-of-maximum surge envelope by basin/category. | Passes coastal screening/envelope test, not per-event hydrodynamics. | Selected coastal envelope source. |
| **NOAA CO-OPS tide gauges / Extreme Water Levels** | Observed coastal water-level frequency and validation evidence. | Strong support source for coastal validation and non-TC water-level context; not a surge-depth grid at every asset. | Coastal calibration / validation support. |
| **NOAA Coastal Flood Exposure Mapper / SLR Viewer** | Coastal scenario screening layers, including sea-level-rise framing. | Useful screening/scenario source, but not the event-based surge object M1 needs. | Scenario / validation support. |
| **RAFT / HURDAT2** | Tropical-cyclone storm identity and observed/synthetic event context. | Support source for event-family linkage and frequency context, not flood depth by itself. | Coastal/hurricane join support. |
| **FEMA FFRD** | Emerging public graduated floodplain / probabilistic framework, potentially ~5- to ~2000-year. | Potential future public spine, but pilot/emerging status blocks V1 national use. | Highest-priority public replacement candidate. |
| **First Street / Fathom** | Mature commercial depth-by-return-period products across riverine/pluvial/coastal. | Could be stronger than public V1 for underwriting if license/provenance are acceptable. | Commercial benchmark / possible swap-in. |
| **HEC-RAS / HEC-HMS** | Free hydrologic/hydraulic modeling engines. | Method engine, not a data source by itself. Requires terrain, flow/rainfall, boundary conditions, calibration. | Local hydraulic-model route where source data and budget allow. |

## Reference-Doc Option Audit

This section exists because the Drive reference lists more candidates than the branch-preview source page should
carry. The pressure test should not be biased toward current notebooks; each option is tested against the M1 object
we actually need.

### Options That Do Not Change V1 Today

| Reference option | Why it does not replace the current spine today | How it should be used |
|---|---|---|
| **USGS FIM + high-water marks** | Excellent evidence, but selected reaches/events only; not national enough for a V1 spine. | Validation/calibration where available; local upgrade over bathtub fallback. |
| **NOAA National Water Center FIM / NWPS** | Closest new free national inundation layer, but forecast/HAND-oriented and not a clean RP-depth catalog. | Priority candidate to pressure-test as fallback validation, especially where BLE is absent. |
| **NOAA CO-OPS Extreme Water Levels** | Point coastal water-level frequency, not site-wide surge/inundation grids. | Coastal validation and non-TC/coastal-water-level context. |
| **NOAA Coastal Flood Exposure Mapper / SLR Viewer** | Scenario/screening product, not event-based M1 source. | Coastal scenario screening and SLR sensitivity, not runtime surge catalog. |
| **HEC-RAS / HEC-HMS** | Modeling method, not a ready source. Building local models is a project per watershed/site. | Local high-confidence replacement where flow/rainfall/terrain/calibration data exist. |

### Options That Could Change The Decision Later

| Reference option | Why it could be better | Promotion gate |
|---|---|---|
| **FEMA FFRD** | Public probabilistic/graduated floodplain framework closer to the exact depth-frequency object M1 wants. | National or asset-region coverage, clear access, reproducible depth/RP outputs, and validation against known sites. |
| **First Street Flood Model** | Mature commercial multi-sub-peril depth-by-return-period product with climate scenarios. | Licensing, provenance, auditability, and agreement that a vendor product can be used as reportable hazard spine. |
| **Fathom US Flood Map** | Mature commercial fluvial/pluvial/coastal hazard engine, potentially direct depth grids. | Same commercial/provenance gate as First Street; compare against BLE/NFHL/known events before swap-in. |
| **NOAA Atlas 15** | Better forward pluvial rainfall input than Atlas 14 due national consistency and non-stationary/future framing. | Public CONUS release, stable API/files, and branch update from Atlas 14 to Atlas 15 rainfall-frequency inputs. |

**Net view after auditing the reference doc:** no immediate V1 spine change, but the flood watchlist should be
stronger than for hail/wildfire. Flood has credible future replacements, especially FFRD or a licensed
First Street/Fathom benchmark, and credible public validation/fallback upgrades via NWC FIM and USGS FIM.

## Decision Logic By Sub-Peril

### Riverine: use depth grids where they exist

Riverine is the strongest public flood source story because the preferred product is already near the model input:

```text
FEMA BLE depth grid
  |
  v
return period -> depth above ground / water surface
  |
  v
M2 samples at asset/cell
  |
  v
M3 depth-damage curve
```

The weakness is coverage and return-period density, not the concept. Where BLE exists, it is the right V1 spine. Where
it does not, the branch uses a fallback:

```text
NFHL / SFHA extent
  + 3DEP / DEM
  + gauge / rating / regression support
  -> bathtub or densified approximation
```

That fallback must be labeled as softer than a hydraulic depth grid.

### Pluvial: no free national depth grid, so model depth honestly

Pluvial is the "blind spot" source-selection case. Atlas 14 gives rainfall frequency, not flood depth:

```text
NOAA Atlas 14 rainfall-frequency
  |
  | runoff transform (SCS-CN in the branch)
  v
runoff / ponding proxy
  |
  | terrain + site-condition logic
  v
modeled pluvial depth at the asset/cell
```

That makes pluvial useful but lower-confidence. It should not be communicated with the same confidence as BLE-backed
riverine depth. The right documentation label is **screening-grade modeled depth**.

### Coastal: use SLOSH as an envelope and preserve event identity

Coastal flood is tied to tropical cyclones, so the source decision has a double-counting issue:

```text
same storm
  |
  +-- hurricane wind      -> hurricane peril
  |
  +-- surge / rainfall    -> flood peril
```

SLOSH MOM is practical and public, but it is an envelope:

```text
SLOSH MOM
  -> storm category / basin -> maximum surge envelope
```

It is not a per-storm ADCIRC-like hydrodynamic simulation. The branch uses it as an envelope-grade surge source and
keeps `event_family_id` so the same tropical cyclone's wind and surge can be joined later without double-counting.

## Caveat Ledger

| Caveat | Why it matters | V1 / branch treatment | Revisit trigger |
|---|---|---|---|
| BLE coverage is incomplete. | Some assets lack a hydraulic depth grid. | Dispatch by site: BLE where available, fallback otherwise; carry source-quality flag. | Broader BLE/FFRD coverage or local HEC-RAS/commercial depth grid. |
| BLE may only anchor selected RPs. | EAL is sensitive to frequent/lower-RP depths. | Densify with gauge/regression/rating logic; label EAL softer than anchored PML. | More complete depth-frequency surface. |
| NFHL/SFHA is extent, not depth. | Zone membership alone cannot drive a depth-damage curve. | Use as screening/fallback context only. | Replace with depth grids. |
| Atlas 14 is rainfall, not inundation. | Rainfall has to become runoff and ponding before it can damage equipment. | Transform through runoff/terrain; label pluvial screening-grade. | Atlas 15 plus public national pluvial depth product. |
| NWC FIM / USGS FIM are useful but incomplete for V1. | They can improve validation/fallback logic but are not yet clean national probabilistic depth-frequency spines. | Track as validation/local-upgrade sources. | Coverage and RP-depth framing become sufficient for M1. |
| Site conditions dominate flood coupling. | Ground elevation, pads, walls, drainage, culverts, levees, and equipment height can change loss more than the regional hazard. | Treat flood as site-conditioned: water level/depth vs asset critical elevation. | Owner survey, equipment elevation, drainage and flood-protection data. |
| SLOSH MOM is an envelope. | It can overstate/blur per-storm surge timing, tide, waves, and local hydraulics. | Label coastal envelope-grade; use for screening and event-family joins. | Per-event surge model / validated storm-tide product. |
| Commercial models may be objectively better but not automatically acceptable. | First Street/Fathom can supply mature depth grids, but licensing/provenance/auditability are model-governance decisions. | Keep as benchmark/swap-in candidates, not public V1 spine. | Commercial review clears and benchmark beats public V1. |
| Flood/hurricane double-counting is real. | Surge/rain and wind are often the same tropical cyclone. | Preserve `event_family_id`; unified TC wind+surge+rain loop deferred. | Main-branch combined hurricane/flood event model. |

## Surprising Findings / Watchlist

These are the pressure-test findings that should keep us honest rather than over-committed to the current branch
choices.

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| Flood is one damage axis but not one source axis. | Everything becomes depth at M3, but riverine/pluvial/coastal need different M1 evidence. | Public national depth-frequency product that cleanly separates sub-perils. |
| BLE makes riverine strong only where it exists. | Confidence is site-dependent; the same model may be BLE-grade or fallback-grade. | Broader BLE/FFRD or local HEC-RAS coverage. |
| Pluvial is the most fragile V1 source choice. | Rainfall frequency is not inundation depth, so model error enters before M3. | Public pluvial depth grids or drainage-aware national model with validation. |
| NWC FIM is the main public fallback-upgrade candidate we should pressure-test next. | It may improve over NFHL/DEM bathtub logic where BLE is absent, even if it is not a full probabilistic spine. | Side-by-side checks against BLE sites and known event/high-water-mark evidence. |
| Coastal source choice is driven by double-counting as much as surge physics. | Surge belongs to flood, but storm identity comes from hurricane. | Unified TC event loop with wind, surge, and rainfall sampled from one storm object. |
| Better commercial/public products could change V1 quickly. | Flood has more plausible swap-in candidates than hail/wildfire if provenance/access clears. | FFRD or commercial depth grids with transparent methods, licensing, and validation. |

## Access / Dependency Notes

```text
riverine:
  FEMA BLE if available
    -> local raster/depth extraction
    -> persist compact depth-vs-RP profile

  NFHL + 3DEP fallback
    -> public polygon + DEM
    -> persist source-quality flag because this is not hydraulic depth

pluvial:
  Atlas 14 rainfall-frequency
    -> runoff/terrain transform
    -> modeled depth profile, screening-grade

coastal:
  SLOSH MOM
    -> surge envelope by category/basin
    -> join to RAFT/HURDAT2 storm context by event_family_id
```

Flood access is less about raw volume and more about **source heterogeneity**. Each sub-peril produces a different
intermediate object, so the storage boundary should be the compact derived profile/catalog plus a source-quality
manifest, not a mirrored copy of every provider raster.

## What Should Graduate To `docs/hazards/flood/source_selection.md`

The high-level source-selection page should carry:

- one selected source pattern per sub-peril;
- a pressure-test table;
- a caveat ledger;
- explicit source-quality labels: BLE / fallback / screening-grade / envelope-grade;
- links to branch notebooks and this discussion.

It should not duplicate the full flood branch notebooks or future plan/register content.

## Deep References

Local / branch:

- Flood source page: [`../../../hazards/flood/source_selection.md`](../../../hazards/flood/source_selection.md).
- Flood branch notebooks: <https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood>
- Flood layer-0 branch notebook: <https://github.com/aamani-ai/Hazard_Modeling/blob/flood/Notebooks/flood/layer0/01_hazard_definition.py>
- Flood branch plans: <https://github.com/aamani-ai/Hazard_Modeling/tree/flood/docs/plans/flood>

Primary/source anchors:

- FEMA National Flood Hazard Layer: <https://www.fema.gov/flood-maps/national-flood-hazard-layer>
- NOAA Atlas 14 / Precipitation Frequency Data Server: <https://hdsc.nws.noaa.gov/pfds/>
- USGS 3D Elevation Program: <https://www.usgs.gov/3d-elevation-program>
- USGS National Water Information System: <https://waterdata.usgs.gov/nwis>
- USGS Flood Inundation Mapper: <https://fim.wim.usgs.gov/fim/>
- NOAA National Water Prediction Service: <https://water.noaa.gov/>
- NOAA CO-OPS Tides & Currents: <https://tidesandcurrents.noaa.gov/>
- NOAA SLOSH overview: <https://www.nhc.noaa.gov/surge/slosh.php>
