# M4 — Solar Loss & Metrics · completion record

**Status:** ✅ built · 2026-06-13 · **Plan:** [`../m4_loss_metrics.md`](../m4_loss_metrics.md) · **Notebook:**
`Notebooks/wildfire/solar/m4_loss_metrics/01_loss_metrics`

## Objective

Assemble M1's **frequency** (λ) + M3's **conditional severity** (per-class loss|fire) into **annual loss
vectors** via the **shared compound-Poisson Monte-Carlo** (reused from hail), then read **EAL / VaR / PML /
TVaR** off the **sampled** distribution, as **% of TIV** (and $). *The layer the old repo broke — done right.*

## What shipped (both assets)

- **Engine reused verbatim** (modular-from-day-one): the hail M4 aggregation / metrics / Method-0 contrast /
  %-of-TIV machinery ported **unchanged**. Only the **per-year sampling** swapped for a site-conditioned,
  pre-integrated peril: `N ~ Poisson(λ)` fires/yr (λ from M1, `fano=1` — *no* p_hit thinning, *no*
  `λ_collection × p`), each fire **samples a flame class** from M3's `prob_given_fire` → its **full conditional
  loss**. `AEP` = annual total (capped at TIV), `OEP` = max single fire.
- **N = 300,000 sim-years**, seed `20260613`. `prob` renormalized before `rng.choice`.
- **LOTV kept clean:** *sampled* occurrence × *sampled* severity — **never** `×λ` or `×prob`. The **Method-0
  contrast** (`λ·E[loss|fire]`, a constant every year) re-demonstrated: preserves EAL, **collapses the tail** —
  the exact old-repo failure, shown side-by-side.
- Persists `data/wildfire/<asset>_wildfire_m4_annual_vectors.parquet` (AEP/OEP per sim-year) +
  `…_m4_metrics.json` ($ and % of TIV), both assets.

## Key results (the low-vs-high payoff)

| metric (% of TIV) | Hayhurst (baseline, low-fire) | Matrix (proving, high-fire) |
|---|---|---|
| λ /yr | 0.00037 (~1-in-2,700) | 0.044 (~1-in-23) |
| zero-loss years | **99.96%** | 95.65% |
| **EAL** | **0.0004% (~$151/yr)** — negligible | **0.2896% (~$1.12M/yr)** |
| VaR99 (PML100) | 0% (no fire in the 1-in-100) | **4.75% (~$18.3M)** |
| PML250 | 0% | **14.01% (~$54.0M)** |
| TVaR99 | 0.0004% | 9.44% |
| OEP-PML100 | 0% | 4.75% (≈ AEP — sparse single-site) |

The model behaving exactly right across a ~120× λ contrast: **near-zero for the desert baseline, a real EAL +
material tail for the sagebrush proving asset** — on **one unchanged engine**. (Matrix TIV estimated via
$/kWp — AW-20; Hayhurst TIV real.)

## Verification

Known-answer checks pass: `EAL ≈ λ·E[loss|fire]` (statistical tolerance `max(0.04·analytic, 4·SE)` — a fixed
relative bound is too tight for rare events where MC EAL is noisy; see Note) ✓ · `zero-loss ≈ exp(−λ)`
(<0.005) ✓ · `AEP ≥ OEP` every year ✓. Matrix EAL hand-check: `0.044 × 6.5% = 0.29% TIV` ✓.

## Note — rare-event EAL is MC-noisy (transferable)

For a low-λ peril (Hayhurst: ~111 fires across 300k sim-years), the MC **EAL itself** carries real sampling
noise, so a *fixed* relative tolerance (`rel < 0.04`) spuriously fails. The fix is a **statistical** tolerance,
`|MC − analytic| ≤ max(0.04·analytic, 4·SE)` with `SE = AEP.std()/√N` — this will recur for any rare hazard
(and is the same reason the *tail*, not the mean, is where rare-peril estimates are fragile).

## Decisions / assumptions

[DD-W7](../decisions.md) (`frequency = Poisson(λ)`, fano=1) · engine reused unchanged (modular principle) ·
gross physical only (no deductibles/limits/BI — deferred) · [AW-20](../assumptions.md) (Matrix TIV estimated,
% of TIV alongside $).

## Caveats (honest)

**Real but approximate — and *not* record-limited.** Unlike hail (short MRMS record), λ comes from FSim's
pre-integrated BP, so *frequency* isn't record-limited. The limits are downstream: the **approximate anchored
curve** (DD-W8), **6-class discrete severity** (coarse deep tail — EVT/continuous deferred, AW-24), `d=10 m`
embedded, and **single-site** (no portfolio correlation / multi-fire-year clustering — NegBin deferred). Don't
quote the metrics as final.

## Next

**M0→M4 wildfire × solar complete.** → the **wind cell** (`Notebooks/wildfire/wind/` M2–M4 on the shared
M0/M1 — per-turbine point-cloud, hub-height attenuation, the 3 wind curves), then the cross-peril close-out.
