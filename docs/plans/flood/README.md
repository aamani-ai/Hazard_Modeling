# Plan: Flood Pipeline

> **Status: flood × solar AND flood × wind built end-to-end (M0→M4) ✅.** **Solar** — Elizabeth Solar (LA, high) +
> Hayhurst (TX, dry), now **riverine + pluvial**: FEMA BLE depth (riverine, +JD-FL-8 regression densification of lower
> RPs) **and** NOAA Atlas 14 → SCS-CN sheet-ponding (pluvial, screening-grade) → site-conditioned coupling →
> `infrasure-damage-curves` depth-damage → annual-max MC, sub-perils **co-sampled + worse-source-wins** (JD-FL-11) →
> **combined EAL 0.27% (envelope 0.27–0.42) / PML500 7.9% TIV** (headline pluvial-dominated; riverine-only EAL 0.155%). **Wind (V2,
> [m_wind_farm.md](m_wind_farm.md))** — **Green River IL** (~60% turbines in SFHA) + Shepherds Flat (mapped-dry):
> per-turbine **extent-based bathtub** depth (Zone A, no BFE/BLE) → per-node coupling → **greenfield** flood×wind
> curve → annual-max MC → **EAL 0.45% / PML500 13% TIV** (substation-concentrated). Two wind findings: **TX wind is
> flood-immune** (0/2,976 turbines wet) and **wind flood is capped per-turbine**. Every layer known-answer-checked.
> Decisions: [`decisions.md`](decisions.md) (JD-FL-1…8, JD-FL-W1…4). **Next:** a production folder architecture.

Same approach as hail, wildfire, and wind: take **one peril** and build the whole pipeline **end-to-end in
notebooks**, step by step, each cell legible (description → code → output → plots → tables), every basic verified
against a known answer. The notebooks will live in [`../../../Notebooks/flood/`](../../../Notebooks/flood) (shared
`m0`/`m1`, then `solar/` for `m2–m4`; `wind/` added in V2).

## The two sides (owner's framing, mirrored from hail/wildfire/wind)

1. **Input data (M0).** Meet and *understand* the raw flood hazard evidence — FEMA NFHL flood zones, return-period
   depth grids (FEMA / FATHOM / First Street), USGS peak-flow gauge records, and a public DEM (3DEP) for the asset
   elevation — before any modeling. **Self-serve public data; no private feed required.**
2. **The model (M1 → M4).** Flood-frequency catalog → **site-conditioned** coupling (depth field × equipment height,
   DEM-modulated) → depth-damage curve → loss distribution & metrics — on the **shared compound-Poisson/NegBin
   Monte-Carlo engine** (reused unchanged from hail/wildfire/wind).

## Planned phase breakdown (V1 — solar)

| Phase | M-step | What we build | Notebook(s) | Status |
|------:|--------|---------------|-------------|--------|
| 1. Input data | M0 (raw evidence) | Meet the flood evidence for two solar sites: FEMA NFHL zones, RP depth grids, USGS gauges, 3DEP DEM. Field-dictionary every layer (value · meaning · datum · units). Decide riverine + pluvial scope. | `m0_input_data/01_site_screen_and_geometry` ✅ · `02_depth_grids_and_dem` ✅ | **01 + 02 built** (public data: screen + geometry/BLE refinement → **Elizabeth Solar LA** high site, **real OSM polygons** both sites; DEM + FEMA zone-map. [m0 plan](m0_input_data.md)) |
| 2. Catalog ✅ | M0 → M1 | **Sub-peril fork** (JD-FL-10): **riverine** = FEMA BLE 100/500-yr depth + 10-yr extent over the real polygon, **+ JD-FL-8 regression densification** (NLDI→NSS→rating) of the 10/25/50-yr depths; **pluvial** = NOAA Atlas 14 → SCS-CN → sheet ponding (JD-FL-9, screening-grade). | `m1_catalog/riverine/01_catalog` ✅ · `m1_catalog/pluvial/01_catalog` ✅ | **built** ([m1 plan](m1_catalog.md)) |
| 3. Solar coupling ✅ | M1 → M2 | **Site-conditioned** (bucket 3), thin (BLE pre-coupled depth in M1). Emits the contract M3 reads: `exposure_fraction` × `conditional_depth` per RP; height-conditioning deferred to M3. No Minkowski. | `solar/m2_coupling/01_coupling` ✅ | **built** ([m2 plan](m2_coupling.md)) |
| 4. Solar damage ✅ | M2 → M3 | **Depth-damage** = canonical **`infrasure-damage-curves` RIVERINE_FLOOD × solar** (the library all perils use), capex-weighted + anchored; `x0` encodes the height inversion (inverter drowns @ 0.75 ft, panels survive). `conditional_loss = exposure × Asset_DR × TIV`. Elizabeth 4.4% TIV @ 500-yr. | `solar/m3_damage/01_damage` ✅ | **built** ([m3 plan](m3_damage.md)) |
| 5. Solar loss & metrics ✅ | M3 → M4 | **Annual-maximum MC** → EAL / VaR / PML / TVaR, **% of TIV**. Sub-perils **co-sampled comonotonic + worse-source-wins** (JD-FL-11, research-backed) → one combined headline + recorded additive-capped envelope; marginals kept. **Elizabeth combined EAL 0.27% (env 0.27–0.42) / PML500 7.9% TIV** (pluvial-dominated). External-validated vs USGS high-water marks (§4b). | `solar/m4_loss_metrics/01_loss_metrics` ✅ | **built** ([m4 plan](m4_loss_metrics.md)) |
| 6. Wind cell (V2) ✅ | M0–M4 | **Built end-to-end.** High **Green River IL** (~60% turbines in SFHA) + baseline **Shepherds Flat** (mapped-dry). Two findings: **TX wind is flood-immune** (0/2,976 turbines wet → high site pivots to Midwest river-valley wind) and **wind flood is capped per-turbine but substation-concentrated**. Depth = extent-based bathtub off 3DEP (Zone A, no BFE/BLE); M3 = **greenfield** flood×wind curve. **Green River EAL 0.45% / PML500 13% TIV.** | `wind_farm/…` ([plan](m_wind_farm.md)) | **built** (JD-FL-W1…4) |

## Settled framing (seeded by the A-series — see [`decisions.md`](decisions.md) + [`01_references.md`](01_references.md))

The competitive-research **A-series pre-defines flood's spine**, so most calls are proposed-decided, not open:
- **JD-FL-1** — flood is a **sub-peril family** (Riverine `[R]` / Pluvial `[F]` / Coastal `[C]`, A12); **V1 = R + F**
  physical damage to solar; **coastal deferred + hurricane-cross-linked**, physical loss only.
- **JD-FL-2 → JD-FL-5 → JD-FL-6** — M1 depth source, settled after a scaling review + deep research: the **national
  pipeline** — **StreamStats** (discharge-at-RP) + **NOAA OWP HAND** (→ depth), **FEMA-BLE-preferred where it exists**;
  single-gauge Bulletin 17C demoted to validation only (doesn't scale to all-US). **BLE is available for the high site**
  (1% + 0.2% depth/WSE) → used as the M1 source for this site. Research: [`jdocs/flood_research_result.md`](../../../jdocs/flood_research_result.md).
- **JD-FL-3** — sites = **Hayhurst (low, reused) + a national-EIA flood-screen high site** (Lower-Mississippi riverine).
- **JD-FL-4** — M1 built as a **sub-peril family** + a reserved **`event_family_id`** — the two cheap hooks that keep
  adding pluvial/coastal later a one-row change, not a refactor.
- **Coupling** = **site-conditioned** + DEM elevation-offset (A21 §2.3); **damage** = tabular **USACE** + per-asset
  offset (A22), solar-specific curve deferred.

- **JD-FL-5 → JD-FL-6** — depth source flips to the national **StreamStats+HAND**, **FEMA-BLE-preferred** (BLE used here).
- **JD-FL-7** — **event-model bridge settled:** annual-maximum MC sampling the BLE loss-exceedance curve → shared
  metric frame (DD-4). The 10-yr onset = **real BLE exposure × explicit, sensitivity-tested depth**.

*All M1 decisions are now settled — see [`decisions.md`](decisions.md) (JD-FL-1…7).*

## Files

- [`00_intent.md`](00_intent.md) — the seed: goal, the honest V1 label, the asset, the deferred wind cell, open questions.
- [`01_references.md`](01_references.md) — bucketed, reasoned reference inputs (A-series spine · old-model fetcher · First Street/HAZUS benchmarks).
- [`decisions.md`](decisions.md) — ADR-style decision log (`JD-FL-*`).
- [`assumptions.md`](assumptions.md) — the assumptions register (`AFL-*`), by layer.
- `m0_input_data.md` · `m1_catalog.md` · `m2_coupling.md` · `m3_damage.md` · `m4_loss_metrics.md` — per-layer plans (written as we reach each phase).
