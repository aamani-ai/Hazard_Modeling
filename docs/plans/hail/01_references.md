# 01 — References (raw inputs, reasoned — not blueprints)

*Per the workflow rule: a reference says "this is possible"; our architecture says "this is what we build,
adapted to us." Each entry: **what it is · what we take · what we adapt or reject.** Grows as we research.*

---

## Bucket A — Process (how we plan)

| Source | What it is | What we take / adapt |
|--------|-----------|----------------------|
| `renewablesinfo_org/docs/workflows` + `docs/design/` | The Major-Feature process + practiced plan folders | The per-phase loop + the plan-folder shape. **Adapted:** notebook-as-deliverable, no `ui.md`, `architecture.md` central. |
| `model-gpr/docs/plans` + `local_docs/plans` | Initiative folders with README + numbered phase/tier files + `done/` | The numbered-file + `done/` archive convention. |

## Bucket B — Side 1: Input data / catalog (M0) — the old repo

> **Reasoning posture:** the old `hazard_analysis` repo is a **source for data wrangling and an anti-pattern
> for loss math.** We adapt how it *fetches and shapes* hail evidence; we do **not** carry over its
> per-event-expected-loss or its `F/A` spatial factor.

| Source | What it is | What we take / reject |
|--------|-----------|------------------------|
| `hazard_analysis/src/noaastorm_fetcher.py` | NOAA Storm Events ingestion (hail reports) | **Take:** the source, fields, fetch mechanics. **Reason about:** report-based hail size vs gridded MESH. |
| `hazard_analysis/src/fema_fetcher.py`, `nri_fetcher.py` | FEMA / NRI ingestion | **Take:** what each adds (NRI expected-annual-loss context, baselines). **Reject:** using NRI EAL as the model output. |
| `hazard_analysis/src/combine_fema_noaastorm_data.py` | Source combination logic | **Take:** the join/dedup approach. **Reason about:** whether it produces a clean *event catalog* (the old repo's gap) or just merged rows. |
| `hazard_analysis/src/{data_processor,timeseries_processor,spatial_adjustments}.py` | Downstream shaping | **Take selectively.** **Reject:** anything entangled with `disaster_analysis.py` (the Layers-1–5 monolith). |
| `hazard_analysis/analysis/damage_subsystems/hail_damage/` + `docs/updates/*stow_angle_hail*` | Prior hail × solar damage analysis (stow angle) | **Take:** the physics insight (stow angle is the dominant input). Feeds Phase 4. |

## Bucket C — Side 2: The model (M0 → M3) — competitive research + math

| Source | What it is | What we take |
|--------|-----------|--------------|
| `infrasure-hazard-competitive-research/learnings/architecture/perils/hail/H00` | Hail v1 scope & commitments | The scope contract for what Phase 1–5 must (and must not) cover. |
| `…/perils/hail/H10_m0_m1_catalog.md` | The M0→M1 catalog spec for hail | The catalog design for Phase 2. |
| A-series: `A20` (catalog), `A21` (coupling — Minkowski), `A22` (damage), `A24` (distributions) | Comparative-architecture-as-spec | The seam designs for Phases 2–5. **Reason:** these are *option spaces*, not final commitments. |
| `Learning/ML-DL/InfraSure_related/hazard_math/01–05` | The structural math (Bernoulli → Poisson → severity → MC → EVT) | The math for Phases 3–5; `04` (MC annual loss) is the Phase-5 engine. |
| `docs/google_drive_docs/` — risk-metrics, terminology, methodology | Output vocabulary + the loss-distribution doctrine | The metric definitions + the doctrine the pipeline implements. |

## Bucket D — In-repo grounding

| Source | What it is |
|--------|-----------|
| [`../../extra/00_scope_and_story.md`](../../extra/00_scope_and_story.md) | The origin story + folder map. |
| [`../../principles/`](../../principles/README.md) | The three principles every phase is checked against. |

---

*Open: confirm hail data sources for v1, and whether MRMS/MESH gridded intensity is in scope for Phase 1 or
deferred. To be resolved in `02_architecture.md` once the phase breakdown is aligned.*
