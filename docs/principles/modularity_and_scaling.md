# Modular From Day One — Build for the Next Peril, the Next Operator

*How we structure the code so that a new peril, a new asset type, a new data source, or a new operator slots
in by implementing an interface — not by editing a monolith and praying through the merge.*

This is not about horizontal scaling or sharding. It is about the harder problem: a model that must grow
**cell by cell** (peril × sub-peril × asset) for years, where every addition is a chance to either extend
cleanly or entangle further. The old model entangled. This document is how we don't.

---

## Why this document exists

The old repo's symptom was visible in its branch list: `bug/before_last_merge`, `bug/fixing_bad_merge`,
`fix/bad_merge`, `feature/fix_freq`. A repo that spends that much energy *recovering from merges* is a repo
whose structure can't absorb change. The root cause: a single `disaster_analysis.py` that spanned every
layer — hazard, exposure, vulnerability, financial, all interleaved. Touching one peril risked all of them.

When the structure can't absorb change, every new peril makes the next one harder, and "add hail support"
turns into a merge archaeology project.

---

## The principle: interfaces are the unit of growth

The rebuild is organized as modules with **typed boundaries** — the M0 → M1 → M2 → M3 → M4 pipeline (raw
evidence → catalog → coupling → damage → financial) — and the contract between stages is a standardized
object, not a function call into someone's internals.

> **The principle.** Growth happens by *implementing an interface*, never by editing a shared monolith.
> Adding a peril means writing a new adapter that emits the standard event-record/hazard-distribution
> object. The downstream loss engine never changes — it already consumes that contract.

The payoff is concrete: the frequency model can swap **Poisson → Negative Binomial → non-stationary λ(t) →
regime-switching** without touching the loss engine, because the engine only needs `draw_count()`. The
severity module can change its curve without the aggregator noticing. Each module is replaceable in
isolation.

---

## Build modular — but don't over-build

Modularity is not an excuse to construct the whole cathedral before the first mass.

> **The rule.** Build the *interfaces* up front; build the *implementations* one cell at a time. Phase 1 is
> **hail × solar, end to end.** Not a speculative 70-cell matrix — one real cell that exercises every seam,
> then the next (riverine flood, then hurricane).

This mirrors the A-series' deliberate deferral of the consolidated build-spec until ≥3 perils are actually
walked. The speculative-enumeration version was tried first and abandoned; the cell-by-cell version is the
lesson. Each phase must **ship value on its own** (Phase 1 = damage-track EAL/PML/VaR) and compound on the
prior — trying all phases in parallel ships none.

---

## Know where the walls are

Scalability here is not "can we handle the load" — it's *where does each choice break, and what replaces it?*
Document the wall before you hit it:

- A coupling type that fits hit-or-miss perils does **not** fit field-intensity perils — that's a known
  boundary, and the dispatch table is the migration path (already designed).
- A frequency model that assumes stationarity breaks under climate non-stationarity — λ(t) is the
  documented next step, swappable behind the same interface.
- The financial layer is **inherited wholesale** (OASIS fmcalc's recursion) rather than rebuilt — "the
  substrate is runtime, not content." Don't re-implement solved infrastructure.

> **The anti-pattern.** Solving a scaling problem before it arrives (over-engineering for perils we haven't
> committed to) *and* its opposite — hitting a wall with no migration path and being forced into a redesign
> under pressure. Document the breaking point; build to it, not past it.

---

## The boundary is sacred

The single most important structural rule: **peril pipelines emit a typed object; the shared engine consumes
it. Neither reaches across the boundary.** A pipeline calling engine internals, or the engine importing a
pipeline's modules, is *the* chief anti-pattern — and it is exactly what the monolithic `disaster_analysis.py`
did by spanning all five layers. If you find yourself importing across the seam, the design is already
drifting back toward the monolith.

---

## Caveats and honest limitations

1. **Interfaces have a design cost.** A typed boundary is more upfront thought than a direct call. It pays
   off only because this model is *built to grow*; a one-shot script wouldn't need it.
2. **Premature modularity is real.** Don't abstract a seam you've only seen once. The coupling types earned
   their interface by appearing across many perils in the research; invent a new module only when a second
   real case demands it.
3. **Inheritance over reinvention has limits.** Inheriting OASIS for the financial layer is right; inheriting
   a *content* assumption that doesn't fit renewables (single-centroid exposure) is the trap the competitive
   research flags. Conform to the *interface* standard; keep the renewable-specific *content* ours.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Standard interface, not standard physics**](hazard_asset_specificity.md) | Same idea, structural side: modular boundaries are *what lets* per-peril physics be specialized without the rest of the system caring. |
| [**Basics spot-on**](basics_spot_on.md) | Modularity is what makes the basics *verifiable*: a clean frequency/severity/aggregation seam can be unit-checked in isolation, so a wrong basic is caught at its module, not three layers downstream. |

---

## Summary

The old model couldn't grow without breaking because everything lived in one place. The rebuild grows by
addition, not surgery: typed interfaces between M0–M4, physics inside the modules, the boundary never
crossed. Build the interfaces up front and the implementations one cell at a time — hail × solar first,
each phase shipping value alone. Know where every choice breaks and keep the migration path written down.
A model designed this way absorbs the next peril instead of fighting it.
