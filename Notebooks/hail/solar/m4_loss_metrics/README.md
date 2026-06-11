# M4 — Loss & Metrics (M3 → M4)

*The finale: turn per-event (probability, cost) into **annual loss vectors**, then read the risk metrics —
EAL, VaR, PML, TVaR. **The part the old repo actually broke.***

**Where this sits:** [M0 evidence](../../m0_input_data/) → [M1 catalog](../../m1_catalog/) →
[M2 coupling](../m2_coupling/) → [M3 damage](../m3_damage/) → **M4 (loss & metrics)**.

## The plain-English question

M3 gave us, per event, *how likely it hits* (`pᵢ`) and *what it costs if it does* (`conditional_loss`). M4
asks: **across many simulated years, what does the loss actually look like — and what are the headline risk
numbers?**

## What we did

A **compound-Poisson Monte Carlo** with fitted **Negative Binomial** event counts: simulate 300k years; each
year, draw a regional event count, flip a `Bernoulli(pᵢ)` weighted coin per event, and on a **hit** add the
**full** conditional loss. That builds the annual loss distribution (a spike at $0 + a heavy tail), off which
we read **EAL, VaR₉₅/₉₉/₉₉.₆, TVaR₉₉, AEP-PML, OEP-PML**.

## The subtle point — two draws, two questions

The simulation uses two random draws because they answer two different questions:

```text
1. Frequency draw:
   How many severe hail events happen somewhere in the region this year?
   N_year ~ NegBin(lambda_collection)

2. Hit/miss draw:
   For each regional event, does this one reach Hayhurst?
   hit_i ~ Bernoulli(p_i)   # a weighted coin, not a 50/50 coin

If miss -> $0
If hit  -> full conditional_loss_i from M3
```

So `pᵢ` is the event's **weighted-coin probability of hitting the asset**. It is not multiplied into the
loss before simulation.

Example:

```text
Simulated year 42:

regional events drawn: 3

event A: p_hit 2%, loss if hit $5M
  weighted coin -> miss
  loss = $0

event B: p_hit 1%, loss if hit $12M
  weighted coin -> hit
  loss = $12M

event C: p_hit 4%, loss if hit $3M
  weighted coin -> miss
  loss = $0

AEP_year = $12M   # annual total loss
OEP_year = $12M   # biggest single-event loss
```

Future EVT / magnitude fitting does **not** require a different MC *engine* — the same NegBin-counts ×
per-event-thinning × full-loss-on-hit loop runs unchanged; only the *upstream severity input* (and possibly
`p_hit`) changes:

```text
current v1:
  bootstrap observed event -> use its p_hit + conditional_loss

future EVT / magnitude version:
  sample event magnitude, e.g. hail size from an EVT-GPD tail
  -> convert sampled size through the damage model
  -> get conditional_loss
  -> still use weighted hit/miss with p_hit
  -> if hit, apply the full sampled loss
```

The caveats matter:

- The sampled size **and its `p_hit` must be drawn jointly.** v1 gets the size↔footprint↔`p_hit` correlation
  for free by bootstrapping *whole observed events*; an EVT version that samples size *independently* breaks
  that coupling → it would need a **severity-dependent `p_hit` / M2-coupling model** if size and footprint
  correlate in the tail (A11–A13 currently assume independence). That's an extra *upstream* model — still not
  a different MC engine.
- A conditional damage distribution would replace the current scalar mean curve, because same-size hail events
  can produce different damage.
- EVT only helps the deep tail if the tail fit is credible; otherwise it can add false precision.
- Financial terms (deductibles, limits, BI) are a separate layer after gross physical loss.

## Why this way — the rule the old repo broke

- ✅ **Stochastic hit + full loss** (`Bernoulli(pᵢ)` then full `conditional_loss`) — **never** `pᵢ × loss`.
  The Method-0 shortcut (summing expected contributions) preserves EAL but **collapses the variance** → the
  tail (VaR/PML) is wrong. We *demonstrate* this with a Method-0 contrast in the notebook.
- ✅ **Cap per simulated year**, not on a fitted curve (capping a fitted curve at asset value is what made the
  old repo's VaR collapse onto the asset value).
- ✅ **Verified** with known-answer checks: `EAL ≈ λ·mean(p·loss)` (both count models); zero-loss years
  `≈ exp(−λ_asset)` **for the Poisson run** — the headline NegBin sits *higher* (clustering piles more mass at $0).

## ⚠️ The metrics are real, but record-limited

`λ_collection` is now fitted on the widened ~5.65-year MRMS record, with over-dispersed annual counts handled
by the Negative Binomial model — so these are **no longer placeholder numbers**. Two *distinct* limits remain,
and they bind in different places:

- **Frequency (the body):** only ~5.65 yr / 5 full years → λ and the dispersion φ are real but noisy (A24); the
  distribution *body* (EAL, ~PML₁₀₀) is trustworthy.
- **Severity (the deep tail):** losses are bootstrapped from the 158 observed events and the curve caps at
  ~34%, so the MC **cannot exceed the largest observed loss** → the deep tail (1-in-250+, OEP-PML) is
  **biased low** (A23). An EVT-GPD severity tail is the fix.

So: **trust the body; treat the deep tail as a floor, not the answer.**

## Inputs → outputs

[M3 damage](../m3_damage/) (`pᵢ` + `conditional_loss`) + asset value + fitted `λ` →
`data/hail/hayhurst_hail_m4_annual_vectors.parquet` (AEP/OEP per simulated year) + `…_m4_metrics.json`.

## Assumptions (this layer)

A20 fitted `λ_collection` = 29.6/yr with NegBin Fano φ = 3.37 (a noisy small-n estimate — A24) · A21 gross
*physical* loss only (no deductibles/limits/BI) · A22 MC = 300k years, cap-per-year (on AEP), empirical
percentiles · A23 deep-tail bootstrap truncation. (The asset value / TIV = $36.78M is **A19**, imported from
M3 — it scales every $ metric.) Full register:
[assumptions A20–A23](../../../../docs/plans/hail/assumptions.md#m4--loss--metrics).

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_loss_metrics`](01_loss_metrics.ipynb) | compound-Poisson MC → annual AEP/OEP → EAL/VaR/PML/TVaR; Method-0 contrast; Poisson-vs-NegBin check | the annual-vectors parquet + metrics JSON |

## Key

Plan: [phase-5-loss-metrics](../../../../docs/plans/hail/done/phase-5-loss-metrics.md). Matches methodology §8
(MC engine) / §10 (tail). **This closes the M0→M4 hail skeleton.**

**Production path from here:** NOAA-calibrated `λ` extension · calibrate the damage curve to PV claims · add
financial terms (deductibles/limits/BI) + an EVT-GPD tail.
