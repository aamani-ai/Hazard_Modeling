# Flood Modeling Choices

**Status:** notebooks imported to main for review from `origin/flood` @ `aff8649`. Flood x solar and flood x
wind-farm are built end-to-end in [`Notebooks/flood/`](../../../Notebooks/flood/README.md). Plan/register docs
are now imported to main under [`docs/plans/flood/`](../../plans/flood/README.md). This file records the
modeling shape so the M0-M4 choices are visible before deeper notebook review. For the physics primer, read
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). For source roles, read
[`source_selection.md`](source_selection.md).

The core flood modeling fact:

```text
one peril, three sub-perils, one damage driver:
  riverine [R] -> depth from hydraulic / floodplain evidence
  pluvial  [F] -> rainfall + terrain modeled ponding depth
  coastal  [C] -> surge envelope tied to tropical-cyclone event family

all reconverge at M3 as depth -> damage.
```

---

## M0-M4 In One Table

| Layer | Flood model object | Main choices |
|---|---|---|
| **Layer 0** | Hazard definition: riverine + pluvial + coastal. | Flood is split by physics/data source but reconverges on inundation depth. |
| **M0** | Source evidence per sub-peril. | Riverine: FEMA BLE preferred, NFHL/SFHA + 3DEP fallback, USGS support. Pluvial: Atlas 14 rainfall + terrain. Coastal: SLOSH MOM plus TC event context. |
| **M1** | Depth-frequency / event profile per sub-peril. | Riverine and pluvial are annual-max return-period depth profiles; coastal is event/category surge-envelope stream. |
| **M2** | Site-conditioned depth at asset. | Compare water depth / water level to equipment elevation, pads, local terrain, turbine/substation placement, or solar array layout. |
| **M3** | Inundation depth -> damage ratio. | Shared depth-damage logic by asset, with solar and wind curves in the imported notebooks. Curves are medium/greenfield confidence depending on asset. |
| **M4** | Combined annual flood loss. | Inland R+F co-sampled; coastal event stream can join hurricane wind on `event_family_id`; metrics read from annual vectors. |

---

## M1 Event Model Contract

Flood is a mixed **return-period surface / proxy-chain / event-envelope** hazard under
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md).

### Riverine

```text
source:
  FEMA BLE depth grids where available
  NFHL/SFHA + 3DEP fallback where BLE is absent
  USGS gauges / StreamStats / Bulletin 17C support densification and validation

count frame:
  annual-max return-period / AEP profile

severity:
  inundation depth at return periods, with lower RPs densified where needed

distribution choice:
  not a raw event catalog in V1
  depth-frequency curve is the M1 object

event identity:
  annual severity draw for inland combine
  named river flood event identity deferred
```

### Pluvial

```text
source:
  NOAA Atlas 14 rainfall frequency
  SCS Curve Number runoff logic
  lidar / DEM terrain for ponding fraction and depth caps

count frame:
  annual-max rainfall / ponding return-period profile

severity:
  modeled local ponding depth

distribution choice:
  screening-grade proxy chain; no free national pluvial depth grid in V1

event identity:
  annual severity draw; no storm-family identity in V1
```

### Coastal

```text
source:
  NOAA SLOSH MOM surge envelopes
  RAFT / HURDAT2 tropical-cyclone event context

count frame:
  compound-Poisson / event-based TC stream by category where branch implementation applies it

severity:
  category surge depth envelope sampled at the site

distribution choice:
  envelope-grade, not per-event ADCIRC hydrodynamics

event identity:
  keeps event_family_id for hurricane wind / surge join
```

---

## Coupling Contract

Flood is **site-conditioned**:

```text
hazard intensity = depth / water level at the asset
asset condition = equipment elevation, pad height, local terrain, drainage/protection
loss starts when depth exceeds component onset
```

M2 changes:

```text
local depth at each asset component
effective exposed fraction
which source wins when multiple inland sources describe the same ground
```

Solar V1 uses a representative value-mix assumption:

```text
solar exposure_fraction = wet area / total footprint area
wet area fraction ~= wet value fraction

the wet share is assumed to contain the same component/capex mix as the whole plant:
  inverter systems
  substation / electrical
  PV array
  civil / access
```

This is why solar M2 can emit `exposure_fraction` and `conditional_depth` without locating each inverter pad or
substation. It is reasonable for V1, but it is a material assumption. If low electrical equipment is clustered in the
wet area, the model can understate loss; if it is raised or dry, the model can overstate loss.

Wind should not use the same areal value-mix assumption for turbines. Turbine pads are discrete nodes. A mapped
collector substation is useful exposure and dependency evidence, but it should become direct physical wind-farm loss
only if we can confirm it is owned by the project and included in the asset TIV / insured value schedule.

Wind-farm collector selection is a strong part of the current method, but it is still a geometry proxy:

```text
USWTDB turbine points -> buffered convex hull -> OSM/HIFLD collector candidates

prefer:
  OSM power=substation + substation=generation inside hull

allow:
  OSM generation substation just outside hull if nearest turbine < 0.6 km

fallback:
  any in-hull OSM substation
  HIFLD in-hull substation
  centroid, flagged weak
```

The reason is empirical: nearest-to-centroid grabbed the adjacent Big Sky Wind collector for Green River. The hull +
`substation=generation` guard found Green River's own valley-bottom collector, which materially changed the provisional
collector-driven physical-loss result and exposed a scope problem. The caveat is that a convex hull can overfill
concave turbine layouts or multi-phase outliers; official boundaries, interconnection records, or owner cost schedules
remain the better source when available. Without that confirmation, the collector belongs in dependency/disruption
screening, not baseline physical damage.

Inland combine:

```text
riverine and pluvial are co-sampled with one annual severity draw
worse-source-wins is the headline rule
additive-capped envelope is the conservative bound
```

Coastal combine:

```text
coastal surge is an event stream
surge can join hurricane wind on event_family_id
rain/pluvial tropical-cyclone linkage is deferred
```

---

## Damage Contract

M3 consumes:

```text
inundation depth above local ground / component threshold
asset component elevation / onset height
```

M3 emits:

```text
damage ratio or event loss by asset/component
```

Current notebook shape:

```text
solar:
  depth-damage curve from damage_modeling / curated curve evidence

wind farm:
  depth sensitivity concentrated in substation/electrical/foundation access, not blades

confidence:
  riverine depth stronger than pluvial depth
  curves medium / greenfield depending on asset
  BI/duration not yet modeled
```

Two thresholds:

```text
flood event basis:
  10/100/500-year depth, annual max, or hurricane category

damage onset:
  inverter/pad/component height
```

---

## M4 Sampling And Metrics

Inland sketch:

```text
for each simulated year:
  draw one annual inland severity state
  read riverine depth from its depth-frequency curve
  read pluvial depth from its modeled depth-frequency curve
  combine by worse-source-wins / envelope rule
  apply M3 depth-damage
```

Coastal sketch:

```text
draw TC / coastal event count
for each event:
  sample category / surge envelope depth
  apply coastal depth coupling
  apply M3
  preserve event_family_id for hurricane wind join
```

Metrics:

```text
EAL
AEP-PML / VaR
OEP-PML
TVaR
$ and % TIV
sub-peril attribution
```

Aggregation doctrine:

```text
inland R/F losses are not blindly additive because the same ground floods once
coastal surge and hurricane wind from the same storm are joined, not double-counted
tail metrics are read from the combined annual vector
do not combine flood sub-perils with max(EAL_riverine, EAL_pluvial, EAL_coastal)
```

The important distinction:

```text
worse-source-wins / max is a depth or event-component double-count guard
EAL / PML / VaR / TVaR are read after annual loss aggregation
```

This follows the cross-hazard rule in
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md): combine event losses at the correct
grain first, then read metrics from the combined annual vector.

---

## Built Numbers And Confidence

Notebook-backed orientation figures, pending review:

| Asset/site | Total flood EAL | Interpretation |
|---|---:|---|
| Solar: LA3 West Baton Rouge, LA | 0.761% TIV | all-three site; inland riverine-dominated plus coastal compound |
| Solar: Discovery, FL | 0.338% TIV | coastal-only reference |
| Solar: Elizabeth, LA | 0.163% TIV | inland-only reference |
| Solar: Hayhurst, TX | 0.030% TIV | dry / low baseline |
| Wind: Green River, IL | 1.276% TIV | provisional collector-included run; scope-flagged pending ownership/TIV decision |
| Wind: Amazon Wind US East, NC | 0.069% TIV | all-three wind site; inland plus coastal compound |
| Wind: Shepherds Flat, OR | 0.000% TIV | mapped-dry baseline |

Confidence state:

```text
riverine:
  strongest public flood sub-peril where BLE exists

pluvial:
  screening-grade blind spot; depth is modeled, not observed

coastal:
  useful direction / envelope; not per-event hydrodynamics

combined flood:
  built in imported notebooks for solar and wind farms; pending doc/review promotion
```

---

## Open Questions And Better Ways

Questions to resolve during notebook review:

```text
pluvial depth:
  Is the Atlas 14 -> SCS-CN -> terrain ponding chain conservative enough, or should it be replaced by FFRD,
  NWC/USGS FIM, Fathom, First Street, or local hydraulic modeling where available?

inland dependence:
  Is comonotonic co-sampling of riverine + pluvial the right V1 dependence assumption, or should we move to
  an event-family / rainfall-runoff correlation model?

coastal surge:
  Is SLOSH MOM acceptable as a V1 envelope, or should the review require per-event ADCIRC / storm-tide
  hydrodynamics for coastal product use?

site data:
  How much do owner equipment elevations, walls, drainage, pads, and substation surveys change M2 compared
  with public DEM assumptions?

cross-peril join:
  Surge joins hurricane wind through event_family_id today. The better final form is one storm loop that
  carries wind, surge, rain/pluvial, and possibly TC-spawned tornadoes without double counting.
```

Better-way candidates:

```text
riverine:
  FEMA FFRD / broader BLE, local HEC-RAS, or commercial depth-frequency grids

pluvial:
  Atlas 15 plus a public/national pluvial depth grid, or drainage-aware local modeling

coastal:
  event-resolved surge, tide, wave setup, and defense/protection treatment

loss:
  component-level depth curves with duration / BI / repair-cost calibration
```

---

## Assumptions And Revisit Triggers

Load-bearing assumptions:

```text
flood = riverine + pluvial + coastal
all sub-perils reconverge on inundation depth
BLE is preferred riverine source
Atlas 14 -> runoff -> terrain is pluvial V1
SLOSH MOM is coastal envelope V1
site-conditioned M2 is mandatory
inland combine is co-sampled / worse-source-wins
coastal surge joins hurricane wind by event_family_id
financial terms and BI are not included
```

Revisit triggers:

```text
FEMA FFRD or broader BLE depth-frequency coverage becomes usable
public national pluvial depth grid becomes available
Atlas 15 replaces Atlas 14
NWC/USGS FIM becomes clean enough for probabilistic depth-frequency use
ADCIRC/per-event hydrodynamic surge enters scope
owner equipment-elevation survey data is available
plans/registers are promoted to main and per-asset hazard docs are written
```

Authoritative references:

- Source selection: [`source_selection.md`](source_selection.md).
- Flood anchor: [`README.md`](README.md).
- Local notebooks: [`../../../Notebooks/flood/`](../../../Notebooks/flood/README.md).
- Local plans: [`../../plans/flood/`](../../plans/flood/README.md).

## Decision Stress-Test Questions

```text
source mode:
  is this branch event-first, return-period-surface-first, or hybrid?

riverine:
  are BLE depth anchors kept separate from Q(T)-based densification assumptions?

pluvial:
  is the no-public-depth-grid limitation explicit?

coastal:
  is SLOSH treated as a category envelope and joined to hurricane by event_family_id?

coupling:
  does M2 sample the asset footprint/nodes instead of letting M1 pre-average loss?

M4:
  does inland use worse-source-wins while coastal keeps storm event identity?
```

If a return-period depth row is treated as if it were a raw event catalog, the bridge assumptions need to be restated.
