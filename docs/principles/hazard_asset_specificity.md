# Standard Interface, Not Standard Physics

*How we capture hazard- and asset-specificity without drowning in special cases — and why **false
generality**, not complexity, is what broke the old model.*

This document is not about being maximally granular. Granularity for its own sake is its own failure mode
(see the caveats). It is about a harder discipline: knowing **where the physics genuinely differs** —
because there the model must specialize — and where the mechanism is truly the same — because only there
may it generalize.

---

## Why this document exists

Generality is seductive. One damage curve per hazard. One spatial factor for every asset. One distribution
fit reused across perils. It feels clean, it's less code, and it *looks* right because the headline number
(EAL) survives the simplification.

That is exactly the trap the old model fell into. It generalized across mechanisms that are not the same,
and the cost stayed hidden until it surfaced in the tail.

---

## The principle: specialize the physics, standardize the interface

A hurricane reaches a wind farm as a **continuous intensity field**. Hail reaches a solar plant as a
**finite footprint that either covers the asset or misses it**. A flood reaches a substation as a field
whose effect depends on the *specific elevation of each component*. These are not three settings of one
model — they are three different physical mechanisms, and each demands its own math.

What they *can* share is the **interface**: every peril, whatever its physics, emits the same typed object
(an event record, a hazard-distribution) that the downstream engine consumes. The physics lives *inside*
the adapter; the *shape of the handoff* is universal.

> **The principle.** Standardize the interface between stages. Specialize the physics within a stage.
> Generalize a parameter, curve, or coupling only when the underlying mechanism is *genuinely* identical —
> never because it's convenient.

This is the A-series' Axiom 1 ("standard interface, not standard physics") and the old repo's Principle 1
("Hazard × Asset Specificity") stated as one rule.

---

## The dual test: when to split, when to share

You cannot specialize infinitely, and you shouldn't. The test for whether two things deserve separate
treatment (from the peril taxonomy, A12) is **both**, not either:

1. **Distinct physical footprint** — does the hazard reach the asset by a different geometry/mechanism?
2. **Distinct data / magnitude metric** — is it measured and catalogued differently?

Pass *both* → split (own coupling, own curve, own parameters). Pass one or neither → share the treatment.
Hurricane wind and hail fail to share because they differ on both. Two hail events on the same plant share
because they differ on neither.

---

## What false generality cost the old model (the real incident)

The precursor audit catalogued **~10 forced-generalization instances**. The load-bearing ones:

- **One spatial factor, `F/A`, for every peril.** It treats every asset as a dimensionless point and uses a
  naïve footprint-over-area ratio. For an areal hit-or-miss peril on a real extended plant this *under-counts
  hit probability by 1.3×–7×*; the geometrically correct form for two convex shapes is `(√F + √s)²/A`. The
  same factor was applied to field-intensity perils, where the whole notion of a single "hit probability"
  is the wrong model. (See [`issues/spatial-factor.md`](../../hazard_analysis/docs/suggested_architecture/issues/spatial-factor.md).)
- **One damage curve per (hazard × asset).** No subcomponent structure, almost no component attributes —
  solar **stow angle**, the single most physics-active input for hail, had no home in the schema at all.
- **One distribution, fit once.** The same fitting path applied regardless of the peril's frequency regime
  (Poisson is the *wrong* default for convective storms / hail — they're over-dispersed; Negative Binomial
  fits).

> **The anti-pattern.** "One curve / one factor / one distribution to rule them all." It is less code today
> and a silent bias forever. The EAL survives the averaging (linearity of expectation), so it *looks* fine —
> which is precisely why it's dangerous.

---

## The shape of the answer: three coupling types

Specificity-with-a-shared-interface is concrete, not aspirational. The rebuild's coupling layer dispatches a
peril to **one of three coupling types**, each with its own math, behind one interface:

| Coupling type | Physics | Example perils | The math |
|---|---|---|---|
| **Areal hit-or-miss** | finite footprint; covered or not | hail, tornado, convective gust, fire perimeter | Minkowski `(√F + √s)²/A` |
| **Field intensity** | continuous field, uniform sub-point susceptibility | hurricane/synoptic wind, earthquake, snow, ice | sample-and-weight |
| **Site-conditioned** | continuous field, *non-uniform* per-asset susceptibility | flood, wildfire flame, storm surge | field × per-asset attribute join |

Three mechanisms, three models, **one** `event_record` contract out. That is the principle made real.

---

## Caveats and honest limitations

1. **Specificity has a cost.** Every split is more parameters to source, validate, and maintain. Specialize
   where evidence shows it *matters* (loss concentrates, or the mechanism truly differs) — not everywhere.
   The moat is *selective* subcomponent depth, not universal depth.
2. **Generalization is sometimes correct.** Where the mechanism is genuinely the same, sharing is right and
   over-splitting is just the false-generality error wearing the opposite mask.
3. **The interface must be designed, not discovered.** Standardizing the handoff only pays off if the typed
   contract is defined up front; bolting it on later reproduces the monolith.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Modular from day one**](modularity_and_scaling.md) | Specificity *needs* the modular boundary to live in: peril-specific physics inside a stage, a standard typed interface between stages. The two principles are the same idea seen from physics vs. structure. |
| [**Basics spot-on**](basics_spot_on.md) | The `F/A` over-count is *also* a basics failure — false generality and wrong math compound. Getting specificity right is part of getting the basics right. |

---

## Summary

A hazard model fails not from too much complexity but from the wrong *kind* of simplicity — collapsing
distinct physical mechanisms into one. Standardize the interface so the system stays composable; specialize
the physics so the numbers stay true. Split when (and only when) the footprint **and** the data differ.
Generalize only when the mechanism is genuinely the same. The old model generalized to look clean and was
wrong where it counted — in the tail, where the decisions live.
