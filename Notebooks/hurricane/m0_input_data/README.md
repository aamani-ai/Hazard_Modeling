# M0 — input data (hurricane)

*Meet and understand the raw hurricane evidence — method-neutral, no fields, no losses. Plan:
[`docs/plans/hurricane/m0_input_data.md`](../../../docs/plans/hurricane/m0_input_data.md).*

| Notebook | What it meets | Status |
|---|---|---|
| [`01_raft_catalog`](01_raft_catalog.ipynb) | the **RAFT** storm-resolved synthetic catalog (the build source) | ✅ **built** |
| [`02_landfall_record`](02_landfall_record.ipynb) | **HURDAT2** observed landfalls — the rate anchor + Holland validation targets | ✅ **built** |
| [`03_site_geometry`](03_site_geometry.ipynb) | the solar sites (screened Gulf/Atlantic high + Hayhurst baseline + flood cross-link riders) | ✅ **built** |

**M0 complete.** → next: M1 (catalog).

**Magnitude metric (carried downstream): the 3-second peak gust (mph)** — sampled at these locked sites in M1 from the
Holland (1980) wind field. M0 carries no gust, only the raw evidence (the storm set, the observed rate, the *where*).

*(The **STORM RP-grid cross-check** the plan paired with 02 moved to **M1** — it's site-dependent + a 1.1 GB
download, and it validates *our* catalog's return-period winds at the locked site.)*

## What `01_raft_catalog` established (the findings that shape M1)

- **RAFT is reachable & storm-resolved** — 40,000 North Atlantic storms over 40 env-years (1979–2018), Zenodo
  `10.5281/zenodo.10392723`, CC-BY-4.0; tracks file 147 MB (rainfall is the separate, deferred 16 GB slice).
- **🔴 `vmax` is in *knots*** — not m/s. Convert **×1.150779 → mph** (the damage-curve unit). A silent m/s read
  would understate gusts ~2×. ([ATC-8](../../../docs/plans/hurricane/assumptions.md))
- **🔴 The raw catalog rate is a ~71× genesis oversample** (~1000 seeds/env-year vs the real ~14 named storms/yr;
  median peak 55 kt → mostly weak). So **M1 must calibrate the per-site rate to observed landfalls** (02), using the
  catalog for conditional severity/geometry only. ([ATC-9](../../../docs/plans/hurricane/assumptions.md))
- **18.2% are major (≥Cat3)** — the loss-driving tail is well-resolved.
- **No rainfall variable** in the tracks file — confirms the wind/rain scope split.

Output: `data/hurricane/tc_m0_raft_summary.parquet` (per-storm summary, the M1 build source) + manifest.

## What `02_landfall_record` established (the rate anchor)

- **HURDAT2 parsed & validated** — 1,973 Atlantic storms, 1851–2023. The **US hurricane-landfall rate reproduces
  the published climatology: 1.69/yr vs ~1.7/yr** (major 0.55 vs ~0.46) — a clean known-answer.
- This is the **rate anchor** that calibrates RAFT's ~71× oversample in M1 (ATC-9), and the per-storm landfall
  intensities are the **validation targets** for M1's Holland field replay (JD-TC-7).
- Emits **two** products so M1 uses one rulebook for frequency and severity: the **landfall catalog**
  (`tc_m0_hurdat2_landfalls.parquet`, 749) *and* the **hurricane-intensity track points**
  (`tc_m0_hurdat2_tracks_hu.parquet`) — the latter lets M1 count **close passages within 100 km** (offshore brushes
  included), matching RAFT's severity definition (JD-TC-8).

## What `03_site_geometry` established (the locked sites)

- **The proving pair is screened** from the national EIA-860 solar fleet on **observed hurricane-landfall density**:
  - **proving / high-TC = Everglades Solar Energy Center** (FL, Miami-Dade) — the highest US hurricane exposure
    (landfalls/100 km) *and* coastal (the surge cross-link ground); the end-to-end example.
  - **baseline / low-TC = Hayhurst Texas Solar** (TX; 24.8 MW) — **0 landfalls/100 km**, the true-zero control.
- **Two cross-link riders are appended** (not screened — they enter to supply a wind leg for flood's compound combine,
  [JD-FL-16](../../../docs/plans/flood/decisions.md)) and are excluded from the hurricane headline:
  - **Discovery Solar Center** (FL) — the flood-coastal wind+surge cross-link site.
  - **LA3 West Baton Rouge** (LA) — the **all-three flood solar site**, present so flood-coastal × solar M4 has its
    hurricane-wind leg.
- Geometry = capacity→radius circle + centroid (enough for solar's degenerate field-intensity, JD-TC-2); TIV $/MW.
- Output: `data/hurricane/tc_m0_sites.json` + `tc_m0_site_screen.csv`.
