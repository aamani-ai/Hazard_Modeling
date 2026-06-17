# 00 — Hazard Definition (layer-0, the active plan) · *the layer we never needed before*

*For hail and wildfire the hazard **event** came pre-defined by the data product. For wind it does **not** —
no single product hands us "the event," so **we** must author the definition, quantitatively, anchored in
engineering and meteorological standards. That authoring is its own layer, and it sits **above M0**. This doc
is the centerpiece: it defines the convective-wind hazard (one peril, two sub-perils) from first principles and
teaches the coupling taxonomy that decides where each convective-wind sub-peril plugs in. Written for a reader
new to the domain — terms defined on first use.*

**Where this sits:** **layer-0 (hazard definition)** → [M0 (input data)](m0_input_data.md) →
[M1 (catalog)](m1_catalog.md) → [M2 (coupling)](m2_coupling.md) → [M3 (damage)](m3_damage.md) →
[M4 (loss & metrics)](m4_loss_metrics.md). Built for **two sites** (Traverse, OK — high/proving ·
Shepherds Flat, OR — low/baseline). **How it works (the exploration):**
[discussion/convective_wind/03_hazard_definition_and_thresholds](../../extra/discussion/convective_wind/03_hazard_definition_and_thresholds.md)
(the standards reasoning) and
[discussion/convective_wind/02_coupling_buckets_and_wind](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)
(the coupling deep-dive).

---

## Why this layer exists (read this first)

The two perils before wind never asked us to *define* the hazard event — the **data product already had**:

| Peril | The data product | What it pre-defined for us |
|---|---|---|
| Hail | **MRMS / MESH** | "severe hail" = a **≥ 1-inch** maximum-estimated-hail-size footprint — the event, the threshold, the magnitude metric, all baked in. |
| Wildfire | **FSim (BP + FLP)** | "fire occurrence + flame-length classes" — the event *and* its conditional severity, pre-integrated over ≥20,000 simulated seasons. We just read the profile. |
| **Wind** | **— none —** | **No single product defines the wind event.** SPC gives reports, NOAA gives episodes, ASCE gives a design surface, IEC gives turbine ratings — but *we* must say what counts as an event, at what threshold, on what magnitude scale, bounded where. |

This is the first time the question *"what is one event, and how strong is it?"* lands on us rather than on the
data vendor. Per [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md), the very first
move in any peril is to **classify the hazard by how its data arrives** before reaching for catalog machinery
— and wind's answer is *"it arrives as several partial sources, none of which is the event definition."* So we
author the definition once, here, anchored in standards (not intuition), and *then* M0 collects evidence and
M1 builds the catalog against it. Authoring-not-inheriting is the whole reason layer-0 is a layer.

> **The honest framing.** Defining the event ourselves is a *responsibility*, not a liberty. The definition
> must be **defensible** — every threshold traces to a published engineering or meteorological standard, every
> number carries its source, and where a value is the old repo's or to-be-confirmed-at-build, we say so. This
> is *basics-spot-on* applied to the hazard's own definition. (Decisions → [DD-WN-1..](decisions.md);
> assumptions → [AWN-1..](assumptions.md).)

---

## The hazard, defined quantitatively

### 1. The magnitude observable — the 3-second peak gust

Every wind sub-peril shares **one** physical intensity measure: the **3-second peak gust wind speed** — the
fastest wind sustained over a 3-second window. `[REF]` The Hazard Data Reference is explicit: *"3-second gust
speed is the **universal metric** — map it to a wind-load / fragility curve per asset."* This is the *causal*
variable the damage curve is built around (the structural load on a turbine scales with gust², not with a
daily average), so it is the single number layer-0 commits to.

- **Standard measurement basis:** the ASCE basic-wind surface defines it as the 3-s gust **at 33 ft (10 m),
  Exposure C** (open terrain). Hub-height and terrain (Exposure B/C/D) corrections move the site value off
  that reference — an M0/M2 adjustment, flagged as an assumption ([AWN-*](assumptions.md)).
- **Why not sustained wind:** sustained (1-min / 10-min mean) wind is the *resource* metric (generation); the
  *damage* metric is the peak gust. The old repo conflated the two (it routed "gust" vs "sustained" magnitude
  types to **different damage curves** — a hack we do **not** replicate). One observable, one curve.

### 2. The event / catalog threshold μ — what counts as an event (for λ, the annual event frequency)

A "wind event" is wind that *crosses a defined severity line*. The line differs by sub-peril, and it comes
from the meteorological standard, not from the asset:

| Sub-peril | Event threshold μ | Source | In SI |
|---|---|---|---|
| **Strong / straight-line wind** | **≥ 58 mph** 3-s gust | **NWS severe-thunderstorm criterion** (the reference's *"convective wind severe = ≥ 58 mph"*) | **≈ 25.9 m/s** (old repo: 25.92 m/s, *"NRI/NOAA Severe"*) |
| **Tornado** | **EF0 ≥ 65 mph** 3-s gust | **Enhanced Fujita (EF) scale** — operational since 2007 (replaced the F scale) | ≈ 29 m/s (old repo: 29.0 m/s, *"EF0 Start"*) |

`[REF]` The EF scale's bins (3-s gust, damage-inferred), verbatim from the reference:

| EF | 3-s gust (mph) | Note |
|---|---|---|
| EF0 | 65 – 85 | weakest rated |
| EF1 | 86 – 110 | |
| EF2 | 111 – 135 | ASCE Ch 32 tornado design covers **~EF2 and below** |
| EF3 | 136 – 165 | |
| EF4 | 166 – 200 | |
| EF5 | **> 200** | the catastrophic tail |

The EF rating is **damage-inferred, not measured** — 3-s gust is estimated from **28 damage indicators × 8
degrees of damage**. Carry the honest caveat: EF is *biased low where there is little to damage* (rural/open
land), so historical EF severity at our two **rural** sites is likely understated — an [AWN-*](assumptions.md)
flag for the catalog fit.

### 3. The physical upper bound L — where the magnitude distribution must end

A magnitude distribution that runs to infinity is unphysical for a single site. We truncate at a **physical
upper bound L**:

- **L ≈ 113 m/s (~253 mph)** — a physical truncation **above** the open-ended EF5 floor (EF5 is **> 200**
  mph; 113 m/s is our chosen ceiling, corroborated by the old-repo F5 midpoint 111.8 m/s) — the
  settled-framing value (the old repo's `HAZARD_LIMITS`), an [AWN-*](assumptions.md) (assumed, not from the
  reference).
  > **Divergence reconciled (settled, with a revisit note):** the old repo placed **113 m/s as its *Strong-Wind*
  > limit** (*"Cyclone Olivia Gust"*) and gave **Tornado L = 145 m/s** (*"Moore 1999 Doppler Max"* — an
  > *observed* Doppler max, not a damage-inferred ceiling). **V1 adopts L = 113 m/s as the tornado/magnitude
  > bound** (the EF5 damage ceiling), and the old F5 midpoint **111.8 m/s** corroborates it. This is a logged
  > decision ([DD-WN-8](decisions.md)) with an [AWN-*](assumptions.md) revisit trigger — **settled, not still
  > open**: the value is chosen; the revisit note is the only residual.

### 4. The severity model — per-sub-peril (tornado = bounded GPD; strong wind = Gumbel/exponential)

Above μ, event gust magnitude is a fitted continuous tail — **extreme-value theory applied to the
*intensity*** — exactly what
[hazard_math note 05](../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)
recommends: *prefer EVT on magnitude/intensity (then map the rare intensity through the damage curve), because
hazard observations are more available than asset-loss data, and one hazard tail feeds many asset curves.* **The
tail shape differs by sub-peril** — this is *not* one wind-wide severity rule:

```
   ξ > 0   heavy / unbounded tail
   ξ = 0   exponential / Gumbel        ← STRONG WIND sits here (log-linear ASCE RP, R² ≈ 0.999), capped at L
   ξ < 0   BOUNDED — a finite upper endpoint   ← TORNADO sits here (reaches the EF5 ceiling L)
```

**Tornado — a bounded GPD (ξ < 0).** A tornado's gust above μ is a **Generalized Pareto Distribution (GPD)**:
left-anchored at μ, **right-bounded at L** (no probability beyond the physical EF5 ceiling). Note 05 is
explicit: *"do not assume catastrophe loss always has ξ > 0; a single asset's physical damage is bounded."* A
truncation at L forces **ξ < 0**. The old repo's `mag_sim` gives the reusable closed form (left-anchor μ,
right-bound L, mean-constrained): `ξ = (μ_mean − μ)/(μ_mean − L)` (negative since `μ_mean − L < 0` → short upper
tail), `σ = −ξ(L − μ)`, evaluated as `genpareto(c=ξ, loc=μ, scale=σ)` on support `[μ, L]` — where **μ_mean** is
the *mean event gust* (the average gust over events above threshold μ; by construction it lies between μ and the
ceiling L, so `μ_mean − L < 0`, forcing **ξ < 0** — a bounded tail).

**Strong wind — Gumbel / light-exponential (ξ ≈ 0), capped at L.** Strong wind does **not** reach the L ceiling
in practice; the build found the **ASCE return-level curve is log-linear (R² ≈ 0.999)**, i.e. gust grows
linearly in log-return-period — a **Gumbel / exponential** tail (ξ ≈ 0), physically capped at L rather than
reaching it. So **do not state ξ < 0 as a wind-wide severity rule** — that is the tornado form. Strong wind is
read off the ASCE RP surface (§5) as a Gumbel tail; the bounded-GPD analytic solve above is reserved for
tornado.

> **Reuse the good part, reject the bad part (basics-spot-on).** We keep the bounded-GPD *analytic solve*. We
> **reject** the old repo's habit of **back-solving μ_mean from a target EAL** (it reverse-engineered the
> magnitude distribution from an NRI loss number rather than fitting the gust tail). The new build fits the
> GPD to the **observed SPC / Storm-Events gust record** — bias-corrected for population — or reads the ASCE
> RP surface (below). The tail is *fit to gusts*, never to a desired answer. (Detail: [M1 plan](m1_catalog.md).)

This is also where wind **cashes in the continuous-severity thread**: unlike wildfire's 6 discrete FLP classes,
wind's magnitude is **continuous** (a real gust in m/s), so the severity distribution is genuinely a fitted
continuous tail, not a class histogram (cf.
[hazard_math note 03](../../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md)).

### 5. The ASCE 7-22 RP surface — the severity tail, *already fitted*

For **strong wind** there is a second route to the severity tail that requires no catalog fit at all. `[REF]`
The reference's linchpin sentence: *"the ASCE design wind-speed maps already contain a probabilistic
return-period analysis … use the map RP surface as the hazard."* The **ASCE 7-22 basic-wind map is a
pre-integrated return-period 3-s-gust surface** — ASCE/NIST already ran the probabilistic tail extrapolation
and baked it into the surface. Reading the map gives gust-by-return-period directly:

```
   ASCE 7-22 basic-wind map  →  3-s gust at each Mean Recurrence Interval (MRI = return period)
       Risk Category I    300-yr        Risk Category III   1,700-yr
       Risk Category II   700-yr        Risk Category IV    3,000-yr
       Appendix F   extends the tail to ~10⁴ – 10⁶-yr   (performance-based / extreme tail)
```

**Risk Category** = ASCE's consequence-of-failure tier (II ordinary structures … IV essential facilities);
higher category = longer design return period. Which category a utility-scale turbine maps to (likely II) is
an M0/assumptions call.

Reading several MRI maps = **sampling the EVT return-level curve at fixed exceedance probabilities**. The
RP→gust relationship *is* the pre-computed return-level curve of §4 — ASCE/NIST did the POT/GPD extrapolation
for us. The build found this surface is **log-linear (gust ∝ log-return-period, R² ≈ 0.999)** — i.e. a
**Gumbel / light-exponential** tail (ξ ≈ 0), capped at L, **not** a bounded GPD with ξ < 0 (that is tornado's
form, §4). This is **exactly the wildfire move** (FSim pre-integrated the seasons into BP+FLP) and is governed by
the same lesson: [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) — *if an upstream
simulator pre-integrated the stochastic set into an annualized probability / return-period field, M1 is
profile-assembly, not extraction.* Carry learning-09's caveat verbatim: **pre-integration is a borrow, not a
free lunch** — we inherit ASCE/NIST's assumptions, vintage, and the Exposure-C reference (terrain B/D adjust);
the uncertainty moved upstream, it did not vanish. (Tornado has a partial analogue: ASCE 7-22 **Chapter 32**
tornado maps are a pre-integrated RP surface too — but capped at **~EF2** and only for Risk Category III/IV, so
they do not cover the catastrophic tornado tail. The catalog-fit path remains primary for tornado.)

---

## The two thresholds — keep them distinct (the part that trips newcomers)

There are **two** wind thresholds and they live in different layers. Conflating them is the classic error.

```
   METEOROLOGICAL EVENT THRESHOLD  μ              ASSET DAMAGE-ONSET THRESHOLD
   "what the catalog COUNTS"                       "where the damage curve LEAVES ZERO"
   → feeds the frequency λ (M1)                    → anchors the damage curve (M3)
   ─────────────────────────────                  ──────────────────────────────────
   Strong wind: NWS ≥ 58 mph ≈ 25.9 m/s            IEC 61400 survival / design wind speed
                (old repo: 25.92)
   Tornado:     EF0 ≥ 65 mph                        (far higher than 58 mph)
```

- **The meteorological threshold μ** is what makes something *an event we count* — it sets λ. A 60-mph gust
  *is* a severe-wind event by NWS criteria, and the catalog counts it.
- **The asset damage-onset threshold** is where a *turbine starts to suffer structural loss*. Modern
  utility-scale turbines are engineered to **IEC 61400** wind classes:

  | IEC class | Reference 10-min mean Vref | 50-yr extreme 3-s gust Ve50 ≈ 1.4·Vref |
  |---|---|---|
  | Class I | 50.0 m/s | ≈ 70 m/s |
  | Class II | 42.5 m/s | ≈ 60 m/s |
  | Class III | 37.5 m/s | ≈ 52 m/s |

  > **Source honesty:** IEC 61400, the Vref classes, and the EF5 ≈ 113 m/s ceiling come from the
  > **settled framing / old-repo `HAZARD_LIMITS`**, **not** from the Hazard Data Reference. The reference
  > supplies the 58-mph threshold, the EF bins, the 3-s-gust metric, and the ASCE RP surfaces; it only
  > instructs *"account for … the survival wind speed in the curve, not just the design speed"* without naming
  > IEC. The IEC numbers are an [AWN-*](assumptions.md) to confirm against the actual turbine model per site.

**The consequence — the damage curve is ANCHORED.** Because damage onset (IEC survival, ~52–70 m/s) is **far
above** the event threshold (58 mph ≈ 25.9 m/s, old repo: 25.92), **most "severe wind" barely scratches a turbine**:

```
   DR (damage ratio)
   1.0 ┤                                        ╭──────
       │                                     ╭──╯
       │                                  ╭──╯   ← rises steeply near IEC survival speed
   0.0 ┤━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
       └──┬──────────────────────────┬─────────┬────── 3-s gust
         μ=58 mph                  IEC survival   L
        DR(μ)≈0                    (onset)       (~113 m/s)
```

(`L ≈ 113 m/s` is a physical truncation **above** the open-ended EF5 floor — EF5 is **> 200** mph with no
upper limit, so 113 m/s is our **chosen** ceiling, corroborated by the old-repo F5 midpoint 111.8 m/s; an
[AWN-*](assumptions.md), assumed not from the reference.)

`DR(μ) ≈ 0` — the curve **leaves zero only near the IEC survival speed**. This is the reference's explicit
turbine mandate (*"for wind turbines, account for operational state (feathered vs operating) and the survival
wind speed in the curve, not just the design speed"*). **Operational state matters:** a *feathered* turbine
(blades pitched edge-on, parked) survives a far higher gust than one *operating* (blades broadside) — the
curve should reflect the survival configuration. This anchored, operational-state-aware curve is **net-new**
work; the old repo had no IEC-anchored turbine curve (it borrowed generic `Real Estate_*` curves). Detail:
[M3 plan](m3_damage.md) and
[hazard_math note 03](../../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md).

---

## A coupling-taxonomy primer (newcomer-friendly) — *how the hazard reaches the asset*

Defining "how strong" is half the job. The other half is **how the hazard reaches the asset** — the
*coupling*. The platform answers this with exactly **three coupling buckets** (the canonical table lives in
[principles/hazard_asset_specificity](../../principles/hazard_asset_specificity.md)). The deciding question is
always: *how does the hazard reach the asset, and what does the asset read?* The reference roots this in a
**footprint taxonomy** — *"point / narrow path / broad swath / regional field"* — and that footprint geometry
is what sorts each peril into a bucket.

| Bucket | Plain-language one-liner | Footprint | The asset reads… | Math |
|---|---|---|---|---|
| **1. Areal hit-or-miss** | "the footprint covers you, or it doesn't" | point / **narrow path** | full loss **if hit**, **$0 if missed** (bimodal) | Bernoulli × Minkowski `(√F+√s)²/A` |
| **2. Field-intensity** | "you're always inside the field; you read your local value, and it differs each event" | **regional field** | a continuous intensity value at your location, event-by-event | sample-and-weight the field |
| **3. Site-conditioned** | "a simulator already pre-baked your site's frequency + intensity; you just look it up" | **broad swath** (pre-integrated) | your own pre-integrated local profile (no hit-or-miss) | profile-assembly (read the per-site profile) |

*Legend (bucket 1 math):* **F** = event footprint area, **s** = asset extent, **A** = the collection region
the event could land in; **`(√F+√s)²/A`** = the chance the footprint covers the asset — see
[discussion/02 §3](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md) for the intuition.

### Where each sub-peril sits — and why

*The two **convective-wind sub-perils** are [T] tornado and [W] strong wind. Hurricane is a **separate, deferred
peril** (not a convective-wind sub-peril) — shown here only to mark where that separate peril's coupling bucket
would sit.*

```
   [T] TORNADO          narrow path    →  BUCKET 1  (areal hit-or-miss)   [built: reuse hail]
   [W] STRONG WIND      broad swath    →  BUCKET 3  (site-conditioned)    [built: reuse wildfire]
   HURRICANE (separate, deferred peril) regional field → BUCKET 2 (field-intensity) [DEFERRED — the unbuilt bucket]
```

- **Tornado → Bucket 1 (areal hit-or-miss).** A tornado is a **narrow, intense path**: *"low strike
  probability at any point, but near-total loss within the path."* That is the hit-or-miss signature — the
  asset is either inside the path (near-total loss) or outside it ($0). It **reuses hail's Minkowski coupling**
  with a **path-aware variant**: a tornado path is a *thin rectangle* (extreme aspect ratio), so the
  hit-geometry `(L+a)(w+a)` is dominated by **length × asset-extent**, not area — a long linear asset has many
  times the strike exposure of a point ([M2 plan](m2_coupling.md)). Tornado is **rare per site**, so its Monte
  Carlo is **sparse** — invoking
  [learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md) (effective sample size; report SE
  and TVaR alongside VaR, because a rare peril empties the near tail).
- **Strong / straight-line wind → Bucket 3 (site-conditioned).** A derecho (a long-lived, wide line of fast
  straight-line thunderstorm wind), downburst (a localized blast of air sinking out of a storm), or synoptic
  high wind (large-scale, non-thunderstorm pressure-gradient wind) is a **broad swath** — *"broad-area, so
  most/all of a portfolio is exposed simultaneously."* The asset
  is **not missed**; it simply reads its **local gust**. And the **ASCE RP surface is the pre-integrated
  profile** (§5) — so strong wind **reuses wildfire's site-conditioned M2 machinery**: no Minkowski, no spatial
  factor, just read the per-site return-level curve. Strong wind is **high-frequency**, so its Monte Carlo is
  **well-populated** (the Matrix analogue from wildfire). This is the *fastest path to a real number*, which is
  why it is built first.
- **Hurricane → Bucket 2 (field-intensity), DEFERRED — a separate peril, not a convective-wind sub-peril.** A
  hurricane is a **regional field**: *"a hurricane is always inside the wind field … the question isn't 'did it
  hit' but 'what wind speed did the site experience.'"* Each event produces a continuous intensity field
  (Holland parametric wind field along a track → swath grid; hurricane-wind curve anchor `x₀ ≈ 160 mph`) and
  *varies event-to-event*. It relates to convective wind **only through the shared 3-s-gust wind-damage curve**
  (wind is hurricane's primary peril; its surge/rainfall cross-link to the flood peril). This is the **genuinely
  unbuilt bucket** — the one where **portfolio correlation and EVT become load-bearing** (one event hits many
  assets at once; the field tail must be extrapolated). It is named here as the future field-intensity build,
  with the wall and migration path documented, not built past
  ([01_scope_and_sub_peril_taxonomy](../../extra/discussion/convective_wind/01_scope_and_sub_peril_taxonomy.md)).
  > **Forward double-count trap (when hurricane is added).** Hurricanes spawn tornadoes and produce
  > straight-line wind, so a TC-spawned tornado could appear in **both** the tornado stream **and** a hurricane
  > catalog — unlike tornado-vs-strong-wind, this is **not** automatically disjoint. Forward-compatibility:
  > treat the V1 tornado catalog as **inland-convective only** (excludes TC-associated tornadoes), or bind
  > hurricane's sub-perils with a shared event identifier and sample them jointly.

> **The "sub-perils matter" payoff.** Inland-convective wind — **one peril, two sub-perils** — tours **two
> coupling types we have already built**: tornado reuses hail's areal hit-or-miss, strong wind reuses wildfire's
> site-conditioned — leaving only field-intensity (the **separate, deferred hurricane peril**) for later. The
> shared compound-Poisson/NegBin engine is **untouched** by either. This is *standard interface, not standard
> physics* made concrete: same handoff, different physics.

For the full reasoning — the footprint taxonomy, the prior-art evidence, the worked intuition — see the
deep-dive: [discussion/convective_wind/02_coupling_buckets_and_wind](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md).

---

## How layer-0 feeds the pipeline

This layer authors the **definition**; the downstream layers consume it.

**→ M0 (input data) — what evidence to collect** ([m0_input_data.md](m0_input_data.md)):

```text
   SPC SVRGIS            tornado tracks 1950+ (~70k, with path length × width geometry);
                         severe wind reports 1955+ (gust in kt or damage-inferred)
   NOAA Storm Events     thunderstorm/high/strong-wind episodes; gust + damage; event context
   ASCE 7-22 maps        [W] basic-wind RP surface (3-s gust by MRI, Exp C) — the pre-integrated profile;
                         [T] Ch 32 tornado design speed by MRI & effective plan area (~EF2 cap);
                         Appendix F long-MRI tail
   EF scale              damage → 3-s-gust mapping (the bin table above)
   USWTDB                turbine point locations (per-turbine view + areal footprint)
   FEMA NRI              loss-side screening
   Two sites             Traverse Wind Energy Center, OK (high/proving) · Shepherds Flat, OR (low/baseline)
```

Honest M0 flags this layer mandates: **no public stochastic tornado/convective-wind catalog exists**
(proprietary: Verisk, Moody's RMS) — so M0 leans on the ASCE RP surfaces (pre-integrated) **or** the
bias-corrected SPC record; and **SPC counts are population-biased** (changing detection of weak events, mixed
measured/damage-only) — **bias-correct before fitting frequency** ([AWN-*](assumptions.md)).

**→ M1 (catalog) — the event criteria + magnitude model** ([m1_catalog.md](m1_catalog.md)):

- **Event criteria:** count an event when the 3-s gust crosses **μ** (NWS 58 mph ≈ 25.9 m/s (old repo: 25.92)
  for strong wind; EF0 for tornado) → the frequency **λ** per sub-peril.
- **Magnitude model (per-sub-peril, §4):** **tornado** = the **bounded GPD** on gust above μ, ξ < 0, truncated
  at **L = EF5 ≈ 113 m/s** — fit to the bias-corrected SPC Tornado record; **strong wind** = **Gumbel/exponential
  (ξ ≈ 0)**, **read off the ASCE RP surface directly** as the log-linear pre-integrated return-level curve
  (§5; learning-09 = profile-assembly, no fit). ξ < 0 is **not** a wind-wide rule — it is tornado's form.
- **Per-sub-peril fork:** strong wind = site-conditioned profile-assembly (well-populated); tornado = catalog
  fit from SPC path stats (sparse → learning-10). The two sub-perils are **disjoint, independent event streams** —
  disjoint by data product (the ASCE basic-wind surface is **non-tornadic** by construction; tornado = the SPC
  Tornado record). This is a classification/data-product assumption, not a physical law (flag it), and it is what
  makes adding their EALs valid downstream (no shared physical event); in V1 it is also safe because strong-wind
  damage is ~0 (gusts stay below the IEC survival onset).

The **two thresholds** then travel separately downstream: **μ** stays with M1 (it sets λ); the **IEC
damage-onset** goes to M3 (it anchors the damage curve where `DR(μ) ≈ 0`). M4 reunites frequency × severity on
the shared compound-Poisson/NegBin Monte Carlo: the **two per-sub-peril {λ, severity} profiles go IN; they are
combined ONLY by co-sampling both event streams into ONE annual-loss distribution per simulated year; ALL tail
metrics (VaR / PML / TVaR) are read off that ONE combined distribution — never by summing per-sub-peril profiles
or quantiles.** **EAL IS additive** across the sub-perils (linearity of expectation): `EAL_combined =
EAL_tornado + EAL_strongwind`, and a per-sub-peril EAL split is meaningful; but **VaR / PML / TVaR are NOT
additive** — summing per-sub-peril tail metrics overstates the joint tail (it assumes the worst tornado year and
worst strong-wind year coincide). *(Caveat: EAL additivity is exact for gross/uncapped loss; once AEP is capped
at TIV, even EAL must be read off the combined sample.)* Adding the EALs is valid because tornado and strong wind
are **disjoint, independent streams** (above) — no shared physical event. Every metric read off the **sampled**
distribution, **% of TIV alongside dollars**, never the expected-loss shortcut
([m4_loss_metrics.md](m4_loss_metrics.md)).

---

## Decisions & assumptions surfaced (this layer)

- **Decisions** ([decisions.md](decisions.md)): convective wind = one peril, two sub-perils (hurricane a
  separate deferred peril) · the 3-s-gust observable · μ = NWS 58 mph (strong) / EF0 (tornado) · L = EF5 ≈ 113 m/s
  (settled, with the 113-vs-145 revisit note) · **per-sub-peril severity** (tornado = bounded GPD ξ < 0; strong
  wind = Gumbel/exponential ξ ≈ 0) · ASCE RP surface as the pre-integrated tail for strong wind · the two-threshold
  (meteorological vs damage-onset) split · tornado ⊥ strong-wind disjointness · EAL-additive-but-tail-not at M4 ·
  the hurricane TC-tornado forward double-count flag · authored-not-inherited as layer-0. Logged **DD-WN-1..**.
- **Assumptions** ([assumptions.md](assumptions.md)): IEC 61400 Vref/Ve50 anchors (confirm vs turbine model) ·
  EF5 = 113 m/s vs 145 m/s · Exposure-C → hub-height/terrain adjustment · SPC population-bias correction ·
  rural EF low-bias · feathered-vs-operating state · tornado/strong-wind disjointness (classification/data-product
  assumption, not a physical law) · stationarity (climate non-stationarity / eastward drift noted, not frozen).
  Logged **AWN-1..**.

**Next → [M0 (input data)](m0_input_data.md):** meet the raw evidence (SPC, NOAA, ASCE, USWTDB) for the two
sites against the definitions authored here.
