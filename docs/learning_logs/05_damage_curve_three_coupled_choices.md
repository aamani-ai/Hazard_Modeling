# The Asset Damage Curve Is Three Coupled Choices — and Value-Allocation Is a Financial Decision

*Why "the hail damage curve" is never one thing: it's **fragility × representation × value-allocation**, and
the last one — how much **asset value** you assign to each physical subsystem — drives the loss as much as the
curve shape does. A reference for the `infrasure-damage-curves` revamp (and for our M3 severity).*

**Status:** v1.0 · written 2026-06-09 · **Sourced from:** hail × solar, M3 severity / the capex-weighted curve swap ([A15](../plans/hail/decisions.md)) · **Applies to:** the damage-curve library build, and severity for every peril/asset.

---

## Where this came from

Swapping our hail severity from a literature curve (extrapolated to ~100%) to the `infrasure-damage-curves`
**capex-weighted subsystem blend** dropped the 1-in-100 from 98% → 54% of TIV. That worked — but it exposed
that "the damage curve" had quietly bundled *three separate decisions*, and that the asset-value side of it is
not a footnote. This is a temporary asset-level fix; the real work happens in the curve repo, and these are
the things that build should get right.

## Why it looked simple — the trap

You ask for "the hail × solar damage curve" as if it's one object: hail size → damage %. But the number that
reaches the financial model is the product of **three independent choices**, and getting any one wrong moves
the loss as much as the others:

```
asset loss  =  Σ_subsystem [  value_weight_i   ×   DR_i( intensity )  ]   ×   asset_value
                              └─ allocation ─┘     └── fragility ──┘
                                                    (and its representation: mean? distribution?)
```

## The lesson

> **The lesson.** An asset damage curve is **fragility × representation × value-allocation**, not one curve.
> Source the *fragility* well, choose the *representation* to fit the metric (a mean kills the tail), and treat
> *value-allocation* as the **financial decision it is** — plant-specific, on an *at-risk-value* basis, not a
> generic capex split. The cap and the level of the whole curve fall out of the value-allocation, so it
> deserves the same rigor as the fragility physics.

### Choice 1 — Fragility (the physics, per subsystem) `[REF]`

The vulnerability of each part vs intensity. Source quality is everything: empirical/standard
(IBHS solar hail testing, IEC 61215 / UL 61730, real events) > expert-judgment. In `infrasure-damage-curves`
the PV_MODULE curve is medium-high confidence (L=0.95); the TRACKER/FIXED_MOUNT are expert-judgment (low).
Decompose by subsystem — modules fail at hail sizes that barely scratch steel mounting.

### Choice 2 — Representation (mean vs vector vs distribution) `[REF → A22 / methodology §6]`

What the stage *emits* per intensity:
- **scalar mean DR** (what we use now) — fine for EAL, but it **smooths away the severity spread**, so it
  *understates the tail* (two same-size events can damage very differently);
- **damage-state vector** (none/slight/moderate/extensive/complete) — HAZUS-style, finer;
- **full conditional distribution** of DR | intensity — the tail-honest choice for VaR/PML.

This is the open "what does the damage stage emit?" question flagged in our reference docs (methodology §6,
A22, `discussion/gpt/04`). Decide it **by the metric you're pricing**, not by convenience.

### Choice 3 — Value-allocation (the sleeper — and it's *financial*) `[OURS]`

`Asset_DR(x) = Σ wᵢ·DRᵢ(x)`, where `wᵢ` is the share of **at-risk asset value** in subsystem *i*. This is
where the curve's **cap and level actually come from**, and it's easy to treat as a throwaway weight when it's
really a financial-modeling decision:

- **The cap is set by allocation, not physics.** Our asset curve caps at ~34% *because* hail-vulnerable
  subsystems (modules 0.32 + mounting 0.10) are only ~42% of value and the rest is hail-immune. Re-allocate
  value and the cap moves — with no change to any fragility curve.
- **The value *basis* matters, and generic capex ≠ at-risk value.** A generic NREL capex split includes
  things that aren't really at-risk replacement value for a *specific existing* plant — e.g. **interconnection,
  development soft-costs, land, financing**. Weighting those as if they're at-risk dilutes the curve wrongly;
  for an existing asset the right basis is the **replaceable physical value** exposed to the peril. (Our
  current weights are generic + not yet optimal — the revamp fixes this.)
- **It must reconcile with the TIV (A19).** The asset value (denominator) and its subsystem allocation are two
  views of the same money — if the TIV carries sunk costs that the allocation treats as hail-immune, the
  %-of-TIV metrics read low; if the TIV itself is the wrong basis, every dollar metric inherits the error.
  *How much value you put on the physical module is as load-bearing as the fragility curve.*

## How to recognize it / apply it (for the curve-repo build)

- **Don't ship "an asset curve."** Ship `{fragility curves} + {representation} + {a value-allocation method}`,
  and make the allocation **plant-configurable** with an explicit, stated **value basis** (at-risk replacement
  vs total capex).
- **Pick the representation by the metric.** Scalar mean for EAL sanity; a conditional DR distribution before
  trusting VaR/PML.
- **Audit the weights as a financial step.** Ask "is this the at-risk value of the *physical* components for
  *this* asset?" — not "what's the generic capex split?"

## Caveats and limits

- Our current M3 curve sets **all three choices at their crude setting** (generic NREL weights · scalar mean ·
  expert-judgment mounting) — a deliberate temporary fix; the revamp refines each.
- This is the **severity-side counterpart** to the frequency learnings: the same *decompose + get-the-basis-
  right* discipline as [`learning_logs/04`](04_two_datasets_one_peril_decompose.md) (datasets) and
  [`/01`](01_extending_a_short_hazard_record.md) (record length).

## Cross-references

- **Decision / artifact:** [`decisions.md` DD-3](../plans/hail/decisions.md), assumptions [A15/A16/A17/A19](../plans/hail/assumptions.md); the vendored curve `data/hail/damage_curves/hail_solar_asset_capex_weighted.json`.
- **The curve library:** [`infrasure-damage-curves`](../../infrasure-damage-curves) (`research/HAIL_x_SOLAR.md`, `docs/aggregation-model.md`).
- `[REF]` methodology §6 (severity) + A22 (damage representation) + `discussion/gpt/04` (scalar/vector/distribution).
- **Principle:** [`hazard_asset_specificity.md`](../principles/hazard_asset_specificity.md) — *standard interface, not standard physics*; the same decompose-don't-conflate discipline.
