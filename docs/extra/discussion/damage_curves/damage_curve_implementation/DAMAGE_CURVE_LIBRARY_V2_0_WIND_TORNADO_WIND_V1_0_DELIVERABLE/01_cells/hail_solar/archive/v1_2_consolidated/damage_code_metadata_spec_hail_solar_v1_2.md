# Hail × Solar Damage-Code Metadata Spec v1.2

This file defines the metadata contract for the **hail × solar** damage code. It is designed to be consumed by a downstream hazard catalog, exposure model, valuation ledger, or financial metrics system.

---

## 1. Damage-code identity

```yaml
damage_code_id: HAIL_SOLAR_PV_MODULE_V1
version: 1.2
hazard: hail
asset_class: solar_pv
primary_failure_unit: PV_MODULE_GLASS_CELL
curve_output_grain: failure_unit_damage_ratio
```

---

## 2. Hazard input

| Field | Required | Type | Unit | Notes |
|---|---:|---|---|---|
| `mesh_diameter_mm` | Yes | number | mm | Primary operational x-axis: MESH-equivalent maximum hail diameter. |
| `hail_size_source` | Recommended | enum | n/a | `observed_report`, `MRMS_MESH`, `vendor_map`, `lab_test`, `scenario`. |
| `source_unit` | Optional | enum | n/a | `mm`, `in`. Convert to mm internally. |

---

## 3. Optional physics bridge

| Field | Required | Type | Unit | Notes |
|---|---:|---|---|---|
| `impact_ke_proxy_j` | Optional / derived | number | J/impact | Per-stone impact-energy proxy. Do not confuse with J/m² event flux. |
| `bridge_assumption_version` | Conditional | string | n/a | Required if KE proxy is used. |
| `bridge_notes` | Conditional | text | n/a | Mass/velocity assumptions. |

---

## 4. Selectors — fixed asset attributes

Selectors choose or shift the curve family.

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `module_archetype` | Yes unless exact specs available | enum | `default_3_2mm_glass_backsheet` | Main v1 selector. |
| `front_glass_thickness_mm` | Recommended | number | `3.2` | Important hail vulnerability metadata. |
| `tempered_glass` | Recommended | boolean | `true` | Hail-linked PV module spec. |
| `glass_glass_vs_backsheet` | Recommended | enum | `glass_backsheet` | Used to classify archetype. |
| `hail_test_rating` | Optional | string | `IEC baseline / enhanced` | If available from manufacturer/testing. |
| `manufacturer_model` | Optional | string | n/a | Used for override and provenance. |

---

## 5. Conditioners — event-time states

Conditioners shift vulnerability during the event.

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `mounting_type` | Yes | enum | `single_axis_tracker` | Determines whether stow applies. |
| `stow_applicable` | Derived | boolean | `true` | Fixed tilt generally `false`; trackers generally `true`. |
| `stow_state` | Conditional | enum | `unknown_probabilistic` | `not_applicable`, `unstowed`, `stowed`, `unknown_probabilistic`. |
| `stow_angle_deg` | Conditional | number | `60` | Required if using explicit stowed curve. |
| `stow_trigger` | Optional | enum | `weather_alert` | manual, automatic, weather-alert, none. |
| `stow_confirmation` | Optional | enum | `commanded_not_confirmed` | separates command from actual state. |
| `stow_success_probability` | Optional | number 0–1 | `0.60` | Used only when actual stow state is unknown. |

Formula if probabilistic:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + (1 - P(stowed)) × DR_unstowed(D)
```

---

## 6. Exposure geometry

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `array_exposure_fraction` | Optional | number 0–1 | `1.00` | Fraction of PV array footprint hit by damaging hail swath. |
| `exposure_basis` | Optional | enum | `full_site_default` | `full_site_default`, `footprint_overlay`, `scenario`. |

---

## 7. Value concentration

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `f_hail_material_share` | Required for loss application | number 0–1 | `0.75` | Share of PV_ARRAY value exposed to module glass/cell replacement damage. |
| `f_kind` | Yes | enum | `material_share` | Hail f is a material share, not flood-style geometry. |
| `value_bucket` | Yes for loss application | enum/string | `PV_ARRAY_MODULE_EXPOSED` | Links to valuation ledger. |

---

## 8. Outputs

| Output | Required | Meaning |
|---|---:|---|
| `failure_unit_damage_ratio` | Yes | Damage ratio for PV_MODULE glass/cell failure-unit. |
| `subsystem_loss_fraction` | Optional | PV_ARRAY loss fraction if value linkage is available. |
| `physical_base_loss_fraction` | Optional | Loss fraction of physical replaceable base if valuation inputs are supplied. |
| `tiv_loss_fraction` | Optional | Loss fraction of installed capex/TIV if basis inputs are supplied. |
| `metadata_flags` | Yes | Flags such as `cap_sensitive`, `stow_unknown`, `frequency_placeholder`, `curve_public_source_derived`. |
| `reviewed_secondary_units` | Yes | List of other reviewed subsystems and v1 treatment. |

---

## 9. Reviewed secondary units

```yaml
reviewed_secondary_units:
  - subsystem: MOUNTING
    treatment: conditioner_only_v1
    reason: tracker/stow affects module exposure; direct hail damage to racking is secondary

  - subsystem: INVERTER_SYSTEM
    treatment: DR_near_zero_v1
    reason: enclosed equipment; direct hail is not first-order unless exposed enclosures are known

  - subsystem: SUBSTATION
    treatment: DR_near_zero_v1
    reason: direct hail to electrical internals is not dominant in v1

  - subsystem: SCADA
    treatment: optional_secondary_low_materiality
    reason: exposed met/instrumentation damage possible but usually low value share

  - subsystem: CIVIL_INFRA
    treatment: DR_near_zero_v1
    reason: direct hail does not normally create civil replacement loss
```

---

## 10. Minimum viable input object

```yaml
mesh_diameter_mm: 50
module_archetype: default_3_2mm_glass_backsheet
mounting_type: single_axis_tracker
stow_state: unknown_probabilistic
stow_success_probability: 0.60
array_exposure_fraction: 1.00
```

---

## 11. High-confidence input object

```yaml
mesh_diameter_mm: 50
hail_size_source: MRMS_MESH
module_archetype: exact_specs_available
front_glass_thickness_mm: 3.2
tempered_glass: true
glass_glass_vs_backsheet: glass_backsheet
manufacturer_model: <module model>
mounting_type: single_axis_tracker
stow_state: stowed
stow_angle_deg: 60
stow_confirmation: confirmed_by_SCADA
array_exposure_fraction: 0.72
exposure_basis: footprint_overlay
f_hail_material_share: 0.75
value_bucket: PV_ARRAY_MODULE_EXPOSED
```
