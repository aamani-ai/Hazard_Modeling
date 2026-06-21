# Hail × Solar Method Guide v1.2 — Consolidated Damage-Code Cell

This v1.2 guide consolidates the hail × solar damage-curve work into a delivery-ready cell package. It preserves the v1.1 site-adaptation logic and adds the key modeling clarification: **hail × solar is a single-primary failure-unit damage code, not a whole-asset curve**.

---

## 1. Cell purpose

The purpose of this cell is to define the **damage-code grain and interface** for hail damage to utility-scale solar PV.

It is not intended to be the final EAL engine. Downstream systems may consume the damage code for EAL, PML, or other financial metrics, but this package is focused on:

```text
hazard input axis
failure-unit damage ratio
asset metadata selectors
site/event conditioners
exposure variables
value-link compatibility
reviewed secondary/DR≈0 units
metadata flags
```

---

## 2. Primary modeling decision

```text
HAIL × SOLAR v1.2
│
├─ primary nonzero damage curve:
│    MESH-equivalent hail diameter → PV_MODULE glass/cell replacement DR
│
├─ value link:
│    PV_ARRAY / PV_MODULE exposed value bucket
│
├─ conditioning:
│    module archetype + stow state/probability + exposure fraction
│
└─ reviewed secondary units:
     mounting/tracker, inverter, substation, SCADA, civil, foundation, drainage
```

Important wording:

```text
single-primary-term
    yes

single whole-asset curve
    no
```

---

## 3. Why one primary curve is appropriate for v1

Hail impact damage concentrates on exposed module front surfaces:

```text
hailstone impact
   │
   ▼
front glass breakage / cell cracking / module replacement trigger
   │
   ▼
PV_MODULE failure-unit DR
   │
   ▼
PV_ARRAY exposed value bucket
```

Other equipment may be present, but creating nonzero hail curves for every subsystem would add false precision unless a distinct, material, sourceable hail mechanism exists.

The v1.2 discipline is therefore:

```text
PV_MODULE glass/cell:
    primary nonzero failure-unit curve

MOUNTING / TRACKER:
    conditioner, because stow changes module exposure

INVERTER / SUBSTATION / SCADA / CIVIL:
    reviewed secondary or DR≈0 for direct hail in v1
```

---

## 4. X-axis

The operational hail x-axis is:

```text
HAIL_DIAMETER_MESH_EQUIV
    maximum hail diameter / MESH-equivalent size
    internal unit: mm
```

Kinetic energy remains a physics bridge:

```text
E_proxy = 0.5 × m(D) × v(D)^2
```

but it is not required as the native hazard input because most hazard catalogs and provider data supply hail size/MESH rather than mass, velocity, and stone concentration.

---

## 5. Selector / conditioner distinction

```text
module_archetype
    = fixed equipment selector
    = what panel is installed
    = chooses or shifts the vulnerability curve family

stow_state / stow_mode
    = event-time conditioner
    = whether the tracker was in a protective angle during the hail event

stow_success_probability
    = optional uncertainty variable
    = P(stowed | damaging hail arrived)
    = used only when actual stow state is unknown
```

Formula under unknown/probabilistic stow:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + [1 - P(stowed)] × DR_unstowed(D)
```

---

## 6. Damage-code output grain

The required output is:

```text
failure_unit_damage_ratio
```

For this cell:

```text
failure_unit_damage_ratio = PV_MODULE glass/cell replacement DR
```

If valuation inputs are present, the workbook can also show:

```text
PV_ARRAY loss %
physical-base loss %
TIV loss %
loss dollars
```

But those are downstream value-linked views, not the core damage-code requirement.

---

## 7. Cell package contents

The v1.2 hail × solar package contains:

```text
README_hail_solar_v1_2.md
    cell-level explanation and package map

damage_curve_records_v1_2_hail_solar_consolidated.xlsx
    structured workbook with curve records, conditioning, site adaptation, and v1.2 documentation sheets

damage_code_metadata_spec_hail_solar_v1_2.md
    input/output contract for the damage code

damage_curve_method_guide_v1_2_hail_solar_consolidated.md
    this method guide

hail_solar_v1_1_site_adaptation_dashboard_preview.png
    dashboard preview from the applied hail severity package

hail_solar_v1_2_coverage_preview.png
    preview of the new coverage/secondary-subsystem documentation sheet
```

---

## 8. Next recommended cell

The next cell should be:

```text
flood × solar
```

because it exercises the next major modeling seam:

```text
hail f  = material-share within PV_ARRAY
flood f = geometry/elevation share based on what equipment is below waterline
```
