# Wind/tornado × wind farm — damage-curve cell README v1.0

**Cell:** `WIND_TORNADO_WIND`  
**Library release:** `v2.0`  
**Cell version:** `v1.0 derived curves`  
**Workbook:** `damage_curve_records_v1_0_wind_tornado_wind.xlsx`

This cell is the first wind-farm structural/repeated-unit cell in the damage-curve library. It should be read after the global method docs, especially:

```text
00_global_method/13_end_to_end_damage_work_architecture.md
00_global_method/14_coverage_role_taxonomy.md
00_global_method/15_wind_tornado_wind_reference_pattern.md
```

## What this cell does

This cell does **not** model:

```text
wind speed → whole wind farm damage ratio
```

It models:

```text
wind / tornado intensity
   │
   ├─ blade structural damage curve
   ├─ tower structural damage curve
   ├─ nacelle consequential/direct damage curve
   ├─ foundation support / overturning curve
   └─ optional acceleration-sensitive electronics pathway

plus:
   ├─ turbine design class selector
   ├─ pitch / brake / yaw / operating-state conditioners
   └─ exposed turbine fraction / swath exposure modifier
```

## One-screen snapshot

```text
strong wind / tornado × wind v1.0
├─ primary nonzero failure-units
│  ├─ ROTOR_ASSEMBLY / BLADE / structural overload, blade strike, debris impact
│  ├─ TOWER / TOWER_SECTION / local buckling, collapse, shell instability
│  ├─ NACELLE / drivetrain-generator-housing / direct or consequential damage
│  └─ FOUNDATION / FOUNDATION_BASE / overturning, anchor, support failure
│
├─ conditioner-only equipment / states
│  ├─ PITCH_SYSTEM / PITCH_DRIVE / feathering state
│  ├─ BRAKE_SYSTEM / MECHANICAL_BRAKE / parked / emergency stop state
│  ├─ NACELLE / YAW_SYSTEM / yaw alignment or yaw error
│  └─ turbine operating state / operating, parked, curtailed, faulted
│
├─ secondary / conditional units
│  ├─ POWER_ELECTRONICS / POWER_CONVERTER / acceleration-sensitive response
│  ├─ SCADA / MONITORING_SYSTEM / control outage or cabinet damage
│  ├─ ELECTRICAL_COLLECTION / CABLE_AC / collection damage in footprint
│  ├─ SUBSTATION / TRANSFORMER_MAIN + SWITCHGEAR / only if footprint includes it
│  └─ CIVIL_INFRA / roads-access-fencing / debris or access damage
│
├─ exposure / protection modifiers
│  ├─ turbine exposure fraction or exposed turbine count
│  ├─ tornado / severe-wind swath footprint
│  ├─ IEC wind class / Vref / design selector
│  ├─ hub-height conversion
│  └─ cut-out / shutdown / protection logic
│
└─ DR≈0 reviewed buckets
   └─ turbines/components outside the damaging footprint or below threshold
```

## Core x-axis

The v1.0 straight-line/severe wind curve uses:

```text
x-axis = hub-height 3-second gust speed
```

The internal fit is normalized:

```text
r = V_3s_hub / Ve50_class
```

where `Ve50_class` is the IEC-class 50-year extreme 3-second gust bridge:

```text
Ve50 = 1.4 × Vref
```

The tornado pathway is separated as a **proxy bridge**:

```text
EF rating / EF wind estimate
   → EF 3-second gust proxy
   → design-normalized speed ratio
   → tornado direct-hit adjusted variant
```

EF-scale speeds are damage-estimated 3-second gust ranges, not direct turbine-level wind measurements.

## Curve form

The v1.0 structural curves use a bounded logistic fragility-style form:

```text
DR_i(V) = max_DR_i / (1 + exp[-k_i × (V/Ve50 - D50_ratio_i)])
```

This is not because every future wind curve must be logistic. It is because this cell is a structural-overload fragility problem with limited public subsystem loss data. The logistic form is monotonic, bounded, and easy to parameterize from design anchors plus high-severity case evidence.

## Default v1.0 curves

| Curve ID | Failure-unit | Role | Included in default loss aggregate? |
|---|---|---:|---:|
| `WT_BLADE_STRUCT` | Rotor blade structural/debris/blade strike | Primary | Yes |
| `WT_TOWER_STRUCT` | Tower buckling/collapse | Primary | Yes |
| `WT_NACELLE_CONSEQ` | Nacelle direct/consequential damage | Primary, dependency-sensitive | Yes |
| `WT_FOUNDATION_OT` | Foundation overturning/support/anchor failure | Conditional primary | Yes |
| `WT_POWER_ELEC_ACCEL` | Converter/control acceleration-sensitive pathway | Secondary/open seam | No |

## Important caveats

This is a **public-source-derived v1.0 curve package**, not a private claims-calibrated wind-turbine fragility product. The workbook and derivation dossier are intentionally explicit about which parts are source-supported and which are engineering-fit assumptions.

The main load-bearing assumptions are:

```text
1. IEC Class II is the generic default selector.
2. Structural damage can be represented by design-normalized logistic curves.
3. D50/k values are engineering-fit parameters anchored to design speeds and EF4 case evidence.
4. Tornado direct-hit behavior is represented by a curve shift plus exposure fraction.
5. Nacelle/foundation dependence on blade/tower damage is flagged but not yet a full dependency matrix.
```

## Source links used in this cell

- DOE / Energy.gov — wind turbines in severe weather: https://www.energy.gov/cmei/wind/articles/how-do-wind-turbines-survive-severe-weather-and-storms
- DTU IEC 61400-1 explainer: https://wasp.dtu.dk/software/windfarm-assessment-tool/iec-61400-1
- Ashes IEC extreme wind equations: https://www.simis.io/docs/wind-iec-extreme-events
- NOAA/NWS Enhanced Fujita scale: https://www.weather.gov/grb/efscale
- NASA Earth Observatory Greenfield tornado: https://science.nasa.gov/earth/earth-observatory/tornado-damage-in-greenfield-152870/
- NIST fragility/damage matrix methodology: https://www.nist.gov/publications/fragility-curves-damage-matrices-and-wind-induced-loss-estimation
- Rice / Dueñas-Osorio acceleration-sensitive turbine components: https://duenas-osorio.rice.edu/sisrra/current-projects-and-sponsors/long-term-unavailability-wind-turbines-wind-induced-accelerations
