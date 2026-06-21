# Discussion Before Commitment — Reasoning Is the Cheapest Place to Be Wrong

*Why we argue a foundational choice out, in writing and out loud, before it touches the
architecture — and why the slow conversation is not a tax on the work but the part of the work that
saves the most.*

A model is a tower of choices, and the choices at the bottom are load-bearing for everything above.
A wrong choice caught in discussion costs a paragraph. The same wrong choice caught after it's built
costs a refactor; caught after it ships, it costs a number someone already trusted. The cheapest
place to be wrong is in the reasoning, before anything is built on top — so that is where we spend
the time.

---

## Why this document exists

There is a pull, on every foundational decision, to *get to the answer.* Pick the grain, pick the
representation, pick the value basis, and move on. Discussion feels like delay; a decision feels like
progress.

That instinct is backwards for the choices that matter most. The decisions at the base of the model
are exactly the ones where a fast, plausible answer is most dangerous — because they're the ones
everything else inherits, and they inherit the wrongness *invisibly* (the lesson of `basics_spot_on`).
A foundational choice made quickly and wrongly doesn't announce itself; it sits quietly under the
build until the tail is wrong in front of a decision.

This document exists because, repeatedly, the *slow* conversation is what produced the right answer —
and more than once it overturned the *fast* one we'd already written down.

---

## The real incidents: three times the slow path beat the fast one

This principle isn't aspiration. It's the observed pattern of how the damage-layer foundations
actually got built.

> **The granularity primitive.** A "failure unit" concept was reasoned, drafted, and *recommended* —
> twice. The first two drafts of the granularity doc concluded we should build it. Continuing to push
> — "why can't I just use a subsystem curve and sum?" — surfaced the real test (does summing
> independents get the *joint* wrong?), which the geometric cross-cut argument had been hiding. The
> primitive was retired. **The conclusion reversed because the discussion didn't stop at the first
> defensible answer.**

> **The out-of-scope proof.** A cross-cut example (lightning) was flawless on its own terms and
> *void* — the hazard wasn't in scope. Only grounding the argument against the system's actual scope
> catalog, mid-discussion, caught it. A faster path would have written the void proof into the
> foundation.

> **The over-built emit interface (nearly).** A "ship the tail metrics with a caveat" option looked
> like a fuller deliverable until the discussion connected it to the old model's *exact* failure —
> a confident-but-understated VaR. The slow connection turned a plausible feature into a rejected
> anti-pattern.

In each case the fast answer was *plausible* — defensible, even. The discussion is what separated
plausible from correct. That separation is the entire value.

---

## The principle: reason it out before you build it

> **The principle.** Foundational choices are argued out — in writing, with worked examples, out
> loud — *before* they are committed to the architecture. The discussion is not preamble to the
> work; for a load-bearing choice, the discussion **is** the work. Reasoning is the cheapest place
> to be wrong, so it is where the wrongness should be found and discarded.

What this looks like in practice, and why each piece earns its keep:

- **Write the reasoning down, not just the conclusion.** A discussion doc that records *why* — the
  alternatives, the test that decided, the case that nearly broke it — lets the next person (or the
  next agent, or a later you) inherit the *reasoning*, not just the decision. A bare conclusion gets
  re-litigated from scratch or, worse, trusted blindly.
- **Separate the system from the answer.** The deliverable of a foundational discussion is usually a
  *method* (how to choose the grain, how to pick the axis), not a filled-in table. The per-case
  answers fall out of running the method. A method transfers; a table of answers doesn't.
- **Prefer the slow path on the choices that propagate.** Not everything deserves this. A choice
  local to one cell can be made and revised cheaply. A choice the whole pipeline inherits cannot —
  that is where the slow conversation pays for itself many times over.

---

## The rule: be willing to come back empty

A discussion that can only end one way is not a discussion; it's a ratification. The discipline that
makes the slow path *work* is the genuine willingness to reach the negative conclusion.

> **The rule.** Enter a foundational discussion prepared to *not* build the thing — to come back
> empty, to keep the existing approach, to retire your own proposal. State, up front, the condition
> under which you'd abandon the idea, and mean it. A conclusion you were unwilling to reach is not
> something the discussion earned; it's something you brought in and dressed up.

This is why "we decided *not* to build a primitive, and here is exactly why" is a first-class
deliverable — often a more valuable one than building it, because it's a complication the system now
provably doesn't carry, with the reasoning on record so it stays un-built for the right reasons.

---

## The anti-pattern: the conclusion that arrives too early

> **The anti-pattern.** Treating the first defensible answer as the final one. Reaching a conclusion
> that *holds up* and stopping there — before asking whether it holds up for the right reason,
> whether a sharper test would overturn it, whether the example proving it is even in scope. A
> plausible conclusion arrived at quickly looks identical to a correct one arrived at slowly, right
> up until something downstream breaks.

The tell is a feeling of relief at having *decided.* On a foundational choice, that relief is the
signal to push once more, not to move on. The discussions that mattered most here all had a moment
where the obvious answer was already on the table and the right answer was one more question away.

---

## Caveats and honest limitations

1. **Not every choice earns the slow path.** Discussion has a real cost, and spending it on a
   reversible, local choice is its own waste. The principle is for the *load-bearing* decisions — the
   ones that propagate. Match the depth of the discussion to how far the choice reaches.
2. **Discussion is not deferral.** Arguing a choice out is not the same as never deciding. The slow
   path ends in a *commitment*, recorded and built on; a discussion that never converges is its own
   failure mode. Reason thoroughly, then decide.
3. **More discussion is not always more truth.** Past the point where the alternatives and tests are
   genuinely exhausted, further talk is circling, not converging. The discipline is to push *until
   the deciding test is found*, then stop — not to mistake length for rigor (the sibling of
   `basics_spot_on`'s "more simulation is not more truth").

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Basics spot-on**](basics_spot_on.md) | The reason the slow path is worth it: foundational wrongness is inherited invisibly, so it must be caught *before* the build — and discussion is where it's caught. Discussion is how a basic gets verified as a *choice* before it's verified as a number. |
| [**System-coherence over local elegance**](system_coherence_over_local_elegance.md) | That principle supplies the *content* of a good foundational discussion (does this pay off end-to-end?) and the *willingness to come back empty*; this one is the practice of holding that discussion before committing. |
| [**Modular from day one**](modularity_and_scaling.md) | Discussion produces the *method* and the *interface*; modularity is how that method gets filled one cell at a time. Reason out the seam, then build the implementations. |

---

## Summary

The choices at the base of a model are load-bearing and inherited invisibly, so the cheapest place
to be wrong about them is in the reasoning, before anything is built. Argue foundational choices out —
in writing, with worked examples — and let the deliverable be a *method*, not a bare answer. Be
genuinely willing to come back empty; a discussion that can only ratify isn't one. Treat the first
defensible answer as a checkpoint, not a destination, because plausible-and-quick is indistinguishable
from correct-and-slow until something downstream breaks. The slow conversation is not a tax on the
work. On the decisions that propagate, it *is* the work.
