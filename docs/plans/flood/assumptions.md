# Flood pipeline — assumptions register

Every input, curve, and simplification the flood build rests on, by layer — so each is visible, challengeable, and
revisable. Prefix `AFL-*`. Grows as we plan and build.

> **Status: V1 built (M0→M4).** The assumptions below are **realized** in the pipeline (treat "proposed" rows as
> *applied in V1*). High site = **Elizabeth Solar** (not Bayou Galion — the screen's SFHA pick, swapped for real
> geometry + deeper BLE flood; see JD-FL-3). Newest M2–M4 assumptions appended at the bottom.

| ID | Layer | Assumption | Source / decision | Status | Revisit trigger |
|---|---|---|---|---|---|
| AFL-1 | scope | V1 = inland **riverine + pluvial** only; **coastal surge deferred** | [JD-FL-1](decisions.md) | proposed | hurricane/surge bucket built |
| AFL-2 | scope | **Physical loss only** — business-interruption (BI) excluded | [JD-FL-1](decisions.md); team hazard-tier scope | proposed | BI tier opens |
| AFL-3 | M2 | Flood couples as **site-conditioned** (bucket 3), depth field met against equipment height | [Notebooks matrix](../../../Notebooks/README.md); wildfire M2 analogue | proposed | a footprint/areal basis proves better |
| AFL-4 | M2 | **Micro-elevation (DEM) is load-bearing** — asset height vs flood surface drives the coupling | flood physics | proposed | DEM resolution too coarse vs asset scale |
| AFL-5 | M0 | Input data is **self-serve public** (FEMA NFHL, RP depth grids, USGS gauges, 3DEP DEM) — no private feed | [00_intent](00_intent.md) | proposed | a needed product turns out gated |
| AFL-6 | M1 | Depth source = **national StreamStats+OWP-HAND pipeline, FEMA-BLE-preferred**; for **the high site (Elizabeth), BLE is used** — 100-yr + 500-yr depth + 10-yr extent | [JD-FL-6](decisions.md)/[JD-FL-7](decisions.md) | **built** | hi-res national depth grid / full BLE coverage → sample-grid primary |
| AFL-12 | M1 | **BLE gives only 1% (100-yr) + 0.2% (500-yr) depth** (+10% extent); **lower RPs (10/25/50-yr) densified** via regression flow-frequency + a BLE-anchored rating (JD-FL-8) | [JD-FL-6](decisions.md)/[JD-FL-8](decisions.md); [research](../../../jdocs/flood_research_result.md) | **built** | full multi-RP grid / live HAND-SRC sourced |
| AFL-13 | M1 | Datum reconciled via **NOAA VDatum**; **regulation/levees + climate non-stationarity** carried as explicit overlays, not embedded | [JD-FL-6](decisions.md) | decided | a regulated/leveed reach or forward-looking climate run requires it |
| AFL-7 | M2 | Coupling = **`depth_at_asset = water_surface_elevation − ground_elevation(asset_DEM)`**; per-sub-cluster susceptibility | A21 §2.3 | proposed | DEM resolution too coarse vs pad spacing |
| AFL-8 | M3 | Depth-damage = **canonical `infrasure-damage-curves` RIVERINE_FLOOD × solar** (capex-weighted, anchored; `x0` encodes component elevation) — *supersedes* the earlier "no solar curve exists / USACE proxy" assumption | infrasure-damage-curves; M3 build | **built** | curve library updates; calibrate to claims data |
| AFL-9 | M4 | Flood loss must **bridge RP depth grids → the shared compound-Poisson MC** (vs an RP+AAL track) — **unresolved** | open ([decisions.md](decisions.md)) | open | settled before M4 build |
| AFL-10 | M0 | Sites = **Hayhurst (low, reused)** + a **national-EIA flood-screen high site** (Lower-Mississippi riverine); national `powerplants_enriched_v2`, not the in-repo AIG portfolio | [JD-FL-3](decisions.md) | proposed | top screen asset lacks grid/DEM coverage → next candidate / pivot region |
| AFL-11 | M1 | Catalog built as a **sub-peril family** (`sub_peril` key) with a **reserved `event_family_id`** — even though V1 ships riverine(+pluvial) only | [JD-FL-4](decisions.md) | proposed | pluvial/coastal added → confirm keys sufficient |
| AFL-14 | M2/M3 | **`value ∝ area`** — areal inundated fraction proxies the fraction of asset *value* exposed (subsystems assumed spread uniformly over the footprint) | M2 build | **built** | site-specific subsystem layout (esp. inverter location) sourced |
| AFL-15 | M3 | **PV variant = single-axis horizontal stow** (x0 2.5 ft); flood-stow (x0 7 ft) is a deferred mitigation lever | M3 build | **built** | tracker flood-stow capability confirmed per site |
| AFL-16 | M4 | **TIV** from $/MW (Hayhurst hail basis $1.483 M/MW); **Elizabeth estimated** by capacity | M4 build | **built** | registry/insured TIV obtained |
| AFL-17 | M4 | Event model = **annual-maximum** (~1 damaging flood/yr), MC sampling the BLE loss-exceedance curve | [JD-FL-7](decisions.md) | **built** | multi-event-per-year evidence; lower-RP densification |
| AFL-18 | M4 | ~~10-yr onset = assumed shallow depth (0.5 ft)~~ **superseded by JD-FL-8**: 10/25/50-yr depths are now regression-rating, BLE-anchored; EAL 0.13%→**0.155%** (+18%), robust to channel slope | [JD-FL-8](decisions.md) | **built** | regression-Q standard error propagated as MC overlay |
| AFL-19 | M3/M4 | **Duration / business-interruption unmodeled** (Gen-1) — physical loss only | A25; team scope | open | BI tier opens |

### Pluvial sub-peril — `AFL-P*`

| ID | Layer | Assumption | Source / decision | Status | Revisit trigger |
|---|---|---|---|---|---|
| AFL-P1 | M1 | Pluvial depth = **NOAA Atlas 14 24-hr rainfall → SCS Curve Number runoff** (CN≈80, graded solar / soil-C) → sheet ponding; **no free pluvial depth product exists** (the blind-spot) | [JD-FL-9](decisions.md); Flood-Data-Ref §2/§5/§7 | **built** | Atlas 15 (climate-aware, ~Sept 2026); FFRD national / commercial pluvial grid |
| AFL-P2 | M1 | Ponding = **sheet model** — footprint-avg = `r·Q` (retention **r=0.5**), wet depth = `r·Q/f` over **ponding fraction f=0.4** (low-lying share of the graded pad). **Both r and f are judgment knobs (no anchor)**; DEM-hypsometry rejected (10 m σ = site slope, not micro-relief → absurd deep pools) | [JD-FL-9](decisions.md); M1 build | **built** | 1 m lidar depression analysis for `f`; 2-D overland run for depth; pluvial depth anchor |
| AFL-P3 | M4 | **Combine = co-sample comonotonic + worse-source-wins** (headline, φ=1); **additive-capped = recorded upper envelope** (φ=0). Headline is **pluvial-dominated** here (driven by `f`) → riverine masked; marginals reported | [JD-FL-11](decisions.md); [research](../../../jdocs/flood_subperil_research_result.md) | **built** | sub-asset spatial exposure → true per-location max-then-sum; riverine↔pluvial copula |

### Wind-farm cell (V2) — `AFL-W*`

| ID | Layer | Assumption | Source / decision | Status | Revisit trigger |
|---|---|---|---|---|---|
| AFL-W1 | M0 | Two wind sites: **Shepherds Flat OR** (baseline, reused from convective_wind) + **Green River IL** (high, screened) | [JD-FL-W1](decisions.md)/[W3](decisions.md) | **built** | a BLE-covered high-flood wind farm appears |
| AFL-W2 | M0–M4 | Flood exposure is **per-node** (turbines + substation), **not areal** — wind turbines sit on high ground (TX fleet: 0/2,976 wet) | [JD-FL-W2](decisions.md) | **built** | turbine siting standards change / floating turbines |
| AFL-W3 | M0 | **TIV from $/kW** (land-based wind ~$1,400/kW; AWN-14 basis); % of TIV alongside $ | [JD-FL-W1](decisions.md) | **built** | registry/insured TIV obtained |
| AFL-W4 | M0 | Boundary = **USWTDB convex hull** (~250 m buffer) for the high site (`renewablesinfo_org` boundary-DB symlink absent); cached polygon for the baseline | [JD-FL-W1](decisions.md) | **built** | symlink returns / OSM plant polygon found |
| AFL-W5 | M0/M3 | **Substation** at the **farm-centroid** node (true location unknown); it **dominates** the loss once flooded → the headline rests on this; turbines-only is the robust floor | [JD-FL-W1](decisions.md) | **built** | real substation GIS sourced |
| AFL-W6 | M1 | **Pad elevations** above grade: turbine 0.30 m, substation 0.15 m | M1 build | **built** | per-site foundation/pad survey |
| AFL-W7 | M1 | **500-yr = 1% water surface + ΔWSE 0.6 m** freeboard (no mapped 0.2% band in this Zone A area) | [JD-FL-W4](decisions.md) | **built** | detailed/StreamStats study gives a real 0.2% surface |
| AFL-W8 | M3 | **Greenfield flood × wind curve** — rotor/nacelle/tower flood-immune (0.63); base vulnerable (~0.37); shapes borrowed from flood×solar + foundation by judgment | [JD-FL-W4](decisions.md); M3 build | **built** | `infrasure-damage-curves` adds a flood × wind curve |

*Resolved since seeding: depth product = FEMA BLE (AFL-6); TIV basis = AFL-16; depth units = metres above ground (BLE ft × 0.3048). Wind cell (V2): depth = extent-based bathtub off 3DEP (AFL-W7 / JD-FL-W4), greenfield curve (AFL-W8).*
