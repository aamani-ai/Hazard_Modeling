# Plan: Hail Pipeline

> **Status: hail × solar complete, hail × wind farm planning.** The first cell, **hail × solar**, now runs
> M0→M4 end-to-end with the full ~5.65-yr MRMS-on-AWS record (`λ_collection ≈ 29.6/yr`, NegBin
> over-dispersion confirmed, metrics real but record-limited). Completed hail × solar phase plans live in
> [`done/`](done/). The active next asset-cell plan is [`hail-wind-farm.md`](hail-wind-farm.md).

The first real implementation: take **one peril (hail)** and build the whole pipeline end-to-end in
notebooks, step by step, each cell with a description, output, plots, and tables. The executed notebooks
live in [`../../../Notebooks/hail/`](../../../Notebooks/hail).

## The two sides (owner's framing)

1. **Input data (M0).** Understand the raw hail evidence and its architecture — *adapted from the old
   `hazard_analysis` repo's ingestion* (take the wrangling, reject the loss methodology). Owner will guide.
2. **The model (M0 → M1 → M2 → M3).** Catalog → coupling → damage → loss distribution & metrics — grounded
   in the competitive-research hail spec, the A-series architecture, and the `hazard_math` notes.

## Built phase breakdown

| Phase | M-step | What we build | Notebook | Key references |
|------:|--------|---------------|----------|----------------|
| **1. Input data** ✅ | M0 (raw evidence) | Understand the raw hail data: sources (NOAA Storm Events hail, MRMS/MESH, FEMA/NRI), fields, spatial/temporal coverage, quality, what an "event record" is. Adapt old-repo fetchers/wrangling. | `m0_input_data/01_noaa_hydronos`, `02_mrms_aws` | old repo `noaastorm_fetcher`/`fema_fetcher`/`nri_fetcher`; H10; Hazard Data Reference (hail) |
| **2. Event catalog** ✅ | M0 → M1 | Turn raw evidence into a clean, reusable hail **event catalog** (ontology, backbone, footprint bundle + manifest) — the object the old repo never built. MRMS spine + NOAA cross-check. | `m1_catalog/01_event_catalog` | [`done/phase-2-event-catalog.md`](done/phase-2-event-catalog.md); [`DD-1`](decisions.md); `H10`; A20/A12/A24 |
| **3. Solar coupling** ✅ | M1 → M2 | Hail × solar = **areal hit-or-miss**: Minkowski `(√F+√s)²/A`, `λ_asset = λ_collection · p`, against the plant footprint. Fixes the old repo's point-factor error (known-answer checked). | `solar/m2_coupling/01_coupling` | [`done/phase-3-coupling.md`](done/phase-3-coupling.md); A21; `hazard_math/01`; old `issues/spatial-factor` |
| **4. Solar damage** ✅ | M2 → M3 | Curated PV `size → damage ratio` curve → per-event **conditional** loss (full loss on hit; `pᵢ` not multiplied in). Scalar v1; distribution/BI deferred. | `solar/m3_damage/01_damage` | [`done/phase-4-damage.md`](done/phase-4-damage.md); A22; methodology §6/§12 |
| **5. Solar loss & metrics** ✅ | M3 → M4 | **Compound-Poisson MC** → annual AEP/OEP → EAL, VaR, PML, TVaR. *The part the old repo broke — done right, with a Method-0 contrast + known-answer checks.* Metrics **real, record-limited** (λ fitted — DD-3 Stage 1). | `solar/m4_loss_metrics/01_loss_metrics` | [`done/phase-5-loss-metrics.md`](done/phase-5-loss-metrics.md); A24; methodology §8–§10; risk-metrics ref; `basics_spot_on` |

**Side 1** = Phases 1–2 ✅ · **Side 2** = Phases 3–5 ✅. **M0→M4 hail × solar runs end-to-end.** Next:
prove the asset axis with **hail × wind farm** (`wind/`) while keeping production hardening visible:
NOAA-calibrated λ extension · damage-curve calibration · financial terms · EVT tail.

## Active / discussion plans

- [`hail-wind-farm.md`](hail-wind-farm.md) — active plan for the next asset cell: hail × onshore wind farm.
- [`discussion/`](discussion/) — working notes before promotion into decisions, assumptions, or active plans.
- [`done/`](done/) — completed hail × solar phase plans.

## How each phase runs

The per-phase loop (Questions → Research → Decisions → Detailed Plan → Execute → Feedback → Document) per
[`../../workflows/feature_workflow.md`](../../workflows/feature_workflow.md). Each phase gets its own
`phase-N-*.md` plan file when we reach it.

## Files

- [`00_intent.md`](00_intent.md) — the seed: goal, the two sides, why hail, domain principles, open questions.
- [`01_references.md`](01_references.md) — bucketed, reasoned reference inputs.
- [`decisions.md`](decisions.md) — ADR-style decision log (DD-1 catalog source, DD-2 frequency).
- [`assumptions.md`](assumptions.md) — the **assumptions register** (every input/curve/simplification the build rests on, by layer).
- [`hail-wind-farm.md`](hail-wind-farm.md) — active plan for the hail × wind farm notebook cell.
- [`done/`](done/) — completed hail × solar phase plans.
- [`discussion/`](discussion/) — discussion notes and unresolved tradeoffs.
