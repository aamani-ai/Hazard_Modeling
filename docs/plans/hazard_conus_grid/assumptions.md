# Hazard CONUS Grid — Assumptions Register

This file holds the cross-cutting assumptions for the CONUS gridded hazard-risk product. Hazard-specific
frequency/severity assumptions live in each hazard subfolder; this register is only for assumptions shared by
every cell, asset, and hazard.

Companion files:

- [`decisions.md`](decisions.md) — choices made between options.
- [`output_schema.md`](output_schema.md) — per-cell artifact contract.
- [`common/benchmark_grid.md`](common/benchmark_grid.md) — grid source, key, and geometry.

**Status legend:** `decided` · `assumed` · `measured` · `input` · `deferred`.

---

## Exposure — canonical assets

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G1** | **Canonical exposure = 100 MW solar and 100 MW wind placed at each valued grid cell.** | The grid product is a location/hazard comparison, so asset size/config must be held fixed. | decided | adding another canonical size/scenario |
| **G2** | **Solar canonical asset = 100 MW dense areal footprint over `s_solar = 1.5 km²`.** Derived density: `66.7 MW/km²`. | USPVDB polygon-area evidence from the discussion phase; solar behaves as a compact near-ground damageable area for grid coupling. | measured / decided | AC-vs-DC convention changes; updated USPVDB evidence |
| **G3** | **Wind canonical asset = 100 MW = 20 turbines × 5 MW over a 30 km² sparse spacing envelope.** Derived density: `0.667 turbines/km²`, `3.33 MW/km²`. | Fixed generic wind farm for comparative maps. The envelope is not a solid damageable polygon. | assumed / decided | measured wind-boundary source lands; a second wind canonical case is requested |
| **G4** | **Wind engineering defaults:** hub height `100 m`, IEC Class II, ASCE Exposure C/open terrain, no v1 topographic speed-up. | The grid baseline should not silently vary by terrain, owner, or actual turbine model. Real-asset runs can specialize. | assumed / decided | adding explicit class/topography/hub-height scenarios |
| **G5** | **Wind narrow-swath exposure uses fractional turbine-density, not full-envelope loss.** | A narrow hail/tornado swath clipping 30 km² should damage an expected fraction of turbines, capped at 100%, not all 100 MW. | decided | using actual turbine coordinates |

## Exposure — granularity

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G6** | **Use the coarsest exposure tier the coupling needs:** area → fractional point-cloud/density → never sub-asset config for the grid. | A generic grid plant cannot honestly know row layout, cable routing, panel SKU, turbine model, or exact turbine coordinates. | decided | a hazard × asset coupling proves the current tier is insufficient |
| **G7** | **Canonical assets are sub-cell exposures.** A 0.25° cell is roughly 500-700 km²; solar is ~0.25% of a cell and wind envelope is ~4-6%. | The grid cell supplies the local hazard regime; the canonical asset supplies the exposed value/geometry. | assumed | assets span multiple cells or a hazard footprint is much smaller than the asset |

## Grid & reporting

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G8** | **Grid = the ERA5 native 0.25° benchmark grid from `benchmark-grid-dataset`.** | Reuse the platform benchmark grid and stable integer `cell_id`; do not invent a Hazard_modeling-only grid. | decided | benchmark-grid-dataset is replaced |
| **G9** | **`cell_id` is the durable join key.** Formula: `cell_id = lat_idx * 1440 + lon_idx`. | Defined in the benchmark grid spec; stable under regional expansion. | decided | never unless platform grid changes |
| **G10** | **Report all dollar risk metrics in both USD and `%TIV`.** | `%TIV` makes cell/asset comparison easier; USD keeps finance use cases alive. | decided | financial terms or insured limits are introduced |
| **G11** | **TIV is flat by canonical asset in v1.** Working basis: solar ~`$148M` per 100 MW; wind ~`$167M` per 100 MW. | Existing platform/default valuation basis; every dollar result scales linearly. | input / assumed | valuation basis is confirmed or regional capex scenarios are added |

## Engine & simulation

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G12** | **M0/M1 is hazard-specific; M2-M4 exposes a standard interface.** | Standard interface, not standard physics. Hail, wildfire, and wind can build different hazard distributions but emit a comparable risk layer. | decided | a hazard cannot satisfy the interface without distorting physics |
| **G13** | **MC depth target = 250,000 years per cell × asset × hazard, unless a pilot shows a lower depth is sufficient.** | Tail readouts such as PML500 and TVaR99 need more effective samples than EAL/PML100. | assumed | EVT tail lands or compute/storage constraints force a lower tier |
| **G14** | **Deep-tail metrics remain flagged when the severity distribution is bootstrap-limited.** | A short observed record cannot honestly support the far tail unless fitted severity/EVT is added. | decided | fitted severity + EVT tail is implemented |

## Deferred to Hazard Subfolders

- Hail M1 frequency and size distribution fitting.
- Wildfire FSim/WRC per-cell burn-probability and flame-length distribution construction.
- Per-hazard validation anchors and sparse-cell shrinkage.
- Per-hazard raw cache conventions.
