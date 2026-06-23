# Plan: Hurricane / Tropical-Cyclone Pipeline

> **✅ V1 BUILT END-TO-END (M0→M4), hurricane wind × solar.** Four solar sites: Everglades Solar (FL, high) +
> Hayhurst (TX, true-zero) + Discovery Solar Center (FL) & LA3 West Baton Rouge (LA) (flood-coastal cross-link riders).
> RAFT storm catalog → Holland field (tail **ASCE-validated** within 5.5%; 90 kt == observed) → field-intensity
> coupling (degenerate on solar, demonstrated) → provisional library damage curve → storm-resolved MC →
> **EAL 2.2% / PML500 41% of TIV** (point on the provisional `tracker_stow` curve; harsher-curve sensitivity 4.1%/66%; Hayhurst 0). `event_family_id`
> stamped for the coastal/pluvial-TC cross-link. **Hazard side independently validated; loss side curve-limited
> (provisional curve flagged for replacement + a Hazus/NRI loss benchmark).** Decisions: [`decisions.md`](decisions.md)
> (JD-TC-1…8). The **wind-farm cell is also built** (per-turbine field-intensity at Amazon Wind Farm US East).
> **Next:** swap the provisional damage curve + loss benchmark.

---

> **Original seed status (kept for context): route-zero (scope + decisions).** The **fourth peril**. Builds the repo's last
> unbuilt coupling type — **field-intensity** (a continuous wind field sampled at the asset) — and lays the
> **storm-resolved catalog** that founds coastal flood. V1 = **hurricane WIND → solar PV**, wind-only, on a
> **shared RAFT TC catalog** (Holland field, validated vs IBTrACS/HURDAT2); **surge & rain stay flood's** (`[C]`/`[F]`),
> reached via the now-active `event_family_id` (flood coastal built). Decisions: [`decisions.md`](decisions.md) (`JD-TC-1..8`).
> Assumptions: [`assumptions.md`](assumptions.md) (`ATC-*`). Base reference:
> [`jdocs/Hazard_Data_Reference-TC_Hurricane.md`](../../../jdocs/Hazard_Data_Reference-TC_Hurricane.md). **Next:**
> detailed per-layer M0→M4 plans, then build.

Same approach as hail, wildfire, convective wind, and flood: take **one peril** and build the whole pipeline
**end-to-end in notebooks**, step by step, each cell legible (description → code → output → plots → tables), every
basic verified against a known answer. Notebooks will live in [`../../../Notebooks/hurricane/`](../../../Notebooks)
(shared `layer0`/`m0`/`m1`, then `solar/` for `m2–m4`; `wind_farm/` **built** — Amazon Wind Farm US East).

## Start here

- **[`00_intent.md`](00_intent.md)** — the seed: why hurricane (4th), the honest V1 scope label, the old-model
  counter-example (the live surge double-count).
- **[`00_hazard_definition.md`](00_hazard_definition.md)** — **layer-0**: the 3-s-gust observable, the storm event,
  the Holland field, the **field-intensity** coupling, and the **primary→secondary cross-link** (wind ours; surge/rain
  flood's).
- **[`decisions.md`](decisions.md)** — `JD-TC-*` (asset/order, coupling honesty, **RAFT catalog**, scope+cross-link,
  sites, the pluvial-hybrid consequence, the Holland footprint method).

## The two architectural dividends

1. **Completes the coupling taxonomy** — field-intensity is the third/last bucket (areal · field-intensity ·
   site-conditioned). Built degenerate on solar V1, fully proven at the wind-farm cell (**built**, Amazon Wind Farm US East).
2. **Founds coastal flood (+ compound flooding)** — the shared, storm-resolved **RAFT** catalog + `event_family_id`
   let one storm's wind + surge + rain combine without double-counting. Unlocked flood's coastal `[C]` (**built**)
   and the TC slice of pluvial `[F]`. See [flood JD-FL-1/4/11](../flood/decisions.md).

## The honest V1 label

> Hurricane V1 models **TC wind → structural damage → solar PV**, on a **storm-resolved RAFT catalog**, producing
> EAL/VaR/PML/TVaR (% of TIV + $). **Wind only.** Surge/rain are flood's (`event_family_id` active — flood coastal built). Wind farm = built (V2 cell). Resource
> wind = Performance tier. Field-intensity coupling is **spatially degenerate on solar** (centroid sample) — V1 does
> **not** claim to have proven it; the wind-farm cell (**built**) does.

## The settled decisions (seed)

| # | Decision | Choice | Why (one line) |
|---|---|---|---|
| [JD-TC-1](decisions.md) | Asset & order | **Solar V1, wind farm V2** | catalog (M0/M1) is shared; solar = coherence + fast number; V2 proves the coupling |
| [JD-TC-2](decisions.md) | Coupling honesty | **Field-intensity, degenerate on solar** | ~1 km polygon at storm scale ≈ one sample; full proof = V2 |
| [JD-TC-3](decisions.md) | Catalog method | **Storm-resolved RAFT tracks → Holland** | RP grid has no storm objects → can't found coastal; RAFT = one catalog for wind+surge+rain |
| [JD-TC-4](decisions.md) | Scope | **Wind only; surge/rain = flood's, hooked** | one owner, one model, one storm identity → no double-count |
| [JD-TC-5](decisions.md) | Sites | **Coastal solar (screened) + Hayhurst** | coastal high = field + surge proving ground; Hayhurst = coherent control |
| [JD-TC-6](decisions.md) | Pluvial consequence | **Atlas 14 + RAFT hybrid (later)** | RAFT enters once, shared; else two disconnected storm universes |
| [JD-TC-7](decisions.md) | Footprint method | **Holland (1980), validated vs IBTrACS/HURDAT2** | the standard open per-event field; STORM RP grid cross-check |
| [JD-TC-8](decisions.md) | Frequency basis | **Observed-anchored λ (HURDAT2 close-passages ÷ record years)** | distinct hurricanes ≥64 kt within 100 km; corrects RAFT's genesis oversample — RAFT supplies severity shape only |

## The M0→M4 sketch

| Layer | What it builds | Key sources / methods | Notebook(s) (planned) |
|------:|----------------|------------------------|------------------------|
| **layer-0** | The authored hazard definition (3-s gust · storm event · Holland field · field-intensity coupling · cross-link) | standards + Hazard Data Ref §1/§5/§8 | `layer0/01_hazard_definition` |
| **M0** | Meet the evidence: RAFT tracks, IBTrACS/HURDAT2 landfall record, STORM RP grid (cross-check), the four solar sites' geometry & TIV | RAFT NetCDF · IBTrACS (NCEI) · HURDAT2 (NHC) · STORM GeoTIFF (Zenodo) · OSM/EIA geometry | `m0_input_data/01_raft_catalog` · `02_landfall_record` · `03_site_geometry` |
| **M1** | **The catalog (the peril, shared):** RAFT tracks → **Holland field** → per-site **storm-resolved** 3-s-gust catalog; **observed-anchored frequency** (HURDAT2 close-passages ÷ record years, JD-TC-8 — RAFT supplies severity only); **`event_family_id` stamped**; validated vs landfall winds + ASCE 7-22 tail | Holland (1980) · gust factor · knots→mph ×1.150779 | `m1_catalog/01_event_catalog` · `02_tail_validation` |
| **M2** | **Coupling — field-intensity** (sample the field at the asset). **Solar = degenerate** (centroid sample), labeled | A21 field-intensity dispatch | `solar/m2_coupling/01_coupling` |
| **M3** | **Damage** — `infrasure-damage-curves` **hurricane-wind × solar** (3-s-gust basis), capex-weighted | infrasure-damage-curves | `solar/m3_damage/01_damage` |
| **M4** | **Loss & metrics** — storm-resolved MC over the RAFT catalog → **EAL/VaR/PML/TVaR, % of TIV + $**, shared engine | shared compound-Poisson/MC engine | `solar/m4_loss_metrics/01_loss_metrics` |

**Validation discipline (every layer):** known-answer checks; Holland field vs observed landfall gusts; catalog RP
vs STORM grid; EAL/PML sanity vs FEMA Hazus / NRI hurricane benchmarks where available.

## Data sources — confirmed reachable (probed 2026-06-19)

| Source | Role | Status |
|---|---|---|
| **IBTrACS** (NCEI CSV) | observed landfall validation | ✅ `200` |
| **HURDAT2** (NHC txt) | Atlantic best-track validation | ✅ `200` |
| **STORM 10 km wind-RP GeoTIFFs** (Zenodo 10931452) | RP cross-check | ✅ `200` |
| **NOAA National Storm Surge (SLOSH MOM)** | future coastal `[C]` (flood-side) | ✅ `200` |
| **RAFT** (Zenodo `10.5281/zenodo.10392723`) | **the V1 catalog spine** | ✅ `200` — tracks `RAFT.NA.v20231016.nc` **154 MB**, streams (range `206`), CC-BY-4.0 |
| **STORM tracks** (4TU DOI 12705164) | not needed for V1 (N. Atlantic = RAFT) | ⚠️ `404` — resolve current DOI only if a non-Atlantic basin is ever needed |

## What's NOT here (and where it lives)

- **Storm surge / TC rainfall** → flood's `[C]`/`[F]`; reached via `event_family_id` (coastal **built**, link active).
- **Wind farm** → hurricane wind-farm cell (**built**, Amazon Wind Farm US East; reuses M1 + convective wind's 3-s-gust turbine curve + turbine geometry).
- **Wind resource (generation)** → Performance tier (`model-gpr`).
- **Per-layer detailed plans** (`m0_input_data.md` … `m4_loss_metrics.md`) → written next, before building.
