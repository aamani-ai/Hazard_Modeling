# Convective Wind × Wind Farm — the asset cell (M2 → M3 → M4)

The **(peril × asset)** cell for the convective-wind peril on a **wind farm** — the wind analogue of
[`hail/solar/`](../../hail/solar/README.md). See the [**convective-wind peril overview**](../README.md) for the
sub-peril framing + the shared catalog. It **inherits the shared convective-wind catalog** (peril-level,
asset-independent): [`../layer0/`](../layer0/) (hazard definition) + [`../m0_input_data/`](../m0_input_data/) (M0:
ASCE RP surface + SPC record + asset geometry) + [`../m1_catalog/`](../m1_catalog/) (M1: λ + severity, per
sub-peril). *This* folder is where **coupling, damage, and loss specialize to a wind farm**.

> **Why an asset cell?** The catalog (what the atmosphere does over a region) is asset-independent; the **coupling,
> fragility, and loss** are asset-specific. A solar farm and a wind farm under the *same* tornado/strong-wind
> catalog couple and break differently. So M2–M4 live under the asset — `wind_farm/` now; a sibling `solar/` cell
> can be added later under `convective_wind/` without touching the shared catalog (P1 — *hazard × asset specificity*).

**Assets (two wind farms):** **Traverse Wind Energy Center, OK** (~999 MW · **TIV ≈ $1.40B** · proving / high-wind) ·
**Shepherds Flat, OR** (~845 MW · **TIV ≈ $1.18B** · baseline / low-wind).

## The fork — where, and why
Convective wind is **one peril, two sub-perils** ([DD-WN-1](../../../docs/plans/convective_wind/decisions.md)). They
diverge at different layers:

| Layer | Forked? | Why |
|---|---|---|
| layer0 · M0 · M1 (peril) | **shared** | one atmosphere, one catalog over the region |
| **M2 coupling** | **folder-fork** → [`tornado/`](m2_coupling/tornado/) (areal hit-or-miss, path-aware Minkowski) · [`strong_wind/`](m2_coupling/strong_wind/) (site-conditioned) | the *coupling machinery* genuinely differs (two footprints, two spatial logics) |
| **M3 damage** | **shared, two curves** (logical fork — [DD-WN-16](../../../docs/plans/convective_wind/decisions.md)) | one turbine, but tornado is *more damaging at the same gust* than strong wind ([AWN-32](../../../docs/plans/convective_wind/assumptions.md)) |
| **M4 loss** | **shared, combined** | each stream sampled through its own curve → **one** annual-loss distribution per site |

## The layers
- **M2 — coupling** · [📖 folder README](m2_coupling/README.md) — `λ_collection → λ_asset`: tornado via path-aware
  Minkowski (`p_hit`, Poisson thinning) + EF|strike + swept fraction; strong wind reads its local ASCE RP gust
  (whole farm exposed, no areal miss).
- **M3 — damage** · [📖 folder README](m3_damage/README.md) — one anchored subsystem-logistic turbine object, **two
  sub-peril curves**: tornado (all subsystems, low onset, steeper, DR→1) vs strong wind (aero only, onset at IEC
  survival, DR≤0.65). `DR(μ)≈0` both. Approximate (the dominant uncertainty; AWN-26).
- **M4 — loss & metrics** · [📖 folder README](m4_loss_metrics/README.md) — one compound-Poisson/NegBin Monte
  Carlo (300k yr); EAL/VaR/PML/TVaR off the **joint** sampled distribution, **% of TIV alongside $**; EAL additive
  across sub-perils, the tail off the joint (never Method 0).

## Headline numbers (real, record-limited, approximate)
| | EAL | PML250 | TVaR99 | tail driver |
|---|---|---|---|---|
| **Traverse** (proving) | 0.064% ($0.89M) | **3.99%** | **4.88%** | tornado |
| **Shepherds Flat** (baseline) | 0.006% ($0.07M) | 0.15% | 0.35% | ~none (correctly small) |

- **Strong wind ≈ 0** on the *damage* track (EAL ~0.006–0.02% of TIV) — gusts stay below IEC survival; its material
  impact (curtailment + fatigue) is the **deferred disruption/degradation track** ([AWN-31](../../../docs/plans/convective_wind/assumptions.md)).
- **Tornado is the catastrophic tail** at Traverse (PML/TVaR ≫ EAL); negligible at Shepherds — the low-vs-high
  payoff on one unchanged engine.

## Deferred (asset-specific)
A sibling `solar/` asset cell under `convective_wind/` · calibrated turbine curves (`infrasure-damage-curves`) ·
the disruption/degradation track (AWN-31) · per-turbine vs whole-farm exposure grain refinements · portfolio
correlation across farms (AWN-22). Plan-of-record: [`docs/plans/convective_wind/`](../../../docs/plans/convective_wind/README.md).
