# Build Strategy — notebooks-first across 3 hazards, *then* the real architecture

> **Status:** active strategy-of-record (2026-06-09). Read this before proposing any "production" folder
> structure or database wiring.

## The decision

We are deliberately **not** jumping into the real code/folder architecture yet. The order is:

1. **Build the full M0→M4 pipeline end-to-end *in notebooks*, for three different hazards** —
   - **Hail** ✅ (M0→M4 done: NOAA/MRMS → catalog → coupling → damage → loss & metrics)
   - **Wildfire** — next
   - **Wind** (or another) — after
2. **Then** — with that cross-hazard experience in hand — design the **production architecture**: the proper
   dev code that connects to a database, stores results, and runs as a real system.

## Why this order

- The architecture's value is the **shared interface across hazards** ("standard interface, not standard
  physics" — `docs/principles/`). You can only see what's genuinely shared vs hazard-specific *after* building
  more than one peril. Hail alone would over-fit the abstraction.
- Each hazard differs where it matters (coupling type, intensity metric, damage curve, data sources). Three
  worked examples (areal hit-or-miss hail · site-conditioned wildfire · field/areal wind) span the variance
  the architecture must absorb.
- Doing it notebook-first keeps each step **inspectable and method-neutral** (per `docs/principles/notebook_work/`)
  while the methodology is still settling. The notebooks are the spec the architecture will be built *from*.

## What's deferred (and the reference for it)

- **The production folder architecture + DB layer** is *far in the future* — not this phase.
- When we get there, the owner has a **project-structure reference** (good variance/templates for this kind of
  project) in the `Learning/` knowledge base to draw on. Use it **then**, not now.
- Don't propose a "real" `src/` layout, ORM, or service structure until the 3 hazards are through the
  notebooks and we deliberately open the architecture phase.

## How this connects to `scripts/`

The repo-root [`scripts/`](../../scripts/) folder is **testing / one-time / utility scripts** that support the
notebooks (e.g. the MRMS record scan) — **not** production code. It is explicitly *not* the start of the
production architecture. See [`scripts/README.md`](../../scripts/README.md). When the architecture phase opens,
production code lives in its own (future) structure, and these scripts stay what they are: scaffolding.

## The throughline

Notebooks (3 hazards) → *learned* architecture → production code + DB. We're in step 1, hazard 1-of-3 done.
