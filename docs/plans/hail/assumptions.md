# Hail pipeline — assumptions register

Every modeling **assumption** the hail → solar build rests on, in one place. An assumption is an input,
parameter, curve, or simplification we **take as given** — because we don't yet have better, or to keep v1
tractable. This is the companion to [`decisions.md`](decisions.md): *decisions* are choices we made between
options (*"we chose MRMS-only over a splice"*); *assumptions* are the values/curves/simplifications those (and
the data) leave us holding (*"the damage curve is these four literature points"*). When an assumption is
load-bearing, **its provenance — not a fit statistic — is what the number rests on.**

**Status legend:** `assumed` (a stated modeling choice/value) · `curated` (taken from literature) · `input`
(given data) · `deferred` (not done yet — needs more data/work) · `decided → DD-n` (backed by a decision).

Each layer's notebook + folder README surfaces its own assumptions inline; this register is the index.
Grouped by layer (M0 → M3); newest layer last.

---

## M0 — input data

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| A1 | **Region = 50-mi circle** around the asset, **assumed spatially homogeneous** (≈uniform event density, footprint size & hail severity across it) | matches NOAA's search radius (apples-to-apples); the region area `A` **cancels** in `λ_asset = λ_collection·p`, so the radius itself washes out — **what's actually assumed is the spatial homogeneity** (it's what makes `λ_collection ∝ A` hold). Chosen for homogeneity + data-consistency, not magnitude ([learning_logs/06](../../learning_logs/06_collection_region_size_cancels.md)). | assumed | larger region / portfolio — re-check homogeneity holds |
| A2 | **Severe threshold = 25.4 mm (1″)** | NWS severe-hail definition; H10 | assumed (standard) | if sub-1″ hail proves damaging to PV |
| A3 | **Window = Apr–Jun 2024** (one peak season) | bounded for volume; MRMS-on-AWS spans ~2020-10→present | deferred | widen for a real λ (DD-1/DD-2) |
| A4 | **Daily grain = last tile of day ≈ 24-h max** | the `MESH_Max_1440min` product | assumed | true daily max over all tiles |
| A5 | **MESH is a radar *estimate*** (over-forecasts; ~75% of hail below it) — not ground truth | Witt 1998; [learning_logs/01](../../learning_logs/01_extending_a_short_hazard_record.md) | inherent (data caveat) | bias-correct MESH vs reports |

**A1 note — spatially homogeneous.** Here this means the 50-mi circle is treated as **one local hail
regime**: event density per km², footprint-size mix, and hail-size/severity mix are roughly stable inside the
circle. It does **not** mean every grid cell is identical. The `A` cancellation is credible only inside that
local-regime assumption; a much larger region could mix different hail climates and break `λ_collection ∝ A`.

## M1 — event catalog

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| A6 | **One event = one hail-day** | 24-h-max product; >95% of a day's severe reports fall in one ~4-h window | assumed (simplification) | sub-daily / connected-component splitting |
| A7 | **MRMS = spine, NOAA = cross-check** (adds no events) | footprints must cross the seam; record homogeneity | decided → [DD-1](decisions.md) | calibrated splice for a long record |
| A8 | **Frequency = Negative Binomial** (Poisson nested) | SCS over-dispersion **CONFIRMED**: φ≈3.4 on the ~5.65-yr record (A24/DD-2) | **fitted** (DD-3 Stage 1) | longer record → fit at higher n (only 5 full years so far) |
| A9 | **Dispersion prior: Fano φ median ≈ 2, 90% [1, 3.5]** | SCS VMR ≈ 1.5–3; weakly-informative | assumed (prior) | data-overridable as the record grows |
| A24 | **Dispersion test is underpowered at small n** — φ fitted on **5 full years**; a stable Fano/NegBin fit wants ~10–15 yr | count-dispersion sampling theory: at n=5 the φ point estimate is noisy (90% band ~[1, 3.5], A9) — *decent, not ideal*. Referenced by A8/A20 and the M1 manifest. | assumed (documented) | re-fit φ at higher n; shrink toward the prior φ≈2 meanwhile (DD-2) |
| A10 | **Footprint = union of above-threshold cells** (speckled MultiPolygon; no smoothing) | faithful to the raw cells | assumed (simplification) | dilation / morphological-close (H10) |

## M2 — coupling

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| A11 | **Coupling = areal hit-or-miss; hit prob = Minkowski `(√F+√s)²/A`** — a size-based probability of **any overlap**, not a distance-to-Hayhurst score | A21; methodology §5 (the correct form; fixes the `F/A` bug). `pᵢ` uses event footprint size `F`, asset size `s`, and region area `A`; it does **not** use the historical footprint's observed distance from the asset. | decided (correct form) | true geometric-overlap as primary |
| A12 | **Asset footprint `s` ≈ 0.50 km²** (24.8 MW × 5 ac/MW, array) | capacity estimate; `s ≪ F` so result insensitive here | assumed (estimate) | actual plant polygon (solar-boundary pipeline) |
| A13 | **Full exposure on hit** (`exposed_fraction = 1`) | `pᵢ` only decides whether the footprint overlaps the plant at all, including edge-contact cases. Conditional on a hit, v1 assumes the whole at-risk solar footprint is exposed because `s ≪ F` (a swath reaching the farm usually covers it all). **Under investigation:** small swaths that only clip a site edge should eventually use `overlap_area / asset_area` rather than full exposure. | assumed (simplification) | larger assets / line geometry / partial overlap; true geometric overlap with exposed fraction |
| A14 | **`λ_asset` = `λ_collection` × `p`** — the asset's annual hit *rate* | `λ_collection` **fitted** ≈ 29.6/yr on the ~5.65-yr record (DD-3 Stage 1) → `λ_asset` ≈ **0.26/yr** | **fitted** (record-limited) | NOAA-calibrated extension for a longer record (DD-3 Stage 2) |

## M3 — severity / damage

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| A15 | **Damage curve = capex-weighted subsystem blend** (`infrasure-damage-curves`): PV_MODULE `L=0.95` + TRACKER `L=0.40` × NREL capex weights → **`Asset_DR=Σwᵢ·DRᵢ`, caps ~34%** | IBHS/IEC empirical module curve + NREL ATB/SAM weights; ~64% of asset value hail-immune → 0 | curated (medium) | full subsystem decomposition; **plant-specific at-risk value-allocation** + conditional-DR distribution — see [`learning_logs/05`](../../learning_logs/05_damage_curve_three_coupled_choices.md) |
| A16 | **Curve saturates (logistic) — no extrapolation** | logistic caps at the capex-weighted `L`; replaces the §12 curve that ran to ~100% | resolved (extrapolation retired) | — |
| A17 | **Damage representation = scalar mean** (no conditional distribution) | methodology v1 choice | assumed (simplification) | conditional *distribution* — tail-relevant; Phase 5 severity sampling (A22) |
| A18 | **Duration / BI deferred** — the damage ratio is physical repair cost only; downtime → revenue loss is a separate additive stage | methodology §7 + §9 | deferred | a dedicated BI / duration stage |
| A19 | **Asset value (used as TIV) = $36,778,400** | the **asset registry** (`model-gpr/local_data/asset_registry_db/asset_registry_latest_export_2026-04-15.csv`, EIA 66880, AIG Client Portfolio) — equals the **old model's `asset_exposure`**, reused for a comparable loss basis; implied **≈ $1,483/kW_ac** (24.8 MW AC). **Caveat:** the registry doesn't state the *valuation basis* (TIV vs replacement-cost vs insured-value), and we treat it as TIV — it scales **every** dollar metric linearly. | input (given) | confirm the valuation basis; refresh from the registry |

## M4 — loss & metrics

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| A20 | **`λ_collection` = 29.6/yr (FITTED)** · NegBin counts (φ=3.37) | fitted in M1 on the ~5.65-yr record; φ=3.37 is the **raw** Fano (no Bayesian shrinkage toward the prior φ≈2 — at n=5 the point estimate is noisy) | **fitted** (real, record-limited — *not* illustrative) | shrink φ toward the prior at small n; longer record + EVT for the deep tail (DD-3 Stage 2) |
| A21 | **Gross *physical* loss only** (no deductibles / limits / BI) | methodology §9 financial terms deferred | deferred | add a financial-terms + BI stage |
| A22 | **MC = 300k years; cap per simulated year; empirical percentiles** | standard cat-model engine; current-climate, historical-only. The per-year cap applies to **AEP** (OEP has no explicit asset ceiling — harmless now: conditional losses ≤34% < TIV). EAL known-answer check compares the *capped* MC mean to the *uncapped* analytic — valid only while the cap rarely binds (true here). | assumed | EVT-GPD tail (§10) for deep return periods |
| A23 | **Deep-tail PML & OEP-PML are bootstrap-truncated** | severities are resampled from the 158 observed events + the curve caps at 34%, so the MC **cannot exceed the largest observed/capped loss** → 1-in-250+ and OEP-PML are biased low (sound for the body/PML100; not for the deep tail) | assumed (documented) | EVT-GPD severity tail + longer record ([learning_logs/01](../../learning_logs/01_extending_a_short_hazard_record.md)) |

---

**How to use this:** when you touch a layer, check its block here; when you add or change an assumption, add
or update a row (and surface it in that layer's notebook + README). The `deferred` rows are the backlog that
turns the v1 skeleton into a production model — most of them resolve by **widening the MRMS record** and
**calibrating the damage curve**.
