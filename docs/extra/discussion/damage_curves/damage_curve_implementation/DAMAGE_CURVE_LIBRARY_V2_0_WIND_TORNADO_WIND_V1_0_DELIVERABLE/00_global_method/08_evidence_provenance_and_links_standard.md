# 08 · Evidence, Provenance, and Link Standard

Every curve must be auditable. A reviewer should be able to see the source link, what fact was extracted, and exactly which parameter or rule it supports.

## 1. No orphan claims

A claim is orphaned if it appears in the curve logic but has no source ID or assumption ID.

```text
NOT OK:
  "Stow reduces hail damage by shifting D50 by 8 mm."

OK:
  "Directional support: sources indicate high-angle stow reduces direct impact exposure.
   Numeric generic shift: ASSUMP_HAIL_STOW_SHIFT_MM = +8 mm, low/medium confidence,
   replace with tracker-specific hail-stow testing."
```

## 2. Evidence hierarchy

Use the strongest evidence available, but label the type honestly.

| Evidence class | Examples | Typical trust |
|---|---|---|
| Claims / field loss data | insurer claims, post-event engineering assessments | high if clean and relevant |
| Lab / test data | hail stress sequence, component tests, wind tunnel tests | high for tested configuration |
| Analytical / physics model | structural load model, impact-energy model | medium/high if validated |
| Standards / ratings | IEC, FM, UL, design codes | good boundary/anchor, not full curve |
| Expert assumption | placeholder shift, generic cap | allowed if explicit and revisitable |

## 3. Source card format

Every source used in a dossier should have a source card:

```text
source_id:
title:
author_or_organization:
year:
url_or_file_path:
source_type:
what_it_supports:
exact_parameter_or_rule:
interpretation_notes:
limitations:
accessed_or_packaged_date:
```

## 4. Source-to-parameter table

| Source ID | Supports | Parameter/rule | How used | Limitation |
|---|---|---|---|---|
| `SRC_001` | x-axis availability | hail diameter / MESH | selected operational x-axis | not damage evidence |
| `SRC_002` | lab anchor | 50 mm breakage rate | curve fit anchor | sample/protocol limits |
| `ASSUMP_001` | stow adjustment | +8 mm D50 shift | placeholder conditioner | replace with tracker-specific evidence |

## 5. Link rule

Every external report, article, database, or source page should include a clickable URL in the dossier or workbook.

If the source is not public:

```text
url_or_file_path: internal file path or source repository pointer
access_control: private / licensed / client-provided
source_extract: short non-sensitive summary
```

## 6. Standards are anchors, not full curves

A certification standard can tell us something like:

```text
component passed X test condition
```

It usually does not tell us:

```text
full damage probability across all intensities
```

Therefore standards should be used as:

```text
- threshold anchors,
- lower-bound/no-damage context,
- design selectors,
- or validation checks,
```

not silently treated as complete damage curves.

## 7. Assumption register rule

Every assumption must state:

```text
assumption_id
current value
what it affects
confidence
direction of bias if wrong
replacement evidence
update trigger
```

This turns uncertainty into a managed part of the model rather than a hidden weakness.

## 8. Reviewer checklist for evidence

```text
[ ] Every source has a link or file pointer.
[ ] Every curve parameter maps to source ID or assumption ID.
[ ] Every assumption is labeled as an assumption.
[ ] Standards are used as anchors, not complete curves.
[ ] Evidence limitations are written next to the parameter they affect.
[ ] Alternative interpretations are documented where material.
```
