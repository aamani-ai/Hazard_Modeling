# 04 · Curation & derivation — how a damage curve actually gets built  🟡 GUIDE

A **guide and a map**, not a library of curves. This doc reasons out *how* a damage curve is
derived for a hazard-subcomponent — the evidence hierarchy, how standards anchor it, the
derive-proximate/parameterize-distal mechanism, and the **functional-form question** (smooth vs.
step vs. discrete states) framed as a *rule for choosing*, not a pre-decided answer. It sits before
[`05`](05_emit_object.md) in the dependency chain, because **how you curate constrains what you can
emit.** The specific curves are produced later, *by running this guide* — per hazard, with
provenance. Same relationship [`03`](03_valuation_guide.md) has to the value database: reason out the
*system* first, fill it cell-by-cell later.

*Source key:* the reference set (the derivation guide + the fragility/vulnerability literature) is
**input, not authority** (P3) — we use its *process structure*, reason past its *default
conventions*; principles = `basics_spot_on`, `system_coherence_over_local_elegance`,
`hazard_asset_specificity`, and the standing **parsimony / primitive-aversion** discipline (don't add
representational complexity the evidence doesn't force). `[OURS]` derived; `[REF]` inherited;
`[SRC]` from the literature survey.

> **The governing posture (P3 + parsimony).** The field's *answers* — "use a lognormal CDF," "use
> DS1–DS4 at 10/50/95%" — are **assumptions made for a purpose**, not truths. We borrow the field's
> *method skeleton* and *evidence discipline*; we **reason past** its default forms. And per our
> standing rule, the **simplest curation the evidence supports is always the preferred option** — a
> richer form must *earn* its place, exactly as a grouping primitive had to in [`01`](01_granularity.md).

---

## 1 · What this guide is for, and the two "shape" questions it untangles

"What shape is the damage curve?" is two different questions, and conflating them is the usual mess:

```
   SHAPE-1  the FUNCTIONAL FORM of the curve         <- THIS doc (curation)
            smooth sigmoid? step? piecewise? discrete states?
            a question about HOW THE CURVE IS BUILT from evidence.

   SHAPE-2  the EMIT OBJECT at a given intensity      <- doc 05 (representation)
            scalar? spread? P(states)? distribution?
            a question about WHAT TRAVELS DOWNSTREAM to the loss engine.
```

They are linked and sequential: **curation (SHAPE-1) constrains representation (SHAPE-2).** If the
evidence yields discrete damage states, a state-vector emit is natural; if it yields a fitted mean
sigmoid, a scalar-or-spread emit is natural. So curation comes first, and hands [`05`](05_emit_object.md)
its input. This guide answers SHAPE-1 and names the handoff.

---

## 2 · The evidence hierarchy — the backbone `[SRC + OURS]`

The field universally classifies damage-function derivation by its **evidence source**, and the
classes form a strength ordering. This is the genuinely authoritative, reusable structure from the
literature (it recurs identically across seismic, flood, wind, volcanic studies) `[SRC]`:

```
   STRONGER  (more direct, more defensible)
      |
      |  EMPIRICAL      observed loss/damage data -> fit a function
      |                 best when events are common; rare for RE assets
      |  ANALYTICAL     physics / structural modelling -> derive response
      |                 (component thermal thresholds, fracture mechanics, load analysis)
      |  STANDARDS      certified ratings / test limits (IEC, ASCE, IP) -> anchor regions
      |                 NOT the curve -- BOUNDARY CONDITIONS (see §4)
      |  EXPERT JUDGMENT structured elicitation -> fill where data/physics run out
      |                 legitimate, but MUST be labeled as such
      v
   WEAKER  (HYBRID = a principled blend, which is what most real curves actually are)
```

> **The hierarchy rule `[OURS]`.** Derive each curve from the **strongest evidence available at its
> grain**, and **label every input by its class.** A curve is a *blend* of classes (hybrid is the
> norm, not the exception) — the deliverable is not "the curve" but "the curve *plus the provenance
> of each piece of it.*" This is `basics_spot_on` applied to curation: provenance is the known-answer
> check for a derived curve. An unlabeled curve is a plausible-but-unverifiable one.

This mirrors [`03`](03_valuation_guide.md)'s value-source discipline exactly: characterize the
source, trust it within its class, carry provenance. Curation and valuation are the same *kind* of
guide, one topic apart.

---

## 3 · The derivation method skeleton (the reusable pattern) `[SRC → OURS]`

The field's method skeleton is good and we adopt its *structure* (reasoning past its default
numbers). Run this per hazard-subcomponent; keep each step short and auditable:

```
   A. SCOPE        hazard / subcomponent / use-case (screening vs pricing; physical-damage only).
   B. DEFINE       what the curve represents: expected damage fraction vs intensity, CONDITIONAL on
                   stated exposure assumptions. NOT a certification limit.
   C. EVIDENCE     gather by class (§2), strongest-first, each piece labeled.
   D. ANCHOR       standards/ratings fix the no-damage and low-damage regions (§4) -- boundary
                   conditions, not the curve.
   E. BRIDGE       hazard output -> component-relevant stress (the chain, doc 02 §5b): e.g. fireline
                   intensity -> heat flux -> heating dose; gust -> load; depth -> ingress.
   F. COMPONENT    per failure-unit (doc 01): threshold(s) + damage behaviour, from the evidence.
   G. AGGREGATE    Asset_DR = Σ wᵢ·DRᵢ (doc 01 summation). The sigmoid usually EMERGES from
                   aggregation -- it is not assumed.
   H. FORM         choose the functional form by the §5 rule (NOT a default lognormal).
   I. UNCERTAINTY  state dominant uncertainties; define validation + update triggers.
```

The key `[OURS]` edits to the field's skeleton: step **D** demotes standards to boundary conditions
(§4); step **E** uses our chain-position rule from [`02`](02_x_axis_intensity_variable.md) rather than
the field's fuzzier "trade-off triangle"; step **G** notes the sigmoid *emerges* (so we don't impose
one); step **H** is a *rule*, not the field's reflexive lognormal default.

---

## 4 · Standards are boundary conditions, not the curve `[OURS, lifted from ref]`

A genuinely sharp idea worth making first-class: certified ratings and test standards **anchor the
curve's regions** but do **not** give you the curve.

```
   DR
    |                                        ,---  saturation (from aggregation, doc 01)
    |                                    ,--'
    |                              ,----'
    |        anchored "no-damage"  |          <- STANDARD fixes WHERE damage onset begins
    |   _________________________,-'             (IEC hail test; IP flood ingress; ASCE wind rating)
    +--|------------------------|----------------> intensity
       0                    rating threshold
       \__ standard says "survives up to here" __/   ... but says NOTHING about the shape ABOVE it.
```

- **Hail** — IEC 61215 (25 mm ice ball @ 23 m/s) anchors a minimum resistance level `[SRC]`.
- **Wind** — ASCE 7 design wind / certified mount ratings anchor the low-damage region `[SRC]`.
- **Flood** — IP ingress ratings anchor the ingress threshold — but say nothing about
  duration/corrosion above it `[SRC]`.
- **Wildfire** — certified operating temperature ranges (IEC 61215/62109) anchor the no-damage region `[SRC]`.

> **The anchor rule `[OURS]`.** Use a standard to pin the region it certifies (usually "no/low
> damage up to the rated level"); derive the shape *above* that from analytical/empirical evidence.
> Never mistake a certification limit for a damage function — it's one boundary point, not the curve.

---

## 5 · The functional-form decision — a RULE, not a default `[OURS]`

The literature's reflex is a **lognormal CDF** `[SRC]` (the seismic-fragility default). Per P3 we do
**not** inherit that. The form is *chosen* by a rule, parsimony-first — the same discipline as the
axis rule in [`02`](02_x_axis_intensity_variable.md) and the grouping rule in [`01`](01_granularity.md).

```
   THE FORM LADDER (climb only when the evidence/use forces it):

   [1] STEP / THRESHOLD    one threshold, binary-ish. simplest. honest when evidence is a single
       |                   rated limit and little else (a standards-anchored screening curve).
   [2] SMOOTH SIGMOID      a continuous mean curve (logistic or lognormal-CDF). the DEFAULT WORKING
       |                   form -- but note it usually EMERGES from aggregating component thresholds
       |                   (doc 01 §G), so you often get it for free rather than assuming it.
   [3] DISCRETE STATES     P(none/slight/mod/extensive/complete) + a state->cost map. natural when
       |                   the EVIDENCE is fragility-derived (state probabilities are what's observed).
   [4] FULL DISTRIBUTION   a distribution of DR at each intensity. richest; most sourcing.
```

> **The form rule `[OURS]`.** Choose the **simplest form the evidence yields and the use-case
> requires.** Specifically:
> - **Let the evidence set the floor.** Fragility-derived evidence *natively* gives states (rung 3);
>   a published mean-damage curve gives a sigmoid (rung 2); a lone rated limit gives a step (rung 1).
>   Don't manufacture a form the evidence can't support.
> - **Let the use-case set the ceiling.** Screening tolerates a step; the distinction that matters for
>   the *metric* (doc 05/06) may demand the spread. Don't climb past what the deliverable needs.
> - **Don't default to lognormal.** It's the field's habit, not a law. Logistic is fine for screening;
>   the sigmoid often *emerges* from aggregation; states are right when the evidence is fragility-native.

This keeps form-choice a transferable *rule* (like every other decision in this set) rather than a
per-hazard guess — and it makes the simplest form the default, complexity earned.

### 5.1 · The crucial link to doc 01: the sigmoid usually *emerges*

A point the literature half-makes and we sharpen: when you aggregate component/failure-unit
thresholds (doc 01's `Σ wᵢ·DRᵢ`), a smooth S-shape **falls out** of the staggered thresholds —
different units failing at different intensities sum into a sigmoid `[SRC + OURS]`. So rung 2 is
often **not an assumption** you impose but a **consequence** of the aggregation you already do.
Fitting an explicit sigmoid (step H) is then optional smoothing for speed, not a modelling claim.

---

## 6 · Derive proximate, parameterize distal `[OURS, lifted from ref]`

The mechanism that makes the chain-position rule ([`02`](02_x_axis_intensity_variable.md)) *buildable*:

```
   DERIVE at a PROXIMATE node (close to damage, where physics is clean):
        e.g. "component fails when T > 200°C"  (analytical, Level 4)
                              |
                              v   bake the physics in
   PARAMETERIZE at a DISTAL node (where the hazard data lives, doc 02):
        DR(fireline_intensity) = L / (1 + exp(-k(I - I₀)))   (the curve M3 actually uses)
```

You reason about failure where the physics is honest (component temperature, fracture stress), then
**express the result as a function of the variable your hazard layer delivers** (intensity, gust,
depth). The proximate physics is *baked into* the distal curve. This is how step E and step H connect:
derive at Level 4, parameterize at Level 2.

---

## 7 · Hazard-by-hazard — which evidence class leads (a map, not the curves) `[SRC]`

Per `hazard_asset_specificity`, the *feasible* derivation differs by hazard. This maps which class
leads where — it does **not** give the curves (those are run later):

| Hazard × asset | Strongest available evidence | Leading method | Honest confidence |
|---|---|---|---|
| **Hail × solar** | empirical (common events, claims data) + lab (IEC ice-ball) + clean physics (KE→fracture) | **empirical-led**, physics-supported | med-high |
| **Wind × {s,w}** | mature structural eng (ASCE, wind tunnel) + adaptable HAZUS curves | **analytical/standards-led**, empirically validated | med-high |
| **Wildfire × solar** | component temp standards (IEC) + heat-transfer physics; **few RE loss events** | **analytical-led** (component aggregation), expert-refined | medium |
| **Flood × solar** | IP ratings (ingress anchor) + depth-damage literature; duration poorly captured | **standards-anchored + analytical**; duration is the gap | med-low |
| **Tornado × wind** | sparse; extreme-intensity → near-total, physics-bounded | **analytical/bounding** | low-med |

The recurring honest note `[SRC]`: **no RE-specific empirically-calibrated curves exist** for most of
these — derivation with labeled judgment is the state of the field, not a failure. Transparency about
provenance is the competitive posture (and the `basics_spot_on` posture).

---

## 8 · What the curation deliverable should look like (the spec)

The eventual per-curve artifact (produced by running this guide) should carry:

```
   a per-(hazard × failure-unit) CURVE record:

   scope            hazard, failure-unit (doc 01), use-case, physical-damage-only
   x-axis           the intensity variable + chain node (doc 02): e.g. fireline intensity
   form             step | sigmoid | states | distribution  -- chosen by §5 rule, justified
   parameters       L (cap, from value-allocation doc 03), x₀, k  (or state thresholds)
   evidence_log     each parameter -> its class (empirical/analytical/standards/expert) + source
   anchors          which standard fixes which region (§4)
   bridge           the proximate→distal derivation (§6), assumptions explicit
   uncertainty      dominant drivers + a stated ± band
   emit_handoff     what this curve emits to doc 05 (scalar/spread/states) -- set by `form`
   validation       backtest plan + update triggers
```

The non-negotiables: **every parameter labeled by evidence class** (§2), **form justified by the
§5 rule** (not defaulted), **anchors named** (§4), **provenance complete**. This is the curation
analogue of [`03`](03_valuation_guide.md)'s value-share spec.

---

## 9 · How this composes end-to-end (coherence check)

```
   evidence (by class, strongest-first)
        -> anchored by standards (boundary conditions, §4)
        -> bridged hazard-output -> component-stress (doc 02 chain)
        -> per failure-unit threshold/behaviour (doc 01 grain)
        -> aggregated Σ wᵢ·DRᵢ (sigmoid emerges, §5.1)
        -> form chosen by the §5 rule (simplest the evidence yields)
        -> emit object handed to doc 05 (form sets scalar/spread/states)
        -> metrics honest per doc 06 (the form/spread decides which)
```

Every stage clears, and curation now explicitly *feeds* the emit object rather than being assumed by
it. The dependency that was implicit in the old `01`-draft is now made first.

---

## 10 · What this guide commits us to

- Derivation is **evidence-class-ordered** (empirical > analytical > standards > expert), every input
  **labeled**, hybrid the norm, **provenance is the deliverable**.
- **Standards anchor regions, they are not the curve** (§4).
- **Functional form is chosen by a parsimony rule** (§5) — simplest the evidence yields and the
  use-case needs; **no reflexive lognormal**; the sigmoid usually *emerges* from aggregation.
- **Derive proximate, parameterize distal** (§6) — the mechanism behind the chain-position rule.
- Curation **constrains** the emit object (SHAPE-1 → SHAPE-2); this guide hands [`05`](05_emit_object.md)
  its input.
- Per P3: the reference's *process* is used; its *default conventions* (lognormal, fixed DS ratios)
  are reasoned past, not inherited.

**Parked / downstream:** the actual curves (run this guide per cell, later); the emit-object decision
([`05`](05_emit_object.md)); which metrics are honest ([`06`](06_metrics_and_tail_honesty.md)).

---

## 11 · Open / revisit triggers

- **Where does the spread come from?** This guide derives the *mean* curve well (the field's strength)
  but the secondary-uncertainty/spread that [`05`](05_emit_object.md) needs for tail metrics is
  thinner in the evidence. Naming the spread's source per hazard is the genuine open gap (and the
  boundary between this guide's purpose and doc 05's).
- **State→cost map for fragility-derived cells.** Rung 3 needs damage-state→cost-ratio mapping; the
  field's DS ratios (10/50/95%) are a *convention to adopt-or-reject*, not inherit — decide per cell.
- **Flood duration.** The depth-damage literature is weak on duration/corrosion (a known field gap);
  our flood curve must flag it rather than paper it (ties to doc 02's flood multi-axis note).
- **RE-specific empirical scarcity.** Most cells will be analytical/expert-led at first; the update
  trigger is loss-event accumulation. The honest confidence bands (§7) must travel with the curves.

---

## 12 · Status

🟡 **Guide drafted; derivation terrain surveyed, curves deliberately not built.** Curation is framed
as an evidence-class-ordered derivation with standards as boundary conditions, a *parsimony rule* for
functional form (not the field's reflexive lognormal), and the derive-proximate/parameterize-distal
mechanism — all per P3 (use the field's process, reason past its defaults) and primitive-aversion
(simplest form the evidence supports). The load-bearing results: **provenance is the deliverable**,
**form is chosen not defaulted**, and **curation constrains the emit object** — so this guide now
sits *before* [`05`](05_emit_object.md) and hands it a typed input. The genuine open gap (§11) is
where the *spread* comes from — the seam to doc 05.

*Links:* [`01 granularity`](01_granularity.md) (the failure-unit grain) ·
[`02 x-axis`](02_x_axis_intensity_variable.md) (chain node + the bridge) ·
[`03 valuation`](03_valuation_guide.md) (the cap L; sibling guide) ·
[`05 emit object`](05_emit_object.md) (what curation hands off) ·
[`06 metrics`](06_metrics_and_tail_honesty.md) · `basics_spot_on` · `reference_is_input_not_authority`
(P3 — the reference is input) · the derivation guide + fragility/vulnerability literature (input).
