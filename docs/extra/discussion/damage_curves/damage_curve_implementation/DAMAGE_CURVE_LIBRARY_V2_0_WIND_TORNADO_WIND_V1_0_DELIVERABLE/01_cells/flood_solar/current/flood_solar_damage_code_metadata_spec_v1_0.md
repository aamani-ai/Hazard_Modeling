# Flood × Solar Damage-Code Metadata Spec — v1.0

**Damage-code family:** `FLOOD_SOLAR`  
**Version:** `v1.0`  
**Purpose:** define inputs, selectors, conditioners, exposure variables, failure-units, and outputs for direct physical flood damage to solar PV assets.

---

## 1. Design principle

Flood damage code should not ask for one plant-level flood score. It should compute local exposure for each relevant failure-unit.

```text
water surface elevation
      │
      ▼
local depth above component datum
      │
      ▼
failure-unit DR
      │
      ▼
downstream loss engine applies value
```

---

## 2. Required hazard inputs

| Field | Type | Unit | Required | Notes |
|---|---|---:|---|---|
| `water_surface_elevation_m` | number | m | preferred | Absolute WSE in the same vertical datum as equipment elevations. |
| `site_flood_depth_m` | number | m | accepted fallback | Local depth above grade if absolute WSE is unavailable. |
| `flow_velocity_mps` | number | m/s | conditional | Needed for scour/foundation/civil pathways. |
| `duration_hr` | number | hr | optional/deferred | Conditioner/open seam in v1.0; not default second axis. |
| `contamination_class` | enum | n/a | optional | fresh / brackish / salt / sewage / chemical / unknown. |

---

## 3. Required exposure geometry

| Field | Applies to | Unit | Notes |
|---|---|---:|---|
| `component_critical_elevation_m` | all depth-driven electrical units | m | Vulnerable datum for cabinet entry, terminals, electronics, or cable entry. |
| `equipment_pad_elevation_m` | inverter, switchgear, transformer | m | May be used to infer critical elevation. |
| `module_lower_edge_elevation_m` | PV modules | m | Required if module submersion pathway is enabled. |
| `cable_trench_or_pullbox_elevation_m` | collection/conduit path | m | Needed for conduit water-path logic. |
| `fraction_value_exposed` | all units | fraction | Fraction of value bucket in the flood swath or below waterline. |

Exposure transform:

```text
h_i = max(0, WSE - z_i_crit)
```

When only site depth above grade is available:

```text
h_i = max(0, site_depth_m - component_critical_height_above_grade_m)
```

---

## 4. Selectors

Selectors are static asset attributes that choose or shift the curve family.

| Selector | Example values | Role |
|---|---|---|
| `enclosure_rating` | NEMA 3R, 4, 4X, 6, 6P, IP65, IP67, unknown | Determines whether equipment is rain/hosedown-protected or submersion-rated. |
| `transformer_type` | liquid_filled, dry_type, cast_resin, unknown | Selects transformer curve variant. |
| `cable_location_rating` | wet_location, dry_location, direct_burial, unknown | Selects cable/conduit curve variant. |
| `equipment_mounting` | pad_mount, skid_mount, elevated_platform, rooftop, unknown | Helps infer critical elevation. |
| `substation_configuration` | outdoor_yard, indoor_control_house, containerized, unknown | Helps select switchgear/control cabinet exposure. |

---

## 5. Conditioners

Conditioners are event-time states. They can adjust severity or add flags, but they are not the primary x-axis in v1.0.

| Conditioner | Example values | Role |
|---|---|---|
| `energized_state` | energized, deenergized, isolated, unknown | Energized equipment may have greater damage/safety consequences. |
| `shutdown_before_flood` | true, false, unknown | Supports conditioner logic; not a substitute for water exposure. |
| `conduit_water_path_present` | true, false, unknown | Can bring water to equipment even when cabinet is elevated. |
| `flood_defense_deployed` | true, false, n/a, unknown | Exposure modifier. |
| `drainage_clear` | true, false, unknown | Exposure modifier. |
| `duration_hr` | numeric | Deferred conditioner; may become second axis later. |
| `salinity_or_contamination` | fresh, salt, sewage, chemical, unknown | Open seam; may affect replacement/reconditioning. |

---

## 6. Failure-unit records

| ID | Subsystem | Component | Axis | v1.0 status |
|---|---|---|---|---|
| `FS_INV` | `INVERTER_SYSTEM` | `INVERTER` | local depth above inverter critical datum | primary |
| `FS_SWG` | `SUBSTATION` | `SWITCHGEAR` | local depth above switchgear critical datum | primary |
| `FS_XFMR` | `SUBSTATION` | `TRANSFORMER_MAIN` | local depth above transformer control/terminal datum | primary |
| `FS_COMB` | `INVERTER_SYSTEM` | `COMBINER_BOX + DC_PROTECTION` | local depth above enclosure datum | primary/secondary |
| `FS_SCADA` | `SCADA` | `MONITORING_SYSTEM` | local depth above control cabinet datum | secondary |
| `FS_CABLE` | `ELECTRICAL_COLLECTION` | `CABLE_AC + CABLE_DC` | depth/pathway/termination exposure | conditional secondary |
| `FS_FOUND` | `FOUNDATION` | `FOUNDATION_BASE` | velocity/scour proxy | conditional secondary |
| `FS_PVMOD` | `PV_ARRAY` | `PV_MODULE` | depth above module lower edge | conditional secondary |

---

## 7. Outputs

| Output | Type | Notes |
|---|---|---|
| `failure_unit_damage_ratio` | number 0–1 | Main output per failure-unit. |
| `curve_id` | string | Which curve/variant was used. |
| `curve_version` | string | `v1.0` for this package. |
| `local_depth_m` | number | Computed local depth used for electrical curves. |
| `selector_flags` | object/list | Enclosure rating, transformer type, cable rating. |
| `conditioner_flags` | object/list | Energized state, conduit path, duration, contamination. |
| `open_seam_flags` | object/list | Missing metadata or unsupported condition. |
| `evidence_tier` | enum | source_anchored_engineering_parameterization / claims_calibrated / placeholder. |

---

## 8. Example damage-code object

```yaml
damage_code_id: FLOOD_SOLAR_ELECTRICAL_INUNDATION_V1
hazard_asset_pair: flood_x_solar
version: v1.0
primary_axis:
  id: FLOOD_LOCAL_DEPTH_COMPONENT_DATUM
  formula: h_i = max(0, WSE - z_i_crit)
failure_units:
  - id: FS_INV
    subsystem: INVERTER_SYSTEM
    component: INVERTER
    curve: inverter_depth_state_curve_v1
    required_metadata:
      - component_critical_elevation_m
      - enclosure_rating
      - fraction_value_exposed
  - id: FS_SWG
    subsystem: SUBSTATION
    component: SWITCHGEAR
    curve: switchgear_depth_state_curve_v1
  - id: FS_XFMR
    subsystem: SUBSTATION
    component: TRANSFORMER_MAIN
    curve: transformer_depth_state_curve_v1
secondary_failure_units:
  - FS_COMB
  - FS_SCADA
  - FS_CABLE
  - FS_FOUND
  - FS_PVMOD
outputs:
  - failure_unit_damage_ratio
  - local_depth_m
  - curve_version
  - metadata_flags
```

---

## 9. Non-goals

This damage code does **not** own:

```text
EAL
PML
return-period loss
portfolio aggregation
policy terms
business interruption
repair downtime
contingent business interruption
```

Those belong downstream. This code emits the right **damage ratio at the right granularity**.
