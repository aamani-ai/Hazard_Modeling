# 06 · Curve Form and Adjustment Standard

This document explains how to choose a curve form and how to decide whether a new configuration requires a new curve or an adjustment to an existing curve.

## 1. Why curve-form documentation matters

A curve can look credible even when it is only a nice-looking formula. The deliverable must show:

```text
why this form,
why not the alternatives,
what evidence supports its anchors,
what assumptions set its shape,
and where the curve should not be trusted.
```

## 2. Common curve forms

| Form | Typical use | Pros | Cons |
|---|---|---|---|
| Step threshold | pass/fail standards, cliff-like failures | simple, transparent | unrealistic discontinuity for expected loss |
| Piecewise linear | sparse anchors | transparent, easy to audit | can create artificial kinks |
| Bounded logistic | fragility-like transitions | smooth, bounded, interpretable D50/slope | can look over-precise if anchors are weak |
| Damage-state probabilities | state-based evidence | supports severity states | more complex emit object |
| Empirical lookup table | claims/lab bins | source-native | may be sparse/noisy |
| Analytical/physics model | structural or thermal mechanisms | mechanistic | needs calibration/inputs |

## 3. Bounded logistic rationale

A bounded logistic is often useful when:

```text
- damage probability increases monotonically with hazard intensity,
- loss is naturally bounded between 0 and a cap,
- there is a transition zone rather than a hard threshold,
- evidence provides one or more breakage/loss anchors,
- and D50 is an interpretable parameter.
```

Formula:

```text
DR(x) = L / (1 + exp(-k × (x - x50)))
```

Where:

```text
L    = upper bound / maximum damage ratio for the failure-unit
x50  = intensity where DR reaches L/2
k    = steepness
```

For hail × solar, the default v1 uses a bounded logistic because module breakage behaves like a transition from mostly intact to mostly replacement-trigger damage as hail diameter increases. The dossier must still show why alternatives were not selected.

## 4. When to create a new curve

Create a new curve when:

```text
- the physical failure mechanism changes,
- the material construction changes enough that source evidence supports different parameters,
- the y-axis meaning changes,
- the x-axis changes materially,
- or the evidence source directly reports a distinct curve/fragility family.
```

Examples:

```text
2.0 mm glass//glass module vs 3.2 mm glass//backsheet module
  may justify separate module archetype curves if source evidence supports different breakage behavior.

flood electrical ingress vs flood foundation scour
  require separate curves because mechanisms and x-axes differ.
```

## 5. When to adjust an existing curve

Adjust an existing curve when the mechanism is the same but resistance, angle, exposure, or event-time state changes.

| Adjustment type | What it changes | Use when | Example |
|---|---|---|---|
| Horizontal shift | intensity needed to reach same damage | resistance changes | thicker glass shifts hail curve right |
| Vertical multiplier | maximum or realized damage | exposed fraction or partial severity changes | protective cover reduces max damage |
| Probability blend | expected curve under uncertain state | event-time state uncertain | `P(stowed) × DR_stowed + (1-P) × DR_unstowed` |
| Exposure multiplier | affected value, not fragility | only part of asset is hit | hail swath covers 60% of array |
| Cap/value change | financial cap, not engineering DR | different value share or f | module BOM f changes cap_L |

## 6. What should not be called a curve adjustment

Do not change the engineering damage curve when the variable only changes value exposure.

```text
array_exposure_fraction
  changes loss dollars and %TIV,
  but does not mean the module is more/less fragile.

f_hail material share
  changes the value cap,
  but does not change the probability that a module breaks.
```

## 7. Selector vs conditioner effect on curves

```text
selector
  fixed asset attribute
  chooses curve family or parameter set

conditioner
  event-time state
  shifts or blends the selected curve

exposure
  affects how much value the curve applies to
```

For hail × solar:

```text
module_archetype
  selector → fragile/default/hardened curve family

stow_state
  conditioner → unstowed/stowed/probabilistic blend

array_exposure_fraction
  exposure → scales loss, not module DR
```

## 8. Required adjustment-rule table

Every cell with variants should include:

| Variable | Type | Current treatment | Source support | Caveat |
|---|---|---|---|---|
| `module_archetype` | selector | chooses curve family | source/test evidence | source sample limits |
| `stow_state` | conditioner | shifts/blends curve | directional support | generic magnitude assumption |
| `exposure_fraction` | exposure | multiplies affected value | site geometry | not a fragility variable |
