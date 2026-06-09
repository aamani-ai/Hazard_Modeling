# Learning

*What building the hazard model taught us — the knowledge we paid for in the doing, not the knowledge we
brought in.*

> **Status:** Living — seeded 2026-06-09. *Bloat then prune*: write entries liberally as you hit them; tidy
> every few phases.

---

## What this folder is

`docs/learning_logs/` is the **derived-knowledge tier** — the empirical residue of building. When a notebook, a
decision, or a near-miss teaches us something *the reference docs didn't have*, it lands here as a short,
transferable write-up, so the next peril — or the next engineer, or the next agent — **inherits the lesson
instead of re-discovering it**.

It exists because the references are **reference, not truth** — and the most valuable things we learn are
exactly the ones that *aren't* in them. That knowledge had no home. This is the home.

## How it differs from its siblings

| Folder | Answers | Stance |
|---|---|---|
| [`extra/`](../extra/) · [`google_drive_docs/`](../google_drive_docs/) | *what others established* — reference, ingested | brought-in |
| [`principles/`](../principles/README.md) | *why we build this way* — beliefs | foundational, stable |
| [`plans/`](../plans/) + [`decisions.md`](../plans/hail/decisions.md) | *what we'll do / what we decided for **this** build* | forward-looking + per-build record |
| **`learning_logs/`** *(this folder)* | *what building taught us, for the **next** build* | retrospective, generalizable |

The sharpest line is against `decisions.md`: **a decision is the choice for one build; a learning is the
transferable insight that choice — or its failure — revealed.** `decisions.md` says *"for hail v1 we chose
MRMS-only."* A learning doc says *"a homogeneous record beats a longer inhomogeneous one for a trustworthy λ
— and here's how to spot the trap on the next peril."*

## When a learning earns its place

Write one if **at least one** is true:

1. **Method lesson** — a way of building, or a trap, worth repeating / avoiding on the next peril.
2. **Substantive insight** — a recurring truth worth one canonical write-up instead of re-deriving it.
3. **Forward pointer** — *"when we get to hurricane, watch X."*
4. **Anti-pattern** — a plausible-looking wrong path, with the reason it's wrong.

It does **not** belong here if it's: a build choice → [`decisions.md`](../plans/hail/decisions.md); a belief
→ [`principles/`](../principles/README.md); a reference fact → [`extra/`](../extra/) /
[`google_drive_docs/`](../google_drive_docs/); a definition → the terminology reference.

## When *not* to write one

- ✅ Write it if you'd want the next peril's builder to read it *before* they hit the same shape of decision.
- ❌ Skip typos, mechanical fixes, one-off environment quirks, and anything already captured as a decision or
  a principle.

## Ground every learning in a real moment

Each entry traces to a concrete build moment — a notebook finding, a decision, a near-miss — with names,
dates, and refs. Not an abstract ideal; *a letter from someone who paid for the lesson*. And it draws the
**`[REF]` vs `[OURS]`** line explicitly: what the references already said, versus what building added. The
second is the whole point of the folder — so mark it clearly.

## Files & naming

Flat, write-order: **`NN_short-handle.md`** (the number is sequence, *not* a peril index — one learning may
span perils). A **subfolder** earns its way in only when a coherent thread of **≥ 3** related learnings
emerges that flat numbering would actively hide (axis: *topic/thread* first, *peril* second, *layer* never).
When it does, it ships with its own `README.md` declaring its local scheme — exactly as the
competitive-research `learnings/architecture/` folder does. **Don't pre-create subfolders.**

## Index

| # | Title | Type | Sourced from | Applies to |
|---|---|---|---|---|
| [01](01_extending_a_short_hazard_record.md) | Extending a short hazard record — the inhomogeneity trap & two ways to do it right | method · anti-pattern | hail × solar · Phase 1 / [DD-1](../plans/hail/decisions.md) | any peril fitting an event-rate λ from a short or multi-source record |
| [02](02_count_distribution_and_dispersion_prior.md) | The count distribution is a tail decision — test it, and hold a prior | method · substrate | hail × solar · Phase 2 / [DD-2](../plans/hail/decisions.md) | any peril fitting an annual event-rate λ |
| [03](03_meet_complex_raw_data_from_scratch.md) | Meet complex raw data from scratch — before you use it | method · forward-looking | hail × solar · Phase 1 / M0 (NOAA vs MRMS) | every new source — esp. raw / gridded / open-source data |
| [04](04_two_datasets_one_peril_decompose.md) | Two datasets, one peril — decompose by component, don't pick a winner | method · forward-looking | hail × solar / [DD-3](../plans/hail/decisions.md) | any peril with ≥2 datasets of differing nature |
| [05](05_damage_curve_three_coupled_choices.md) | The asset damage curve is three coupled choices — value-allocation is a financial decision | method · forward-looking | hail × solar · M3 / damage-curve swap | the damage-curve library build; severity for any peril/asset |

*Sub-folders in this tree:* none yet (see the naming rule above).

## How to add an entry

1. Pick the next `NN`. 2. Copy the template below into `NN_short-handle.md`. 3. Write it from a real build
moment, marking `[REF]` vs `[OURS]`. 4. Add a row to the index. 5. Commit alongside the phase that sourced it.

## The per-learning template

```markdown
# <Title>

*<one-line italic intro — the lesson in a sentence>*

**Status:** v1.0 · written <date> · **Sourced from:** <peril / phase / notebook> · **Applies to:** <future peril / asset / phase>

---

## Where this came from
The concrete build moment — peril, phase, notebook, decision, or near-miss (names / dates / refs).

## Why it looked fine — the trap
The reasonable-looking assumption. The hardest, most valuable section: name why the wrong path was plausible.

## The lesson
> **The lesson.** One crystallized, reusable sentence.

The reasoning, with worked numbers where they sharpen it. Mark `[REF: …]` vs `[OURS — …]`.

## How to recognize it next time
The early signal / invariant / trigger that should catch the same shape of decision on the next peril.

## Caveats and limits
Where the lesson does / does not apply; what it is *not*.

## Cross-references
The decision it generalizes, the principle it serves, the reference it builds on (with stable doc-IDs).
```

---

**Last update:** 2026-06-09 — folder seeded with entry 01.
