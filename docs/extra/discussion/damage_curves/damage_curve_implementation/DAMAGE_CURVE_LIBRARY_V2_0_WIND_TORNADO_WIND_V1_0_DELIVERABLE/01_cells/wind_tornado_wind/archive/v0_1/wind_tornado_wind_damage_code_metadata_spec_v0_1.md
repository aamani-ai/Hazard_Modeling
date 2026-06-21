# Wind / tornado × wind — damage-code metadata spec v0.1

**Cell ID:** `WIND_TORNADO_WIND`  
**Purpose:** define the runtime metadata needed to evaluate wind/tornado damage codes for wind farms.  
**Status:** v0.1 scaffold. This is the metadata contract for curve derivation and later code implementation.

---

## 1. Damage-code identity

A wind/tornado wind-farm damage code should identify:

```yaml
damage_code_id: WIND_TORNADO_WIND_BLADE_STRUCTURAL_V0_1
cell_id: WIND_TORNADO_WIND
asset_class: wind
hazard_family: severe_wind_tornado
failure_unit:
  subsystem: ROTOR_ASSEMBLY
  component: BLADE
  failure_mode: structural_overload_or_debris
status: scaffold_not_final_curve
```

The important distinction is that the **cell** may contain several damage codes:

```text
WIND_TORNADO_WIND
├─ WIND_TORNADO_WIND_BLADE_STRUCTURAL
├─ WIND_TORNADO_WIND_TOWER_COLLAPSE
├─ WIND_TORNADO_WIND_NACELLE_DAMAGE
├─ WIND_TORNADO_WIND_FOUNDATION_SUPPORT
└─ WIND_TORNADO_WIND_SHARED_PLANT_CONDITIONAL
```

---

## 2. Hazard input fields

| Field | Type | Units / values | Role | Notes |
|---|---|---:|---|---|
| `gust_3s_hub_mps` | hazard input | m/s | Primary straight-line wind x-axis | Preferred for non-tornado severe wind if available. |
| `gust_3s_10m_mps` | hazard input | m/s | Source-native input | Must be bridged to hub height before using turbine structural curves. |
| `tornado_wind_proxy_mps` | hazard input | m/s | Primary tornado x-axis if available | Must document height/averaging/source. |
| `tornado_ef_rating` | hazard bridge | EF0–EF5 | Categorical bridge | EF is damage-estimated; use with uncertainty flags. |
| `swath_polygon_id` | exposure | ID | Footprint overlay | Used to compute exposed turbine count. |
| `exposed_turbine_count` | exposure | integer | Repeated-unit aggregation | Prefer count when turbine coordinates are known. |
| `turbine_exposure_fraction` | exposure | 0–1 | Repeated-unit aggregation | Use when count is unavailable. |
| `duration_above_threshold_s` | conditioner/open seam | seconds | Optional future axis | v0.1 does not force duration as 2-D. |
| `large_debris_flag` | conditioner/open seam | bool/category | Tornado/debris pathway | Candidate v1.0 modifier or separate pathway. |

---

## 3. Selectors

Selectors are fixed or slowly changing asset attributes. They choose or shift a curve family.

| Selector | Meaning | Source |
|---|---|---|
| `iec_wind_class` | Turbine design class / resistance selector | Turbine certificate/spec sheet |
| `vref_mps` | Design reference wind speed | IEC class / manufacturer |
| `turbulence_class` | A+, A, B, C category | IEC class / manufacturer |
| `hub_height_m` | Height for hazard translation and structural loads | USWTDB/EIA/site data |
| `rotor_diameter_m` | Rotor swept area and blade length context | USWTDB/EIA/site data |
| `blade_length_m` | Blade component geometry | Derived from rotor diameter or turbine spec |
| `turbine_model` | Manufacturer/model-specific curve selector | Asset registry / USWTDB |
| `tower_type` | Steel tubular / concrete / hybrid | Asset metadata |
| `foundation_type` | Spread footing / pile / rock anchor / other | Civil design package |
| `survival_wind_speed_mps` | Model-specific design/survival anchor | Manufacturer / design documentation |

Do not treat selectors as event intensity. For example, `Vref` helps choose or anchor vulnerability, but the event x-axis is still event wind intensity.

---

## 4. Conditioners

Conditioners are event-time states that modify the curve.

| Conditioner | Values | Why it matters |
|---|---|---|
| `operating_state` | operating / parked / curtailed / faulted | Changes load state and possible failure mode. |
| `feathered_state` | confirmed_feathered / not_feathered / unknown | Blade feathering reduces aerodynamic exposure/load. |
| `yaw_alignment_deg` | degrees / aligned / yaw_error | Yaw error changes projected rotor/nacelle loading. |
| `brake_status` | available / failed / unknown | Changes overspeed and parked/stop state. |
| `grid_availability` | grid_available / grid_loss | Grid loss may trigger emergency stop or protection behavior. |
| `control_availability` | available / degraded / failed | Pitch/yaw/brake control may fail independently. |

These are not necessarily damaged value buckets in v0.1. They modify blade/tower/nacelle curves.

---

## 5. Exposure geometry

Wind farms are repeated-unit assets. A tornado or compact severe-wind swath may hit only part of the farm.

| Field | Role |
|---|---|
| `turbine_coordinates` | Allows exact turbine count inside hazard footprint. |
| `exposed_turbine_count` | Number of turbines the per-turbine curves apply to. |
| `turbine_exposure_fraction` | Fractional fallback if exact count is unavailable. |
| `shared_plant_footprint_hit` | Whether substation/collection/roads are affected. |
| `storm_swath_width_m` | Context for footprint severity and exposure. |
| `wind_direction_deg` | Optional direction for yaw/exposure logic. |

Exposure geometry changes the affected amount, not the structural fragility curve itself.

---

## 6. Output fields

A damage code should emit:

| Output | Meaning |
|---|---|
| `failure_unit_damage_ratio` | Damage ratio for that failure-unit. |
| `damage_state` | Optional state label: none/minor/major/total/collapse. |
| `curve_record_id` | Which curve record was used. |
| `selected_variant` | Selected design class / operating state / tornado pathway. |
| `confidence_tier` | Source quality / derivation maturity. |
| `open_seam_flags` | Known unresolved issues triggered by inputs. |
| `value_link_id` | Pointer to valuation bucket; actual dollars handled downstream. |

The damage code should not compute EAL, PML, or final financial metrics. Those belong to the downstream hazard-frequency and valuation engine.

---

## 7. Example runtime object

```yaml
damage_code_id: WIND_TORNADO_WIND_TOWER_COLLAPSE_V0_1
cell_id: WIND_TORNADO_WIND
failure_unit:
  subsystem: TOWER
  component: TOWER_SECTION
  failure_mode: tower_buckling_or_collapse
hazard_axis:
  id: WTW_TORNADO_WIND_PROXY_MPS
  unit: m/s
selectors:
  iec_wind_class: II
  vref_mps: 42.5
  hub_height_m: 100
  tower_type: steel_tubular
conditioners:
  feathered_state: unknown
  yaw_alignment_deg: unknown
  brake_status: unknown
exposure:
  exposed_turbine_count: 5
  turbine_count_total: 80
curve:
  form_candidate: structural_fragility_or_state_curve
  status: v0_1_scaffold_not_final
outputs:
  - failure_unit_damage_ratio
  - damage_state
  - open_seam_flags
```
