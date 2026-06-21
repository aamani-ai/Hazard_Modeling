# Hail × Solar Method Guide v1.3 — Consolidated Damage-Code Cell

This v1.3 guide consolidates the hail × solar damage-curve work and adds the key missing governance layer: **curve derivation and adjustment proof**.

---

## 1. Cell purpose

The purpose of this cell is to define the damage-code grain and interface for hail damage to utility-scale solar PV.

It is not intended to be the final EAL engine. Downstream systems may consume the damage code for EAL, PML, or financial metrics. This package focuses on:

```text
hazard input axis
failure-unit damage ratio
asset metadata selectors
site/event conditioners
exposure variables
value-link compatibility
reviewed secondary/DR≈0 units
curve derivation evidence
selector/conditioner adjustment logic
```

---

## 2. Primary modeling decision

```text
HAIL × SOLAR v1.3
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

## 3. Where the derivation proof lives

The detailed proof is now separated into a dedicated dossier:

```text
hail_solar_curve_derivation_dossier_v1_3.md
```

The workbook carries the same proof in structured sheets:

```text
Hail_Derivation_Index
Hail_Evidence_Params
Hail_Base_Curve_Fit
Hail_Adjustment_Rules
Hail_Variant_Catalog
Hail_Assumption_Register
```

A reviewer should use those sheets to answer:

```text
Which sources were used?
Which evidence became which anchor?
How were D50 and k calculated?
Which archetype curves are directly fitted vs extrapolated?
How does stow shift the curve?
Which assumptions are placeholders?
What would trigger an update?
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

## 5. Base curve form

The module damage curve is:

```text
P_break(D) = 1 / (1 + exp(-k × (D - D50)))
```

v1.3 interprets:

```text
module replacement DR ≈ glass breakage probability
```

Current archetype curves:

```text
fragile thin glass//glass        D50 ≈ 41.1 mm
default 3.2mm glass//backsheet   D50 ≈ 52.7 mm
hail-hardened/thicker glass      D50 ≈ 64.1 mm
```

---

## 6. Selector / conditioner distinction

```text
module_archetype
    = fixed equipment selector
    = what panel is installed
    = chooses the vulnerability curve family

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

## 7. Adjustment rules

Use this decision logic:

```text
New curve
    use when distinct module construction or failure behavior is source-supported

Horizontal shift
    use when same mechanism has changed resistance threshold

Vertical multiplier
    use when maximum exposed/affected fraction changes

Probability blend
    use when event-time state is uncertain

Exposure multiplier
    use when only part of the array footprint was hit
```

Current v1.3 stow adjustment:

```text
D50_stowed = D50_selected + 8 mm
max_DR_stowed = 0.90
```

This is explicitly a placeholder until tracker/stow-specific evidence is available.

---

## 8. Damage-code output grain

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

## 9. Next recommended cell

The next cell should be:

```text
flood × solar
```

because it exercises the next major modeling seam:

```text
hail f  = material-share within PV_ARRAY
flood f = geometry/elevation share based on what equipment is below waterline
```
