# Wind / tornado × wind — curve derivation dossier v0.1

**Cell ID:** `WIND_TORNADO_WIND`  
**Status:** v0.1 derivation scaffold — no final curve fitting yet.  
**Purpose:** decide the failure-unit coverage, x-axis architecture, candidate curve forms, evidence plan, and derivation questions for v1.0.

---

## 1. Why this cell is different

This cell is not like `hail × solar` and not like `flood × solar`.

```text
hail × solar
  one dominant component failure-unit
  x-axis = MESH-equivalent hail diameter
  curve form = bounded logistic for module breakage

flood × solar
  multiple electrical/elevation failure-units
  x-axis = local water depth above component datum
  curve form = piecewise/state curves

wind/tornado × wind
  repeated turbine units
  structural failure modes
  operating-state conditioners
  partial swath exposure
  curve form = structural fragility/state curves, not predetermined
```

The wind-farm cell must therefore be modeled as a **bundle of per-turbine structural failure-unit records**, with separate exposure aggregation across turbines.

---

## 2. Coverage decision

### Primary nonzero failure-units

```text
primary nonzero failure-units
├─ ROTOR_ASSEMBLY / BLADE
├─ TOWER / TOWER_SECTION
├─ NACELLE / drivetrain-generator-housing
└─ FOUNDATION / FOUNDATION_BASE, conditional on support/overturning pathway
```

These are primary because extreme wind/tornado loading directly targets the turbine structural load path.

### Conditioner-only equipment / states

```text
conditioner-only equipment / states
├─ PITCH_SYSTEM / feathering state
├─ BRAKE_SYSTEM / parked / emergency stop / overspeed state
├─ YAW_SYSTEM / yaw alignment or yaw error
└─ turbine operating state / operating, parked, curtailed, faulted
```

These should not be modeled as separate physical damage buckets by default. They modify blade/tower/nacelle vulnerability.

### Secondary / conditional units

```text
secondary / conditional units
├─ POWER_ELECTRONICS / POWER_CONVERTER
├─ SCADA / MONITORING_SYSTEM
├─ ELECTRICAL_COLLECTION / CABLE_AC
├─ SUBSTATION / TRANSFORMER_MAIN + SWITCHGEAR
└─ CIVIL_INFRA / access roads, if footprint/debris affects them
```

These may matter, but they should not be inferred automatically from turbine structural damage.

---

## 3. X-axis decision

### Decision

Use two related but distinguishable wind pathways:

```text
straight-line / severe synoptic wind
  x-axis = hub-height 3-second gust speed

convective tornado
  x-axis = tornado wind speed proxy if available
  fallback bridge = EF-scale wind range / categorical tornado intensity
```

### Why not one generic wind speed axis?

A tornado and a straight-line gust can both be expressed as a wind speed, but they are not identical loading environments.

```text
straight-line severe wind
├─ broader footprint
├─ easier height adjustment
├─ more compatible with gust hazard products
└─ turbine state/cut-out/feathering may be more predictable

tornado
├─ compact path
├─ strong spatial gradient
├─ rapid direction change
├─ possible vertical components and pressure effects
├─ debris impact
└─ EF rating is often damage-estimated, not directly measured
```

So v0.1 keeps them as related pathways rather than flattening them.

### Rejected alternatives

| Alternative | Why rejected as primary v0.1 axis |
|---|---|
| `IEC wind class / Vref` | Design selector/anchor, not event intensity. |
| `turbine count exposed` | Exposure geometry, not damage intensity. |
| `EF rating only` | Useful bridge but categorical and damage-estimated. |
| `dynamic pressure only` | Useful physics bridge, but not provider-native and still needs coefficients/geometry. |
| `duration × wind speed 2-D` | Real but not forced in v0.1 unless evidence requires it. |

---

## 4. Candidate curve forms

This cell should not copy the hail logistic by default. Curve form should be selected per failure-unit.

| Failure-unit | Candidate form | Why |
|---|---|---|
| Blade / rotor | Fragility/logistic or state curve | Failure probability transitions with wind/load; states can represent minor/major/break. |
| Tower | Structural fragility/lognormal or piecewise collapse state | Collapse is threshold-like but uncertain due design class, yaw, tornado-specific loads. |
| Nacelle | Dependency/state curve | Nacelle damage may be direct or consequence of blade/tower failure; assembly rule needed. |
| Foundation | Threshold/state curve tied to load or overturning proxy | Requires foundation/geotechnical data; not safe to invent generic curve. |
| Pitch/yaw/brake | Conditioner shift/blend | These change vulnerability state; usually not direct physical damage curves in this cell. |
| Exposure fraction | Multiplier / count aggregation | Changes how many turbines are affected, not component fragility. |

---

## 5. Evidence-to-decision map

| Source | What it supports | What it does **not** support |
|---|---|---|
| DOE/EERE severe-storm wind turbine page | Cut-out, shutdown, feathering, yaw control as conditioners | It does not provide structural fragility parameters. |
| IEC 61400-1 design requirements | Structural integrity and design-load-case framing | It is not an empirical damage curve. |
| DTU/WAsP IEC 61400-1 explainer | Wind class/load-case logic; yaw error and operating modes | It is secondary explanation; verify against the licensed standard. |
| NWS EF scale | Tornado EF bridge and 3-second gust ranges | EF rating is damage-estimated and categorical. |
| NASA Greenfield event summary | Case evidence: EF4, peak wind, downed wind turbines | One event is not a curve. |
| Greenfield structural failure analysis | Candidate v1.0 source for tower/blade failure mechanisms | Use exact findings only after review/access; do not over-generalize. |
| NREL Cost of Wind Energy Review | Value linkage for rotor/nacelle/tower/BOS | Not damage-curve evidence. |

Source links are included in the workbook `Sources` sheet.

---

## 6. New curve vs adjustment rules for this cell

### Create a new curve when

```text
- the value bucket is different and material;
- the physical failure mechanism is distinct;
- the x-axis/pathway differs materially;
- evidence supports a separate response.
```

Examples:

```text
blade structural failure ≠ tower collapse
straight-line gust curve may ≠ tornado-specific curve
substation footprint damage ≠ turbine structural damage
```

### Adjust an existing curve when

```text
- the same failure mechanism remains;
- only resistance, operating state, or exposure changes.
```

Examples:

```text
IEC wind class / Vref          → selector shift / curve family selection
feathered vs unfeathered       → conditioner shift/blend
aligned vs yaw error           → conditioner shift/blend
partial turbine swath exposure → exposure multiplier/count, not a new curve
```

---

## 7. Assembly and double-counting risk

Wind/tornado × wind needs assembly rules because turbine components are physically coupled.

```text
tower collapse
   may imply rotor + nacelle total loss

blade failure
   may damage nacelle or tower secondarily

nacelle fire/damage
   may be consequence of blade/tower failure
```

v1.0 must define a precedence rule such as:

```text
If TOWER collapse state = total collapse:
    apply tower + rotor + nacelle total-loss assembly cap;
    do not separately sum independent rotor/nacelle curves unless evidence says they are repairable independent losses.
```

This is a high-priority open seam.

---

## 8. v1.0 derivation plan

```text
1. Decide final split between straight-line wind and tornado pathways.
2. Source turbine structural anchors:
   - design class / Vref
   - observed tornado/wind farm case data
   - forensic/FEA studies
   - insurer/claims/engineering reports if available
3. Choose curve forms separately for blade, tower, nacelle, foundation.
4. Define selector transformations:
   - IEC class
   - hub height / rotor diameter
   - tower type
   - turbine model
5. Define conditioner transformations:
   - feathered state
   - yaw error
   - brake/parked/faulted state
6. Define exposure aggregation:
   - exposed turbine count
   - swath fraction
   - shared plant footprint
7. Add source-to-parameter mapping and assumption register.
8. Produce v1.0 curve data and dashboards.
```

---

## 9. Source links

- DOE/EERE severe weather turbine operations: https://www.energy.gov/eere/articles/how-do-wind-turbines-survive-severe-storms
- IEC 61400-1 design requirements summary: https://webstore.ansi.org/standards/iec/iec61400eden2019
- DTU/WAsP IEC 61400-1 explainer: https://wasp.dtu.dk/software/windfarm-assessment-tool/iec-61400-1
- NWS Enhanced Fujita Scale: https://www.weather.gov/grb/efscale
- NASA Greenfield tornado event summary: https://science.nasa.gov/earth/earth-observatory/tornado-damage-in-greenfield-152870/
- Greenfield structural failure analysis candidate: https://www.sciencedirect.com/science/article/pii/S1350630725011288
- NREL Cost of Wind Energy Review: https://www.nrel.gov/docs/fy25osti/91775.pdf
