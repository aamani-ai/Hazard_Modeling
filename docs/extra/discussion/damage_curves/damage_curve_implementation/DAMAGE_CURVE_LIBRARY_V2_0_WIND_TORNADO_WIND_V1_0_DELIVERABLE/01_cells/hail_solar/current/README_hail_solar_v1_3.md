# Hail × Solar Damage-Curve Cell README v1.3

This is the current consolidated package for the `hail × solar` damage-code cell.

---

## Start here for this cell

Read in this order:

```text
1. README_hail_solar_v1_3.md
2. hail_solar_curve_derivation_dossier_v1_3.md
3. damage_code_metadata_spec_hail_solar_v1_3.md
4. damage_curve_method_guide_v1_3_hail_solar_consolidated.md
5. damage_curve_records_v1_3_hail_solar_derivation_audit.xlsx
```

---

## What v1.3 adds

v1.3 adds the missing proof layer:

```text
source evidence
   → source interpretation
   → anchors
   → curve form
   → D50 / k parameters
   → selector adjustment logic
   → conditioner adjustment logic
   → assumption register
```

The workbook now includes these dedicated audit sheets:

```text
Hail_Derivation_Index
Hail_Evidence_Params
Hail_Base_Curve_Fit
Hail_Adjustment_Rules
Hail_Variant_Catalog
Hail_Assumption_Register
```

---

## Current modeling decision

```text
HAIL × SOLAR v1.3
├─ primary nonzero curve:
│    MESH-equivalent hail diameter → PV_MODULE glass/cell replacement DR
│
├─ selector:
│    module archetype / glass construction
│
├─ conditioner:
│    tracker stow state / stow probability
│
├─ exposure:
│    array exposure fraction
│
└─ reviewed secondary units:
     mounting/tracker, inverter, substation, SCADA, civil, foundation, drainage
```

Important:

```text
single-primary-term damage code = yes
whole-asset hail curve = no
```

---

## Main workbook

Open:

```text
damage_curve_records_v1_3_hail_solar_derivation_audit.xlsx
```

The core sheets for proof are:

| Sheet | Purpose |
|---|---|
| `Hail_Derivation_Index` | Reviewer route through the proof trail. |
| `Hail_Evidence_Params` | Which source supports which parameter or rule. |
| `Hail_Base_Curve_Fit` | Logistic fit, anchors, D50/k calculation. |
| `Hail_Adjustment_Rules` | New curve vs horizontal shift vs vertical multiplier vs probability blend. |
| `Hail_Variant_Catalog` | Fragile/default/hardened/stowed/probabilistic variants. |
| `Hail_Assumption_Register` | Load-bearing assumptions and update triggers. |

---

## Main caveats

```text
1. The curve is public-source-derived, not private claims-calibrated.
2. The stow adjustment is a placeholder transformation, not tracker-specific test calibration.
3. f_hail material share remains a load-bearing value-link open seam.
4. Secondary non-module direct-hail curves are not modeled in v1; they are reviewed and tagged.
5. EAL/PML/tail metrics belong downstream and require hazard frequency plus uncertainty.
```
