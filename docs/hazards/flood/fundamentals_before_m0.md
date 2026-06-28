# Flood Fundamentals Before M0

This is an internal reading guide for someone learning the flood pipeline before opening the flood notebooks.
It is not a method spec, a decision register, or a run log. It is the prerequisite mental model: the physics
you need in your head, the data reality you must respect, and the reason the M0-M4 pipeline is shaped the way
it is.

It is one hazard-specific instance of the cross-hazard guide:
[`../fundamentals_before_m0.md`](../fundamentals_before_m0.md).

Read this before:

```text
Notebooks/flood/layer0/
Notebooks/flood/m0_input_data/
Notebooks/flood/m1_catalog/
```

Cross-hazard pattern:

```text
physics -> data-source reality -> M0-M4 translation
```

For flood:

```text
physics       -> water depth above ground/equipment
data reality  -> three different source families, one per sub-peril
pipeline      -> fork at M1 by sub-peril, then reconverge at depth -> damage
```

The short version:

```text
flood modeling = water physics + data availability + asset elevation

The universal damage driver is:

    inundation depth at the vulnerable equipment

not:

    "the flood polygon touched the site"
    "the site is in a FEMA zone"
    "the rainfall was large"
```

---

## 1. The Person-Doing-The-Modeling Prerequisite

Before M0, the analyst needs to answer three questions in plain language.

```text
1. Physics:
   What physical quantity causes damage?

2. Data:
   What public data source can actually tell us that quantity, or a proxy for it?

3. Pipeline translation:
   Given the physics and the data limits, what should M0, M1, M2, M3, and M4 mean?
```

For flood, that becomes:

```text
Physics       -> water depth above ground/equipment
Data          -> three different source families, one per sub-peril
Pipeline      -> fork at M1 by sub-peril, then reconverge at depth -> damage
```

This is why flood needs a reader orientation before the normal methodology. It is easy to say "flood" as if
it is one object. In the actual modeling, flood is a family of three related hazards.

---

## 2. The Core Physics: Water Surface Minus Ground

Flood damage starts with one equation:

```text
depth_above_ground = water_surface_elevation - ground_elevation
```

Then damage depends on whether that water reaches vulnerable equipment:

```text
effective_damage_depth = max(0, depth_above_ground - component_onset_height)
```

ASCII cross-section:

```text
elevation
   ^
   |
   |        +-------------------+  vulnerable component
   |        | inverter / box    |
   |        +-------------------+
   |        ^ component_onset_height above ground/pad
   |
   | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  water surface elevation
   |                 |
   |                 | depth_above_ground
   |                 v
   | ----------------------------------  ground / pad elevation
   |
   +------------------------------------------------> space
```

If the water is below the component onset height, the catalog may still count a flood, but the damage curve
can still return near-zero damage.

That is the flood version of "two thresholds":

```text
FLOOD EVENT BASIS                         DAMAGE-ONSET DEPTH
"what M1/M4 counts"                       "where M3 starts loss"

10/100/500-year flood depth               inverter/pad/component height
annual maximum severity                   DR(depth <= onset) ~= 0
```

The most important beginner mistake is mixing these up.

---

## 3. Flood Is One Peril, Three Sub-Perils

The shared damage driver is depth, but the source of the water differs.

```text
                         ONE DAMAGE DRIVER
                         inundation depth
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
   [R] riverine           [F] pluvial            [C] coastal
   river overflow         rainfall ponding       storm surge
```

Table version:

| Sub-peril | Physics | Practical question | Data reality |
|---|---|---|---|
| Riverine | River or stream overflows its channel/floodplain. | How deep is river flooding at this site for each return period? | Best-supported where FEMA BLE depth grids exist. |
| Pluvial | Rain falls faster than the ground/drainage can absorb or move it. | How much local ponding forms on the site? | Blind spot: no free national pluvial depth grid, so depth is modeled. |
| Coastal | Tropical cyclone or coastal storm pushes surge inland. | What surge depth reaches the site for a storm/category? | SLOSH is useful but envelope-like; must avoid double-counting with hurricane. |

This is the central flood architecture:

```text
different physics + different data at M1
same damage driver at M3
```

---

## 4. Why Flood Is Not A Hail-Style Hit Probability Problem

Hail often asks:

```text
Did the event footprint overlap the asset?
```

Flood asks:

```text
What local water depth reaches each exposed part of the asset?
```

So flood coupling is site-conditioned:

```text
hazard field / return-period surface
        |
        v
sample depth at the site
        |
        v
adjust for ground elevation, pad height, equipment location
        |
        v
depth-damage curve
```

No Minkowski hit probability is needed for the normal flood setup. The flood source already describes a local
depth surface or a way to derive one. The asset does not enter because it has a probability of being hit; it
enters because its local elevation and equipment layout determine how much water matters.

For flood, `site-conditioned` includes both natural conditions and engineered/managed conditions: river
proximity, ground elevation, drainage path, flood walls, pads, equipment height, and source-product artifacts.
See [`LL15`](../../learning_logs/15_site_conditioned_is_not_one_thing.md) for the cross-hazard rule.

---

## 5. The Data Reality Per Sub-Peril

Flood is not hard because the physics is mysterious. It is hard because each sub-peril gives us a different
kind of data.

```text
[R] Riverine
    best case: FEMA BLE depth grids
    gives: depth at return periods, usually 100-year and 500-year
    issue: lower return periods often need densification

[F] Pluvial
    source: NOAA Atlas 14 rainfall frequency
    gives: rainfall depth at return periods
    missing: direct ponding depth grid
    therefore: rainfall -> runoff -> ponding must be modeled

[C] Coastal
    source: SLOSH surge envelope + hurricane event catalog
    gives: surge depth by storm/category screen
    issue: same storm may also drive hurricane wind and rainfall
```

The clean mental split:

```text
riverine  -> often reads depth
pluvial   -> models depth from rainfall
coastal   -> borrows surge depth from hurricane-linked data
```

---

## 6. The Three Data Words You Must Understand

### Water Surface Elevation

`water_surface_elevation` is the height of the flood water in an absolute vertical reference frame.

```text
WSE = "how high is the water surface?"
```

### Ground Elevation

`ground_elevation` is the local land/pad elevation, usually from DEM or lidar.

```text
ground = "how high is the asset's ground?"
```

### Inundation Depth

`inundation_depth` is the difference.

```text
depth = WSE - ground
```

ASCII:

```text
elevation
   ^
   |
   |      water surface elevation
   | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   |
   |             depth
   |             <--->
   | -------------------------------  ground elevation
   |
   +--------------------------------> space
```

This is why datum discipline matters. If WSE is in one vertical datum and ground is in another, the subtraction
can be wrong even if both data files look valid.

---

## 7. Return Period And AEP, In Plain English

Flood data is often indexed by return period:

```text
10-year flood   -> AEP 0.10
100-year flood  -> AEP 0.01
500-year flood  -> AEP 0.002
```

This does not mean "happens exactly once every 100 years." It means:

```text
100-year flood = 1% annual exceedance probability
```

In the inland flood model, we usually build a curve:

```text
AEP / return period -> depth -> damage -> loss
```

Then M4 samples an annual maximum:

```text
one simulated year
    draw severity percentile / AEP
    read loss from the loss-exceedance curve
```

So inland flood is usually annual-maximum, not a hail-style list of many footprint events per year.

---

## 8. M0-M4 Translation For Flood

The flood pipeline follows the same platform interface, but the meaning of each layer is flood-specific.

```text
Layer 0  -> define the flood family
M0       -> meet the raw evidence
M1       -> build sub-peril depth/RP catalogs
M2       -> couple depth to the asset geometry/elevation
M3       -> convert local depth to damage
M4       -> combine annual losses and metrics
```

ASCII pipeline:

```text
                       FLOOD FAMILY
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   riverine M1         pluvial M1          coastal M1
   RP depth field      rainfall->ponding   surge event catalog
        |                   |                   |
        +----------+--------+---------+---------+
                   |                  |
                   v                  v
              M2 coupling        hurricane join for coastal
              depth at asset     event_family_id
                   |
                   v
              M3 depth -> damage
                   |
                   v
              M4 annual loss metrics
```

Layer meanings:

| Layer | Flood meaning |
|---|---|
| Layer 0 | Define riverine/pluvial/coastal, their magnitude basis, and their data sources. |
| M0 | Inspect real flood evidence: FEMA zones, BLE grids, DEM/lidar, Atlas 14, SLOSH, gauges. |
| M1 | Emit asset-independent sub-peril depth/frequency objects. |
| M2 | Sample those objects at the asset: solar footprint area or wind nodes/substation. |
| M3 | Apply depth-damage curves with component onset heights and caps. |
| M4 | Sample annual loss, combine sub-perils, report EAL/PML/VaR/TVaR. |

---

## 9. Solar Versus Wind: Same Flood, Different Coupling

The hazard is the same. The asset geometry changes M2.

```text
Solar PV:
    dense areal polygon
    value roughly follows area
    coupling = flooded fraction + conditional depth

Wind farm:
    sparse turbine point cloud + collector substation
    value sits at nodes
    coupling = per-node depth at each pad/substation
```

ASCII:

```text
solar site                         wind farm

+----------------------+           o       o          turbine nodes
| #################### |                o
| #################### |           o             S     S = collector substation
| #################### |                    o
+----------------------+           o       o

areal inundation                   per-node inundation
```

This is why the same flood hazard can be material for a low solar pad but minor for turbines on raised pads,
while a valley-bottom collector substation can dominate wind-farm flood loss.

---

## 10. Combining Sub-Perils: Flood Usually Maxes, Not Adds

Riverine and pluvial can be driven by the same storm and can drown the same equipment.

Naively adding them can double-count:

```text
riverine loss + pluvial loss
```

The flood headline is usually worse-source-wins for overlapping equipment:

```text
combined_inland_loss = max(riverine_loss, pluvial_loss)
```

Why?

```text
same component + same water damage mechanism = it drowns once
```

But the additive-capped value is useful as an envelope:

```text
upper_envelope = min(TIV, riverine_loss + pluvial_loss)
```

ASCII:

```text
same equipment flooded by two sources

river water depth:    ~~~~~~~
rain ponding depth:   ~~~
equipment:            [ inverter ]

damage evaluation: use the worse effective depth, not two separate drownings
```

Coastal is different because it is event-based and linked to hurricane by `event_family_id`. The key discipline
is the same: one physical storm should not be counted twice across flood and hurricane.

---

## 11. What To Watch Before Trusting A Flood Result

Use this checklist before reading a flood notebook output.

```text
[ ] Which sub-peril is this: riverine, pluvial, coastal, or combined?
[ ] Is the number a water-surface elevation, ground elevation, or depth?
[ ] Are vertical datums reconciled before subtracting WSE - ground?
[ ] Is the site using real depth grids, or modeled depth from rainfall?
[ ] For riverine, are lower RPs observed, densified, or assumed?
[ ] For pluvial, is it clearly labeled screening-grade?
[ ] For coastal, is surge tied to hurricane with event_family_id?
[ ] Does M2 use the right asset geometry: areal solar or per-node wind?
[ ] Does M3 keep damage-onset height separate from event return period?
[ ] Does M4 combine overlapping flood sources by max/envelope rather than naive sum?
```

---

## 12. The One-Screen Mental Model

```text
Flood is not "a polygon hit me."

Flood is:

    water source
        -> water surface / runoff / surge
        -> local depth above asset ground
        -> depth above vulnerable component
        -> damage ratio
        -> annual loss distribution

The source differs:

    riverine = river overflow, often measured by depth grids
    pluvial  = rainfall ponding, modeled because depth grids are missing
    coastal  = storm surge, event-linked to hurricane

The driver reconverges:

    all sub-perils -> inundation depth -> depth-damage

The asset enters at M2:

    solar = areal footprint
    wind  = per-node pads/substation
```

If you keep only one sentence:

```text
For flood, the prerequisite is learning to think in local depth above vulnerable equipment, while remembering
that the three ways of creating that depth have very different data quality.
```
