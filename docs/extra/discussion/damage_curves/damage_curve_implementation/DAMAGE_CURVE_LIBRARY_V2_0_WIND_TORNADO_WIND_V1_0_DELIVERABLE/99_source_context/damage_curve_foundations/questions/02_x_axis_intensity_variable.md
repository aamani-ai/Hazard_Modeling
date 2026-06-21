# 00x · The x-axis — what intensity variable a damage curve is a function of  🟢 NEAR-FINAL

The hidden prerequisite to representation ([`05`](05_emit_object.md)). Before we can argue "scalar
vs. 5 modes vs. distribution," we have to know what the curve is a function *of* — because a
distribution over damage at "a 60 mm hail event" is a clean object, while a distribution over "a
flood that's 2 m deep AND 3 m/s AND 18 h long" is a different and harder one. This doc frames the
x-axis decision with two rules: a **parsimony rule** on *how many* axes (univariate by default; a
second axis must earn its place), and a **chain-position rule** on *which* variable (put the axis at
the most-downstream node your hazard data can deliver).

*Source key:* principles = `hazard_asset_specificity` (the dual test + standard-interface),
`basics_spot_on`, `system_coherence_over_local_elegance`; depends on
[`01`](01_granularity.md) (grain) — which does most of the work on Q-x1. `[OURS]`
derived; `[REF]` inherited.

---

## 1 · The question is three nested questions

"What's on the x-axis?" is not one decision. It's three, and conflating them is the usual mess:

```
   Q-x1  HOW MANY axes?       univariate (one intensity scalar) vs multivariate (a surface)
   Q-x2  WHICH variable?      a TWO-part choice:
         Q-x2a  which QUANTITY?      hail: diameter? kinetic energy? momentum?
         Q-x2b  WHERE on the chain?  hazard-output? intermediate? at-the-component?
                                     (wildfire: fireline intensity? heat flux? component temp?)
   Q-x3  CONDITIONED on what? asset-STATE at event time that ISN'T hazard intensity
                              stow angle, prior damage, saturation — the awkward middle
```

This doc covers all three. **Q-x1** (the parsimony rule, §2–§5) gates representation and is where
doc-08 does the heavy lifting. **Q-x2** (the chain-position rule, §5b) is a genuine reasoned choice
with a data dependency, not a hand-wave. **Q-x3** (§6) is separated out cleanly — because a
conditioner is *not* an x-axis at all, and treating it as one is a known error.

---

## 2 · The default: univariate, on physical grounds

Most hazards present *several* physical quantities (a hailstorm has stone size, density, fall speed,
count; a flood has depth, velocity, duration). The instinct is to reach for a multivariate curve.
Parsimony-first says: **resist, and make the second axis earn its place** — the same discipline that
served us on failure units (don't build the primitive unless forced) and the dual test (don't split
unless footprint *and* metric differ).

Why the default is *univariate* and not just *simple*: a damage curve's dominant uncertainty is the
curve itself (`basics_spot_on`). Every extra axis multiplies the data needed to pin the surface and
multiplies the ways the curve can be wrong, while the *marginal* truth it adds is often small. An
axis that doesn't change the decision is precision the system can't use (`system_coherence`).

---

## 3 · The rule: a second axis must survive TWO escapes

A second variable `v2` earns its own axis **only if** the damage cannot be reduced to one axis by
*either* escape below. If either escape applies, stay univariate.

```
   ESCAPE 1 — COMPOSITE (collapse):
     physics gives a combiner that fuses the inputs into ONE intensity scalar.
     -> the curve is univariate on the COMPOSITE.  Not multivariate.
     classic: hail. diameter + density + fall-speed  -->  KINETIC ENERGY = 1/2 m v^2.
              one axis (KE or MESH-equivalent). the physics hands you the combiner; use it.

   ESCAPE 2 — SPLIT (different parts):
     the two variables damage DIFFERENT parts by DIFFERENT mechanisms.
     -> NOT one multivariate curve; TWO univariate curves on different axes, SUMMED (doc-08).
     classic: flood. DEPTH shorts the electricals; VELOCITY scours the foundation.
              => DR_elec(depth) + DR_found(velocity), each univariate. doc-08 already split them.

   A joint AXIS is needed ONLY if BOTH escapes fail:
     the SAME failure unit responds to TWO variables JOINTLY and NON-SEPARABLY
     (can't collapse to a composite, can't split across parts).
```

This is the **exact shape** of the joint≠sum bar from doc 08, one level over: a joint *axis* is the
analogue of a joint *grouping* — needed only when the thing genuinely doesn't separate.

```
   the parsimony cascade:

   apparent multivariate hazard
        |
        +-- ESCAPE 1: does physics give a combiner?  --yes-->  univariate on composite. DONE.
        |        no
        +-- ESCAPE 2: do the variables hit different parts? --yes--> split into univariate curves
        |                                                              (doc-08 summation). DONE.
        |        no
        +-- GENUINELY multivariate: same unit, non-separable joint response.
                 -> a real 2-D damage surface. RARE. must be shown, not assumed.
```

---

## 4 · The crux insight — multivariate at the asset level often dissolves at the unit level `[OURS]`

This is the part most worth your scrutiny, because it's where doc 08 quietly does the heavy lifting.

The reason flood *looks* irreducibly multivariate is that, at the **asset** level, damage depends on
both depth and velocity. But doc 08 already told us not to model at the asset level — we model at the
**failure-unit / subsystem** level and sum. And at *that* level, the two variables come apart:

```
   ASSET level (apparent):    DR_asset = f(depth, velocity)   <- looks 2-D, irreducible

   UNIT level (doc-08):       DR_elec(depth)      univariate on depth
                              DR_found(velocity)  univariate on velocity
                              DR_asset = Σ          <- two 1-D curves, summed

   the multi-axis-ness was an ARTIFACT of aggregating parts that respond to DIFFERENT variables.
   resolve to the right grain (doc-08) and the joint axis EVAPORATES.
```

> **Claim `[OURS]`.** Genuine irreducible multivariate damage curves are **rare**, because most
> apparent multi-axis behavior comes from *different parts responding to different variables* — which
> doc-08's grain resolution already separates into independent univariate curves. The joint axis only
> survives when a **single** failure unit needs two non-separable variables at once.

This is a strong simplifier: the x-axis question is *mostly already answered* by getting the grain
right. True 2-D surfaces are the exception we handle case by case, not the rule we design for. §5
applies the duration test and finds the exception count for v1 is **at most one** (wildfire
residence time), which is deferred — so v1 is univariate throughout.

---

## 5 · The one surviving candidate is duration — and it resolves to univariate for v1

Both escapes dispose of the obvious multivariate cases. The *only* candidate left for a genuine
second axis is **duration**, and resolving it is what lets v1 be univariate throughout. The key is
to not conflate two things both called "duration":

```
   "duration" splits into the damage-PROCESS it feeds:

   (2a) PEAK / threshold     -> damage is set by the PEAK; once exceeded, duration irrelevant.
   (2b) CUMULATIVE / fatigue -> damage ACCUMULATES with time at intensity (cross-EVENT, slow).
   (2c) PROGRESSIVE / burn-through -> sustained exposure reaches DEEPER than a flash (per-event).

   only 2b and 2c make duration a real second PHYSICAL axis. 2a folds duration away.
```

Sorting the in-scope pairs by process:

| Hazard | Process | Why | Duration verdict |
|---|---|---|---|
| **Hail** | 2a peak | impact is instantaneous; "storm length" = stone *count* = **frequency**, not duration | univariate (KE); no axis |
| **Flood** | 2a threshold | shorting is set by *reaching* the equipment (depth); longer submersion → corrosion is 2nd-order / maintenance | univariate (depth) + univariate (velocity), per §4 |
| **Wind** | 2a per event; 2b cross-event | a single extreme *event* does **peak-load** damage (gust exceeds threshold *now*); **fatigue** is slow accumulation over *years* of normal operation — not an event, belongs to the lifetime/disruption track (AWN-31) | univariate (gust); fatigue → out of event-damage scope |
| **Wildfire** | **2c burn-through** | flame **residence time** plausibly drives damage beyond what fireline intensity alone captures — a slow front delivers more heat than a fast flash at equal intensity; and this is *per-event*, so it does **not** escape to the disruption track | the **one** genuine 2-D candidate — **deferred** (§5a) |

The decisive move for **wind**: our pipeline models discrete *events* (compound-Poisson). Fatigue
isn't an event — it's the erosion of capacity *between* events — so it leaves the per-event damage
curve by the same logic that puts feathering and derating on the disruption track. That's a real
physical distinction, not a dodge. So wind is **peak-driven, univariate on gust**, for event-based
damage.

### 5a · Wildfire residence time — the one real 2-D case, deferred (not denied) `[OURS]`

Wildfire burn-through (2c) is genuine and *in scope* (per-event, physical). It is the single honest
exception to "everything is univariate." We **defer** it from v1 rather than build 2-D machinery:

- it's a **single** pair — building general 2-D curve machinery for one case violates
  `system_coherence` (don't build the cathedral for one mass);
- the built wildfire cell already uses **fireline intensity as a univariate axis** and works, bounding
  the marginal truth residence-time adds;
- `modularity_and_scaling` says: ship univariate v1, **document the wall**, build the 2-D extension
  *when* the wildfire cell's error demands it — not pre-emptively.

> **The documented wall `[OURS]`.** Wildfire residence-time is a known, real, in-scope second
> physical axis, *deliberately excluded from v1*. When wildfire fidelity demands it, the migration is
> a 2-D fireline-intensity × residence-time surface for the fire-exposed failure unit — and *only*
> that unit. Until then: univariate on fireline intensity. (Practical note: pre-computed FSim
> simulations make a fireline-intensity-keyed univariate curve directly buildable today.)

So the v1 result is clean: **every in-scope damage curve is univariate**, with wildfire residence
time the one named, deferred exception.

---

## 5b · Q-x2b — WHERE on the causal chain the axis sits (the chain-position rule) `[OURS]`

Choosing the x-axis isn't only "which quantity" (Q-x2a) — it's *where on the causal chain from
hazard to damage* you place it. Every hazard has a chain, and any node on it is a valid "intensity."
Wildfire makes this vivid, but it **generalizes to every pair**:

```
   the causal chain (wildfire shown; every hazard has one):

   fireline intensity  -->  heat flux at equipment  -->  component temperature  -->  DAMAGE
   (kW/m, hazard output)   (kW/m^2, after geometry)    (deg C of the part)         (DR)

   hail:   stone kinetic energy  -->  impact force at panel  -->  glass stress  -->  DAMAGE
   flood:  water depth           -->  hydrostatic load/ingress -->  equipment short --> DAMAGE
   wind:   3-s gust              -->  aerodynamic load on member --> stress      -->  DAMAGE

   the x-axis can sit at ANY node. they trade off the SAME way every time:
```

```
   UPSTREAM (hazard output)        <---------------->     DOWNSTREAM (at the component)

   + matches the HAZARD data you have      |   + closer to the actual DAMAGE physics
     (FSim emits fireline intensity)       |     (temperature/stress IS what breaks the part)
   + one curve travels across equipment    |   + more mechanistically honest
   - hides the coupling (geometry,         |   - REQUIRES a coupling model to reach the node
     exposure, material) inside the curve  |     (intensity -> temp needs assumptions + data)
```

> **The chain-position rule `[OURS]`.** Put the x-axis at the **most-downstream node on the causal
> chain that your hazard layer can actually deliver as data.** Go as close to the damage as the data
> lets you; no closer. Everything between that node and the damage is absorbed into the *curve* (and
> its conditioners) — not the axis. You pick the axis the data can *speak*.

This is the `hazard_asset_specificity` standard-interface idea applied to the x-axis: the axis sits
at the **seam where hazard data is emitted**, and the downstream physics lives *inside* the curve.

**Worked — wildfire `[OURS]`.** FSim emits **fireline intensity**, so fireline intensity *is* the
axis — not because component temperature wouldn't be more honest (it would), but because temperature
is downstream of a coupling model (intensity → heat-flux → temp) we'd have to build *and feed*,
while fireline intensity is handed to us. The intensity→temperature physics lives inside the curve.

**The coherence consequence (ties to §6) `[OURS]`.** Whatever node you pick, the variables *upstream*
of it that you folded away must not silently become forgotten conditioners. Wildfire-on-fireline-
intensity means distance-from-flame and exposure-geometry now live *inside* the curve — so either the
curve is calibrated for a representative geometry (flag it as a conditioner, §6) or you've hidden a
variable. Moving the axis **upstream** increases what's hidden in the curve and the conditioner list;
moving it **downstream** decreases it but demands more coupling. Same "where does the complexity live"
trade as everywhere else.

---

## 6 · Q-x3 — conditioning variables are NOT an x-axis `[OURS]`

The awkward middle from the very start of our whole damage discussion. Stow angle, prior damage,
panel age — these change how intensity maps to damage, but they are **not** hazard intensity and do
**not** belong on the x-axis. Putting them there conflates "how hard the hazard hit" with "what state
the asset was in."

```
   THREE different roles, kept separate:

   x-AXIS         : hazard INTENSITY (what the event did)          -> hail KE, flood depth, gust
   CONDITIONER    : asset STATE at event time (modulates the map)  -> stow angle, prior damage
   CURVE-SELECTOR : fixed asset ATTRIBUTE (picks the curve)        -> glass thickness, tracker type
```

A conditioner acts on the curve in one of three ways (the §07 question, parked there): shift x₀,
fork the curve, or scale DR. The point *here* is only: **it is not a second x-axis.** It's a
parameter *of* the curve, not an *input dimension* of it. And the nasty case — stow angle correlates
with the hazard (you stow *because* hail is forecast) — is a *conditioning* problem, not an
axis-dimensionality problem, so it stays out of this doc and lives in [component-depth (parked)](07_component_attribute_depth.md).

> Keeping Q-x3 off the x-axis is what stops the dimensionality from exploding. If conditioners were
> axes, every curve would be 5-D. They're not axes; they're modifiers.

---

## 7 · Per-hazard map (resolved for v1)

Both rules applied to the in-scope damage hazards. Q-x1 (how many) and a first Q-x2b (where on the
chain, data-driven). These are the v1 axis assignments, not hypotheses.

| Hazard × asset | Q-x1: axes | Escape / reason | x-axis (v1) + chain node |
|---|---|---|---|
| **Hail × solar** | univariate | E1 composite KE; count→frequency | **kinetic energy / MESH** (hazard-output node) |
| **Tornado/strong wind × wind** | univariate | E1 gust as peak; fatigue→cross-event→disruption | **3-s gust** (hazard-output node) |
| **Flood × solar** | two univariate | E2 split: depth→electricals, velocity→foundation | **depth** & **velocity**, summed |
| **Wildfire × solar** | univariate (v1) | E1 fireline intensity; residence-time 2-D **deferred** (§5a) | **fireline intensity** (FSim-emitted node) |
| **Hurricane × {s,w}** | split | E2: wind→structure, surge/rain→flood pathway | **gust** + flood pathway (cross-linked, per catalog) |
| **Winter ice/snow × {s,w}** | univariate | E1 gravity load as composite | **areal load (kPa)** (hazard-output node) |

The recurring pattern, now confirmed: **E1 collapses most, E2 splits the rest, and every leftover
"second axis" candidate resolves to duration (→ disruption or deferred) or count (→ frequency).** The
v1 conclusion is therefore clean: *in-scope physical damage curves are univariate, on the doc-08
grain, with at most a per-part axis split (flood) — and the single genuine 2-D surface (wildfire
residence time) is deferred.*

---

## 8 · What this commits us to

- **Univariate by default (Q-x1).** A second axis must survive **both escapes** (composite-collapse,
  part-split) to earn its place.
- **Most apparent multivariate-ness dissolves at the doc-08 grain** — different parts respond to
  different variables → separate univariate curves, summed.
- **Duration is peak-captured or disruption-side** for every in-scope pair except wildfire
  burn-through, which is the **one genuine 2-D case, deferred from v1** (§5a) — so **v1 is univariate
  throughout.**
- **Chain-position rule (Q-x2b):** the x-axis sits at the **most-downstream node the hazard data can
  deliver**; downstream physics lives inside the curve. Wildfire → fireline intensity (FSim-emitted).
- **Conditioners (stow, age, prior damage) are NOT axes** — they're curve modifiers (§6), parked to
  [component-depth (parked)](07_component_attribute_depth.md). Whatever the axis folds away upstream must be tracked as a
  conditioner, not lost.
- **Payoff for [`05`](05_emit_object.md):** representation can assume a **univariate** input, keeping
  "scalar vs. modes vs. distribution" a clean 1-D question — with one flagged 2-D exception (wildfire)
  it can ignore for v1.

---

## 9 · Open / revisit triggers

- **Wildfire residence-time materiality.** Is residence-time a *first-order* lever on fire damage, or
  second-order like flood corrosion? If second-order, wildfire is cleanly univariate and the 2-D case
  vanishes entirely; if first-order, the deferred 2-D extension (§5a) becomes higher priority. A fire-
  physics / FSim-data question — the one genuinely open item.
- **Composite metric validity (Q-x2a).** When E1 collapses to a composite (hail KE, fireline
  intensity, areal load), is the combiner *real physics* (KE = ½mv²) or a convenient average that
  hides a metric choice? E1 is only a clean escape if the combiner is principled.
- **Chain-position vs the conditioner ledger.** Each upstream-axis choice (§5b) pushes variables into
  the curve as implicit conditioners. Confirm per cell that none are silently dropped (the §6 tie-in).
- **The hurricane cross-link.** Hurricane splits into wind + flood-pathway (E2); confirm the x-axis
  split matches the catalog's surge↔coastal-flood primary/secondary structure rather than inventing a
  parallel one.

---

## 10 · Status

🟢 **Near-final.** Two rules established and applied across all in-scope pairs: **Q-x1 parsimony**
(univariate by default; a second axis survives only by failing both escapes — and after the duration
analysis, *none* do for v1) and **Q-x2b chain-position** (axis at the most-downstream node the hazard
data delivers). Result: **every v1 damage curve is univariate**, with wildfire residence-time the one
named, deferred 2-D case. Conditioners are kept off the axis (§6). This hands [`05`](05_emit_object.md)
a clean univariate input. Remaining open items (§9) are refinements, not blockers — chiefly whether
wildfire residence-time is material enough to pull its deferred 2-D extension forward.

*Links:* [`05` emit object](05_emit_object.md) (the consumer) · [`01` grain](01_granularity.md)
(does the heavy lifting via E2) · [component-depth (parked)](07_component_attribute_depth.md) (conditioners) ·
[scope-edges (parked)](06_financial_terms_and_scope_edges.md) (duration/disruption boundary) ·
`hazard_asset_specificity` (dual test + standard interface) · `Hazard_Data_Reference` (two-track scope).
