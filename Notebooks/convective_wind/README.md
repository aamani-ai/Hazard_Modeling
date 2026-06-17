# Convective wind — peril overview

The **convective-wind** hazard, organized `peril → asset`. This folder holds the **shared convective-wind catalog**
(asset-independent); the per-asset pipeline (coupling → damage → loss) lives in the asset subfolder. Driven by the
plan in [`../../docs/plans/convective_wind/`](../../docs/plans/convective_wind/README.md). Kernel: `.venv`
(`hazard_modeling`).

> **Convective wind = ONE peril, TWO sub-perils** — **tornado [T]** (rotating, narrow, violent) and **strong /
> straight-line wind [W]** (broad-swath synoptic/derecho). They share the **3-s peak gust** observable and the
> turbine, but differ as perils — different footprints, frequencies, data products, and coupling. **Hurricane /
> tropical cyclone is a *separate*, deferred peril** (field-intensity), related only by the shared 3-s-gust damage
> curve — *not* a convective-wind sub-peril.

```
convective_wind/
  layer0/          ← the AUTHORED hazard definition (3-s gust · two thresholds · EF scale · the sub-peril split)  ┐ the PERIL
  m0_input_data/   ← raw evidence: ASCE RP gust surface (W) + SPC tornado/wind record (T) + asset geometry        │ (asset-
  m1_catalog/      ← per-sub-peril catalog: W = profile-assembly from ASCE; T = bias-corrected SPC λ + bounded GPD ┘  independent)
  wind_farm/       ← convective wind × WIND FARM — coupling · damage · loss & metrics   ✅ built end-to-end
  # solar/         ← a later sibling asset cell (same catalog, different coupling/fragility)
```

> **New here?** Read the authored definition in **[`layer0/`](layer0/README.md)** (why two thresholds, what a 3-s
> gust is), skim the shared catalog below (M0 → M1), then open **[`wind_farm/`](wind_farm/README.md)** for the full
> M2 → M3 → M4 worked example and the headline risk numbers.

---

## Layer-0 — the authored hazard definition  ·  [📖 folder README](layer0/README.md)

Unlike hail/wildfire (where the hazard was self-evident), convective wind needs its **definition authored first** —
the two sub-perils, the universal **3-s peak gust** observable, and the **two distinct thresholds** that the rest of
the pipeline hangs on:

| | Threshold | Governs | Lives in |
|---|---|---|---|
| **meteorological event** μ | 58 mph ≈ 25.9 m/s (NWS severe) / EF0 ≈ 29 m/s | what the **catalog counts** (for λ) | M1 |
| **asset damage-onset** | IEC 61400 survival ≈ Ve50 ≈ 52–70 m/s | where the **damage curve leaves zero** | M3 |

Keeping them separate is *the* anti-pattern the old repo collapsed; it makes `DR(μ) ≈ 0` (most "severe wind" barely
scratches a turbine). Notebook: `layer0/01_hazard_definition` ✅.

## The shared hazard catalog (M0 → M1) — built once, reused by every asset

The atmosphere over a region is the same regardless of what sits underneath, so M0/M1 live at the **peril** level.
Only M2–M4 specialize per asset.

### M0 — input data  ·  [📖 folder README](m0_input_data/README.md)

Three sources behind one interface; each notebook does a complete-pass field dictionary (per `docs/principles/notebook_work/`).

| Notebook | Source | What / grain | Status |
|---|---|---|---|
| `m0_input_data/01_asce_hazard` | **ASCE 7-22** return-period 3-s-gust surface (the `gis.asce.org` ArcGIS backend; `w2022_mri{10..1e6}`) | **pre-integrated EVT** product → the **strong-wind (W)** hazard spine; RP→gust read per site (no fit) | ✅ built + executed |
| `m0_input_data/02_spc_storm_record` | **SPC** SVRGIS tornado tracks + severe-wind reports + **NOAA Storm Events** | point/track reports → the **tornado (T)** raw evidence; **population/detection-biased** (must bias-correct before any λ fit — AWN-1) | ✅ built + executed |
| `m0_input_data/03_asset_geometry` | **USWTDB** turbine point-cloud + boundary polygon + $/kW TIV | the two wind farms' geometry (footprint for coupling, TIV for % of TIV) | ✅ built + executed |

### M1 — event catalog + frequency  ·  [📖 folder README](m1_catalog/README.md)

The catalog **forks by sub-peril** — two data products, two machineries (the live test of *standard interface, not
standard physics*):

| | Strong / straight-line wind [W] | Tornado [T] |
|---|---|---|
| **frequency λ** | **read** the ASCE RP curve → λ (profile-assembly, *no fit*) — the **wildfire** pattern | **fit** λ_collection from SPC (**bias-corrected**), thinned by `p_hit` in M2 — the **hail** pattern |
| **severity** | Gumbel / light-exponential (ξ≈0), capped at L | bounded **GPD** (ξ<0), truncated at the EF5 ceiling L=113 m/s |

Notebook: `m1_catalog/01_catalog` → `data/convective_wind/<site>_wind_m1_manifest.json` (the typed M2/M4 contract), both sites. ✅.

```text
        ASCE 7-22 RP surface (W)          SPC SVRGIS + Storm Events (T)
        pre-integrated EVT                point/track reports, biased
                 │                                   │
                 ▼  profile-assembly (no fit)        ▼  bias-correct → fit λ_collection + bounded GPD
        ┌─────────────────────────────────────────────────────────────┐
        │  M1 CATALOG  (per sub-peril {λ, severity})  →  M2/M4 contract │
        └─────────────────────────────────────────────────────────────┘
```

---

## The per-asset pipeline

### ✅ Wind farm — [`wind_farm/`](wind_farm/README.md)

Two wind farms: **Traverse Wind Energy Center, OK** (proving / high-wind, TIV ≈ $1.40B) + **Shepherds Flat, OR**
(baseline / low-wind, TIV ≈ $1.18B). Built end-to-end, and this is where the **sub-peril fork plays out**:

- **M2 coupling** — *folder-forks*: tornado = **areal hit-or-miss** (path-aware Minkowski + swept fraction); strong
  wind = **site-conditioned** (read the site's ASCE RP gust, whole farm exposed).
- **M3 damage** — **one turbine, two sub-peril fragility curves**: a tornado is *more damaging at the same gust*
  than straight-line wind (rotation defeats feathering; vertical/pressure/debris loads) → lower onset + steeper +
  full reach; strong wind = aero reach, onset at IEC survival. Both `DR(μ)≈0`.
- **M4 loss** — both streams co-sampled into **one** annual-loss distribution per site; EAL additive, every tail
  metric off the **joint**. **Traverse EAL 0.064% / PML250 3.99% / TVaR99 4.88%** (tornado tail); Shepherds ≈flat;
  strong wind ≈0 (the known-answer check). Open [`wind_farm/README.md`](wind_farm/README.md) for the walkthrough.

A `solar/` cell could be added later as a sibling under the same catalog — different coupling and fragility, same
M0→M4 interface.

---

## Production path (peril-level)
Calibrated turbine fragility curves from `infrasure-damage-curves` (the M3 curves are the dominant uncertainty,
AWN-26) · the **strong-wind disruption/degradation track** (curtailment + fatigue — AWN-31, the Performance tier) ·
the separate **hurricane** peril (watch the TC-tornado double-count flag, AWN-30) · **portfolio correlation** across
farms (AWN-22). The `deferred` rows in the [assumptions register](../../docs/plans/convective_wind/assumptions.md)
are the backlog. Method provenance: [`docs/references/`](../../docs/references/README.md).
