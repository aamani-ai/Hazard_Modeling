# M4 — Solar Loss & Metrics (the finale, on the shared engine)

*Assemble M1's frequency + M3's conditional severity into **annual loss vectors** via the **shared
compound-Poisson Monte-Carlo** (reused from hail), then read **EAL / VaR / PML / TVaR** off the **sampled**
distribution, as **% of TIV**. The layer the old repo broke — done right, verified.*

**Where this sits:** M0 → M1 → M2 → M3 → **M4 (loss & metrics)**. Both solar assets. Plan:
[`docs/plans/wildfire/m4_loss_metrics.md`](../../../../docs/plans/wildfire/m4_loss_metrics.md).

## Engine reuse + wildfire wiring

The hail M4 aggregation/metrics/Method-0/%-of-TIV port **verbatim** (modular-from-day-one). Only the per-year
sampling changes: **`N ~ Poisson(λ)`** fires/yr (λ from M1, site-conditioned — *no* p_hit thinning, *no*
λ_collection×p), each fire **samples a flame class** from M3's `prob_given_fire` → its **full conditional
loss**; `fano=1`. `AEP` = annual total (cap TIV), `OEP` = max single fire. Run in **% of TIV**; $ via TIV.

- **LOTV:** sample occurrence + sample severity — **never** `×λ` or `×prob`. Method-0 contrast re-demonstrated.
- **Known-answer:** `EAL ≈ λ·E[loss|fire]` · `zero-loss ≈ exp(−λ)` · `AEP ≥ OEP`.

## Inputs → outputs

M1 manifest (λ) + M3 damage (per-class prob + conditional loss) + TIV →
`data/wildfire/<asset>_wildfire_m4_annual_vectors.parquet` + `…_m4_metrics.json` ($ and % of TIV), both assets.

**Caveat:** *approximate* (DD-W8 anchored curve; 6-class discrete severity, coarse deep tail — AW-24;
single-site) — **not** record-limited (λ is FSim-pre-integrated). Real but approximate; don't quote as final.

**Next:** M0→M4 wildfire × solar complete → the **wind cell** + cross-peril close-out.
