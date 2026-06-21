# M0 — Input Data (the active plan)

*The first modeling layer (it sits **under** [layer-0](00_hazard_definition.md), which authored the event method
before any data): meet the raw hurricane evidence and **understand** it. "What tropical-cyclone hazard does the
public record say exists at the two solar sites, and what do we really know about it?" Method-neutral —
understanding, not the model. Mirrors hail's record-fit M0 and wildfire/flood's pre-integrated M0; hurricane meets
**both shapes** — a storm-resolved catalog to build from (RAFT) **and** pre-integrated/observed surfaces to
validate against (STORM RP grid, IBTrACS/HURDAT2).*

**Where this sits:** layer-0 (definition) → **M0 (evidence)** → [M1 catalog](m1_catalog.md) →
[M2 coupling](m2_coupling.md) → [M3 damage](m3_damage.md) → [M4 loss & metrics](m4_loss_metrics.md). No losses, no
field built yet — just the *evidence*, each source on its own terms, then reconciled. **How the event was defined
first:** [00_hazard_definition](00_hazard_definition.md). Base reference:
[`jdocs/Hazard_Data_Reference-TC_Hurricane.md`](../../../jdocs/Hazard_Data_Reference-TC_Hurricane.md).

---

## The structural twist — M0 meets a *storm-resolved catalog* + two validation surfaces

Hail M0 met a **record** (extract events, fit a rate). Wildfire/flood M0 met a **pre-integrated surface** (read a
profile). Hurricane M0 meets a **storm-resolved synthetic catalog** — RAFT tracks, each a *storm object* — which is
neither: we don't fit a rate to a sparse record (the catalog *is* the rate, over thousands of synthetic years) and
we don't read a pre-integrated profile at a point (we must *build* the field ourselves, M1). M0's job is to
**understand the catalog and bracket it with truth**:

| Source | Shape | Role in M0 |
|---|---|---|
| **RAFT** (synthetic tracks + intensity + rainfall) | storm-resolved catalog | **the build source** — the storms we'll turn into fields (M1) |
| **IBTrACS / HURDAT2** (observed best tracks) | event record | **landfall-wind validation** — does the catalog (and later the Holland field) match reality? |
| **STORM 10 km wind-RP GeoTIFF** | pre-integrated RP surface | **RP cross-check** — does our catalog's return-period wind agree (noting STORM's empirical-Weibull runs low past ~100-yr)? |

> So M0 here is **understand the catalog, then bracket it** — not "fit a record" and not "read a surface." Both
> validation sources are public; all feed the M1 field-catalog build.

---

## Sourcing — direct public products ([JD-TC-3](decisions.md), [ATC-17](assumptions.md))

| Notebook | Source | What it is | Access |
|---|---|---|---|
| `01_raft_catalog` | **RAFT** (Risk Analysis Framework for TCs) | synthetic N. Atlantic tracks: position, along-track intensity (pressure/wind), radius params, **TC rainfall** | NetCDF; CC-BY-4.0; **Zenodo `10.5281/zenodo.10392723`** ✅ probed live (2026-06-19) — tracks file `RAFT.NA.v20231016.nc` **154 MB** (V1 spine); resolve via the Zenodo **API** (versioned record), don't hardcode a version |
| `02_landfall_…` | **IBTrACS** (NCEI) | observed global best tracks, max wind, central pressure, 3-hourly | CSV/NetCDF; public domain |
| `02_landfall_…` | **HURDAT2** (NHC) | Atlantic best tracks, 6-hourly center/wind/pressure | CSV; public domain |
| `02_landfall_…` | **STORM 10 km wind-RP GeoTIFFs** (Zenodo 10931452) | max-wind return-period grids (m/s), 28 RPs | GeoTIFF; CC0 |
| `03_site_geometry` | **OSM / EIA `powerplants_enriched_v2`** | solar footprint polygon + capacity (TIV basis) | public |
| (screening) | **FEMA Hazus / NRI** (Hurricane) | tract-level loss benchmark | public |

**Re-verify endpoints live at build time** (probed 2026-06-19: IBTrACS/HURDAT2/STORM-GeoTIFF/SLOSH = `200`; **RAFT
Zenodo `10392723` = `200`, tracks `.nc` streams via range `206`**; the 4TU STORM-*tracks* DOI = `404` → resolve
STORM tracks' current DOI at build if ever needed). Cache raw pulls to `data/hurricane/<asset>_raw/` (**gitignored**;
keep a small manifest).

> **Data-size split (confirmed at probe) — the scope boundary pays off concretely.** RAFT's **tracks+intensity**
> file (`RAFT.NA.v20231016.nc`) is **154 MB** — the V1 wind spine, an easy pull. RAFT's **TC rainfall** is
> `RAFT_accum_rainfall_*.tar.gz` × 9 ≈ **16 GB** — the **deferred pluvial-TC slice** ([JD-TC-6](decisions.md)). **V1
> wind fetches only the 154 MB tracks file; the 16 GB of rainfall stays untouched** until the compound-flood build.

### Setup prerequisite
The `.venv` has `pandas`/`pyarrow`/`numpy`/`xarray`/`rasterio`/`geopandas`/`shapely`. Hurricane adds **`xarray`/
`netCDF4`** for RAFT (confirm present). A Holland implementation (CLIMADA's, or a thin local one) is an **M1**
concern — M0 only *reads* RAFT, it does not build fields. Notebooks are jupytext `.py`(percent) + `.ipynb`, kernel
`hazard_modeling`.

---

> **✅ Built (2026-06-19) — what the RAFT file actually contained** (reconciling the plan with reality):
> 40,000 N. Atlantic storms × 120 6-hourly steps; per-step `lat/lon/vmax/mslp/rmax/shear`; per-storm
> `year(1979–2018)/basin_ID/storm_ID`. **Three findings folded back:** (1) **`vmax` is knots**, not m/s (→mph
> ×1.150779 — [ATC-8](assumptions.md) corrected); (2) the **raw ~1000 storms/env-year is a ~71× genesis
> oversample** vs real ~14/yr → **M1 calibrates the per-site rate to observed landfalls** ([ATC-9](assumptions.md));
> (3) **no rainfall variable** in the tracks file (it's the deferred 16 GB slice — confirms the scope split). The
> per-site subset (plan step 2 below) **moves to M1** once 03 locks the sites; 01 emits the asset-independent
> per-storm summary instead. See [`Notebooks/hurricane/m0_input_data/01_raft_catalog`](../../../Notebooks/hurricane/m0_input_data/01_raft_catalog.ipynb).

## Notebook `01_raft_catalog` — the storm-resolved synthetic catalog (the build source)

1. **From-scratch "what is this catalog" walkthrough** — a RAFT row is a **storm object**: a track (lat/lon over
   time) carrying along-track central pressure, max wind, radius-of-max-wind, and rainfall. Explain plainly: this is
   *not* a forecast and *not* an observation — it is a **synthetic catalog spanning many years**, so the **catalog
   itself is the frequency** (no rate-fit needed; contrast hail). Storm-resolution is the load-bearing property
   ([JD-TC-3](decisions.md)): every storm has identity → the future `event_family_id`.
2. **Subset to the site neighborhood** — keep tracks whose closest approach passes within a stated collection
   radius of each site (radius *size* cancels in `λ_site`, [learning-06](../../learning_logs/06_collection_region_size_cancels.md)).
   Cache the subset.
3. **Field-dictionary every variable** (value + meaning + units/base + what-it's-NOT): **wind in m/s** (⚠ →mph
   ×2.237, [ATC-8](assumptions.md)); **max *sustained* wind** (1-min, Saffir-Simpson basis — *not* the 3-s gust;
   gust factor applied in M1, [ATC-7](assumptions.md)); central pressure (hPa); RMW (km); rainfall (mm).
4. **Catalog audit** — synthetic-year count, storms/year near each site, intensity distribution, RMW distribution;
   confirm the N. Atlantic basin covers both US sites. State RAFT's own skill (R²≈0.73 landfall winds vs obs) as
   the honest accuracy bound.
5. **Emit** `data/hurricane/<asset>_tc_m0_raft.parquet` (subset track points + storm IDs + intensity/radius/rain)
   + manifest (DOI, basin, synthetic-year count, radius, units).

> **✅ Built (2026-06-19) as `02_landfall_record` — scope refined.** The **STORM RP-grid cross-check moved to M1**
> (it's site-dependent + a 1.1 GB download, and it validates *our* catalog's RP at the locked site — an M1
> validation, not M0 understanding). M0/02 is now the **HURDAT2 observed landfall record**: it **reproduced the
> published US hurricane-landfall climatology — 1.69/yr vs ~1.7/yr** (major 0.55 vs ~0.46) — confirming it as a
> trustworthy **rate anchor** for RAFT's oversample, plus the per-storm landfall intensities as M1's Holland
> **validation targets**. IBTrACS deferred (HURDAT2 suffices for US Atlantic). See
> [`Notebooks/hurricane/m0_input_data/02_landfall_record`](../../../Notebooks/hurricane/m0_input_data/02_landfall_record.ipynb).

## Notebook `02_landfall_record_and_rp_crosscheck` — the two truth surfaces

1. **IBTrACS / HURDAT2 walkthrough** — observed best tracks: what "best track" means (post-storm reanalysis),
   3/6-hourly resolution, max wind = sustained. The **landfall-validation purpose**: when M1's Holland field replays
   a historical track, modeled landfall gust must reproduce the observed.
2. **Extract historical landfalls near each site** — storms passing within the collection radius, with observed
   landfall max wind + pressure → the validation targets.
3. **STORM RP grid walkthrough + sample** — read the 10 km max-wind RP GeoTIFF at each site centroid → an RP→wind
   curve. Explain it is **pre-integrated, empirical-Weibull RP** (⚠ runs low past ~100-yr vs EVD — Hazard Data Ref
   §7, [ATC-10](assumptions.md)); m/s (→mph ×2.237).
4. **Field-dictionary** both: observed sustained wind vs synthetic, RP = return period, datum/units.
5. **Emit** `data/hurricane/<asset>_tc_m0_validation.parquet` (historical landfalls + STORM RP curve per site) +
   manifest.

> **✅ Built (2026-06-19).** Screened the national EIA solar fleet (reused flood's cache) on **observed
> HURDAT2 hurricane-landfall density within 100 km**. **High = Everglades Solar Energy Center (FL, Miami-Dade,
> 74.5 MW) — 31 landfalls/100 km** (highest US hurricane exposure + coastal → surge cross-link ground);
> **baseline = Hayhurst (TX, 0 landfalls)** — true-zero control. Geometry = capacity→radius circle + centroid
> (degenerate field-sample point); TIV $1.483 M/MW. **M0 complete.** See
> [`Notebooks/hurricane/m0_input_data/03_site_geometry`](../../../Notebooks/hurricane/m0_input_data/03_site_geometry.ipynb).

## Notebook `03_site_geometry` — the two solar sites

1. **The two sites** ([JD-TC-5](decisions.md)) — a low-vs-high contrast:

| role | asset | where | screened exposure |
|---|---|---|---|
| **proving** | screened **Gulf/Atlantic-coast solar farm** | confirmed in this notebook | material TC landfall wind; coastal (future surge ground) |
| **baseline** | **Hayhurst Texas Solar** (reused) | Culberson Co., TX (desert) | near-zero TC — the control |

2. **Screen the high site** — rank coastal solar (national `powerplants_enriched_v2`) by TC exposure (STORM RP wind
   / historical landfall density) **and** real-footprint availability; confirm one. Reuse Hayhurst's polygon.
3. **Geometry** — the solar **footprint polygon** (dense areal, ~km²) — *not* a point cloud (that's wind-farm V2).
   Record centroid (the degenerate field-sample point, [JD-TC-2](decisions.md)) + footprint.
4. **TIV** — $/MW × capacity (Hayhurst hail basis; coastal site estimated, [ATC-16](assumptions.md)) → % of TIV + $.
5. **Emit** `data/hurricane/<asset>_tc_m0_geometry.parquet` + manifest.

## Cross-source comparison (the M0 payoff → feeds M1)

For each site, put the **RAFT synthetic intensity** beside the **observed IBTrACS/HURDAT2 landfalls** (does the
synthetic catalog's intensity range bracket the historical?) and the **RAFT-implied RP wind** beside the **STORM RP
curve** (do they agree, given STORM's empirical-Weibull low tail?). Conclude the M1 plan: **RAFT is the build
source; IBTrACS/HURDAT2 the landfall validation; STORM the RP cross-check.** This is M0's deliverable — the hazard
*understood and bracketed*, ready for the Holland field build.

---

## Outputs

```text
data/hurricane/<asset>_raw/                          raw RAFT NetCDF, IBTrACS/HURDAT2, STORM GeoTIFF, polygon  (gitignored)
data/hurricane/<asset>_tc_m0_raft.parquet            RAFT track subset + storm IDs + intensity/radius/rain     (gitignored)
data/hurricane/<asset>_tc_m0_validation.parquet      historical landfalls + STORM RP curve per site            (gitignored)
data/hurricane/<asset>_tc_m0_geometry.parquet        solar footprint polygon + centroid + TIV                  (gitignored)
data/hurricane/<asset>_tc_m0_*_manifest.json         provenance + units + DOIs + radius                        (kept)
```

## Assumptions surfaced (this layer)

[ATC-5](assumptions.md) (RAFT catalog) · [ATC-8](assumptions.md) (m/s→mph) · [ATC-7](assumptions.md) (sustained→3-s
gust, deferred to M1) · [ATC-9](assumptions.md) (frequency from RAFT) · [ATC-10](assumptions.md) (validation +
STORM low tail) · [ATC-16](assumptions.md) (sites/TIV) · [ATC-17](assumptions.md) (public data) · collection-radius
size cancels ([learning-06](../../learning_logs/06_collection_region_size_cancels.md)).

## Open questions to resolve in / before M0

- **RAFT DOI/access** — confirm the current NetCDF is fetchable; note basin file layout.
- **High site** — confirm the screened coastal solar farm (exposure + real footprint).
- **Collection radius** — choose the homogeneity radius (size cancels; don't tune magnitude with it).
- **Sustained-vs-gust** — confirm RAFT's wind definition (1-min sustained) so M1's gust factor is applied once.

## Honoring the exploratory-data-notebook principle (the binding checklist)

All three M0 notebooks must satisfy [`principles/notebook_work/exploratory_data_notebooks.md`](../../principles/notebook_work/exploratory_data_notebooks.md)
— *interpret every variable; the interpretation is the deliverable.* The "number needs its base" traps, hurricane
instances:

| Source / field | The trap | Its base / correct reading |
|---|---|---|
| RAFT / STORM wind | looks like "the wind" | **m/s**, not mph (×2.237); and **sustained**, not 3-s gust |
| RAFT max wind | reads as gust | **1-min sustained** — apply a gust factor (M1) before the damage curve |
| STORM RP wind | reads as "the 1000-yr wind" | **empirical-Weibull RP** — runs **low** past ~100-yr vs EVD |
| RAFT synthetic year | reads as a forecast | a **synthetic climatology** — the catalog *is* the frequency |
| solar polygon at storm scale | "the field hits the plant" | the storm field is ~uniform across ~1 km → **one centroid sample** (degenerate coupling, M2) |

**Next → [M1 (catalog)](m1_catalog.md):** turn the RAFT tracks into a **Holland wind field**, sample per site, stamp
`event_family_id`, and **validate vs IBTrACS/HURDAT2 landfall winds** + the STORM RP curve.
