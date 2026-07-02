# 01 — References (raw inputs, reasoned — not blueprints)

*Per the workflow rule: a reference says "this is possible"; our architecture says "this is what we build,
adapted to us." Each entry: **what it is · what we take · what we adapt or reject.** Grows as we research.*

> Unlike hail (built before these folders were wired in), flood opens with **two strong reference sets already in
> the repo** — the competitive-research **A-series** (which *pre-defines* flood's taxonomy, catalog, coupling, and
> damage form) and the **old hazard model** (a flood *fetcher*, anti-pattern for loss). So flood's definition is
> **largely inherited** (like wildfire from FSim), not authored (like wind). This file curates them.

---

## Bucket A — Architecture / definition (the spine) — `infrasure-hazard-competitive-research-main/learnings/architecture/`

> **Posture:** these are the **option-space + scope spine** — we take the taxonomy and the committed method
> choices, and reason where they leave gaps (esp. the event-model bridge to our shared MC engine).

| Source | What it is | What we take / adapt |
|--------|-----------|----------------------|
| **A12 — peril taxonomy spine** (§2, §6.1) | Flood = **three distinct sub-peril rows**: Riverine `[R]`, Pluvial `[F]`, Coastal `[C]`; the dual-test split (distinct footprint + distinct data); coastal **cross-linked to hurricane** via `event_family_id` | **Take:** flood-as-sub-peril-family framing; **R + F + C all built** (C joined to hurricane on `event_family_id`, JD-FL-12 — not excluded). Sets [JD-FL-1](decisions.md). |
| **A20 — M0↔M1 hazard catalog** (§2.5, §3.3, §6.8, §7) | Flood frequency = **hydrodynamic-reanalysis backbone → pre-integrated return-period depth rasters** (10/50/100/200/500-yr); USACE historical for validation | **Take:** pre-integrated depth grids as the M1 spine (the FSim/ASCE analogue, [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)). Sets [JD-FL-2](decisions.md) — **now superseded by [JD-FL-6](decisions.md)**: the V1 spine is **FEMA BLE** (+ SFHA-bathtub + NLDI→NSS/gauge `Q(T)`), with Fathom only a future commercial swap-in. **Resolved:** the RP-grid → shared-MC bridge is settled as the annual-max MC ([JD-FL-7](decisions.md)). |
| **A21 — M1↔M2 coupling types** (§2.3) | Flood = **site-conditioned**; the elevation-offset formula `depth_at_asset = water_surface_elevation − ground_elevation(asset_DEM)`; per-sub-cluster susceptibility (some inverter pads above, some below the floodplain) | **Take:** site-conditioned coupling + the DEM-offset formula verbatim as the M2 contract. Confirms [AFL-3/AFL-4](assumptions.md). |
| **A22 — M2↔M3 damage representation** (§2.4, §3.7, §7.6) | Depth-damage = **tabular USACE curves** (depth → MDR lookup); renewable-specific curves **do not exist yet** (Q7 open) | **Superseded:** A22 Q7 ("no solar flood curve") no longer holds — the canonical **`infrasure-damage-curves` RIVERINE_FLOOD × solar** curve exists and is **adopted** (source-agnostic over all sub-perils, AFL-8), keeping only the subsystem-split idea (base electrical drowns shallow; elevated panels survive). The USACE-from-scratch route is dropped. |
| **A24 — distribution choices** · **A25 — damage vs disruption scope** | Count/severity distribution axioms; flood = **acute × damage** cell only for V1 (no chronic / slow-onset) | **Take:** physical-damage-only fence (matches the team's no-BI scope); the distribution discipline feeds M4. |

## Bucket B — Input-data fetching — `old-hazard-model/` (data wrangling, **anti-pattern for loss math**)

> **How the old model does flood × solar (audited in code — the anti-pattern to escape).** Its pipeline is
> **loss-first and hazard-blind**: (1) **frequency** = NOAA Storm-Events flood *counts* within 10 mi of the site
> (`flash_flood_range_query.py` → Hydronos `noaa_storm`; `hazard_range_parameters.csv`); (2) **severity** = one
> **global lognormal per flood type, calibrated to a single benchmark loss** (`lognormal_global_fit.csv`: Riverine
> = "Great Flood 1993", Flash = "E. KY 2022", Coastal = "Sandy 2012"), applied to every site identically; (3)
> **damage** = **borrowed HAZUS residential/building curves** (`solar_config_default.csv` maps the solar inverter /
> electrical / substation to `riverine_flood_1_floor_no_basement`, `coastal_flood_1_story_residential_1st_floor_only`,
> `flood_power_plant`) — **no solar-specific flood curve**; (4) **assembly** = `magnitude_simulator.py` runs
> **backward** — an inverse "Real Estate" curve turns target EAL/VaR into a magnitude, a forward proxy curve turns it
> back into loss. Tellingly, **flood has no entry in `hazard_spatial_sizes.csv`** → **no footprint, no coupling, no
> DEM/elevation** — the asset's height vs the flood surface is never considered.

| Source | What it is | What we take / reject |
|--------|-----------|------------------------|
| `analysis/flood/flash_flood_range_query.py` + `config/hazard_range_parameters.csv` | **Hydronos** event-count query (Flash / Riverine / Coastal Flood, lat-lon + 10 mi radius, 2000–2024) | **Take:** the fetch mechanics + that Hydronos can supply flood event lists, and the per-subsystem-per-hazard mapping *structure* of `solar_config_default.csv`. **Reject:** event-counting *as the hazard* — population/report-biased counts (the hail DD-1 problem), no depth, conflates R/F/C. Not the M1 spine (pre-integrated grids are — [JD-FL-2](decisions.md)). |
| `config/lognormal_global_fit.csv` | Flood **severity** = one benchmark-calibrated lognormal per flood type, same for all sites | **Reject:** *loss-first* severity (reverse-fit to a famous event's dollar loss), not site-specific, not depth-derived. We build **depth-driven, per-site** severity from the RP grids instead. |
| `config/subsystems/solar_config_default.csv` | Solar subsystem × flood → **residential/building proxy** depth-damage curves | **Reject the curves** (a "1-story residential, 1st-floor-only" curve standing in for a solar inverter); **keep the subsystem-decomposition idea**. Confirms A22 Q7 — no renewable flood curve exists. |
| `analysis/mag_sim/magnitude_simulator.py`, `config/hazard_spatial_sizes.csv` | The **backward** loss→magnitude→loss engine; the (flood-absent) footprint table | **Reject wholesale for flood:** loss-first reverse-solve is the cardinal error the rebuild targets; flood has **no coupling** here at all. Useful only as the *structure* to improve on. |

## Bucket C — Competitive benchmarks — `…/competition/` + `…/glossary/`

| Source | What it is | What we take |
|--------|-----------|--------------|
| **First Street** (`glossary/FIRST_STREET.md`, `competition/FIRST_STREET.md`) | Best-in-class flood: R+F+C; **Fathom-US 2.0** 10 m → 3 m depth substrate; USACE curves + proprietary pluvial curve; multi-GCM uncertainty bands | The data-substrate target (Fathom-US) + the curve-sourcing reality (USACE public; pluvial proprietary). **Note:** they model *properties, not renewables* — the solar curve is our gap to fill. |
| **HAZUS** (`competition/HAZUS.md` §4) | FEMA flood loss: **multi-return-period depth grids → depth-damage → AAL via exceedance integration** | The reference **event model** (RP scenarios + AAL) — *the* thing to reconcile with our compound-Poisson MC. |

## Bucket D — In-repo grounding

| Source | What it is |
|--------|-----------|
| The shared **M4 MC engine** (hail/wildfire/wind notebooks) | The loss engine flood must plug into — the reconciliation target for the RP-vs-occurrence event model. |
| [`../../principles/`](../../principles/README.md) · [`learning_logs/09`](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) | The three principles + the pre-integrated-vs-extracted lesson (directly applies to JD-FL-2). |

---

*Resolved: the public-data depth path is settled as **FEMA BLE** (+ SFHA-bathtub for Zone-A wind sites + NLDI→NSS /
gauge `Q(T)` for the lower RPs, [JD-FL-6](decisions.md)); the RP-curve → shared-MC event-model bridge is settled as the
annual-max MC ([JD-FL-7](decisions.md)). First Street / Fathom-US 2.0 are retained only as a **future commercial
swap-in**, never the V1 spine.*
