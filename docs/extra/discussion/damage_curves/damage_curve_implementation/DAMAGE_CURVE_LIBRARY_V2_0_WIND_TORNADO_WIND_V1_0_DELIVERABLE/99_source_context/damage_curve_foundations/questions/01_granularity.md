# 08 · Damage-curve granularity — how we grain, and why not a failure unit  🟢 DECIDED

The foundational granularity decision for the damage layer, and the reasoning that produced it.
This doc is two things at once: a **guide** (how to choose the grain for any hazard-asset pair) and a
**learning record** (why we considered a new "failure unit" primitive, put it on trial, and
*deliberately did not build it*). The negative result is the more valuable half — it's defensible,
transferable, and it saved a real cost.

It does **not** decide the emit-object shape ([`05`](05_emit_object.md)) or the value-weight
*computation* ([value-allocation (parked)](03_value_allocation_and_tiv.md)); those are parked.

*Source key:* substrate = dev `subsystem_code_lookup` / `component_code_lookup` (asset vocabulary,
**ref not truth**); catalog = `Hazard_Data_Reference` (**authoritative on scope**); principles =
`basics_spot_on`, `hazard_asset_specificity`, `modularity_and_scaling`,
`system_coherence_over_local_elegance`. `[REF]` inherited; `[OURS]` derived here.

---

## TL;DR — the decision in one box

> **Write damage curves at the *subsystem* grain by default. Go finer (or onto a different x-axis)
> only where one mechanism *concentrates* damage in a sub-part or drives it through a *different
> intensity variable*. Cap each curve at its at-risk fraction of value, and *sum* the losses. Do
> NOT build a grouped "failure unit" aggregation object** — because summation already composes
> losses across the asset tree, so grouping only earns its keep when parts genuinely **interact**
> (joint ≠ sum), and no in-scope hazard does that outside of cascade (which is [cascade (parked)](05_aggregation_dependence.md),
> parked). The existing subsystem/component decomposition is **enough**.

```
   for each (hazard, asset):
        |
        +-- per SUBSYSTEM, a curve  DR_s(x)  capped at its at-risk fraction
        |       +-- FINER than subsystem ONLY if the mechanism CONCENTRATES
        |       |     (hail -> module sub-unit inside PV_ARRAY)
        |       +-- DIFFERENT x-axis ONLY if the mechanism differs within the hazard
        |             (flood: electricals on DEPTH, foundation on VELOCITY)
        |
        +-- loss = Σ_s  DR_s(x) · value_s        <-- SUMMATION composes. no grouping object.
        |
        +-- group into a "unit" ONLY IF  joint ≠ sum  (parts interact)
                 +-- in-scope hazards: NONE qualify (interactions are cascade -> doc 05)
                 +-- therefore: NO failure-unit primitive.
```

---

## 1 · The question, and the principle that governed it

The substrate organizes the asset by **what you procure and can catalog** — right for an *asset
model*. The damage model asks a different question ("when this hazard hits, what breaks?"), so we
had to ask whether the asset's decomposition is also the right *damage* grain, or whether damage
needs its own primitive.

The governing rule was `system_coherence_over_local_elegance`:

> The burden of proof is on the **departure**. We already have a working decomposition; a new
> damage-side primitive must show the *whole system* is better off — and we must be willing to come
> back empty if no real, in-scope case forces it.

We were willing. We came back empty. That is the result, and it is a good one.

---

## 2 · The candidate we tested: the "failure unit"

The idea under trial:

> **Failure unit (candidate, NOT adopted).** The smallest set of asset parts that, under a given
> hazard mechanism, fail *together* — assigned one damage ratio on one intensity relationship.
> Hazard-relative: the same parts regroup differently under different hazards.

It was seductive. The same solar parts *do* regroup by hazard — hail concentrates on module glass,
flood takes everything below a waterline, fire takes the flammable slice. The failure set often
**cross-cuts** the subsystem tree: it's a slice across several subsystems, grouped by a principle
(elevation, flammability) the functional tree has no node for. That cross-cutting *felt* like it
forced a new primitive.

It does not. Watching *why* is the lesson.

---

## 3 · The trial — and the two corrections that killed the primitive

### 3.1 · First correction: scope (the lightning misstep) `[OURS]`

The first cross-cut example reached for was **lightning on a wind turbine** — surge follows the
ground path, frying electronics across four subsystems. Geometrically perfect.

It proved nothing. The catalog (`Hazard_Data_Reference`) is authoritative on scope and **lightning
is not an in-scope peril** — it appears once, as an input feature to a hail nowcasting model. A
cross-cut on an out-of-scope hazard is void. (Independently, much lightning loss is
electronics-replacement → *disruption*, not physical damage → fails the scope boundary anyway.)

> Lesson 1 — `basics_spot_on` at the design level: a plausible-but-wrong *example* looks identical
> to a right one until checked against the known answer. The known answer was the scope catalog — a
> system-level fact, not a local argument.

### 3.2 · Second correction: the bar itself (the load-bearing one) `[OURS]`

Even with *in-scope* cross-cuts (flood by elevation, wildfire by flammability), the primitive still
fails — because the test we were using was the wrong test.

```
   WRONG bar (geometric, weak):   "does the failure set cross-cut the subsystem tree?"
   RIGHT bar (interaction, strong): "does summing INDEPENDENT subsystem curves get the JOINT wrong?"
```

The decisive realization: **summation does not require grouping.** If the inverter floods and the
cabling floods, write a curve for each and *add the losses* — you never needed to bundle them into a
named "unit" to sum them. Grouping into an object earns its keep **only** when the joint failure is
**not** the sum of the marginals — i.e. when the parts genuinely **interact** (a shared conditioning
variable that changes the joint, or correlation the independent sum can't represent).

> Lesson 2 (embed forever): **geometric cross-cutting is inert.** The question is never "does the
> set cross the tree?" — it's "does treating the parts as independent-and-additive get the answer
> wrong?" If summation handles it, no grouping object is needed, however much the set cross-cuts.

### 3.3 · Applying the right bar to every in-scope pair

```
   pair               joint ≠ sum?  -> needs grouping object?
   hail x solar       no — concentrates, nests, additive            NO
   high wind x solar  no — additive given uplift intensity          NO
   tornado x wind     no — "bloc" = each subsystem curve SATURATES   NO   (sum still gives ~1.0)
   strong wind x wind no — rotor aero, nests, additive              NO
   FLOOD x solar      no — additive GIVEN depth; each part f_i(depth)NO   (looked like a cross-cut; isn't needed)
   WILDFIRE x solar   its one interaction = ember PROPAGATION        NO*  (*that's CASCADE -> doc 05, parked)

   => NONE of the in-scope pairs need a failure-unit aggregation primitive.
      The two that looked like they did (flood, wildfire) are additive (flood) or
      cascade (wildfire, owned by doc 05). The primitive is not built.
```

---

## 4 · What we keep (the lens — free, transferable)

Retiring the primitive does **not** throw away the exploration. Three things survive — as
*discipline*, not machinery:

| # | Survives as | What it is |
|---|---|---|
| **K1** | **Grain discipline** | Per mechanism, ask: does it *concentrate* (→ resolve finer than subsystem) or run on a *different intensity axis* (→ separate curve)? The reasoning lens, applied when curating each cell. |
| **K2** | **Honest value bookkeeping** | Surface the at-risk fraction `f`; never bury it inside a curve cap where it masquerades as fragility. (A cap of 0.40 *is* a value fact, not a physics fact — label it so.) |
| **K3** | **The bar itself** | "joint ≠ sum?" is the standing test for *any* future grouping primitive. If a later hazard genuinely makes parts interact (non-cascade), revisit — but only then. |

---

## 5 · The grain method (the guide)

For any (hazard, asset), choose curve grain by walking the mechanism through three checks:

```
   mechanism --A--> CONCENTRATION?  does damage concentrate in a sub-part while the rest of the
              |                      subsystem is ~immune?
              |        yes -> resolve FINER than subsystem (hail -> module sub-unit)
              |        no  -> stay at subsystem
              |
              --B--> DISTINCT AXIS?  does a part of this subsystem fail on a DIFFERENT intensity
              |                      variable than the rest, within the same hazard?
              |        yes -> give it its OWN curve on its OWN axis
              |               (flood: FOUNDATION on flow VELOCITY; electricals on DEPTH)
              |        no  -> one axis for the hazard
              |
              --C--> CURATABLE?      can we source a curve at this grain (evidence / standard /
                                     defensible placeholder)?
                       no  -> aggregate UP to the curatable grain and LABEL the smearing.
```

Then always: **cap each curve at its at-risk fraction, and sum.**

```
   loss(x) = Σ_curves  DR_c(x_c) · value_c
   - each curve c may be a subsystem, a finer sub-part, or a same-subsystem-different-axis split
   - x_c is that curve's own intensity variable (depth, velocity, gust, mm hail...)
   - value_c is its at-risk value (subsystem value, or a fraction, placeholder-ok per substrate DD-047/076)
   - the asset tree is the LEDGER; summation is the COMPOSITION. no separate grouping object.
```

### 5.1 · One amendment to the plain subsystem model

The only place the naive "one curve per subsystem" needs stretching: **a subsystem may carry more
than one curve** when it spans more than one mechanism/axis (flood's FOUNDATION-scour-on-velocity
vs the depth-driven electricals). This is *curve resolution*, not a grouping object — the curves
still just sum.

---

## 6 · A pair is a *partition*, not a single curve

A reminder the earlier framing under-stated: a (hazard, asset) maps to **several** curves, not one.
Flood × solar alone has (at least): below-waterline electricals on depth, foundation on velocity,
and the dry/immune elevated modules (DR ≈ 0). The immune parts are kept *explicitly* (as DR ≈ 0
contributors) so the partition stays **exhaustive and non-overlapping** — every at-risk dollar in
exactly one curve's value base, or the sum either double-counts (overlap) or leaks (gap).

```
   exhaustive + non-overlapping tiling of asset value, per hazard:

   [ curve1.value | curve2.value | ... | immune.value(DR=0) ]  == TIV (reconciled)
        no part of value appears twice;  no at-risk part is missing.
```

This is a *bookkeeping discipline* (K2), not a new object. It's how the dollar number reconciles
against one value ledger — the `system_coherence` "value reconciliation" stage made concrete.

---

## 7 · How this composes end-to-end (the coherence check)

```
   curation:        curves curated at subsystem grain (or finer per §5), placeholders labeled
   curve:           each emits DR on its own axis (shape = doc 01's call, parked)
   application:     loss = Σ DR_c(x_c)·value_c   — pure summation, no bespoke glue
   multi-hazard:    each hazard has its OWN partition over the SAME parts; no shared grouping
                    object to keep consistent -> hazards stay independent (modularity seam intact)
   value reconcile: exhaustive non-overlapping tiling (§6) -> sums reconcile to TIV
```

Every stage clears. The asset tree is untouched; adding a hazard adds curves, not structure. This
is *why* the negative result is the coherent one — the simpler design composes better, not just
cheaper.

---

## 8 · What this commits us to

- Damage grain = **subsystem by default**, finer or different-axis **only** on concentration /
  distinct-mechanism (the §5 A→B→C method).
- **Cap at at-risk fraction, sum the losses.** The asset tree is the ledger; summation composes.
- **No failure-unit aggregation primitive**, and **no sub-subsystem value ledger** beyond the
  at-risk fractions the curves already need (the cross-cut grouping that would have forced a full
  ledger is not built).
- Keep the **lens** (K1 grain discipline, K2 honest value bookkeeping, K3 the joint≠sum bar).
- Partitions are **exhaustive and non-overlapping** per hazard (§6).

**Still parked (not solving everything at once):** emit shape ([`05`](05_emit_object.md)) · value
*computation* ([value-allocation (parked)](03_value_allocation_and_tiv.md)) · stow mechanism
([component-depth (parked)](07_component_attribute_depth.md)) · **cascade / interaction** ([cascade (parked)](05_aggregation_dependence.md))
— the *one* place a grouping could still be forced, and the place to revisit K3.

---

## 9 · The learning, distilled (why this doc is worth keeping)

1. **Geometric cross-cutting is inert; interaction is the real test.** "Does the failure set cross
   the tree?" is the wrong question. "Does summing independents get the joint wrong?" is the right
   one. Summation composes across the tree without any grouping object. *(Embedded as a standing
   principle.)*
2. **Check examples against system-level facts before trusting them.** The lightning cross-cut was
   flawless and void — scope killed it. A plausible example is not a proof. *(`basics_spot_on`, one
   level up.)*
3. **Slower discussion beats quick conclusions.** The first two drafts of this doc *recommended
   building the primitive.* Continuing to push — "why can't I just use subsystem curves?" — is what
   surfaced the real answer. The willingness to overturn our own recommendation is the deliverable.
4. **A negative result, well-reasoned, is a deliverable.** We are *not* building a thing, and we can
   say exactly why, defensibly, against the in-scope evidence. That is worth more than building it.

---

## 10 · Open / revisit triggers

- **Cascade / interaction ([cascade (parked)](05_aggregation_dependence.md)).** The *only* door left open. If a
  hazard makes parts genuinely interact (joint ≠ sum) in a way that is **not** cascade, the K3 bar
  fires and we revisit a grouping object. Wildfire ember-propagation is the nearest case — and it's
  cascade, so it's cascade's (parked), not this doc's.
- **Multi-axis within a subsystem (§5.1).** Flood depth-vs-velocity is the clean case; watch for
  others where one subsystem needs several axes.
- **The messy middle.** Our concentration cases (hail) are clean. We haven't found the case where
  "concentrate finer?" has no crisp answer. Its absence isn't proof of non-existence.

---

## 11 · Status

🟢 **Decided.** Subsystem-default grain, finer-on-concentration-or-axis, capped and summed, **no
failure-unit primitive.** The candidate primitive was put on trial under `system_coherence`,
survived a scope-grounded misstep (lightning, rejected), and was then retired by the correct bar
(**joint ≠ sum**, which no in-scope pair meets). The existing subsystem/component decomposition is
sufficient; the exploration is kept as a reusable grain guide + learning record. **Ready to move
on** — next live questions: the emit-object shape ([`05`](05_emit_object.md)) and value basis
([value-allocation (parked)](03_value_allocation_and_tiv.md)).

*Links:* [context (parked)](00_context_and_scope.md) · [`05`](05_emit_object.md) · [value-allocation (parked)](03_value_allocation_and_tiv.md) ·
[cascade (parked)](05_aggregation_dependence.md) · `system_coherence_over_local_elegance` ·
`basics_spot_on` · `Hazard_Data_Reference` (scope authority) · substrate (asset vocabulary, ref-not-truth).
