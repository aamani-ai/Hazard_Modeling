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
| [06](06_collection_region_size_cancels.md) | The collection region — model over an area, and its size cancels (choose it for homogeneity, not magnitude) | method · substrate | hail × solar · M0/M2 / [A1](../plans/hail/assumptions.md) · [DD-1](../plans/hail/decisions.md) | any areal hit-or-miss peril built as `λ_collection · p` over a region |
| [07](07_one_simulation_two_products.md) | One simulation, two products — not interchangeable, and validate the paid wrapper before you pay | method · anti-pattern | wildfire × solar · M0 / [DD-W3](../plans/wildfire/decisions.md) · [DD-W4](../plans/wildfire/decisions.md) | any peril with ≥2 products of one model, or a paid API over public data |
| [08](08_oozing_developed_pixels.md) | The asset pixel can be a hole — rasters ooze frequency onto developed land but suppress intensity | method · forward-looking | wildfire × solar · M0 / [AW-15](../plans/wildfire/assumptions.md) | any site-conditioned peril read at a developed/engineered site |
| [09](09_pre_integrated_vs_extracted_catalog.md) | When the simulator pre-integrates the event set, M1 is profile-assembly, not event-extraction (and λ comes from a different place) | method · anti-pattern | wildfire × solar · M1 / [DD-W7](../plans/wildfire/decisions.md) | every peril at M1 — classify pre-integrated vs raw-evidence before choosing catalog/frequency machinery |
| [10](10_monte_carlo_effective_sample_size.md) | A Monte Carlo metric is only as precise as its *effective* sample — and a known-answer tolerance must track that, not a fixed band | method · anti-pattern | wildfire × solar · M4 / [DD-W7](../plans/wildfire/decisions.md) | every peril reading metrics off an MC — acutely rare perils (low λ) and deep-tail PMLs |
| [11](11_return_period_conventions.md) | Return period is `1/p` (annual-exceedance), not `1/λ` — the EVT conventions coincide only when rare; safe to mix an ASCE MRI with a fitted rate only at the asset level | method · substrate | convective wind × wind farm · M0 (`01_asce_hazard`) / [DD-WN-3](../plans/convective_wind/decisions.md) | any peril that reads a return-period/MRI surface *and* fits an event-rate λ |
| [12](12_evt_for_a_new_peril.md) | EVT for a new peril — the decision tree: read-or-fit → method (POT vs block-maxima) → tail (ξ: bounded/light/heavy) → pin it; stitches 01·02·04·09·11 + the severity refs, with all three perils worked through it | method · forward-looking | synthesis · hail + wildfire + convective-wind M0–M1 | every **new peril** or **new hazard data product** at M0/M1 (not a new asset under an existing peril) |
| [13](13_densify_sparse_rp_anchor_the_shape.md) | Densifying a sparse return-period curve — anchor a regional *shape* to your real points, don't import a heavier absolute model (the anchors cancel the weak inputs) | method · anti-pattern | flood × solar · M1/M4 / [JD-FL-8](../plans/flood/decisions.md) | any peril holding a sparse RP intensity curve whose frequent end must be filled for a trustworthy EAL |
| [14](14_combining_correlated_sub_perils.md) | Combining correlated sub-perils that share a damage curve — max for shared ground, additive for disjoint, blend between, report the envelope (and never sum per-peril VaR) | method · anti-pattern | flood × solar · M4 / [JD-FL-11](../plans/flood/decisions.md) | any peril with ≥2 correlated sub-perils sharing one damage mechanism (flood, hurricane wind+surge+rain, compound events) |
| [13](13_one_chain_many_products.md) | One chain, many products — same intensity *quantity* ≠ same *node*, and basis risk lives in the node-gap (catalog / damage curve / parametric trigger each pin X at their own node) | method · substantive insight | convective wind M0–M3 + cross-repo `damage_modeling` x-axis foundations + Descartes parametric ref / [discussion](../extra/discussion/intensity_variable_and_products/README.md) | any peril read by ≥2 consumers; choosing/critiquing the hazard intensity variable for any new product (incl. a parametric trigger) |
| [15](15_site_conditioned_is_not_one_thing.md) | Site-conditioned is not one thing — classify the condition surface before choosing M2 | method · substantive insight | flood fundamentals + wildfire M2/site-condition discussion + convective-wind strong-wind coupling | any site-conditioned peril, plus field-intensity perils with local field adjustments |
| [CG-01](conus_grid/01_exact_cell_alignment_and_neighborhood_qa.md) | Exact cell alignment is stricter than hazard nearby | method · anti-pattern | common hail M0 / MYRORSS source qualification with grid selected-cell adapter | any grid hazard layer that maps raw evidence onto fixed cells |
| [CG-02](conus_grid/02_raw_gridded_sources_need_batch_denominators.md) | Raw gridded sources need batch denominators | execution · data-contract | common hail M0 / MYRORSS source qualification with grid selected-cell adapter | gridded hazard sources scanned from raw files |

*Sub-folders in this tree:* [`conus_grid/`](conus_grid/README.md) for fixed-grid hazard product learnings.

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

**Last update:** 2026-06-26 - added entry 15 (site-conditioned is not one thing — classify the condition
surface before choosing M2), sourced from the flood/wildfire/strong-wind coupling discussion. Previous:
2026-06-21 entry 13; 2026-06-16 CONUS-grid entries CG-01/CG-02; 2026-06-13 entries 07-10 from wildfire
M0-M4.
