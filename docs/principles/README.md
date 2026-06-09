# Principles

The foundational beliefs this repo is built on. **Not** how-to guides, **not** checklists, **not** API
docs — this folder answers a different question: **why do we build hazard models the way we do?**

Most principles documents are written from aspiration. These are written from a **post-mortem.** This
project is a ground-up rebuild of a hazard model that produced EAL / VaR / PML numbers nobody could
trust — and almost every belief here is a lesson the old model *paid for*. (Full story:
[`../extra/00_scope_and_story.md`](../extra/00_scope_and_story.md).)

---

## The three principles

| File | The principle | The failure it answers |
|------|---------------|------------------------|
| [`hazard_asset_specificity.md`](hazard_asset_specificity.md) | **Standard interface, not standard physics** — specialize where the physics genuinely differs; generalize only the *interface*. | The old model forced one damage curve, one spatial factor, one distribution across perils and assets whose physics are not the same. |
| [`modularity_and_scaling.md`](modularity_and_scaling.md) | **Modular from day one** — a new peril, asset, data source, or operator slots in by *implementing an interface*, not editing a monolith. | A single `disaster_analysis.py` spanned every layer; change meant merge after merge (`bug/fixing_bad_merge`, `fix/bad_merge`…). |
| [`basics_spot_on.md`](basics_spot_on.md) | **Get the basics exactly right** — the foundational math *is* the product; verify it before building anything on top. | The whole collapse: tail metrics computed on the wrong random variable. Patches treated symptoms; the foundation stayed wrong. |

These three are not independent — they reinforce one another, and each page ends with how it connects to
the other two.

## Working sub-areas

Beyond the three foundational principles, this folder also collects **working principles** — how we operate
in a particular mode — in sub-folders:

| Sub-folder | Covers |
|---|---|
| [`notebook_work/`](notebook_work/README.md) | How we work in notebooks, especially **exploratory data notebooks** — interpret every variable (not just display it), understand a source before using it. |

## Principles — and guides

Principles answer **why we build this way**; guides answer **how to do a thing**. They're usually kept
apart, but for tightly interconnected, hands-on work they sometimes **co-locate**: a principle sub-folder
here may also carry an applied **guide** (e.g. a checklist for setting up an exploratory notebook). That's
expected — when the topic is this practical, the *why* and the *how* travel together, so don't be surprised
to find a guide sitting next to a principle in this folder.

---

## Why this folder exists

Every project accumulates mechanics — the runbooks, the "do X to get Y." That work matters, and it lives
elsewhere. But mechanics alone produce a model that is *competent but characterless*: it tells you how to
add a peril, not **why** a peril must be modeled the way it is, or which assumption will quietly corrupt the
tail if you get it wrong.

For *this* project the stakes are sharper than usual. The old model was not lazy work — it was a lot of
real effort built on foundations that were subtly wrong, and the wrongness was invisible until the numbers
were already in front of decisions. Without a principles layer, the next contributor (or the next agent, or
a future version of us) re-derives the values from the code, inherits the decisions without the reasoning,
and re-introduces the exact mistakes this rebuild exists to escape.

This folder is the guardrail against that drift. It is the part of the project meant to outlast any
particular peril, dataset, or framework version.

---

## How to use these documents

- **Building something new** — read the relevant principle *before* writing code. Ask: is this consistent
  with these beliefs? If not, change the approach, or change the principle openly and say why.
- **Reviewing work** — use principles as ground truth. "Does this collapse a random variable to its mean
  before a nonlinearity?" is a better review comment than "the tail looks off."
- **Surprised by a decision** — something that looks over-careful (a per-peril coupling type, a refusal to
  reuse a curve) usually traces to a principle here. If it doesn't, that's a gap worth filling.
- **The project evolves** — principles evolve too, deliberately. Don't silently contradict them; update
  them with the reasoning. How the principles changed is itself useful knowledge.

---

## A note on grounding and tone

Every principle here should be traceable to a **real failure of the old model or a real choice in the
rebuild** — not an abstract ideal. Where a principle cites a number (`175×`, `~12×`, `F/A`), it comes from
the actual incident write-ups in
[`../../hazard_analysis/docs/suggested_architecture/issues/`](../../hazard_analysis/docs/suggested_architecture/issues).
They are written to be read by someone who has never touched this codebase — direct and honest about what
we believe and why, without being preachy. The spirit: *a letter from someone who paid for these lessons
and wants to save you from re-discovering them.*

---

## Provenance

This folder builds on the precursor written inside the old repo —
[`hazard_analysis/docs/suggested_architecture/learning/principles.md`](../../hazard_analysis/docs/suggested_architecture/learning/principles.md)
— which first named **Hazard × Asset Specificity** and **Modular Layer Architecture**. This is the
canonical, evolved home for those, and it adds the third principle explicitly: **basics spot-on**, the one
the old model's collapse made impossible to ignore.
