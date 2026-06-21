# Damage-Code Metadata Spec — `<hazard> × <asset>` `<version>`

## 1. Damage-code identity

```yaml
damage_code_id: <ID>
cell_id: <hazard_asset>
version: <version>
status: draft | reviewable | site_adaptable | calibrated
```

## 2. Hazard axis

```yaml
hazard_axis:
  id: <axis_id>
  input_field: <field_name>
  unit_internal: <unit>
  source_units_allowed: [<unit>, <unit>]
  valid_range: [<min>, <max>]
  extrapolation_policy: <clamp | warn | error | extrapolate_with_flag>
```

## 3. Failure-units

```yaml
failure_units:
  - id: <failure_unit_id>
    subsystem: <SUBSYSTEM_CODE>
    component: <COMPONENT_CODE>
    treatment: primary_nonzero
    curve_id: <curve_id>
    y_axis: <damage_ratio_meaning>
    value_bucket: <value_bucket>
    f_kind: material_share | site_geometry | n/a
```

## 4. Reviewed secondary and DR≈0 units

```yaml
secondary_or_reconciliation_units:
  - subsystem: <SUBSYSTEM_CODE>
    component: <COMPONENT_CODE or null>
    treatment: conditioner_only | secondary_low_materiality | DR_near_zero | out_of_scope
    reason: <reason>
    update_trigger: <trigger>
```

## 5. Selectors

| Field | Required? | Allowed values | Default | Effect | Missing-data behavior |
|---|---|---|---|---|---|
| `<field>` | yes/no/conditional | `<values>` | `<default>` | chooses curve / parameter set | `<behavior>` |

## 6. Conditioners

| Field | Required? | Allowed values | Default | Effect | Missing-data behavior |
|---|---|---|---|---|---|
| `<field>` | yes/no/conditional | `<values>` | `<default>` | shifts / blends / state selection | `<behavior>` |

## 7. Exposure and value modifiers

| Field | Required? | Unit | Default | Effect |
|---|---|---|---|---|
| `<field>` | yes/no/conditional | `<unit>` | `<default>` | scales value / selects exposed units |

## 8. Outputs

```yaml
outputs:
  primary:
    - failure_unit_damage_ratio
    - selected_curve_id
    - metadata_flags
  optional_convenience:
    - subsystem_loss_fraction
    - physical_base_loss_fraction
    - TIV_loss_fraction
```

## 9. Flags

| Flag | Meaning | Trigger |
|---|---|---|
| `DEFAULT_SELECTOR_USED` | default selector was used | selector missing |
| `UNKNOWN_CONDITIONER_STATE` | event-time state unknown | conditioner missing |
| `EXTRAPOLATED_HAZARD_AXIS` | input outside fitted range | x beyond range |
| `OPEN_SEAM_APPLIES` | known open seam affects this output | seam flag active |

## 10. Example call

```yaml
input:
  <hazard_field>: <value>
  <selector_field>: <value>
  <conditioner_field>: <value>
  <exposure_field>: <value>

output:
  failure_unit_damage_ratio: <value>
  selected_curve_id: <curve_id>
  flags: []
```
