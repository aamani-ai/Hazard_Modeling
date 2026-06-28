# Convective Wind Source Selection — V1

Convective wind is one peril with two sub-perils. The source-selection decision must be split the same way:

```text
strong / straight-line wind  -> ASCE return-period gust surface
tornado                      -> SPC/NOAA report and track record
```

**Status:** decided for V1 · written 2026-06-26 · **Applies to:** convective-wind M0/M1 for the onshore wind
asset cell and the planned CONUS grid.

---

## Decision In One Screen

| Sub-peril | Selected V1 source | Why |
|---|---|---|
| **Strong / straight-line wind [W]** | **ASCE 7-22 return-period 3-s gust surface** | It is already a pre-integrated engineering EVT surface for local non-tornadic gusts. |
| **Tornado [T]** | **SPC SVRGIS tornado tracks + NOAA Storm Events / SPC records** | It is the public long-record source for tornado paths, EF ratings, and report evidence. |

This is not two arbitrary choices. The two sub-perils have different data shapes:

```text
strong wind:
  a broad local gust hazard profile already fit upstream
  -> read the return-period curve

tornado:
  a narrow path hazard with biased historical reports
  -> bias-correct / fit a path-event catalog
```

## Source Roles

| Source | Evidence type | Current role | Why not more? | Revisit trigger |
|---|---|---|---|---|
| **ASCE 7-22 RP gust surface** | Pre-integrated return-period 3-s gust field. | **Strong-wind V1 spine.** | Non-tornadic design surface; not a tornado path catalog. | If site-specific measured gust data or updated ASCE surfaces materially change the profile. |
| **SPC SVRGIS tornado tracks** | Tornado path/track record with EF information. | **Tornado V1 spine.** | Reporting/detection bias and EF damage-inference bias require correction. | Better homogenized tornado catalog or measured tornado wind-field reconstruction. |
| **NOAA Storm Events / SPC reports** | Point/report evidence for tornado and severe wind. | Validation, bias correction, cross-checks. | Raw reports are population/detection biased; many wind reports are estimates. | Calibrated report model or longer stable window. |
| **FEMA NRI / loss-index products** | County/tract risk/loss index. | External sanity check only. | Already mixes hazard, exposure, and loss; not an M1 physical hazard source. | Validation benchmark after loss outputs exist. |
| **Hurricane / TC wind products** | Track/wind-field hazard. | Deferred separate peril. | Tropical cyclone wind is field-intensity, not inland convective wind. | Hurricane build enters scope. |

## Pressure-Test Status And Caveats

**Pressure-test status:** built on main. The deeper reasoning now lives in
[`discussion/convective_wind/05_source_selection_pressure_test.md`](../../extra/discussion/convective_wind/05_source_selection_pressure_test.md);
this page carries the compressed decision record.

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| ASCE 7-22 non-hurricane RP gust surface | Strong / straight-line wind frequency and severity profile. | Passes the strong-wind M1-object test: the return-period gust curve is already a pre-integrated engineering EVT surface. | **Selected strong-wind spine.** | Borrowed assumptions: ASCE/NIST method, vintage, Exposure C, terrain basis, and deep-tail uncertainty. |
| SPC severe-wind reports as strong-wind spine | Direct observed severe-wind event counts. | Fails V1 spine test for strong wind: reports are biased, sparse, height/exposure-dependent, and often estimated rather than measured. | **Cross-check / future extraction path only.** | Could become useful with a homogenized measured-gust record. |
| SPC SVRGIS tornado tracks | Tornado frequency, path geometry, EF mix, and event dates. | Passes tornado-object test because tornado is a narrow path peril and needs path geometry; fails as raw truth without bias correction. | **Selected tornado spine with high QA.** | Detection bias, F/EF seam, unrated events, and rural-low EF bias remain material. |
| ASCE 7-22 Chapter 32 tornado maps | Tornado design-speed sanity check. | Useful but not enough for V1 tornado catalog: caps around lower tornado design ranges, depends on effective area/risk category, and has no historical path-event frequency/EF mix. | **Cross-check only.** | Not a substitute for violent-tornado tail modeling. |
| NOAA Storm Events | Additional report context for tornado and severe wind. | Useful for validation/bias checks, but point/report data alone does not provide the path geometry and stable denominator needed for M1. | **Validation / bias support.** | Population/reporting bias must be modeled. |
| FEMA NRI / loss-index products | Coarse risk benchmark. | Fails physical-source test because it mixes hazard, exposure, vulnerability, and loss. | **External sanity check only.** | Cannot calibrate physical gust frequency/severity directly. |
| Hurricane / TC wind catalogs | Field-intensity wind from tropical cyclones. | Fails convective-wind scope test: same 3-s gust observable, but different event physics, footprint, source, and double-count risk. | **Separate peril, not a sub-peril.** | TC-spawned tornado overlap must be guarded when hurricane is combined with tornado. |

### Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| ASCE is pre-integrated. | Dispersion and EVT assumptions are upstream, not fitted/tested by us. | Read the return-level curve; label `fano = 1` structural for strong wind. | Public stochastic convective-wind catalog or better site-specific measured gust record. |
| ASCE basis is 3-s gust at 33 ft / 10 m, Exposure C. | Turbine hub-height and terrain/exposure differ from the map basis. | Treat ASCE as meteorological hazard; turbine fragility/hub-height treatment lives in M2/M3 assumptions. | Site-specific terrain/exposure correction or measured hub-height gust evidence. |
| Strong-wind damage to turbines is near-zero on the structural damage track. | The material impact may be curtailment/fatigue rather than catastrophic damage. | Run damage track honestly; defer disruption/degradation/performance track. | Performance/BI/reliability track is built. |
| SPC tornado record is detection-biased. | Weak tornado counts rose with observation/reporting changes. | Use bias-aware / stable-window fitting and EF2+ cross-checks, not raw all-year counts. | Homogenized tornado catalog or improved detection-bias model. |
| EF rating is damage-inferred and rural-low. | Rural/open-land tornadoes can be underrated, understating severity. | Carry rural-low caveat; severity tail is approximate and likely conservative-low in sparse damage-indicator areas. | Measured/reconstructed tornado wind-field dataset. |
| Tornado and strong-wind streams are treated disjoint. | Additive EAL assumes the ASCE non-tornadic surface and SPC tornado catalog do not double-count the same stream. | Treat disjointness as a V1 data-product assumption; flag hurricane/TC overlap separately. | Evidence of overlap or unified convective/hurricane event catalog. |
| Portfolio correlation deferred. | Broad strong-wind fields and outbreaks can correlate losses across assets. | Single-site V1; no portfolio correlation. | Portfolio M4 / event-family correlation model. |

### Surprising Findings / Watchlist

Compact carry-forward findings; full reasoning lives in
[`discussion/convective_wind/05_source_selection_pressure_test.md`](../../extra/discussion/convective_wind/05_source_selection_pressure_test.md).

- Same observable, different source objects: strong wind uses ASCE return-period gusts; tornado uses SPC path
  geometry.
- ASCE is a profile read, not an observed event catalog; do not infer event dispersion from it.
- SPC is necessary for tornado paths, but raw counts still need detection/rating-era QA.
- TC-spawned tornado overlap remains an aggregation watch item when hurricane is combined with convective wind.

## Access And Dependency Profile

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| ASCE 7-22 RP gust surface | ASCE GIS / ArcGIS-backed return-period surface access. | Public/accessible web source; terms should be respected and cached artifacts should record provenance. | Return-period gust surface, queried/interpolated by site or grid cell. | Lightweight profile read compared with raw-event processing; runtime should cache extracted profiles. |
| SPC SVRGIS tornado tracks | SPC public GIS files / archives. | Public. | Vector tracks and attributes; moderate table/geospatial processing. | Tornado V1 spine; needs bias and rating-era QA. |
| NOAA Storm Events / SPC reports | NCEI/SPC public report tables or bulk downloads. | Public. | Point/report tables; lightweight. | Validation and bias-correction support. |
| FEMA NRI / loss-index products | OpenFEMA / FEMA downloads. | Public. | County/tract risk/loss-index tables/geospatial products. | External check only; not runtime M1. |
| Hurricane / TC wind products | Future hurricane catalog/wind-field sources. | Source-dependent. | Track/catalog/field products. | Deferred separate peril; not an inland-convective V1 dependency. |

The access split mirrors the physics split. Strong wind can be read from a precomputed return-period surface.
Tornado needs public report/track archives and a more careful QA path before fitting frequency and severity.

## Source Grain And Runtime Flow

Convective wind has two source grains because the sub-perils are different physical objects.

```text
strong / straight-line wind:
  selected product: ASCE 7-22 non-hurricane 3-s gust return-period surface
  temporal grain:   return period / annual exceedance probability
  spatial grain:    continuous raster surface, sampled at site or benchmark cell
  runtime role:     read the pre-integrated return-level curve

tornado:
  selected product: SPC SVRGIS / NOAA tornado path and report record
  temporal grain:   historical path events, then a bias-aware rate window
  spatial grain:    path geometry with EF/rating attributes
  runtime role:     build a path-event catalog and thin it to the asset/grid
```

The strong-wind path is a profile read:

```text
ASCE 7-22 ArcGIS-backed hazard surface
    |
    | selected layers:
    |   non-hurricane 3-s gust by return period / MRI
    |   mph at 33 ft / 10 m, Exposure C
    |   tornado Ch. 32 layers are cross-check only
    v
M0 point/cell query
    |
    | deep asset:
    |   query the asset/site location
    |
    | CONUS grid:
    |   query or interpolate each benchmark cell
    v
derived strong-wind profile
  return period -> 3-s gust
    |
    v
M1
  profile-assembly into lambda + continuous gust severity
```

The tornado path is an event-extraction path:

```text
SPC / NOAA public tornado records
    |
    | selected fields:
    |   path geometry, date/time, EF/F rating, length, width
    |   report metadata for bias/rating-era checks
    v
M0 cleanup and source QA
    |
    | apply detection/rating-era rules
    | derive EF mix and path-geometry summaries
    | preserve raw-vs-cleaned provenance
    v
derived tornado M1 catalog
  collection-region lambda
  EF-conditioned path geometry
  bounded gust severity model
    |
    v
M2
  path-aware Minkowski hit probability and swept fraction
```

The storage boundary follows the source shape:

- **ASCE strong wind:** cache the queried profiles / extracted raster samples and provenance, not the whole ASCE
  service.
- **Tornado:** keep the cleaned path-event catalog, rate-window summary, EF/path distributions, and provenance;
  raw public files remain re-fetchable source artifacts.

## Strong Wind: Why ASCE Wins

Strong wind needs a local gust profile, not a raw report count.

ASCE gives:

```text
return period -> 3-s gust at location
```

That is already the object M1 needs for the strong-wind branch. It is the wind analogue of wildfire/FSim:
the upstream product has already done the tail fitting, so our job is to read/interpolate it correctly and
preserve the return-period/AEP frame.

Alternatives such as raw severe-wind reports or station records are not ignored; they are just not better V1
spines. They are biased, sparse, height/exposure-dependent, and would require a full homogenized EVT build.

## Tornado: Why SPC/NOAA Is Necessary But High-QA

Tornado needs path evidence. ASCE does not provide tornado paths. SPC/NOAA gives the public record we can
start from:

```text
tornado reports / tracks
  -> path geometry and EF class
  -> collection-region frequency
  -> bounded gust severity model
```

But this source is high-QA:

- weak tornado detection improved over time;
- the F-scale to EF-scale seam matters;
- EF is damage-inferred, so rural/open-land tornado intensity can be understated;
- unrated tornadoes and report practices affect frequency and severity.

So the source is selected, but the raw record is not treated as truth without bias handling.

## QA/QC Burden

```text
[x] split strong wind and tornado before source selection
[x] strong wind reads ASCE RP curve; no raw-count frequency fit
[x] tornado uses path/report data with bias correction
[x] event threshold and damage-onset threshold remain separate
[x] 3-s gust is the shared observable
[ ] hurricane/TC overlap is deferred and must be guarded later
[ ] portfolio correlation is deferred
```

## What This Page Prevents

```text
Mistake 1:
  "Use one wind dataset for everything."
  -> wrong; tornado and strong wind have different footprint physics and data products.

Mistake 2:
  "Fit strong-wind frequency from raw severe-wind reports."
  -> unnecessary for V1; ASCE already provides the engineering return-period surface.

Mistake 3:
  "Treat EF ratings as measured wind speed."
  -> wrong; EF is damage-inferred and biased by available damage indicators.
```

## Deep References

- Convective-wind anchor: [`README.md`](README.md).
- Convective-wind fundamentals: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Source pressure-test discussion:
  [`05_source_selection_pressure_test.md`](../../extra/discussion/convective_wind/05_source_selection_pressure_test.md).
- M0 ASCE source notebook: [`01_asce_hazard.py`](../../../Notebooks/convective_wind/m0_input_data/01_asce_hazard.py).
- M0 SPC source notebook: [`02_spc_storm_record.py`](../../../Notebooks/convective_wind/m0_input_data/02_spc_storm_record.py).
- M1 catalog notebook: [`01_catalog.py`](../../../Notebooks/convective_wind/m1_catalog/01_catalog.py).
- Decisions: [`plans/convective_wind/decisions.md`](../../plans/convective_wind/decisions.md), especially
  DD-WN-1, DD-WN-3, DD-WN-7, DD-WN-8, and DD-WN-9.
- Assumptions: [`plans/convective_wind/assumptions.md`](../../plans/convective_wind/assumptions.md), especially
  AWN-1, AWN-11, AWN-15, AWN-17, AWN-28, AWN-30, and AWN-31.
- Discussion: [`discussion/convective_wind/`](../../extra/discussion/convective_wind/README.md).
- Lessons: [`LL09`](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) and
  [`LL12`](../../learning_logs/12_evt_for_a_new_peril.md).
- Code: [`Notebooks/convective_wind/`](../../../Notebooks/convective_wind/README.md).
