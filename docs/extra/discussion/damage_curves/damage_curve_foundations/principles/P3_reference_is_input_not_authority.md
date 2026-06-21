# Reference Is Input, Not Authority — Treat What You're Handed as Evidence

*How to treat the things a project hands you — a schema, a dataset, a standard, a built artifact,
your own prior draft — as **input to reasoning**, not as the conclusion. The discipline of using a
reference for what it's good for, and re-deriving what it isn't.*

Every project arrives pre-loaded with material that *looks* authoritative: an existing
decomposition, a canonical dataset, an inherited model, a doc someone already wrote. The pull is to
treat these as settled ground and build on top. But each was built for *a* purpose, and that purpose
is rarely *your* purpose. Treat the reference as evidence to reason *from*, never as the answer to
reason *to*.

---

## Why this document exists

A reference carries an aura of authority that is often unearned for the question in front of you.
The asset schema looks like it should define the damage grain. The capex dataset looks like it
should hand you the value weights. The built cell looks like it already decided the method. The
prior draft looks like it settled the question.

In every one of those cases, treating the reference as truth would have introduced a silent error —
not because the reference was *wrong*, but because it was *right for a different question.* The
schema was built for procurement, not failure; the dataset was built for cost-tracking, not
at-risk-value; the built cell improvised a method it never named; the prior draft reached a
conclusion a sharper test would overturn.

This document exists because the failure mode is invisible: inheriting a reference's answer feels
like *building on solid ground*, right up until the ground turns out to have been poured for a
different building.

---

## The real incidents: four references, four correct demotions

This is the observed pattern of how the damage-layer work actually treated its inputs.

> **The substrate schema → vocabulary, not the damage answer.** The asset decomposition
> (subsystem → component) is organized by *what you procure and can catalog.* It was tempting to
> adopt its boundaries as the damage grain. Treating it as *vocabulary and validity-grammar*
> (borrow the names, respect the legal parts list) while *re-deriving* the failure grain from
> mechanism was the correct move. Where the two disagreed, the disagreement was information.

> **The cost datasets (NREL/LBNL) → terrain to characterize, not numbers to mine.** The canonical
> capex sources are authoritative *on cost* — and they disagree with each other on the *denominator*
> (one excludes interconnection, another includes it). Treating them as a landscape to survey (grain,
> basis, vintage, trust) rather than a well to draw final values from is what surfaced the basis
> problem instead of burying it.

> **The built cells → evidence, not authority.** The three built damage cells (hail, wildfire, wind)
> already improvised methods — a 6-subsystem blend, a two-curve fork. Treating those as *evidence of
> what the physics demanded* (the wildfire blend reaching across subsystems was a real signal) rather
> than as *the settled method* let us name the underlying concept the cells had only improvised.

> **Our own prior drafts → checkpoints, not conclusions.** The granularity doc's first two drafts
> recommended building a primitive. Treating our *own* prior reasoning as a reference to be
> re-examined — not a decision to be defended — is what allowed the reversal when a sharper test
> arrived.

The pattern: each reference was *kept for what it was good for* and *demoted from authority on the
question it wasn't built to answer.* None was discarded; none was obeyed.

---

## The principle: use the reference for its purpose, re-derive the rest

> **The principle.** A reference is evidence, scoped to the purpose it was built for. Use it for
> *that* — borrow its vocabulary, trust it within its domain, build on its validity grammar. For any
> question it was *not* built to answer, treat its apparent answer as a *hypothesis to test against
> your own reasoning*, not a conclusion to inherit. When the reference and your reasoning disagree,
> that disagreement is **information about the boundary between their purpose and yours** — not an
> error to reconcile away in the reference's favor.

The two halves are equally important, and the discipline is in holding both:

- **Don't discard it.** Re-deriving everything from scratch when a perfectly good vocabulary,
  standard, or dataset exists is its own waste — and it throws away the genuine authority the
  reference *does* carry within its scope. Inventing parallel names for parts that already have good
  names is not rigor; it's reinvention.
- **Don't obey it.** Adopting a reference's answer to a question it wasn't built for imports a silent,
  purpose-mismatched error. The schema's grain, the dataset's denominator, the cell's method — each
  must be *earned* against your own purpose, not assumed from the reference's authority.

The skill is knowing *which question the reference actually answers* — and being precise that its
authority ends at that boundary.

---

## The rule: name the reference's purpose before you use its answer

> **The rule.** Before adopting any number, boundary, or method from a reference, state what the
> reference was *built to do.* If that purpose matches your question, use it directly. If it doesn't,
> the reference is input — characterize it (what it's good for, on what basis, how much to trust),
> and re-derive the actual answer yourself. A value, grain, or method adopted without naming the
> reference's purpose is an unexamined inheritance.

The corollary: **provenance is part of the value.** A number carried from a reference travels with
its source, its basis, and its trust tier — never as a bare figure that has shed the context that
tells you when it stops being true. (A capex share without its basis is three numbers wearing a
trench coat.)

---

## The anti-pattern: inheriting the answer because the reference looked authoritative

> **The anti-pattern.** Adopting a reference's boundary, number, or method because the reference is
> *official* — the canonical schema, the standard dataset, the prior decision — without checking
> whether it was built to answer *your* question. The authority is real but *scoped*, and borrowing
> it past its scope imports the reference's purpose along with its data.

The tell is the phrase "well, the schema already says…" or "the standard dataset has…" used to *end*
a question rather than *inform* it. The reference saying something is the start of the reasoning, not
its conclusion — especially when the reference is your own past work, where the pull to defend the
prior decision is strongest.

---

## Caveats and honest limitations

1. **Some references *are* authoritative for your question — use them directly.** The scope catalog
   is authoritative on what's in scope; the standard is authoritative on its own definitions. The
   principle isn't reflexive skepticism — it's *purpose-matching.* When the purposes align, inherit
   freely.
2. **Re-derivation has a cost; spend it where the purpose-gap is real.** Don't re-derive what the
   reference genuinely settles. The discipline is to find the *boundary* of the reference's purpose
   and re-derive only across it — not to distrust everything as a posture.
3. **A placeholder-with-provenance beats both a blank and a false-precision number.** When a
   reference can't fully answer your question, a labeled, overridable assumption *sourced from* the
   reference (and flagged as such) is legitimate — better than inventing precision and better than
   leaving a hole. Honesty about what the number *is* matters more than the number being exact.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Standard interface, not standard physics**](hazard_asset_specificity.md) | A reference's vocabulary is often a good *interface* even when its content is wrong for you — borrow the typed names, specialize the content. The substrate-as-vocabulary move is this principle and that one together. |
| [**Basics spot-on**](basics_spot_on.md) | Inheriting a reference's answer unexamined is how a plausible-but-wrong basic enters: it *looks* authoritative. Provenance — naming the source and basis — is the known-answer check applied to inherited values. |
| [**Discussion before commitment**](discussion_before_commitment.md) | Treating your own prior draft as a reference-to-re-examine rather than a decision-to-defend is what lets a discussion reverse its own earlier conclusion. The two principles guard the same drift from opposite sides. |

---

## Summary

Every project hands you material that looks like settled ground — schemas, datasets, standards, built
artifacts, your own past drafts. Each was built for a purpose, and that purpose is usually not yours.
Use the reference for what it was built to do: borrow its vocabulary, trust it within its scope, build
on its grammar. For everything past that scope, treat its apparent answer as a hypothesis to test, not
a conclusion to inherit — and when it disagrees with your reasoning, read the disagreement as
information about the boundary, not as an error to fix in the reference's favor. Don't discard what's
good; don't obey past its purpose. Carry provenance with every value. A reference is the start of the
reasoning, not the end of it.
