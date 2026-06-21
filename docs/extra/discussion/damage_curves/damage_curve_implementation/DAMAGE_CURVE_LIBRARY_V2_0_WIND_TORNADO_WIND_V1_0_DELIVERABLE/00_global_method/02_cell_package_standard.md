# 02 · Cell Package Standard

A **cell** is one hazard × asset pair, such as:

```text
hail × solar
flood × solar
strong wind / tornado × wind
wildfire × solar
lightning × wind
```

The cell package is the project-management unit. It can contain one curve or many curves, depending on how many failure-units are materially affected.

## 1. Required README sections

Each cell README should include these sections.

```text
1. Cell identity
2. Snapshot tree
3. Scope and exclusions
4. Primary nonzero failure-unit(s)
5. Conditioner-only equipment
6. Reviewed secondary / low-materiality equipment
7. DR≈0 / not-directly-affected buckets
8. Hazard x-axis decision
9. Curve form and y-axis meaning
10. Selector / conditioner / exposure map
11. Value-link basis
12. Evidence and derivation pointer
13. Workbook map
14. Open seams and update triggers
15. Implementation notes
```

## 2. Snapshot tree format

Every cell should start with a one-screen identity tree.

Example:

```text
hail × solar
├─ primary nonzero failure-unit
│  └─ PV_ARRAY / PV_MODULE / glass-cell replacement trigger
│
├─ conditioner-only equipment
│  └─ MOUNTING / TRACKER, because tracker stow changes module exposure
│
├─ reviewed secondary / low-materiality equipment
│  └─ SCADA / MET_STATION, exposed instruments
│
└─ DR≈0 direct-hail buckets in v1
   ├─ INVERTER_SYSTEM
   ├─ SUBSTATION
   ├─ CIVIL_INFRA
   ├─ FOUNDATION
   └─ SITE_DRAINAGE
```

This snapshot is valuable because future cells may need two or more primary curves:

```text
flood × solar
├─ primary nonzero failure-units
│  ├─ INVERTER_SYSTEM / INVERTER / electrical ingress
│  ├─ SUBSTATION / SWITCHGEAR / inundation damage
│  ├─ ELECTRICAL_COLLECTION / cable trench inundation
│  └─ FOUNDATION / scour or erosion, if velocity pathway is included
│
├─ exposure-geometry equipment
│  └─ SITE_DRAINAGE / FLOOD_DEFENSE, because it changes water depth at equipment
│
└─ DR≈0 or low direct-flood buckets
   └─ PV_MODULE direct physical breakage, unless submerged/debris pathway is modeled
```

## 3. Required coverage table

The README or workbook must contain a coverage table.

| Bucket type | Meaning | Must document |
|---|---|---|
| Primary nonzero | Has a material damage curve in this cell | Failure mechanism, x-axis, curve ID, value link |
| Conditioner-only | Does not get its own direct-damage curve but changes another curve | Which curve it modifies and how |
| Secondary / low-materiality | Reviewed and plausible, but not modeled in v1 | Why excluded, update trigger |
| DR≈0 direct effect | Kept for reconciliation but assumed no direct damage in v1 | Reason and hazard scope |
| Out of scope | Not part of this cell's hazard pathway | Boundary condition |

## 4. Required derivation proof pointer

The README must point to the derivation dossier.

```text
Curve proof lives in:
curve_derivation_dossier_<cell_id>_<version>.md
```

Do not leave the reviewer to infer curve curation from plots alone.

## 5. Required workbook map

The README should tell the user where to look in the workbook.

Example:

| Question | Workbook sheet |
|---|---|
| What are the curve records? | `Curve_Records` |
| Which sources support the parameters? | `Evidence_Log`, `Hail_Evidence_Params` |
| How was the base curve fitted? | `Hail_Base_Curve_Fit` |
| How are variants defined? | `Hail_Variant_Catalog` |
| What assumptions remain? | `Hail_Assumption_Register`, `Open_Seams_Index` |

## 6. Deviations

If a cell cannot follow the standard structure, add a short `Deviation from standard` section:

```text
Deviation:
  This cell uses damage states instead of a continuous curve.
Reason:
  Evidence is reported as damage-state probabilities, not continuous loss ratios.
Consequence:
  The damage code emits state probabilities and expected DR, not a single direct curve.
```
