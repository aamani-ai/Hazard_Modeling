# Notebooks — Hail → Solar pipeline

The executed, step-by-step end-to-end workflow for **hail**. Driven by the plan in
[`../../docs/plans/hail/`](../../docs/plans/hail/README.md) and the per-phase loop in
[`../../docs/workflows/feature_workflow.md`](../../docs/workflows/feature_workflow.md). Datasets are saved
under [`../../data/hail/`](../../data/hail). Kernel: `.venv` (`hazard_modeling`).

## Pipeline at a glance — ASCII maps

### 1. The big picture (M0 → M4)

```text
                        RAW WORLD                                   MODEL WORLD
 ┌──────────────────────────────────────────────┐    ┌─────────────────────────────────────┐
 │                                              │    │                                     │
 │   NOAA Storm Events          MRMS MESH       │    │   Asset: Hayhurst Texas Solar       │
 │   (point reports,            (gridded radar, │    │   EIA 66880 · TIV $36.78M           │
 │    1996→2024)                 2020→2026)     │    │   footprint s, region A             │
 │        │                         │           │    │                                     │
 └────────┼─────────────────────────┼───────────┘    └──────────────────┬──────────────────┘
          │                         │                                   │
          ▼                         ▼                                   │
 ┌─────────────────────────────────────────────┐                        │
 │  M0  INPUT DATA   "what hit the region?"    │                        │
 │  one interface, two sources                 │                        │
 │  · 373 NOAA reports (cross-check)           │                        │
 │  · 158 MRMS hail-days / 5.65 yr (spine)     │                        │
 └──────────────────────┬──────────────────────┘                        │
                        ▼                                               │
 ┌─────────────────────────────────────────────┐                        │
 │  M1  EVENT CATALOG   "canonical events"     │                        │
 │  hail-day → Event w/ footprint polygon F    │                        │
 │  + frequency fit:  NegBin                   │                        │
 │    λ_collection = 29.6/yr   φ = 3.37        │                        │
 └──────────────────────┬──────────────────────┘                        │
                        ▼                                               ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │  M2  COUPLING   "does an event hit THIS asset?"                         │
 │  per-event Minkowski hit probability:  p = (√F + √s)² / A               │
 │  λ_asset = λ_collection · E[p] = 0.26/yr   (~1 hit every 3.8 yr)        │
 └──────────────────────┬──────────────────────────────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────┐   ┌────────────────────────┐
 │  M3  DAMAGE   "if hit, how bad?"            │◄──│ infrasure-damage-curves│
 │  capex-weighted subsystem blend             │   │ PV_MODULE  L=0.95      │
 │  hail size → damage ratio (DR)              │   │ TRACKER    L=0.40      │
 │  asset DR caps at ~34% of TIV               │   │ rest: hail-immune      │
 └──────────────────────┬──────────────────────┘   └────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────┐
 │  M4  LOSS & METRICS   "annual loss dist"    │
 │  compound-Poisson Monte Carlo               │
 │  (NegBin counts × per-event thinning)       │
 │  → AEP / OEP per-year vectors               │
 │  → EAL 5.7% · PML₁₀₀ 54% · PML₂₅₀ 62%       │
 └─────────────────────────────────────────────┘
```

### 2. The conceptual chain (one line)

```text
 evidence ──► events ──► hits ──► damage ──► dollars
   (M0)        (M1)      (M2)      (M3)       (M4)

 "what       "discrete   "does it  "if hit,   "what does a year
  happened    things      reach     how much   of this cost, and
  out there"  with rate   my site"  breaks"    how bad is a bad year"
              λ and
              footprint"
```

### 3. The math spine (how λ and severity combine)

```text
              FREQUENCY                          SEVERITY
 ┌────────────────────────────┐      ┌────────────────────────────────┐
 │ N_regional ~ NegBin        │      │ per event i:                   │
 │   mean λ_coll = 29.6/yr    │      │   hail size MESH_i             │
 │   Fano φ = 3.37            │      │        │ damage curve          │
 │        │ thinning by p_i   │      │        ▼                       │
 │        ▼                   │      │   DR_i ∈ [0, ~0.34]            │
 │ N_hits: λ_asset = 0.26/yr  │      │   loss_i = DR_i × TIV          │
 └─────────────┬──────────────┘      └───────────────┬────────────────┘
               │                                     │
               └───────────────┬─────────────────────┘
                               ▼
              ┌──────────────────────────────────┐
              │  Monte Carlo year y:             │
              │   draw N events, thin by p,      │
              │   draw losses, cap at TIV        │
              │                                  │
              │   AEP_y = Σ losses  (aggregate)  │
              │   OEP_y = max loss  (occurrence) │
              └────────────────┬─────────────────┘
                               ▼
              ┌──────────────────────────────────┐
              │  EAL  = mean(AEP)        = 5.7%  │
              │  PML_T = quantile 1−1/T          │
              │   PML₁₀₀(AEP) = 54%  ·  VaR/TVaR │
              │  ~77% of years: zero loss        │
              └──────────────────────────────────┘
```

### 4. The data-source decision (DD-1/DD-3 — why two sources don't merge)

```text
        NOAA (long, biased, points)        MRMS (short, clean, footprints)
                 │                                   │
                 │     ✗ naive splice                │
                 │       (rate jump at seam)         │
                 │                                   │
                 ▼                                   ▼
        ┌─────────────────┐               ┌─────────────────────┐
        │ cross-check /   │               │ THE SPINE:          │
        │ calibration     │──validates──► │ events, footprints, │
        │ (adds 0 events) │               │ λ_collection, p     │
        └─────────────────┘               └─────────────────────┘
                 │
                 └─► later (Stage 2): bias-correct MESH FAR → extend λ record
```

### 5. Artifact lineage (each layer reads only the previous layer's parquet)

```text
 Hydronos API          AWS Open Data (MRMS GRIB tiles)
      │                        │
      ▼                        ▼ (scripts/scan_mrms_record.py — cache-first, resumable)
 …_m0_noaa_50mi.parquet   …_m0_mrms_202010_202606.parquet      data/hail/mrms_raw/ (~905 MB, gitignored)
      │  (cross-check)         │  (spine)
      └──────────┬─────────────┘
                 ▼  m1_catalog/01_event_catalog
 …_m1_catalog.parquet (GeoParquet) + …_catalog.geojson + …_m1_manifest.json
                 │
                 ▼  m2_coupling/01_coupling
 …_m2_coupled.parquet + …_m2_summary.json
                 │
                 ▼  m3_damage/01_damage          ◄── data/hail/damage_curves/
 …_m3_damage.parquet + …_m3_summary.json             hail_solar_asset_capex_weighted.json
                 │
                 ▼  m4_loss_metrics/01_loss_metrics
 …_m4_annual_vectors.parquet + …_m4_metrics.json     ◄── THE HEADLINE NUMBERS
```

### 6. Anatomy of one simulated year (inside the M4 Monte Carlo)

```text
 year y ──► draw N ~ NegBin(λ_coll=29.6, φ=3.37)         e.g. N = 31 regional events
                │
                ▼  for each event: resample (event, p_i, loss_i) from the catalog
            ┌───────────────────────────────────────────────┐
            │ event 1:  Bernoulli(p₁=0.004) → miss → $0     │
            │ event 2:  Bernoulli(p₂=0.011) → miss → $0     │
            │   …                                           │
            │ event k:  Bernoulli(p_k=0.018) → HIT          │
            │           → loss_k = DR_k × TIV  (full,       │
            │             conditional — p never multiplied  │
            │             into the loss: the LOTV fix)      │
            └───────────────────────┬───────────────────────┘
                                    ▼
              AEP_y = Σ hit losses (capped at TIV) · OEP_y = max hit loss
                                    ▼
        repeat ~100k years ──► sorted AEP/OEP vectors ──► EAL / VaR / PML / TVaR
        (~77% of years: zero hits → $0)
```

### 7. What's fitted vs. what's not (v1 modeling choices, and why)

Only **frequency** got a parametric fit. The two "magnitude" pieces — hail size and damage-given-size —
deliberately did **not** (sound for the *body* of the loss distribution; the *deep-tail* upgrades are
logged as `deferred` in the [assumptions register](../../docs/plans/hail/assumptions.md)).

```text
 component            v1 treatment                      fitted?   tail-honest upgrade (deferred)
 ─────────────────    ───────────────────────────────   ───────   ──────────────────────────────
 FREQUENCY            NegBin fit on annual counts        ✅ YES    NOAA-calibrated λ extension
 (event counts)       λ=29.6/yr, Fano φ=3.37                       (DD-3 Stage 2 — MESH FAR
                      (cheap to fit; over-dispersion                bias-correction)
                       is tail-critical → fit it now)

 HAIL SIZE            empirical bootstrap of the         ❌ NO     EVT-GPD size-tail fit (A23)
 (hazard magnitude)   158 observed event sizes                     — bootstrap can't exceed the
                      (real sample → good *body*)                   largest seen event (118 mm)

 DAMAGE | SIZE        deterministic curve:               ❌ NO     conditional DR distribution
 (severity)           size → one scalar DR                         (A17) — same-size events
                      (capex-weighted blend, cap ~34%)              damage differently; scalar
                                                                    mean smooths the spread away

                              WHY THE ASYMMETRY?
            ┌─────────────────────────────────────────────────────┐
            │  body of the loss distribution (EAL, ~PML₁₀₀):      │
            │    bootstrap + real curve is enough  → didn't need  │
            │                                                     │
            │  deep tail (1-in-250+, OEP):                        │
            │    truncated by max-observed-size + the 34% cap     │
            │    → needed, but the damage curve itself is the     │
            │      dominant (and temporary) uncertainty — fitting │
            │      a fancy severity distribution on top of an     │
            │      uncalibrated curve = polishing the wrong thing │
            └─────────────────────────────────────────────────────┘
```

---

## `m0_input_data/` — the M0 (input-data) layer, **one notebook per source**  ·  [📖 folder README](m0_input_data/README.md)

The whole point of the M0→M3 architecture is to test *multiple* input datasets behind one interface, then
reconcile them. Each cell carries description → code → output/plot/table, and does a *complete-pass* field
dictionary (per `docs/principles/notebook_work/`).

| Notebook | Source | Grain | Status |
|----------|--------|-------|--------|
| `01_noaa_hydronos.ipynb` | NOAA Storm Events (Hydronos API) + FEMA NRI (reference-only) | **point reports** (hail size + location; no footprint) | ✅ built + executed |
| `02_mrms_aws.ipynb` | MRMS MESH (AWS Open Data) | **gridded** → real event **footprints**; **opens with a from-scratch "what is this data" walkthrough** (§1–§7) before exploring (§8–§11) | ✅ built + executed |

> **New to MRMS?** `02` now **starts from the very basics** — NOAA is a *list of events*; MRMS is a *picture*
> (a grid of hail-size numbers). §1–§7 explain it ground-up (mental model → the actual bytes/numbers → the
> field→threshold→polygon journey → how we fetch it) before §8–§11 explore the window and emit the M0 record.
> Complex raw data earns this pass — see [`learning_logs/03`](../../docs/learning_logs/03_meet_complex_raw_data_from_scratch.md).

> **Reconciling the sources is *not* a third M0 source.** Combining the sources into one clean event set is
> the front of **M0→M1 (the event catalog)** — A20's "catalog construction" — so it lives in `m1_catalog/`
> below, not here. `m0_input_data/` holds only the per-source M0 explorations.

## `m1_catalog/` — the M0 → M1 layer (the event catalog)  ·  [📖 folder README](m1_catalog/README.md)

Normalizes the M0 evidence into **one canonical event record per physical event** (a footprint raster
bundle). Per [`DD-1`](../../docs/plans/hail/decisions.md): **MRMS is the spine** (footprints), **NOAA is a
cross-check overlay** (calibration only — adds no events). Plan:
[`../../docs/plans/hail/phase-2-event-catalog.md`](../../docs/plans/hail/phase-2-event-catalog.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_event_catalog.ipynb` | MRMS hail-days → canonical `Event` records (real **footprint-swath polygons**) + `CatalogManifest`; NOAA cross-check → `confidence_flags` | `data/hail/hayhurst_hail_m1_catalog.parquet` (**GeoParquet**) + `…_catalog.geojson` + `…_m1_manifest.json` | ✅ built + executed |

## `m2_coupling/` — the M1 → M2 layer (does the event hit the asset?)  ·  [📖 folder README](m2_coupling/README.md)

Hail = **areal hit-or-miss**: per-event Minkowski hit probability `p = (√F + √s)² / A`, thinning the regional
rate to the asset — **fixing the old repo's point-factor (`F/A`) error**, with known-answer checks. Plan:
[`../../docs/plans/hail/phase-3-coupling.md`](../../docs/plans/hail/phase-3-coupling.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_coupling.ipynb` | per-event `pᵢ` (Minkowski) + old-repo comparison + geometric cross-check; carries intensity to M3 | `data/hail/hayhurst_hail_m2_coupled.parquet` + `…_m2_summary.json` | ✅ built + executed |

## `m3_damage/` — the M2 → M3 layer (how bad is it, if it hits?)  ·  [📖 folder README](m3_damage/README.md)

Severity: each event's hail size → a **curated** PV damage curve → a damage ratio → the **conditional** dollar
loss (the full loss *if it hits*; `pᵢ` carried, never multiplied in). Plan:
[`../../docs/plans/hail/phase-4-damage.md`](../../docs/plans/hail/phase-4-damage.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_damage.ipynb` | curated `size → damage ratio` curve → per-event damage ratio + conditional loss | `data/hail/hayhurst_hail_m3_damage.parquet` + `…_m3_summary.json` | ✅ built + executed |

## `m4_loss_metrics/` — the M3 → M4 layer (loss & metrics)  ·  [📖 folder README](m4_loss_metrics/README.md)

The finale: **compound-Poisson Monte Carlo** — per simulated year, `Bernoulli(pᵢ)` + full conditional loss →
annual AEP/OEP vectors → **EAL / VaR / PML / TVaR**. *The part the old repo broke* — done right, with a
Method-0 contrast + known-answer checks. Metrics are **real but record-limited** (λ **fitted** on the ~5.65-yr MRMS record — DD-3 Stage 1). Plan:
[`../../docs/plans/hail/phase-5-loss-metrics.md`](../../docs/plans/hail/phase-5-loss-metrics.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_loss_metrics.ipynb` | compound-Poisson MC → AEP/OEP → EAL/VaR/PML/TVaR; Method-0 contrast; λ sweep | `data/hail/hayhurst_hail_m4_annual_vectors.parquet` + `…_m4_metrics.json` | ✅ built + executed |

---

**🎉 The full M0 → M4 hail skeleton now runs end-to-end** — raw evidence → catalog → coupling → damage →
annual loss → risk metrics, the right way. Production path: widen the MRMS record (→ real λ), calibrate the
damage curve, add financial terms + an EVT tail (see each layer's `📖 folder README` and the
[assumptions register](../../docs/plans/hail/assumptions.md) `deferred` rows).
