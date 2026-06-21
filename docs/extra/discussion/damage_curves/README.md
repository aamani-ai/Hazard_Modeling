# discussion/damage_curves/

**Where we think out loud about the *damage curve* — what it is, what *type* it should be, and what M3
emits — *before* we commit it to the architecture.** Nothing here is code or a plan-of-record; it's the
reasoning that *produces* the plan. Once a decision settles, it graduates to `docs/plans/` (`DD-*` / `A-*`)
and the [`infrasure-damage-curves`](../../../../infrasure-damage-curves) library, then to the M3 notebooks.

This folder consolidates what the project already has and has argued about damage curves — across the Drive
reference set, the curve library, the three built cells (hail×solar, wildfire×solar, convective-wind×wind-farm),
the learning logs, and earlier discussion notes — and splits the open calls into one sub-doc per
**independently-closeable** decision.

---

## The frame: a damage curve is three coupled choices

Not one curve, but **fragility × representation × value-allocation** (`[OURS]`,
[learning-log 05](../../../learning_logs/05_damage_curve_three_coupled_choices.md)):

- **fragility** — how intensity maps to *physical* damage (the shape);
- **representation** — what we *emit* (a scalar mean, a spread, a state vector, a full distribution);
- **value-allocation** — what share of asset value each subsystem carries (this sets the cap).

Most open questions below are really "which knob, on which of these three."

```
                    a damage curve is THREE coupled choices
                     (most open questions = "which knob?")

   [ FRAGILITY ] --(x)--> [ REPRESENTATION ] --(x)--> [ VALUE-ALLOCATION ]
   intensity -> damage     what M3 EMITS               subsystem value shares
   the shape (eng lit)     scalar .. distribution      -> the cap = sum(wi*Li)
                           (OPEN - doc 01)             (doc 03)
```

## Scope (the v1 box — read before arguing)

Everything here is about the curve **as built in v1**, which is deliberately narrow:

- **Single-site** — one asset; no portfolio / correlated multi-asset aggregation.
- **Damage-track only** — gross **physical repair/replacement cost**. No revenue-loss / curtailment /
  feathering / fatigue (that's the disruption track / Performance tier).
- **Occurrence basis, gross of financial terms** — no deductibles, limits, claims-made timing, or tax.
- **Current-climate** — intensity→damage; hazard-rate non-stationarity is a catalog/coupling concern.

When a sub-doc leaves this box, it says so.

## How this folder is organised (read in order)

| # | Doc | What it decides | Status |
|---|---|---|---|
| 00 | [`00_context_and_scope.md`](00_context_and_scope.md) | The settled ground: scope box, vocabulary, what's already decided, current state per cell, the library today, the how-to-choose framework. | 🟢 settled frame |
| 01 | [`01_emit_object.md`](01_emit_object.md) | **The headline** — what M3 emits (scalar / mean+spread / state-vector / distribution); interface-vs-content; per-peril vs uniform. Builds on [`../gpt/04`](../gpt/04_damage_representation_scalar_vector_distribution.md). | 🔴 open (Q1, Q5) |
| 02 | [`02_metrics_and_tail_honesty.md`](02_metrics_and_tail_honesty.md) | Which risk metrics ship at v1 under scalar-mean; what's withheld/caveated. | 🔴 open (Q2) |
| 03 | [`03_value_allocation_and_tiv.md`](03_value_allocation_and_tiv.md) | Generic capex vs plant-specific at-risk value; TIV reconciliation. | 🔴 open (Q4) |
| 04 | [`04_portfolio_extension.md`](04_portfolio_extension.md) | Single-site → correlated multi-asset aggregation. | 🔴 open (Q3) |
| 05 | [`05_aggregation_dependence.md`](05_aggregation_dependence.md) | Subsystem independence vs cascade / conditional failure. | 🔴 open (Q6) |
| 06 | [`06_financial_terms_and_scope_edges.md`](06_financial_terms_and_scope_edges.md) | Deductibles/limits/claims-made; physical-cap vs economic-loss; the disruption boundary. | 🔴 open (Q7) |
| 07 | [`07_component_attribute_depth.md`](07_component_attribute_depth.md) | Stow-angle (& tilt/age) pathway; subsystem vs component grain. | 🔴 open (Q8) |
| — | [`assumptions.md`](assumptions.md) | The `DC*` register for assumptions made *in this discussion*. | 🟡 draft |

## Related — don't duplicate, link

- The platform-level aggregation / double-counting discussion: [`../aggregation/`](../aggregation/README.md).
- The deeper prior treatment of the emit object: [`../gpt/04_damage_representation_scalar_vector_distribution.md`](../gpt/04_damage_representation_scalar_vector_distribution.md).
- The three-coupled-choices origin: [`../../../learning_logs/05_damage_curve_three_coupled_choices.md`](../../../learning_logs/05_damage_curve_three_coupled_choices.md).
- The curve library (the source for M3 severity): [`../../../../infrasure-damage-curves`](../../../../infrasure-damage-curves).
- The methodology + terminology (Drive = source of truth): [`../../../google_drive_docs/README.md`](../../../google_drive_docs/README.md) — §6 severity · §7 duration · §9 financial.
- The principles that govern every call: [`../../../principles/`](../../../principles/README.md).
- Per-cell registers: [hail](../../../plans/hail/assumptions.md) · [wildfire](../../../plans/wildfire/decisions.md) · [convective-wind](../../../plans/convective_wind/decisions.md).
- The scope-and-story anchor: [`../../00_scope_and_story.md`](../../00_scope_and_story.md).

## Status

🟡 **Open for discussion.** Frame settled (`00`). Headline open decision = the **emit object** (`01`) — it
gates which metrics are honest (`02`). Suggested sequence: close `01` first (it unblocks the rest), then
`02`/`03`, then the extensions (`04`–`07`).
