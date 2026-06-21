# Hurricane / tropical-cyclone — the field-intensity peril

Worked, end-to-end notebooks for **hurricane wind**. This peril models **tropical-cyclone WIND** and exercises the
repo's **field-intensity** coupling type — a continuous wind field sampled at the asset. It also founds coastal flood:
its **storm-resolved RAFT catalog** carries event identity (`event_family_id`) so the same storms reach flood's
secondary perils. Plan of record: [`docs/plans/hurricane/`](../../docs/plans/hurricane/README.md).

**Magnitude metric: the 3-second peak gust (mph)** at the site, synthesized from the **Holland (1980)** parametric
wind field evaluated along storm tracks. Storm **surge** and **TC rainfall** are the secondary perils — they are
sourced and handled as flood's coastal `[C]` and pluvial `[F]` sub-perils and cross-linked via `event_family_id`,
**not** modeled in the hurricane cell.

**Data sources:**
- **RAFT** North-Atlantic synthetic TC track catalog — the storm set (40k storms, 1979–2018; Zenodo `10.5281/zenodo.10392723`).
- **NOAA HURDAT2** — the observed landfall / close-passage record → frequency anchor + severity validation.
- **EIA-860** — the solar fleet screen population.
- **USWTDB** — wind-turbine locations (the wind-farm asset).
- **ASCE 7-22** design wind speeds — the independent tail validation.
- **infrasure-damage-curves** library — HURRICANE × solar fragility curves; the convective_wind turbine curve is
  reused for the wind-farm cell (hurricane wind on a turbine ≈ straight-line wind).

```
hurricane/
  m0_input_data/      ← raw evidence: RAFT catalog, HURDAT2 landfalls, site geometry + TIV
  m1_catalog/         ← the peril (shared): tracks → Holland field → per-site 3-s-gust catalog + event_family_id
  solar/              ← asset cell: M2 coupling · M3 damage · M4 loss & metrics
  wind_farm/          ← asset cell: per-turbine field-intensity at Amazon Wind US East (NC)
```

## Two assets, M0→M4

**M0 → M1 are shared** across both assets — the storm catalog and the per-(storm, site) 3-s-gust field. M1 frequency
is **observed-anchored** (HURDAT2 close-passage / landfall rate) × RAFT-physics severity; the RAFT genesis oversample
is corrected ([JD-TC-8](../../docs/plans/hurricane/decisions.md)). Each M1 row is stamped `event_family_id`. Assets
fork at M2.

| Layer | Notebook | Status |
|---|---|---|
| M0 | [`m0_input_data/01_raft_catalog`](m0_input_data/01_raft_catalog.ipynb) | ✅ RAFT understood (40k N. Atlantic storms, 1979–2018) |
| M0 | [`m0_input_data/02_landfall_record`](m0_input_data/02_landfall_record.ipynb) | ✅ HURDAT2 rate anchor (1.69/yr ≈ published 1.7/yr) |
| M0 | [`m0_input_data/03_site_geometry`](m0_input_data/03_site_geometry.ipynb) | ✅ sites locked + screened + cross-link riders appended |
| M1 | [`m1_catalog/01_event_catalog`](m1_catalog/01_event_catalog.ipynb) | ✅ Holland field + observed-anchored λ (JD-TC-8); RAFT severity validated (90 kt == obs) |
| M1 | [`m1_catalog/02_tail_validation`](m1_catalog/02_tail_validation.ipynb) | ✅ tail matches ASCE within 5.5% (100–700 yr), no low bias |
| **solar** M2 | [`solar/m2_coupling/01_coupling`](solar/m2_coupling/01_coupling.ipynb) | ✅ field-intensity, degenerate (footprint spread median 0.5%) |
| **solar** M3 | [`solar/m3_damage/01_damage`](solar/m3_damage/01_damage.ipynb) | ✅ library HURRICANE×SOLAR (provisional); worst Cat-5 ≈ 41% TIV |
| **solar** M4 | [`solar/m4_loss_metrics/01_loss_metrics`](solar/m4_loss_metrics/01_loss_metrics.ipynb) | ✅ EAL 2.23% / PML500 41.5% TIV (point, provisional curve); Hayhurst 0 |
| **wind** M2 | [`wind_farm/m2_coupling/01_coupling`](wind_farm/m2_coupling/01_coupling.ipynb) | ✅ per-node field-intensity at Amazon (non-degenerate, spread median 4.4%) |
| **wind** M3 | [`wind_farm/m3_damage/01_damage`](wind_farm/m3_damage/01_damage.ipynb) | ✅ reused turbine curve → per-storm **per-subsystem** DR + `event_family_id` |
| **wind** M4 | [`wind_farm/m4_loss_metrics/01_loss_metrics`](wind_farm/m4_loss_metrics/01_loss_metrics.ipynb) | ✅ wind-only EAL 0.012% / PML500 1.43% TIV (surge-dominated cell) |

### Solar cell — sites

Four solar sites ride the pipeline:

- **Hayhurst Texas Solar** (TX) — true-zero baseline (inland, no landfalls; λ=0).
- **Everglades Solar Energy Center** (FL) — the proving / high-TC end-to-end example (screened highest US landfall density).
- **Discovery Solar Center** (FL) — cross-link rider for flood-coastal's wind+surge compound combine.
- **LA3 West Baton Rouge** (LA) — the **all-three flood solar site**, present so flood-coastal × solar M4 has its
  hurricane-wind leg.

The cross-link / all-three riders (Discovery, LA3) enter by append (M0 → M1 → M3) to supply a wind leg for flood;
they are **excluded from the hurricane headline** (M4 filters `cross-link`). Everglades + Hayhurst are the example pair.

Solar M2 couples the gust field to the footprint and is spatially **degenerate** (gust spread ≪ gust across a sub-km
plant → `value_exposed_fraction = 1.0`). M3 = gust → capex-weighted asset DR (tracker-stow curve). M4 =
compound-Poisson wind EAL / VaR / PML / TVaR (% of TIV + $).

### Wind-farm cell — site

- **Amazon Wind US East** (NC), 104 × 2 MW (TIV $291M) — the **all-three flood wind site**.

Wind M2 is **per-turbine** (non-degenerate — real gust spread across the ~km-scale lease). M3 = per-storm,
**per-subsystem** turbine wind DR (rotor / nacelle / electrical / substation reached; tower / foundation / civil not
reached by straight-line loading → asset DR caps ~0.65), stamped `event_family_id` — exactly the input the
flood-coastal × wind M4 joins to the surge leg. M4 = compound-Poisson wind-only EAL / PML. Wind is small at Amazon
(turbines survive sound-weakened storms); the cell's material hazard is surge, supplied by flood.

## What makes hurricane special

- **Field-intensity coupling** — a continuous wind field sampled at the asset. *Spatially degenerate on solar*
  (storm ≫ sub-km plant → ~one centroid sample), fully exercised at the wind-farm cell (per-turbine across the lease).
- **Storm-resolved RAFT catalog** — events are objects with identity (`event_family_id`), so one catalog founds
  hurricane wind **and** flood's coastal surge + pluvial-TC rain (no double-count). This is why RAFT, not the
  pre-integrated STORM RP grid ([JD-TC-3](../../docs/plans/hurricane/decisions.md)).
- **Wind only** — surge / rain are *flood's* sub-perils, reached via `event_family_id`, not re-catalogued here. The
  hurricane × asset M3 per-storm damage feeds the flood-coastal compound combine (surge × wind) via `event_family_id`
  ([JD-FL-12](../../docs/plans/flood/decisions.md)).

## Environment

Same as the rest of the repo: `source ../../.venv/bin/activate`, `pip install -r ../../requirements.txt`, then
register the kernel (`python -m ipykernel install --user --name hazard_modeling`) — exactly as
[`Notebooks/README.md`](../README.md) describes. RAFT adds one dependency, **`h5netcdf`** (in `requirements.txt`), to
read the HDF5/NetCDF-4 catalog. Heavy data (the 147 MB RAFT `.nc`, parquets) stays gitignored under
`data/hurricane/`; manifests are kept.
