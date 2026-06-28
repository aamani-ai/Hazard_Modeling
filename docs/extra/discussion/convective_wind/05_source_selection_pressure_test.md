# Convective Wind Source-Selection Pressure Test

**Status:** discussion note, V1 source choice already built on main. This is the missing reasoning layer between
the Drive/source references and the M0/M1 notebooks. It is not a plan-of-record; the plan/registers still live under
`docs/plans/convective_wind/`.

Convective wind is one peril with two sub-perils:

```text
convective wind
  |
  +-- strong / straight-line wind [W]  -> broad field / site-conditioned profile
  |
  +-- tornado [T]                      -> narrow path / areal hit-or-miss catalog
```

That fork is the source-selection key. The two sub-perils share the same damage observable, **3-second peak gust**,
but they do not share the same source object.

## What M1 Needs

For each sub-peril, M1 must emit the standard hazard object:

```text
{lambda_per_yr, fano_factor, severity_distribution, magnitude_metric, provenance}
```

But the route to that object differs:

| Sub-peril | M1 needs | Correct source object |
|---|---|---|
| Strong / straight-line wind | Local gust return-level profile: return period -> 3-s gust. | A pre-integrated return-period gust surface. |
| Tornado | Path-event rate, EF/severity mix, path geometry, outbreak dispersion. | A historical path/report catalog with bias handling. |

So the source-selection question is not "which wind dataset is best?" It is:

```text
Can this source provide the object this sub-peril needs,
without mixing in exposure, damage, or loss?
```

## Candidate Pressure Test

| Candidate | What it provides | Pass/fail against M1 object | V1 role |
|---|---|---|---|
| **ASCE 7-22 non-hurricane RP gust surface** | 3-second gust by mean recurrence interval, sampled at a location/cell. | **Pass for strong wind.** It is already the return-level curve M1 needs. | Selected strong-wind spine. |
| **SPC severe-wind reports** | Observed/estimated convective wind reports, often point-level, often damage-estimated. | Fails as V1 strong-wind spine. Counts are reporting-biased and gusts are not a clean homogeneous measured record. | Cross-check / future extraction path only. |
| **SPC SVRGIS tornado tracks** | Tornado path geometry, EF/F rating, date/location, path length/width. | **Pass for tornado, with QA.** It supplies the path object M2 needs and the rate/severity evidence M1 needs. | Selected tornado spine. |
| **NOAA Storm Events** | Event/report context, episode grouping, magnitude type, damage notes. | Support source. Useful for bias and report-quality context, but not enough alone for path-aware tornado M1. | Validation and bias support. |
| **ASCE 7-22 Chapter 32 tornado maps** | Tornado design speeds by return period/effective area/risk category. | Useful check, but fails as catalog spine: no event identity, no historical path distribution, no EF mix. | Cross-check only. |
| **FEMA NRI / loss-index products** | County/tract risk or loss-index products. | Fails physical-source test because hazard, exposure, vulnerability, and loss are already mixed. | External sanity check only. |
| **Hurricane / tropical cyclone wind catalogs** | Tropical-cyclone wind fields and tracks. | Fails scope test. Same gust observable, different storm physics and event family. | Separate hurricane peril. |

## Decision Logic

### Strong wind: read the profile, do not fit raw reports

Strong wind behaves like the wildfire/FSim source pattern:

```text
ASCE 7-22 return-period gust surface
  |
  | sample site or grid cell
  v
return period -> 3-s gust
  |
  | M1 profile assembly
  v
lambda + severity distribution
```

The important point is that ASCE is **pre-integrated**. We are not observing individual storms and fitting the tail
ourselves. ASCE/NIST have already turned wind-climatology evidence into a return-period surface. That makes it a
good V1 spine for strong wind, provided we carry its assumptions honestly.

SPC severe-wind reports are real evidence, but they are not a better V1 spine. A raw severe-wind report count is not
a stable annual rate because reporting density, measured-vs-estimated gusts, station height/exposure, and damage-only
reports all affect the record. Using those reports as the primary strong-wind rate would create a large homogenization
project before we even reach M1.

### Tornado: use SPC/NOAA, but never raw-count it naively

Tornado behaves like the hail/MRMS event-catalog pattern:

```text
SPC tornado tracks + NOAA/SPC report context
  |
  | QA: rating era, weak-event detection, rural-low EF, unknown ratings
  v
bias-aware regional path catalog
  |
  | M1
  v
lambda_collection + EF/severity mix + path geometry + dispersion
  |
  | M2
  v
path-aware hit probability / swept fraction at the asset
```

Tornado cannot be represented by a location-only gust curve, because the event object is a narrow path. The path
geometry is not a detail; it is the thing M2 needs to answer "does the tornado hit this farm?"

The caveat is equally important: SPC/NOAA is selected as the spine, but the raw record is not treated as truth.
Weak tornado detection improved over time, the F-scale to EF-scale seam matters, and EF is damage-inferred, which
can underrate rural/open-land tornadoes. That is why the notebooks use a detection-stable window and robustness
checks instead of fitting every historical count blindly.

## Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| ASCE is pre-integrated. | We inherit upstream EVT, exposure, terrain, and vintage choices. | Read the return-level curve and mark strong-wind `fano = 1` as structural. | Public stochastic convective-wind event catalog or better measured site gust record. |
| ASCE basis is 3-s gust at 33 ft / 10 m, Exposure C. | Turbine hub height, local terrain, and asset fragility basis differ. | Use ASCE as meteorological hazard; hub-height/fragility assumptions stay in M2/M3. | Site-specific terrain/exposure correction or hub-height gust evidence. |
| SPC tornado record is detection-biased. | Weak-event counts are not stationary across the full record. | Bias-aware stable-window fit plus EF2+ cross-check. | Homogenized tornado catalog. |
| EF rating is damage-inferred. | Rural/open-land tornadoes can be underrated because damage indicators are sparse. | Carry rural-low caveat and do not over-claim the violent-tail fit. | Reconstructed/measured tornado wind-field dataset. |
| Strong-wind structural damage to turbines is near-zero in V1. | The material operational effect may be curtailment, fatigue, or BI, not physical replacement loss. | Physical-damage track only; performance/disruption deferred. | Performance-tier degradation/BI track. |
| Tornado and strong-wind streams are treated as disjoint data products. | Aggregation assumes ASCE non-hurricane wind and SPC tornado path catalog do not double-count one stream. | Combine as separate sub-peril streams; watch hurricane/TC tornado overlap separately. | Unified convective/hurricane event-family catalog. |

## Surprising Findings / Watchlist

These are not evidence that the current implementation is automatically right. They are the pressure-test findings
that could change source roles if better evidence appears.

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| Same damage observable does not imply same source. | Strong wind and tornado both use 3-s gust, but one is a return-period field and the other is a path-event catalog. | Unified event-resolved convective-wind product with broad-field gusts and tornado paths. |
| ASCE wins strong wind because it already solved the return-level problem. | Re-fitting raw severe-wind reports would add bias work without clearly improving V1. | Homogeneous measured gust catalog with exposure/height controls and stable annual denominator. |
| Tornado needs SPC path geometry even though SPC is biased. | A biased path catalog is still closer to the M2 object than a no-path return-period map. | Reconstructed tornado wind-field/path catalog with reduced rural-low EF bias. |
| Strong-wind loss may live outside physical damage. | A good physical-damage source choice may still miss curtailment, fatigue, and BI. | Operational/performance loss scope enters M3/M4. |

## Access / Dependency Notes

```text
ASCE strong wind:
  ASCE Hazard Tool / ArcGIS-backed service
  small site/cell profile reads
  cache extracted profiles and provenance, not the whole service

SPC/NOAA tornado:
  public track/report archives
  moderate geospatial/event-table processing
  persist cleaned path catalog + bias-window summaries
```

This is a low-storage source strategy. The expensive part is not raw volume; it is **interpretation quality**:
getting units, event basis, report bias, and path geometry right.

## What Should Graduate To `docs/hazards/convective_wind/source_selection.md`

The high-level source-selection page should carry only:

- selected V1 spine per sub-peril;
- one pressure-test table;
- caveat ledger;
- access/dependency summary;
- link back to this discussion for the deeper reasoning.

It should not duplicate all notebook details or the whole assumptions register.

## Deep References

Local:

- Convective-wind source page: [`../../../hazards/convective_wind/source_selection.md`](../../../hazards/convective_wind/source_selection.md).
- ASCE M0 notebook: [`../../../../Notebooks/convective_wind/m0_input_data/01_asce_hazard.py`](../../../../Notebooks/convective_wind/m0_input_data/01_asce_hazard.py).
- SPC/NOAA M0 notebook: [`../../../../Notebooks/convective_wind/m0_input_data/02_spc_storm_record.py`](../../../../Notebooks/convective_wind/m0_input_data/02_spc_storm_record.py).
- M1 catalog notebook: [`../../../../Notebooks/convective_wind/m1_catalog/01_catalog.py`](../../../../Notebooks/convective_wind/m1_catalog/01_catalog.py).
- Assumptions: [`../../../plans/convective_wind/assumptions.md`](../../../plans/convective_wind/assumptions.md).

Primary/source anchors:

- ASCE Hazard Tool: <https://www.ascehazardtool.org/>
- SPC SVRGIS: <https://www.spc.noaa.gov/gis/svrgis/>
- NOAA Storm Events bulk data: <https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/>
