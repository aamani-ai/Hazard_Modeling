# The Count Distribution Is a Tail Decision — Test It, and Hold a Prior

*Why whether annual event counts are Poisson or Negative Binomial barely moves the average loss but strongly
moves the tail (PML/VaR) — so you **test** the dispersion; and when the record is too short to test, you fall
back on a **principled prior**, not a thin-tailed default.*

**Status:** v1.0 · written 2026-06-09 · **Sourced from:** hail × solar, Phase 2 frequency question / [DD-2](../plans/hail/decisions.md) · **Applies to:** any peril fitting an annual event-rate λ (flood, wind, wildfire).

---

## Where this came from

The M1 hail catalog manifest declares `frequency_process = negative_binomial`. The fair question: *why NegBin
— is that an assumption? Should we just test and fit? Or use Poisson?* Pulling on it surfaced a lesson
bigger than hail.

## Why it looked fine — three traps

1. **Poisson is the convenient default.** One parameter, and it's what we inherited (OASIS-LMF). But Poisson
   *forces* `variance = mean` — it has no freedom to be over-dispersed.
2. **"Just assume NegBin" is also wrong.** Swapping one unchecked assumption for another is the same sin.
   The count family is an empirical question, not a style preference.
3. **"Just fit it" quietly fails at our sample size.** Over-dispersion lives in the *year-to-year* variance
   of counts — you need many *annual* counts to see it. With ~5–6 years of record (our MRMS-on-AWS reality)
   the dispersion test is underpowered; a naïve fit will look Poisson-ish simply because it can't tell.

## The lesson

> **The lesson.** The count distribution is a **tail decision**, not a mean decision: test the annual-count
> **dispersion** (the Fano factor, var/mean). NegBin *nests* Poisson, so fit NegBin and let the data collapse
> it to Poisson if warranted — never default to Poisson. And when the record is too short to test, **anchor
> on a principled prior** (over-dispersed, because the peril clusters), not on the thin-tailed default.

**The reasoning:**

- **It's the tail, not the mean.** `[REF]` For **EAL** (the mean annual loss) Poisson vs NegBin is nearly
  identical — same λ → same mean. For **VaR / PML at 1-in-100/250** it matters a lot: Poisson under-disperses
  → too-thin tail → **PML understated.** That is the same *family* of error the old repo made — fine on the
  average, broken in the tail.
- **The physics says over-dispersed.** `[REF]` SCS/hail **clusters** — active synoptic seasons fire many
  events, quiet seasons few — so the variance of annual counts exceeds the mean (A24 §4.2: empirical
  variance-to-mean ≈ **1.5–3**; the OASIS Poisson default is "empirically wrong for SCS").
- **NegBin contains Poisson.** `[REF]` NegBin = a Poisson whose rate wobbles year to year (Poisson-Gamma);
  as the wobble → 0 it *is* Poisson. So fitting NegBin is strictly safer — if the data are really Poisson,
  the dispersion parameter comes back ≈ 0.
- **At small n the prior must carry it.** `[OURS]` A24 §4.3 flags the dispersion test as underpowered below
  ~10–15 yr. With ~5–6 annual counts you cannot reliably distinguish Poisson from mild over-dispersion — so
  the *prior* dominates, and the safe prior is over-dispersed (errs toward a fatter tail, the conservative
  direction for PML, and collapses to Poisson gracefully).

## The prior we hold (hail v1) `[OURS]`

A weakly-informative prior on the annual-count **Fano factor** `φ = var/mean`:

- **family:** Negative Binomial (nests Poisson at `φ = 1`);
- **prior median `φ ≈ 2`**, central 90% ≈ **[1, 3.5]** — centered in the SCS literature range (`[REF]` A24
  VMR ≈ 1.5–3) but deliberately reaching down to `φ = 1` so enough years of data can pull it back to Poisson;
- **mapping:** at fit time, with mean count `μ`, the NB2 dispersion is `α = (φ − 1)/μ`;
- **behavior:** at small n the posterior ≈ the prior (→ NegBin, fatter tail); as the record widens it becomes
  data-dominated.

This prior is recorded in the catalog manifest (`frequency_process_params.prior`), so the deferred fit
inherits it rather than starting from a guess.

## The fit-and-check protocol (when the record widens)

1. Compute the Fano factor `φ` of annual counts (≈1 → Poisson; >1 → over-dispersed).
2. Fit **both** Poisson and NegBin by MLE; compare via likelihood-ratio test / AIC on the dispersion param.
3. Prefer the **Bayesian fit** with the prior above — the posterior shrinks toward Poisson or NegBin as the
   data warrant, which is exactly what you want at intermediate n. Report `φ`, the test, the chosen family,
   and the fitted params with uncertainty.

## How to recognize it next time

Any peril where you're about to pin a frequency from **few years of counts**. The tell: a one-parameter
**Poisson on a clustered peril** (SCS, flood, wildfire seasons). Before shipping it, ask: *did I test the
dispersion — and if I couldn't, did I anchor on an over-dispersed prior or silently accept Poisson's thin
tail?*

## Caveats and limits

- **Prior center is generic SCS.** `φ ≈ 2` is a CONUS-level figure; a moderate-hail site (Culberson) may
  differ. The prior is weak *by design* and gets refined per-region as the record grows.
- **Over-dispersion ≠ non-stationarity.** NegBin treats year-to-year wobble as *random*. A **trend** or
  **regime** is a different fix — non-stationary `λ(t)` or regime-switching (A24's other options) — don't
  use NegBin to paper over a real trend.
- **Frequency dispersion is separate from the severity tail.** Both feed loss; this lesson is about the
  *count* distribution only. The hail-*size* tail (EVT) is its own decision.
- **This is the frequency half of [`learning_logs/01`](01_extending_a_short_hazard_record.md)** — a short record
  hurts λ's *value* (01) *and* its *dispersion estimate* (here). Widening the record helps both.

## Cross-references

- **Decisions:** [`../plans/hail/decisions.md`](../plans/hail/decisions.md) § DD-2 (this choice), § DD-1 (the record-length basis).
- **Principle:** [`basics_spot_on.md`](../principles/basics_spot_on.md) — a thin-tailed count distribution is a basics-failure that only shows up in the PML.
- `[REF]` **A24 §4.2 / §4.3 / §4.5** — NegBin for SCS, small-n caveat, hail row:
  [`A24_distribution_choices.md`](../../infrasure-hazard-competitive-research/learnings/architecture/A24_distribution_choices.md).
- `[REF]` founder `hazard_asset_loss_distribution_methodology` — *"test the dispersion… NegBin is the default"* ([`../google_drive_docs/README.md`](../google_drive_docs/README.md)).
- **Artifact:** `data/hail/hayhurst_hail_m1_manifest.json` → `frequency_process_params.prior`.
