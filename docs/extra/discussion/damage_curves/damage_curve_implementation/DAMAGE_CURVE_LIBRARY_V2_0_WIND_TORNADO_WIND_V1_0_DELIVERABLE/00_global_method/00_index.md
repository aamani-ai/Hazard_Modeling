# 00 · Global Method Index — Damage Curve Library v2.0 Framework Package

This folder contains the reusable **documentation and modeling standard** for every hazard × asset damage-curve cell.

The goal is not to force every cell into a rigid template. The goal is to make sure every future cell answers the same audit-critical questions:

```text
What can fail?
What curve represents that failure?
Why that x-axis?
Why that curve form?
Which evidence supports the parameters?
What selectors choose curve families?
What conditioners adjust the curve during the event?
What exposure/value variables scale the result?
Which alternatives were considered and rejected?
Which assumptions remain open?
```

## Library operating model

```text
DAMAGE CURVE LIBRARY
│
├─ global method docs
│  └─ reusable standards, templates, review checklists
│
└─ cell packages
   └─ one package per hazard × asset pair
      ├─ README
      ├─ derivation dossier
      ├─ damage-code metadata spec
      ├─ workbook
      ├─ previews
      └─ archive
```

The modeling hierarchy stays the same:

```text
CELL
  = project-management unit
  = e.g. hail × solar, flood × solar, wind/tornado × wind

FAILURE-UNIT
  = curve-record / damage-code unit
  = e.g. PV_MODULE_GLASS_CELL, INVERTER_ELECTRICAL_INGRESS, BLADE_STRUCTURAL

SUBSYSTEM / COMPONENT
  = value-link and reconciliation unit
  = e.g. PV_ARRAY / PV_MODULE, INVERTER_SYSTEM / INVERTER
```

## New in v2.0 — wind/tornado × wind v1.0 derived curves

v2.0 upgrades the wind/tornado × wind cell from v0.1 scaffold to v1.0 derived curves. The current cell now includes a detailed derivation dossier, source-to-parameter mapping, design-normalized logistic structural curves, tornado direct-hit variant, selector/conditioner/exposure rules, a workbook with formula-driven curves and dashboard charts, and a damage-code metadata spec.

## New in v1.9 — wind/tornado × wind reference pattern

v1.9 added `15_wind_tornado_wind_reference_pattern.md`, a reference pattern for the first wind-farm cell. It documents repeated-unit structural damage, blade/tower/nacelle/foundation coverage, pitch/brake/yaw conditioners, hub-height gust versus tornado wind-proxy x-axis decisions, EF-scale bridge logic, and turbine swath exposure.

## New in v1.8 — coverage role taxonomy

v1.8 adds `14_coverage_role_taxonomy.md`, a standalone detailed standard for classifying subsystems/components inside a hazard × asset cell as primary nonzero units, secondary/conditional units, conditioner-only equipment, exposure/protection modifiers, or `DR≈0` reviewed buckets. This is the document to use when deciding whether a subsystem needs its own curve, modifies another curve, changes exposure, or should be explicitly reviewed out.

## New in v1.7 — end-to-end architecture flow

Start with `13_end_to_end_damage_work_architecture.md` when you want the full system view: cell selection, substrate mapping, failure-unit coverage, x-axis decisions, curve-form choice, derivation proof, value link, damage-code interface, QA gates, and downstream boundaries. It includes both ASCII diagrams and a Mermaid flowchart.

## How to use these files

Recommended read order:

```text
00_index.md
01_delivery_architecture.md
13_end_to_end_damage_work_architecture.md
14_coverage_role_taxonomy.md
15_wind_tornado_wind_reference_pattern.md
02_cell_package_standard.md
03_failure_unit_coverage_standard.md
04_x_axis_decision_standard.md
05_curve_derivation_dossier_standard.md
06_curve_form_and_adjustment_standard.md
07_selector_conditioner_exposure_standard.md
08_evidence_provenance_and_links_standard.md
09_damage_code_interface_standard.md
10_review_checklist.md
```

Templates live in:

```text
00_global_method/_templates/
```

## Supportive standard, not a straitjacket

This framework is meant to reduce repeated format decisions so the actual work can focus on curve curation. It is not meant to block a cell that genuinely needs a different structure.

The rule is:

```text
Follow the standard by default.
Deviate when the hazard mechanism demands it.
Document the deviation clearly.
```

A deviation is acceptable when:

```text
- the hazard has a different causal structure,
- the evidence is available in a different form,
- a different y-axis is more honest,
- the curve must be state-based rather than continuous,
- multiple failure-units require a different workbook layout,
- or the cell is intentionally a thin/placeholder cell.
```

A deviation is not acceptable when it hides:

```text
- the x-axis decision,
- the source-to-parameter mapping,
- the curve-form rationale,
- the value-link basis,
- reviewed-but-not-modeled subsystems,
- or unresolved assumptions.
```


## Added in package v1.5

```text
12_flood_solar_reference_pattern.md
```

This new reference pattern captures the second archetype cell:

```text
flood × solar
= multi-failure-unit geometry cell
= depth above component datum for electrical ingress
= velocity/scour proxy for foundation/civil pathways
= site-geometry/elevation at-risk fraction
```


## Added in package v1.9

```text
15_wind_tornado_wind_reference_pattern.md
```

This new reference pattern captures the third archetype cell:

```text
wind/tornado × wind
= repeated-unit structural wind-farm cell
= blade / tower / nacelle / foundation failure-unit bundle
= pitch / brake / yaw as operating-state conditioners
= hub-height gust and tornado wind proxy as distinct pathways
= turbine count / swath as exposure geometry
```
