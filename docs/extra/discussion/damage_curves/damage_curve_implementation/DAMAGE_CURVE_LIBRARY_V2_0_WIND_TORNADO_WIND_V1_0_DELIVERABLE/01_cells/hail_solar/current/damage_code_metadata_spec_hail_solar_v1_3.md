# Hail × Solar Damage-Code Metadata Spec v1.3

This file defines the metadata contract for the **hail × solar** damage code. v1.3 adds explicit derivation/provenance fields and clarifies selector/conditioner adjustment logic.

---

## 1. Damage-code identity

```yaml
damage_code_id: HAIL_SOLAR_PV_MODULE_V1
version: 1.3
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
| `hail_test_rating` | Optional / high value | string | `IEC baseline / enhanced / 50mm / 75mm` | If available, can override generic archetype. |
| `manufacturer_model` | Optional | string | n/a | Used for override and provenance. |
| `bom_test_report_id` | Optional / high value | string | n/a | Links to exact BOM hail test evidence if available. |

---

## 5. Conditioners — event-time states

Conditioners shift vulnerability during the event.

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `mounting_type` | Yes | enum | `single_axis_tracker` | Determines whether stow applies. |
| `stow_applicable` | Derived | boolean | `true` | Fixed tilt generally `false`; trackers generally `true`. |
| `stow_state` | Conditional | enum | `unknown_probabilistic` | `not_applicable`, `unstowed`, `stowed`, `unknown_probabilistic`. |
| `stow_angle_deg` | Conditional | number | `60` | Required if using explicit stowed curve; v1.3 stores but does not continuously calibrate by angle. |
| `stow_trigger` | Optional | enum | `weather_alert` | manual, automatic, weather-alert, none. |
| `stow_confirmation` | Optional | enum | `commanded_not_confirmed` | Separates command from actual state. |
| `stow_success_probability` | Optional | number 0–1 | `0.60` | Used only when actual stow state is unknown. |

Formula if probabilistic:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + (1 - P(stowed)) × DR_unstowed(D)
```

`P(stowed)` is not hail frequency. It is event-time state uncertainty.

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

## 8. Curve derivation / provenance metadata

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `curve_id` | Yes | string | `HAIL_SOLAR_DEFAULT_3P2_GBS` | Identifies archetype or transformed curve. |
| `curve_form` | Yes | enum/string | `logistic` | v1.3 uses logistic P_break(D). |
| `curve_native_axis` | Yes | enum | `MESH_DIAMETER_MM` | Axis of fitted curve. |
| `D50_mm` | Yes for logistic | number | `52.696` | Diameter at 50% breakage / replacement DR. |
| `k_1_per_mm` | Yes for logistic | number | `0.165912` | Steepness. |
| `anchor_set_id` | Yes | string | `ANCHORS_DEFAULT_3P2_GBS_V1_3` | Links to fit anchors. |
| `evidence_map_version` | Yes | string | `HAIL_EVIDENCE_PARAMS_V1_3` | Links to source-to-parameter map. |
| `assumption_register_version` | Yes | string | `HAIL_ASSUMPTIONS_V1_3` | Links to explicit assumptions. |
| `derivation_status` | Yes | enum | `public_source_derived` | Not private claims-calibrated. |
| `confidence` | Yes | enum | `medium` | Curve-level confidence. |

---

## 9. Adjustment logic metadata

| Field | Required | Type | Example | Notes |
|---|---:|---|---|---|
| `adjustment_type` | Conditional | enum | `base_curve`, `horizontal_shift`, `vertical_multiplier`, `probability_blend`, `exposure_multiplier` | Describes transformation. |
| `D50_shift_mm` | Conditional | number | `8` | Used for stowed placeholder curve. |
| `max_DR_multiplier` | Conditional | number | `0.90` | Used for stowed placeholder curve. |
| `adjustment_confidence` | Conditional | enum | `low` | Numeric stow adjustment is placeholder. |
| `adjustment_source_id` | Conditional | string | `E_VDE_HAIL_STOW` | Links to evidence map. |
| `adjustment_open_seam_id` | Conditional | string | `AS_STOW_D50_SHIFT` | Links to assumption register/open seam. |

---

## 10. Outputs

| Output | Required | Meaning |
|---|---:|---|
| `failure_unit_damage_ratio` | Yes | Damage ratio for PV_MODULE glass/cell failure-unit. |
| `subsystem_loss_fraction` | Optional | PV_ARRAY loss fraction if value linkage is available. |
| `physical_base_loss_fraction` | Optional | Loss fraction of physical replaceable base if valuation inputs are supplied. |
| `tiv_loss_fraction` | Optional | Loss fraction of installed capex/TIV if basis inputs are supplied. |
| `metadata_flags` | Yes | Flags such as `cap_sensitive`, `stow_unknown`, `curve_public_source_derived`, `stow_adjustment_placeholder`. |
| `reviewed_secondary_units` | Yes | List of other reviewed subsystems and v1 treatment. |

---

## 11. Minimum viable input object

```yaml
mesh_diameter_mm: 50
module_archetype: default_3_2mm_glass_backsheet
mounting_type: single_axis_tracker
stow_state: unknown_probabilistic
stow_success_probability: 0.60
array_exposure_fraction: 1.00
```

---

## 12. High-confidence input object

```yaml
mesh_diameter_mm: 50
hail_size_source: MRMS_MESH
module_archetype: exact_specs_available
front_glass_thickness_mm: 3.2
tempered_glass: true
glass_glass_vs_backsheet: glass_backsheet
manufacturer_model: <module model>
bom_test_report_id: <report id>
hail_test_rating: <enhanced hail test>
mounting_type: single_axis_tracker
stow_state: stowed
stow_angle_deg: 60
stow_confirmation: confirmed_by_SCADA
array_exposure_fraction: 0.72
exposure_basis: footprint_overlay
f_hail_material_share: 0.75
value_bucket: PV_ARRAY_MODULE_EXPOSED
```
