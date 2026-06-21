# Wind / tornado × wind farm — cell README v0.1

**Cell ID:** `WIND_TORNADO_WIND`  
**Package status:** v0.1 scaffold — coverage, x-axis, metadata, evidence plan, and curve-form architecture.  
**Curve status:** no final derived damage curves yet. This package is deliberately a scaffold so v1.0 can focus on source curation and fitting.

---

## 1. Purpose of this cell

This cell expands the damage-curve library from solar assets into **wind farm structural / repeated-unit damage**.

The purpose is not to create a single wind-farm loss percentage. The purpose is to define the right **damage-code granularity**:

```text
hazard intensity / wind field
      │
      ▼
per-turbine failure-unit curves
      │
      ├─ blade / rotor damage
      ├─ tower collapse / buckling
      ├─ nacelle damage
      ├─ foundation / support failure
      └─ secondary shared-plant damage, if footprint hits it
      │
      ▼
exposure aggregation across turbines and plant-scope systems
```

The wind-farm case is different from both prior worked examples:

| Prior cell | What it taught | What wind/tornado × wind adds |
|---|---|---|
| `hail × solar` | Single-primary failure-unit and material-share exposure | Repeated turbines and structural failure |
| `flood × solar` | Multi-failure-unit electrical/elevation geometry | Turbine-level structural curves plus swath exposure |
| `wind/tornado × wind` | New cell | Repeated units, turbine operating-state conditioners, tower/blade/nacelle/foundation assembly rules |

---

## 2. Snapshot coverage tree

```text
strong wind / tornado × wind v0.1
├─ primary nonzero failure-units
│  ├─ ROTOR_ASSEMBLY / BLADE / structural overload, blade strike, debris impact
│  ├─ TOWER / TOWER_SECTION / local buckling, collapse, shell instability
│  ├─ NACELLE / drivetrain-generator-housing / direct or consequential damage
│  └─ FOUNDATION / FOUNDATION_BASE / overturning, anchor, support failure
│
├─ conditioner-only equipment / states
│  ├─ PITCH_SYSTEM / PITCH_DRIVE / feathering state
│  ├─ BRAKE_SYSTEM / MECHANICAL_BRAKE / emergency stop or parked state
│  ├─ NACELLE / YAW_SYSTEM / yaw alignment or yaw error
│  └─ turbine operating state / operating, parked, curtailed, faulted
│
├─ secondary / conditional units
│  ├─ POWER_ELECTRONICS / POWER_CONVERTER
│  ├─ SCADA / MONITORING_SYSTEM
│  ├─ ELECTRICAL_COLLECTION / CABLE_AC
│  ├─ SUBSTATION / TRANSFORMER_MAIN + SWITCHGEAR
│  └─ CIVIL_INFRA / roads-access-fencing, if footprint/debris affects them
│
├─ exposure / protection modifiers
│  ├─ turbine exposure fraction or exposed turbine count
│  ├─ tornado / severe-wind swath footprint
│  ├─ IEC wind class / Vref / design selector
│  ├─ terrain exposure and hub-height conversion
│  └─ cut-out / shutdown / protection logic
│
└─ DR≈0 reviewed buckets
   └─ turbines/components outside the damaging footprint or below threshold
```

This snapshot is intentionally not a curve. It is the identity map that tells the derivation pass what needs a curve, what is a conditioner, what is only exposure geometry, and what is reviewed out.

---

## 3. Main modeling decision

Do **not** model:

```text
wind speed → whole wind farm DR
```

Model instead:

```text
wind / tornado intensity
      │
      ├─ blade structural damage curve
      ├─ tower structural damage curve
      ├─ nacelle damage / dependency curve
      ├─ foundation support curve, if sourceable
      └─ shared plant damage, conditional on footprint

plus:
      turbine exposure fraction / exposed turbine count
      operating-state conditioners
      design-class selectors
```

The damage code should be per **failure-unit**, and the downstream exposure engine should decide how many turbines and which plant-scope systems are actually in the damaging footprint.

---

## 4. Primary x-axis decision

The v0.1 decision is to keep two related but distinguishable wind pathways:

| Pathway | Primary operational x-axis | Why |
|---|---|---|
| Straight-line / hurricane / severe synoptic wind | Hub-height 3-second gust speed | Structural damage is gust/load driven; gust speed can usually be gridded or converted from hazard products. |
| Tornado | Tornado wind speed proxy, or EF-scale bridge if no continuous wind field is available | Tornadoes have rapid direction changes, strong spatial gradients, vertical components, debris, and compact footprints. |

Design class variables such as `IEC wind class`, `Vref`, and turbine survival/design ratings are **selectors/anchors**, not the event x-axis.

Swath footprint and number of turbines exposed are **exposure geometry**, not damage-curve x-axes.

---

## 5. v0.1 deliverables

This folder contains:

```text
current/
├─ README_wind_tornado_wind_v0_1.md
├─ wind_tornado_wind_damage_code_metadata_spec_v0_1.md
├─ wind_tornado_wind_curve_derivation_dossier_v0_1.md
├─ workbook_sheet_manifest_wind_tornado_wind_v0_1.md
├─ CELL_DOCUMENTATION_CROSSWALK_wind_tornado_wind_v0_1.md
└─ damage_curve_records_v0_1_wind_tornado_wind.xlsx
```

The workbook is the structured build artifact. The Markdown files explain the decisions, alternatives, and next derivation work.

---

## 6. What v1.0 must add

v1.0 should replace this scaffold with actual source-curated curve records:

```text
1. Decide whether tornado and straight-line wind use separate curve families.
2. Pull source anchors for blade, tower, nacelle, and foundation response.
3. Choose curve forms per failure-unit, not by copying hail/flood.
4. Define assembly precedence to avoid double-counting tower/nacelle/rotor losses.
5. Quantify how IEC class / Vref shifts or selects curve families.
6. Quantify how feathered/yaw/brake/parked states condition curves.
7. Add source-to-parameter mapping and assumption register.
8. Produce dashboard plots and curve-data tables.
```

---

## 7. Source links used in v0.1

- DOE/EERE severe-storm operations and feather/yaw/cut-out logic: https://www.energy.gov/eere/articles/how-do-wind-turbines-survive-severe-storms
- IEC 61400-1 design requirements summary: https://webstore.ansi.org/standards/iec/iec61400eden2019
- DTU/WAsP explanation of IEC 61400-1 classes/load cases: https://wasp.dtu.dk/software/windfarm-assessment-tool/iec-61400-1
- NWS Enhanced Fujita scale: https://www.weather.gov/grb/efscale
- NASA Greenfield tornado event summary: https://science.nasa.gov/earth/earth-observatory/tornado-damage-in-greenfield-152870/
- Greenfield wind turbine structural failure analysis candidate: https://www.sciencedirect.com/science/article/pii/S1350630725011288
