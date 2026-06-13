# M4 — Solar Loss & Metrics (the active plan) · *the finale, on the shared engine*

*Assemble M1's frequency + M3's conditional severity into **annual loss vectors** via the **shared
compound-Poisson Monte-Carlo** (reused from hail), then read **EAL / VaR / PML / TVaR** off the **sampled**
distribution, as **% of TIV**. This is the layer the old repo broke — done right, and verified.*

**Where this sits:** M0 → M1 → M2 → M3 → **M4 (loss & metrics)**. Both solar assets. Notebook:
`Notebooks/wildfire/solar/m4_loss_metrics/01_loss_metrics`.

## Reuse the engine (modular-from-day-one)

The hail M4 compound-MC **aggregation / metrics / Method-0 contrast / %-of-TIV** machinery ports **verbatim**.
Only the **per-year sampling** changes for a site-conditioned, pre-integrated peril:

| | Hail (areal) | **Wildfire (site-conditioned)** |
|---|---|---|
| count/year | `N ~ NegBin(λ_collection, φ)` | **`N ~ Poisson(λ)`** (λ from M1; `fano=1`) |
| thinning | `Bernoulli(p_hit)` per event (Minkowski) | **none** — the occurrence *is* the fire (no spatial factor) |
| severity | bootstrap `(p_hit, conditional_loss)` jointly | **sample a flame class ~ `prob_given_fire`** → its M3 conditional loss |

So: each simulated year, draw `N ~ Poisson(λ)` fires; for each, **sample a flame-length class** from M3's
per-class distribution and add its **full conditional loss**; `AEP_year` = annual total (capped at TIV),
`OEP_year` = largest single fire. **Run in % of TIV** (TIV-free); dollars via TIV (Hayhurst real; Matrix
estimated, AW-20).

## LOTV (basics-spot-on — the whole point of M4)

**Sample** occurrence (Poisson) and **sample** severity (class draw) — **never** `× λ` or `× prob`. The
**Method-0 contrast** (`λ · E[loss|fire]`, a constant every year) is re-demonstrated: it preserves EAL but
collapses the tail — the exact old-repo failure.

## Known-answer checks (before trusting any metric)

- `EAL ≈ λ · E[loss|fire]` = `λ · Σ prob·conditional_loss` (mean preserved). ✓
- `zero-loss-year fraction ≈ exp(−λ)` (every fire yields loss>0 — anchored DR>0 for all classes). ✓
- `AEP ≥ OEP` every year. ✓
- (No NegBin run — `fano=1`; note NegBin is deferred for multi-fire-year clustering / portfolio correlation.)

## Expected (the low-vs-high payoff)

| | Hayhurst (λ≈0.0004/yr) | Matrix (λ≈0.044/yr) |
|---|---|---|
| zero-loss years | ~99.96% | ~95.7% |
| EAL | ~0.0004% TIV (~$140/yr) — negligible | **~0.29% TIV (~$1.1M/yr)** |
| tail (VaR99/PML100) | **≈ 0** (a fire is ~1-in-2700 yr → none in the 1-in-100) | **material** (fire ~1-in-23 yr → the 1-in-100 has one) |

The model behaving: **near-zero for the desert baseline, a real EAL + tail for the sagebrush proving asset.**

## Inputs → outputs

M1 manifest (`λ`) + M3 damage (per-class `prob_given_fire`, `cond_loss_pct_tiv`, `cond_loss_usd`) + TIV →
`data/wildfire/<asset>_wildfire_m4_annual_vectors.parquet` (AEP/OEP per sim-year) +
`…_m4_metrics.json` (EAL/VaR/PML/TVaR in $ and % of TIV), both assets.

## Assumptions / decisions

Reuse engine (modular — engine unchanged) · `frequency = Poisson(λ)`, fano=1 ([DD-W7](decisions.md)) ·
gross physical only (no deductibles/limits/BI — deferred) · MC = 300k sim-years, current-climate ·
% of TIV alongside $ ([AW-20](assumptions.md); Matrix TIV estimated).

## Caveats (honest)

- **Approximate, not record-limited.** Unlike hail (short MRMS record), λ comes from FSim's pre-integrated BP
  — so the *frequency* isn't record-limited. The limits are: the **approximate, anchored curve** (DD-W8), the
  **6-class discrete severity** (coarse deep tail — EVT/continuous deferred, AW-24), `d=10 m` embedded, and
  **single-site** (no portfolio correlation).
- Metrics are **real but approximate** (curve-limited) — don't quote as final.

## Next

**M0→M4 wildfire × solar complete** → the **wind cell** (`wildfire/wind/` M2–M4 on the shared M0/M1 — per-
turbine, hub-height attenuation, the 3 wind curves), then the cross-peril close-out.
