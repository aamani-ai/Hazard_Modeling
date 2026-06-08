# Google Drive docs — *InfraSure Hazard* reference set

Local `.docx` copies of the team's shared Google Drive folder **"InfraSure Hazard"**
(`Shared with me › Modeling › Docs › InfraSure Hazard`). They're kept in-repo so the reference
material is available offline and to agents working in this repo.

> **Google Drive is the source of truth.** These local copies are a snapshot (exported
> **2026-06-08**) and can drift — re-export from Drive when in doubt. The set is **shared with
> the team**, so edits belong in Drive, not here.

## Drive folders

| Folder | Link |
|---|---|
| 📁 **InfraSure Hazard** (root) | <https://drive.google.com/drive/folders/18A4LM7PBrhZQO1jepOKdPFhY-jCyGwi4> |
| &nbsp;&nbsp;└ 📁 **1) Reference** | <https://drive.google.com/drive/folders/1AICAoQXu09xAJ0DobAMaYbI28_ZyICZT> |
| &nbsp;&nbsp;└ 📁 **2) Methodology & Implementation** | <https://drive.google.com/drive/folders/1IqlpCA2tbBMUfXtwXpkFS0iLjyaVPK0B> |

## Files in this folder

Stored **flat** here; the *Drive subfolder* column shows where each lives in Drive. (Sizes are the
on-disk `.docx` sizes.) *More files will be added to "2) Methodology & Implementation."*

| Local file | Drive subfolder | ~Size | What it is |
|---|---|---|---|
| `hazard_modeling_terminology.docx` | 1) Reference | 20 KB | Definitions of hazard-modeling **input** terms, each paired with the term it's most often confused with. |
| `Hazard_Data_Reference.docx` | 1) Reference | 205 KB | Keystone framework + seven per-peril **public-data source** references for climate hazards to energy assets. |
| `risk_metrics_reference.docx` | 1) Reference | 213 KB | Use-case primer deriving EAL, PML, VaR, TVaR as readings off one loss distribution (the **outputs**). |
| `hazard_asset_loss_distribution_methodology.docx` | 2) Methodology & Implementation | 238 KB | Doctrine for **building** the annual loss-distribution vector from hazard events — the engine behind every metric. |

## Suggested reading order

The four lock into one pipeline — **events → loss distribution → metrics**:

1. **`hazard_modeling_terminology`** — the vocabulary (magnitude vs intensity, rate vs AEP, fragility vs vulnerability…). Read first to avoid the classic confusions.
2. **`Hazard_Data_Reference`** — the framing (the Hazard→Exposure→Vulnerability→Loss→Resilience chain, the damage-vs-disruption split) and where the actual public hazard data comes from, per peril.
3. **`hazard_asset_loss_distribution_methodology`** — how to turn events + damage curves into a vector of simulated annual losses (frequency · severity · duration · Monte-Carlo aggregation · EVT tails).
4. **`risk_metrics_reference`** — how EAL / VaR / PML (AEP & OEP) / TVaR are each just a reading off that distribution, and which metric each decision needs.

---

## File details

### 1. `hazard_modeling_terminology.docx`
**Hazard Modeling Terminology** · *Drive: 1) Reference*

Precise definitions of hazard-modeling **input** terms, each paired with the term it's most often confused with.

- **Purpose.** A controlled-vocabulary reference for the terms a modeler handles *before any loss curve exists*. Each entry gives a one-line definition, its unit, and a "Not:" line naming what it's most often mistaken for. The input-side mirror of the Risk Metrics Reference.
- **Key topics.** Magnitude vs intensity (footprint = per-event intensity map) · rate (λ) vs annual exceedance probability (p = 1−e^(−λ), T = 1/p) · return period as probability not calendar (+ forward adjustment for non-stationarity) · exposure / exposed value / sampled intensity / intensity measure · damage ratio vs damage state, fragility vs vulnerability, derating · severity distribution vs OEP/AEP · event duration vs duration-above-threshold vs downtime.
- **Sections.** Orientation → source/event terms → frequency & time-probability → site/exposure → response/severity → duration → confusions-at-a-glance → cross-reference index.
- **Use it when.** Defining or sanity-checking model inputs: settling whether a "frequency" is a rate or an annual probability, keeping magnitude vs intensity straight, picking the right sampled-intensity statistic, or distinguishing fragility from vulnerability outputs.

### 2. `Hazard_Data_Reference.docx`
**Hazard Data Reference — Energy Infrastructure Climate Risk Collection** · *Drive: 1) Reference*

Keystone framework plus seven per-peril public-data source references for modeling climate hazards to energy assets.

- **Purpose.** Establishes the conceptual framework (the Hazard→Exposure→Vulnerability→Loss→Resilience chain, and the split into a *damage* track and a *disruption/output-loss* track), defines the template and categorization rules every per-peril doc follows, then catalogs the actual public data sources per hazard — what they cover, how to build a footprint grid, and where the public domain falls short.
- **Key topics.** The catastrophe risk chain as the organizing spine · damage perils (fragility, repair cost) vs disruption perils (derating, energy-not-served) · peril/sub-peril rules + a fixed ten-field source schema · per-peril sources for hurricane, winter, wildfire, hail, flood, tornado/wind, drought/heat · coverage scorecards · named datasets (SLOSH, STORM/RAFT, FSim, ASCE 7-22, FEMA NRI/NFHL/FFRD, ERA5, NEX-GDDP/LOCA2, MTBS, MRMS/MESH, NOAA Atlas 14/15) · an inverse source-to-use-case matrix.
- **Sections.** Framework & Hazard Foundation (keystone) → Template Specification → per-peril chapters (hurricane · winter/ice · wildfire · hail · flood · tornado/wind · drought/heat) → Source Coverage & Starting Map.
- **Use it when.** You need to know what public hazard data exists for a peril and how to turn it into an asset-overlay intensity grid — or you need the project's framing/vocabulary. Note its scorecards flag gaps (no public stochastic catalog for winter, hail, or tornado/wind) and that some strong options (First Street, Fathom) are commercial.

### 3. `hazard_asset_loss_distribution_methodology.docx`
**Hazard-Asset Loss Distribution Methodology** · *Drive: 2) Methodology & Implementation*

Doctrine for building the annual loss-distribution vector from hazard events — the engine behind every risk metric.

- **Purpose.** The "doctrine layer" companion to the Risk Metrics Reference: where the Reference *reads* metrics off the annual loss distribution, this specifies how to *build* that distribution from hazard physics + asset characteristics. The object built is one concrete thing — a vector of simulated **actual** annual losses — from which EAL, VaR, PML (AEP & OEP), TVaR become trivial reads. A central premise: InfraSure holds event data (intensity, footprint, size), *not* a clean history of dollar losses, so losses come from applying a curated, sourced damage curve to events, then fitting a distribution. (Explicitly **not** the per-cell runbook (A-series) nor the implementation/code — a Repo Architecture Document is forthcoming.)
- **Key topics.** Universal `event_record` interface (standardize the output, not the physics) · coupling types (areal hit-or-miss, field intensity, site-conditioned) × exposure geometry (point, area, line, portfolio) · frequency (Poisson base, Negative Binomial for over-dispersion, non-stationary/regime-switching, thinning; never the expected-loss shortcut) · severity from curated fragility/vulnerability curves + duration → business interruption · compound-Poisson Monte-Carlo → AEP & OEP · financial transformation (ordered nonlinear terms; physical cap ≠ total economic/BI cap) · EVT tails (empirical body + GPD tail, threshold/shape selection) + validation.
- **Sections.** Prerequisites → Purpose & build pipeline → Universal interface → Catalog input contract → Coupling & exposure geometry → Frequency → Severity → Duration → Event-loss generation & annual aggregation → Financial transformation → Tail/EVT → Method-selection framework → Worked example (hail on a 100 MW solar farm) → Validation & staged roadmap → Glossary.
- **Use it when.** Understanding or implementing **how** the annual loss distribution is generated for a peril+asset: building/reviewing a hazard adapter (the shared `event_record` contract), choosing a frequency model, curating a damage curve with provenance, wiring the Monte-Carlo aggregation, extrapolating deep-tail PMLs with EVT, or sequencing the staged build (Phase 1: areal hit-or-miss, solar first). Pair with the Risk Metrics Reference for downstream definitions.

### 4. `risk_metrics_reference.docx`
**Risk Metrics Reference: EAL, PML, VaR, CVaR/TVaR** · *Drive: 1) Reference*

A use-case primer deriving EAL, PML, VaR, and TVaR as readings off one loss distribution.

- **Purpose.** Explains how each catastrophe/financial risk metric is a specific reading off a single loss distribution, along the chain *event catalog → two annual distributions (aggregate AEP, occurrence OEP) → metric readings → decisions (price, structure, capital)*. Teaches which metric each decision needs, how to build the distribution correctly (and the critical error of summing expected losses — corrupts every tail metric but leaves EAL intact), and how readings combine into a capital stack / risk-transfer tower.
- **Key topics.** Aggregate (AEP) vs occurrence (OEP) annual distributions · EAL as the mean · VaR = AEP-PML at a horizon/percentile · TVaR/CVaR as the coherent tail average · OEP-PML for per-occurrence limits · the "sum of expected losses" build error · six valid build methods + hazard-coupling map · worked example (Brazos Ridge, 200 MW TX wind) + capital-stack structuring.
- **Sections.** Orientation → the source object & its two distributions → building them correctly → reading the metrics → worked example → choosing the reading for the decision → pitfalls & counterparty checklist → glossary.
- **Use it when.** Choosing, interpreting, or defending a risk metric: which number a decision needs (EAL for pricing/premium, AEP-PML for insurance attachment & debt sizing, OEP-PML for per-occurrence limits, VaR/TVaR for capital & climate stress), interrogating a counterparty's "PML" (occurrence vs aggregate? return period? BI included?), or verifying tail metrics were built from actual rather than averaged losses. Use the Section 7 pitfalls list as a review aid.

---

*Per-file summaries above were generated from the actual document contents (2026-06-08). They're a
navigation aid — defer to the documents (and to Drive) for specifics.*
