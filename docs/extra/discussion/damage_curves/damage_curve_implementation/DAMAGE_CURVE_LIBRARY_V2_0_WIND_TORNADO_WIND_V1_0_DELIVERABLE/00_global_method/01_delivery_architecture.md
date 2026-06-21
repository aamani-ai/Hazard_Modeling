# 01 · Delivery Architecture Standard

This document defines the expected structure for the damage-curve library and each hazard × asset cell package.

## 1. Core idea

One global method folder plus one self-contained package per hazard × asset cell:

```text
DAMAGE_CURVE_LIBRARY/
├─ START_HERE.md
├─ MANIFEST.md
├─ 00_global_method/
│  ├─ method standards
│  └─ templates
├─ 01_cells/
│  ├─ hail_solar/
│  ├─ flood_solar/
│  ├─ wind_wind/
│  └─ wildfire_solar/
└─ 99_source_context/
   └─ reference docs used by the library
```

This makes every cell portable. A reviewer can open one cell folder and understand the curve without searching across a pile of loose files.

## 2. Required cell folder structure

```text
01_cells/<cell_id>/
├─ current/
│  ├─ README_<cell_id>_<version>.md
│  ├─ curve_derivation_dossier_<cell_id>_<version>.md
│  ├─ damage_code_metadata_spec_<cell_id>_<version>.md
│  ├─ damage_curve_method_guide_<cell_id>_<version>.md
│  ├─ damage_curve_records_<cell_id>_<version>.xlsx
│  └─ optional crosswalk / special notes
├─ previews/
│  ├─ dashboard preview PNGs
│  └─ derivation audit preview PNGs
└─ archive/
   └─ prior major versions
```

## 3. Artifact purposes

| Artifact | Purpose | Audience |
|---|---|---|
| `README` | Fast orientation and cell snapshot | Everyone |
| `curve_derivation_dossier` | Proof trail for the curve | Reviewer / model governance |
| `damage_code_metadata_spec` | Inputs, selectors, conditioners, outputs | Engineering / implementation |
| `method_guide` | Cell-specific modeling narrative | Analyst / reviewer |
| `workbook` | Structured curve records, evidence logs, parameter tables, dashboards | Analyst / QA |
| `previews` | Quick visual checks | Everyone |
| `archive` | Traceability to prior versions | Governance |

## 4. Maturity levels

Not every cell needs to be equally mature on day one. Use explicit maturity labels.

| Level | Name | Meaning |
|---:|---|---|
| 0 | Scoped | Cell exists; failure-units and x-axis candidates identified. |
| 1 | Derived severity | A sourced severity curve exists, with derivation dossier. |
| 2 | Site-adaptable | Selectors, conditioners, and exposure variables are implemented. |
| 3 | Frequency-ready | Cell can consume site hazard frequency or return-period intensity. |
| 4 | Calibrated | Curve has claims/field calibration or statistically defensible validation. |

A cell can be useful at Level 1 or 2. It does not need to be Level 4 to be included, as long as limitations are explicit.

## 5. Read order inside a cell

```text
1. README
   └─ What is this cell? What fails? What curve exists?

2. Derivation dossier
   └─ Why this curve? What evidence? How are parameters fitted?

3. Metadata spec
   └─ What inputs and metadata does the damage code require?

4. Workbook
   └─ Structured records, formulas, dashboards, QA.

5. Method guide
   └─ Longer narrative and modeling boundaries.
```

## 6. Versioning rule

There are two version streams:

```text
Library/framework version
  = global documentation standard
  = e.g. v1.4 framework

Cell version
  = version of a specific hazard × asset package
  = e.g. hail_solar v1.3 curve derivation
```

The framework can advance without changing a cell's curve. In that case the package should say:

```text
framework version: v1.4
cell version: hail_solar v1.3
curve parameters: unchanged
```

## 7. ASCII package map

```text
GLOBAL METHOD
   │
   ├─ how to structure every cell
   ├─ how to document x-axis decisions
   ├─ how to document curve forms
   ├─ how to decide new curve vs adjustment
   ├─ how to capture selectors/conditioners/exposure
   └─ how to review evidence/provenance

CELL PACKAGE
   │
   ├─ specific hazard × asset snapshot
   ├─ specific failure-unit coverage
   ├─ specific curve derivation
   ├─ specific metadata interface
   └─ specific workbook records
```
