# M3 — Severity / Damage (M2 → M3)

*Given an event reaches the asset, **how bad is it?** The layer that turns a hail size into a damage ratio
and a conditional dollar loss.*

**Where this sits:** [M0 evidence](../../m0_input_data/) → [M1 catalog](../../m1_catalog/) →
[M2 coupling](../m2_coupling/) → **M3 (severity / damage)** → Phase 5 loss & metrics.

## The plain-English question

M2 said *whether* each event hits (the probability `pᵢ`). M3 says *how much it costs if it does*: run each
event's hail size through a **damage curve** to get a damage ratio, then × the asset value → the conditional
dollar loss.

## What we did

Built a **capex-weighted subsystem** `hail size → damage ratio` curve and applied it to each event. Output:
a per-event **damage ratio** + **conditional loss** (the *full* loss if the event hits — the asset DR
**caps at ≈34%** of value, ≈$12.6M, reached by the biggest event: **118.5 mm / 4.67″** hail). Severity is
steeply size-driven, so a few giant-hail events carry most of the potential loss.

## Why this way (two rules that define the stage)

1. **Curve-driven, not fitted.** We have hail *sizes*, not a history of what hail cost this plant — so we
   don't fit losses. We take a **capex-weighted subsystem blend** from
   [`infrasure-damage-curves`](../../../../infrasure-damage-curves) (PV-module + tracker fragility × NREL
   capex weights) and apply it. **Its provenance is the deliverable, not a fit statistic** — change the
   curve, change the losses.
2. **Conditional, full, and `pᵢ`-free.** This is the loss *if it hits* — the **full** conditional loss. We
   **never** multiply by `pᵢ` here. Frequency (`pᵢ`) and severity (conditional loss) stay separate until the
   Phase-5 Monte Carlo combines them — multiplying them is the Method-0 shortcut that breaks the tail.

## The curve (v1)

**Capex-weighted subsystem blend** (`hail_solar_asset_capex_weighted.json`): only the hail-exposed
subsystems carry a fragility curve — **PV module** (`L=0.95`) and **tracker / mounting** (`L=0.40`), each a
logistic in hail size — and the asset damage ratio is the capex-weighted sum **`Asset_DR = Σ wᵢ·DRᵢ`**
(PV array `w≈0.32`, mounting `w≈0.10`). The remaining ~64% of asset value (inverters, substation,
electrical, civil, SCADA) is effectively **hail-immune → 0**, so the asset DR **saturates at ≈34%** — no
>100% extrapolation (the failure mode of the old literature curve this replaced).

## Inputs → outputs

[M2 coupled events](../m2_coupling/) (hail size + `pᵢ`) + `asset_value` ($36.78M) →
`data/hail/hayhurst_hail_m3_damage.parquet` (event + `damage_ratio` + `conditional_loss_usd` + carried
`pᵢ`) + `…_m3_summary.json`.

## Deferred (stated, not hidden)

- **Conditional damage *distribution*** (vs the scalar mean) — the tail-relevant richness; Phase 5 needs a
  severity *spread* to sample (A22).
- **Duration / business interruption** — v1 folds repair downtime into the damage ratio, revenue loss aside.
- **Curve calibration to PV claims** + better subsystem weights / a conditional-DR distribution — the
  `infrasure-damage-curves` revamp (this blend is a sound but *temporary* asset-level v1).

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_damage`](01_damage.ipynb) | capex-weighted subsystem curve → per-event damage ratio + conditional loss; carries `pᵢ` | the damage parquet + summary |

## Key

Plan: [phase-4-damage](../../../../docs/plans/hail/phase-4-damage.md). Matches methodology §6 (curate, don't
fit) + §12 (the hail-on-solar curve).

## Assumptions (this layer)

A15 **capex-weighted subsystem blend** (PV_MODULE `L=0.95` + TRACKER `L=0.40` × NREL capex weights →
`Asset_DR=Σwᵢ·DRᵢ`, caps ~34%) · A16 logistic **saturates** (no extrapolation; replaces the old literature
curve that ran to ~100%) · A17 scalar mean damage *(no conditional distribution — tail-relevant, deferred)*
· A18 duration/BI folded into the ratio · A19 asset value = $36.78M. Full detail + status:
[assumptions register A15–A19](../../../../docs/plans/hail/assumptions.md#m3--severity--damage).

**Next → Phase 5 (loss & metrics):** the compound-Poisson Monte Carlo — `Bernoulli(pᵢ)` + full conditional
loss → annual AEP/OEP vectors → EAL / VaR / PML / TVaR. The part the old repo broke.
