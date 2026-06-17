# 02 — The Three Coupling Buckets, and Where Wind Sits

*An educational deep-dive, written for a reader new to the domain. The single question it answers: **how does
a hazard *reach* an asset, and what does the asset *read*?** Get that right and everything downstream (the
frequency math, the spatial factor, the Monte-Carlo regime) follows. Wind is the perfect teacher here,
because convective wind's two sub-perils sit in **two different coupling buckets** — and the separate,
deferred hurricane peril sits in the third — so by the end you will see the whole platform's coupling map,
and "field-intensity vs the rest" will finally click. A discussion doc, not a plan; it settles *how the
coupling works* before the M2 plans (`docs/plans/convective_wind/m2_coupling.md`).*

> Siblings: [`01` scope & taxonomy](01_scope_and_sub_peril_taxonomy.md) · [`03` hazard definition](03_hazard_definition_and_thresholds.md).
> The platform-canonical coupling source is [`P1` — *standard interface, not standard physics*](../../../principles/hazard_asset_specificity.md);
> the original deep-dive is [`../gpt/03`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md).

---

## TL;DR (the whole argument in one screen)

1. **Every peril in this platform is dispatched to exactly one of three coupling types**, each with its own
   math, behind **one standard interface** to the shared engine. Coupling = *how the hazard reaches the asset*.
2. The three are: **(1) areal hit-or-miss** — a footprint covers you or it doesn't (Bernoulli (a single hit/miss coin flip) × Minkowski);
   **(2) field-intensity** — you are *always* inside a continuous field and read your local value, which
   differs each event (sample the field); **(3) site-conditioned** — a simulator has *already* pre-baked your
   site's frequency + intensity, you just look it up (profile-assembly).
3. The reference gives the *physical* root of these as a **footprint taxonomy**: *point / narrow path / broad
   swath / regional field.* **Narrow path → areal** (tornado). **Broad swath → site-conditioned** (strong
   wind). **Regional field → field-intensity** (hurricane).
4. **Convective wind's two sub-perils land in two buckets, and the separate hurricane peril in the third** —
   that is the "sub-perils matter" payoff. Convective wind (tornado + strong wind) tours **two already-built
   buckets** (hail's areal, wildfire's site-conditioned); only the separate, deferred hurricane peril needs
   the third (field-intensity), which is why it is deferred.
5. **The old repo got the coupling *wrong* for strong wind** — it applied a hail-style `spatial_factor`
   (`F/A`) to a broad-swath peril that has no "miss." That single confusion is part of why its strong-wind
   numbers were incoherent. The right call: strong wind is **site-conditioned** (no hit-or-miss).
6. **The ASCE 7-22 RP gust surface is pre-integrated hazard** — exactly like FSim's BP+FLP for wildfire — so
   strong wind reuses wildfire's M2 machinery verbatim ([learning-09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).

---

## 1. Coupling, in one sentence — and why it is the load-bearing choice

A hazard model has four moving parts: **how often** events happen (frequency), **how big** they are
(severity/magnitude), **how the hazard reaches the asset** (coupling), and **how the asset responds** (the
damage curve). Coupling is the one people skip — and it is the one the old model got wrong. It is the bridge
between "an event happened *somewhere*" and "*this asset* experienced an intensity of X."

> **The whole question:** *given that the hazard occurred, how does its intensity arrive at this specific
> asset's location?* The answer is one of exactly three shapes. Pick the wrong shape and the frequency math,
> the spatial factor, and the variance are all wrong — even if the curve and the severity distribution are
> perfect.

The deciding test (the dual test, [P1](../../../principles/hazard_asset_specificity.md)) is the same one we used
to split **convective wind into its two sub-perils** in [`01`](01_scope_and_sub_peril_taxonomy.md): does the
peril have a distinct **footprint geometry** and a distinct **data/magnitude metric**? Footprint is the part
that drives coupling.

---

## 2. The reference's footprint taxonomy — the physical root

The Hazard_Data_Reference defines each hazard by five properties; one of them is **spatial footprint**, with
this exact four-way taxonomy (reference, verbatim):

> **"Point / narrow path / broad swath / regional field."**

It then says footprint *"determines spatial and temporal correlation: which assets are affected together, for
how long, and with what lag across a distributed system."* That sentence is the entire reason coupling
matters — footprint decides **which assets are hit together** (correlation), which decides the *portfolio*
tail. Map the four footprint shapes onto our three coupling buckets:

```text
  REFERENCE FOOTPRINT          →   PLATFORM COUPLING BUCKET        →  EXAMPLE PERIL
  ─────────────────────────────────────────────────────────────────────────────────
  point / narrow path          →   (1) AREAL HIT-OR-MISS           →  HAIL, TORNADO
       "covers you or misses"          Bernoulli × Minkowski

  regional field               →   (2) FIELD-INTENSITY             →  HURRICANE
       "always inside the field"       sample the field per event       (earthquake, snow)

  broad swath                  →   (3) SITE-CONDITIONED            →  WILDFIRE, STRONG WIND
       "pre-baked per-site profile"     profile-assembly (read it)       (flood)
  ─────────────────────────────────────────────────────────────────────────────────
```

The non-wind perils in parentheses (earthquake / snow / ice / flood) are **illustrative, bucket assignment TBD
per the dual test** — shown to give the shape intuition, not as committed classifications.

The subtlety worth flagging up front: **broad swath maps to site-conditioned only because of how the *data*
arrives.** A broad outflow physically *is* a field over space — but for strong wind we never get a per-event
field; we get a **pre-integrated return-period surface** (ASCE) that has already aggregated all events into a
per-site profile. So the *operational* bucket is site-conditioned. Footprint sets the physics; **how the data
arrives** sets which machinery we use. Hold that thought — it is the whole strong-wind story (§6).

---

## 3. Bucket 1 — Areal hit-or-miss ("a footprint covers you, or it doesn't")

**The intuition.** An event has a finite footprint — a hailstorm swath, a tornado path. It lands *somewhere*
on the landscape. Your asset is either **under the footprint (a hit) or not (a miss)**. There is no
"partially exposed" in the spatial sense: a hit means the asset gets the event's full conditional intensity;
a miss means **nothing happens to it** ($0 loss). It is a coin flip — Bernoulli — whose probability depends on
how big the footprint is relative to the region it could land in.

**The math (plain).** The hit probability is **not** the naive ratio of footprint area to region area
(`F/A`). Two shapes overlap if their *centers* come within a combined reach of each other, so the correct
probability uses the **Minkowski sum** of the two convex shapes:

```text
  p_hit = (√F + √s)² / A            F = footprint area, s = asset extent, A = collection region
```

The old model used the naive `F/A` and under-counted the hit probability **1.3×–7×** ([P1](../../../principles/hazard_asset_specificity.md),
[hazard_math/01](../../../../Learning/ML-DL/InfraSure_related/hazard_math/01_bernoulli_hit_miss_model.md)). The
asset's event rate is then built by **Poisson thinning** — i.e. take the regional event rate and keep only the
fraction of events that actually land on the asset (thinning a Poisson process by `p_hit` again gives a Poisson
process): `λ_asset = λ_collection · E[p_hit]` — the regional rate, scaled down by the chance any given event
actually lands on the asset.

**The key newcomer point — keep the bimodality.** A hit is *full conditional loss*; a miss is *$0*. The
distribution of annual loss is therefore **spiky**: mostly zeros, occasionally a big jump. That bimodal
variance is exactly what the old model destroyed when it stored `damage% × value × spatial_factor` — the
*expected* loss averaged over the coin flip, not a *realized* sample. (More on that in §7.)

**A region nuance ([learning-06](../../../learning_logs/06_collection_region_size_cancels.md)):** when
`λ_asset = λ_collection · p_hit` is computed over *one* region, the region's size **cancels** — a bigger
region has proportionally more events *and* a proportionally smaller hit probability. So you choose the region
for *homogeneity and data consistency*, never to tune the magnitude. (This matters for tornado: pick a region
where the strike density is roughly uniform.)

**Reference perils:** hail (built), **tornado**, fire perimeter.

---

## 4. Bucket 2 — Field-intensity ("you are always inside the field; read your local value")

**The intuition.** Some events do not "land somewhere and maybe miss you" — they produce a **continuous
intensity field over a large area**, and your asset is **always inside it**. A hurricane does not flip a coin
about whether it hits your site; if it is in your region, your site experiences *some* wind speed — the
question is never *did it hit*, it is **what value did the field have at my location.** And that value
**differs from event to event** (a near-eyewall pass vs a distant brush are both "hits" with very different
local intensities).

**The math (plain).** There is no hit probability to thin — `p_hit = 1` inside the field
([hazard_math/01](../../../../Learning/ML-DL/InfraSure_related/hazard_math/01_bernoulli_hit_miss_model.md) caveat).
Instead you **sample the field**: per event, build the intensity surface (for hurricane, a **Holland
parametric wind field along the storm track → a swath grid**), then read the value at each asset's location.
Because one event covers many assets, **the losses are correlated across the portfolio** — and that
correlation is what makes the *portfolio* tail far heavier than the sum of independent single-asset tails.

**Why this is the genuinely unbuilt bucket — and why EVT lives here.** A single asset's physical damage is
*bounded* (you cannot lose more than its value), so a single-site severity has a short, bounded tail — EVT
on one asset earns little. But at **portfolio scale**, a field-intensity event piles correlated losses
together, and the field's *spatial* tail (how extreme the peak field value can get) must be **extrapolated**
beyond the observed record. That is where **EVT becomes load-bearing**
([hazard_math/05](../../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)).
Field-intensity is the only bucket we have **not** built — which is exactly why the separate hurricane peril
(the field-intensity peril, *not* a convective-wind sub-peril) is deferred.

**Reference perils:** **hurricane** / cyclone (Holland field), earthquake, snow, ice load.

---

## 5. Bucket 3 — Site-conditioned ("a simulator already pre-baked your site's profile; look it up")

**The intuition.** Sometimes an upstream authority has **already done the hard part for you.** Instead of an
event set you must spatially couple, you are handed a **pre-integrated per-site profile**: a single
annualized frequency + a conditional-intensity distribution that *already aggregates over all events/seasons*
at that exact location. There is **no spatial hit-or-miss** to compute, no field to sample per event — your
asset just **reads its own local profile.** The whole stochastic event set was integrated upstream.

**The math (plain) — M1 becomes profile-assembly, not event-extraction.** Because the integration already
happened, M1's job is to *read* the rate directly and declare the process — **no λ-fit from a short record,
no dispersion test, no `λ_collection · p` spatial factor** (the dispersion is *structural*, baked inside the
simulator). For wildfire: `λ = −ln(1−BP)` straight off the burn-probability raster, then the flame-length
histogram is the conditional severity. This is the lesson of
[learning-09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md): *classify the hazard by **how
its data arrives** before choosing M1's machinery — a probability/return-period means profile-assembly; a
count/observation series means extraction.*

**M2 is therefore *thin*** — and that thinness is *correct*, not a shortcut. Most of the "coupling" happened
upstream in the simulator; M2's job is the honest handoff (occurrence × conditional intensity) plus small
local corrections (e.g. wildfire's "oozing" — read the surrounding-fuel ring where the asset's own pixel is a
developed hole, [learning-08](../../../learning_logs/08_oozing_developed_pixels.md)). We *document* the
thinness rather than manufacture coupling that isn't there.

**The honesty cost (not a free lunch).** Pre-integration means you **inherit the upstream authority's
assumptions, vintage, and exposure conventions** and cannot re-test them. For wildfire, that is FSim's fuel
vintage; for strong wind, it will be ASCE/NIST's terrain-exposure reference (Exposure C) and RP statistics.
The uncertainty did not vanish — it **moved upstream**. Honesty = saying so.

**Reference perils:** wildfire (FSim BP+FLP, built), flood depth-return grids, **strong wind** (ASCE RP gust
surface).

---

## 6. Where each convective-wind sub-peril sits — and *why* (plus the separate hurricane peril)

Now the payoff. Convective wind's two sub-perils land in two different buckets, and the separate, deferred
hurricane peril in the third — this is *why* "sub-perils matter" is not a slogan.

### Tornado → Bucket 1 (areal hit-or-miss)

A tornado is the reference's **narrow path** footprint: *"narrow, intense, catastrophic path. **Low strike
probability at any point, but near-total loss within the path.**"* That is the textbook hit-or-miss signature —
a footprint that either covers the asset (near-total loss) or misses it ($0). So tornado **reuses hail's
Minkowski coupling**, with one twist: a tornado path is a **thin rectangle** (length ≫ width — extreme aspect
ratio), so the Minkowski sum specializes to a **path-aware** form:

```text
  hail (compact swath):    p_hit = (√F + √s)² / A
  tornado (thin path):     p_hit ≈ (L + a)(w + a) / A   →  dominated by  L × a
                            L = path length, w = path width (small), a = asset extent
```

The reference makes the consequence explicit: *"Risk ≈ annual strike probability (path-area density) ×
conditional damage at the EF level"* and *"a point lookup understates linear assets — a long transmission line
has many times the strike exposure of a single substation."* For a wind farm this is exactly why the
**per-turbine USWTDB point cloud** matters: a long line of turbines presents far more strike length than a
single point would (§8 of [`01`](01_scope_and_sub_peril_taxonomy.md)). EF-class footprint areas (the typical
damage-path plan area `F` for a tornado of each class, km²) are reusable directly from the old repo
(`EF0=0.5 … EF5=20.0 km²`) — these are the `F` that feeds `p_hit` — as are the F-scale midpoints.

Because strike probability at any point is **tiny**, tornado is the **sparse Monte-Carlo regime**: most
simulated years are empty, the near tail can be barely populated, and VaR can *floor to $0* at feasible
sample sizes. That is precisely the situation [learning-10](../../../learning_logs/10_monte_carlo_effective_sample_size.md)
describes — so tornado **must** report TVaR alongside VaR and quote a standard error. (The old repo's F-scale
tornado model already encodes this: `is_floored=True` when `λ_asset · RP ≤ 1`, with TVaR as the remedy.)

### Strong / straight-line wind → Bucket 3 (site-conditioned)

A derecho/downburst/thunderstorm-outflow is the reference's **broad swath** footprint: *"broad-area gusts…
affects whole regions and every asset."* The reference is blunt about the coupling consequence
(verbatim): *"Strong wind [W] is broad-area and correlated across a portfolio… Don't apply one spatial logic
to both — [W] drives correlated portfolio loss, [T] drives rare severe single-asset loss."* There is **no
"miss"** — a broad swath that reaches your region reaches your asset; the asset reads its **local gust**.

The operational reason it is *site-conditioned* (and not field-intensity) is **how the data arrives.** We do
not get a per-event swath field for strong wind; we get the **ASCE 7-22 design-wind map**, which the reference
describes exactly as a pre-integrated surface (verbatim): *"the maps embed the RP… the ASCE design maps
already contain a probabilistic RP analysis. Use the map RP surface as the hazard."* That is **structurally
identical to FSim's BP+FLP for wildfire** — an upstream authority (ASCE/NIST) has already integrated the
stochastic event set into a per-site return-period 3-s-gust surface. So:

- **strong-wind M1 = profile-assembly** ([learning-09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) —
  read the RP→gust relationship directly; the several MRI maps (RC I 300-yr / II 700-yr / III 1,700-yr / IV
  3,000-yr; Appendix F out to ~10⁴–10⁶-yr) **are** the pre-computed return-level curve;
- **strong-wind M2 = wildfire's site-conditioned machinery, reused** — thin coupling, honest handoff, no
  spatial factor;
- and because strong wind is **high-frequency**, its Monte-Carlo tail is **well-populated** — the *easy*
  regime, the opposite of tornado.

*(Alternative path, also allowed by the reference: instead of the ASCE surface, fit a catalog — Poisson
occurrence + GPD gust severity to the SPC/Storm-Events record, bias-corrected. That is the **extraction**
branch of learning-09. Strong wind can be built either way; the ASCE surface is the faster, pre-integrated
path — see [`03`](03_hazard_definition_and_thresholds.md).)*

### Site-conditioned vs field-intensity — the one difference that matters

Both are broad-area with no hit-or-miss — so what separates them? **WHEN the spatial integration happens.**
**Site-conditioned**: an upstream authority ALREADY integrated every event into one fixed per-site profile;
the Monte Carlo just resamples that same profile every year — no event ever produces a new spatial pattern.
**Field-intensity**: each simulated event BUILDS a fresh intensity surface and the asset reads a different
local value every time — which is exactly what couples many assets together in one event (portfolio
correlation), and is why we have not built it. Site-conditioned = pre-baked, look it up; field-intensity =
built fresh per event, sample it.

### Hurricane (a SEPARATE, deferred peril) → Bucket 2 (field-intensity)

Hurricane is **not** a convective-wind sub-peril — it is a **separate peril**, shown here only because it
occupies the third coupling bucket and is the next field-intensity build. A hurricane is the reference's
**regional field** footprint, and it is scored buildable on every axis (public
stochastic catalogs STORM/RAFT + the Holland wind-field method) — *unlike* tornado/strong wind, which have **no
public stochastic catalog.** But it is the **genuinely unbuilt bucket**: a hurricane is always inside its own
wind field, so there is no hit-or-miss to thin, and unlike strong wind we do *not* get a pre-integrated
design surface to read — we **build a real per-event continuous field** (Holland) along each track and read it
at each asset. That is where **portfolio correlation + EVT become load-bearing** (§4). So hurricane is named,
fenced, and deferred as the **next field-intensity build** — not bolted onto V1.

---

## 7. The prior-art evidence — the old repo got strong-wind coupling wrong

This is not hindsight; the old `hazard_analysis` repo's own self-audit proves it. Two distinct failures, both
rooted in mis-coupling strong wind:

**(a) It applied a hail-style spatial factor to a broad-swath peril.** The old strong-wind path used
`spatial_factor = F/A` (footprint ÷ collection region) and `λ_asset = λ_collection × spatial_factor` — the
**areal hit-or-miss** machinery — for a peril that has **no miss.** Strong wind is broad-swath / correlated;
treating it as hit-or-miss is a category error. The reference's own warning (*"don't apply one spatial logic
to both"*) is exactly the line the old repo crossed.

**(b) The Method-0 expected-loss shortcut, with its ~12× error.** Worse, the old code stored each event's
contribution as `damage% × value × spatial_factor` **deterministically per event**, then fit a distribution
to the annual sums. By the Law of Total Variance (the total spread of annual loss = the spread WITHIN the hit
case + the spread BETWEEN hit and miss; Method 0 keeps the first and throws away the second, the dominant one)
this preserves the *mean* (EAL) but discards the dominant hit/miss variance — so it **understated VaR₉₉ by
~12×** for strong wind specifically. The old repo's own
worked example (`strong-wind-var-worked-example.md`) is the proof:

| Metric | Method 0 (fitted, the bug) | Method 3 (correct, compound-Poisson) |
|---|---|---|
| EAL | $4.98M | $4.83M *(agree — linearity of expectation)* |
| **VaR₉₉ ≡ PML₁₀₀** | **$8.99M** | **$108.94M** *(~12× higher — the bug)* |
| TVaR₉₉ | n/a | $141.19M |

And it fit PML (OEP — occurrence exceedance probability, the worst SINGLE event in a year) and VaR (AEP —
aggregate exceedance probability, the total of ALL events in a year) as **two independent statistical
objects**, producing the impossible
**~175×** internal ratio ($547M VaR vs $3.1M PML₅₀₀) — "mathematically impossible under any single coherent
framework." Only EAL survived, because expectation is linear and the coupling/variance error cancels in the
mean. The fix is [P3](../../../principles/basics_spot_on.md)'s doctrine: **one coherent compound-Poisson/NegBin
Monte-Carlo loss distribution, every metric read off it, never the expected-loss collapse** — and **the right
coupling bucket per sub-peril** (strong wind = site-conditioned; tornado = areal). This is the cardinal lesson
the wind M4 doc must name explicitly. *(See the M4 plan; metrics always shown as % of TIV alongside dollars.)*

> The two failures compound: wrong coupling **and** wrong aggregation. V1 fixes both — right bucket per
> sub-peril, one sampled distribution for the metrics.

---

## 8. The whole-platform coupling map (so "field-intensity vs the rest" clicks)

Step back and see all the perils at once. This is the map the platform is built on — and wind is the peril
that fills in the gaps:

```text
                         AREAL HIT-OR-MISS        SITE-CONDITIONED          FIELD-INTENSITY
                         (bucket 1)               (bucket 3)                (bucket 2)
                         ─────────────────        ─────────────────         ─────────────────
  footprint              point / narrow path      broad swath               regional field
  "the asset…"           is hit or missed         reads its pre-baked        is always inside,
                                                   local profile             reads local value/event
  spatial factor         YES  (Minkowski p_hit)   NO  (none — pre-integrated) NO  (p=1 inside field)
  M1 machinery           extract + thin           profile-assembly           per-event field build
  correlation            ~independent point-to-pt structural (upstream)      strong (one event, many assets)
  MC regime              sparse if rare           well-populated             portfolio-correlated
  EVT load-bearing?      at the severity tail     inherited (upstream)       YES (portfolio + field tail)

  BUILT PERILS           HAIL ✅                   WILDFIRE ✅                 — (none yet)
  CONVECTIVE-WIND        TORNADO [T]               STRONG WIND [W]            —
    SUB-PERILS           (one peril, two sub-perils: tornado + strong wind)
  SEPARATE WIND PERIL    —                         —                          HURRICANE (separate, deferred)
  other examples         fire perimeter           flood depth-RP grids       earthquake, snow, ice
```

Read the bottom rows: **hail proved bucket 1, wildfire proved bucket 3, and bucket 2 is empty.**
Convective wind's two sub-perils reuse the two proven buckets (tornado → bucket 1, strong wind → bucket 3)
and **name the separate hurricane peril as the build that finally fills bucket 2.** That is the elegance of
doing wind third — it tours the platform's whole coupling map, and it tells us *exactly* what is left unbuilt
and where the new machinery (field generation + portfolio EVT) will have to go.

> **DECISION (graduates to `DD-WN-*`).** Commit the per-sub-peril coupling assignment: **tornado =
> areal hit-or-miss (reuse hail's Minkowski, path-aware thin-rectangle)** · **strong wind = site-conditioned
> (reuse wildfire's M2; ASCE RP surface as pre-integrated hazard)** · **the separate, deferred hurricane peril
> = field-intensity.** The shared compound-Poisson/NegBin engine is **untouched** in all three. The two
> convective sub-perils are combined **only** by co-sampling both event streams into **one** annual-loss
> distribution — all tail metrics (VaR / PML / TVaR) read off that **one** combined distribution, never summed
> per-sub-peril (EAL is additive across the disjoint streams, but the tail metrics are not). *(Recommended:
> yes — reference §footprint-taxonomy + the [W]/[T] correlation note + the old repo's mis-coupling self-audit
> all converge.)*

---

*Next: turn the committed assignments into `docs/plans/convective_wind/m2_coupling.md` (the plan-of-record — the
path-aware Minkowski for tornado, the thin site-conditioned handoff for strong wind, the per-turbine USWTDB
note, the field-intensity contrast for the deferred hurricane). The authored hazard definition these couple
to is in [`03`](03_hazard_definition_and_thresholds.md).*
