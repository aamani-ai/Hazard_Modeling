# 10 · Review Checklist

Use this checklist before calling a hazard × asset cell package ready.

## 1. Package completeness

```text
[ ] README exists and has a snapshot tree.
[ ] Derivation dossier exists.
[ ] Damage-code metadata spec exists.
[ ] Workbook exists.
[ ] Previews exist for key dashboard/audit sheets.
[ ] Archive folder contains prior major versions, if any.
```

## 2. Coverage and granularity

```text
[ ] Primary nonzero failure-unit(s) are identified.
[ ] Conditioner-only equipment is identified.
[ ] Secondary / low-materiality equipment is reviewed.
[ ] DR≈0 direct-effect buckets are documented.
[ ] No subsystem is silently omitted if it holds material value.
[ ] No weak curve is added merely because a subsystem exists.
```

## 3. X-axis

```text
[ ] Selected x-axis is stated.
[ ] Unit and conversion rules are stated.
[ ] Source-native availability is described.
[ ] Alternatives are listed and rejected/parked with reasons.
[ ] Physics bridge is documented if applicable.
[ ] Multivariate variables are handled explicitly.
```

## 4. Curve derivation

```text
[ ] y-axis meaning is precise.
[ ] Evidence inventory includes links or file pointers.
[ ] Source-to-parameter mapping exists.
[ ] Raw anchors and interpreted anchors are separated.
[ ] Curve-form alternatives are discussed.
[ ] Selected curve form is justified.
[ ] Parameter derivation math is shown.
[ ] Assumptions are registered.
[ ] Open seams and update triggers are listed.
```

## 5. Selectors, conditioners, exposure

```text
[ ] Selectors are fixed asset attributes, not event states.
[ ] Conditioners are event-time states, not asset identity fields.
[ ] Exposure variables scale affected value, not fragility, unless explicitly justified.
[ ] Unknown/default behavior is defined.
[ ] Probability blends are used only for uncertain states, not hazard frequency.
```

## 6. Value linkage

```text
[ ] Each primary failure-unit maps to a subsystem/component value bucket.
[ ] Basis is labeled.
[ ] f_kind is labeled where relevant.
[ ] Cap_L is documented if the workbook computes it.
[ ] Physical damage and soft/sunk value are not silently mixed.
```

## 7. Damage-code interface

```text
[ ] Hazard input fields are declared.
[ ] Required selectors and conditioners are declared.
[ ] Outputs are failure-unit DRs first.
[ ] Convenience financial views are labeled as such.
[ ] Metadata flags are defined for defaults/extrapolation/open seams.
```

## 8. Ready status

Assign one of these:

```text
DRAFT
  structure exists; derivation incomplete

REVIEWABLE
  curve, evidence, and workbook are complete enough for technical review

SITE-ADAPTABLE
  selectors/conditioners/exposure inputs are implemented

CALIBRATED
  claims/field calibration or strong empirical validation is included
```

## 9. Final reviewer question

A cell is not ready until a reviewer can answer:

```text
Why this curve, and not another one?
Why this failure-unit grain?
Which source supports each load-bearing number?
What happens when metadata is missing?
What should be updated when better evidence arrives?
```
