# EVT for a New Peril — Read-or-Fit → Which Method → Which Tail → Pin It

*The day you start hurricane, flood, or any new hazard you face the same fork: do you **read** a pre-integrated
hazard product or **fit** one from raw evidence — and if you fit, **which** EVT (POT vs block-maxima), **which** tail
(bounded vs light), and how do you **pin** it so the next person trusts it? This stitches the scattered
frequency / severity / provenance lessons into one decision tree, grounded in the three perils we've actually built.*

**Status:** v1.0 · written 2026-06-17 · **Sourced from:** synthesis across hail × solar, wildfire × solar,
convective-wind × wind-farm (M0–M1) / learnings [01](01_extending_a_short_hazard_record.md) ·
[02](02_count_distribution_and_dispersion_prior.md) · [04](04_two_datasets_one_peril_decompose.md) ·
[09](09_pre_integrated_vs_extracted_catalog.md) · [11](11_return_period_conventions.md) · **Applies to:** every
**new peril** or **new hazard data product** at M0/M1 — *not* a new *asset* under an existing peril (that reuses the
catalog unchanged).

---

## First, the scope rule (so you don't fit when you shouldn't)

EVT lives at **M0/M1 — the peril, asset-independent.** A new **asset** under an existing peril (convective-wind ×
solar, hail × BESS) **reuses the catalog/EVT unchanged** — no new fit. This guide fires only on a **new peril**, or a
**new hazard data product** for an existing peril. *If you reached for EVT because you added an asset, stop — you've
mis-located the work* ([learning-09](09_pre_integrated_vs_extracted_catalog.md) draws the same line for M1 machinery).

## The decision tree

```text
  Step 0 — WHAT DO YOU HOLD?   Q: does the source give a PROBABILITY / RETURN-PERIOD, or a COUNT / OBSERVATION series?
  (learning-09)
        pre-integrated                                                         raw evidence
  (RP surface · burn-prob · depth-return grid)                      (reports · swaths · tracks · station extremes)
                │                                                                     │
                ▼                                                                     ▼
   ┌─────────────────────────────┐                          ┌──────────────────────────────────────────────┐
   │ READ — profile-assembly      │                          │ FIT                                            │
   │ • no re-fit, no dispersion   │                          │ (1) FREQUENCY λ: decompose → bias-correct →    │
   │   test (it lives in the      │                          │     dispersion test → Poisson | NegBin         │
   │   product)                   │                          │ (2) METHOD:  POT/GPD  (default) | block-maxima │
   │ • characterize the curve's   │                          │ (3) TAIL ξ:  <0 bounded | 0 light | >0 heavy   │
   │   actual shape               │                          │              (physical ceiling? → ξ<0 at L)    │
   └──────────────┬───────────────┘                          └───────────────────────┬────────────────────────┘
                  └───────────────────────────┬──────────────────────────────────────┘
                                              ▼
                          Step 4 — PIN IT:  method · convention (rate vs RP) · basis/vintage ·
                                            uncertainty (SE, esp. deep tail) · mixing rule
```

## Step 0 — Read or fit? (the gate — [learning-09](09_pre_integrated_vs_extracted_catalog.md))

The one-question test: **"does my source hand me a probability / return-period, or a count / observation series?"**
- **Pre-integrated** (ASCE MRI surface; FSim annual burn probability; flood depth-return grids — any RP / annualized
  field): an authority already integrated the stochastic set → **READ it (profile-assembly).** Do *not* re-fit, invent
  a catalog, or re-test dispersion (it's *inside* the product). Jump to **Step 4**.
- **Raw evidence** (event reports, radar swaths, storm tracks, station extremes) → **FIT it** (Steps 1–3).
- The trap both ways: running fit-machinery on a pre-integrated product (double-counts / invents events), or treating
  a read product as if you'd estimated it (claims a precision you didn't earn).

## Step 1 — Frequency λ (fit path)

- **Multiple datasets? Decompose, don't splice** ([04](04_two_datasets_one_peril_decompose.md) /
  [01](01_extending_a_short_hazard_record.md)): use each for what it's good at — the long-but-biased record to
  *extend the rate*, the short-but-clean one as the *spine*. A naive temporal splice fabricates a rate discontinuity.
- **Bias-correct BEFORE fitting** ([01](01_extending_a_short_hazard_record.md); the SPC detection-bias case, AWN-1):
  population/detection drift, reporting changes — fit on a detection-stable window.
- **Choose the count distribution by testing dispersion** ([02](02_count_distribution_and_dispersion_prior.md)):
  Fano `φ = var/mean`. `φ ≈ 1` → **Poisson**; `φ > 1` → **Negative Binomial** (clustering / outbreaks). Hold a prior
  (convective perils cluster → expect over-dispersion), but *test* — Poisson is the NegBin special case, so default-test
  not default-assume. (Pre-integrated → dispersion is structural, `fano=1`, untestable — the wildfire case.)
- **Fit λ at the COUNTING threshold μ**, which is distinct from the **damage-onset** threshold (DD-WN-7, the
  two-thresholds rule): λ counts "events"; damage starts higher.

## Step 2 — Method: POT vs block-maxima (the choice you asked about)

| | **Block-maxima (GEV)** | **Peaks-over-threshold (POT / GPD)** |
|---|---|---|
| data used | one maximum per block (year) | *all* independent exceedances over a threshold `u` |
| needs | a long record | threshold choice + **declustering** (independence) |
| you fit | GEV (location, scale, **ξ**) | GPD (scale, **ξ**) + a **Poisson rate** of exceedance |
| use when | data is naturally annual; within-year independence is hard | many sub-annual exceedances; you can decluster |
| **default lean** | — | **POT** — more data → less uncertainty; it's what ASCE non-hurricane + most hazard work use ([learning-11](11_return_period_conventions.md)) |

- **Keep rate vs return-period straight** ([11](11_return_period_conventions.md)): POT gives a **rate `λ(u)`**
  (events/yr); the **return period is `1/p = 1/(1−e^{−λ})`**, which is `≈ 1/λ` *only when rare*. Never reciprocate a
  frequent rate into a "return period."
- **If you're READING** a pre-integrated product, you still pin *which* method generated it (ASCE non-hurricane =
  2-D Poisson-process / **POT**, bounded; hurricane = Monte-Carlo simulation) — Step 4.

## Step 3 — Tail shape ξ (severity — AWN-17 / DD-WN-8 / [hazard_math-05](../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md))

`ξ` sets the upper tail — and for physical hazards it usually wants to be ≤ 0:
- **ξ < 0 (reverse-Weibull — BOUNDED):** finite ceiling `L`. The **default for physically-capped** hazards (tornado
  EF5 ceiling; ASCE non-hurricane wind). Prefer it whenever a max-credible bound exists.
- **ξ = 0 (Gumbel / exponential — light, unbounded):** thin tail. Strong wind reads ≈ this over MRI ≤ 10⁶ (a faithful
  approximation of ASCE's bounded curve, since the bound bites beyond our range — AWN-17).
- **ξ > 0 (Fréchet — HEAVY, unbounded):** fat tail — *rare/suspect* for physical wind/hail (physics caps them);
  justify hard before adopting.
- **Sparse data? Solve, don't MLE.** Tornado used an analytic bounded-GPD solve from the mean + the bound:
  `ξ = (μ_mean − μ)/(μ_mean − L)`, `σ = −ξ(L − μ)` — robust where an MLE would be unstable.
- **Never back-solve severity from a target EAL** (AWN-18 anti-pattern — the old repo's reverse-engineering).
- **Keep frequency × severity COUPLED** ([09](09_pre_integrated_vs_extracted_catalog.md); the Method-0 prohibition):
  never average/multiply the marginals separately; reunite them only by **sampling** (M4).

## Step 4 — Pin it (read OR fit — [learning-11](11_return_period_conventions.md) / AWN-15)

Record, every time:
- **method + distribution** (POT vs maxima; GEV/GPD; ξ sign + bound) — and for a *borrowed* product, the **generating
  EVT + citation** (don't leave it "a borrow with inherited assumptions" — that was the AWN-15 gap we closed for ASCE).
- **convention**: is the "frequency" a rate `λ` or an annual-exceedance `p`? is the "return period" `1/λ` or `1/p`?
- **basis & limits**: vintage, terrain/exposure basis, **stationarity** (climate drift), and **uncertainty** — the SE,
  *especially the deep tail* (ASCE App-F 10⁴–10⁶ MRIs carry ~10–16 mph SE).
- **mixing rule**: combining sub-perils is valid by **disjointness / independence** (AWN-28) — *not* rarity; the
  rate↔return-period interchange is the part that needs the **rare regime** (asset level, not collection level).

## Worked — our three perils through the same tree

| peril (source) | hold | gate | method | tail |
|---|---|---|---|---|
| **hail** (MRMS radar swaths) | raw | **FIT** | `λ_collection` from a 5.65-yr record; **NegBin** φ≈3.4 | hail-size → DR severity |
| **wildfire** (FSim BP + FLP) | pre-integrated | **READ** | profile-assembly; `λ = −ln(1−BP)`; Poisson (**fano=1 structural**) | FLP histogram (discrete, conditional) |
| **conv. wind — strong [W]** (ASCE MRI surface) | pre-integrated (POT-GPD, bounded) | **READ** | profile-assembly; ξ≈0 over MRI ≤ 10⁶ | bounded; cap at L = 113 m/s |
| **conv. wind — tornado [T]** (SPC tracks/reports) | raw (biased) | **FIT** | `λ_collection` **bias-corrected**; NegBin/Poisson by site | **bounded GPD, ξ<0**, analytic solve, L = EF5 |

Every cell is a real decision we made — the tree is just the pattern behind them.

## Caveats and limits

- This is the **M0/M1 frequency + severity** tree — *not* coupling (M2) or damage (M3). Coupling type
  (areal hit-or-miss / field-intensity / site-conditioned) is a **separate** dispatch (the peril×asset matrix); the
  damage curve is a third, independent choice ([05](05_damage_curve_three_coupled_choices.md)).
- **"Read" is not free** — you inherit the product's assumptions and *can't test them* ([09](09_pre_integrated_vs_extracted_catalog.md));
  Step-4 pinning is how you stay honest about where the uncertainty moved.
- **Declustering and threshold choice** (POT independence) are genuine sub-skills this guide *names* but doesn't fully
  *teach* — reach for the EVT reference ([hazard_math-05](../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md))
  when you actually sit down to fit a POT model.

## Cross-references

- **Stitches:** [09](09_pre_integrated_vs_extracted_catalog.md) (read vs fit) · [01](01_extending_a_short_hazard_record.md)
  (short records) · [02](02_count_distribution_and_dispersion_prior.md) (dispersion) ·
  [04](04_two_datasets_one_peril_decompose.md) (decompose datasets) · [11](11_return_period_conventions.md)
  (conventions + provenance).
- **Severity/tail:** AWN-17 / [DD-WN-8](../plans/convective_wind/decisions.md) /
  [hazard_math-05](../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md).
- **Reference it builds on:** methodology doc §4–5 (frequency); terminology doc §3 (rate / AEP / return period).
- **Where it'll show next:** **hurricane** (a *simulation-read* product + the TC-tornado disjointness trap, AWN-30) ·
  **flood** (depth-return grids = read, like wildfire's BP).
