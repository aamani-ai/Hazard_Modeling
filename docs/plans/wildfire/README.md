# Plan: Wildfire Pipeline

> **Status: M0–M4 wildfire × solar complete — wind cell next.** **M0** (input data), **M1** (catalog), **M2**
> (thin site-conditioned coupling), **M3** (anchored BoS damage curve), and **M4** (loss & metrics) are built
> end-to-end for two assets (Hayhurst low-fire baseline + Matrix high-fire proving). M0 = both public products
> (WRC 2.0 + FSim FLP1-6) with real boundaries + a cross-candidate comparison + a Hydronos validation; M1 = the
> per-asset hazard profile (λ from BP, FLP→kW/m severity, the engine-contract manifest, DD-W7); M2 = the thin
> site-conditioned coupling; M3 = the anchored BoS-weighted kW/m damage curve (conditional loss|fire ≈ 1.0%
> Hayhurst / 6.5% Matrix; approximate, accurate later — DD-W8); M4 = the shared compound-Poisson MC →
> **EAL 0.0004% TIV (Hayhurst, negligible) vs 0.29% TIV + a material 14% PML250 (Matrix)** — the low-vs-high
> contrast paying off on one unchanged engine. Next: the **wind cell** (`wildfire/wind/` M2–M4 on the shared
> M0/M1). Scope/data doctrine settled in
> [`../../extra/discussion/wildfire/`](../../extra/discussion/wildfire/README.md).

Hazard **2 of 3** (hail ✅ · **wildfire** · wind). Same approach as hail: take **one peril** and build the
whole pipeline **end-to-end in notebooks**, step by step, each cell legible (description → code → output →
plots → tables), every basic verified against a known answer. The notebooks will live in
[`../../../Notebooks/wildfire/`](../../../Notebooks/wildfire) (shared `m0`/`m1`, then `solar/` for `m2–m4`).

## The two sides (owner's framing, mirrored from hail)

1. **Input data (M0).** Meet and *understand* the raw wildfire hazard data — two public USFS products (WRC
   2.0 and native FSim) — before any modeling. Sourced directly from public rasters; **no Hydronos / no
   secret** ([DD-W3](decisions.md)).
2. **The model (M1 → M4).** Catalog → site-conditioned coupling → BoS-weighted damage → loss distribution &
   metrics — grounded in the data dictionary, the A-series architecture, and the `hazard_math` notes, on the
   **shared compound-NegBin Monte-Carlo engine** (reused unchanged from hail).

## Planned phase breakdown

| Phase | M-step | What we build | Notebook(s) | Status |
|------:|--------|---------------|-------------|--------|
| **1. Input data** ✅ | M0 (raw evidence) | Understood both public products (WRC 2.0 30 m + FSim native FLP1-6 270 m), real site boundaries, site-scale maps, and **compared** them: BP agrees; intensity diverges by regime (→ commit FSim FLP1-6, DD-W4). Direct raster fetch, no Hydronos. | `m0_input_data/01_wrc_geoplatform`, `02_fsim_rds` | **built** ([m0 plan](m0_input_data.md)) |
| 2. Catalog ✅ | M0 → M1 | **Per-asset hazard profile**: λ from BP (no short-record fit — FSim pre-integrated; DD-W7) + conditional severity (FLP1-6 → kW/m); engine-contract manifest; AW-21 edge-rule check done. *Structurally unlike hail's regional event catalog.* | `m1_catalog/01_catalog` | **built** ([m1 plan](m1_catalog.md)) |
| 3. Solar coupling ✅ | M1 → M2 | **Site-conditioned** (bucket 3) — *not* hail's Minkowski. A **deliberately thin** layer (M1 already coupled): oozing-confirm + whole-site exposure + embedded `d=10m` susceptibility → emits `(λ, conditional kW/m severity, exposure)`. Why-thin + deferrals documented. | `solar/m2_coupling/01_coupling` | **built** ([m2 plan](m2_coupling.md)) |
| 4. Solar damage ✅ | M2 → M3 | **BoS-weighted, anchored** logistic MDR on kW/m (canonical `infrasure-damage-curves`; DD-W8). Conditional loss\|fire ≈ **1.0% (Hayhurst) / 6.5% (Matrix)** of TIV. Approximate curve — accurate later. | `solar/m3_damage/01_damage` | **built** ([m3 plan](m3_damage.md)) |
| 5. Solar loss & metrics ✅ | M3 → M4 | The **shared compound-Poisson MC**, engine untouched (only per-year sampling swapped) — EAL/VaR/PML/TVaR off the *sampled* distribution, % of TIV. **EAL 0.0004% (Hayhurst) vs 0.29% TIV + 14% PML250 (Matrix)**; Method-0 tail-collapse re-demonstrated. | `solar/m4_loss_metrics/01_loss_metrics` | **built** ([m4 plan](m4_loss_metrics.md)) |
| 6. Wind cell | M2–M4 | `wind/` on the shared M0/M1 — per-turbine point-cloud + hub-height attenuation + shared-event correlation. | `wind/…` | not started |

## Settled framing (from the discussion → see [`decisions.md`](decisions.md))

- **DD-W1** V1 = **exogenous geographic wildfire only, honestly labeled**; equipment-driven brushfire (+ BESS
  thermal runaway, smoke-soiling, PSPS) named as **distinct deferred perils**.
- **DD-W2** Coupling = **site-conditioned** (bucket 3), same row for solar & wind.
- **DD-W3** Data = **public USFS rasters, direct; no Hydronos, no secret**.
- **DD-W4** Severity histogram = **native FSim FLP1-6** (270 m), not the lossy WRC FLEP reconstruction.
- **DD-W5** Spatial grain = **asset-boundary zonal sampling** (capacity-radius fallback), not a 0.25° cell.
- **DD-W6** V1 site-conditioning = defensible **proxy** (boundary BP + LANDFIRE fuel + fixed `d`=10 m + wind
  hub-height); **imagery deferred to V1.5+**.

## Files

- [`00_intent.md`](00_intent.md) — the seed: goal, the two sides, scope, domain principles, open questions.
- [`decisions.md`](decisions.md) — ADR-style decision log (`DD-W*`).
- [`assumptions.md`](assumptions.md) — the assumptions register (`AW-*`), by layer.
- [`m0_input_data.md`](m0_input_data.md) — **the active M0 plan** (the two candidate-exploration notebooks).
- Source-of-truth understanding lives in the discussion docs: [scope/framing `01`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md) · [data dictionary `02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md).
