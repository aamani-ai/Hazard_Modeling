# 09 · Damage-Code Interface Standard

The damage-code layer should output damage ratios at the right granularity. It should not become the EAL engine or financial metrics engine.

## 1. Purpose

A damage code answers:

```text
Given hazard intensity and relevant asset metadata,
what damage ratio applies to each modeled failure-unit?
```

It should not need to answer:

```text
What is the annual frequency of the hazard?
What is the final EAL?
What is the insurance premium?
What is the full financial return-period loss?
```

Those are downstream applications that consume the damage code.

## 2. Standard damage-code object

```yaml
damage_code_id: <ID>
version: <version>
hazard_asset_pair: <hazard_x_asset>

hazard_axis:
  id: <axis_id>
  input_field: <field>
  unit: <unit>
  valid_range: [min, max]
  extrapolation_policy: clamp_or_warn

failure_units:
  - id: <failure_unit_id>
    subsystem: <SUBSYSTEM_CODE>
    component: <COMPONENT_CODE>
    treatment: primary_nonzero
    curve_id: <curve_id>
    y_axis: damage_ratio
    value_link_bucket: <bucket>
    f_kind: material_share | site_geometry | n/a

selectors:
  - field: <field>
    effect: chooses_curve_family | chooses_parameter_set
    required: true | false | conditional
    default: <default>

conditioners:
  - field: <field>
    effect: shifts_curve | blends_curves | state_selection
    required: true | false | conditional
    default: <default>

exposure:
  - field: <field>
    effect: scales_affected_value | selects_exposed_units
    required: true | false | conditional
    default: <default>

outputs:
  - failure_unit_damage_ratio
  - selected_curve_id
  - conditioner_state_used
  - metadata_flags
  - open_seam_flags
```

## 3. Output grain

The primary output should be at the failure-unit level:

```text
failure_unit_damage_ratio
```

Optional convenience outputs may include:

```text
subsystem_loss_fraction
physical_base_loss_fraction
TIV_loss_fraction
```

But those require a value basis and should be clearly labeled as convenience views, not the primary vulnerability output.

## 4. Reviewed-but-not-modeled outputs

The code or metadata spec should also declare reviewed units:

```yaml
secondary_or_reconciliation_units:
  - subsystem: INVERTER_SYSTEM
    treatment: DR_near_zero_v1
    reason: direct hail is not the dominant mechanism in this cell

  - subsystem: MOUNTING
    treatment: conditioner_only_v1
    reason: tracker stow changes module exposure but direct tracker damage is not modeled
```

This preserves the snapshot identity of the cell.

## 5. Null and unknown handling

For required selectors or conditioners, the code should define default behavior.

Examples:

```text
module_archetype unknown
  → use default_3_2mm_glass_backsheet, flag DEFAULT_SELECTOR_USED

stow_state unknown
  → use probabilistic/default scenario, flag UNKNOWN_CONDITIONER_STATE

hazard input outside range
  → clamp or extrapolate with warning, depending cell policy
```

## 6. No hidden EAL

The damage code may be run over a hazard frequency curve by another system. It should not internally hard-code frequency assumptions unless the cell explicitly includes a site-adaptation utility sheet.

```text
hazard catalog
   │
   ▼
damage code
   │
   ▼
failure-unit DR
   │
   ▼
financial / risk engine
   ├─ EAL
   ├─ PML
   ├─ return-period loss
   └─ portfolio metrics
```
