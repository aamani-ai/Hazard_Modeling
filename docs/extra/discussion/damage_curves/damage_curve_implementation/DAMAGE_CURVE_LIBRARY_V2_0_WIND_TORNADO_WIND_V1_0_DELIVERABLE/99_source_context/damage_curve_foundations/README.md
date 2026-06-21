# Damage-curve foundations — discussion & principles

The reasoning that produced the damage layer's foundational decisions, in dependency order.
Question-docs (`questions/`) decide *what we build and why*; principle-docs (`principles/`) are the
cross-cutting beliefs that govern *how* we reason. Read in number order.

## The deliverable the discussions produce

`00_assembled_curve_record.md` — **the integrating spine.** The six question-docs are *many
discussions that assemble into one deliverable*: a per-failure-unit curve record, every field mapped
to the doc that governs it, with a fill-order runbook and a worked example. Read this to see how the
pieces compose into one output; read the question-docs for the reasoning behind each field. (The
filled-in records are built separately, by running the discussions against this spec.)

## Questions (the foundational decisions)

| # | Doc | Decides | Status |
|---|---|---|---|
| **01** | `questions/01_granularity.md` | At what grain damage curves are built — subsystem-default, cap + sum, **no grouping primitive** (grouping only if joint ≠ sum) | 🟢 decided |
| **02** | `questions/02_x_axis_intensity_variable.md` | What's on the x-axis — **univariate for v1**; two escapes; chain-position rule; wildfire residence-time deferred | 🟢 near-final |
| **03** | `questions/03_valuation_guide.md` | How dollar value is assigned — a *guide*: 3 questions, **basis-first**, placeholders-with-provenance | 🟡 guide done; numbers later |
| **04** | `questions/04_curation_derivation.md` | **How a curve is derived** — evidence hierarchy, standards as boundary conditions, functional form by a *parsimony rule* (not reflexive lognormal); constrains the emit object | 🟡 guide done; curves later |
| **05** | `questions/05_emit_object.md` | What the curve emits per event — decided by the **first nonlinearity**; distribution-ready interface, scalar-where-linear content | 🟢 decided (v1) |
| **06** | `questions/06_metrics_and_tail_honesty.md` | Which metrics are honest / ship — EAL where cap rarely binds; tail = **withheld, not caveated** under scalar | 🟢 decided |

Reading order follows the dependency chain: grain (01) underlies everything → what's on the axis
(02) → how value is assigned (03) → **how the curve is derived (04, which constrains what can be
emitted)** → what's emitted (05) → which metrics are honest (06).

## Principles (cross-cutting, outlive the damage work)

| # | Doc | The belief |
|---|---|---|
| **P1** | `principles/P1_system_coherence_over_local_elegance.md` | The whole pipeline is the judge; burden of proof on the departure; willing to come back empty |
| **P2** | `principles/P2_discussion_before_commitment.md` | Reasoning is the cheapest place to be wrong; the slow conversation is the work |
| **P3** | `principles/P3_reference_is_input_not_authority.md` | Use a reference for its purpose; re-derive across the boundary; provenance travels |

These join the three inherited foundational principles (`basics_spot_on`, `hazard_asset_specificity`,
`modularity_and_scaling`).

## Still parked (from the agreed sequence)

After 05 finishes: portfolio extension · cascade/interaction (the one open door for a future grouping
primitive) · financial terms + disruption boundary (mostly settled by the physical-only line) ·
component-attribute depth (stow angle, Phase-3).

## Note on external links

Some links point *outside* this bundle and are intentional: (1) the three **inherited principles**
(`basics_spot_on`, `hazard_asset_specificity`, `modularity_and_scaling`) live in the project's
existing principles folder; (2) links labelled **"(parked)"** point to the original discussion
folder's open-question docs (portfolio, cascade, financial-terms, component-depth, context) not part
of this reorganization. These resolve in the full project tree, not inside this standalone zip.

## Note on numbering

These were renumbered into clean reading order. The original exploratory filenames (`08` granularity,
`00x` x-axis, etc.) came from an earlier discussion folder's scheme; this set supersedes them. Links
labelled "(parked)" point to the original discussion folder's open-question docs not yet folded into
this reorganization.
