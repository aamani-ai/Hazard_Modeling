# Scope & Story — `Hazard_modeling` (read me first)

> **What this file is.** The origin story of this repo *and* a navigation map of the cross-connected
> folders it's built on. If you're an agent or teammate picking this up cold, start here: it tells you
> **why** this repo exists, **how** we got to it, and **where** every piece of supporting knowledge lives.
>
> **Status:** living document, written **2026-06-08** from the owner's account of the project plus a deep
> read of the linked material. It is the knowledge anchor that will feed the repo's `README.md`,
> `AGENTS.md`, and `CLAUDE.md` as the work takes shape. Specifics in the connected repos move; treat the
> linked files as the source of truth and re-read when in doubt.

---

## TL;DR

InfraSure is building **hazard risk modeling for renewable-energy infrastructure** (utility-scale **solar PV
and wind** first). An earlier repo — [`hazard_analysis`](../../hazard_analysis) — got far enough to produce
EAL / VaR / PML / AEP-OEP numbers, but those numbers had a **primary, fundamental math error** (not just
docs/architecture debt): the tail metrics were computed on the **wrong random variable**, so VaR and PML were
untrustworthy while only EAL survived. Patch-fixing was rejected. Instead the foundations were rebuilt from
scratch — **competitive research → reference docs → structural math → a methodology doctrine** — and *this*
repo is where that rebuilt approach gets implemented. This file threads those pieces together.

---

## 1. Why this repo exists — the old repo's fundamental failure

The old repo isn't bad work; it's a repo that **outgrew its foundations**. Two tells:

- **The branch list reads like an incident log:** `bug/before_last_merge`, `bug/fixing_bad_merge`,
  `fix/bad_merge`, `feature/fix_freq`, `feature/per_event_EAL`, `feature/tornado-var`, … — a project drowning
  in merge-recovery and per-symptom patches.
- **The deeper problem is mathematical**, and it's written up in
  [`hazard_analysis/docs/suggested_architecture/issues/`](../../hazard_analysis/docs/suggested_architecture/issues).

### The crux (the one thing to understand)

Each event's loss was stored as `damage% × asset_value × spatial_factor`. That product is the **expected**
loss *averaged over the Bernoulli hit/miss draw* — **not a realized sample**. By the Law of Total Variance
this preserves the mean (so **EAL is fine**, by linearity of expectation) but **discards the dominant variance
term**: the bimodal reality that an asset is either *hit* (full conditional loss) or *missed* ($0). Quantiles
read off the resulting artificially smoothed, near-Normal annual-sum distribution **understate tail risk
badly** — ~**12× low on VaR₉₉** for Strong Wind in the worked example.

This stacks with three more issues:

| # | Issue | Effect |
|---|-------|--------|
| A | **Frame mismatch** — PML read in the **OEP** (per-event) frame, VaR in the **AEP** (annual-aggregate) frame, then compared by an invariant `VaR₉₉ ≤ PML₅₀₀` | Only valid when `λ_asset·OEP(L) ≪ 1`. For high-frequency Strong Wind (λ≈0.25/yr) it's geometrically invalid and **fires by ~175×** (VaR₉₉=$547M vs PML₅₀₀=$3.1M). 175× is impossible under any single coherent framework — it's the signature of **two independently-fitted objects** drifting. |
| B | **Law-of-Total-Variance error** (the crux above) | VaR/PML computed on expected, not actual, annual losses → tails wrong. |
| C | **Asset-value cap saturation** | Clipping the annual matrix at `asset_value` mechanically pins VaR₉₉ ≈ asset_value for frequent hazards (the tell that the fit ran off the data). |
| — | **Spatial factor = `F/A`** (point-asset) | Under-counts hit probability **1.3×–7×** for real solar/wind footprints. Correct form for two convex shapes is `(√F + √s)²/A`. *Scales every dollar output but does not fix B.* |
| — | **100× unit bug** | `Loss Ratio` stored as a percentage but read as a ratio → inflates `sim_mag` inputs (and EAL) by exactly 100× (`investigation_sim_mag_inflation.md`). |

**The fix** (and the thesis of the rebuild): one **unified compound-Poisson Monte Carlo**. Draw
`N_hits ~ Poisson(λ_asset = λ_collection × spatial_factor)` per year, draw **full conditional severities** for
the hits, sum, repeat. Then EAL, VaR, AEP-PML, OEP-PML, and TVaR all derive from **one severity model + one
λ_asset** — Poisson-coherent by construction. (The old repo's `dev` branch already does exactly this for
Tornado; the rebuild generalizes that pattern.)

**Don't-repeat list for the new repo:** never store expected-loss-as-sample · never compare metrics across
OEP/AEP frames without the coherence constraint · never collapse a random variable to its mean before a
downstream nonlinearity (deductible, cap, aggregation).

**Read:**
[`issues/pml-var-aep-methodology.md`](../../hazard_analysis/docs/suggested_architecture/issues/pml-var-aep-methodology.md)
(the canonical writeup) ·
[`issues/strong-wind-var-worked-example.md`](../../hazard_analysis/docs/suggested_architecture/issues/strong-wind-var-worked-example.md)
(reproducible proof: Method 0 vs Method 3 agree on EAL ≈ $4.98M but differ ~12× on VaR₉₉) ·
[`issues/var_methodology_demo.py`](../../hazard_analysis/docs/suggested_architecture/issues/var_methodology_demo.py)
(the seed=42 script generating every number) ·
[`issues/spatial-factor.md`](../../hazard_analysis/docs/suggested_architecture/issues/spatial-factor.md).

---

## 2. The journey — how we got here

```
  OLD REPO (hazard_analysis)                  "stop patching; rebuild the foundations"
  ─ math is fundamentally wrong ───────────────────────┐
                                                        ▼
  ┌──────────────────────┐   ┌───────────────────┐   ┌──────────────────┐   ┌───────────────────┐   ┌──────────────┐
  │ COMPETITIVE RESEARCH  │ → │  REFERENCE DOCS    │ → │   HAZARD MATH    │ → │   METHODOLOGY     │ → │  THIS REPO   │
  │ vendor landscape +    │   │  terminology,      │   │  compound-Poisson│   │  the doctrine for │   │ Hazard_      │
  │ A-series architecture │   │  risk metrics,     │   │  pipeline (the   │   │  building the     │   │ modeling     │
  │ spine (the moat +     │   │  data catalog      │   │  structural math)│   │  annual loss dist │   │ (implement)  │
  │  the "how" of cat mods)│  │  (the vocabulary)  │   │                  │   │                   │   │              │
  └──────────────────────┘   └───────────────────┘   └──────────────────┘   └───────────────────┘   └──────────────┘
       + the owner's pre-existing fundamental-math knowledge base (Learning/) feeds the math + methodology
```

In the owner's words: the old repo's failure made it clear the **maths is the crux** — that's what the old
repo got wrong consistently. So the rebuild started from the basics: the **competitive research** (to learn how
the field actually builds cat models, and where the moat is), distilled with the **Learning** knowledge base
into the **reference docs** (terminology, output metrics, data catalog), which — combined with the
architectural learning — enabled the **structural math** and finally the **methodology doc**. This repo is the
destination: where that methodology becomes an implementation.

---

## 3. The conceptual core (what the rebuilt approach actually is)

### The pipeline (the math spine)
A **compound-Poisson catastrophe model**, composed in strict order:

```
frequency → coupling (hit/miss) → severity → Monte-Carlo annual aggregation → EVT tail
N ~ Poisson(λ)   H ~ Bernoulli(p)   D(I)·V        A_y = Σ Lᵢ , O_y = max Lᵢ      GEV/GPD
```
- **Event loss:** `Lᵢ = Hᵢ · Fᵢ · D(Iᵢ) · V` (hit/miss · exposed fraction · damage ratio from the curve · asset value).
- **Two annual vectors, never conflated:** `A_y = Σ Lᵢ` → **AEP** (feeds EAL/VaR/TVaR); `O_y = max Lᵢ` → **OEP**
  (feeds per-occurrence PML). `AEP ≥ OEP` always; the size of the gap is a frequency-regime diagnostic.
- The **curated damage curve `D(I)` is the dominant uncertainty** — fitting can't rescue a biased curve.
- **EVT enters last** and is dangerous (it extrapolates); default to modeling the **intensity tail** (reusable)
  not the loss tail. Frequency default for convective perils (hail) is **Negative Binomial**, not Poisson
  (over-dispersion).

### The module spine (the architecture)
The industry NAIC 4-module standard (Hazard → Exposure → Vulnerability → Financial) is re-expressed as
InfraSure's **M0 → M1 → M2 → M3 → M4**: split Module 1 into **M0 (raw evidence)** + **M1 (clean event
catalog)**, and make **M2 = the coupling / intersection layer its own module** — because that seam is
**InfraSure's value-proposition wedge**, not a vendor black box. (M4 financial is inherited wholesale from
OASIS fmcalc — "the substrate is runtime, not content.")

### Three coupling types (the heart of M1→M2 dispatch)
1. **Areal hit-or-miss** — finite footprint; Minkowski `(√F+√s)²/A` math (hail, tornado, convective gust).
2. **Field intensity** — continuous field, uniform sub-point susceptibility; sample-and-weight (hurricane/synoptic wind, EQ, snow, ice).
3. **Site-conditioned** — continuous field, *non-uniform* per-asset susceptibility (flood, wildfire, surge).

### Scope & sequencing (what's actually being built first)
- **V1 = damage track only** (intensity → physical damage → repair/replacement cost). **V2+ = disruption track**
  (intensity → output curtailment → revenue loss) — the industry-missing differentiator. **V3 = market/portfolio correlation.**
- **Phase 1 = solar + hail, end-to-end**, as the proving cell. The approach is **cell-by-cell**
  (`peril × sub-peril × asset_type`), not a speculative 70-cell matrix.
- **Strategy:** Tier 1 = a full standard pipeline at parity with RMS/AIR/Swiss Re (table stakes); **Tier 2 =
  selective subcomponent depth where loss concentrates** (hail × panels, wind × blades) — *that's the moat.*
  The competitive research confirms **no incumbent** reaches per-subcomponent damage curves with continuous
  engineering-feature parameters.

---

## 4. Folder map — where everything lives

> All of these are reachable from this repo via the gitignored cross-project symlinks at the repo root.

| Folder (symlink) | What it is | Why it matters here |
|---|---|---|
| [`hazard_analysis/`](../../hazard_analysis) | **The OLD repo.** Full working pipeline + a rich `docs/`. | The autopsy (§1) and the rethink live here. Source of "what not to repeat." |
| [`infrasure-hazard-competitive-research/`](../../infrasure-hazard-competitive-research) | Vendor-landscape research **+ the A-series architecture spine**. | Establishes the moat thesis and the *architecture* the methodology builds on. |
| [`Learning/`](../../Learning) | The owner's personal knowledge base (risk, insurance, stats, ML). | `ML-DL/InfraSure_related/hazard_math/` is the structural-math layer. |
| [`docs/google_drive_docs/`](../google_drive_docs/README.md) | Local `.docx` of the team's shared Drive **InfraSure Hazard** reference set. | The reference docs: terminology, hazard data, risk metrics, loss-distribution methodology. |
| [`docs/extra/`](.) | This file + reference materials to come. | The "start here" knowledge anchor. |
| [`model-gpr/`](../../model-gpr) | Sibling **Performance Modeling** repo (Tier 1 of the platform). | Out of scope for now — relevance to be explained later by the owner. |
| [`renewablesinfo_org/`](../../renewablesinfo_org) | The owner's renewables **data platform** repo. | Two roles: the *how-we-work* **methodology spine** (workflows · design · principles) **and** the **asset reference DB** we pick modeling assets from. See §4f. |
| [`docs/extra/discussion/`](discussion/) | The owner's saved **GPT design discussions** — adapters, coupling types, damage representation. | A design-thinking record that mirrors the A-series seams (see §4e). |

### 4a. `hazard_analysis/` — the old repo (autopsy + rethink)
- **`docs/suggested_architecture/issues/`** — the math critiques (§1).
- **`docs/suggested_architecture/docs/`** — the rethink: [`goals.md`](../../hazard_analysis/docs/suggested_architecture/docs/goals.md)
  (mission, two-tier strategy, the subcomponent moat), [`architecture_solution.md`](../../hazard_analysis/docs/suggested_architecture/docs/architecture_solution.md)
  (tactical hail-first plan), [`high-level-architecture.md`](../../hazard_analysis/docs/suggested_architecture/docs/high-level-architecture.md)
  (peril-agnostic destination), [`layered-pipeline.md`](../../hazard_analysis/docs/suggested_architecture/docs/layered-pipeline.md) (the monorepo/folder structure + typed boundary object).
- **`docs/suggested_architecture/learning/`** — [`principles.md`](../../hazard_analysis/docs/suggested_architecture/learning/principles.md)
  (Principle 1: Hazard×Asset Specificity; Principle 2: Modular Layer Architecture) and
  [`risk-metrics-methodology.md`](../../hazard_analysis/docs/suggested_architecture/learning/risk-metrics-methodology.md)
  (OEP vs AEP, the seven VaR methods — only "Option 0" is universally wrong, the coupling taxonomy).
- **`docs/suggested_architecture/extra/hazard_schema_gap_analysis_all_asset_types.md`** — per-asset audit of which
  subcomponent attributes exist vs. are missing (e.g., solar **stow angle** has no home in the schema). Grounds the moat in real data work.
- `docs/updates/` — the deep history of investigations & code reviews (e.g., `spatial_factor_pml_var_review.md`).

### 4b. `infrasure-hazard-competitive-research/` — landscape + architecture spine
- **`README.md`** — scope caveat (the *hazard* pillar only), folder map, sourcing/tagging conventions.
- **`competition/`** — 11 vendor deep-dives (Renew Risk, Verisk STM, Moody's RMS, kWh Analytics, AIR/Verisk, First Street, Swiss Re NCME, HAZUS, CLIMADA, OASIS LMF, MSCI).
- **`glossary/`** — the cross-vendor artifacts: [`00_coverage_matrix.md`](../../infrasure-hazard-competitive-research/glossary/00_coverage_matrix.md)
  (**THE central artifact** — shows no vendor reaches InfraSure's target), [`00_rosetta.md`](../../infrasure-hazard-competitive-research/glossary/00_rosetta.md)
  (same-word-different-meaning collisions: "PML" alone has ≥3 meanings), [`00_open_source_module_compare.md`](../../infrasure-hazard-competitive-research/glossary/00_open_source_module_compare.md).
- **`learnings/`** — 25+ strategic meta-notes ([`INDEX.md`](../../infrasure-hazard-competitive-research/learnings/INDEX.md) maps them). Key: Group B owns the *catalog* (the moat) / Group C owns the *wiring* (the open standard); build for **agent/MCP consumption day one**; BESS/hydrogen are greenfield.
- **`learnings/architecture/` — the A-series spine** (the `A13/A20/A21/A22` the methodology references):
  [`README.md`](../../infrasure-hazard-competitive-research/learnings/architecture/README.md) first, then
  [`A12` peril taxonomy](../../infrasure-hazard-competitive-research/learnings/architecture/A12_peril_taxonomy_spine.md),
  [`A13` cell-walking runbook](../../infrasure-hazard-competitive-research/learnings/architecture/A13_cell_walking_methodology.md)
  (23 questions × 6 seams), [`A21` coupling types](../../infrasure-hazard-competitive-research/learnings/architecture/A21_m1_m2_coupling_types.md)
  (the Minkowski wedge), [`A24` distribution choices](../../infrasure-hazard-competitive-research/learnings/architecture/A24_distribution_choices.md)
  (C0–C6 + **Axiom 3: "stochastic must stay stochastic past every nonlinearity"** — the formal statement of the old repo's error),
  [`A25` damage-vs-disruption scope](../../infrasure-hazard-competitive-research/learnings/architecture/A25_damage_vs_disruption_scope.md),
  and the first concrete cell [`perils/hail/H00`](../../infrasure-hazard-competitive-research/learnings/architecture/perils/hail/H00_scope_and_v1_commitments.md).

### 4c. `Learning/ML-DL/InfraSure_related/hazard_math/` — the structural math
Six rereadable notes deriving the compound-Poisson pipeline in composition order:
[`01` Bernoulli hit/miss](../../Learning/ML-DL/InfraSure_related/hazard_math/01_bernoulli_hit_miss_model.md) ·
[`02` Poisson frequency](../../Learning/ML-DL/InfraSure_related/hazard_math/02_poisson_frequency_model.md) ·
[`03` severity / event-loss](../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md) ·
[`04` Monte-Carlo annual loss](../../Learning/ML-DL/InfraSure_related/hazard_math/04_monte_carlo_annual_loss_simulation.md) (the capstone) ·
[`05` EVT tail](../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md). Each note documents the specific modeling mistake it prevents.

### 4d. `docs/google_drive_docs/` — the reference docs
The shared Drive set: **terminology** (input vocabulary), **risk metrics** (output vocabulary: EAL/VaR/PML/TVaR/OEP/AEP),
**hazard data reference** (the data catalog/framework), **loss-distribution methodology** (the doctrine). Full
index + per-file summaries + Drive links: [`docs/google_drive_docs/README.md`](../google_drive_docs/README.md).
> Note: the methodology + risk-metrics `.docx` are intentionally **duplicated** into `hazard_math/` (§4c) — same files, two homes.

### 4e. `docs/extra/discussion/` — the owner's design discussions
Saved **GPT discussions** (under `gpt/`) so the thinking isn't lost. They track the same seams as the A-series:
- [`01_adapters_first_principles.md`](discussion/gpt/01_adapters_first_principles.md) — the adapter/interface concept from first principles (the typed boundary between per-peril pipelines and the shared engine).
- [`02_adapter_dataflow_event_catalog_to_loss.md`](discussion/gpt/02_adapter_dataflow_event_catalog_to_loss.md) — the data flow from event catalog through to loss.
- [`03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md`](discussion/gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md) — the three coupling types (≈ A21 / M1→M2).
- [`04_damage_representation_scalar_vector_distribution.md`](discussion/gpt/04_damage_representation_scalar_vector_distribution.md) — damage representation: scalar vs vector vs distribution (≈ A22 / M2→M3).

> _Not yet deep-read/summarized into this map_ — titles + seam-mapping above are from the filenames; a richer pass is flagged in §6.

### 4f. `renewablesinfo_org/` — methodology spine **and** the asset-data source
The owner's renewables data platform, wearing two hats here:

**(1) How-we-work spine.** Most process artifacts in this repo were adapted from it: `docs/workflows/`
(the Major-Feature process + per-phase loop → our [`docs/workflows/`](../../docs/workflows/README.md)),
`docs/design/` (the plan-folder shape → our [`docs/plans/hail/`](../plans/hail/README.md)),
`docs/principles/` (the documentation *style* → our [`docs/principles/`](../principles/README.md)), plus
`docs/conventions.md`. `docs/principles/scaling.md` is hard-won solo-with-agents discipline that maps onto
our *basics-spot-on* principle.

**(2) The asset-data source — the big one for the build.** The asset registry we pick modeling assets from
lives here. Docs: [`docs/reference/workspace/`](../../renewablesinfo_org/docs/reference/workspace)
(`architecture.md` · `schema.md` · `governance.md` · a 6.5k-line `decisions.md` · `engineering/`).
- **DB:** the DEV/demo workspace (Neon, `tenant_workspace_v2`) — single-table multi-tenant + Postgres RLS +
  sparse EAV override layer. Assets are the **`plants`** (+ **`generators`**) reference tables; public rows
  have `workspace_id IS NULL` (~15.5k plants / ~30k generators). `modeling_metadata_plant.tech` is the clean
  classifier (`solar_pv` ≈ 48%).
- **Pick an asset locally:** [`data/base/asset_master.parquet`](../../renewablesinfo_org/data/base/asset_master.parquet)
  (30,225 generator rows, **typed** `Latitude`/`Longitude`, `Nameplate Capacity (MW)`,
  `Technology`/`Energy Source Code`=`SUN`/`Prime Mover`=`PV`, owner) — the easiest source. Web flat index:
  `web/public/data/plant_index.json`.
- **Subcomponent moat (later):** the **engineering substrate** (`engineering_subsystem → engineering_component`)
  decomposes a solar asset into `PV_ARRAY → PV_MODULE` and `MOUNTING → TRACKER`. The hail-fragility drivers
  are typed, hazard-flagged fields: `glass_thickness_mm`, `tempered_glass` (module); `stow_strategy`,
  `hail_stow_capable` (tracker).

**Caveats (load-bearing):**
- It's **DEV-only** and intentionally diverges from prod — don't assume workspace/modeling tables exist on the public site.
- **HAIL is not in the current `hazard_type` enum** (`wildfire/flood/heat/hurricane/freeze/drought`) — our hail work *extends* it.
- The hail subcomponent fields above are **typed but unsourced skeletons** today (EIA/USPVDB don't provide glass thickness, tempered-glass, or tracker stow) — they must be assumed, externally sourced, or supplied as workspace input. A v1 hail model leans on what *is* available: mounting type, cell type, bifacial, tilt/azimuth, AC/DC capacity, lat/lon, capacity, owner.

---

## 5. Reading order (cold start)

1. **This file** (the map).
2. **§1 + the `issues/` docs** — understand why the old repo failed (the "why we're here").
3. **`docs/google_drive_docs/README.md`** then the **terminology** and **risk-metrics** docs — the vocabulary.
4. **`hazard_math/` 01→05** — the structural math.
5. **The methodology doc** (`hazard_asset_loss_distribution_methodology`) — the doctrine that ties math to build.
6. **A-series** `README → A12 → A13 → A21 → A24 → A25 → hail/H00` — the architecture spine the methodology assumes.
7. **`suggested_architecture/` goals → solution → high-level → layered-pipeline** — the target architecture.
8. **Competitive research** `README → glossary/00_coverage_matrix → learnings/INDEX` — the landscape & moat (strategy).

---

## 6. Open threads / not-yet-here

- **Discussion folder — found** at `docs/extra/discussion/gpt/` (see §4e), now in-repo. _Open: a deeper read/summary of the four GPT discussion docs folded into the map above._
- **`model-gpr` relevance** — deferred; the owner will explain how the Performance Modeling sibling connects.
- **The implementation / repo-architecture doc** — the methodology explicitly defers code structure to a
  forthcoming "Repo Architecture Document." Not written yet; this repo is where it lands.
- **Data / schema gaps** — the moat depends on attributes not yet stored (solar stow angle, wind site physics,
  BESS, thermal). See the gap-analysis doc (§4a).
- **A30 consolidated build-spec** — deliberately deferred in the A-series until ≥3 perils are walked (hail → riverine flood → hurricane).

---

## 7. How this doc is used

This is the **knowledge anchor**. As the project moves:
- It feeds the repo's [`README.md`](../../README.md) (overview), [`AGENTS.md`](../../AGENTS.md) (agent/contributor
  guidance), and [`CLAUDE.md`](../../CLAUDE.md) — those should be updated *from* this file as scope solidifies.
- When the owner guides the **first implementation step**, this doc is the shared context that makes that
  conversation efficient.
- Keep it current: update on a new connected folder, a scope decision, or a correction to the story above.
