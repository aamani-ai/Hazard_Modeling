# Flood × Solar Damage-Code Metadata Spec v0.1

**Cell:** `FLOOD_SOLAR`  
**Status:** v0.1 schema / metadata scaffold  
**Goal:** define the inputs, selectors, conditioners, exposure variables, and outputs needed for flood damage codes for solar PV assets.

---

## 1. Damage-code interface philosophy

The damage code should return **damage ratios at the correct failure-unit grain**. It should not perform full EAL, PML, TIV reporting, portfolio aggregation, or policy-metric logic.

```text
hazard catalog / site model
       │
       ▼
flood damage code
       │
       ├─ reads hazard inputs
       ├─ reads component metadata
       ├─ computes failure-unit DRs
       └─ emits DR + metadata flags
       │
       ▼
valuation / metrics layer
       └─ applies DR to value buckets and computes financial metrics
```

---

## 2. Canonical hazard inputs

```yaml
hazard_axis:
  primary_depth_axis:
    id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    definition: max(0, water_surface_elevation_m - component_critical_elevation_m)
    unit: m
    role: primary x-axis for electrical ingress / inundation

  absolute_water_surface:
    id: WATER_SURFACE_ELEVATION
    unit: m
    datum_required: true
    role: upstream hazard input before component exposure transform

  local_flood_depth:
    id: LOCAL_FLOOD_DEPTH_ABOVE_GRADE
    unit: m
    role: fallback if component elevations are expressed above local grade

  velocity_axis:
    id: FLOOD_FLOW_VELOCITY
    unit: m/s
    role: primary x-axis for scour / erosion / debris-velocity pathways

  duration_axis:
    id: INUNDATION_DURATION
    unit: hr
    role: conditioner or deferred axis in v0.1

  contamination_axis:
    id: FLOODWATER_CONTAMINATION_CLASS
    values: [fresh_clean, sediment_laden, sewage_chemical, salt_brackish, unknown]
    role: conditioner
```

---

## 3. Exposure geometry variables

These variables are the heart of the flood cell. They convert a site flood elevation into component-specific exposure.

```yaml
exposure_geometry:
  site_datum:
    type: string
    examples: [NAVD88, local_site_grade, plant_datum]
    required: true_if_absolute_elevations_used

  water_surface_elevation_m:
    type: number
    required: true_if_absolute_elevations_used

  local_flood_depth_above_grade_m:
    type: number
    required: true_if_no_absolute_datum

  component_critical_elevation_m:
    type: number
    required: true_for_depth_driven_curves
    description: elevation at which floodwater reaches the vulnerable part of the component

  pad_or_skid_elevation_m:
    type: number
    role: common source for component critical elevation

  water_depth_above_component_m:
    formula: max(0, water_surface_elevation_m - component_critical_elevation_m)
    output: true

  exposure_fraction:
    type: number
    range: [0, 1]
    description: fraction of units/value bucket exposed to the relevant flood condition
```

ASCII:

```text
absolute WSE
   │
   ├─ compare with inverter critical elevation
   ├─ compare with switchgear critical elevation
   ├─ compare with transformer/control elevation
   └─ compare with combiner/SCADA elevation
        │
        ▼
component-specific depth above datum
```

---

## 4. Fixed selectors

Selectors are asset attributes that choose, shift, or cap a curve. They are not event states.

| Selector | Applies to | Why it matters |
|---|---|---|
| `NEMA_type` | inverters, switchgear, combiner boxes, cabinets | Distinguishes rain/hosedown-rated vs submersion-rated enclosures. |
| `IP_rating` | electronics/enclosures | Helps classify ingress resistance where IP data is available. |
| `inverter_topology` | inverter | Central/skid/string architecture affects exposure and unit count. |
| `transformer_type` | transformer | Dry/oil-filled/pad-mounted/control-cabinet configuration affects recovery path. |
| `switchgear_type` | switchgear | Metal-clad, pad-mounted, outdoor cabinet, control-house. |
| `cable_burial_type` | collection | Direct-buried, conduit, trench, aboveground tray. |
| `conduit_sealing_type` | collection/enclosures | Determines whether floodwater can travel through conduit to equipment. |
| `foundation_type` | foundation/racking | Driven pile, helical pile, ballast, pad. |
| `soil_erodibility_class` | foundation/civil | Affects scour and erosion vulnerability. |

---

## 5. Event-time conditioners

Conditioners can change severity during a specific event.

| Conditioner | Applies to | Why it matters |
|---|---|---|
| `energized_state` | electrical equipment | Energized equipment exposed to water can have worse damage/safety outcomes. |
| `shutdown_before_flood` | inverter/substation | May reduce electrical fault damage, but not water contamination/corrosion. |
| `inundation_duration_hr` | all flooded equipment | Longer exposure may worsen corrosion/contamination and recovery. |
| `contamination_class` | electrical equipment, cables | Salt, sewage, chemicals, and sediment can change replacement/reconditioning logic. |
| `drainage_clear` | site drainage/conduit | Blocked drainage increases exposure. |
| `flood_defense_deployed` | berms, barriers, pumps | Changes water reaching equipment. |
| `post_event_reconditionability` | electrical equipment | Determines replacement vs reconditioning output state. |

---

## 6. Failure-unit records

```yaml
failure_units:
  - id: FLOOD_SOLAR_INVERTER_INUNDATION
    subsystem: INVERTER_SYSTEM
    component: INVERTER
    role: primary_nonzero
    x_axis_id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    value_bucket: INVERTER_SYSTEM / INVERTER
    selectors: [NEMA_type, IP_rating, inverter_topology]
    conditioners: [energized_state, shutdown_before_flood, inundation_duration_hr, contamination_class]
    exposure_geometry: [component_critical_elevation_m, pad_or_skid_elevation_m, exposure_fraction]
    output: inverter_damage_ratio

  - id: FLOOD_SOLAR_SWITCHGEAR_INUNDATION
    subsystem: SUBSTATION
    component: SWITCHGEAR
    role: primary_nonzero
    x_axis_id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    value_bucket: SUBSTATION / SWITCHGEAR
    selectors: [NEMA_type, IP_rating, switchgear_type]
    conditioners: [energized_state, shutdown_before_flood, inundation_duration_hr, contamination_class]
    output: switchgear_damage_ratio

  - id: FLOOD_SOLAR_TRANSFORMER_INUNDATION
    subsystem: SUBSTATION
    component: TRANSFORMER_MAIN
    role: primary_nonzero
    x_axis_id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    value_bucket: SUBSTATION / TRANSFORMER_MAIN
    selectors: [transformer_type, control_cabinet_elevation, oil_filled_flag]
    conditioners: [energized_state, contamination_class, inundation_duration_hr]
    output: transformer_damage_ratio

  - id: FLOOD_SOLAR_COMBINER_DC_PROTECTION_INUNDATION
    subsystem: INVERTER_SYSTEM
    component: COMBINER_BOX / DC_PROTECTION
    role: primary_or_secondary_nonzero
    x_axis_id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    value_bucket: INVERTER_SYSTEM / COMBINER_BOX + DC_PROTECTION
    selectors: [NEMA_type, IP_rating, enclosure_mount_height]
    conditioners: [energized_state, contamination_class, inundation_duration_hr]
    output: combiner_dc_protection_damage_ratio

  - id: FLOOD_SOLAR_SCADA_CABINET_INUNDATION
    subsystem: SCADA
    component: MONITORING_SYSTEM
    role: secondary_nonzero
    x_axis_id: FLOOD_DEPTH_ABOVE_COMPONENT_DATUM
    value_bucket: SCADA / MONITORING_SYSTEM
    selectors: [cabinet_rating, enclosure_mount_height]
    conditioners: [energized_state, contamination_class, duration_hr]
    output: scada_damage_ratio

  - id: FLOOD_SOLAR_COLLECTION_CONDUIT_WATER_PATH
    subsystem: ELECTRICAL_COLLECTION
    component: CABLE_AC / CABLE_DC
    role: secondary_conditional
    x_axis_id: FLOOD_DEPTH_ABOVE_CONDUIT_ENTRY or WATER_PATH_PRESENT
    value_bucket: ELECTRICAL_COLLECTION
    selectors: [cable_burial_type, conduit_sealing_type, trenching_type]
    conditioners: [duration_hr, contamination_class]
    output: collection_damage_ratio_or_path_modifier

  - id: FLOOD_SOLAR_FOUNDATION_SCOUR
    subsystem: FOUNDATION
    component: FOUNDATION_BASE
    role: conditional_nonzero
    x_axis_id: FLOOD_FLOW_VELOCITY or DEPTH_VELOCITY_PROXY
    value_bucket: FOUNDATION
    selectors: [foundation_type, soil_erodibility_class, slope_position]
    conditioners: [duration_hr, debris_loading]
    output: foundation_scour_damage_ratio
```

---

## 7. Output contract

The damage code should emit:

```yaml
outputs:
  required:
    - failure_unit_id
    - damage_ratio
    - x_axis_value_used
    - x_axis_unit
    - subsystem
    - component
    - value_bucket_id
    - basis_note
    - exposure_fraction
    - assumption_flags
    - source_curve_id

  optional:
    - replacement_vs_recondition_state
    - downtime_state
    - confidence_tier
    - open_seam_ids
    - curve_variant_id
```

The financial layer can then compute:

```text
loss_i = DR_i × value_bucket_i × exposure_fraction_i
```

The damage code should not silently apply DR to the whole asset TIV.

---

## 8. Required future metadata signals

This cell tells us that the following metadata fields are worth capturing in the engineering / resiliency layer:

```text
equipment elevations:
    inverter pad, switchgear, transformer control cabinet, combiner box, SCADA cabinet

flood protection:
    berm height, floodwall height, drainage capacity, pump availability, flood-defense deployment

electrical protection:
    NEMA type, IP rating, enclosure type, conduit sealing, cable routing

operating state:
    energized / shutdown, warning lead time, operator action, reconditioning policy

site conditions:
    flow velocity, slope position, soil erodibility, drainage bottlenecks, ponding areas
```
