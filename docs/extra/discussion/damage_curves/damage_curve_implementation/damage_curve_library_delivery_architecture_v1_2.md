# Damage-Curve Delivery Architecture v1.2

This document defines the recommended delivery structure for the damage-curve workstream. It is intentionally **cell-first**: the reusable library has one high-level method guide, and each hazard × asset pairing is delivered as a self-contained cell package.

The goal of this workstream is **not** to be the EAL engine or financial-metrics engine. The purpose is to define the correct **damage-code granularity, metadata, curve structure, and interface** so downstream hazard catalogs, exposure overlays, valuation ledgers, and financial metrics can consume it cleanly.

---

## 1. The operating model

```text
DAMAGE-CURVE LIBRARY
│
├─ Global method / delivery guide
│  └─ shared rules, schema, governance, and examples
│
└─ hazard × asset cell packages
   ├─ hail × solar
   ├─ flood × solar
   ├─ wind/tornado × wind
   ├─ wildfire × solar
   └─ ...future cells
```

Inside each cell:

```text
hazard × asset cell                  ← delivery / project-management unit
   │
   └─ failure-unit damage code        ← modeling unit
       │
       ├─ subsystem / component map   ← engineering vocabulary
       ├─ value-link bucket           ← valuation/reconciliation unit
       ├─ hazard axis                 ← what the hazard catalog supplies
       ├─ selectors                   ← fixed asset attributes
       ├─ conditioners                ← event-time states
       ├─ exposure geometry           ← how much of the value bucket is exposed
       ├─ curve parameters            ← damage function
       ├─ evidence / provenance       ← why this curve exists
       └─ metadata flags              ← open seams, cap sensitivity, QA notes
```

The core rule is:

```text
CELL = project-management unit
FAILURE-UNIT = damage-code / curve-record unit
SUBSYSTEM + COMPONENT = value-link and reconciliation unit
```

---

## 2. Why the delivery should be split this way

A single giant workbook for all hazards will become hard to audit. A separate package for every subsystem will create many empty or weak curves. The clean split is:

```text
one global method guide
   +
one package per hazard × asset pairing
```

This preserves two things at once:

1. **Consistency across cells** — every pair follows the same schema and governance.
2. **Cell-specific honesty** — each hazard × asset pair can document its own x-axis, metadata, open seams, and failure-unit coverage.

---

## 3. Recommended folder/package pattern

```text
damage_curve_delivery/
│
├─ 00_damage_curve_library_delivery_architecture.md
├─ 01_global_record_schema.xlsx or .md
├─ 02_governance_and_versioning.md
│
└─ cells/
   │
   ├─ hail_solar/
   │  ├─ README_hail_solar.md
   │  ├─ damage_curve_records_hail_solar.xlsx
   │  ├─ damage_code_metadata_spec_hail_solar.md
   │  ├─ method_guide_hail_solar.md
   │  ├─ dashboard_preview.png
   │  └─ archive/
   │     └─ prior working versions, if needed
   │
   ├─ flood_solar/
   │  ├─ README_flood_solar.md
   │  ├─ damage_curve_records_flood_solar.xlsx
   │  ├─ damage_code_metadata_spec_flood_solar.md
   │  └─ dashboard_preview.png
   │
   └─ wind_wind/
      ├─ README_wind_wind.md
      ├─ damage_curve_records_wind_wind.xlsx
      ├─ damage_code_metadata_spec_wind_wind.md
      └─ dashboard_preview.png
```

---

## 4. What belongs in the global guide vs cell packages

| Artifact | Scope | What it should contain |
|---|---|---|
| Global method guide | All cells | Principles, schema philosophy, x-axis/selector/conditioner/exposure definitions, evidence hierarchy, QA gates, naming conventions. |
| Cell README | One hazard × asset pair | What the cell does, primary failure-units, reviewed secondary units, x-axis, metadata, limitations, package contents. |
| Cell workbook | One hazard × asset pair | Curve records, curve parameters, value links, conditioning variables, QA tables, dashboard plots, and applied examples. |
| Metadata spec | One hazard × asset pair | Damage-code input/output contract: hazard fields, selectors, conditioners, exposure geometry, outputs, flags. |
| Dashboard preview | One hazard × asset pair | Visual summary of the curve and reporting ladder. |
| Archive | Optional | Prior iterations or intermediate working files, separated from the current deliverable. |

The principle is:

```text
Markdown explains reasoning.
Excel carries structured records, formulas, parameters, and plots.
Zip packages make each cell portable.
```

---

## 5. Damage-code interface pattern

Every future cell should document these layers:

```text
hazard input
   = what the hazard catalog gives the damage code

selector
   = fixed asset attribute that selects or shifts a curve family

conditioner
   = event-time state that changes vulnerability during the event

exposure geometry
   = how much of the relevant value bucket is actually exposed

value concentration f
   = share of the value bucket the failure mechanism can touch

output
   = damage ratio at the failure-unit grain, plus flags
```

ASCII model:

```text
hazard intensity
      │
      ▼
base damage curve
      │
      ├─ selector: fixed asset attribute
      │       module archetype, turbine class, IP rating
      │
      ├─ conditioner: event-time state
      │       tracker stow, energized state, feathered state
      │
      ├─ exposure geometry
      │       footprint hit, below-waterline, turbines in swath
      │
      └─ value concentration f
              material share, geometry share, component share
      │
      ▼
failure-unit damage ratio
      │
      ▼
downstream value / loss engine
```

---

## 6. How many curves should a cell have?

The answer depends on the hazard mechanism.

```text
If the mechanism concentrates on one failure-unit:
    one primary nonzero curve may be correct.

If the mechanism acts through several pathways:
    multiple failure-unit curves are required.

If a subsystem is reviewed but not materially affected:
    tag it DR≈0 / secondary / conditioner-only; do not force a weak curve.
```

Decision tree:

```text
candidate subsystem/component
   │
   ├─ distinct physical failure mechanism?
   │      └─ no → no separate curve
   │
   ├─ material value share?
   │      └─ no → secondary / DR≈0 row
   │
   ├─ sourceable enough for a curve?
   │      └─ no → placeholder / open seam
   │
   └─ yes
          └─ create a failure-unit curve record
```

---

## 7. Examples of expected granularity by cell

| Hazard × asset | Expected granularity | Why |
|---|---|---|
| Hail × solar | Single-primary curve: PV module glass/cell damage | Hail damage concentrates on panels/modules. Other subsystems should be reviewed, but not forced into weak curves in v1. |
| Flood × solar | Multi-term | Water depth/velocity can damage inverters, transformers, switchgear, SCADA cabinets, cabling, foundations, and drainage differently. |
| Strong wind / tornado × wind | Multi-term | Blades, rotor, nacelle, tower, pitch/brake state, and foundations have distinct mechanisms. |
| Wildfire × solar | Multi-term or two-dominant-term | Modules, wiring, combiner boxes, inverters, vegetation/civil, and substation exposure can each matter. |
| Lightning × wind | Multi-term, protection-centered | Blades, receptors/down-conductors, nacelle electronics, converter, transformer, and SCADA/protection systems may all matter. |

---

## 8. Required package checklist for every cell

```text
[ ] Cell README exists
[ ] Workbook exists
[ ] Metadata spec exists
[ ] Dashboard/preview exists
[ ] Primary failure-unit(s) declared
[ ] Reviewed secondary / DR≈0 units declared
[ ] Hazard axis declared
[ ] Selectors declared
[ ] Conditioners declared
[ ] Exposure geometry variables declared
[ ] Value-link bucket declared
[ ] Curve form and parameters declared
[ ] Evidence/provenance declared
[ ] Open seams declared
[ ] Outputs and metadata flags declared
[ ] Version and status declared
```

---

## 9. Recommended next package sequence

The first consolidated cell is:

```text
hail × solar v1.2
```

Then the recommended build sequence is:

```text
1. flood × solar
2. strong wind / tornado × wind
3. wildfire × solar
4. lightning × solar/wind
5. snow/ice × solar/wind
```

The reason to move to flood × solar next is that it exercises a different exposure concept:

```text
hail f  = material-share within PV_ARRAY
flood f = geometry/elevation share based on what is below waterline
```

---

## 10. Naming convention

Recommended names:

```text
damage_curve_records_<hazard>_<asset>_vX_Y.xlsx
method_guide_<hazard>_<asset>_vX_Y.md
damage_code_metadata_spec_<hazard>_<asset>_vX_Y.md
<ha‌zard>_<asset>_delivery_package_vX_Y.zip
```

Use lowercase file stems and underscores. Avoid spaces.

---

## 11. Status

This v1.2 delivery architecture is ready to use. The current first cell package is **hail × solar v1.2 consolidated**.
