# Phase 5 — Loss & Metrics (M3 → M4)

> **Status:** building (2026-06-09). Basis: A24, methodology §8 (event-loss generation) / §9 (financial) /
> §10 (EVT), risk-metrics reference. **This is the part the old repo actually broke** — so it gets a Method-0
> contrast and known-answer checks.

The finale: turn the per-event `(pᵢ, conditional_loss)` from M3 into **annual loss vectors**, then read the
risk metrics off them. Completes the end-to-end M0→M4 hail skeleton.

## The engine — compound-Poisson Monte Carlo (event-level thinning)

```
for each of N simulated years:
    n_coll ~ Poisson(λ_collection)            # regional events this year
    year_loss = 0 ; year_max = 0
    for each of the n_coll events:
        draw (pᵢ, conditional_lossᵢ) from the catalog   # bootstrap — keeps footprint↔intensity↔p correlated
        if uniform() < pᵢ:                    # Bernoulli HIT
            year_loss += conditional_lossᵢ    # the FULL loss — never pᵢ × loss
            year_max  = max(year_max, conditional_lossᵢ)
    AEP_year = min(year_loss, asset_value)    # cap PER SIMULATED YEAR (not on a fitted curve)
    OEP_year = year_max
```

**Two rules this encodes (the repo's bugs, fixed):**
1. **Stochastic hit, full loss — never the expected contribution.** `Bernoulli(pᵢ)` + full `conditional_loss`,
   not `pᵢ × loss`. Summing expected losses (Method-0) preserves EAL but collapses the variance → kills
   VaR/PML. *The single most important build rule* (methodology §5/§8).
2. **Cap per simulated year, not on a fitted aggregate curve.** Capping a fitted curve at asset value is what
   made the old repo's VaR collapse onto the asset value.

## Illustrative λ (the one assumption we must state loudly)

> **✅ Superseded (DD-3 Stage 1).** `λ` is now **fitted** on the widened ~5.65-yr MRMS record —
> `λ_collection = 29.6/yr`, NegBin `φ = 3.37` (→ register A20; small-n caveat A24). The illustrative-λ plan
> below was the v1 placeholder *before* the record was widened; it's kept here for planning history. The
> headline metrics are now **real (record-limited)**, not illustrative.

The MC needs a `λ`. We have no fitted one (DD-2 — record too short). So we use an **illustrative**
`λ_collection ≈ 20/yr` (rough peak-season annualization — *placeholder, not a fit*) and a **sensitivity sweep**
(`{10, 20, 40}`). **The resulting dollar metrics demonstrate the pipeline; they are NOT Hayhurst's real risk
numbers** — those follow the widened record + the NegBin fit. → register A20.

## Verification (because this is the broken-before step)

- **Known-answer checks:** `EAL_MC ≈ λ_collection · mean(pᵢ·lossᵢ)` (analytic mean); zero-loss-year fraction
  `≈ exp(−λ_asset)` where `λ_asset = λ_collection · mean(pᵢ)`.
- **Method-0 contrast:** show the shortcut preserves EAL but its "VaR₉₉" collapses to ≈ EAL — far below the
  true MC VaR₉₉ — because it discards the hit-or-miss variance the tail is made of.

## Inputs → outputs

[M3 damage](../../Notebooks/hail/m3_damage/) (`pᵢ`, `conditional_loss_usd` per event) + `asset_value` +
the **fitted** `λ` (A20) → `data/hail/hayhurst_hail_m4_annual_vectors.parquet` (AEP/OEP per simulated year) +
`…_m4_metrics.json` (EAL, VaR₉₅/₉₉/₉₉.₆, TVaR₉₉, AEP-PML₁₀₀/₂₅₀, OEP-PML₁₀₀, zero-loss fraction, Poisson-vs-NegBin contrast).

## Deferred / out of scope

- ~~**Real `λ`** (the fit) — widen the record (DD-2).~~ **✅ Done (DD-3 Stage 1):** record widened, `λ` fitted (29.6/yr, NegBin φ=3.37, A20) — headline metrics are now real (record-limited).
- **Financial terms** (deductibles, limits, BI) — v1 reports **gross physical loss** only (methodology §9). → A21.
- **Conditional severity *distribution*** — we bootstrap the scalar per-event losses (some spread across the
  11 events), not a within-size damage distribution (A17); the richer severity model is the tail upgrade.
- **EVT-GPD tail** — we read empirical percentiles; an EVT tail (methodology §10) is the refinement once the
  record/sim supports it.

**This closes the M0→M4 hail skeleton.** Production path from here: widen the MRMS record (→ real λ + NegBin
fit), calibrate the damage curve to PV claims, add financial terms + EVT tail.
