# Plan: Hail → Solar, End-to-End Pipeline

> **Status: building.** **Phase 1 (M0 input data)** ✅ · **Phase 2 (M0→M1 event catalog)** ✅ ([plan](phase-2-event-catalog.md))
> · **Phase 3 (M1→M2 coupling)** ✅ ([plan](phase-3-coupling.md)) · **Phase 4 (M2→M3 damage)** ✅
> ([plan](phase-4-damage.md)) · **Phase 5 (M3→M4 loss & metrics)** ✅ — compound-Poisson MC → EAL/VaR/PML,
> verified ([plan](phase-5-loss-metrics.md)). **🎉 M0→M4 runs end-to-end** — and **Stage-1 widening is done**
> (full ~5.65-yr MRMS record; λ **fitted** ≈29.6/yr, over-dispersion **confirmed** φ≈3.4 → NegBin; metrics now
> **real but record-limited**, DD-3). **Next: the severity curve** (it's running the metrics hot — DD-3 Stage 2 /
> calibrate damage curve / EVT tail).

The first real implementation: take **one peril (hail)** and build the whole pipeline end-to-end in
notebooks, step by step, each cell with a description, output, plots, and tables. The executed notebooks
live in [`../../../Notebooks/hail/`](../../../Notebooks/hail).

## The two sides (owner's framing)

1. **Input data (M0).** Understand the raw hail evidence and its architecture — *adapted from the old
   `hazard_analysis` repo's ingestion* (take the wrangling, reject the loss methodology). Owner will guide.
2. **The model (M0 → M1 → M2 → M3).** Catalog → coupling → damage → loss distribution & metrics — grounded
   in the competitive-research hail spec, the A-series architecture, and the `hazard_math` notes.

## Proposed phase breakdown  *(pending your alignment)*

| Phase | M-step | What we build | Notebook | Key references |
|------:|--------|---------------|----------|----------------|
| **1. Input data** ✅ | M0 (raw evidence) | Understand the raw hail data: sources (NOAA Storm Events hail, MRMS/MESH, FEMA/NRI), fields, spatial/temporal coverage, quality, what an "event record" is. Adapt old-repo fetchers/wrangling. | `m0_input_data/01_noaa_hydronos`, `02_mrms_aws` | old repo `noaastorm_fetcher`/`fema_fetcher`/`nri_fetcher`; H10; Hazard Data Reference (hail) |
| **2. Event catalog** ✅ | M0 → M1 | Turn raw evidence into a clean, reusable hail **event catalog** (ontology, backbone, footprint bundle + manifest) — the object the old repo never built. MRMS spine + NOAA cross-check. | `m1_catalog/01_event_catalog` | [`phase-2-event-catalog.md`](phase-2-event-catalog.md); [`DD-1`](decisions.md); `H10`; A20/A12/A24 |
| **3. Coupling** ✅ | M1 → M2 | Hail = **areal hit-or-miss**: Minkowski `(√F+√s)²/A`, `λ_asset = λ_collection · p`, against the plant footprint. Fixes the old repo's point-factor error (known-answer checked). | `solar/m2_coupling/01_coupling` | [`phase-3-coupling.md`](phase-3-coupling.md); A21; `hazard_math/01`; old `issues/spatial-factor` |
| **4. Damage** ✅ | M2 → M3 | Curated PV `size → damage ratio` curve → per-event **conditional** loss (full loss on hit; `pᵢ` not multiplied in). Scalar v1; distribution/BI deferred. | `solar/m3_damage/01_damage` | [`phase-4-damage.md`](phase-4-damage.md); A22; methodology §6/§12 |
| **5. Loss & metrics** ✅ | M3 → M4 | **Compound-Poisson MC** → annual AEP/OEP → EAL, VaR, PML, TVaR. *The part the old repo broke — done right, with a Method-0 contrast + known-answer checks.* Metrics **real, record-limited** (λ fitted — DD-3 Stage 1). | `solar/m4_loss_metrics/01_loss_metrics` | [`phase-5-loss-metrics.md`](phase-5-loss-metrics.md); A24; methodology §8–§10; risk-metrics ref; `basics_spot_on` |

**Side 1** = Phases 1–2 ✅ · **Side 2** = Phases 3–5 ✅. **🎉 M0→M4 runs end-to-end.** Next: **production
hardening** — widen the MRMS record (→ real λ + NegBin fit) · calibrate the damage curve · financial terms + EVT tail.

## How each phase runs

The per-phase loop (Questions → Research → Decisions → Detailed Plan → Execute → Feedback → Document) per
[`../../workflows/feature_workflow.md`](../../workflows/feature_workflow.md). Each phase gets its own
`phase-N-*.md` plan file when we reach it.

## Files

- [`00_intent.md`](00_intent.md) — the seed: goal, the two sides, why hail, domain principles, open questions.
- [`01_references.md`](01_references.md) — bucketed, reasoned reference inputs.
- [`decisions.md`](decisions.md) — ADR-style decision log (DD-1 catalog source, DD-2 frequency).
- [`assumptions.md`](assumptions.md) — the **assumptions register** (every input/curve/simplification the build rests on, by layer).
- [`phase-2-event-catalog.md`](phase-2-event-catalog.md) — the M0→M1 catalog plan-of-record.
- [`phase-3-coupling.md`](phase-3-coupling.md) — the M1→M2 coupling plan-of-record (Minkowski hit-probability).
- [`phase-4-damage.md`](phase-4-damage.md) — the M2→M3 severity/damage plan-of-record (curated PV curve).
- [`phase-5-loss-metrics.md`](phase-5-loss-metrics.md) — the M3→M4 loss & metrics plan-of-record (compound-Poisson MC).
