# 07 · Selector, Conditioner, Exposure, and Value-Modifier Standard

This document defines the metadata categories that every damage code should declare.

## 1. Four different roles

```text
HAZARD INPUT
  what the hazard catalog supplies

SELECTOR
  fixed asset attribute that chooses a curve family or parameter set

CONDITIONER
  event-time state that shifts or blends a curve

EXPOSURE / VALUE MODIFIER
  determines how much of the value bucket the curve applies to
```

These must not be mixed.

## 2. ASCII model

```text
hazard input x
   │
   ▼
selected curve family
   ▲
   │
selector metadata
   │
   └─ module archetype, turbine class, IP rating, glass thickness

selected curve
   │
   ▼
conditioned curve
   ▲
   │
conditioner metadata
   │
   └─ stow state, energized state, feathered state, yaw alignment

conditioned DR
   │
   ▼
loss calculation
   ▲
   │
exposure/value modifiers
   │
   └─ swath fraction, below-waterline share, value f, physical base
```

## 3. Hail × solar example

| Role | Field | Meaning |
|---|---|---|
| Hazard input | `mesh_diameter_mm` | MESH-equivalent maximum hail diameter |
| Selector | `module_archetype` | Chooses fragile/default/hardened curve family |
| Selector | `front_glass_thickness_mm` | More detailed module selector if available |
| Selector | `glass_construction` | glass//glass vs glass//backsheet |
| Conditioner | `stow_state` | event-time tracker state: stowed/unstowed/unknown |
| Conditioner | `stow_success_probability` | optional expected-state blend when actual state is unknown |
| Exposure | `array_exposure_fraction` | fraction of PV array footprint affected by hail swath |
| Value modifier | `f_hail_material_share` | exposed value share inside PV_ARRAY/PV_MODULE bucket |

## 4. Stow state clarification

`stow_state` is an operating/control state, not a module property.

```text
module_archetype
  = what panel is installed

stow_state
  = how tracker/mounting was positioned during the event
```

`stow_success_probability` means:

```text
P(tracker was actually in protective hail-stow state | damaging hail arrived)
```

It is not:

```text
- hail frequency,
- annual exceedance probability,
- EAL,
- or probability that the site experiences hail.
```

If actual state is known:

```text
confirmed stowed   → P(stowed) = 1
confirmed unstowed → P(stowed) = 0
unknown            → use scenario or default probability, with flag
```

## 5. Flood × solar example

| Role | Field | Meaning |
|---|---|---|
| Hazard input | `flood_depth_m` | water depth at site/equipment |
| Hazard input | `velocity_mps` | flow velocity for scour/drag pathways |
| Selector | `equipment_ip_or_nema_rating` | enclosure resistance |
| Selector | `pad_height_m` | equipment elevation above grade |
| Conditioner | `energized_state` | energized/de-energized at inundation |
| Exposure | `equipment_below_waterline` | which equipment is submerged |
| Value modifier | `f_flood_geometry` | share of value below waterline |

## 6. Wind × wind example

| Role | Field | Meaning |
|---|---|---|
| Hazard input | `gust_speed_mps` | local gust intensity |
| Selector | `turbine_class` | structural design class |
| Selector | `hub_height_m` | hazard exposure and turbine geometry |
| Conditioner | `feathered_state` | blades feathered or not |
| Conditioner | `yaw_alignment` | aligned/misaligned to wind |
| Exposure | `turbines_in_swath_fraction` | fraction of turbines affected |
| Value modifier | `blade_value_share` | share of rotor/turbine value exposed |

## 7. Required metadata table per cell

Each damage-code metadata spec must include:

| Field | Role | Required? | Default | Effect on model | Source / provenance |
|---|---|---|---|---|---|
| `<field>` | hazard / selector / conditioner / exposure / value_modifier | yes/no/conditional | default | chooses / shifts / blends / scales | source or assumption |

## 8. Design rule

```text
Selectors choose.
Conditioners shift or blend.
Exposure variables scale affected value.
Value modifiers change caps or denominators.
```

If a variable changes more than one thing, split it into separate fields or document the combined effect explicitly.
