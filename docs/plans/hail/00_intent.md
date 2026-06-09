# 00 — Intent

*The seed for the hail → solar pipeline. Owner's framing, captured before we plan phases.*

## The goal

Take **one peril — hail — and build the whole end-to-end workflow in notebooks**, step by step, so we can
*see results at every step* (each cell: a description, the code, its output, plots, tables). This is the
first real implementation of the rebuilt approach — the proof that the foundations (principles + math +
references) actually compose into trustworthy numbers.

## Why hail (first)

> _Owner to fill in — the rationale for picking hail as the proving peril. (Noted that hail × solar is also
> the first concrete "cell" in the competitive-research architecture, and the peril with the richest
> documented under-counting evidence — Thompson 2024's ~300%.)_

## The two sides

1. **Input data (M0).** Understand the raw hail evidence and its architecture — adapted from the old
   `hazard_analysis` repo's data ingestion. The old repo is a **reference, not a template**: its data
   wrangling (NOAA Storm Events / FEMA / NRI fetchers) is worth adapting; its loss methodology is the
   anti-pattern we're escaping. Owner will guide this side.
2. **The model (M0 → M1 → M2 → M3).** From clean catalog through coupling, damage, and loss distribution —
   grounded in the competitive-research hail spec (`perils/hail/`), the A-series architecture, and the
   `hazard_math` notes. This is the substance of what we're building.

## Domain principles for this pipeline

This pipeline lives or dies by [`../../principles/`](../../principles/README.md), and especially:

- **Basics spot-on** — Phase 5 (loss & metrics) is exactly where the old repo collapsed. The metrics must
  derive from *one coherent loss distribution* (one compound-Poisson simulation), and be verified against a
  known-answer check before we trust a single number.
- **Standard interface, not standard physics** — hail is *areal hit-or-miss*; build its coupling/damage as
  hail-specific physics behind interfaces a future peril can reuse, not a one-size model.
- **Modular from day one** — each phase produces a clean, named object (event catalog → coupled events →
  damaged events → loss vectors) that the next phase consumes; the notebook structure mirrors that.

## What success looks like

A reviewable, step-by-step notebook series that takes raw hail data to a coherent annual loss distribution
for a solar asset and reads EAL / VaR / PML / TVaR off it — every step legible, every basic verified, and
the structure reusable for the next peril.

## Open questions (to resolve as we plan)

- The why-hail rationale (above).
- Side-1 scope: which sources are in for v1 (NOAA Storm Events vs MRMS/MESH vs NRI) and what the v1 "event
  record" must contain.
- The reference solar asset(s) to run the pipeline against.
- One notebook per phase, or a smaller/larger granularity?
