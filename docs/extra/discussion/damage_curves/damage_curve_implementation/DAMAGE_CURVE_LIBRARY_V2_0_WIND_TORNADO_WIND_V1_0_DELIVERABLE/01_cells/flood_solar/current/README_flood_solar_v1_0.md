# Flood × Solar Damage Curve Cell — v1.0

**Cell:** `FLOOD_SOLAR`  
**Version:** `v1.0`  
**Status:** public-source-anchored derived curve package  
**Primary purpose:** define the right damage-code granularity, x-axes, metadata, and curve records for flood damage to solar PV assets.

This cell intentionally does **not** create one generic plant-level flood curve. Flood damage in solar is driven by local equipment exposure: inverters, switchgear, transformer controls, combiner/DC protection, SCADA cabinets, cable/conduit pathways, and conditional module/foundation pathways can each have different exposure datums and different replacement logic.

```text
flood × solar v1.0
├─ primary nonzero depth-driven electrical failure-units
│  ├─ INVERTER_SYSTEM / INVERTER / cabinet-skid inundation
│  ├─ SUBSTATION / SWITCHGEAR / cabinet inundation
│  ├─ SUBSTATION / TRANSFORMER_MAIN / transformer-control inundation
│  ├─ INVERTER_SYSTEM / COMBINER_BOX + DC_PROTECTION / enclosure inundation
│  └─ SCADA / MONITORING_SYSTEM / control-cabinet inundation
│
├─ conditional / secondary failure-units
│  ├─ ELECTRICAL_COLLECTION / CABLE_AC + CABLE_DC / conduit-trench water path
│  ├─ FOUNDATION / FOUNDATION_BASE / scour or wet-soil support degradation
│  ├─ CIVIL_INFRA / roads-access-fencing / erosion or debris
│  ├─ PV_ARRAY / PV_MODULE / total submersion or debris impact
│  └─ MOUNTING / RACKING_STRUCTURE / debris-velocity load, if applicable
│
├─ protection / exposure modifiers
│  ├─ SITE_DRAINAGE / DRAINAGE_SYSTEM / capacity exceedance
│  ├─ SITE_DRAINAGE / FLOOD_DEFENSE / overtopping or failure
│  ├─ equipment pad elevation and freeboard
│  ├─ conduit slope, drain path, and sealing
│  └─ shutdown / energized state before inundation
│
└─ DR≈0 direct-flood buckets in v1.0
   └─ equipment above waterline with no alternate conduit/water-ingress path
```

## Current files

| File | Purpose |
|---|---|
| `damage_curve_records_v1_0_flood_solar.xlsx` | Main structured workbook: coverage, evidence, curve parameters, value links, curve data, dashboard, QA. |
| `flood_solar_curve_derivation_dossier_v1_0.md` | Detailed proof trail: source evidence → x-axis decision → curve form → parameters → adjustment rules. |
| `flood_solar_damage_code_metadata_spec_v1_0.md` | Damage-code input/output contract and required metadata. |
| `workbook_sheet_manifest_flood_solar_v1_0.md` | Workbook sheet-by-sheet map. |
| `CELL_DOCUMENTATION_CROSSWALK_flood_solar_v1_0.md` | Crosswalk from global documentation standard to this cell package. |

## Read order

```text
1. README_flood_solar_v1_0.md
2. flood_solar_curve_derivation_dossier_v1_0.md
3. flood_solar_damage_code_metadata_spec_v1_0.md
4. damage_curve_records_v1_0_flood_solar.xlsx
```

## Core modeling decisions

| Decision | v1.0 treatment |
|---|---|
| Workflow unit | Hazard × asset cell: `flood × solar`. |
| Curve-record unit | Failure-unit, not subsystem-only and not whole-plant. |
| Primary x-axis | `FLOOD_LOCAL_DEPTH_COMPONENT_DATUM`: local water depth above each component's critical elevation. |
| Secondary x-axis | `FLOOD_VELOCITY_SCOUR_PROXY`: velocity/scour pathway for foundations/civil assets. |
| Curve form | Piecewise-linear / state curve. Flood equipment damage is threshold-like, not naturally logistic. |
| Exposure `f` kind | Site geometry / elevation, not material/BOM share. |
| EAL / PML / tail | Not owned by this package; downstream hazard catalog and financial model handle those metrics. |

## Source basis

The primary public sources are:

- DOE/FEMP, **Preventing and Mitigating Flood Damage to Solar Photovoltaic Systems**: https://www.energy.gov/femp/preventing-and-mitigating-flood-damage-solar-photovoltaic-systems
- NEMA, **Evaluating Water-Damaged Electrical Equipment**: https://www.nema.org/standards/view/evaluating-water-damaged-electrical-equipment
- NEMA, **NEMA Enclosure Types**: https://www.nema.org/docs/default-source/products-document-library/nema-enclosure-types.pdf
- FEMA / Building America Solution Center, **Protecting Building Utility Systems From Flood Damage**: https://basc.pnnl.gov/library/protecting-building-utility-systems-flood-damage-principles-and-practices-design-and
- USACE HEC-FIA, **Depth-Percent Damage Relationships**: https://www.hec.usace.army.mil/confluence/fiadocs/fiatechref/latest/direct-damage/depth-percent-damage-relationships-direct-damage

## Important caveat

The v1.0 curves are **public-source-anchored engineering parameterizations**, not claims-calibrated empirical loss curves. The package is designed so the same records can be replaced or tightened when claims, forensic, OEM, or site-specific engineering data becomes available.
