# Return Period Is `1/p` (Annual-Exceedance) — Not `1/λ`; and the Conventions Coincide Only When Rare

*ASCE hands the wind hazard as gust-by-**MRI** ("mean recurrence interval"). MRI is just the wind world's word for
**return period** — but "return period" itself is defined more than one way in EVT, and our house convention pins
exactly one. Knowing **which**, and **when the definitions agree**, is what makes it legitimate to combine an ASCE
MRI (strong wind) with a fitted Poisson rate (tornado) in the same M4.*

**Status:** v1.0 · written 2026-06-17 · **Sourced from:** convective wind × wind farm · M0 (`01_asce_hazard`) — the
"is MRI just return period?" question / [DD-WN-3](../plans/convective_wind/decisions.md) · **Applies to:** any peril
that **reads** a return-period/MRI surface *and* **fits** an event-rate λ — i.e. mixes the two frequency framings in
one model.

---

## Where this came from

The ASCE 7-22 surface is **gust-by-MRI** (`01_asce_hazard` reads `w2022_mri{10…1e6}`); we asked whether MRI is "just
return period." It is — but answering it *precisely* surfaced that our pipeline uses **two different kinds of
frequency number at once**: strong wind reads an **ASCE MRI** (profile-assembly, no fit — DD-WN-3), while tornado/hail
**fit a Poisson/NegBin rate λ**. Treat those two "frequencies" as the same kind of number and you get the classic
rate-vs-probability bug.

## The lesson

> **House convention** (the [terminology doc](../google_drive_docs/hazard_modeling_terminology.docx) §3): **rate λ** =
> events/yr (unbounded, can exceed 1); **annual exceedance probability `p = 1 − e^{−λ}`** (Poisson, bounded 0–1);
> **return period `T = 1/p`**. So `T = 1/(1 − e^{−λ})` — the *annual-exceedance* flavour — and **ASCE's MRI is exactly
> this** ("design speed by MRI = return-period intensity"). The rate's reciprocal **`1/λ` is the mean inter-arrival
> time, which our docs deliberately do *not* call a return period.** The two **coincide only when the event is rare**
> (`p ≈ λ` for `λ ≪ 1`) and **diverge sharply when frequent** (`λ = 2 ⇒ p ≈ 86%`, not 200%). Never reciprocate a
> fitted rate into a "return period" unless you have already checked `λ ≪ 1`.

`[REF]` The terminology doc states it directly: `T = 1/p`, `p = 1 − e^{−λ}`, *"rate vs. annual probability… the single
most common input-side error,"* close for rare perils and divergent for frequent ones. The
[risk-metrics doc](../google_drive_docs/risk_metrics_reference.docx) applies the same bridge to the occurrence curve —
`OEP_max(L) = 1 − exp(−λ_asset · q_event(L)) ≈ λ_asset · q_event(L)` *"in the sparse regime"* — and the
[methodology doc](../google_drive_docs/hazard_asset_loss_distribution_methodology.docx) §5: *"the chance of zero
events in a year is `exp(−λ)`; the chance of at least one is `1 − exp(−λ)`."*

`[OURS]` Two *distinct* things get conflated here (an earlier draft of this entry merged them — keep them apart):
- **Why we can *combine* the two sub-perils into one loss distribution → disjointness, NOT rarity.** Co-sampling two
  *independent* compound-Poisson streams is *always* valid (their superposition is again compound-Poisson; EAL adds;
  the tail is the convolution) — it needs **independence** ([AWN-28](../plans/convective_wind/assumptions.md) /
  [DD-WN-15](../plans/convective_wind/decisions.md): tornado ⊥ strong wind, disjoint by data product). Rarity is
  irrelevant to *this*.
- **Why an ASCE MRI and a fitted Poisson rate sit on the same footing (rate ↔ return-period) → THIS is the rarity
  part.** `1/λ ≈ 1/p` only when `λ ≪ 1`. And here is where the **collection-vs-asset** line lives: our collection-level
  rate is **not** rare (hail `λ_collection ≈ 29.6/yr`; regional tornado rates high) — there `1/λ` and `1/p` are wildly
  apart; only **after thinning to the asset** (`λ_asset ≪ 1`) and folding in severity do they reconverge.

In the build the second concern is real but **benign**: M1 converts the ASCE return-level curve to a Poisson rate
(profile-assembly, ξ≈0 fit anchored on the rare design tail, where `1/p = 1/λ` is exact), and the only frequent
regime — the 58 mph μ-threshold, `λ_sw ≈ 0.9/yr` — carries `DR ≈ 0` (below IEC survival), so **no loss flows through
where the rare-approximation would be loosest.** The loss lives in the rare damaging tail, where the interchange is
exact.

`[EVT-LIT]` *(external literature, brought in to connect — not to contradict the house convention.)* The broader
EVT / hydrology literature uses **two** return-period definitions, and it helps to see ours as a labelled choice
between them:
- **Block-maxima / GEV:** `T = 1/(1 − F_annual-max(x))` — waiting time in *exceedance years*.
- **Peaks-over-threshold / Poisson:** `T = 1/λ(x)` — mean inter-arrival of *exceedance events* (Coles 2001, §3–4;
  standard hydrologic POT practice).

Under a Poisson process these are **the same objects as our house quantities**: `1 − F_annual-max = 1 − e^{−λ} = p`,
so block-maxima `T = 1/p` (**our** return period) and POT `T = 1/λ` (**our** rate's reciprocal). **No contradiction —
identical math.** The only difference is which quantity the *word* "return period" attaches to: parts of the POT
literature call `1/λ` a return period; **our docs reserve "return period" for `1/p` and name `λ` the "rate,"**
precisely to head off the conflation that loose POT usage invites. When citing the POT `1/λ` form, say so explicitly
and map it back to `λ` (rate), not to `T` (return period).

**Which branch ASCE actually uses (pinned).** ASCE 7-22's **non-hurricane** maps — the branch our inland sites read —
are a **2-D Poisson-process / peaks-over-threshold** EVT model + local regression (NIST), with a **bounded** tail
(reverse-Weibull / POT-GPD, **ξ<0**; [Simiu 1996 *Peaks-Over-Threshold*](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9445%281996%29122%3A5%28539%29),
Peterka-Shahid 1998; [ASCE 7-22 App F](https://amplify.asce.org/content/standard/9780784415788/part/provisions/back-matter/appf),
[NIST mapping](https://www.nist.gov/publications/mapping-return-values-extreme-wind-speeds)). So it is **POT, not
block/annual-maxima** (annual-maxima + Gumbel was the *pre-1995, fastest-mile* basis). Two consequences for us: (1)
the ASCE *generating* tail is **bounded (ξ<0)**, but its return-level curve is **near-log-linear over MRI ≤ 10⁶**, so
our M1 ξ≈0-+-cap-at-L is a faithful approximation (the bound bites only far beyond our range) — corrected from an
earlier "not a bounded GPD" overstatement ([AWN-17](../plans/convective_wind/assumptions.md)); (2) the **deep-tail
Appendix-F speeds (10⁴–10⁶ MRI) carry large SE ≈ 10–16 mph** (NIST) — real uncertainty in the gusts we read.

**Worked.** How far apart the two are, by rarity:

| rate `λ` (events/yr) | POT `1/λ` | annual-exc. `1/(1−e^{−λ})` | gap |
|---|---|---|---|
| 1/700 (a 700-yr gust) | 700 | 700.5 | **0.07%** |
| 0.02 (50-yr) | 50 | 50.5 | 1% |
| 0.1 (10-yr) | 10 | 10.5 | 5% |
| 1 | 1 | 1.58 | **58%** |

In the build: strong wind reads **MRI 700 ≈ 110 mph at Traverse** straight off ASCE (`1/p`, deep-rare → no ambiguity);
tornado fits `λ_collection` then thins to `λ_asset ≈ 0.24/yr` (Traverse) — only at *that asset rate* is
"`1/λ_asset` ≈ return period" approximately true.

## How to recognize it next time

When two "frequencies" meet in one model, interrogate **each**: is it a **rate** (count/yr, can exceed 1) or a
**probability / return-period** (`1/p`, bounded)? If you are about to turn a rate into a "return period" by
reciprocal, **check `λ ≪ 1` first.** The one-question test: *"is this number a count-per-year, or a per-year
probability?"*

## Caveats and limits

- **A THIRD convention exists, and we have not pinned it — flag for discussion.** *Empirical* (Weibull
  plotting-position) RP vs *EVD-fitted* RP. The Hazard-Data-Reference raises it for STORM hurricane grids
  (*"document which convention you adopt"*). Our M4 AEP curve is built **empirically** (`M_YEARS / rank` on sorted
  annual losses) — fine for the body, but the deep tail (PML250 read at 300k years) is plotting-position and
  **sample-limited** ([learning-10](10_monte_carlo_effective_sample_size.md)). Worth an explicit decision when we add
  EVD-fitted tails or ingest STORM-style grids. **Not resolved — raised, per the discuss-don't-assume rule.**
- **"AEP" is overloaded.** In the [risk-metrics doc](../google_drive_docs/risk_metrics_reference.docx), `AEP` =
  **Aggregate** Exceedance Probability (the annual-*total*-loss curve), **not** the generic *annual* exceedance
  probability `p` used here. Same letters, different object — keep them distinct.
- **No contradiction with the Drive docs.** The substance is already in the terminology + metrics docs; this entry
  only *names* the conventions and adds the collection-vs-asset operational rule. Writing the explicit
  block-maxima / POT / empirical taxonomy *into* the terminology doc would be a discuss-then-update-Drive step — not
  required, since the docs already carry the substance.

## Cross-references

- **Reference it builds on:** terminology doc §3 (rate / AEP / return period) · metrics doc (`OEP = 1 − e^{−λ_asset·q}`,
  sparse regime; the AEP naming note) · methodology doc §5 (Poisson `1 − e^{−λ}`).
- **Decision it serves:** [DD-WN-3](../plans/convective_wind/decisions.md) (strong wind = profile-assembly off the MRI
  surface) and the hail/tornado `λ_collection → λ_asset` thinning ([DD-WN-5](../plans/convective_wind/decisions.md)).
- **Siblings:** [`06`](06_collection_region_size_cancels.md) (the `λ_collection · p` frame this thins from) ·
  [`02`](02_count_distribution_and_dispersion_prior.md) (the rate λ as a fitted object) ·
  [`10`](10_monte_carlo_effective_sample_size.md) (the empirical-tail caveat above).
- **Where it shows in code:** `Notebooks/convective_wind/m0_input_data/01_asce_hazard.ipynb` §2 (the MRI field
  dictionary) · the M4 AEP exceedance curve (empirical `M_YEARS/rank` return period).
