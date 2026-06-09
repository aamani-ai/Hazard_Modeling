# Workflow: Building a Capability (a peril pipeline)

A repeatable process for building a new capability from a blank page — for this repo, a **peril pipeline**
(e.g. hail → solar, end to end). Adapted from the `renewablesinfo_org` *Major Feature* workflow; the
per-phase loop is identical, the front matter is reasoned to fit modeling work.

> **What's different from the web-platform original.** Our deliverable per phase is a **notebook** (each
> cell = description → code → output → plot/table), not a deployed UI — so there is no `ui.md`.
> `architecture.md` (the M0→M3 data + math design) is *central*, not optional. And every phase is checked
> against [`../principles/`](../principles/README.md), especially **basics spot-on** (the foundation the
> old model skipped).

---

## Where things live

- **Plans** → `docs/plans/{initiative}/` — a folder per initiative (= `renewablesinfo_org`'s `docs/design/`).
- **Notebooks** (the executed work) → `Notebooks/{initiative}/` — one notebook per phase.
- When an initiative is done → archive its plan folder under `docs/plans/done/`.

## The plan folder (file set adapts to the initiative)

| File | Purpose |
|------|---------|
| `README.md` | Index: what this is, status, the phase table, links. Updated throughout. |
| `00_intent.md` | The seed — the problem, why it matters, initial direction, domain principles, open questions. |
| `01_references.md` | Curated external inputs, **bucketed and reasoned** — source · what it is · what we take · what we adapt/reject. Grows throughout. |
| `02_architecture.md` | The technical design: M0→M3 data flow, the catalog/coupling/damage/loss contracts, where reasoning fills the gaps references leave. |
| `phase-N-{name}.md` | One file per phase. Runs the per-phase loop below. |
| `feedback.md` | Living log of iteration decisions ("tried X, switched to Y because Z"), dated. |

Not every file is needed day one; write the seed (`README`, `00_intent`, `01_references`) first, let
`02_architecture` reveal the gaps, then break into phases **together**.

---

## The per-phase loop (the iteration)

Every phase runs the same 7-step cycle. This is the "research, reason, reference, plan, document, implement,
feedback" loop:

```
  1. QUESTIONS    — what decisions are needed? what's unknown? what could go wrong?
  2. RESEARCH     — read the real source data/code; verify assumptions against actual values, not estimates;
                    pull from references (old repo, competitive A-series, hazard_math, Drive docs).
  3. DECISIONS    — options + trade-offs + a recommendation; get alignment (or trust delegated judgment);
                    record the decision so later phases inherit the reasoning.
  4. DETAILED PLAN— files/cells to build (specific), ordered steps, the contracts/objects produced,
                    a verification checklist (known-answer checks — the basics-spot-on discipline).
  5. EXECUTE      — build the notebook step by step; each cell has a description, output, plot/table;
                    sanity-check after each step.
  6. FEEDBACK     — review the result together; fix before moving on; capture what changed in feedback.md.
  7. DOCUMENT     — update the README phase table + references; note decisions affecting later phases.
```

Phases execute **one at a time** and each should produce a standalone, reviewable result. Decisions
compound — early phases set patterns later ones follow, so get them right.

---

## Closing an initiative

When all phases are done: archive the plan folder to `docs/plans/done/{initiative}/`, fold durable learnings
into [`../principles/`](../principles/README.md) or the relevant `02_architecture.md`, and update the repo
`README.md` / `AGENTS.md` if the structure changed.
