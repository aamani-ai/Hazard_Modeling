# Hurricane Source-Selection Pressure Test

**Status:** discussion note, previewing the `hurricane` branch. This records the deeper source-choice reasoning that
should sit between the Drive references and the M0/M1 notebooks. The hurricane branch plans and notebooks remain the
authority until that branch lands on main.

The hurricane peril modeled here is **tropical-cyclone wind**:

```text
hurricane wind
  magnitude: peak 3-second gust at the asset/cell
  coupling: field-intensity
  event object: storm-resolved tropical-cyclone track
```

Storm surge and tropical-cyclone rainfall are not ignored. They are handled as flood sub-perils and joined back by
`event_family_id`.

## What M1 Needs

Hurricane M1 needs a storm-resolved wind catalog:

```text
storm_id / event_family_id
track + structure
peak 3-s gust at asset/cell
physical annual frequency
tail validation
```

No single public source gives all of that cleanly, so the V1 branch deliberately splits roles:

```text
RAFT synthetic TC catalog
  -> storm-resolved severity shape and event identity

HURDAT2 observed best track
  -> physical close-passage / landfall frequency anchor

ASCE 7-22 wind surface
  -> independent return-period tail validation

SLOSH / TC rainfall sources
  -> flood, not hurricane-wind M1
```

## Candidate Pressure Test

| Candidate | What it provides | Pass/fail against M1 object | V1 / branch role |
|---|---|---|---|
| **RAFT North Atlantic synthetic TC catalog** | Storm-resolved synthetic tracks, intensity, pressure, radius fields, event identity. | **Pass for severity shape and event identity.** Fails raw-frequency test because the catalog intentionally oversamples genesis. | Selected wind severity / storm-object spine. |
| **HURDAT2 observed Atlantic best track** | Observed historical tracks, landfalls, intensities, long record. | **Pass for observed rate anchor.** Too sparse alone for stable site-tail severity. | Frequency anchor and validation target. |
| **ASCE 7-22 wind surface** | Pre-integrated return-period gust surface. | Passes independent tail-validation test, but fails event-object test. | Tail sanity check, not runtime storm catalog. |
| **STORM/RP grid products** | Precomputed return-period tropical-cyclone wind fields. | Useful benchmark, but no event identity for wind/surge/rain joins. | Deferred/validation source. |
| **NOAA SLOSH / storm-surge products** | Surge envelopes/fields. | Correct source family for surge, but not wind. | Flood coastal input, joined by `event_family_id`. |
| **TC rainfall products** | Rainfall fields/accumulations. | Correct source family for TC rain, but not wind; data volume and flood ownership matter. | Flood pluvial/TC-rain deferred slice. |
| **Hazus / FEMA NRI / commercial risk products** | Loss/risk indexes or vendor-modeled risk. | Fails physical-source test if hazard, exposure, vulnerability, and loss are already mixed. | Benchmark only after provenance review. |

## Decision Logic

### Why RAFT is the build source, but not the raw rate

Hurricane requires an event object, not only a return-period surface:

```text
RAFT storm
  |
  | track + vmax + pressure + radius
  v
Holland wind field
  |
  | sample at site/cell
  v
peak 3-s gust per storm
  |
  v
storm_id / event_family_id preserved for M4 joins
```

That event identity is the decisive advantage. It lets one tropical cyclone carry wind, surge, and rainfall without
counting the same storm multiple times.

The caveat is also decisive: the branch M0 notebook finds that RAFT's raw genesis count is a deliberate oversample
relative to observed climatology. So RAFT supplies the conditional severity/geometry, while observed frequency is
anchored with HURDAT2.

### Why HURDAT2 anchors frequency

HURDAT2 is the observed record. The branch uses it to anchor the physical close-passage / landfall rate and to check
landfall intensity behavior:

```text
HURDAT2 observed best track
  |
  | landfall / close-passage rule
  v
observed lambda
  |
  | calibrates RAFT storm sample
  v
physical annual hurricane-wind catalog
```

HURDAT2 alone is not enough for the full severity object. A single site has too little observed tail evidence for a
stable deep wind-field distribution, which is why RAFT remains the severity spine.

### Why ASCE validates instead of replacing the event catalog

ASCE is a useful independent tail check:

```text
ASCE return-period gust
  -> compare modeled hurricane gust tail
  -> catch silent low/high bias
```

But ASCE is not storm-resolved. It cannot tell us which storm caused wind, surge, and rain. If ASCE were the runtime
source, we would lose the event-family key that flood needs.

## Caveat Ledger

| Caveat | Why it matters | V1 / branch treatment | Revisit trigger |
|---|---|---|---|
| RAFT raw rate is an oversample. | Raw synthetic storm counts would overstate annual frequency. | Use RAFT for severity shape; calibrate physical lambda to HURDAT2. | New public stochastic catalog with validated physical rate. |
| RAFT units are easy to misuse. | `vmax` is knots / sustained wind, not mph and not 3-s gust. | Explicit unit conversion and gust-factor discipline in M1. | Schema/unit contract in production code. |
| HURDAT2 intensities are operational estimates across a long record. | Observation practices changed over time. | Use as frequency anchor and validation target, not sole deep-tail severity source. | Reanalysis/homogenized TC record or climate-adjusted frequency model. |
| ASCE has no event identity. | It cannot join hurricane wind to the same storm's surge/rainfall. | Use for tail validation only. | Screening mode that intentionally sacrifices event-family joins. |
| Surge/rain are flood-owned. | Putting them under hurricane wind would double-count flood damage or blur ownership. | Preserve `event_family_id`; flood owns inundation damage. | Unified TC wind + surge + rain event loop. |
| Tail metrics are sensitive to catalog size and validation range. | 1-in-1000+ metrics can exceed the directly validated range. | Carry branch validation summary and flag deep-tail extrapolation. | Larger accepted synthetic sample or external RP benchmark. |

## Surprising Findings / Watchlist

These findings are deliberately framed as pressure-test outputs, not as a defense of the branch implementation.

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| RAFT is the storm-object spine but not the rate spine. | Event identity and severity shape are useful, but raw synthetic counts cannot become lambda. | Public stochastic TC catalog with validated physical annual rates. |
| ASCE is not enough even if its tail matches. | Return-period gust has no storm identity, so it breaks flood wind/surge/rain joins. | A screening-only deployment or an event-resolved RP source. |
| HURDAT2 is the observed anchor but too sparse for deep site severity. | Frequency and severity roles must stay separate. | Homogenized/reanalysis record or larger validated synthetic ensemble. |
| Hurricane source selection is partly an aggregation decision. | Wind, surge, and rain can be the same storm; source roles must preserve event identity. | Unified TC wind+surge+rain M4 with explicit ownership. |
| Units are a first-order QA risk. | Sustained knots vs 3-s gust mph can silently move severity and loss. | Production unit contracts and automated manifest checks. |

## Access / Dependency Notes

```text
RAFT:
  Zenodo record / NetCDF track file
  ~150 MB wind/track file in branch notes
  raw cached locally, derived storm summaries persisted

HURDAT2:
  NOAA/NHC public fixed-format text
  small download
  derived landfall / close-passage summaries persisted

ASCE:
  return-period gust surface
  validation read, not event catalog

SLOSH / rainfall:
  flood-owned source products
  joined by event_family_id, not duplicated under hurricane wind
```

The operational dependency is manageable because the selected wind source is storm-resolved but not massive. The
larger deferred volume is TC rainfall, which correctly belongs to the flood pluvial/TC-rain discussion rather than
the hurricane-wind M1 spine.

## What Should Graduate To `docs/hazards/hurricane/source_selection.md`

The high-level source-selection page should carry:

- the role split: RAFT severity, HURDAT2 frequency, ASCE validation;
- the explicit non-decision: surge/rain belong to flood;
- one pressure-test table;
- caveat ledger;
- branch notebook links and this discussion link.

It should not duplicate the full branch notebooks or restate every storm-field conversion detail.

## Deep References

Local / branch:

- Hurricane source page: [`../../../hazards/hurricane/source_selection.md`](../../../hazards/hurricane/source_selection.md).
- Hurricane branch notebooks: <https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/Notebooks/hurricane>
- RAFT M0 branch notebook: <https://github.com/aamani-ai/Hazard_Modeling/blob/hurricane/Notebooks/hurricane/m0_input_data/01_raft_catalog.py>
- HURDAT2 M0 branch notebook: <https://github.com/aamani-ai/Hazard_Modeling/blob/hurricane/Notebooks/hurricane/m0_input_data/02_landfall_record.py>
- Hurricane branch plans: <https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/docs/plans/hurricane>

Primary/source anchors:

- RAFT Zenodo record: <https://zenodo.org/records/10392723>
- NOAA/NHC HURDAT2 data: <https://www.nhc.noaa.gov/data/#hurdat>
- ASCE Hazard Tool: <https://www.ascehazardtool.org/>
- NOAA SLOSH overview: <https://www.nhc.noaa.gov/surge/slosh.php>
