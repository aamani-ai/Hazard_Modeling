# 04 — Aggregation & Double-Counting: how sub-peril losses combine (and where it bites)

*A discussion doc, not a plan. It exists to settle **how we combine losses across the two convective-wind
sub-perils** (and, recursively, across perils) — **before M4 builds the combine, and before hurricane makes it
hard.** The question looks small ("do we add the EALs and PMLs?") but the wrong answer is exactly the class of
error this rebuild exists to escape (the old model's incoherent tail). Written for a reader new to the domain;
every claim is tagged `[REF]` (settled in the Drive methodology — the source of truth) or `[OURS]` (a build
assumption we are making, to be flagged for a Drive-doc update if it ever becomes load-bearing).*

> **Source of truth.** The aggregation rules below are the **Drive methodology**
> (`docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` + `risk_metrics_reference.docx`). Per
> our governance rule (the Drive docs are the primary truth; deviate only via discuss → update the Drive doc →
> then build — [`../../00_scope_and_story.md`](../../00_scope_and_story.md)), this doc *applies and
> reasons about* that methodology — it does not invent a new one. Where we add a build-specific assumption, it is
> tagged `[OURS]` and flagged as a candidate Drive-doc addition.

> Siblings: [`01` scope & taxonomy](01_scope_and_sub_peril_taxonomy.md) · [`02` coupling](02_coupling_buckets_and_wind.md)
> · [`03` hazard definition](03_hazard_definition_and_thresholds.md). Consumes → [`plans/convective_wind/m4_loss_metrics.md`](../../../plans/convective_wind/m4_loss_metrics.md).

---

## TL;DR (the whole argument in one screen)

1. **EAL adds; the tail does not.** `[REF]` `EAL_total = EAL_tornado + EAL_strongwind` is *exact* (linearity of
   expectation — works for any dependence). But **VaR / PML / TVaR are quantiles and do NOT sum** — *"combine
   event catalogs, then compute,"* never add per-sub-peril tail numbers.
2. **The right combine is ONE sampled distribution.** `[REF]` Each simulated year draws events from *both*
   sub-perils' `(λ, severity)`, sums the **realized** losses into that year's total, and every metric is read off
   that single joint distribution — with a per-sub-peril **EAL** attribution split (EAL is the only thing that
   may be split additively).
3. **Adding EAL is safe only if the event sets are DISJOINT** `[REF concept]` — no single physical event counted
   twice. For tornado vs strong wind they **are** disjoint, but **by data product, not by physics** `[OURS]`: the
   ASCE basic-wind surface is non-tornadic by construction; tornado is the SPC `Tornado` record. The fence is the
   *dataset*, not nature.
4. **A second backstop: strong-wind damage ≈ 0** `[OURS]` — even residual overlap carries ~no loss (strong-wind
   gusts stay below IEC survival), so it can't double-count anything material *in this build*. This is a numerical
   accident, not a structural guarantee.
5. **Summing per-sub-peril PMLs MIS-states the tail** `[REF]` — VaR is not additive, and **not even a safe bound**
   (it is non-coherent). The direction depends on the distributions: for continuous comonotonic losses summing
   *overstates*; but our **M4 result** shows the opposite — with zero-inflated, NegBin-clustered tornado tails the
   **joint VaR is *higher* than the sum (summing *understates* by ~28%)**. Either way: read the tail off the joint.
6. **Hurricane breaks the clean case** `[REF concept]` — TC-spawned tornadoes appear in both a tornado catalog
   AND a hurricane catalog, and hurricane wind *is* damaging (the zero-damage backstop won't save it). The fix is
   a partition discipline (V1 tornado = inland-convective only) or shared-event sampling — deferred with hurricane.
7. **The rule is recursive** `[REF]` — "disjoint streams → sample into one distribution → EAL additive, tail off
   the joint" is the *same* operation at the sub-peril level (within convective wind), the peril level
   (convective wind + hail + wildfire → Total Loss), and the portfolio level.

---

## 1. The worry, stated plainly

We model convective wind as **two sub-perils** with separate catalogs ([`01`](01_scope_and_sub_peril_taxonomy.md)):
tornado `{λ_T, severity_T}` and strong wind `{λ_W, severity_W}`. At the end we want **one wind risk number per
site** (EAL, VaR, PML, TVaR). The naïve move is to compute each metric per sub-peril and **add them**:
`EAL = EAL_T + EAL_W`, `PML₁₀₀ = PML₁₀₀,T + PML₁₀₀,W`. The worry — the right worry — is **double-counting** and,
more subtly, **whether quantiles even add at all.** Get this wrong and the headline tail is silently wrong, which
is the exact failure the rebuild exists to escape ([`principles/basics_spot_on`](../../../principles/basics_spot_on.md)).

The answer has two layers: **(A) the metric rule** (what may be added) and **(B) the disjointness condition**
(when adding is even meaningful). Both come from the Drive methodology; we apply them to convective wind.

---

## 2. The metric rule — EAL adds, the tail does not  `[REF]`

The Drive methodology is explicit, and it splits cleanly by metric:

- **EAL is additive.** EAL is the *mean* of the annual-loss distribution, and **expectation is linear**:
  `E[A+B] = E[A] + E[B]` for **any** dependence (no independence needed). `[REF]` *"for gross, uncapped loss it
  can be computed by summing expected event losses (Method 0) and still be correct, since expectation is linear
  and averaging preserves the mean"*; EAL is called *"a portfolio-aggregation building block."* So a per-sub-peril
  EAL split that **sums to the total EAL** is legitimate and useful.
  - ⚠️ **Caveat `[REF]`:** that immunity holds **only for gross, uncapped loss.** Once a shared **cap** (e.g. the
    annual loss capped at TIV, which M4 does), **deductible**, or **aggregate limit** spans the combined loss,
    `min(A+B, TIV) ≠ min(A,TIV) + min(B,TIV)` — so even EAL must then be read off the **combined** sampled
    distribution, not summed from capped per-sub-peril EALs. *(Report per-sub-peril EAL on the **uncapped** mean;
    take the **combined** EAL off the capped joint vector.)*

- **VaR / PML / TVaR are NOT additive.** These are **quantiles** (or tail-averages) of a distribution, and
  quantiles do not sum. `[REF]` *"Aggregating per-occurrence metrics linearly — OEP numbers cannot be summed
  across years or assets; combine event catalogs, then compute"*; *"per-asset PMLs do not sum across a portfolio
  when perils are correlated."* Summing them is wrong (see §5).

> **The shape of the answer:** **two profiles in → one sampled distribution out.** Read the **mean (EAL)** by sum
> *or* off the joint; read **every tail metric off the joint only.**

---

## 3. The combine, mechanically — one sampled distribution  `[REF]`

The methodology's engine (and our M4 plan) does this: per simulated year, draw events from **each** sub-peril's
own `(λ, severity)` (tornado: NegBin/Poisson areal-thinned; strong wind: Poisson site-conditioned), **sum the
realized losses** into that year's `AEP_year` (capped at TIV), take the max single event as `OEP_year`, repeat for
~300k years, then read `EAL = mean`, `VaR₉₉ = pctl(99)`, `TVaR₉₉ = mean(tail)` off the **one** vector. `[REF]` The
methodology's universal interface makes this work — every peril emits the same `event_record`, and *"the annual
aggregator that consumes them does not know or care which hazard produced them."* The Drive doc's worked example
(Brazos Ridge) shows it concretely: hail, tornado, ice and hurricane scenarios all sit on **one** all-peril AEP
curve, each return-period band attributed to the dominant peril — *not* stitched from separate per-peril curves.

This is why we keep two **separate** catalogs upstream but **combine by sampling**, never by arithmetic on
metrics — the realization of [`basics_spot_on`](../../../principles/basics_spot_on.md) ("one coherent distribution").

---

## 4. The disjointness condition — what makes adding EAL valid

Linearity makes `E[A+B] = E[A]+E[B]` *arithmetically*, but that is only the *right* number if `A` and `B` don't
both contain the loss of the **same physical event**. If a single event's loss is booked in *both* sub-perils,
`E[A]+E[B]` counts it twice — linearity does not save you. So **adding EAL across sub-perils is valid iff the
event sets are disjoint** (mutually exclusive). `[REF concept]`

**Are tornado and strong wind disjoint? Yes — but by *data product*, not by physics.** `[OURS]`
- A tornado and a straight-line gust **can co-occur** (the same convective storm spawns both), and they live on
  the **same 3-s-gust axis** with **overlapping event thresholds** (strong-wind μ = 58 mph ≈ 25.9 m/s sits *below*
  tornado μ = EF0 65 mph). So physically there is an **overlap band**, not a clean partition.
- What keeps them disjoint is **how we source each stream**:
  - **strong wind ← the ASCE basic-wind surface**, which is **non-tornadic by construction** `[REF, ASCE]`
    (ASCE 7 basic-wind maps exclude direct tornado strikes; tornado is the separate Ch.32 surface). So **no
    tornado enters the strong-wind stream.**
  - **tornado ← the SPC `Tornado` event-type record** — tornadoes only.
  - ⇒ each physical event is logged in exactly one stream. **The fence is the dataset, not nature.**

> **Why this matters (the subtlety):** disjointness here is a **classification / data-product property**, not a
> physical law. It holds *because* the strong-wind spine is the non-tornadic ASCE surface. The documented
> *alternative* strong-wind path — fitting the SPC thunderstorm-wind reports
> ([`03`](03_hazard_definition_and_thresholds.md)) — would make disjointness depend on **NOAA's `EVENT_TYPE`
> hygiene** (no tornado damage mis-logged as thunderstorm wind), which is a data-cleanliness assumption, not a
> guarantee. **If the strong-wind source ever changes, re-audit disjointness.** `[OURS]`

---

## 5. The tail — why summing PMLs is wrong  `[REF]`

`VaR_p(A+B)` is the p-quantile of the **sum's** distribution; `VaR_p(A) + VaR_p(B)` adds the two **marginal**
quantiles. These are **not** equal — and crucially **VaR is non-coherent**, so the sum is **not even a safe
bound**, and the direction of the error depends on the distributions:
- For **continuous, comonotonic** positive losses, summing **overstates** (it pretends both deliver their 1-in-100
  blow the same year).
- But for our **zero-inflated, NegBin-clustered** sub-perils, the **M4 result is the opposite**: the **joint VaR99
  is *higher* than the sum** — summing **understates by ~28%** (Traverse: joint \$11.6M vs sum \$8.3M). VaR turns
  out *super-additive* here.

The invariant, regardless of direction: **read every tail metric off the joint sampled distribution; never sum
quantiles.** `[REF]` (TVaR *is* coherent / sub-additive, so a sum of TVaRs is at least a conservative upper bound;
VaR is not even that — exactly why M4 reports both and reads them off the joint.)

> **Tornado-specific note `[REF/AWN-16]`:** tornado is sparse (Traverse Fano ≈ 12 → NegBin; Shepherds ≈ 0), so at
> moderate return periods tornado VaR can **floor to \$0** and the combined VaR is strong-wind-dominated. That is
> why M4 reports **TVaR** alongside VaR for the tornado tail — a \$0 VaR does **not** mean "no tornado tail"
> ([learning-10](../../../learning_logs/10_monte_carlo_effective_sample_size.md)).

---

## 6. The "safe because strong-wind damage ≈ 0" backstop — and its limit  `[OURS]`

There is a **second** reason the convective-wind combine is clean today: even if some overlap slipped through, it
would carry **~no loss**, because **strong-wind damage ≈ 0** — its gusts stay below the IEC survival onset
(the anchored-curve / two-threshold finding, [`03`](03_hazard_definition_and_thresholds.md); quantified in
[m1_catalog](../../../../Notebooks/convective_wind/m1_catalog/01_catalog.ipynb): even the 10⁶-yr gust ≈ 75 m/s ≪ IEC ~52–70 m/s
onset). So the overlap band (≈29–58 m/s) maps through the damage curve to ≈0 — it **cannot double-count a material
loss.**

> ⚠️ **This is a numerical accident of *this* build, not a structural guarantee.** It would **bite** if: (a) the
> turbine curve's damage onset were lower (overlap gusts start causing loss); or (b) we ever reported **frequencies**
> additively rather than losses; or (c) the strong-wind source changed (§4). So we **state the disjointness
> assumption explicitly and do not lean on the zero-damage accident** as the primary defense — it is a backstop,
> not the argument.

---

## 7. Hurricane — where the clean case breaks  `[REF concept]`

When the deferred **hurricane** peril ([`01` §6](01_scope_and_sub_peril_taxonomy.md)) is built, the disjointness
that protects convective wind **fails**:
- a hurricane **spawns tornadoes** (landfalling TCs routinely produce tornado outbreaks) — these are *real tornado
  tracks* in the SPC `Tornado` record **and** would be represented inside a TC catalog → the **same physical
  tornado counted twice**;
- a hurricane produces **extreme straight-line wind** that overlaps the strong-wind stream;
- and the zero-damage backstop **does not apply** — hurricane wind *is* turbine-damaging.

These sub-perils also **share a year and a calendar instant** (strongly positively correlated — the *opposite* of
the near-independence that makes convective wind clean), so even sampling them as *independent* streams would
**understate** the joint tail (scattering co-occurring losses across different simulated years).

**Two valid disciplines (decide at hurricane-build time):**
1. **Partition the event sets** — attribute TC-spawned tornadoes to the hurricane parent and **exclude them from
   the inland-convective tornado catalog**; route TC straight-line wind to hurricane, not strong wind. Then
   disjointness + independent sampling are restored.
2. **Bind correlated sub-perils to one parent event** — the methodology's catalog contract links sub-perils of a
   single parent event via a shared **event/family identifier** so they fire **together** in a simulated year,
   preserving correlation; metrics off the joint. `[REF concept — confirm the exact contract field against the
   methodology source; the named field was not verifiable verbatim in our copy.]`

> **Forward-compatibility action now `[OURS, DD-WN-9]`:** flag the V1 tornado catalog as **inland-convective only
> — excludes TC-associated tornadoes**, so the hurricane build can partition cleanly. (This is the single most
> important double-counting trap on the roadmap.)

---

## 8. The recursive rule — same operation at every level  `[REF]`

The combine is the **same** at three nesting levels, because it rests on two distribution-level identities that
hold at any depth: **(i)** expectation is linear (EAL composes by summation, sub-peril → peril → Total Loss);
**(ii)** quantiles are not linear (every tail metric must be read off the single combined sampled distribution).

```text
  sub-peril level   tornado ⊕ strong wind          → one CONVECTIVE-WIND distribution      (M4, this build)
  peril level       convective wind ⊕ hail ⊕ wildfire → one TOTAL-LOSS distribution         (Overall-Risk tier)
  portfolio level   asset ⊕ asset (shared events)   → one PORTFOLIO distribution            (deferred, copula)
```

`[REF]` *"combine event catalogs, then compute"* is stated for cross-year/cross-asset aggregation — the same rule.
The **one non-trivial condition**: independent per-stream sampling is correct only for **disjoint** sets that are
**also near-independent**; genuinely **correlated** co-occurring streams (hurricane sub-perils; multiple farms
under one derecho — `DD-WN-12`'s portfolio-correlation trigger) must inject the dependence into the joint sampling
(shared year/event id) or the tail is understated. **EAL is unaffected by dependence; only the tail is sensitive.**

> **V1 scope `[OURS]`:** convective wind treats its two sub-perils as **disjoint and independent** — valid (§4) and
> safe (§6). Cross-peril Total Loss will inherit the same recursion under a **V1 independence assumption** (a
> defensible default, **stated not assumed-away**); cross-peril correlation (a shared climate driver) is the
> documented deferred upgrade.

---

## 9. Settled vs ours — and what may need a Drive-doc update

| Claim | Status | Source / note |
|---|---|---|
| EAL additive (gross/uncapped); tail metrics not additive | `[REF]` | Drive methodology + risk-metrics reference |
| Combine by sampling into one distribution; metrics off the joint; EAL attribution split | `[REF]` | methodology engine + Brazos Ridge example |
| Cap/deductible/limit breaks EAL additivity → read off the joint | `[REF]` | risk-metrics reference |
| Double-counting = same physical event in two streams; needs disjoint sets | `[REF concept]` | methodology (secondary-perils / shared-event) |
| Tornado ⊥ strong wind **by data product** (ASCE non-tornadic vs SPC Tornado) | `[OURS]` | our sourcing choice; re-audit if the strong-wind source changes |
| "Safe because strong-wind damage ≈ 0" backstop | `[OURS]` | build-specific; not the primary defense |
| Hurricane partition / shared-event-id discipline | `[REF concept] + [OURS plan]` | confirm the exact catalog-contract field |
| Recursive rule at sub-peril / peril / portfolio levels | `[REF]` | methodology, stated for cross-year/asset |

> **Governance note (Drive docs = source of truth):** the `[OURS]` rows are build assumptions, not yet in the
> Drive methodology. If any becomes load-bearing platform doctrine — especially **the explicit "EAL adds /
> tail doesn't, for sub-perils" statement** and **the disjointness-partition discipline for overlapping perils
> (hurricane)** — propose adding it to `hazard_asset_loss_distribution_methodology.docx` **first**, then encode it.
> These are the strongest candidates for a Drive-doc update.

---

*Next: this graduates the aggregation reasoning into [`plans/convective_wind/m4_loss_metrics.md`](../../../plans/convective_wind/m4_loss_metrics.md)
(the combine spec + the EAL-additive/tail-not + disjointness statements, already added in the reference-alignment
pass) and the `DD-WN-12/13/14/15` decisions. The hurricane trap (§7) is carried on `DD-WN-9`. Build M4 only once
this reads true.*
