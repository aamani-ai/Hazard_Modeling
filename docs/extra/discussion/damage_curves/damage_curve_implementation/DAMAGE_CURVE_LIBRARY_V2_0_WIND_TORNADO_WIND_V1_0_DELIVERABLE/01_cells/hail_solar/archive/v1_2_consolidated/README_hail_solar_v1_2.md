# Hail × Solar Damage-Curve Cell Package v1.2

This README consolidates the current **hail × solar** damage-curve deliverable. The purpose of this cell is to define a clean, auditable **damage-code interface** for hail damage to utility-scale solar PV — not to be the full EAL or financial-metrics engine.

The cell currently includes:

```text
hazard axis:
    MESH-equivalent maximum hail diameter, mm

primary failure-unit:
    PV_MODULE glass/cell damage inside PV_ARRAY

main output:
    module replacement damage ratio

value linkage:
    PV_ARRAY / PV_MODULE exposed value bucket

site conditioning:
    module archetype, stow state, stow probability if unknown, array exposure fraction
```

---

## 1. Core modeling decision

For **hail × solar**, v1.2 uses a **single primary nonzero failure-unit curve**:

```text
MESH-equivalent hail diameter
        │
        ▼
PV_MODULE glass/cell replacement DR
        │
        ▼
PV_ARRAY exposed value bucket
```

This is not the same as applying one curve to the whole solar plant. The curve applies to the relevant failure-unit only.

```text
BAD:
    hail × solar = one DR applied to whole TIV

GOOD:
    hail × solar = one primary failure-unit DR,
                   then downstream value logic applies it to the PV_ARRAY/PV_MODULE bucket
```

---

## 2. Why panels/modules are the primary failure-unit

Hail impact damage concentrates on the exposed module surface:

```text
hailstone impact
   │
   ▼
front glass breakage / cell cracking / module replacement trigger
   │
   ▼
PV_MODULE damage ratio
   │
   ▼
PV_ARRAY value loss, if value linkage is supplied
```

Other solar equipment exists and must be reviewed, but v1.2 does not force weak nonzero curves for every subsystem.

---

## 3. Reviewed subsystem coverage

| Subsystem | Component / bucket | v1.2 treatment | Why |
|---|---|---|---|
| `PV_ARRAY` | `PV_MODULE` glass/cell/front-side module | **Primary nonzero curve** | Direct hail-impact mechanism and highest materiality. |
| `MOUNTING` | `TRACKER`, `FIXED_MOUNT`, `RACKING_STRUCTURE` | Conditioner / secondary | Tracker state changes module exposure; direct hail damage to racking is secondary in v1. |
| `INVERTER_SYSTEM` | `INVERTER`, `COMBINER_BOX`, `DC_PROTECTION` | DR≈0 / optional secondary | Usually enclosed; direct hail not first-order unless enclosures are exposed and fragile. |
| `SUBSTATION` | `TRANSFORMER_MAIN`, `SWITCHGEAR` | DR≈0 / optional secondary | Direct hail to housings/auxiliaries possible, but not a dominant v1 loss term. |
| `SCADA` | `MONITORING_SYSTEM`, `MET_STATION` | Optional secondary | Exposed instruments may be vulnerable but usually low value share. |
| `ELECTRICAL_COLLECTION` | `CABLE_DC`, `CABLE_AC` | DR≈0 for direct hail | Not normally a direct hail-impact failure bucket. |
| `CIVIL_INFRA` | roads/fencing/site works | DR≈0 for direct hail | Not a first-order hail replacement loss. |
| `FOUNDATION`, `SITE_DRAINAGE` | piles/drainage | DR≈0 for direct hail | Relevant to flood/wind/snow, not direct hail v1. |

---

## 4. Hail x-axis decision

The operational x-axis is **hail size**, not native kinetic energy:

```text
primary x-axis:
    maximum hail diameter / MESH-equivalent hail size

internal unit:
    mm

source-native accepted units:
    inches or mm

physics bridge:
    diameter → mass/velocity assumptions → per-stone impact KE proxy
```

Why:

```text
hazard providers usually provide hail size or MESH
PV module physics is better explained by impact energy
therefore: use hail size as the native input, and KE as a bridge
```

ASCII:

```text
provider hazard layer
    hail size / MESH
          │
          ▼
normalized diameter D, mm
          │
          ▼
optional physics bridge
    E_proxy = 0.5 × m(D) × v(D)^2
          │
          ▼
module damage curve
```

---

## 5. Module archetype clarified

A **module archetype** is a fixed equipment selector.

It answers:

```text
What kind of PV module is installed from a hail-fragility point of view?
```

Examples:

```text
fragile_thin_glass_glass
default_3_2mm_glass_backsheet
hail_hardened_thicker_glass
```

More detailed metadata behind the archetype:

```text
front_glass_thickness_mm
tempered_glass
glass_glass_vs_backsheet
module_format
frame/support design
hail test rating
manufacturer/model, if available
```

It is a **selector**, not a weather variable and not an operating state.

```text
MESH diameter
   │
   ├─ fragile module       → curve shifted left
   ├─ default module       → baseline curve
   └─ hail-hardened module → curve shifted right
```

---

## 6. Stow mode / stow state clarified

The word is **stow**, not store.

For tracker systems, **stow** means rotating the panels into a protective position before or during a storm.

```text
normal operation:
    tracker follows the sun

hail stow:
    tracker rotates to reduce direct hail impact exposure

wind stow:
    tracker rotates to reduce aerodynamic loading
```

Stow is an event-time **conditioner**, not a module selector.

| Field | Meaning |
|---|---|
| `mounting_type` | fixed tilt, single-axis tracker, dual-axis tracker |
| `stow_applicable` | whether stow logic applies |
| `stow_state` | `not_applicable`, `unstowed`, `stowed`, `unknown_probabilistic` |
| `stow_angle_deg` | protective angle if known |
| `stow_trigger` | manual, automatic, weather-alert, none |
| `stow_confirmation` | commanded vs confirmed |
| `stow_success_probability` | optional probability used only when actual stow state is unknown |

---

## 7. Probability of stow clarified

`P(stowed)` means:

```text
Given a damaging hail event occurred,
what is the probability the tracker was actually in hail-stow position
when the damaging hail arrived?
```

It is **not**:

```text
probability of hail
annual hail frequency
EAL
return period
```

If the actual state is known:

```text
confirmed_stowed   → P(stowed) = 1.0
confirmed_unstowed → P(stowed) = 0.0
```

If the actual state is unknown:

```text
unknown_probabilistic → use scenario assumption, e.g. P(stowed) = 0.60
```

Simple conditioning formula:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + [1 - P(stowed)] × DR_unstowed(D)
```

---

## 8. Damage-code interface summary

```yaml
damage_code_id: HAIL_SOLAR_PV_MODULE_V1
hazard_asset_pair: hail_x_solar
hazard_axis:
  id: HAIL_DIAMETER_MESH_EQUIV
  input_field: mesh_diameter_mm
  unit: mm

failure_units:
  - id: PV_MODULE_GLASS_CELL
    subsystem: PV_ARRAY
    component: PV_MODULE
    role: primary
    curve: mesh_mm_to_module_replacement_dr
    f_kind: material_share
    value_bucket: PV_ARRAY_MODULE_EXPOSED

selectors:
  - module_archetype
  - front_glass_thickness_mm
  - tempered_glass
  - glass_glass_vs_backsheet

conditioners:
  - mounting_type
  - stow_state
  - stow_angle_deg
  - stow_success_probability_optional

exposure:
  - array_exposure_fraction_optional

outputs:
  - failure_unit_damage_ratio
  - subsystem_loss_fraction_optional
  - metadata_flags
  - reviewed_secondary_units
```

---

## 9. What the workbook contains

The consolidated v1.2 workbook contains the prior v1.1 site-adaptation sheets plus documentation sheets:

```text
Hail_Solar_Coverage
    subsystem coverage table: primary, conditioner-only, secondary, DR≈0

Damage_Code_Interface
    damage-code input/output contract

Selector_Conditioner_Map
    reusable metadata pattern for future hazard × asset cells
```

The older v1.1 sheets still carry:

```text
Hail_Site_Inputs
Hail_Conditioning
Hail_Hazard_Frequency
Hail_Site_Loss
Hail_Return_Period_Loss
Hail_EAL_By_Bin
Hail_Sensitivity
Hail_V1_1_Dashboard
Hail_V1_1_QA
```

---

## 10. What this package is and is not

This package **is**:

```text
an auditable hail × solar damage-code cell
an x-axis and metadata specification
a primary failure-unit curve package
a value-link-ready severity model
```

This package is **not**:

```text
the full EAL engine
the final insurer-calibrated claims model
a whole-asset hail curve applied directly to TIV
a stochastic tracker-operations model
```

---

## 11. Recommended next cell

After this consolidation, the next recommended cell is:

```text
flood × solar
```

Reason:

```text
hail f  = material share within PV_ARRAY
flood f = geometry/elevation share based on which equipment is below waterline
```

Flood will test multi-term failure-unit modeling and exposure geometry, which is the natural next seam after hail × solar.
