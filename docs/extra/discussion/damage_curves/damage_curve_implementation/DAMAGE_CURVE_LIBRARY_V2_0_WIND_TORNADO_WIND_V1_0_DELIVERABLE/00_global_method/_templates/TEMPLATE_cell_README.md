# README — `<hazard> × <asset>` Damage-Curve Cell `<version>`

## 1. Cell identity

```text
cell_id: <HAZARD_ASSET>
hazard: <hazard>
asset_class: <asset>
cell_version: <version>
framework_version: <version>
status: DRAFT | REVIEWABLE | SITE-ADAPTABLE | CALIBRATED
```

## 2. Snapshot tree

```text
<hazard> × <asset>
├─ primary nonzero failure-unit(s)
│  ├─ <SUBSYSTEM> / <COMPONENT> / <failure trigger>
│  └─ <optional second failure-unit>
│
├─ conditioner-only equipment
│  └─ <equipment that changes another curve>
│
├─ reviewed secondary / low-materiality equipment
│  └─ <reviewed but not modeled in v1>
│
└─ DR≈0 direct-effect buckets in this version
   ├─ <SUBSYSTEM>
   └─ <SUBSYSTEM>
```

## 3. Scope

Included pathways:

```text
- <pathway>
- <pathway>
```

Excluded / deferred pathways:

```text
- <pathway> — reason and update trigger
```

## 4. Primary curve summary

| Curve ID | Failure-unit | X-axis | Y-axis | Value link | Status |
|---|---|---|---|---|---|
| `<curve_id>` | `<failure_unit>` | `<x_axis>` | `<damage_ratio>` | `<value_bucket>` | `<status>` |

## 5. X-axis decision

Selected x-axis:

```text
<x_axis_id>: <description>
unit_internal: <unit>
source_units_allowed: <units>
```

Alternatives considered:

| Candidate | Decision | Reason |
|---|---|---|
| `<axis>` | selected / bridge / rejected / future | `<reason>` |

## 6. Curve form

Selected form:

```text
<formula or state model>
```

Why selected:

```text
<short rationale>
```

Alternatives not selected:

| Alternative | Reason not selected |
|---|---|
| `<form>` | `<reason>` |

## 7. Selector / conditioner / exposure map

| Field | Role | Required? | Default | Effect |
|---|---|---|---|---|
| `<field>` | selector / conditioner / exposure / value_modifier | yes/no/conditional | `<default>` | `<chooses/shifts/blends/scales>` |

## 8. Value link

```text
value_bucket:
basis:
f_kind:
cap_L:
```

## 9. Evidence and derivation

Detailed proof lives in:

```text
curve_derivation_dossier_<cell_id>_<version>.md
```

Key sources:

| Source ID | Link | Supports |
|---|---|---|
| `<SRC_ID>` | `<url_or_file_path>` | `<what it supports>` |

## 10. Workbook map

| Question | Workbook sheet |
|---|---|
| Curve records | `<sheet>` |
| Evidence mapping | `<sheet>` |
| Curve fit | `<sheet>` |
| Assumptions | `<sheet>` |
| QA | `<sheet>` |

## 11. Open seams

| Seam ID | Description | Why it matters | Update trigger |
|---|---|---|---|
| `<SEAM_ID>` | `<description>` | `<impact>` | `<trigger>` |

## 12. Implementation notes

```text
<notes for damage-code implementation>
```
