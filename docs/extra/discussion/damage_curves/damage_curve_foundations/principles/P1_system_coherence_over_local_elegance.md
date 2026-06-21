# System-Coherence Over Local Elegance — The Whole Pipeline Is the Judge

*Why a modeling choice is only as good as its behavior end-to-end — and why the burden of proof
always sits on the new idea, not the existing one. The discipline that keeps a locally-beautiful
decision from quietly breaking the system that has to carry it.*

A model is not a collection of locally-correct stages. It is one chain — curation → curve →
application → multi-hazard aggregation → value reconciliation — and a choice that is more accurate
*in isolation* but breaks coherence *across the chain*, or demands data the system can't produce, is
not an improvement. It is a regression wearing the costume of rigor.

---

## Why this document exists

The first three principles guard against being *wrong*: wrong math (`basics_spot_on`), wrong
generality (`hazard_asset_specificity`), wrong structure (`modularity_and_scaling`). This one guards
against a subtler failure — being *locally right and globally worse.*

It is easy to fall in love with a clean idea. A finer grain that captures the physics better. A
richer representation that carries more uncertainty. A more faithful decomposition. Each can be
genuinely more correct *at its own stage* and still be the wrong call, because the test of a
modeling choice is not "is this stage better?" but "is the **whole system** better off, end to end,
given what it can actually source and compute?"

This principle exists because that question is the one most easily skipped — and skipping it is how
a model accretes locally-justified complexity that no one can source, reconcile, or maintain.

---

## The near-incident: a perfect proof on the wrong ground

This principle was not written from aspiration. It was written from a near-miss that happened while
designing the damage layer — caught, in the open, by the discipline it names.

We were deciding whether the damage layer needed its own granularity primitive (the *failure unit*),
and we needed a worked example of a hazard whose damage **cross-cuts** the asset's functional
decomposition — a failure set that slices across several subsystems, grouped by a principle the tree
has no node for. The example reached for was **lightning on a wind turbine**: a strike's surge
follows the conductive ground path, frying pitch electronics, the power converter, a monitoring
card, and the sacrificial surge device — a flawless cross-cut, organized by electrical connectivity
rather than function.

It was elegant. It was geometrically perfect. And it was **wrong as a proof**, for two reasons that
only surface when you check the choice against the rest of the system:

> **Out of scope.** The authoritative hazard catalog lists the in-scope perils explicitly. Lightning
> is not among them — it appears once, as an *input feature* to a hail nowcasting model, never as a
> peril we model. A cross-cut on an out-of-scope hazard proves nothing about *our* system.
>
> **Out of bounds even if in scope.** Much lightning loss is electronics replacement — "swap the
> fried card" — which sits on the *disruption* side of the scope boundary, not physical destruction.
> It would fail the damage-track test independently.

The proof was locally beautiful and globally void. The fix was not cleverer reasoning; it was
**grounding the choice in the system's own scope catalog** before trusting it. Once we did, the real
proof was sitting in scope the whole time (flood, organized by elevation; wildfire, by flammability)
— quieter, less seductive, and *correct*.

> The lesson is exactly `basics_spot_on`'s, one level up: a plausible-but-wrong *example* looks
> identical to a right one until you check it against the known answer. Here the known answer was the
> scope catalog — a property of the whole system, not of the local argument.

---

## The principle: the whole pipeline is the judge

> **The principle.** A modeling choice is only as good as its behavior *end-to-end* — curation →
> curve → application → multi-hazard aggregation → value reconciliation. A choice that is locally
> more correct but breaks pipeline coherence, demands data the system cannot produce, or contradicts
> a system-level fact (scope, units, the value ledger) is **not** an improvement. The judge is the
> whole chain, never the single stage.

Concretely, before adopting a choice, it must clear the chain, not just its own stage:

- **Curation** — can we actually *source* a curve (or value, or parameter) at this grain? Evidence,
  standard, or defensible placeholder — or are we inventing precision?
- **Application** — does it compose with the stages on either side, or does it need bespoke glue?
- **Multi-hazard** — does it stay coherent when a *second* hazard regroups the same parts, or does it
  silently assume one hazard's view?
- **Value reconciliation** — does the dollar number reconcile against the same value ledger the rest
  of the system uses, or does it carry a private, unreconciled basis?

A choice that wins at its own stage and loses on any of these has not earned adoption.

---

## The rule: the burden of proof is on the departure

There is almost always an *existing* way of doing things — an existing decomposition, an existing
grain, an existing representation. The existing way has a quiet virtue: the rest of the system is
already built to consume it. So the asymmetry is deliberate and non-negotiable.

> **The rule.** When a choice *departs* from what the system already does, the burden of proof is on
> the **departure**, not the incumbent. The departure must show the *whole system* is better off —
> not that one example is prettier. **Prefer the existing approach unless the departure pays for
> itself across the entire chain.** And be willing to come back empty: if the departure can only be
> justified by a contrived or out-of-scope case, the honest conclusion is to *not depart.*

This is what licensed us to put the failure unit *on trial* rather than assume it — and to be
genuinely prepared to convict (drop it to a reasoning lens, or drop it entirely) had no in-scope
pair forced it. A departure you are unwilling to reject is not a proof; it is a preference.

The corollary cuts both ways. When the burden *is* met — when a real, in-scope case forces the
departure and it composes cleanly across the chain — adopt it without flinching. The principle is
not conservatism. It is *earned* change: the existing approach holds the floor until the new one
pays the end-to-end price, and then it yields cleanly.

---

## The anti-pattern: reverse-engineering the proof

The failure mode this principle names is not complexity. It is **motivated reasoning dressed as
rigor** — starting from "this elegant idea must be right" and hunting for the example that justifies
it, instead of letting the system decide whether the idea is needed at all.

> **The anti-pattern.** Falling in love with a local idea and then *reverse-engineering* a
> justification — reaching for whatever example makes it look necessary, even an out-of-scope or
> contrived one, rather than checking honestly whether any *real, in-scope* case forces it. A proof
> you went looking for to confirm a conclusion you'd already drawn is not a proof.

The tell is emotional: when you find yourself *defending* an idea's necessity rather than *testing*
it, you have crossed from reasoning into advocacy. The antidote is to name, up front, the condition
under which you would *abandon* the idea — and to mean it.

---

## Caveats and honest limitations

1. **This is not an excuse for inertia.** "Prefer the existing approach" is a burden-of-proof
   default, not a veto. When the departure clears the chain, it wins — and dragging feet then is its
   own failure. The principle demands *earned* change, not *no* change.
2. **"End-to-end" is bounded by what's decidable now.** You cannot fully evaluate a choice against
   stages you haven't built yet. The discipline is to check it against the stages and system-facts
   you *do* have (scope, units, the value basis, the immediate neighbours), and to *flag* the
   downstream stages it might affect — not to pretend you've cleared a chain you can't yet see.
3. **Local elegance is still a signal — just not a verdict.** A locally beautiful idea is often
   pointing at something real; the principle doesn't say ignore it. It says: don't *adopt* it on
   beauty alone. Test it against the whole pipeline, and let *that* decide.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Basics spot-on**](basics_spot_on.md) | Same epistemic spine, scaled up: `basics_spot_on` checks a *number* against a known answer; this checks a *design choice* against the whole system. The lightning near-miss is its worked example at the design level — plausible-but-wrong, caught by a system-level known answer (the scope catalog). |
| [**Standard interface, not standard physics**](hazard_asset_specificity.md) | That principle says *specialize the physics, standardize the interface*; this one supplies the test for *when a specialization is worth it* — only when it pays off end-to-end. Together they prevent both false generality and unjustified specialization. |
| [**Modular from day one**](modularity_and_scaling.md) | Modularity is *how* a departure stays cheap (adopt the interface now, fill implementations one cell at a time); this principle is *whether* the departure is warranted at all. Structure and justification, the two halves of a sound change. |

---

## Summary

A model is one chain, and the chain is the judge. A choice that is locally more accurate but breaks
coherence, demands unsourceable data, or contradicts a system-level fact is not an improvement — it
is a regression in disguise. The burden of proof sits on every departure from what the system
already does: it must pay for itself across curation, application, multi-hazard aggregation, and
value reconciliation, and you must be willing to walk away if it can only be justified by a
contrived or out-of-scope case. This principle was born from exactly such a case — a flawless proof
on out-of-scope ground, caught by checking it against the system's own scope before trusting it.
Beauty is a hint, not a verdict. **The whole pipeline decides.**
