# 03 — Authoring the Hazard: Definition, Thresholds & Severity

*A discussion doc, not a plan. It exists to settle **why wind's hazard must be authored — and how** — before
we open layer-0 / M1. This is the reasoning *behind* the layer-0 spec: the standards we anchor to, the
**two-threshold** insight, EVT-on-magnitude (the **bounded GPD, ξ<0, for tornado**; **Gumbel/exponential,
ξ≈0, capped at L, for strong wind**), and the ASCE return-period surface as a pre-computed return-level curve.
It is written for a reader new to the domain, so each term is defined on first use. The conclusions graduate
to [`docs/plans/convective_wind/00_hazard_definition.md`](../../../plans/convective_wind/00_hazard_definition.md)
and [`decisions.md`](../../../plans/convective_wind/decisions.md).*

> Siblings: [`01` scope & taxonomy](01_scope_and_sub_peril_taxonomy.md) · [`02` coupling buckets](02_coupling_buckets_and_wind.md).
> The EVT/severity background: [`hazard_math/05`](../../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)
> · [`hazard_math/03`](../../../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md).

---

## TL;DR (the whole argument in one screen)

1. **Wind is the first peril we must *author*.** For hail (MESH = "severe hail ≥ 1 inch") and wildfire (FSim
   = "fire occurrence + flame-length classes") the event came **pre-defined by the data product**. No single
   product pre-defines a "wind event" — so *we* define it, quantitatively, anchored in **engineering and
   meteorological standards**, not intuition.
2. **The magnitude observable is the 3-second peak gust** — the reference's *"universal metric"* — read at
   hub height, mapped through a wind-load/fragility curve.
3. **There are TWO thresholds, and keeping them distinct is the central insight.** The **meteorological event
   threshold** (what the catalog *counts*, for λ) is **NWS severe ≥ 58 mph (≈ 25.9 m/s)** for strong wind /
   **EF0 ≥ 65 mph** for tornado. The **asset damage-onset threshold** (where the damage curve *leaves zero*)
   is far higher — the turbine's **IEC 61400 survival/design wind speed.** Most "severe wind" barely scratches
   a turbine.
4. **The physical upper bound** L = the **EF5 ceiling ≈ 113 m/s (~253 mph)** — gust magnitude is bounded; the
   severity tail is *short*, not heavy. **V1 adopts L = 113 m/s with a revisit note** (vs the old repo's
   145 m/s — reconciled in §4).
5. **Severity is per-sub-peril, not one wind-wide form.** **Tornado** severity *is* a **bounded Generalized
   Pareto Distribution (GPD) with ξ<0** on gust magnitude above μ, truncated at the EF5 ceiling L (it reaches
   the ceiling — the analytic solve from the old repo's `mag_sim`). **Strong wind** severity is **Gumbel /
   light exponential (ξ≈0), physically capped at L** — the build found the ASCE return-level curve is
   log-linear (R²≈0.999), so it is *not* a bounded GPD with ξ<0. The gust is a **continuous** magnitude
   (unlike wildfire's 6 discrete flame-length classes) — so wind finally cashes in the continuous-severity
   thread.
6. **For strong wind, the ASCE 7-22 RP surface *is* the pre-computed EVT return-level curve** — ASCE/NIST did
   the tail extrapolation for us. Reading several MRI maps = sampling the return-level function at fixed
   exceedance probabilities. The honesty cost: we inherit their assumptions and cannot re-test them.
7. **Honest gaps named:** the reference supplies the 58 mph threshold, the EF bins, the 3-s-gust metric, and
   the ASCE surfaces — it does **not** itself name IEC 61400, the Vref classes, or the EF5 ≈ 113 m/s ceiling.
   Those anchors come from the standards / old-repo HAZARD_LIMITS. We label that provenance honestly.

---

## 1. Why wind must be authored (the first peril without a pre-defined event)

For every prior peril, the **data product itself defined the event**, and we simply inherited it:

```text
  HAIL      →  MESH (the MRMS product)   →  event = "severe hail ≥ 1 inch"      ← pre-defined for us
  WILDFIRE  →  FSim (the USFS simulator) →  event = "fire occurrence + 6 FLP classes"  ← pre-defined for us
  WIND      →  ??? (no single product)   →  event = WE MUST DEFINE IT           ← AUTHORED
```

There is no MESH-equivalent for wind. The data is *fragmented*: SPC SVRGIS has tornado paths and wind-report
points; NOAA Storm Events has thunderstorm/high/strong-wind episodes (gust in knots or damage-inferred); ASCE
7-22 has design-wind and tornado *maps*; the EF scale is a damage→wind *mapping*. **None of them says "here is
a wind event and its magnitude" in one place.** So defining the event — *what counts, at what magnitude, up to
what limit* — is a genuine modeling step we must perform ourselves.

This is why wind gets a **new layer, layer-0, *above* M0** — the **hazard-definition layer.** M0 is "get the
raw data"; layer-0 is "decide *what a wind event is*, quantitatively, before we go get the data that measures
it." For hail and wildfire, layer-0 was empty (the product did it). For wind it is the centerpiece. And the
discipline is **anchor every choice in a published standard**, never intuition — that is what makes an
authored definition defensible rather than arbitrary.

> **DECISION WN (gating).** Introduce a **layer-0 hazard-definition step** above M0 for wind (and treat it as
> the model's first deliverable), authored from standards? *(Recommended: yes — wind is the first peril
> without a product-defined event; the definition is genuine, citable modeling work.)*

---

## 2. The magnitude observable — the 3-second peak gust

Before thresholds, fix the *variable* the whole model is built around. The reference is explicit (verbatim):
*"3-second gust speed is the universal metric — map it to a wind-load / fragility curve per asset."* Both
sub-perils converge on it: tornado ratings (EF) are *expressed* as 3-s gusts; ASCE design speeds are 3-s
gusts; turbine survival speeds (IEC) are stated as 3-s gusts. So:

- **Magnitude observable = 3-second peak gust wind speed**, at **hub height** (the turbine's exposed
  elevation, 80–130 m — not the 10 m standard met height; an elevation adjustment is needed and is an honest
  assumption to register).
- It is the **single causal intensity measure** the vulnerability curve is built around. Everything — the
  thresholds, the severity distribution, the damage curve — lives on this one axis.

A definitional note worth keeping straight: a **gust** (a 3-second peak) is *not* the **sustained / mean**
wind (a 1- or 10-minute average). The old repo conflated them — it routed gust-type events to the tornado
curve and sustained-type events to the strong-wind curve (a curve swap masquerading as physics). V1 maps a
single, well-defined 3-s peak gust to a single turbine curve. *(Do not replicate the gust-vs-sustained curve
swap — a flagged old-repo bug.)*

---

## 3. The TWO thresholds — the central insight

This is the part a newcomer most needs, because the two thresholds are easy to collapse into one — and
collapsing them is *wrong.* They answer different questions and live in different layers of the model.

```text
  THRESHOLD 1 — METEOROLOGICAL EVENT THRESHOLD (μ)        THRESHOLD 2 — ASSET DAMAGE-ONSET THRESHOLD
  "what does the CATALOG count?"  → drives λ (frequency)  "where does the DAMAGE CURVE leave zero?" → drives loss
  ────────────────────────────────────────────────────   ─────────────────────────────────────────────────────
  strong wind:  NWS severe ≥ 58 mph  (≈ 25.9 m/s)         turbine survival/design wind speed (IEC 61400)
  tornado:      EF0 ≥ 65 mph         (≈ 29 m/s)           Ve50 ≈ 1.4 · Vref ≈ 52–70 m/s  (class III–I)
  ────────────────────────────────────────────────────   ─────────────────────────────────────────────────────
  set by:  the weather service / damage scale            set by:  the turbine's engineering design
  used in: M1 (the rate of events worth counting)        used in: M3 (the conditional damage curve)
```

**The insight:** a "severe wind event" (just over 58 mph) is a *meteorological* event worth **counting** — but
it is **far below** what it takes to **damage** a modern turbine. The turbine is engineered to *survive* 3-s
gusts up to its IEC class limit (Ve50 ≈ 52–70 m/s ≈ 116–157 mph). So the damage curve is **anchored**:
`DR(μ) ≈ 0` at the meteorological threshold (most severe wind barely scratches a turbine), and it rises
**steeply only as the gust approaches the IEC survival speed.** If we collapse the two thresholds — start the
damage curve at 58 mph — we would massively over-state turbine loss from everyday severe-wind events.

Why count events that don't damage the asset at all? Because **the catalog must be defined independently of
the asset** — λ is a property of the *hazard*, the damage curve is a property of the *asset*. Keeping them
separate is exactly the [P3](../../../principles/basics_spot_on.md) discipline (keep occurrence separate from
severity; the engine reunites them by *sampling*, never by an expected-loss collapse). The frequency is high
(many ≥58 mph events) but the *conditional* damage at those magnitudes is ≈0 — and that is the honest picture,
not a bug.

> **DECISION WN (gating).** Keep the two thresholds **distinct**: μ = NWS 58 mph (strong wind) / EF0 65 mph
> (tornado) for the **catalog/λ**, and the **IEC survival/design speed** as the **damage-onset** anchor for
> the M3 curve? *(Recommended: yes — this is the load-bearing distinction of the whole wind build.)*

---

## 4. The standards we anchor to (and exactly what each gives us)

Authoring responsibly means every number traces to a published standard. The four anchors:

| Standard | What it is (plain) | What it gives the wind model |
|---|---|---|
| **NWS severe-thunderstorm criterion** | the National Weather Service's definition of "severe" convective wind | **μ for strong wind = ≥ 58 mph (≈ 25.9 m/s)** — the catalog threshold. *(Exactly the old repo's 25.92 m/s.)* |
| **EF (Enhanced Fujita) scale** | a **damage-inferred** wind rating (operational since 2007; replaced the F scale), estimated from **28 damage indicators × 8 degrees of damage** | the tornado magnitude bins (verbatim): **EF0 65–85 / EF1 86–110 / EF2 111–135 / EF3 136–165 / EF4 166–200 / EF5 >200 mph** (3-s gust). μ for tornado = EF0 (65 mph). |
| **ASCE 7-22** (design loads) | the US structural-design wind standard; its maps are **return-period 3-s-gust surfaces** at 33 ft, Exposure C | the **pre-integrated RP gust surface** for strong wind (the EVT already done — §6); MRIs by risk category (RC I 300-yr / II 700-yr / III 1,700-yr / IV 3,000-yr; Appendix F to ~10⁶-yr); Ch 32 = first-ever tornado design maps (~EF2 and below). |
| **IEC 61400** (wind-turbine design) | the international turbine-design standard; defines **wind classes** by reference speed | the **damage-onset anchor**: class I/II/III reference 10-min mean **Vref = 50 / 42.5 / 37.5 m/s**; the 50-yr extreme 3-s gust **Ve50 ≈ 1.4 · Vref ≈ 52–70 m/s.** The turbine's *survival* speed. |

**The physical upper bound L.** Gust magnitude is not unbounded — beyond a physical ceiling there is
essentially no probability mass. **V1 adopts L = the EF5 ceiling ≈ 113 m/s (~253 mph)** as a settled choice
with a **revisit note** (the old repo's HAZARD_LIMITS value; note the old repo's F-scale midpoints put F5 at
111.8 m/s — consistent; the divergence vs the old repo's 145 m/s tornado limit is reconciled below). This
bound is what makes the tornado severity tail **short** (§5) and is the cap for strong wind too.

> ⚠️ **Honest provenance note.** The Hazard_Data_Reference supplies the **58 mph threshold**, the **EF bins**,
> the **3-s-gust metric**, and the **ASCE RP surfaces** — but it does **not** itself name **IEC 61400**, the
> **Vref classes**, or the **EF5 ≈ 113 m/s ceiling.** Those anchors come from the IEC standard / the old-repo
> HAZARD_LIMITS, not from the reference (the reference only says, for turbines, *"account for survival wind
> speed… not just design speed"*). We cite that split honestly in `00_hazard_definition.md`.

> 🔧 **Divergence reconciled (from prior art).** The old repo's tornado limit was **145 m/s** (Moore-1999
> *observed Doppler max*), while it placed **113 m/s** as the *Strong Wind* limit (Cyclone Olivia gust).
> **V1 adopts the EF5 damage-inferred ceiling ≈ 113 m/s as L for both convective sub-perils** — this is the
> settled status (not "still open"), carried with a revisit note (damage-inferred ceiling vs observed Doppler
> max). Record the reconciliation as a decision, not a silent change.

---

## 5. Severity — per-sub-peril EVT on gust magnitude (EVT-on-intensity)

Now the severity model: *given* an event above μ, how big is the gust? The answer is **Extreme Value Theory
on the intensity** — fit the tail of the gust magnitude, then map the rare gust through the damage curve. The
*shape* of that tail is **per-sub-peril, not one wind-wide form**: **tornado = a bounded GPD with ξ<0** (it
reaches the EF5 ceiling L); **strong wind = Gumbel / light exponential, ξ≈0, capped at L** (the build found
the ASCE return-level curve is log-linear, R²≈0.999). ξ<0 is **not** a wind-wide severity rule — it is the
tornado case.

**Why EVT-on-intensity (not EVT-on-loss).** [hazard_math/05](../../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)'s
rule: prefer EVT on the *hazard magnitude*, because hazard observations are more available than asset-loss
data and one hazard tail feeds many asset curves; use loss-tail EVT only when the loss object is credible.
Wind has a real gust record (SPC/Storm Events) and a real physical ceiling — a textbook EVT-on-intensity case.

**The bounded GPD (the reusable analytic solve).** A **Generalized Pareto Distribution** models exceedances
above a threshold μ. Its shape parameter ξ decides the tail:

```text
  ξ > 0   heavy / unbounded tail        (catastrophe-loss intuition — but NOT right for wind)
  ξ = 0   exponential / Gumbel tail     ← THIS is STRONG WIND (capped at L; ASCE curve log-linear, R²≈0.999)
  ξ < 0   BOUNDED, finite upper endpoint ← THIS is TORNADO: it reaches the physical ceiling L (EF5)
```

[hazard_math/05](../../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)
warns explicitly: *do not assume catastrophe loss always has ξ>0; a single asset's physical damage is
bounded.* For **tornado**, the gust reaches the bound L (EF5 ceiling), so **ξ < 0** — a *short, bounded* upper
tail. For **strong wind**, the empirical ASCE return-level curve is log-linear (R²≈0.999), i.e. **Gumbel /
exponential, ξ≈0, physically capped at L** — *not* a bounded GPD with ξ<0. The old repo's `mag_sim` already
has the closed-form **bounded-GPD** solve we reuse **for tornado** (left-anchored at μ, right-bounded at L,
mean-constrained):

```text
  ξ = (μ_mean − μ) / (μ_mean − L)        ← μ_mean − L < 0  ⇒  ξ < 0  ⇒  bounded tail  (TORNADO)
  σ = −ξ · (L − μ)
  → scipy.stats.genpareto(c=ξ, loc=μ, scale=σ),  support [μ, L], truncated at L
```

For **strong wind** we do **not** use this bounded-GPD solve: the severity is **Gumbel / exponential (ξ≈0),
capped at L**, read off (or fit to) the log-linear ASCE return-level curve (§6) — the gust does not push up
against the ceiling the way a tornado does, so the tail is light-exponential, not a ξ<0 bounded GPD.

**Continuous magnitude — the thread wind cashes in.** Wildfire's severity was **6 discrete** flame-length
classes (FLP1–6). Wind's gust is a **continuous** magnitude on the 3-s-gust axis
([hazard_math/03](../../../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md):
magnitude ≠ severity — magnitude is the physical strength, severity is the loss *after* the curve). So wind is
where the platform finally exercises a **continuous** severity distribution end-to-end.

> ⛔ **The one part of `mag_sim` to REJECT.** The old repo back-solved `μ_mean` from a target EAL
> (`μ_mean = InverseCurve(EAL_ratio / λ)`) — i.e. it *reverse-engineered the magnitude distribution from the
> answer it wanted.* That is circular. The new build **fits the GPD to the observed gust record** (SPC/Storm
> Events, bias-corrected) **or reads the ASCE RP surface** directly — never anchors the tail to an EAL target.
> *(Keep the analytic ξ/σ solve and the bounded shape; drop the EAL back-solve.)*

> **DECISION WN.** Severity is **per-sub-peril**: **tornado = bounded GPD (ξ<0) on the 3-s gust, anchored at
> μ, truncated at L** (reuse the old analytic ξ/σ solve), fit to the SPC/Storm-Events record (bias-corrected);
> **strong wind = Gumbel/exponential (ξ≈0), capped at L**, read off (or fit to) the log-linear ASCE
> return-level curve — *not* EAL-anchored in either case? *(Recommended: yes — EVT-on-intensity per
> hazard_math/05; reject the EAL back-solve; do not impose ξ<0 wind-wide.)*

---

## 6. The ASCE surface = a pre-computed EVT return-level curve

For strong wind specifically, there is a shortcut that is *better* than fitting our own GPD: the EVT has
**already been done for us.** This is the linchpin that makes strong wind a site-conditioned peril
([`02`](02_coupling_buckets_and_wind.md) §6).

**What a return-level curve is (plain).** EVT, once fit, lets you answer: *"what gust speed is exceeded once
every T years?"* — for any return period T. Plotting gust-vs-T is the **return-level curve.** Reading several
points off it (the 100-yr gust, the 700-yr gust, the 1,700-yr gust…) traces the tail.

**The ASCE maps *are* that curve, pre-computed.** The reference is explicit (verbatim): *"the ASCE design maps
already contain a probabilistic RP analysis (NIST tornado simulation, ASCE wind statistics), so the RP surface
exists even though a downloadable event set does not."* The ASCE 7-22 design-wind maps deliver the 3-s gust by
**MRI (Mean Recurrence Interval = return period)** — RC I 300-yr / II 700-yr / III 1,700-yr / IV 3,000-yr, and
**Appendix F** extends to ~10⁴–10⁶-yr for the deep tail. So:

```text
  reading the ASCE maps at several MRIs   ≡   sampling the return-level curve at fixed exceedance probabilities
  the RP → gust relationship              ≡   the pre-computed EVT tail (POT/GPD already fit by ASCE/NIST)
```

This is **structurally identical to FSim** pre-integrating ≥20,000 fire seasons into BP+FLP — the upstream
authority did the stochastic integration and the tail extrapolation; we **read** the result
([learning-09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)). It is the *fastest path to
a real strong-wind number* — exactly the reason strong wind is built first (the wildfire-FSim parallel).

**The honesty cost (carry it forward).** A pre-integrated surface is *a borrow, not a free lunch.* We inherit
ASCE/NIST's assumptions: the **Exposure C** reference terrain (open country — must be adjusted for the site's
actual terrain B/D), the **3-s-gust at 33 ft** reference height (must be lifted to hub height), the RP
statistics and their vintage, and the convention by which the tail was extrapolated. We **cannot re-test**
those upstream choices — the uncertainty *moved upstream*, it did not vanish. And a transferable caution from
the hurricane prior art: **which RP convention** a surface uses matters for the tail (empirical-Weibull
plotting positions vs an EVD-fit give materially different winds beyond the 100-yr RP), and that tail is
exactly what drives PML/VaR. Flag the convention.

> **DECISION WN.** For strong wind, treat the **ASCE 7-22 RP gust surface as the pre-computed return-level
> curve** (profile-assembly, reuse wildfire's M2), with the inherited-assumption caveats recorded; keep the
> SPC-extracted GPD catalog as the **alternative/validation** path? *(Recommended: yes — pre-integrated =
> fastest defensible number; document what we inherit.)*

---

## 7. The honest uncertainties (named, so the fences are visible)

Authoring a hazard means owning what we *don't* know. The load-bearing uncertainties, by source:

- **Reporting / population bias (SPC).** SPC tornado and wind counts are **population-biased** and reporting
  practices changed over time (more weak events detected now); wind reports **mix measured gusts with
  damage-only entries.** **Bias-correct before fitting frequency** — the old repo did *not*, and pulled 1950+
  data while filtering to 1996+ with no correction. This directly biases λ.
- **Rural under-rating of EF.** EF is **damage-inferred**, so it is **biased low where there is little to
  damage** (rural/open land) and **capped by the strongest damage indicator present.** *Both* our proving
  sites (Traverse OK, Shepherds Flat OR) are **rural** → historical EF severity there is likely **understated.**
  Treat historical EF magnitude as uncertain.
- **Pre/post-2007 discontinuity.** Tornado rating switched **F → EF in 2007**; the 58 mph severe-wind
  definition and detection also shifted. These create discontinuities that distort any trend/frequency fit —
  account for them.
- **Inherited ASCE assumptions** (§6) — Exposure C reference, 33 ft height, RP convention, vintage — borrowed,
  not re-testable.
- **The provenance split** (§4) — IEC 61400 / Vref / EF5-ceiling are *not* in the Hazard_Data_Reference; they
  come from the standards / old repo. Labeled as such.
- **Vertical-velocity limitation** — the EF scale assumes horizontal failure winds, but violent tornadoes
  carry significant near-ground vertical velocity → a source of under-rating in the extreme tail.
- **Climate non-stationarity** — an observed eastward drift of activity (into the Southeast / "Dixie Alley")
  and clustering. V1 is a **current-climate** track; we **flag** non-stationarity rather than freeze or project
  the climatology.

> Honesty discipline ([P3](../../../principles/basics_spot_on.md)): be **right about the math** while being
> **honest about the inputs.** Every item above is a *named, fenced* limitation — not a silent default.

---

## 8. What graduates to the layer-0 spec

The conclusions of this discussion become the layer-0 plan-of-record
([`docs/plans/convective_wind/00_hazard_definition.md`](../../../plans/convective_wind/00_hazard_definition.md)):

```text
  Magnitude observable :  3-second peak gust, hub height (elevation adjustment = registered assumption)
  Event threshold μ    :  strong wind  ≥ 58 mph (≈ 25.9 m/s)  [NWS severe]
                          tornado      ≥ 65 mph (EF0)          [EF scale]
  Physical bound L     :  EF5 ceiling ≈ 113 m/s (~253 mph)     [V1-adopted, revisit-noted vs old-repo 145 m/s]
  Damage-onset (2nd)   :  IEC 61400 survival/design — Ve50 ≈ 1.4·Vref ≈ 52–70 m/s  [curve leaves zero here]
  Severity model       :  PER-SUB-PERIL —
                          tornado     = bounded GPD (ξ<0) on the 3-s gust, anchored μ, truncated L
                                        (fit to SPC/Storm-Events, bias-corrected)
                          strong wind = Gumbel/exponential (ξ≈0), capped at L
                                        (read the ASCE RP surface — log-linear return-level curve, R²≈0.999)
  Operational state    :  feathered vs operating affects the curve (per the reference) — registered for M3
```

---

*Next: these graduate to `docs/plans/convective_wind/00_hazard_definition.md` (the authored layer-0 spec) and the
`DD-WN-*` decisions; the coupling that consumes this definition is in [`02`](02_coupling_buckets_and_wind.md),
and the scope that frames it is in [`01`](01_scope_and_sub_peril_taxonomy.md). The two thresholds, kept
distinct, are the thing to carry into M1 (μ → λ) and M3 (IEC onset → the anchored curve).*
