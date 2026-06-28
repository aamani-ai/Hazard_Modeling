# Hurricane Source Selection — Branch Preview

This page records the source-selection logic for the hurricane wind peril as summarized from the `hurricane`
branch. It is a preview on main until that branch lands.

**Status:** preview from the `hurricane` branch · written 2026-06-26 · **Applies to:** hurricane wind M0/M1
source selection for solar and wind-farm cells. Surge and rainfall are real tropical-cyclone damage agents, but
they are owned by flood and joined back by `event_family_id`.

---

## Decision In One Screen

Hurricane V1/branch-preview uses different sources for severity, frequency, and validation:

```text
RAFT synthetic TC catalog
  -> storm structure and wind-field severity shape
  -> not raw frequency

HURDAT2 observed record
  -> close-passage / landfall frequency anchor

ASCE 7-22 gust surface
  -> independent return-period validation

SLOSH / rainfall sources
  -> flood coastal / pluvial, not hurricane-wind M1
```

The key choice is:

```text
severity shape from RAFT
frequency from HURDAT2
validation from ASCE
surge/rain routed to flood
```

That prevents RAFT's synthetic over-sampling from leaking into annual rates while preserving the event identity
needed to join hurricane wind with flood surge/rain later.

## Source Roles

| Source | Evidence type | Current role | Why not more? | Revisit trigger |
|---|---|---|---|---|
| **RAFT synthetic TC catalog** | Storm-resolved synthetic North Atlantic tracks and structure. | **Wind severity / physics spine.** Drives Holland wind-field synthesis and event identity. | Not used raw for frequency because synthetic genesis is over-sampled relative to observed climatology. | Larger accepted RAFT subset, branch review changes, or better public stochastic TC catalog. |
| **HURDAT2** | Observed historical tropical-cyclone track record. | **Frequency anchor** for close-passage / landfall rates. | Sparse for site-level tail severity by itself; observed record is not enough to populate deep wind-field severity. | Updated observed record, revised close-passage rule, or regional climate adjustment. |
| **ASCE 7-22 wind surface** | Pre-integrated return-period 3-s gust surface. | Independent validation / tail sanity check. | No storm identity, so it cannot join wind, surge, and rain from the same storm. | If validation fails or ASCE vintage/terrain basis becomes the runtime source for a screening mode. |
| **NOAA SLOSH / flood rainfall sources** | Surge envelope and rainfall/inundation evidence. | Cross-peril inputs owned by flood. | Not hurricane wind; using them here would double-count flood damage. | Unified TC wind + surge + rain event loop with explicit ownership. |
| **Hazus / NRI / commercial hurricane risk products** | Loss/risk or vendor-modeled products. | Deferred benchmark. | They may mix hazard, exposure, vulnerability, and loss. | Loss-side validation or reportable underwriting benchmark after provenance review. |

## Pressure-Test Status And Caveats

**Pressure-test status:** branch-preview. The deeper reasoning lives in
[`discussion/hurricane/01_source_selection_pressure_test.md`](../../extra/discussion/hurricane/01_source_selection_pressure_test.md);
this page carries the compressed decision record.

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| RAFT North Atlantic synthetic TC catalog | Storm-resolved severity shape, track/structure fields, and event identity. | Passes storm-object test: M1 can synthesize per-storm wind fields and preserve `event_family_id`; fails raw-frequency test because the catalog oversamples genesis. | **Selected wind severity / storm-object spine.** | Physical lambda must be calibrated to observed HURDAT2 close-passage / landfall rates. |
| HURDAT2 observed best track | Observed frequency anchor and landfall/close-passage validation. | Passes frequency-anchor test; too sparse alone for a stable site-level deep-tail severity distribution. | **Selected observed-rate anchor.** | Long-record intensity estimates and observing practices vary over time. |
| ASCE 7-22 wind surface | Independent return-period gust benchmark. | Passes validation test; fails event-object test because it has no storm identity for wind/surge/rain joins. | **Tail validation / sanity check.** | Cannot be the storm-resolved runtime catalog unless we intentionally give up event-family joins. |
| STORM / RP-grid products | Precomputed tropical-cyclone return-period wind fields. | Useful benchmark, but not the V1 spine if it does not preserve per-storm identity. | **Deferred benchmark / validation.** | Revisit if a public event-resolved catalog or RP product clears provenance and identity needs. |
| NOAA SLOSH / TC rainfall products | Surge/rainfall evidence from the same tropical cyclones. | Correct source family for inundation, but wrong owner for hurricane-wind M1. | **Flood-owned sources.** | Must be joined by `event_family_id` to avoid double-counting. |
| Hazus / NRI / commercial risk products | Loss/risk benchmarks. | Fails physical-source test when hazard, exposure, vulnerability, and loss are already mixed. | **Benchmark only.** | Only after provenance/licensing review and loss-side validation need. |

### Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| RAFT raw rate is an oversample. | Raw synthetic storm counts would overstate physical annual frequency. | Use RAFT for severity and event identity; calibrate lambda to HURDAT2. | New public stochastic TC catalog with validated physical rates. |
| RAFT/HURDAT2 wind units are easy to misuse. | Fields are sustained winds in knots; damage uses 3-s gust mph. | M0/M1 explicitly convert units and preserve basis in manifests. | Production schema/unit validator. |
| HURDAT2 alone is sparse for site-tail severity. | Deep PMLs need more storm realizations than the observed record provides. | Use HURDAT2 for frequency/validation, RAFT for severity shape. | Longer/reanalysis record or accepted climate-adjusted catalog. |
| ASCE has no event identity. | It cannot join wind to the same storm's surge/rainfall. | Use for tail validation only. | Screening mode where event-family joins are intentionally out of scope. |
| Surge/rain are flood-owned. | Putting inundation inside hurricane wind would double-count or blur ownership. | Preserve `event_family_id`; flood owns coastal/pluvial inundation. | Unified TC wind + surge + rain event loop. |
| Extreme tail still needs careful validation. | 1-in-1000+ metrics may exceed branch validation range. | Carry ASCE validation summary and flag deep-tail uncertainty. | Larger accepted synthetic sample or independent RP benchmark. |

### Surprising Findings / Watchlist

Compact carry-forward findings; full reasoning lives in
[`discussion/hurricane/01_source_selection_pressure_test.md`](../../extra/discussion/hurricane/01_source_selection_pressure_test.md).

- RAFT is the storm-object and severity spine, not the raw frequency source; HURDAT2 anchors physical lambda.
- HURDAT2 is essential but too sparse by itself for stable deep site-tail severity.
- ASCE validates the return-period tail, but it cannot replace the storm-resolved catalog because it has no event
  identity.
- Units and wind basis are first-order QA risks: sustained knots, mph, m/s, and 3-s gust must stay explicit.
- Surge/rain ownership is part of source selection: flood owns inundation and hurricane wind joins by
  `event_family_id`.

## Access And Dependency Profile

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| RAFT synthetic TC catalog | Zenodo RAFT record / branch raw cache. | Public, CC-BY-4.0 per branch notebook. | NetCDF storm-track file; branch notebook records the track file at roughly 150 MB. | M0 must decode units, storm years, intensity, pressure, radius, and oversampling. |
| HURDAT2 | NOAA/NHC public best-track record. | Public. | Observed storm track table. | Frequency anchor; needs close-passage and storm-threshold rules. |
| ASCE 7-22 wind surface | ASCE GIS / ArcGIS-backed return-period gust surface. | Public/accessible web source; terms should be respected and cached artifacts should record provenance. | Return-period 3-s gust surface. | Validation read, not primary storm catalog. |
| SLOSH / rainfall sources | NOAA / flood-branch source paths. | Public/source-dependent. | Surge envelopes, rainfall/flood inputs. | Owned by flood; only joined through shared storm identity. |
| Hazus / NRI / commercial products | FEMA/vendor-specific. | Public or licensed, source-dependent. | Loss/risk products. | Deferred benchmark, not M1 wind input. |

## Source Grain And Runtime Flow

The hurricane source grain is storm-resolved, but rate and severity come from different sources:

```text
severity / physics grain:
  RAFT synthetic storm track
  track + pressure + wind + radius fields
  -> Holland parametric wind field
  -> peak 3-s gust at asset/cell

frequency grain:
  HURDAT2 observed storm track
  close-passage or landfall count rule
  -> observed annual rate lambda

validation grain:
  ASCE 7-22 return-period gust
  -> independent tail check, not event identity
```

Runtime flow:

```text
RAFT synthetic TC catalog
    |
    | selected use:
    |   storm structure and severity shape
    |   event identity / event_family_id
    |   not raw annual frequency
    v
M0 storm decoding
    |
    | units: knots / mph / m/s discipline
    | fields: track, pressure, max wind, radius of max wind
    v
M1 wind-field synthesis
  Holland wind field per storm
  peak 3-s gust at site/cell
    |
    +-----------------------------+
                                  |
HURDAT2 observed record           |
    |                             |
    | close-passage frequency     |
    v                             v
observed lambda anchor       derived hurricane M1 catalog
                              storm_id / event_family_id
                              peak_gust_3s_mph
                              frequency basis
```

ASCE sits beside that path:

```text
ASCE 7-22 return-period gust surface
  -> compare modeled RP gusts
  -> validate that the hurricane hazard tail is not silently low
  -> do not replace the storm-resolved catalog because it has no event_family_id
```

The storage boundary is:

```text
raw/source catalogs:
  RAFT, HURDAT2, ASCE, SLOSH/rainfall sources

derived artifacts to persist:
  decoded storm catalog
  wind-field/gust summaries
  frequency anchor manifest
  ASCE validation summary
  event_family_id mapping for flood joins
```

## Why Not Use One Source For Everything

RAFT is strong where HURDAT2 is weak: storm structure and deep severity. HURDAT2 is strong where RAFT is weak:
observed frequency. ASCE is strong for return-period validation, but it has no storm identity.

```text
using RAFT for raw frequency
  -> overstates rate because the synthetic catalog over-samples genesis

using HURDAT2 alone for severity
  -> too few site-tail events for a stable deep severity shape

using ASCE alone as runtime
  -> loses storm identity and cannot join surge/rain from the same TC
```

## QA/QC Burden

```text
[x] hurricane scope is wind-only; surge/rain routed to flood
[x] RAFT used for severity shape, not raw frequency
[x] HURDAT2 used to anchor observed frequency
[x] Holland field synthesis validated against ASCE return-period gusts
[x] units tracked: knots, mph, m/s, sustained wind, 3-s gust
[x] event_family_id preserved for flood joins
[ ] main-branch decisions/registers land when hurricane branch is merged
[ ] larger catalog / deeper tail extrapolation reviewed for 1-in-1000+ metrics
```

## What This Page Prevents

```text
Mistake 1:
  "Use RAFT's raw synthetic count as lambda."
  -> wrong; RAFT provides severity shape, while HURDAT2 anchors frequency.

Mistake 2:
  "Use ASCE as the whole hurricane model."
  -> incomplete; ASCE validates return-period gusts but has no storm identity.

Mistake 3:
  "Put surge/rain under hurricane because the storm is a hurricane."
  -> wrong for this repo; flood owns inundation, joined by event_family_id.
```

## Deep References

- Hurricane anchor: [`README.md`](README.md).
- Hurricane fundamentals: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Source pressure-test discussion:
  [`01_source_selection_pressure_test.md`](../../extra/discussion/hurricane/01_source_selection_pressure_test.md).
- Hurricane branch code: [`Notebooks/hurricane/`](https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/Notebooks/hurricane).
- Hurricane branch plans: [`docs/plans/hurricane/`](https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/docs/plans/hurricane).
- Flood source selection: [`../flood/source_selection.md`](../flood/source_selection.md).
- Convective-wind source selection: [`../convective_wind/source_selection.md`](../convective_wind/source_selection.md).
