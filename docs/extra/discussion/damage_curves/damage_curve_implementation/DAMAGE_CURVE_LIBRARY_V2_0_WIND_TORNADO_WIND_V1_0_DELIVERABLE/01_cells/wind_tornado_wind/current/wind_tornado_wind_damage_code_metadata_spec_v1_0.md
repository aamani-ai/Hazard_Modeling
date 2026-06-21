# Wind/tornado × wind farm — damage-code metadata spec v1.0

This document defines the runtime metadata contract for the `WIND_TORNADO_WIND` damage-code cell.

## Damage-code identity

```yaml
cell_id: WIND_TORNADO_WIND
cell_version: v1.0
asset_class: wind
hazard_family:
  - severe_wind
  - tornado
damage_code_type:
  - repeated_unit_structural_bundle
  - state_conditioned
  - exposure_geometry
```

## Failure-unit records

```yaml
failure_units:
  - curve_id: WT_BLADE_STRUCT
    subsystem: ROTOR_ASSEMBLY
    component: BLADE
    failure_mode: structural_overload_debris_blade_strike
    role: primary_nonzero

  - curve_id: WT_TOWER_STRUCT
    subsystem: TOWER
    component: TOWER_SECTION
    failure_mode: tower_buckling_collapse
    role: primary_nonzero

  - curve_id: WT_NACELLE_CONSEQ
    subsystem: NACELLE
    component: GEARBOX | GENERATOR_INTERNAL | YAW_SYSTEM
    failure_mode: nacelle_direct_or_consequential_damage
    role: primary_nonzero_dependency_sensitive

  - curve_id: WT_FOUNDATION_OT
    subsystem: FOUNDATION
    component: FOUNDATION_BASE
    failure_mode: overturning_anchor_support_failure
    role: conditional_primary

  - curve_id: WT_POWER_ELEC_ACCEL
    subsystem: POWER_ELECTRONICS
    component: POWER_CONVERTER
    failure_mode: acceleration_sensitive_converter_or_control_damage
    role: secondary_conditional_open_seam
```

## Hazard inputs

```yaml
hazard_inputs:
  preferred:
    - hub_height_3s_gust_mps

  tornado_bridge:
    - ef_rating
    - ef_gust_proxy_mph
    - ef_gust_proxy_mps

  optional_upstream:
    - ten_meter_3s_gust_mps
    - terrain_exposure
    - vertical_profile_exponent
    - tornado_swath_polygon
```

## Internal axis

```yaml
internal_axis:
  id: X_SPEED_RATIO_TO_IEC
  formula: r = V_3s_hub / Ve50_class
  unit: dimensionless
```

## Required selectors

```yaml
selectors:
  - field: iec_wind_class
    allowed: [IEC I, IEC II, IEC III, site_specific]
    default: IEC II
    role: chooses Ve50 and horizontal speed scale

  - field: turbine_model_or_design_speed
    allowed: free_text_or_numeric
    role: overrides generic IEC class where known

  - field: hub_height_m
    role: required if hazard speed is not already hub-height
```

## Recommended selectors

```yaml
recommended_selectors:
  - rotor_diameter_m
  - blade_length_m
  - rated_power_kw
  - survival_wind_speed_mps
  - turbine_manufacturer_model
```

## Conditioners

```yaml
conditioners:
  - field: operating_state
    allowed: [operating, parked, curtailed, faulted, unknown]
    role: changes load state

  - field: feathered_state
    allowed: [feathered, not_feathered, unknown]
    role: changes blade aerodynamic loading

  - field: yaw_alignment
    allowed: [aligned, yaw_error, unknown]
    role: changes lateral/oblique loading

  - field: brake_status
    allowed: [available, failed, unknown]
    role: overspeed/protection state

  - field: grid_availability
    allowed: [available, unavailable, unknown]
    role: can affect controls/protection
```

## Exposure variables

```yaml
exposure:
  - field: total_turbine_count
    unit: count

  - field: turbines_exposed_count
    unit: count

  - field: exposed_turbine_fraction
    unit: fraction_0_1
    formula: turbines_exposed_count / total_turbine_count

  - field: substation_in_footprint
    allowed: [yes, no, unknown]

  - field: collection_in_footprint
    allowed: [yes, no, unknown]
```

## Output object

```yaml
outputs:
  - failure_unit_damage_ratio
  - selected_curve_variant
  - selected_iec_class
  - speed_ratio_to_iec
  - exposure_fraction_used
  - dependency_flags
  - source_confidence
  - open_seams
```

## Notes

This damage code returns severity. Hazard frequency, EAL, PML, insured deductibles, and final financial metrics are downstream.
