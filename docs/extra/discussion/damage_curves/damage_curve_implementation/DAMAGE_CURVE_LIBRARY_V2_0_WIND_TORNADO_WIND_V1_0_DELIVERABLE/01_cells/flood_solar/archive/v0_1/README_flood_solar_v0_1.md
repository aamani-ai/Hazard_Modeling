# Flood × Solar Damage-Curve Cell Package v0.1

**Package status:** v0.1 scaffold / coverage / x-axis / evidence-plan package  
**Cell ID:** `FLOOD_SOLAR`  
**Purpose:** define the correct **damage-code granularity and format** for flood damage to solar PV assets before deriving final numeric curves.

This package intentionally does **not** claim to be a final calibrated flood-loss curve. It is the detailed cell scaffold that answers:

```text
What fails?
What x-axis drives each failure?
What metadata must the damage code read?
Which subsystems are primary, secondary, protection-only, or DR≈0?
Which evidence sources support the eventual curve derivation?
What curve forms are plausible, and why?
```

The next version, `flood_solar v1.0`, should use this scaffold to derive actual curves for the highest-priority failure-units.

---

## 1. Why flood × solar is the right next cell

Hail × solar was intentionally a **single-primary-term** cell:

```text
hail × solar
└─ PV_ARRAY / PV_MODULE / glass-cell replacement trigger
```

Flood × solar is different. It is the first **multi-failure-unit geometry cell**.

```text
flood × solar
├─ depth-driven electrical ingress / submersion
├─ conduit / trench water-path failures
├─ substation and switchgear inundation
├─ foundation / pile / pad scour where velocity matters
├─ site-drainage / flood-defense protection state
└─ reviewed PV array and mounting exposure where submersion or debris is relevant
```

The core methodological contrast is:

```text
hail f  = material/component share
flood f = site geometry / elevation share
```

So flood is the right cell to prove the framework can handle **equipment elevation**, **waterline exposure**, and **multiple nonzero failure-units** inside one hazard × asset package.

---

## 2. Core modeling decision

Do **not** build this:

```text
flood depth → whole solar plant DR
```

Build this:

```text
flood hazard
   │
   ├─ water depth relative to equipment datum
   │      ├─ inverter inundation DR
   │      ├─ switchgear inundation DR
   │      ├─ transformer/control inundation DR
   │      ├─ combiner/DC protection inundation DR
   │      └─ SCADA cabinet inundation DR
   │
   ├─ conduit / trench water path
   │      └─ collection / enclosure ingress modifier or separate curve
   │
   └─ flow velocity / scour proxy
          ├─ foundation / pile scour DR
          └─ civil / access / drainage damage DR
```

The damage-code unit is therefore **one row per failure-unit**, not one row for the whole solar asset.

---

## 3. Flood × solar v0.1 snapshot

```text
flood × solar v0.1
├─ primary nonzero failure-units
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
└─ DR≈0 direct-flood buckets in v0.1
   └─ any equipment whose critical elevation is above water surface elevation
      and has no alternate conduit/water-ingress path
```

This snapshot is meant to be copied into future cell READMEs because it makes the cell identity visible in one glance.

---

## 4. Primary x-axis decision

Flood should not be forced onto one generic x-axis. The v0.1 decision is:

```text
depth-driven ingress/submersion curves:
    x_i = water_depth_above_component_critical_elevation_m

scour / structural erosion curves:
    x_i = flow_velocity_mps
       or depth_velocity_proxy, if evidence supports it

duration:
    conditioner or deferred axis unless evidence forces a true second dimension

contamination / salinity:
    conditioner, not primary x-axis in v0.1

drainage / flood defense:
    exposure/protection modifier, not a standalone physical damage curve unless the asset itself fails
```

The standard exposure transform is:

```text
water_depth_above_component_i
    = max(0, water_surface_elevation - component_critical_elevation_i)
```

Where `component_critical_elevation_i` may be the inverter cabinet threshold, switchgear critical electrical elevation, transformer control-cabinet elevation, combiner box base, cable-trench entry elevation, or similar component-specific datum.

---

## 5. Selector / conditioner / exposure split

For flood × solar, the most important modeling discipline is to keep these separate:

| Type | Flood × solar example | Meaning |
|---|---|---|
| Hazard input | `water_surface_elevation_m`, `flood_depth_m`, `flow_velocity_mps` | What the hazard catalog provides. |
| Exposure geometry | `component_critical_elevation_m`, `pad_height_m`, `depth_above_component_m` | Determines whether water physically reaches the failure-unit. |
| Selector | `NEMA_type`, `IP_rating`, `transformer_type`, `cable_burial_type`, `foundation_type` | Fixed asset attribute that chooses or shifts a curve. |
| Conditioner | `energized_state`, `shutdown_before_flood`, `duration_hr`, `contamination_class`, `drainage_clear` | Event-time state that changes severity. |
| Protection modifier | `flood_wall_height_m`, `berm_height_m`, `drainage_capacity`, `pump_available` | Changes exposure before the damage curve is applied. |
| Value link | subsystem/component value bucket | Where downstream loss dollars attach. |

---

## 6. Why this package is scaffold-first

The public evidence is strong about **what matters**:

- solar PV flood mitigation guidance emphasizes total submersion, equipment elevation, conduit water paths, and enclosure ratings;
- water-damaged electrical equipment guidance emphasizes replacement or professional reconditioning decisions;
- flood-loss models use depth-damage functions and component values;
- enclosure ratings distinguish rain/hosedown protection from temporary/prolonged submersion.

But public evidence is not yet enough to assign final numeric curves to every utility-scale PV subsystem. So v0.1 avoids false precision and instead locks the structure.

```text
v0.1 deliverable:
    coverage + axes + metadata + source map + derivation plan

v1.0 deliverable:
    derived curve parameters for top-priority failure-units
```

---

## 7. Files in this cell package

```text
current/
├─ README_flood_solar_v0_1.md
├─ flood_solar_damage_code_metadata_spec_v0_1.md
├─ flood_solar_curve_derivation_dossier_v0_1.md
├─ damage_curve_records_v0_1_flood_solar.xlsx
├─ workbook_sheet_manifest_flood_solar_v0_1.md
└─ CELL_DOCUMENTATION_CROSSWALK_flood_solar_v0_1.md

previews/
└─ flood_solar_v0_1_coverage_preview.png
```

---

## 8. Recommended v1.0 derivation order

Do the first numeric derivation in this order:

```text
1. Inverter inundation
2. Switchgear inundation
3. Transformer/control inundation
4. Combiner/DC protection inundation
5. SCADA/control cabinet inundation
6. Collection/conduit water path
7. Foundation/scour
8. PV module total submersion/debris, only if material for the site class
```

The first five are depth-driven electrical ingress/submersion curves. They should share a common x-axis pattern but have distinct critical elevations, curve caps, and recovery/replacement treatment.
