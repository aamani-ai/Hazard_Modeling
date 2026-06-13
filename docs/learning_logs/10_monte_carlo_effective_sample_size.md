# A Monte Carlo metric is only as precise as its *effective* sample — and a known-answer tolerance must track that, not a fixed band

*300,000 simulated years did not make the rare-peril EAL precise — it rested on ~111 events — so a fixed 4% validation band failed on correct code; the fix is a tolerance set from the run's own standard error.*

**Status:** v1.0 · written 2026-06-13 · **Sourced from:** wildfire × solar · M4 loss & metrics (`Notebooks/wildfire/solar/m4_loss_metrics/01_loss_metrics`) · **Applies to:** every peril that reads metrics off a Monte Carlo — acutely rare perils (low λ) and deep-tail PMLs

---

## Where this came from

M4 runs the shared compound-Poisson MC for `M = 300,000` simulated years and checks the wiring with a known-answer assertion: the simulated EAL must match the analytic `EAL = λ·E[loss|fire]` (exact, by the law of total expectation). The first version used a **fixed relative band**, `|EAL_mc − EAL_analytic| ≤ 0.04·EAL_analytic`.

It **failed for Hayhurst** (the low-fire baseline, λ ≈ 0.00037) and **passed for Matrix** (the high-fire asset, λ ≈ 0.044) — same engine, same code, same `M`. Nothing was wrong with the engine. Measuring the actual noise settled it:

```text
                   Hayhurst        Matrix
expected events λM   ~111           ~13,200      <- the EFFECTIVE sample
fire-years seen       114            13,047
relative SE of EAL   18.3%           1.4%         <- the EAL's own noise
4·SE band applied    73%             5.5%
fixed 4% band         FAILS          ~passes
```

## Why it looked fine — the trap

`M = 300,000` *looks* like an enormous sample, so demanding the mean match to 4% feels not just safe but generous. The hidden flaw: for a rare peril **almost every simulated year contributes a zero** to the EAL. The mean is pinned by the handful of years that actually had a fire — ~111 for Hayhurst, not 300,000. The estimate's precision is governed by that **effective** sample, and `1/√111 ≈ 9.5%` before you even account for severity spread. A 4% band was asking for a precision the run could never have — so it was doomed to trip on perfectly correct code, which reads as "a bug" and tempts you to either chase a phantom or loosen the band blindly (and mask a *real* bug next time).

## The lesson

> **A Monte Carlo metric is only as precise as its *effective* sample — `λ·M` events for the mean, `M·(1−α)` years for a quantile — so quote it with a standard error, and set any known-answer tolerance from that error, never from an arbitrary fixed band.**

The mechanics, with the numbers that sharpen them:

- **The mean has its own sampling error.** `[REF —` `SE = s/√M` is textbook for any sample mean.`]` For the compound-Poisson EAL it has a clean closed form: `relative SE = √(1+CV²) / √(λM)`, where `CV` is the coefficient of variation of the per-event loss and `λM` is the expected event count. `[OURS —` the build made vivid that this bites the **EAL itself**, not only the tail: at `λM ≈ 111` the EAL carried ~18% relative noise.`]`
- **Effective sample size is one principle, two faces.** `[REF —` note 04's "How Many Simulated Years?" already gives `tail_count = M·(1−α)` for quantiles.`]` `[OURS —` the EAL's `λM` is the *same* idea for the mean; naming them together is the unlock. The nominal `M` is a mirage; what governs precision is the count of *informative* draws.`]`
- **The fix is a self-calibrating tolerance.** `tolerance = max(rel_floor·analytic, k·SE)` with `k = 4`. `[OURS —` the `k·SE` term means a correct run strays past it only ~1-in-16,000 times (~4σ), while a genuine wiring bug is off by orders of magnitude and still trips loudly; the `rel_floor` keeps a 4% floor so a small *bias* still trips when events are common and SE is tiny.`]` It auto-tightens when precise (Matrix 5.5%) and auto-loosens when genuinely noisy (Hayhurst 73%).

The scaling even checks out across the two assets: predicted ratio of relative SEs `√(13200/111) ≈ 10.9` vs observed `18.3%/1.4% ≈ 13` — the `1/√(effective N)` law, confirmed on our own run.

## How to recognize it next time

- **Low λ or a deep return period** → suspect the metric is thinly sampled *before* trusting it. Compute `λM` (for the EAL) or `M·(1−α)` (for a PML); if it's in the dozens, the estimate is noisy no matter how big `M` looks.
- **A known-answer check fails by "a bit" (10–30%), not by orders of magnitude** → it's almost certainly sampling noise meeting a too-tight tolerance, not a bug. A real wiring error misses by ×10 or more. Set the band to `max(rel, 4·SE)` and re-judge.
- **A tail metric jumps when you change the seed** → the effective tail sample is too thin; simulate more years, use variance reduction, or extrapolate (EVT — but check it's defensible *there*; see below).

## Caveats and limits

- **`s/√M` is the SE of a *mean*.** A quantile's (VaR/PML) standard error is **not** `s/√M` — use a bootstrap or order-statistic interval. Tail quantiles are far noisier than the EAL.
- **Effective N can be *smaller* than `λM`.** Clustering (NegBin / regime years) packs events into fewer independent blocks, so the real degrees of freedom are fewer than the raw event count.
- **Noise ≠ "wrong," precision ≠ "right."** Hayhurst's noisy EAL is `$151/yr` — economically negligible, so the noise changes no decision; we did *not* burn ~4M years chasing 5% precision on a number that rounds to nothing. Match the precision you demand to the decision at stake.
- **This is about sampling error, not model error.** A tight SE on a metric built from a wrong λ, curve, or correlation is precisely-estimated nonsense (04's "100,000 years of false confidence"). The standard error tells you how stable the number is, never whether the inputs are true.
- **It does *not by itself* argue for EVT.** EVT addresses a *structural* tail (extrapolating beyond the sim, or a genuinely heavy `ξ>0` tail) — a different problem from sampling noise. Effective-sample thinking tells you *where* MC runs out of resolution; whether to extrapolate there is note 05's question, and for a bounded single-site severity the answer is usually "more years / continuous severity," with EVT earning its keep mainly at portfolio scale.

## Cross-references

- **Concept note (the math, peril-agnostic):** [`hazard_math/06_monte_carlo_error_effective_sample_size.md`](../../Learning/ML-DL/InfraSure_related/hazard_math/06_monte_carlo_error_effective_sample_size.md) — the precision law, how to invert it for `M`, the tolerance recipe, convergence checks. Built from this moment; this log is the war story behind it.
- **The engine it measures:** [`hazard_math/04_monte_carlo_annual_loss_simulation.md`](../../Learning/ML-DL/InfraSure_related/hazard_math/04_monte_carlo_annual_loss_simulation.md) ("How Many Simulated Years?" + "Convergence Checks").
- **The tail tool it points at:** [`hazard_math/05_extreme_value_theory_tail_modeling.md`](../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md).
- **Generalizes:** [DD-W7](../plans/wildfire/decisions.md) (Poisson(λ), fano=1) and the M4 plan/record ([`m4_loss_metrics.md`](../plans/wildfire/m4_loss_metrics.md) · [`done/m4-loss-metrics.md`](../plans/wildfire/done/m4-loss-metrics.md)).
- **Serves the principle:** *basics spot-on* — a verification check is only meaningful if its tolerance matches the estimator's real precision.
