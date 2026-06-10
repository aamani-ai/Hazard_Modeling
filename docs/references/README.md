# references/ — methodology provenance

*Where each method comes from. The fourth doc tier: [`principles/`](../principles/README.md) (why we
build this way) · [`plans/`](../plans/README.md) (what we decided) ·
[`learning_logs/`](../learning_logs/README.md) (what building taught us) · **`references/` (what it's
grounded in)**.*

## Why this exists

Our methods aren't invented. They were synthesized the same way we built the **InfraSure hazard
competitive-research repo**: survey the field (10+ cat-model vendors + the academic catastrophe-modeling
literature), document each competitor's methodology, take the defensible pieces, and adapt them to
**renewable-asset** specifics. This doc is the **bridge** that surfaces that provenance here — so that
*"where is this method from?"* and *"how do you know the industry does this?"* both have a one-click
answer.

For each choice the map below gives three things: **what we do → grounded in (external source) → derived
in (our research-repo doc).** Full external citations (authors, years, DOIs/URLs) live in
[`bibliography.md`](bibliography.md), reproduced in-repo so this answer doesn't depend on research-repo
access.

> **Access note.** The research-repo links (`A12`, `A21`, …) resolve at
> [`github.com/D-ivyy/infrasure-hazard-competitive-research`](https://github.com/D-ivyy/infrasure-hazard-competitive-research)
> for those with access. Everyone else: the **external** citations are fully reproduced in
> [`bibliography.md`](bibliography.md). **Status** flags whether a method is **built** (live in the
> hail × solar pipeline) or **(deferred)** (grounded for the roadmap, not yet implemented) — so nothing
> below implies we run something we don't.

---

## The provenance map

Short-keys (e.g. `[Klugman et al. 2012]`) resolve in [`bibliography.md`](bibliography.md). Research-repo
docs are the **A-series** (architecture) — indexed at the bottom.

### M0 — input data (the peril evidence)

| What we do | Grounded in (external) | Derived in (research repo + ours) | Status |
|---|---|---|---|
| MRMS MESH (gridded radar hail) as the footprint source | `[Wendt & Jirak 2021]`; MRMS/NSSL | [A20](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A20_m0_m1_hazard_catalog.md) · A4/A5 · [learning_logs/03](../learning_logs/03_meet_complex_raw_data_from_scratch.md) | built |
| NOAA SPC/NCEI point reports as cross-check | SPC/NCEI Storm Events; `[Allen & Tippett 2015]` | A20 · DD-1 | built |
| Severe-hail threshold 25.4 mm (1″) | NWS definition; `[Allen & Tippett 2015]` (2010 redefinition) | A2 | built |
| MESH-vs-report caveat (radar proxy differs from human reports, esp. low-population regions) | `[Wendt & Jirak 2021]` (MESH–Storm Data report differences) — any MESH over-forecast / FAR framing traces to **Witt 1998** (our A5), not W&J | A5 · [learning_logs/01](../learning_logs/01_extending_a_short_hazard_record.md) | documented |

### M1 — event catalog + frequency

| What we do | Grounded in (external) | Derived in (research repo + ours) | Status |
|---|---|---|---|
| One event = one hail-day; footprint = union of above-threshold MESH cells | `[Schuster et al. 2005]` (radar swath ≈ damage swath) | [A20](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A20_m0_m1_hazard_catalog.md) · A6/A10 | built |
| MRMS spine + NOAA cross-check (homogeneity > length; no naive splice) | — (our synthesis) | DD-1/DD-3 · [learning_logs/01](../learning_logs/01_extending_a_short_hazard_record.md), [/04](../learning_logs/04_two_datasets_one_peril_decompose.md) | built |
| **Frequency = Negative Binomial** (over-dispersed; Gamma-Poisson) | `[Klugman et al. 2012]`; `[Hussain et al. 2025]`; `[Allen & Tippett 2015]`; `[Miralles et al. 2023]` | [A24 §1](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A24_distribution_choices.md) · A8/A9/A20 · [learning_logs/02](../learning_logs/02_count_distribution_and_dispersion_prior.md) | built |
| Dispersion test underpowered at small n (φ on 5 yr; prior at n<10–15) | `[Coles 2001]` §2.6; `[Das & Ghosh 2013]`; `[Hosking 1990]` | A24 · A9/A24 (register) | documented |
| Climate-conditioned / regime-switching λ(t) | `[Lepore et al. 2021]`; `[Taszarek et al. 2020]`; `[Goldenberg et al. 2001]` | A24 §1.3–1.4 | (deferred) |

### M2 — coupling (does the event reach the asset?)

| What we do | Grounded in (external) | Derived in (research repo + ours) | Status |
|---|---|---|---|
| Areal hit-or-miss; Minkowski `p = (√F + √s)²/A` | `[Stoyan et al. 1995]` — stochastic-geometry / Minkowski-sum *basis*; the specific `(√F+√s)²/A` convex-shape form is **derived in A21**, not quoted from Stoyan | [A21 §2](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A21_m1_m2_coupling_types.md) · A11 | built |
| Fixing the old repo's single-centroid `F/A` under-count | **the single-centroid triplet**: `[Thompson 2024 / kWh]` (+300%), `[Sabbatelli & Goodyer 2025 / Moody's]` (+230%), `[Rudaviciute 2022 / Moody's]` (−41/+83%) | [learning #19](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/19_canonical-citation-triplet-for-single-centroid-error.md) · A21 | built |
| Coupling type is set by (peril × exposure geometry) — areal / field / site-conditioned | `[OASIS LMF Keys 2024]`; `[Neuberger Berman 2025]` (geometry as first-order) | A21 · [`hazard_asset_specificity.md`](../principles/hazard_asset_specificity.md) | built (areal); defined (field/site) |
| λ_asset = λ_collection · E[p] (A cancels) | `[Stoyan et al. 1995]` | A14 · A21 | built |

### M3 — damage / severity

| What we do | Grounded in (external) | Derived in (research repo + ours) | Status |
|---|---|---|---|
| **Capex-weighted subsystem blend** `Asset_DR = Σ wᵢ·DRᵢ` (component → asset) | `[Porter et al. 2001]` (assembly-based vulnerability); IBHS/IEC module-hail; NREL ATB/SAM | [A22](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A22_m2_m3_damage_representation.md) · A15 · [learning_logs/05](../learning_logs/05_damage_curve_three_coupled_choices.md) · `infrasure-damage-curves` | built |
| Fragility vs. vulnerability; logistic/lognormal curve form; saturates (no extrapolation) | `[FEMA P-58 / ATC 2012]`; `[Cornell et al. 2002]`; `[Rossetto & Elnashai 2003]` | A22 · A16 | built |
| Monotone interpolation of tabulated curves | `[Fritsch & Carlson 1980]` (PCHIP) | A24 §5.2 | reference |
| Scalar-mean DR (no conditional distribution) | — (v1 choice) | A17 · [learning_logs/05](../learning_logs/05_damage_curve_three_coupled_choices.md) | built (v1) |
| Conditional-DR **distribution** (secondary uncertainty) | `[Verisk (AIR) 2018]`; `[OASIS/IF 2017]`; `[Miralles et al. 2023]` | A22 · A17 | (deferred) |

### M4 — loss & metrics

| What we do | Grounded in (external) | Derived in (research repo + ours) | Status |
|---|---|---|---|
| Compound-Poisson Monte Carlo (NegBin counts × per-event thinning) | `[Klugman et al. 2012]`; `[Embrechts et al. 1997]`; `[McNeil et al. 2015]` | [A24](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A24_distribution_choices.md) · A22 | built |
| **LOTV rule** — `Bernoulli(pᵢ)` + full conditional loss, never `pᵢ × loss` | `[Klugman et al. 2012]` (frequency–severity separation); `[McNeil et al. 2015]` | A24 · `hazard_math` · DD-4 | built |
| EAL / VaR / PML / TVaR off the same AEP/OEP per-year vectors; **AEP vs OEP** never mixed | `[American Academy of Actuaries 2018]`; `[McNeil et al. 2015]` | A13 · DD-4 · Drive `risk_metrics_reference` | built |
| EVT-GPD deep tail (beyond the bootstrap-truncated tail) | `[Embrechts et al. 1997]`; `[Coles 2001]`; `[Davison & Smith 1990]`; `[McNeil 1997]` | A24 §2 · A23 | (deferred) |
| Financial terms (deductibles / limits / BI) | `[OASIS LMF fmcalc 2024]`; `[Klugman et al. 2012]` §5.4–5.5; `[Neuberger Berman 2025]` | A24 §4 · A21 (gross-only) | (deferred) |

### Cross-cutting

| What we do | Grounded in (external) | Derived in (research repo) | Status |
|---|---|---|---|
| (peril × sub-peril × asset_type) taxonomy | FEMA NRI · cat-model hierarchy · CLIMADA · First Street · OASIS (surveyed in A12) | [A12](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A12_peril_taxonomy_spine.md) | built (frame) |
| Three coupling types (the dispatch) | `[Stoyan et al. 1995]`; CLIMADA | [A21](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A21_m1_m2_coupling_types.md) · [`hazard_asset_specificity.md`](../principles/hazard_asset_specificity.md) | built |

**Bare items (v1 methodology choices, external calibration deferred):** the observation window (A3),
scalar-mean DR (A17), BI-folded-into-the-ratio (A18), the Method-0 contrast, and the TIV valuation basis
(A19) are deliberate v1 simplifications grounded in the methodology doctrine; each carries a `revisit`
trigger in the [assumptions register](../plans/hail/assumptions.md).

---

## Research-repo index (the A-series)

All at `https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/…`

| Doc | Topic | What we take |
|---|---|---|
| [A10](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A10_design_space.md) | the modeling design space | the M0→M4 modular spine |
| [A11](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A11_module_vocabulary.md) | module / seam vocabulary | the four-module seam names |
| [A12](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A12_peril_taxonomy_spine.md) | peril × sub-peril × asset taxonomy | the (peril × asset) matrix |
| [A13](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A13_cell_walking_methodology.md) | cell-walk methodology + financial recursion | metric framing; financial-order |
| [A20](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A20_m0_m1_hazard_catalog.md) | M0→M1 catalog / event ontology | the catalog architecture |
| [A21](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A21_m1_m2_coupling_types.md) | M1→M2 coupling types + Minkowski | M2 coupling (areal) |
| [A22](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A22_m2_m3_damage_representation.md) | M2→M3 damage representation | the capex-weighted blend |
| [A24](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A24_distribution_choices.md) | distribution choices (freq · EVT · severity · financial) | NegBin · MC · EVT (deferred) |
| [A23](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A23_disruption_track_stepping_stone.md) · [A25](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/A25_damage_vs_disruption_scope.md) | disruption track + V1 scope | scope fence (damage-track V1) |
| [reference pack](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/references/A24_reference_pack.md) · [learning #19](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/19_canonical-citation-triplet-for-single-centroid-error.md) | the citation packs | the source of [`bibliography.md`](bibliography.md) |

## The methodology doctrine (shared Google Drive)

The four canonical Drive docs (local copies + folder links:
[`docs/google_drive_docs/README.md`](../google_drive_docs/README.md)) — Drive is the source of truth:

- **hazard_modeling_terminology** — vocabulary (magnitude vs intensity, λ vs AEP, return period, …).
- **Hazard_Data_Reference** — the Hazard→Exposure→Vulnerability→Loss chain + per-peril data sources.
- **hazard_asset_loss_distribution_methodology** — the doctrine: coupling types, frequency, severity,
  compound-Poisson MC → AEP/OEP, EVT, financial terms (the engine behind every metric).
- **risk_metrics_reference** — EAL / PML / VaR / TVaR as readings off one loss distribution; the
  "sum-of-expected-losses" build error (the old repo's cardinal failure).

---

## How to cite

- **External source** → use the short-key, which resolves in [`bibliography.md`](bibliography.md):
  `…over-dispersed counts ([Hussain et al. 2025]).`
- **Internal derivation** → cite the A-doc + section: `[REF: A21 §2.1]`, or link it.
- In **notebooks / layer READMEs**, a one-line "References" pointer here is enough — keep the full chain
  in this doc, not duplicated everywhere.

**Related:** [`docs/plans/hail/01_references.md`](../plans/hail/01_references.md) is the *planning intake*
list (what fed each phase as we built it); **this** folder is the canonical, repo-facing provenance.
