# M0 — Input Data (raw wind hazard evidence)

*The first layer: meet the raw wind hazard data and **understand** it, before any modeling. "What extreme-wind
hazard does the public record say exists at the two sites, and what do we really know about it?" Method-neutral —
understanding, not the model.*

**Where this sits:** layer-0 (definition) → **M0 (evidence)** → M1 catalog → M2 coupling → M3 damage → M4 loss &
metrics. No losses, no events-as-objects yet — just the *evidence*, each source explored on its own terms, then
**compared**. Plan: [`docs/plans/convective_wind/m0_input_data.md`](../../../docs/plans/convective_wind/m0_input_data.md) ·
Principles: [`docs/principles/notebook_work/`](../../../docs/principles/notebook_work/README.md).

## The structural twist — wind M0 meets **two data shapes at once**

Hail M0 met a **record** (extract events, fit a rate). Wildfire M0 met a **pre-integrated surface** (read a
profile, no fit). **Convective wind is the first peril that needs both** — it is **one peril with two sub-perils**,
tornado [T] and strong / straight-line wind [W], and they land in different coupling buckets
([discussion/convective_wind/02](../../../docs/extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)). (The
separate, deferred hurricane / tropical-cyclone peril is *not* a convective-wind sub-peril; it relates only through
the shared 3-s-gust wind-damage curve, and is out of scope for V1.)

| Notebook | Source | What it is | Data shape | Status |
|---|---|---|---|---|
| [`01_asce_hazard`](01_asce_hazard.ipynb) | **ASCE 7-22 design-wind maps** (Hazard Tool ArcGIS backend) | a **pre-integrated return-period 3-s-gust surface** — the EVT tail already fitted (the wildfire/FSim analog) | profile-assembly (**read** it) | ✅ **built** |
| [`02_spc_storm_record`](02_spc_storm_record.ipynb) | **SPC SVRGIS + NOAA Storm Events** | a **path/strike + report record** — tornado tracks (path geometry, EF) + severe-wind reports (the hail analog) | extraction (**fit** λ + severity) | ✅ **built** |
| [`03_asset_geometry`](03_asset_geometry.ipynb) | **USWTDB** turbine points + **boundary polygons** (renewablesinfo DB) | the two sites' areal footprint + per-turbine point cloud (two exposure views) | geometry | ✅ **built** |

**Why two shapes?** Strong wind arrives **pre-integrated** (ASCE did the probabilistic tail) → `01`; tornado has
**no public stochastic catalog**, so its frequency must be **fit from the SPC record** (bias-corrected) → `02`.
Both feed the same M1, which **forks per sub-peril** ([DD-WN-3](../../../docs/plans/convective_wind/decisions.md) strong
wind, [DD-WN-5](../../../docs/plans/convective_wind/decisions.md) tornado).

## The two sites — a low-vs-high contrast (mirrors hail's Hayhurst/Matrix)

| role | site | where | what it proves |
|---|---|---|---|
| **proving** | **Traverse Wind Energy Center** (~999 MW) | Oklahoma — Custer Co; tornado-alley + derecho corridor | the high end registers |
| **baseline** | **Shepherds Flat** (~845 MW) | Oregon — Gilliam Co; Columbia Gorge | the engine returns a correctly-small number where the hazard is low |

## What `01_asce_hazard` found (built)

- ASCE 7-22 strong-wind hazard is a **pre-integrated return-level curve** per site: RC II (700-yr) 3-s gust ≈
  **110 mph (Traverse, OK)** vs **99 mph (Shepherds Flat, OR)** — a real but **modest** straight-line-wind gap.
- The gust is **spatially flat** (≈0.1 mph) across each ~25 km footprint → the broad-swath / **site-conditioned**
  signature (no hit-or-miss; reuses wildfire's thin M2).
- **The two thresholds are far apart:** severe-wind events (μ = 58 mph) recur often, but turbine-damage onset (IEC
  survival ~117–157 mph) sits deep in the tail — even the 3000-yr gust ≈ class-III onset. → the M3 curve is
  **anchored** (DR≈0 over the bulk of the catalog); the destroying gusts come from the violent **tornado** tail.
- ASCE **Chapter-32** tornado design speeds cap ~EF2 (Shepherds Flat pinned at the 50 mph floor — outside tornado
  alley) → a **cross-check only**; the tornado spine is the SPC record (`02`).

## What `02_spc_storm_record` found (built)

- **Tornado is the catastrophic single-asset tail and lives here** (no design surface covers its violent tail).
  SPC tornado record 1950–2025 (73,458 tracks, all whole-track `sg==1`). Within 150 km: **Traverse ≈ 1,890
  tornadoes** (incl. EF3–EF5) vs **Shepherds Flat ≈ 36** (almost all weak) — a **~52× proving-vs-baseline contrast.**
- 🔴 **The record is population/reporting-biased (AWN-1) — a raw count is NOT a hazard rate.** Demonstrated:
  weak-tornado (EF0/EF1) share rises **0.61 → 0.90** across decades (detection, not climate); the **F→EF scale
  change (2007)**; **~1,546 unrated (`-9`)** tornadoes, concentrated post-2010; and wind reports are **~92%
  estimated, ~20% zero-magnitude, left-censored at ~50 kt (58 mph)**. → M1 must **bias-correct before fitting λ**;
  **no silent 1996+ filter** (the old repo's omission).
- **Episode de-duplication** (Storm Events): one outbreak `EPISODE_ID` = 412 events → counting raw reports
  inflates a single storm system many-fold; collapse on `EPISODE_ID` for independent-event frequency.
- **Per-site tornado path stats** (len × wid × EF) extracted for the M2 path-aware Minkowski; empirical path areas
  are far smaller than the old-repo EF-class area constants (a reconciliation flagged for M2).
- `loss`/`closs`/`DAMAGE_PROPERTY` **ignored** (non-PV $ basis — the hail `hail_hlrb`/TIV lesson).

## What `03_asset_geometry` found (built)

- Each farm is an **areal, multi-turbine asset** — two geometries kept: the **boundary polygon** (areal extent
  for tornado-path / swath intersection) and the **USWTDB turbine cloud** (per-turbine strike view). A single
  centroid would understate tornado strike exposure (AWN-23). Connection = the shared boundary DB
  (`renewablesinfo_org/.../powerplants_enriched_v2.parquet`, the same one solar + `model-gpr` use) + USWTDB API.
- **Traverse**: ~603 km² polygon, **356 turbines** in-polygon (GE 2.8-127), 999 MW nameplate — clean.
  **Shepherds Flat**: ~211 km², its **4 phases ≈ 338 turbines** (Horseshoe Bend, S/N Hurlburt, Shepherds Flat),
  845 MW — but the OSM polygon **over-captures ~46 neighbour turbines** (flagged; TIV uses the farm nameplate).
- **TIV (estimated, AWN-14):** Traverse ≈ **$1.4 B**, Shepherds Flat ≈ **$1.2 B** at $1,400/kW (placeholder — the
  %-of-TIV denominator; refine with a registry/valuation basis). Subsystem split deferred to M3.
- Caveats: `eia_id` null (name-match, not EIA join); USWTDB project names differ + per-phase (spatial match, not
  name); loose OSM polygon at Shepherds Flat.

**M0 is complete** — the wind hazard is understood across all three shapes (ASCE surface · SPC record · geometry).

## Inputs → outputs

Live ASCE Hazard Tool ArcGIS backend (`gis.asce.org/.../ASCE722`, no auth) → per-site
`data/convective_wind/<slug>_wind_m0_asce.parquet` (RP→gust table; gitignored) + `…_manifest.json` (kept). Raw `identify`
JSON cached under `data/convective_wind/raw/<slug>/` (gitignored).

## Key decisions & assumptions (this layer)

[DD-WN-3](../../../docs/plans/convective_wind/decisions.md) (ASCE surface = profile-assembly, no Hydronos) ·
[DD-WN-6/7](../../../docs/plans/convective_wind/decisions.md) (3-s gust; two thresholds). Assumptions **AWN-5** (3-s gust),
**AWN-11** (sources), **AWN-15** (ASCE = pre-integrated, Exposure-C borrow), **AWN-6/9/10** (two thresholds; IEC
provenance), **AWN-8** (EF5 ≈ 113 m/s ceiling) — plus the frequency-critical **AWN-1** (SPC population bias) lands
in `02`. Full register: [`assumptions.md`](../../../docs/plans/convective_wind/assumptions.md).

**Next → M1 (catalog):** fork per sub-peril — **strong wind** = profile-assembly off the ASCE surface (`01`, no
λ-fit); **tornado** = **bias-corrected** SPC fit (`02`, λ + bounded-GPD/EF severity) — carrying the boundary
polygon + turbine cloud (`03`) into M2 coupling. The 🔴 bias-correction (AWN-1) is M1's headline task.
