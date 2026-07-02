# Hail × Solar PV — the proving cell (M2 → M3 → M4)

The first **(peril × asset)** cell built end-to-end. It **inherits the shared hail catalog**
([`../m0_input_data/`](../m0_input_data/) M0 + [`../m1_catalog/`](../m1_catalog/) M1 — see the
[hail peril overview](../README.md)); *this* folder is where coupling, damage, and loss specialize to
a solar farm.

**Asset:** Hayhurst Texas Solar · EIA 66880 · **TIV $36.78M** · footprint `s ≈ 0.50 km²` in a
50-mi region `A ≈ 20,342 km²`. **Coupling type: areal hit-or-miss** (a solar farm is a *dense areal
polygon*).

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
          ▼                         ▼   (shared catalog — ../m0, ../m1) │
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

### 4. Artifact lineage (M1 catalog → M2 → M3 → M4)

```text
 …_m1_catalog.parquet (GeoParquet)   ◄── the shared catalog (../m1_catalog)
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

### 5. Anatomy of one simulated year (inside the M4 Monte Carlo)

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
        repeat 300k years ──► sorted AEP/OEP vectors ──► EAL / VaR / PML / TVaR
        (~77% of years: zero hits → $0)
```

### 6. What's fitted vs. what's not (v1 modeling choices, and why)

Only **frequency** got a parametric fit. The two "magnitude" pieces — hail size and damage-given-size —
deliberately did **not** (sound for the *body* of the loss distribution; the *deep-tail* upgrades are
logged as `deferred` in the [assumptions register](../../../docs/plans/hail/assumptions.md)).

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

## The layers (M2 → M3 → M4)

### M2 — coupling  ·  [📖 folder README](m2_coupling/README.md)

Hail = **areal hit-or-miss**: per-event Minkowski hit probability `p = (√F + √s)² / A`, thinning the
regional rate to the asset — **fixing the old repo's point-factor (`F/A`) error**, with known-answer
checks. `λ_asset = λ_collection · E[p] = 0.26/yr` (~1 hit every 3.8 yr). Plan:
[`phase-3-coupling.md`](../../../docs/plans/hail/done/phase-3-coupling.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `m2_coupling/01_coupling.ipynb` | per-event `pᵢ` (Minkowski) + old-repo comparison + geometric cross-check; carries hail size to M3 | `data/hail/hayhurst_hail_m2_coupled.parquet` + `…_m2_summary.json` | ✅ built + executed |

### M3 — damage  ·  [📖 folder README](m3_damage/README.md)

Severity: each event's hail size → a **capex-weighted subsystem blend** (from
[`infrasure-damage-curves`](../../../infrasure-damage-curves): PV_MODULE `L=0.95` + TRACKER `L=0.40`
× NREL capex weights → `Asset_DR = Σ wᵢ·DRᵢ`, **caps ~34%** of TIV — ~64% of asset value, the
inverters/substation/electrical/civil, is hail-immune → 0) → a damage ratio → the **conditional**
dollar loss (the full loss *if it hits*; `pᵢ` carried, never multiplied in). Plan:
[`phase-4-damage.md`](../../../docs/plans/hail/done/phase-4-damage.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `m3_damage/01_damage.ipynb` | capex-weighted `size → damage ratio` curve → per-event damage ratio + conditional loss (max ≈ $12.6M = 34% of TIV) | `data/hail/hayhurst_hail_m3_damage.parquet` + `…_m3_summary.json` | ✅ built + executed |

### M4 — loss & metrics  ·  [📖 folder README](m4_loss_metrics/README.md)

The finale: **compound-Poisson Monte Carlo** (300k years) — per simulated year, `Bernoulli(pᵢ)` + full
conditional loss → annual AEP/OEP vectors → **EAL / VaR / PML / TVaR**. *The part the old repo broke* —
done right, with a Method-0 contrast + a Poisson-vs-NegBin contrast + known-answer checks. Plan:
[`phase-5-loss-metrics.md`](../../../docs/plans/hail/done/phase-5-loss-metrics.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `m4_loss_metrics/01_loss_metrics.ipynb` | compound-Poisson MC → AEP/OEP → EAL/VaR/PML/TVaR; Method-0 + Poisson-vs-NegBin contrasts | `data/hail/hayhurst_hail_m4_annual_vectors.parquet` + `…_m4_metrics.json` | ✅ built + executed |

---

## Headline numbers (real, record-limited)

**EAL 5.7%** of TIV ($2.09M) · AEP-PML₁₀₀ **54%** · AEP-PML₂₅₀ **62%** · OEP-PML₁₀₀ **34%** · ~77% of
years zero-loss. **Real but record-limited** — λ is fitted on a ~5.65-yr record and the damage curve is
temporary, so the distribution *body* (EAL, ~PML₁₀₀) is trustworthy while the **deep tail is
bootstrap-truncated**. See [`m4_loss_metrics/README.md`](m4_loss_metrics/README.md) for exactly what to
trust vs. not.

## Solar-specific deferred items

- **EVT-GPD severity tail** (A23) — deep return periods beyond the largest observed event.
- **Conditional DR distribution** (A17) — vs. the current scalar-mean curve.
- **Damage-curve calibration** to PV claims (the `infrasure-damage-curves` revamp) + **financial terms**
  (deductibles / limits / BI — methodology §9).

See the [assumptions register](../../../docs/plans/hail/assumptions.md) `deferred` rows.

## What The Hail Solar Cell Asks

```text
solar M2 asks:
  for each hail footprint:
    what is the footprint area?
    what is the solar plant area?
    what is the hit probability after the Minkowski asset-size correction?
    is the hit probability kept out of severity?

solar M3 asks:
  if the event hits:
    what hail size reaches the plant?
    what PV module and tracker damage ratios apply?
    what capex-weighted asset damage ratio results?
    what full conditional loss is emitted?

solar M4 asks:
  across simulated years:
    how many regional hail events occur?
    which events hit the plant?
    what full losses are added on hits?
    what AEP and OEP metrics result?
```

The asset-cell rule is:

```text
M2 decides hit probability.
M3 decides full loss if hit.
M4 flips the hit coin.
```
