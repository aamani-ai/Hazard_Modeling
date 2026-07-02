# Hail × Solar PV

The first **(peril × asset)** cell built end-to-end. This page is the *asset* half — how hail **couples to**,
**damages**, and produces **loss** for a solar farm. The asset-free hazard layer (catalog, frequency,
severity, the MESH-curation challenge) is in the [hail anchor](README.md); read that first.

> **Coupling type: areal hit-or-miss.** A solar farm is a dense, near-ground, contiguous polygon, so the
> question is simply "did a hail footprint cover the plant?" — a finite footprint either overlaps the asset
> or misses it.

---

## How hail reaches a solar farm (M2 → M3 → M4)

```
  M2  COUPLING             M3  DAMAGE               M4  LOSS & METRICS
  "does it hit?"           "if hit, how bad?"       "annual loss distribution"
  ┌─────────────────┐      ┌──────────────────┐     ┌──────────────────────┐
  │ p_hit =         │      │ size → DR         │     │ compound-Poisson MC: │
  │ (√F + √s)² / A  │ ───► │ capex-weighted    │ ──► │ Bernoulli(p_hit) ×   │
  │ areal hit/miss  │      │ blend, caps ~34%  │     │ FULL loss on a hit   │
  └─────────────────┘      └──────────────────┘     └──────────┬───────────┘
                                                               ▼
                                           EAL · VaR · PML · TVaR   ($ and % of TIV)
```

**M2 — coupling (areal hit-or-miss).** Per event, the probability the footprint overlaps the plant is the
**Minkowski** form:

```
p_hit = (√F + √s)² / A          (capped at 1)
```

`F` = severe-hail footprint area, `s` = solar plant footprint, `A` = collection-window area. This is the
*correct* areal form — it accounts for the asset's finite size — and it fixes the old repo's naive `F/A`
point-factor (kept only as a labeled diagnostic). The asset's location in the window is treated as unknown,
so `p_hit` is the expected overlap probability for a generic plant in the window — and because the window
*size* cancels (`λ_asset = ρ·E[(√F+√s)²]`, [LL06](../../learning_logs/06_collection_region_size_cancels.md)),
the deep run and the grid use the *same* coupling, just with their own `F` and `A`.

```
  In window A, a severe footprint (F) either covers the plant (s) — or misses it:

         MISS                          HIT
   ┌───────────────┐            ┌───────────────┐       ▓ = severe footprint (area F)
   │  ▓▓▓▓▓        │            │  ▓▓▓▓▓▓▓      │       ▢ = solar plant      (area s)
   │  ▓▓▓▓▓   ▢    │            │  ▓▓▓▢▓▓▓      │
   │  ▓▓▓▓▓        │            │  ▓▓▓▓▓▓▓      │       p_hit = (√F + √s)² / A
   └───────────────┘            └───────────────┘       (size of A cancels — LL06)
```

### V1 exposure simplification — full exposure on hit

`p_hit` only answers the M2 question: **does the hail footprint overlap the plant at all?** It does not
estimate what fraction of the array is touched after overlap. In V1, once the Bernoulli hit occurs, M3
treats the at-risk solar footprint as fully exposed:

```
conditional_loss_if_hit = damage_ratio(hail_size) × exposed_value
exposed_fraction = 1.0
```

This is acceptable as a first-pass simplification because the modeled solar footprints are small relative
to typical severe-hail swaths, so a swath that reaches the plant usually covers the exposed array. It is
still a simplification: small swaths, edge clips, larger plants, or non-compact layouts should eventually
use true geometric overlap, e.g. `exposed_fraction = overlap_area / asset_area`.

Keep this separate from `p_hit`: `p_hit` belongs to frequency / hit-miss sampling in M4; `exposed_fraction`
belongs to conditional severity / value scaling in M3. Do **not** multiply `p_hit` into M3 loss.

**M3 — damage.** Hail size → damage ratio via a **capex-weighted subsystem blend** (`infrasure-damage-curves`):
PV modules `L≈0.95` + trackers `L≈0.40`, weighted by NREL capex shares. Most of the asset value —
inverters, substation, electrical, civil — is hail-immune, so the **asset damage ratio caps at ~34%**.
The curve saturates (logistic; no extrapolation), which is also why the extreme MESH tail is largely *moot
for solar loss* — the panel is destroyed well before the implausible sizes — one of the candidate answers to
the [outlier question](README.md#5-challenges--limitations).

**M4 — loss & metrics.** Compound-Poisson Monte Carlo: per simulated year draw the event count, flip a
`Bernoulli(p_hit)` per event, and on a **hit** add the **full** conditional loss (never `p_hit × loss` — that
collapses the variance and was the old repo's bug). Off the annual AEP/OEP vectors we read EAL, VaR, PML, TVaR.

## The two deployments, side by side

The hazard-layer differences (window, frequency model, footprint) are explained in the
[anchor §3](README.md#3-how-we-model-it--two-deployments-of-one-engine). Here's how the *asset* result lands
in each:

| | Deep per-asset run | CONUS grid |
|---|---|---|
| **Asset** | real: Hayhurst TX Solar, **24.8 MW**, EIA 66880 | canonical: **100 MW** at each valued cell |
| **Footprint `s`** | ≈ **0.50 km²** (real array estimate) | **1.5 km²** (canonical 100 MW dense footprint) |
| **TIV** | **$36.78M** (≈ $1,483/kW) | **$148.3M** (same $1,483/kW basis) |
| **Window `A`** | 50-mi circle, ≈ 20,342 km² | the 0.25° cell, ≈ 600 km² |
| **`F` source** | reconstructed event footprint polygon | severe-pixel area within the cell (proxy) |
| **Frequency** | NegBin, λ_collection = 29.6/yr | Poisson, per-cell `lambda_cell_raw` |
| **MC** | 300k years | 250k-year target |
| **Status** | **built end-to-end** | **selected-cell smoke only — not reportable** |

## Headline numbers

**Deep per-asset (Hayhurst) — real, record-limited:**

- `λ_asset` = λ_collection × E[p_hit] ≈ **0.26 hits/yr** (~1 every 3.8 yr)
- **EAL ≈ 5.7% of TIV ($2.09M)** · AEP-PML₁₀₀ **54%** · AEP-PML₂₅₀ **62%** · OEP-PML₁₀₀ **34%**
- ~77% of years are zero-loss
- **Trust the body (EAL, ~PML₁₀₀); treat the deep tail as a floor** — losses are bootstrapped from 158
  observed events and the curve caps at ~34%, so 1-in-250+ is biased low ([A23](../../plans/hail/assumptions.md)).

**CONUS grid:** the engine produces the full comparable metric schema (EAL, VaR, PML, TVaR, AEP/OEP, $ and
%-TIV) on a selected-cell smoke set under two severity policies (`raw_mrms`, `cap_100mm_sensitivity`). All
engine QA passed, **but no grid loss number is reportable** until the severity / outlier policy
([anchor §5a](README.md#5-challenges--limitations)) is decided. Frequency screening is usable now.

## Assumptions specific to this pair

- Coupling = areal hit-or-miss, Minkowski (deep: A11; grid: G6/coupling). V1 exposure simplification = full exposure on hit (`exposed_fraction = 1`, A13).
- Damage curve = capex-weighted blend, scalar mean, caps ~34% (A15–A17); conditional-DR *distribution* deferred.
- Canonical grid solar: 100 MW / 1.5 km² / TIV $148.3M (G2, G11). Deep asset TIV $36.78M, valuation basis unconfirmed (A19).

## Deferred (V1.5 / V2)

EVT-GPD severity tail · conditional damage-ratio distribution · damage-curve calibration to PV claims ·
financial terms (deductibles / limits / BI) · grid severity-QA decision + full-CONUS scaleout.

## Go deeper

- **Deep-run code:** [`Notebooks/hail/solar/`](../../../Notebooks/hail/solar/README.md) (M2 → M3 → M4).
- **Grid code:** [`Notebooks/hazard_conus_grid/hail/solar/`](../../../Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/README.md).
- **Registers:** [`plans/hail/assumptions.md`](../../plans/hail/assumptions.md) · [`plans/hazard_conus_grid/assumptions.md`](../../plans/hazard_conus_grid/assumptions.md).
- **Hazard modeling choices:** [`modeling_choices.md`](modeling_choices.md).
- **Hazard layer:** [hail anchor](README.md).
