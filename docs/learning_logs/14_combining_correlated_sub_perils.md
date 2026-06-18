# Combining Correlated Sub-Perils That Share a Damage Curve — Max for Shared Ground, Additive for Disjoint, Blend Between (and Report the Envelope)

*Two flood sub-perils (riverine + pluvial) hit one solar farm through the **same** depth-damage curve. Do you **add** their losses or take the **worse**? Neither alone — it depends on whether they drown the **same** equipment or **different** equipment, and the honest answer is a blend reported as an envelope, not a single fabricated point.*

**Status:** v1.0 · written 2026-06-17 · **Sourced from:** flood × solar, M4 combine / [JD-FL-11](../plans/flood/decisions.md) + [research](../../jdocs/flood_subperil_research_result.md) · **Applies to:** any peril with ≥2 correlated sub-perils sharing one damage mechanism — flood (riverine/pluvial/coastal), hurricane (wind+surge+rain), compound events.

---

## Where this came from

Flood has two inland sub-perils — **riverine** (river overflow) and **pluvial** (rain ponding). Both are rain-driven
(correlated: one storm causes both) and both inundate the asset, scored by the **same** capex-weighted depth-damage
curve. M4 had to combine them into one annual loss. The instinct flip-flopped: **add** them (like convective_wind does
its tornado + strong-wind), or take the **worse** (a drowned inverter can't drown twice)? We built worse-wins, then a
"are you sure?" forced a research pass that resolved it.

## Why it looked fine — the trap

Two plausible-but-wrong shortcuts, each defensible in isolation:
1. **"Add them"** — the legacy/old-model move (and what convective_wind does for *its* sub-perils). Feels conservative
   and complete. But for flood it **double-counts**: the same storm, and the same equipment, billed twice.
2. **"Take the worse"** — physically clean (one component, one drowning). But it makes the dominant sub-peril
   **mask** the other entirely — here pluvial swallowed riverine, so the carefully-anchored riverine layer contributed
   *nothing* to the headline.

The trap is treating it as **one** choice (add *vs* max) when it's actually **two independent questions** — and when
the right answer for a *sibling peril* (convective_wind = add) doesn't transfer because the **mechanism differs**.

## The lesson

> **The lesson.** Decompose the combine into (a) **occurrence** — do they co-occur? — and (b) **severity** — given both
> occur, do they damage the **same** or **different** equipment? For correlated sub-perils, **co-sample one shared
> storm severity** (comonotonic), then combine by **max-depth-per-location → one damage evaluation**: `max` where they
> hit the **same** ground (a component drowns once — this is literally what Fathom/First Street do: *"max depth at each
> pixel"*), **additive** only where the ground is **disjoint**. With no sub-asset resolution this collapses to one
> honest knob — `L = max + (1−φ)·min`, φ = shared-ground overlap — reported as an **envelope** (φ=1 worse-wins → φ=0
> additive-capped), **not** a fabricated central. And **never sum per-sub-peril VaR/PML** — that silently assumes
> perfect dependence; always rebuild the *combined per-year vector* and compute metrics on it.

`[REF]` The Flood-Data-Ref says "combine without double-counting." `[OURS]` Building it surfaced the real decomposition
(occurrence × same-vs-different-equipment), that **the right rule differs by peril because the mechanism differs**
(wind *adds* — tornado/strong-wind hit *different subsystems*; flood *maxes* — same water, same equipment), and that
the honest output is an **envelope**, not a point. The external research (Bates 2021; FFRD/HEC-WAT; Guan 2023; Oasis
LMF) confirmed max-per-location + co-sampling and that **inland riverine↔pluvial dependence is a published knowledge
gap** — so φ is judgment, hence the reported band.

**Worked.** Elizabeth: riverine EAL 0.15% + pluvial 0.27%. Naive **add** = 0.42% (over-counts). **Worse-wins** (our
headline, φ=1, justified because a compact flat solar pad has *high* overlap) = **0.27%**. The two are the reported
**envelope (0.27%–0.42%)**; the headline stays single-valued so flood remains Total-Loss-combinable like every peril.

## How to recognize it next time

- **The tell:** two+ sub-perils feeding the **same** damage curve, and you're about to either `+` or `max` their
  losses. Stop and ask the **two** questions (co-occur? same equipment?) before picking.
- **Cross-peril:** don't copy a sibling peril's combine rule without checking the **mechanism** — `add` is right when
  sub-perils hit *different* components, `max` when they hit the *same*. Same repo, opposite rules, both correct.
- **Metric red flag:** if anyone sums per-peril VaR or PML, that's the comonotonic *upper bound*, not the answer —
  rebuild the combined vector.
- **Output discipline:** when the combine rests on an unmeasured dependence/overlap, report the **envelope**; resist
  inventing a precise central (φ=0.7) that dresses up a soft number.

## Caveats and limits

- **`max` under-counts genuinely disjoint low ground**; `additive` over-counts overlap. The φ-blend is a screening
  approximation, not a substitute for a real sub-asset spatial overlay.
- **Garbage-in caveat:** here the *headline is pluvial-dominated*, and pluvial is screening-grade (no depth anchor,
  the `f` knob — [learning context AFL-P2]). So the combine inherits the weakest layer's uncertainty; **report the
  marginals** so the solid sub-peril stays visible, and treat the headline as screening-grade.
- **Coastal/hurricane extension** needs an **event-identity** tag so one tropical cyclone's surge + rain + river rise
  are combined within the event (per-location max) and **not** billed twice across the flood and hurricane perils.

## Cross-references

- **Decision it generalizes:** [JD-FL-11](../plans/flood/decisions.md) (co-sample + worse-wins headline + additive
  envelope) · [JD-FL-10](../plans/flood/decisions.md) (sub-peril fork → combine at M4).
- **Research it rests on:** [`flood_subperil_research_result.md`](../../jdocs/flood_subperil_research_result.md) (Bates
  2021 max-per-pixel; FFRD shared-storm; Guan 2023 dependence gap; Oasis LMF metric aggregation).
- **Sibling learnings:** [`10`](10_monte_carlo_effective_sample_size.md) (metrics off an MC — the VaR-on-the-combined-
  vector discipline) · [`13`](13_densify_sparse_rp_anchor_the_shape.md) (the riverine side this combines with).
- **Where it shows in code:** `Notebooks/flood/solar/m4_loss_metrics/01_loss_metrics.ipynb` §2 (co-sample + worse-wins
  + recorded additive envelope).
