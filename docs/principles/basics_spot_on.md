# Basics Spot-On — The Math Is the Product

*Why the foundational math has to be exactly right before anything is built on it — and why this is the
principle the old model's collapse made impossible to ignore.*

If there is one principle that subsumes the others, it is this one. A hazard model's output is a number that
someone prices, underwrites, or sizes debt against. If the basic math producing that number is wrong, every
feature on top of it inherits the wrongness — and inherits it *invisibly*, because a plausible wrong number
looks exactly like a right one.

---

## Why this document exists

The old model did not fail from missing features. It failed because the **basics were not spot-on** — and
the failure was specific, diagnosable, and avoidable. This is the antidote, written so we never re-pay the
price. The owner's pre-existing work — the [`hazard_math/`](../../Learning/ML-DL/InfraSure_related/hazard_math)
notes and the Drive reference set (terminology, risk metrics, methodology) — exists *because of* this
principle: get the foundation provably right first.

---

## The real incident: VaR/PML on the wrong random variable

The old model stored each event's loss as `damage% × asset_value × spatial_factor`. That product is the
**expected** loss *averaged over the Bernoulli hit/miss draw — not a realized sample.** By the Law of Total
Variance this preserves the mean but **discards the dominant variance term**: the bimodal truth that the
asset is either hit (full conditional loss) or missed ($0). Quantiles read off the resulting artificially
smoothed, near-Normal distribution understated the tail by **~12× on VaR₉₉** for a high-frequency peril.

It compounded. PML was fit on annual-max *magnitudes* (OEP frame); VaR was fit on annual *sums of expected
losses* (AEP frame) — **two independently fitted objects with no coherence constraint.** An invariant check
comparing them (`VaR₉₉ ≤ PML₅₀₀`) fired by **~175×** ($547M vs $3.1M for Strong Wind) — a ratio
*mathematically impossible* under any single coherent framework. And beneath it all, a unit bug: `Loss
Ratio` stored as a percent but read as a ratio, inflating inputs by exactly **100×**.

> Only **EAL survived** — because summing expected losses then averaging equals sampling then averaging
> (linearity of expectation). Every metric that depends on the *shape* of the distribution — VaR, PML, TVaR
> — was wrong. The one number that looked fine was the only one the broken method couldn't break.

(Sources: [`issues/pml-var-aep-methodology.md`](../../hazard_analysis/docs/suggested_architecture/issues/pml-var-aep-methodology.md),
[`issues/strong-wind-var-worked-example.md`](../../hazard_analysis/docs/suggested_architecture/issues/strong-wind-var-worked-example.md).)

---

## The principle: one coherent object, derived correctly

> **The principle.** Every risk metric must be a *reading off one coherent loss distribution*, built by
> drawing actual stochastic outcomes — never by collapsing randomness to its mean for convenience.

The correct construction (a unified compound-Poisson Monte Carlo): draw `N ~ Poisson(λ_asset)` per year,
draw **full conditional severities** for the hits, sum to the annual aggregate `A_y` and take the max as the
occurrence loss `O_y`, repeat. Then EAL, VaR, AEP-PML, OEP-PML, and TVaR **all** derive from one severity
model and one λ_asset — coherent by construction. There is no second fit to drift.

This has a formal name in the architecture (A24, **Axiom 3**): *stochastic must stay stochastic past every
nonlinearity.* The moment you replace a random variable with its expectation upstream of a deductible, a cap,
or an aggregation, you have silently broken the tail — because `E[max(0, L − d)] ≠ max(0, E[L] − d)`.

---

## The rule: verify the basics, with absolute values

Plausible-but-wrong is the enemy. The defense is verification against **known answers**, not relative
sanity checks.

> **The rule.** A basic isn't "done" until a worked example with known numbers confirms it. The old repo's
> own [`var_methodology_demo.py`](../../hazard_analysis/docs/suggested_architecture/issues/var_methodology_demo.py)
> (seed=42, deterministic) is the model: it shows the broken method and the correct method *agree on EAL and
> diverge ~12× on VaR* — the divergence *is* the proof. Every foundational piece gets a check like that.

If your VaR and your PML come out of two independent fits, you have *already* failed this rule, whatever the
numbers say.

---

## The anti-pattern: patching symptoms

When the tail looked wrong, the old model shipped a "tail-guard / Weibull re-pin" patch — pinning the fitter,
clamping the tail. It hid the artifact. **It did not fix the distribution being fit, which was still the
wrong distribution.**

> **The anti-pattern.** Treating a symptom (a tail that looks off) instead of the disease (the wrong random
> variable). A clamp that makes a bad number look reasonable is worse than the obviously-bad number, because
> it buys false confidence and ships.

This is why the project chose to **rebuild rather than patch.** You cannot patch your way out of a foundation
that's solving the wrong equation.

---

## Caveats and honest limitations

1. **"Basics spot-on" is not "perfect before anything."** The basics are a *bounded* set — the compound-
   Poisson pipeline, the coherence of the metrics, the units. Get *those* exactly right. The curated damage
   curve will always carry irreducible uncertainty; the discipline is to be *right about the math* and
   *honest about the curve*, not to pretend the curve is exact.
2. **More simulation is not more truth.** A biased damage curve fed through a flawless Monte Carlo produces
   precise, confident, wrong numbers. Spot-on basics include knowing which input is the dominant uncertainty
   (it's the curve) and not laundering it through sample size.
3. **Verification has a cost and it is non-negotiable.** Worked examples and unit checks take time the way
   the old model's missing tests would have. That time is the price of trustable numbers.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Standard interface, not standard physics**](hazard_asset_specificity.md) | The `F/A` over-count was a basics error dressed as generality; correct coupling math *is* a basic. |
| [**Modular from day one**](modularity_and_scaling.md) | Modularity is what makes a basic *verifiable in isolation* — you can unit-check frequency, severity, and aggregation at their seams instead of guessing three layers downstream. |

---

## Summary

The old model collapsed on the basics: it computed tail metrics on the expected loss instead of a sampled
one (EAL survived, VaR/PML didn't), fit PML and VaR as two incoherent objects (the impossible 175×), and
patched the symptoms while the foundation stayed wrong. The rebuild's answer is one coherent loss
distribution from one compound-Poisson simulation, every metric read off it, stochastic kept stochastic past
every nonlinearity, and every basic confirmed against a known-answer worked example. The math is not
plumbing beneath the product. **The math is the product.**
