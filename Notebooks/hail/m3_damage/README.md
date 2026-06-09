# M3 — Severity / Damage (M2 → M3)

*Given an event reaches the asset, **how bad is it?** The layer that turns a hail size into a damage ratio
and a conditional dollar loss.*

**Where this sits:** [M0 evidence](../m0_input_data/) → [M1 catalog](../m1_catalog/) →
[M2 coupling](../m2_coupling/) → **M3 (severity / damage)** → Phase 5 loss & metrics.

## The plain-English question

M2 said *whether* each event hits (the probability `pᵢ`). M3 says *how much it costs if it does*: run each
event's hail size through a **damage curve** to get a damage ratio, then × the asset value → the conditional
dollar loss.

## What we did

Built a **curated** `hail size → damage ratio` curve and applied it to each event. Output: a per-event
**damage ratio** + **conditional loss** (the *full* loss if the event hits — biggest event ≈ 67% of value,
the 3.76″ hail day). Severity is steeply size-driven, so a few giant-hail events carry most of the potential
loss.

## Why this way (two rules that define the stage)

1. **Curated, not fitted.** We have hail *sizes*, not a history of what hail cost this plant — so we don't
   fit losses. We curate a curve from literature (panel hail-rating standards + post-event studies; anchors
   from methodology §12) and apply it. **Its provenance is the deliverable, not a fit statistic** — change
   the curve, change the losses.
2. **Conditional, full, and `pᵢ`-free.** This is the loss *if it hits* — the **full** conditional loss. We
   **never** multiply by `pᵢ` here. Frequency (`pᵢ`) and severity (conditional loss) stay separate until the
   Phase-5 Monte Carlo combines them — multiplying them is the Method-0 shortcut that breaks the tail.

## The curve (v1)

Anchors (mm → mean damage %): **(25.4→0), 27→1.2, 40→4.5, 60→20, 75→40**; 0 below the 25.4 mm severe
threshold; linear between; **extrapolated above 75 mm** (flagged — our 95.5 mm top event sits there).

## Inputs → outputs

[M2 coupled events](../m2_coupling/) (hail size + `pᵢ`) + `asset_value` ($36.78M) →
`data/hail/hayhurst_hail_m3_damage.parquet` (event + `damage_ratio` + `conditional_loss_usd` + carried
`pᵢ`) + `…_m3_summary.json`.

## Deferred (stated, not hidden)

- **Conditional damage *distribution*** (vs the scalar mean) — the tail-relevant richness; Phase 5 needs a
  severity *spread* to sample (A22).
- **Duration / business interruption** — v1 folds repair downtime into the damage ratio, revenue loss aside.
- **Curve calibration to PV claims / the >75 mm extrapolation** — literature-curated for now.

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_damage`](01_damage.ipynb) | curated curve → per-event damage ratio + conditional loss; carries `pᵢ` | the damage parquet + summary |

## Key

Plan: [phase-4-damage](../../../docs/plans/hail/phase-4-damage.md). Matches methodology §6 (curate, don't
fit) + §12 (the hail-on-solar curve).

## Assumptions (this layer)

A15 curated damage-curve anchors (mm→%: 25.4→0, 27→1.2, 40→4.5, 60→20, 75→40) · A16 >75 mm = extrapolation
(capped) · A17 scalar mean damage *(no conditional distribution — tail-relevant, deferred)* · A18 duration/BI
folded into the ratio · A19 asset value = $36.78M. Full detail + status:
[assumptions register A15–A19](../../../docs/plans/hail/assumptions.md#m3--severity--damage).

**Next → Phase 5 (loss & metrics):** the compound-Poisson Monte Carlo — `Bernoulli(pᵢ)` + full conditional
loss → annual AEP/OEP vectors → EAL / VaR / PML / TVaR. The part the old repo broke.
