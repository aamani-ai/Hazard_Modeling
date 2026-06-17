# 01 — Wind × Wind-Farm V1: Scope & the Sub-Peril Taxonomy

*A discussion doc, not a plan. It exists to settle **what V1 actually models** before we open layer-0 / M0.
The peril V1 builds is **convective wind** — **one peril with two sub-perils** ([T] tornado and [W] strong /
straight-line wind), which still earn distinct treatment because they sit in different coupling buckets — so
the first job is to *decompose convective wind* honestly into its two sub-perils, then build them in the most
tractable order. (Hurricane / tropical cyclone is a **separate, deferred peril**, not a sub-peril of
convective wind.) Every section ends with a decision; the owner's calls turn into `DD-WN-*` / `AWN-*` rows in
`docs/plans/convective_wind/`.*

---

## TL;DR (the whole argument in one screen)

1. **Convective wind is one peril with two sub-perils — tornado [T] and strong / straight-line wind [W].**
   The two are **genuinely different physical systems** — they pass the reference's dual split-test (distinct
   footprint **and** distinct data/metric), so they earn separate treatment *within* convective wind. A
   *stronger vs weaker gust* is one process; *a rotating vortex vs a broad outflow* is two sub-perils. This
   matches the Drive reference ("Convective wind — 2 sub-perils with distinct footprints, shared report
   record"). **Hurricane / tropical cyclone is a separate, deferred peril** (wind is hurricane's *primary*
   peril; its surge/rainfall cross-link to the flood peril) — related to convective wind **only** through the
   shared 3-s-gust wind-damage curve, not by membership in any "wind family."
2. **Wind is a wind turbine's *dominant* loss pathway.** Unlike solar (where hail and wildfire are #1/#2),
   the turbine is a tall, slender, aerodynamically-loaded structure — extreme wind is its defining structural
   hazard. So wind × wind-farm is the natural Hazard 3 of 3, and the loss is a **pure physical-damage** track.
3. **Route = both convective sub-perils first: strong wind, then tornado. The separate hurricane peril
   deferred.** The two convective sub-perils together **tour two of the three coupling buckets we have already
   built** (tornado reuses hail's areal hit-or-miss; strong wind reuses wildfire's site-conditioned
   machinery), leaving only field-intensity (the deferred hurricane peril) — the genuinely unbuilt bucket —
   for later. See [`02`](02_coupling_buckets_and_wind.md).
4. **Strong wind is built *first* because the hazard arrives pre-integrated.** The **ASCE 7-22 design-wind
   map is a return-period 3-s-gust surface** — ASCE/NIST already did the probabilistic tail analysis — exactly
   the way FSim pre-integrated wildfire. That is the fastest path to a real number (mirrors the wildfire
   kickoff). Tornado second: rare, path-geometry-driven, the catastrophic tail.
5. **The hazard must be *authored*.** For hail (MESH) and wildfire (FSim) the event came pre-defined by the
   product. **No single product pre-defines a "wind event."** So we define it quantitatively, anchored in
   standards (NWS 58 mph, EF scale, ASCE 7-22, IEC 61400) — a new **layer-0** step above M0. See [`03`](03_hazard_definition_and_thresholds.md).
6. **The scope line is sharper for wind than for any prior peril.** For solar, "hazard" (hail, fire) and
   "resource" (sun) were obviously different things. For wind, **the hazard medium IS the resource medium** —
   so we must draw the line in words: hazard-tier wind = *extreme wind that structurally damages the turbine*
   (this repo); resource wind driving generation/revenue = the Performance tier (`model-gpr`).
7. **Two sites, mirroring hail's low-vs-high contrast:** **Traverse Wind Energy Center, OK** (high —
   tornado-alley + derecho corridor) and **Shepherds Flat, OR** (low — Columbia Gorge, minimal
   tornado/derecho). One unchanged engine, two very different risk pictures — the payoff.

---

## 1. Where we are, and why we're talking first

Hail × solar and wildfire × solar are both built end-to-end (shared `M0`/`M1` peril catalog → a `solar/`
cell for `M2–M4`). Wind mirrors that shape — but wind has **two firsts** that no prior peril had, and both
are scope traps if we rush:

- **Convective wind has two sub-perils.** "Convective wind" is not one event. If we model it as a single
  undifferentiated peril we repeat the old model's false-generality mistake (one curve, one factor, one
  distribution across physics that differ). We have to decide *which sub-perils* we build, in *which order*,
  and *why* — before M0. (And we keep the **separate hurricane peril** explicitly out of V1, fenced as a
  deferred build.)
- **It is not pre-defined by a data product.** Hail's event ("severe hail ≥ 1 inch") came baked into MESH;
  wildfire's ("fire occurrence + flame-length classes") came baked into FSim. There is **no equivalent single
  product** that hands us "a wind event." We must author the definition — see [`03`](03_hazard_definition_and_thresholds.md).

The principles that decide the ties here:

- **Standard interface, not standard physics** — each convective-wind sub-peril (and the separate, deferred
  hurricane peril) gets *its own* physics behind the *same* typed interface; that is exactly what lets us
  split convective wind into [T]/[W] and **defer** the hardest, separate peril (hurricane) at zero
  architectural cost. The dual split-test ([P1](../../../principles/hazard_asset_specificity.md)) is the
  warrant for splitting tornado vs strong wind *within* convective wind.
- **Basics spot-on** — *the math is the product* — but also **don't over-claim coverage**: a correct tail on
  a mislabeled scope is still a credibility failure. "Wind risk" must not silently mean "convective wind only."
- **Modular from day one** — the shared compound-Poisson/NegBin Monte-Carlo loss engine **does not change**;
  each sub-peril ships value on its own and slots in by implementing the interface.

---

## 2. Convective wind = one peril, two sub-perils — the split-test, applied

The Hazard_Data_Reference is explicit about *when* a phenomenon earns its own sub-peril tag. A phenomenon
splits only on **both** axes (the dual test, reference §2):

1. **Distinct physical footprint** — "a genuinely different physical system… not just a different intensity
   of the same process. *(A stronger vs weaker gust is one process.)*"
2. **Distinct data / magnitude metric.**

The reference's own verdict table rules: *"Tornado / Strong Wind — rotating vortex / straight-line field —
distinct footprint + SPC data split — Split [T]/[W] — correct."* Note the split is on **footprint geometry**,
not gust magnitude. Run convective wind's two sub-perils through the test (the separate hurricane peril is
shown in the bottom row for contrast — it is **not** a convective-wind sub-peril):

| Convective-wind sub-peril | Physical system (footprint) | Magnitude metric / data | Splits? |
|---|---|---|---|
| **Tornado [T]** | rotating vortex — **narrow, intense path** | EF scale (damage-inferred) + path length × width; SPC SVRGIS path polygons | ✅ distinct footprint **and** distinct data (path geometry, unique to tornado) |
| **Strong / straight-line wind [W]** | straight-line field — **broad swath** (derecho, downburst, thunderstorm gust, synoptic high wind) | 3-s gust (kt, measured/damage-inferred); SPC severe-wind point reports + ASCE RP surface | ✅ distinct footprint **and** distinct data (point reports, no path) |
| *(separate peril, for contrast)* **Hurricane / tropical cyclone** | rotating cyclone — **regional intensity field** | 3-s gust over a swath built from a track; public stochastic catalogs (STORM/RAFT) + Holland field | a **separate deferred peril** — not a convective-wind sub-peril; related only via the shared 3-s-gust damage curve |

Both convective sub-perils pass. **Convective wind is one peril with two sub-perils** (tornado [T] + strong
wind [W]), each with its own footprint and its own coupling type. The 3-s gust is the *shared* magnitude
metric across them — and across the separate hurricane peril too — (the universal wind metric —
[`03`](03_hazard_definition_and_thresholds.md)); that shared curve is an **output/vulnerability grouping (the
"3-s-gust wind-damage-curve group"), not a peril family.** Within convective wind, the footprint geometry and
the data path differ between [T] and [W] — which is precisely what the dual test cares about.

> **DECISION WN-1 (gating).** Treat **convective wind as one peril with two sub-perils** (tornado · strong
> wind, each splitting on footprint + data), with **hurricane a separate, deferred peril** sharing only the
> 3-s-gust damage curve; build the taxonomy once before building any sub-peril? *(Recommended: yes —
> corroborated by the reference's own [T]/[W] verdict and the [P1](../../../principles/hazard_asset_specificity.md) dual test.)*

---

## 3. Why wind, why the turbine — the materiality case

For solar, hail and wildfire were chosen because they are the #1/#2 *loss drivers* on PV. For a **wind
turbine**, the dominant hazard *is wind itself* — and not the everyday resource wind, but the **extreme tail**:

- The reference puts tornado and strong wind in the **Destruction (Damage) family**, and names the wind
  turbine's dominant loss pathway as **Damage** (not disruption). So wind × wind-farm is a **pure
  physical-damage build** — the function/revenue-disruption track (energy-not-served, repair downtime) is
  *out of scope here*; it lives in the Performance tier and in repair-duration modeling.
- A utility-scale turbine is a tall (80–130 m hub), slender, aerodynamically-loaded structure whose damage
  mechanisms the reference lists directly: *"wind loading & overturning; debris impact; **turbine blade/tower
  failure**."* The primary exposed asset for convective wind is literally *"wind turbines (direct)."* This is
  the asset the hazard was made for.
- The loss is **asymmetric across the turbine's subsystems** — strong wind reaches the exposed aero
  subsystems (rotor/blades, nacelle/drivetrain); a tornado reaches further (it can take the tower). That
  subsystem distinction is real and feeds M3 (the old repo's `wind_config` already encoded it — see [`02`](02_coupling_buckets_and_wind.md) and the M3 plan).

So Hazard 3 = wind, asset = utility-scale onshore wind farm, is the natural completion of the
peril × asset map: it is the turbine's defining structural risk, and it is a clean damage track.

---

## 4. The route — both convective sub-perils first, the separate hurricane peril deferred

Convective wind has two buildable sub-perils; the separate hurricane peril is the deferred third build. The
order is **not** arbitrary; it falls out of two questions: *which is most tractable (fastest to a real,
defensible number)?* and *which reuses machinery we already have?*

```text
CONVECTIVE WIND (one peril, two sub-perils) + the SEPARATE deferred hurricane peril — build order
──────────────────────────────────────────────────────────────────────
  1. STRONG / STRAIGHT-LINE WIND  ──▶  SITE-CONDITIONED (bucket 3)
     [convective-wind sub-peril W]   broad swath; reuses WILDFIRE's M2; ASCE RP surface = pre-integrated
       hazard (like FSim) → FASTEST path to a real number.  High-frequency.

  2. TORNADO                       ──▶  AREAL HIT-OR-MISS (bucket 1)
     [convective-wind sub-peril T]   narrow path; reuses HAIL's Minkowski (path-aware thin rectangle).
       Rare per site → sparse Monte Carlo → the catastrophic tail.

  3. HURRICANE  [SEPARATE PERIL,   ──▶  FIELD-INTENSITY (bucket 2)
       DEFERRED]                      regional field; the GENUINELY UNBUILT bucket. Holland wind field
       along a track → swath grid → portfolio correlation + EVT load-bearing.
──────────────────────────────────────────────────────────────────────
NET: convective wind's two sub-perils tour TWO already-built coupling types,
     leaving only field-intensity (the separate hurricane peril) for later.
```

**Why strong wind first.** It is the wildfire of convective wind: the hazard arrives **pre-integrated**. The
ASCE 7-22 design-wind map is a return-period 3-s-gust surface — ASCE/NIST already baked the probabilistic
tail extrapolation into it (reference §4/§7: *"the maps embed the RP"*). That is the same situation as
FSim's BP+FLP for wildfire, so strong-wind M1 is **profile-assembly, not event-extraction**
([learning_logs/09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) and M2 **reuses
wildfire's site-conditioned machinery**. Pre-integrated hazard = fastest path to a real number — exactly the
lesson the wildfire kickoff cashed in. (Frequency-regime bonus: strong wind is high-frequency, so its tail is
well-populated — the easy Monte-Carlo regime.)

**Why tornado second.** It reuses hail's areal hit-or-miss coupling — a narrow tornado path is a thin
rectangle (extreme aspect ratio), so hail's Minkowski sum `(√F+√s)²/A` becomes a **path-aware** variant
dominated by length × asset-extent. But tornado is **rare per site** (low strike probability at any point),
so the Monte Carlo is **sparse** — it exercises [learning_logs/10](../../../learning_logs/10_monte_carlo_effective_sample_size.md)
(effective sample size) and *forces* us to report TVaR alongside VaR (the old repo's F-scale model floors VaR
to $0 in the sparse regime). The catastrophic single-asset tail is the payoff and the harder validation.

**Why the separate hurricane peril is deferred** (named, fence visible — note hurricane is a *distinct peril*,
not a convective-wind sub-peril):
- It is the **genuinely unbuilt coupling bucket** — field-intensity (bucket 2). A hurricane is *always inside
  the wind field*; the question is never "did it hit," it is "what wind speed did the site experience." That
  needs a **Holland parametric wind field along a track → swath grid** — net-new machinery, not a reuse.
- It is **coastal**, not inland-convective — a different geography and a different data path (public
  stochastic catalogs STORM/RAFT + the Holland field), where **portfolio correlation and EVT become
  load-bearing** (one event hits many assets; the field tail must be extrapolated).
- It is therefore the **bigger build** and the natural *next* field-intensity peril — we name it as the
  future build and **where** the field-intensity machinery + EVT-at-portfolio-scale will earn their keep, and
  we **do not** build past the wall.

> ⚠️ **Forward-compatibility flag (hurricane double-count trap).** When the separate hurricane peril is added,
> there is a real double-count trap that does **not** exist between tornado and strong wind: hurricanes spawn
> tornadoes and produce straight-line wind, so a TC-spawned tornado could appear in **both** the convective
> tornado stream **and** a hurricane catalog (unlike tornado-vs-strong-wind, this is **not** automatically
> disjoint). Forward-compatibility options: treat the V1 tornado catalog as **inland-convective only**
> (excludes TC-associated tornadoes), or bind hurricane's sub-perils with a shared event identifier and sample
> them jointly. *(Carry this into DD-WN-9 / the hurricane deferral plan.)*

> **DECISION WN-2 (gating).** Build order = **strong wind (site-conditioned, ASCE-pre-integrated) → tornado
> (areal, path-aware) → the separate hurricane peril DEFERRED (field-intensity)**? *(Recommended: yes —
> tractability + coupling-reuse + the honest deferral of the one unbuilt bucket.)*

---

## 5. The honest V1 label

Same forcing function as wildfire's exogenous-vs-endogenous honesty: state coverage limits in the open, so a
*partial* wind model is never mistaken for *total* wind risk.

> *Wind × Wind-Farm V1 models **convective wind only** — its two sub-perils: **strong / straight-line
> convective wind** (derecho, downburst, thunderstorm gust, synoptic high wind; site-conditioned via the ASCE
> 7-22 return-period gust surface) and **tornado** (areal path-strike via the SPC path record). Magnitude =
> the **3-second peak gust** at hub height, mapped through an **anchored, IEC-survival-conditioned** turbine
> damage curve, and aggregated through the shared compound-Poisson/NegBin Monte Carlo. **Hurricane / tropical
> cyclone is a separate, deferred peril** (the field-intensity build), related to convective wind only through
> the shared 3-s-gust damage curve. **Hail-on-turbine, lightning, ice/icing throw, and winter/synoptic
> non-convective extremes** are **adjacent turbine perils (separate perils, NOT convective-wind sub-perils)**.
> V1 does **not** claim to cover total wind risk to the asset.*

This is the *basics-spot-on* honesty axis applied to scope: the math may be right, but a model that silently
calls "convective wind" the whole of "wind risk" repeats the old model's credibility problem in a new costume.

> **DECISION WN-3 (gating).** Adopt the honest V1 label above and lock it into `00_intent.md` + a `DD-WN-*`
> row? *(Recommended: yes.)*

---

## 6. The full deferred list (named, so the fences are visible)

Beyond V1's two convective sub-perils, the turbine's broader exposure includes **several separate perils** —
the deferred hurricane peril plus a set of **adjacent turbine perils** that fail the dual test *as wind*.
Naming them is the point; each is a *different peril or process*, not a setting of the V1 convective-wind
model, and none is a convective-wind sub-peril:

| Separate peril / channel | Why it is distinct (not a V1 setting, not a convective-wind sub-peril) | Coupling bucket / process |
|---|---|---|
| **Hurricane / tropical cyclone** *(separate peril)* | rotating regional cyclone; coastal; track + parametric (Holland) wind field; public stochastic catalogs; wind is its *primary* peril with surge/rainfall cross-linking to flood | **Field-intensity (bucket 2)** — the genuinely unbuilt bucket; the next field-intensity build; related to convective wind only via the shared 3-s-gust damage curve |
| **Hail-on-turbine** *(adjacent turbine peril)* | distinct hazard *medium* (ice, not wind); already a built peril for solar — would be a new wind × hail cell, **not** a convective-wind sub-peril | areal hit-or-miss (already built for solar) |
| **Lightning** *(adjacent turbine peril)* | electrical/thermal, not aerodynamic; ignites/destroys via current, not gust; own frequency process (flash density) — **a separate peril, not a convective-wind sub-peril** | distinct peril; not wind-driven structural loss |
| **Ice / icing & ice-throw** *(adjacent turbine peril)* | accretion load + shed-ice projectile; a *winter* process; own magnitude metric (ice thickness) — **a separate peril, not a convective-wind sub-peril** | distinct peril (the reference lists ice as its own hazard with its own metric) |
| **Winter / non-convective synoptic extremes** *(adjacent turbine peril)* | broad-area high wind from synoptic systems (some of this *is* captured by the ASCE map as part of [W]) — the genuinely *non-convective* part (winter storms, ETCs) is a **separate peril, not a convective-wind sub-peril** | partially site-conditioned; flag the boundary |
| **Fatigue / sub-extreme operational loading** | gradual aerodynamic fatigue from *resource* wind — **Performance-tier**, not a catastrophic event | **out of this repo entirely** (see §7) |

> Most of the everyday "wind" a turbine sees is the *resource* wind that drives generation. V1 is explicitly
> the **extreme structural-damage tail** of convective wind's two sub-perils only. (Honest-label discipline, §5.)

---

## 7. The scope line — hazard wind vs resource wind (the hard line)

This is the **critical** boundary for wind, and it must be in words because — unlike every prior peril — the
hazard medium *is* the resource medium.

```text
For SOLAR (hail, wildfire):  HAZARD medium  ≠  RESOURCE medium      (hail/fire vs sun — obvious)
For WIND:                    HAZARD medium  =  RESOURCE medium      (wind vs wind — BLURS)
                                                       ↓
                          we draw the line in WORDS, not by the medium
```

| | **Hazard-tier wind (THIS repo)** | **Performance-tier wind (`model-gpr`)** |
|---|---|---|
| What | **Extreme** wind that **structurally damages** the turbine | The wind **resource** driving generation/revenue |
| The question | "Did an extreme event break the structure?" → **physical loss** | "How much energy/revenue did the wind produce, and how variable?" → **P50/P90/P99 generation** |
| Magnitude | 3-s peak gust above the damage-onset threshold (IEC survival) | mean wind speed at hub height, power curve, capacity factor |
| Loss object | damage ratio × TIV (asset value) | generation shortfall / revenue variability |
| Output | EAL / VaR / PML / TVaR (% of TIV alongside $) | probabilistic generation forecast |

The hard line: **hazard-tier wind = the destructive tail; performance-tier wind = the productive body.** The
two share a medium and a metric family (wind speed) but they answer different questions, live in different
tiers, and must not be conflated. V1 models *only* the destructive tail of the convective members.

### 7a. A deeper cut — for a *turbine*, strong wind is mostly a *disruption* peril (P1, forward-looking)

The reference sorts perils into two **impact pathways**: the **Damage track** (destruction) and the **Disruption
track** (output loss), noting *"a peril can travel both."* It lists strong wind in the **Damage track** — true for
a **building** (cladding/roof fail at gusts a turbine shrugs off). But by **hazard × asset specificity**
([P1](../../../principles/hazard_asset_specificity.md)) the *dominant* pathway is **asset-specific**, and for a
**turbine** it flips:

- A turbine **cuts out (~25 m/s) → feathers/parks** in high wind. That deliberate shutdown is exactly *why* its
  catastrophic-damage contribution from straight-line wind is **≈ 0** (feathered = survival config) — and it is
  *also* the **disruption** (lost generation while parked). **The turbine trades output to avoid breaking steel.**
- So for a turbine, strong wind is **mostly a *disruption + long-term-degradation* peril**: operational
  curtailment / energy-not-served (→ Performance tier, `model-gpr`, + a future BI / repair-downtime layer) and
  cumulative **fatigue** (→ a slow degradation / reliability mechanism) — with only a **≈ 0 catastrophic-damage
  tail**, which is what THIS tier models. **Tornado carries the wind *damage*.**

> **Honest nuance.** "≈ 0" is the *aerodynamic-overload* damage given survival design; real blade/component
> failures in high wind happen via **defects / pitch-control failures / maintenance** (a *reliability* channel),
> not pure overload — a separate future track, not "wind never breaks a turbine."

> **Governance (this is an observation, not a reclassification).** Strong wind **stays in the Damage track** —
> consistent with the reference (*"a peril travels both pathways"*). We only note its turbine-pathway split, and
> that the disruption/degradation track is **deferred** (Performance tier + future BI/reliability) while V1 runs
> the (≈ 0) damage track **end-to-end** (the small number is the honest output + a known-answer check). Formally
> moving strong wind to the disruption track would require a **Drive-doc update first** (the Drive docs are the
> source of truth). Tracked as **AWN-31**.

> **DECISION WN-4 (gating).** State this hard scope line explicitly in `00_intent.md` **and** as a `DD-WN-*`
> decision (it is the single most blur-prone boundary in the whole platform)? *(Recommended: yes — required
> by the AGENTS tier-scope mandate; for wind this is not optional housekeeping, it is the scope.)*

---

## 8. The two sites — Traverse (high) vs Shepherds Flat (low)

Hail proved the engine with a deliberate **low-vs-high** pair (Hayhurst, negligible vs Matrix, material), so
the same unchanged engine produces two very different risk pictures. Wildfire did the same (Hayhurst vs
Matrix). Wind mirrors it — two real utility-scale onshore wind farms, picked from the renewablesinfo boundary
DB (OSM/EIA polygons), straddling the convective-wind hazard gradient:

| | **Traverse Wind Energy Center** (HIGH / proving) | **Shepherds Flat** (LOW / baseline) |
|---|---|---|
| Location | Oklahoma | Oregon (Columbia Gorge) |
| Capacity | ~999 MW | ~845 MW |
| Why this site | **Tornado-alley + derecho corridor** — high strike-density geography; the site that *should* light up | Minimal tornado/derecho exposure; the calibration "near-zero" baseline |
| What it proves | the catastrophic-tail (tornado areal strike) and the well-populated strong-wind tail both register | the engine returns a *correctly small* number where the hazard is genuinely low (the negligible-but-not-zero check) |

The **boundary polygon** (from the boundary DB) gives the areal footprint for path/swath intersection (the
tornado coupling needs an *area*, not a point). The **per-turbine point locations** come from **USWTDB** — for
the per-turbine view (a long line of turbines has many times the strike exposure of a single point; the
reference: *"a point lookup understates linear assets"*). So: polygon for the areal/site footprint, USWTDB
points for the per-turbine resolution.

> ⚠️ **Owner action / to-verify at M0.** Confirm both boundary polygons resolve in the renewablesinfo
> boundary DB and that USWTDB has the turbine point clouds for both. The capacities here are nameplate
> approximations from the settled framing — pin the exact MW + turbine count + model at M0 (they scale TIV
> and the per-turbine count). *(Status: to-verify — see [AWN-*](../../../plans/convective_wind/assumptions.md).)*

> **DECISION WN-5.** Lock the two-site pair (Traverse high / Shepherds Flat low), with polygon-for-footprint
> + USWTDB-for-turbine-points? *(Recommended: yes — direct hail/wildfire analogue; sites are real and in the
> boundary DB.)*

---

## 9. Light layer-0 / M0 / M1 sketch (context only — we still plan these step by step)

```text
LAYER-0  docs/plans/convective_wind/00_hazard_definition.md   ← the NEW step, above M0 (wind is AUTHORED)
    └ author the hazard quantitatively: 3-s gust observable; event threshold μ
      (NWS 58 mph / EF0 65 mph); physical bound L = EF5 ceiling ≈ 113 m/s
      (V1-adopted, revisit-noted vs old-repo 145 m/s); the SECOND, asset-coupled
      threshold (IEC 61400 survival/design); severity = bounded GPD (ξ<0) for
      TORNADO, Gumbel/exponential (ξ≈0) capped at L for STRONG WIND / ASCE RP
      surface. The two thresholds kept distinct. See 03.

M0  Notebooks/convective_wind/m0_input_data/   (peril-shared)
    └ SPC SVRGIS (tornado paths + wind reports) · NOAA Storm Events · ASCE 7-22
      RP gust surface (point lookups) · ASCE Ch 32 tornado maps · USWTDB turbine
      points · the two site boundaries. Interpret every layer; record the
      population/reporting-bias caveat (SPC counts are population-biased — bias-
      correct before fitting frequency). Both sites are rural → historical EF
      severity likely understated (the rural-low-bias caveat).

M1  Notebooks/convective_wind/m1_catalog/   (peril-shared)
    └ per-sub-peril event definition + λ + severity (per-sub-peril ξ):
        strong wind  = ASCE pre-integrated RP surface (profile-assembly, learning-09)
                       OR a SPC-extracted catalog (Poisson occurrence + Gumbel/
                       exponential gust, ξ≈0, capped at L);
        tornado      = SPC path stats (EF-class probs, path length × width, areas);
                       severity = bounded GPD (ξ<0), truncated at the EF5 ceiling L.

    (then, per sub-peril, step by step:) M2 coupling — tornado areal (hail
    Minkowski, path-aware) · strong wind site-conditioned (wildfire reuse) ·
    M3 anchored turbine damage curve (IEC survival onset, operational state) ·
    M4 the SHARED compound-Poisson/NegBin MC, untouched, metrics off the SAMPLED
    distribution, % of TIV alongside dollars (NEVER the Method-0 expected-loss shortcut).
```

> **How the two sub-perils combine (carry into the M4 plan).** Two separate per-sub-peril {λ, severity}
> profiles go IN; they are combined **only** by co-sampling both event streams into **one** annual-loss
> distribution per simulated year; **all** tail metrics (VaR / PML / TVaR) are read off that **one** combined
> distribution — never by summing per-sub-peril profiles or quantiles. **EAL is additive** across the
> sub-perils (linearity of expectation): EAL_combined = EAL_tornado + EAL_strongwind, and a per-sub-peril EAL
> split is meaningful. But **VaR / PML / TVaR are NOT additive** — summing per-sub-peril tail metrics
> overstates the joint tail (it assumes the worst tornado year and worst strong-wind year coincide). Caveat:
> EAL additivity is exact for gross/uncapped loss; once AEP is capped at TIV, even EAL must be read off the
> combined sample. **Disjointness assumption:** tornado and strong wind are treated as **disjoint, independent
> event streams** — disjoint *by data product* (the ASCE basic-wind surface is **non-tornadic by
> construction**; tornado = the SPC Tornado record), which is what makes adding their EALs valid (no shared
> physical event). In V1 it is also safe because strong-wind damage is ~0 (gusts stay below the IEC survival
> onset). It is a classification/data-product assumption, **not a physical law** — flag it.

---

*Next: once the owner settles Decisions WN-1…WN-5, these graduate to `docs/plans/convective_wind/` (`00_intent`,
`00_hazard_definition`, `decisions.md` `DD-WN-*`, `assumptions.md` `AWN-*`), and we open **layer-0**, then
**M0** — one layer at a time, no jumps. The coupling reasoning that justifies the build order is in
[`02`](02_coupling_buckets_and_wind.md); the authored hazard definition is in [`03`](03_hazard_definition_and_thresholds.md).*
