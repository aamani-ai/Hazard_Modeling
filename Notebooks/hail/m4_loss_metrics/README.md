# M4 — Loss & Metrics (M3 → M4)

*The finale: turn per-event (probability, cost) into **annual loss vectors**, then read the risk metrics —
EAL, VaR, PML, TVaR. **The part the old repo actually broke.***

**Where this sits:** [M0 evidence](../m0_input_data/) → [M1 catalog](../m1_catalog/) →
[M2 coupling](../m2_coupling/) → [M3 damage](../m3_damage/) → **M4 (loss & metrics)**.

## The plain-English question

M3 gave us, per event, *how likely it hits* (`pᵢ`) and *what it costs if it does* (`conditional_loss`). M4
asks: **across many simulated years, what does the loss actually look like — and what are the headline risk
numbers?**

## What we did

A **compound-Poisson Monte Carlo**: simulate 300k years; each year, draw a Poisson count of regional events,
flip a `Bernoulli(pᵢ)` coin per event, and on a **hit** add the **full** conditional loss. That builds the
annual loss distribution (a spike at $0 + a heavy tail), off which we read **EAL, VaR₉₅/₉₉/₉₉.₆, TVaR₉₉,
AEP-PML, OEP-PML**.

## Why this way — the rule the old repo broke

- ✅ **Stochastic hit + full loss** (`Bernoulli(pᵢ)` then full `conditional_loss`) — **never** `pᵢ × loss`.
  The Method-0 shortcut (summing expected contributions) preserves EAL but **collapses the variance** → the
  tail (VaR/PML) is wrong. We *demonstrate* this with a Method-0 contrast in the notebook.
- ✅ **Cap per simulated year**, not on a fitted curve (capping a fitted curve at asset value is what made the
  old repo's VaR collapse onto the asset value).
- ✅ **Verified** with known-answer checks (`EAL ≈ λ·mean(p·loss)`; zero-loss years `≈ exp(−λ_asset)`).

## ⚠️ The metrics are *illustrative*

The MC needs a `λ`, and we have **no fitted one** (DD-2 — record too short). So we run an **illustrative**
`λ_collection ≈ 20/yr` (placeholder) + a sensitivity sweep. **The dollar metrics demonstrate the pipeline;
they are NOT Hayhurst's real risk numbers** — those follow the widened record + the NegBin fit.

## Inputs → outputs

[M3 damage](../m3_damage/) (`pᵢ` + `conditional_loss`) + asset value + illustrative `λ` →
`data/hail/hayhurst_hail_m4_annual_vectors.parquet` (AEP/OEP per simulated year) + `…_m4_metrics.json`.

## Assumptions (this layer)

A20 illustrative `λ` *(placeholder + sweep)* · A21 gross *physical* loss only (no deductibles/limits/BI) ·
A22 MC = 300k years, cap-per-year, empirical percentiles. Full register:
[assumptions A20–A22](../../../docs/plans/hail/assumptions.md#m4--loss--metrics).

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_loss_metrics`](01_loss_metrics.ipynb) | compound-Poisson MC → annual AEP/OEP → EAL/VaR/PML/TVaR; Method-0 contrast; λ sweep | the annual-vectors parquet + metrics JSON |

## Key

Plan: [phase-5-loss-metrics](../../../docs/plans/hail/phase-5-loss-metrics.md). Matches methodology §8
(MC engine) / §10 (tail). **This closes the M0→M4 hail skeleton.**

**Production path from here:** widen the MRMS record (→ real λ + NegBin fit) · calibrate the damage curve to
PV claims · add financial terms (deductibles/limits/BI) + an EVT-GPD tail.
