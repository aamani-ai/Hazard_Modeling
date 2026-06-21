# Wind/tornado × wind farm — curve derivation dossier v1.0

This dossier is the proof trail for the `WIND_TORNADO_WIND` v1.0 curve package.

The goal is not to claim perfect universal wind-turbine fragility. The goal is to create a documented, auditable, public-source-derived damage-code layer that downstream hazard and financial systems can consume.

---

## 1. What is being derived?

The v1.0 cell derives component/failure-unit damage curves for a wind farm under strong straight-line/severe wind and tornado/direct-hit conditions.

```text
input hazard intensity
   │
   ├─ straight-line/severe wind:
   │     hub-height 3-second gust speed
   │
   └─ tornado:
         EF-scale / tornado wind proxy
         converted carefully to a 3-second gust proxy

then:
   │
   ▼
design-normalized speed ratio
   r = V_3s_hub / Ve50_class

then:
   │
   ▼
failure-unit damage ratios
   ├─ blade DR
   ├─ tower DR
   ├─ nacelle DR
   └─ foundation DR
```

This is **not** an asset-level whole-farm curve.

---

## 2. Failure-unit coverage

```text
strong wind / tornado × wind v1.0
├─ primary nonzero failure-units
│  ├─ ROTOR_ASSEMBLY / BLADE
│  ├─ TOWER / TOWER_SECTION
│  ├─ NACELLE / drivetrain-generator-housing
│  └─ FOUNDATION / FOUNDATION_BASE
│
├─ conditioner-only equipment / states
│  ├─ PITCH_SYSTEM / feathering state
│  ├─ BRAKE_SYSTEM / parked / emergency stop state
│  ├─ NACELLE / YAW_SYSTEM / yaw alignment or yaw error
│  └─ turbine operating state
│
├─ secondary / conditional units
│  ├─ POWER_ELECTRONICS / acceleration-sensitive response
│  ├─ SCADA / controls
│  ├─ ELECTRICAL_COLLECTION
│  ├─ SUBSTATION, if footprint includes it
│  └─ CIVIL_INFRA, if footprint/debris affects it
│
├─ exposure / protection modifiers
│  ├─ exposed turbine fraction
│  ├─ tornado/severe-wind swath footprint
│  ├─ IEC wind class
│  ├─ terrain/hub-height conversion
│  └─ cut-out/shutdown/protection logic
│
└─ DR≈0 reviewed buckets
   └─ turbines/components outside the damaging footprint or below threshold
```

### Why these failure-units?

Wind turbines are repeated structural systems. Extreme wind/tornado damage is usually concentrated in the turbine superstructure rather than evenly across all plant value.

The primary physical buckets are:

| Failure-unit | Reason |
|---|---|
| Blade | Direct aerodynamic loading, debris impact, blade strike, overspeed/feathering failure pathways |
| Tower | Structural support, buckling/collapse under extreme loading |
| Nacelle | Direct wind/debris loading and consequential damage after tower/blade failure |
| Foundation | Overturning/support/anchor failure; conditional because foundation may survive tower/blade damage |

Secondary buckets are reviewed, but not forced into weak default curves unless the evidence supports them.

---

## 3. X-axis decision

### Selected axis for straight-line/severe wind

```text
x-axis = hub-height 3-second gust speed
unit   = m/s
```

The curve is internally evaluated as:

```text
r = V_3s_hub / Ve50_class
```

This lets the same curve family shift by IEC design class.

### Why not site-level 10 m wind speed?

A wind farm is a tall structure. A 10 m weather-station wind value is not the load at the rotor/nacelle/tower. It may be useful as an upstream hazard input, but it needs a hub-height conversion before reaching this damage code.

### Why not one tornado EF category as the x-axis?

The EF scale is useful but imperfect. NOAA/NWS describes EF ratings as damage-estimated 3-second gust ranges, not direct measurements. EF ratings also depend on available damage indicators. Therefore EF can be used as a tornado proxy bridge, but the curve should still evaluate on a wind-speed proxy with clear uncertainty.

Source: https://www.weather.gov/grb/efscale

### Why not one whole-farm damage curve?

Because wind-farm loss depends on:

```text
1. per-turbine structural fragility,
2. which failure-unit is damaged,
3. how many turbines are inside the damaging footprint,
4. whether the event is straight-line wind or tornado/direct hit,
5. which value bucket is hit.
```

A whole-farm curve would bury those decisions and increase double-counting risk.

---

## 4. Design-speed bridge

IEC classes define turbine design environments. In v1.0 we use the following generic bridge:

```text
Ve50 = 1.4 × Vref
```

where:

```text
Vref  = 10-minute average reference wind speed at hub height
Ve50  = 50-year extreme 3-second gust at hub height
```

The workbook stores:

| IEC class | Vref m/s | Ve50 m/s | Ve50 mph |
|---|---:|---:|---:|
| IEC I | 50.0 | 70.0 | 156.6 |
| IEC II | 42.5 | 59.5 | 133.1 |
| IEC III | 37.5 | 52.5 | 117.4 |

Sources:

- DTU IEC 61400-1 explainer: https://wasp.dtu.dk/software/windfarm-assessment-tool/iec-61400-1
- Ashes IEC extreme wind equations: https://www.simis.io/docs/wind-iec-extreme-events
- DOE severe-weather article: https://www.energy.gov/cmei/wind/articles/how-do-wind-turbines-survive-severe-weather-and-storms

---

## 5. Evidence-to-parameter map

| Evidence | What it supports | How used |
|---|---|---|
| DOE severe-weather article | Cut-out, shutdown, feathering, yaw, typical IEC design gust context, direct tornado-hit caveat | Defines pitch/brake/yaw as conditioners and supports low-damage design anchor context |
| DTU IEC explainer | IEC class/load-case framing, extreme wind, gusts, yaw error, turbulence | Supports design class selector and operating state conditioning |
| Ashes IEC equations | `Ve50 = 1.4 × Vref` | Supports speed normalization |
| NOAA/NWS EF scale | EF 3-second gust ranges and caveat that EF is damage-estimated | Supports tornado proxy bridge and uncertainty flag |
| NASA Greenfield tornado | EF4 185 mph event downed wind turbines/power lines | High-severity case evidence, not a full curve |
| NIST fragility method | Damage-state/fragility/damage-matrix framework and no-double-counting logic | Supports bounded monotone fragility-style curve and dependency flags |
| Rice acceleration research | Acceleration-sensitive turbine subcomponents | Supports secondary acceleration/open-seam pathway |

---

## 6. Curve form decision

### Selected form

The structural curves use a bounded logistic fragility-style form:

```text
DR_i(V) = max_DR_i / (1 + exp[-k_i × (V/Ve50 - D50_ratio_i)])
```

where:

```text
V             = hub-height 3-second gust or tornado proxy bridge speed
Ve50          = IEC-class design gust bridge
D50_ratio_i   = design-normalized speed ratio where the component reaches 50% of max damage
k_i           = steepness on normalized speed ratio
max_DR_i      = maximum damage ratio for the value bucket
```

### Why logistic?

A logistic form is appropriate for v1.0 because this is a structural fragility problem with sparse public subsystem loss data. It is:

```text
bounded between 0 and max_DR,
monotone with wind speed,
smooth enough for interpolation,
parameter-light,
and compatible with future uncertainty/spread upgrades.
```

NIST's wind-induced loss framework supports the use of fragility curves, conditional probabilities, and damage matrices, with care not to double count or omit damage types.

Source: https://www.nist.gov/publications/fragility-curves-damage-matrices-and-wind-induced-loss-estimation

### Rejected alternatives

| Alternative | Why not selected for v1.0 |
|---|---|
| Step threshold | Too brittle; implies all turbines fail at a single speed. |
| Whole-farm percent-damage table | Hides failure-units, exposure, and value buckets. |
| Piecewise-state curve | Good for flood/electrical inundation, less natural for structural exceedance under wind. |
| Direct empirical claims curve | Not available publicly at the required component/failure-unit grain. |
| Full aeroelastic simulation | Best physics but not feasible as a generic cell-level damage code. |

---

## 7. v1.0 parameter set

| Curve ID | Failure-unit | max_DR | D50 ratio, straight-line | k ratio | tornado D50 shift |
|---|---|---:|---:|---:|---:|
| `WT_BLADE_STRUCT` | Blade structural/debris/blade strike | 1.00 | 1.38 | 12.0 | -0.10 |
| `WT_TOWER_STRUCT` | Tower buckling/collapse | 1.00 | 1.48 | 11.0 | -0.12 |
| `WT_NACELLE_CONSEQ` | Nacelle direct/consequential damage | 0.85 | 1.44 | 10.0 | -0.10 |
| `WT_FOUNDATION_OT` | Foundation overturning/support failure | 0.65 | 1.62 | 9.0 | -0.08 |
| `WT_POWER_ELEC_ACCEL` | Acceleration-sensitive power electronics | 0.30 | 1.20 | 8.0 | -0.05 |

The first four curves are in the default structural loss aggregate. `WT_POWER_ELEC_ACCEL` is stored as a secondary/open-seam pathway and is not included by default because acceleration response cannot be inferred reliably from wind speed alone.

---

## 8. How the tornado variant works

The tornado variant is **not** a new fully empirical tornado turbine curve. It is a direct-hit adjustment to the same structural fragility family:

```text
D50_tornado = D50_straight + tornado_d50_shift
```

Because shifts are negative, the tornado variant reaches damage at lower design-normalized speed ratios.

Why?

```text
tornado/direct-hit cases can involve:
  - rapidly changing wind direction,
  - intense turbulence,
  - debris impact,
  - non-synoptic wind fields,
  - yaw misalignment,
  - highly localized footprint.
```

The Greenfield EF4 case is evidence that direct-hit EF4 conditions can down wind turbines, but it does not provide a complete probability curve.

Source: https://science.nasa.gov/earth/earth-observatory/tornado-damage-in-greenfield-152870/

For farm-level loss, tornado must also use:

```text
exposed_turbine_fraction
```

because a tornado core usually affects only part of a wind farm.

---

## 9. Selectors, conditioners, and exposure variables

### Selectors

Selectors choose the curve family or speed scale.

| Selector | Role |
|---|---|
| `iec_wind_class` | Chooses `Ve50` and shifts the curve on absolute speed |
| `turbine_model_or_design_speed` | Overrides generic IEC class if available |
| `hub_height_m` | Used for hazard-height conversion |
| `rotor_diameter_m` / `blade_length_m` | Useful future selectors for load/geometry |

### Conditioners

Conditioners are event-time states that change vulnerability.

| Conditioner | Role |
|---|---|
| `operating_state` | operating / parked / curtailed / faulted |
| `feathered_state` | blade pitch protection state |
| `yaw_alignment` | aligned / yaw error / unknown |
| `brake_status` | brake available/failed/unknown |
| `grid_availability` | can matter for control/protection state |

In v1.0, these are recorded and used qualitatively. The generic numeric multipliers are **not** claimed as sourced.

### Exposure variables

Exposure controls how many turbines or which plant systems are affected.

| Exposure field | Role |
|---|---|
| `exposed_turbine_fraction` | fraction of turbine value in damaging footprint |
| `turbines_exposed_count` | explicit count alternative |
| `total_turbine_count` | denominator for exposure fraction |
| `substation_in_footprint` | whether shared plant systems are included |
| `collection_in_footprint` | whether collection/civil assets are included |

Exposure modifies value affected, not per-turbine fragility.

---

## 10. Value-link logic

For a wind farm:

```text
failure-unit DR
  × failure-unit value share
  × physical replaceable base
  × exposed turbine fraction
  = loss
```

Default v1.0 value buckets:

| Curve ID | Value bucket | Default share of physical base |
|---|---|---:|
| `WT_BLADE_STRUCT` | Rotor/blade value | 0.173 |
| `WT_TOWER_STRUCT` | Tower value | 0.169 |
| `WT_NACELLE_CONSEQ` | Nacelle value | 0.345 |
| `WT_FOUNDATION_OT` | Foundation/support value | 0.062 |
| `WT_POWER_ELEC_ACCEL` | Power electronics value | 0.037, not in default aggregate |

This keeps damage ratios separate from financial metrics. EAL/PML/TIV reporting belongs downstream.

---

## 11. Dependency / double-counting warning

Blade, tower, nacelle, and foundation damages are not fully independent.

Examples:

```text
tower collapse
   → nacelle damage likely consequential

blade strike
   → tower/nacelle damage may follow

foundation overturning
   → tower/nacelle/blades likely destroyed
```

v1.0 stores separate curves because the framework needs failure-unit records, but it flags dependency as an open seam. Future versions should replace the simple summation with a damage-state transition matrix when evidence supports it.

---

## 12. What v1.0 does not claim

This package does not claim:

```text
- a claims-calibrated wind-farm vulnerability curve,
- a universal OEM-independent turbine fragility,
- a measured tornado hub-height wind-speed curve,
- a fully independent sum of blade/tower/nacelle/foundation losses,
- or a final EAL/PML model.
```

It does claim:

```text
- a documented first derived curve family,
- proper cell/failure-unit/value-link structure,
- public-source-backed x-axis and curve-form rationale,
- explicit assumptions and update triggers,
- and a runtime-ready damage-code interface.
```
