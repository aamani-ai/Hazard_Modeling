# discussion/conus_grid/

**Where we think out loud about the CONUS *gridded* hazard-risk product — *before* we build it.**
This is the go-to home for that discussion; nothing here is code or a plan-of-record, it's the reasoning
that *produces* the plan. Once a decision settles here, it graduates to `docs/plans/` (`DD-*` / `A-*`) and
then to notebooks/scripts.

---

## The two use cases this repo serves

The hazard engine has **two distinct deliverables** — *separate products with different consumers*, but the
**same M0→M4 engine** (see the consequence below).

| # | Use case | Unit of analysis | Consumer | Where it's discussed |
|---|---|---|---|---|
| **1** | **Deep per-asset risk** | one **real** asset (true geometry, capacity, BoS mix, TIV) | a specific deal / asset owner | the main `Notebooks/` build (M0→M4) + the per-peril discussion folders |
| **2** | **CONUS gridded risk** | a **canonical** asset at every grid cell → a per-cell risk matrix per hazard | the platform's breadth layer (a map, like the wildfire index — but more accurate + consistent) | **← this folder** |

> **This folder is about use case 2 only.** Use case 1 is the per-asset notebooks and is not re-litigated here.

### The consequence that makes this one investment, not two

The ideal state for the grid ([`01`](01_ideal_architecture_compute_and_grid.md)) is to run the **exact same
M0→M4 engine** per cell, just with a **canonical asset** (`100 MW solar` + `100 MW wind` at the cell centre)
swapped in for the real one. So:

```
        ONE engine (M0 → M1 → M2 → M3 → M4)
                       │
        ┌──────────────┴───────────────┐
   real asset                     canonical asset
   at its true location           at each grid-cell centre
        │                               │
   USE CASE 1                      USE CASE 2
   (deep per-asset)                (CONUS grid)
```

A real asset is just an **off-grid run of the same model**. That's *why* the grid is trustworthy, why the two
products can't silently drift (the platform's EAL-percentage bug is exactly a grid-vs-point **version drift** —
[`01` §4](01_ideal_architecture_compute_and_grid.md)), and why "screening" here is **not** a low-quality tier —
it's the full engine at grid resolution.

---

## How this folder is organised

**Generic (cross-cutting) at the top; each hazard's specifics in its own subfolder** — the same
*shared-vs-specific* seam the Notebooks use (`peril → asset`). Adding wildfire/wind later = a new sibling
subfolder; the generic docs don't move.

### Generic — the product design (read in order)

| # | Doc | What it decides |
|---|---|---|
| 01 | [`01_ideal_architecture_compute_and_grid.md`](01_ideal_architecture_compute_and_grid.md) | **Architecture · compute · grid.** Two-stage split (hazard field built once · loss engine fanned out per cell); per-hazard difficulty lives entirely in M0/M1; CONUS hail is *hours*, not *weeks*; grid locked to the 0.25° wildfire-index grid. |
| 02 | [`02_per_cell_output_schema.md`](02_per_cell_output_schema.md) | **The per-cell output contract** — EAL, AEP/OEP curves, PMLs, VaR/TVaR, exceedance probs, in $ and % of TIV, solar + wind. "Store curves, expose readouts" (`PML₁₀₀ ≡ VaR₉₉`). |
| 03 | [`03_exposure_granularity.md`](03_exposure_granularity.md) | **How granular we define the canonical asset** — the coarsest tier the coupling needs (area → point-cloud → *never* sub-asset config), **appended per (hazard × asset)**. Why "screening" is a *precise* assumption. |
| — | [`assumptions.md`](assumptions.md) | **The grid product's `G*` assumptions register** — canonical asset, area→cell translation, the exposure-granularity append register, MC depth, grid, reporting basis. Cross-cutting; per-hazard M1 assumptions live in each peril's register. |

### Per-hazard — the M1 hazard-field sourcing (one subfolder each)

| Hazard | Subfolder | Contents |
|---|---|---|
| **Hail** | [`hail/`](hail/README.md) | `00` data-product research (factual findings) → `01` sourcing triage (the decision: **self-build, anchored**). |
| Wind | *(to come)* | same shape — research → triage. |
| Wildfire | *(largely in [`../wildfire/`](../wildfire/README.md) + FSim)* | the general wildfire scope discussion already covers much of it. |
| Tornado | *(to come)* | — |

> **Working practice:** every hazard gets its data-product **research pass *before* implementation**; the
> findings stay factual (`<hazard>/00_*_research.md` — tables + sources, no recommendations), and the decision
> distils into a separate `<hazard>/01_*_sourcing_triage.md`. Evidence and opinion in different files.

## Related — don't duplicate, link

- The per-peril scope discussions: [`../wildfire/`](../wildfire/README.md) (wildfire = the easy "ready hazard field" case).
- The full M0→M4 journey & coupling types: [`../gpt/05_m0_to_m4_full_modeling_journey.md`](../gpt/05_m0_to_m4_full_modeling_journey.md) · [`../gpt/03_coupling_types_…`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md).
- Why a canonical asset is robust for hail (`A`, `s` cancel): [`../../../learning_logs/06_collection_region_size_cancels.md`](../../../learning_logs/06_collection_region_size_cancels.md).
- The principles that govern every call: [`../../../principles/`](../../../principles/README.md).
- The scope-and-story anchor: [`../../00_scope_and_story.md`](../../00_scope_and_story.md).

## Status

🟡 **Open for discussion.** Generic frame settled (architecture, output schema, exposure granularity, grid
locked, 250k MC); hail sourcing recommended (**self-build, anchored**) with DEC-H1…H5 pending. Next threads:
the hail × wind exposure logic (`03` §3), real-asset attach/validation, sparse-cell distribution fitting, and
the wind/wildfire M1 sourcing passes.
