# 07 · Component-attribute depth — stow angle & friends  🔴 OPEN (Phase-3)

Today the curve is **subsystem-grain**. Component attributes — solar **stow angle** (flagged "the single most
physics-active input for hail"), tilt, module age, glass thickness beyond spec-match — have no home yet. The
old model's lack of exactly this was a load-bearing failure
([`hazard_asset_specificity.md`](../../../principles/hazard_asset_specificity.md)).

## The decision (Q8)

| Option | What it does | Trade |
|---|---|---|
| **(a) Hold at subsystem grain** ← today | no component attributes in v1 | the moat is *selective* depth — build it only where loss concentrates |
| **(b) Prototype stow angle for hail×solar** | one proof case for the deepest-physics attribute | proves the pathway; scoped |

## The dual test (when depth is justified)

Add a split only if **both** hold: (1) distinct physical footprint/mechanism **and** (2) distinct
data/magnitude metric. Stow angle passes for hail (operational stow materially changes impact) — but the
*mechanism* is undecided.

## The unarchitected mechanics (why it's not just "add a column")

- **How** does the attribute act — shift `x₀` (protective stow moves the 50 %-damage midpoint), **fork** the
  curve per discrete angle, or apply a **multiplier**?
- **Where** — M2 coupling (effective intensity at the array) or M3 curve selection?
- **Which** angles / seasonal & diurnal variation?

```
   how might an attribute (e.g. stow angle) act on the curve?

   (a) SHIFT x0             (b) FORK per angle        (c) MULTIPLIER
    DR|    ,-  ,-            DR|   ,- 0deg              DR|    ,- x1.0
      |   /  /                 |  / ,- 30deg             |   / ,- x0.6
      |  / /   protective      | /,/- 60deg (stow)       |  //
    --+-'--'----> x          --+'-'-------> x          --+'------> x
      stow moves midpoint       one curve per angle       scale DR down

   ... and WHERE does it act:  M2 (effective intensity)  or  M3 (curve selection)?
```

No design doc exists. Also open: does subsystem grain mask within-subsystem variation (junction box vs module
glass)?

## Status

🔴 **Open, Phase-3.** Named but not architected.

## To decide

1. (a) / (b) for now.
2. If (b): the mechanism (x₀-shift / fork / multiplier) and the pipeline location (M2 vs M3).

*Links:* [`00 §3`](00_context_and_scope.md) · [LL05](../../../learning_logs/05_damage_curve_three_coupled_choices.md) ·
[`hazard_asset_specificity`](../../../principles/hazard_asset_specificity.md).
