# Hail Source Selection — V1

This page records the source-selection decision between the broad reference universe and the hail M0/M1
notebooks.

It answers the recurring question:

```text
Why is MRMS the V1 spine, and why are NOAA reports not the primary source?
```

**Status:** decided for V1 · written 2026-06-26 · **Applies to:** hail M0/M1 for both the deep per-asset run
and the CONUS grid. Asset-specific coupling and damage still live in the per-asset pages and notebooks.

---

## Decision In One Screen

Hail V1 uses **MRMS daily MESH** as the gridded hazard evidence spine.

```text
MRMS daily MESH
  -> severe-hail days / cell-days
  -> footprint or severe-area evidence
  -> observed MESH severity summaries
  -> M1 hail catalog / hazard layer
```

Other sources are still important, but they do not play the same role:

| Source | V1 role | V1 non-role |
|---|---|---|
| **MRMS daily MESH** | Primary gridded spine for occurrence, footprint/severe-area evidence, and observed MESH severity. | Not assumed to be unbiased true hail size. |
| **NOAA Storm Events / SPC** | Report-side validation, date context, calibration evidence, future bias-corrected rate extension. | Not raw grid truth, not footprint source, not exact-cell frequency by itself. |
| **MYRORSS** | Deferred gridded radar extension and source-qualification track. | Not promoted into V1 frequency/severity until homogeneity and denominator gates are passed. |
| **Murillo & Homeyer / hail climatology** | Bias-correction reference and broad spatial sanity check. | Not a downloadable cell-level V1 field; not a full size distribution. |
| **Das & Allen / EVT hail-size work** | Future tail-method reference or tail input if public data is confirmed. | Not a V1 occurrence source or full conditional size distribution. |
| **FEMA NRI** | Downstream coarse EAL/risk-pattern sanity check. | Not M1 hazard, not size distribution, not direct loss input. |
| **GridRad-Severe** | Research-grade radar input candidate. | Not V1 because it is an event-subset/raw-volume source, not an unbiased annual frequency field. |

The short version:

```text
MRMS owns the gridded physical evidence.
NOAA validates and calibrates; it does not supply the V1 spine.
MYRORSS extends the radar record later, after source qualification.
```

## What Hail M0/M1 Needs

Hail M1 needs more than "some hail data." It needs several different objects:

```text
1. Frequency
   how many severe hail events / days occur per year?

2. Spatial footprint or severe-area evidence
   where did the severe hail field exist?

3. Conditional severity
   how large was the hail, conditional on a severe event?

4. Denominator
   which days / cells / regions were actually observed?

5. Validation route
   how do we know the gridded evidence is plausible?
```

No public source gives all five perfectly. The decision is therefore not "pick the best dataset overall."
The decision is:

```text
which source serves which model component?
```

This is the same rule captured in [`LL04`](../../learning_logs/04_two_datasets_one_peril_decompose.md).

## Why MRMS Is The V1 Spine

MRMS MESH is not perfect, but it is the only V1 source that gives the essential physical object: a gridded
hail-size field.

MRMS gives:

- **spatial completeness** over the served domain;
- **native grid evidence** rather than point reports;
- **footprints / severe-area evidence** after thresholding;
- **a consistent source denominator** once the accepted source-date inventory is frozen;
- **a direct MESH severity field** for observed-body summaries;
- **the same evidence type** for deep per-asset and CONUS-grid deployments.

The accepted V1 grid denominator is documented in the MRMS grid build notes:

```text
accepted source dates: 2,071
continuous window: 2020-10-14 through 2026-06-15
served CONUS cells: 13,085
```

MRMS's weakness is also explicit: MESH is a radar estimate, not true ground hail size. It can over-predict
size and produce physically implausible raw extremes. That makes MRMS **high-QA**, not unusable.

The V1 treatment is:

```text
frequency:
  use severe-hail day / cell-day flags.

severity:
  preserve raw MESH for audit,
  flag/cap implausible tails for modeling,
  label deep-tail loss metrics as provisional until de-biasing / EVT lands.
```

## Why NOAA Is Not The Primary V1 Source

NOAA Storm Events / SPC reports are valuable, but they are the wrong object for the primary M1 spine.

They are **point reports**:

```text
report at lat/lon/time/size
```

They are not:

```text
gridded severe-hail footprints
observed no-hail denominators
complete spatial fields
```

The blocking issues are:

| Need | Why raw NOAA cannot satisfy it |
|---|---|
| Footprint / severe area | NOAA is points. It cannot produce the event footprint `F` needed by hail's areal coupling. |
| Exact cell frequency | Reports depend on people, roads, population, report practices, and time. A quiet cell can mean no hail or no report. |
| Homogeneous rate | Reporting practice changes over time, so a long raw report record is not automatically a clean rate record. |
| Source splice | Naively joining NOAA pre-MRMS with MRMS-era radar creates a source-regime jump in `lambda`, not a real climate signal. |

So NOAA's V1 role is validation/calibration:

```text
MRMS says: the radar field had severe hail here.
NOAA asks: did people report hail nearby, and what size did they report?
```

NOAA can become more important later through a **calibrated extension**, where the MRMS/NOAA overlap is used
to learn reporting bias before extending rate history. Raw NOAA is not promoted directly.

## The Main Tradeoff

The V1 choice accepts this tradeoff:

```text
shorter but spatially complete gridded radar spine
    beats
longer but population-biased point-report spine
```

That is why the project uses MRMS even though MRMS needs serious QC. The alternative is not "clean NOAA";
the alternative is a long, biased, non-footprint source that cannot drive the spatial math.

## Candidate Assessment

| Candidate | Evidence type | Strength | Blocking limitation | V1 disposition |
|---|---|---|---|---|
| MRMS MESH | Daily gridded radar-estimated hail size. | Best public V1 spine: gridded, spatially complete, footprint-capable. | Raw MESH is biased/noisy for true size; short accepted V1 record. | **Selected spine.** |
| NOAA Storm Events / SPC | Point reports with date/location/size. | Long record; human-observed size evidence. | Population/reporting bias; no footprints; no observed-zero denominator. | **Validation/calibration only.** |
| MYRORSS | Older gridded radar reanalysis. | Extends radar-like record before operational MRMS. | Needs source qualification, cross-era homogeneity check, and gap handling. | **Deferred V1.5/V2 candidate.** |
| Murillo & Homeyer / hail climatology | Bias-corrected hail climatology and MESH methods. | Strong science reference for MESH bias and spatial sanity. | Coarser/smoothed, not a full downloadable V1 size distribution. | **Bias/QC anchor.** |
| Das & Allen / EVT hail-size work | Hail-size return-likelihood / tail model. | Useful tail methodology, possibly exact grid. | Tail-only; occurrence not supplied; public data access unconfirmed. | **Tail reference / future candidate.** |
| FEMA NRI | County/tract risk index and annualized frequency/loss fields. | Useful external pattern check. | Mixes hazard, exposure, and loss ratio; no physical size distribution. | **Downstream cross-check only.** |
| GridRad-Severe | Event-based radar volumes. | High-quality severe-storm research input. | Event-subset/raw volumes; not continuous annual denominator or ready M1. | **Research input, not V1.** |

## Pressure-Test Status And Caveats

**Pressure-test status:** strong for V1 on main. The detailed reasoning lives in the hail source research and
triage notes, especially
[`00_m1_data_products_research.md`](../../extra/discussion/conus_grid/hail/00_m1_data_products_research.md),
[`01_m1_sourcing_triage.md`](../../extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md), and
[`03_mrms_tail_qa_and_m1_policy.md`](../../extra/discussion/conus_grid/hail/03_mrms_tail_qa_and_m1_policy.md).

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| MRMS daily MESH | Gridded hail-size field, severe-area evidence, source denominator. | Passes the physical-object test: it gives spatial footprints / cell-days, not just reports. Also public and reproducible. | **Selected spine.** | Radar-estimated size is biased/noisy; raw severe-tail magnitude is provisional. |
| NOAA Storm Events / SPC | Long observed report record and human size reports. | Fails the primary-spine test: point reports do not provide footprints, observed-zero denominator, or population-bias-free frequency. | **Validation/calibration only.** | Report bias must be modeled before using for rate extension. |
| MYRORSS | Longer radar-like gridded history. | Promising but not yet homogeneous with operational MRMS; needs source qualification and cross-era gap checks. | **Deferred V1.5/V2 extension.** | Cannot be spliced directly into MRMS rates. |
| Murillo & Homeyer / hail climatology | Bias-correction recipe and spatial climatology sanity. | Useful as method/validation anchor, but not a complete cell-level event-frequency and size-distribution feed. | **Bias/QC anchor.** | De-biasing not implemented in V1 outputs. |
| Das & Allen / EVT tail work | Hail-size tail / return-likelihood method. | Tail-only and public data access not yet confirmed. | **Future tail candidate.** | Deep PML remains provisional until tail method/data are integrated. |
| FEMA NRI / loss-index products | Coarse external risk pattern. | Fails M1 source test because it already mixes hazard, exposure, vulnerability, and loss. | **Downstream cross-check only.** | Not usable as physical frequency/severity input. |

### Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| MRMS MESH is not true hailstone size. | Raw size affects M3 severity and tail loss. | Preserve raw MESH for audit; flag/cap implausible tails; label severity-tail outputs provisional. | Murillo/Homeyer-style de-biasing or validated gridded hail-size tail. |
| Accepted MRMS record is short and operational-era only. | Frequency and dispersion are record-limited. | Freeze accepted source-date denominator; report V1 as current-operational-era screening. | Homogeneous MYRORSS extension or calibrated NOAA extension. |
| NOAA reports are population/reporting biased. | Raw reports can overstate populated corridors and understate rural cells. | Use as validation/calibration context, not as direct M1 event footprint or rate. | Bias model built against MRMS/report overlap. |
| Cell/grid severity can be sparse. | Per-cell tails can be unstable even when national maps look smooth. | Poisson grid default plus sparse-cell labels; deep tail not reportable without further QA. | Pooling / hierarchical grid model or longer homogeneous record. |
| Daily grain collapses sub-daily storm structure. | Multiple storms in one day can be merged. | V1 event unit is hail-day / cell-day because the selected product is 24h max MESH. | Sub-daily product and storm-splitting workflow. |

### Surprising Findings / Watchlist

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| The best V1 source is the shorter gridded radar record, not the longer report record. | The model needs footprints/cell-days and an observed denominator; point reports cannot supply that directly. | A calibrated NOAA/report extension that proves stable rate and footprint reconstruction against MRMS overlap. |
| MRMS is selected even though MESH is biased for true hail size. | Frequency/footprint evidence is strong, while severity-tail confidence is weaker. | A validated MESH de-biasing layer or public gridded hail-size tail product. |
| MYRORSS is the most important future challenger, not NOAA raw reports. | It could extend the radar-like denominator backward if source homogeneity is proven. | Cross-era QA showing MYRORSS and MRMS can be joined without a false rate/severity jump. |
| Daily max grain is a modeling choice, not a physical storm definition. | It makes the grid tractable but merges sub-daily storm structure. | A sub-daily storm-splitting workflow with manageable storage/compute and improved loss relevance. |

## Access And Dependency Profile

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| MRMS MESH | NOAA MRMS public cloud bucket / archive path for `CONUS/MESH_Max_1440min_00.50`. | Public, no auth. | Daily gridded GRIB2 tiles; large enough to need inventory, caching, and batch processing. | Heavy but reproducible batch scan; V1 freezes accepted source-date denominator. |
| NOAA Storm Events / SPC | NCEI/SPC public report tables or API/bulk CSV pulls. | Public, no auth for normal use. | Tidy point/report tables; lightweight compared with MRMS. | Direct download/API; validation/calibration dependency only. |
| MYRORSS | NOAA OAR MYRORSS public AWS bucket. | Public, no auth. | Older gridded radar/reanalysis files; large, raw, source-qualification required. | Deferred batch extension; needs homogeneity and gap checks before promotion. |
| Murillo & Homeyer / hail climatology | Published paper/method; derived fields are not treated as a direct V1 download. | Public literature; gridded fields may require author request. | Coarser/smoothed climatology and bias-correction recipe. | Literature/method dependency, not an operational V1 data feed. |
| Das & Allen / EVT hail-size work | Published paper; data availability must be confirmed before use. | Public paper; gridded data access unconfirmed. | Tail/return-likelihood product, not full event body. | Future tail-method candidate; no V1 runtime dependency. |
| FEMA NRI | OpenFEMA / FEMA downloads. | Public. | County/tract/fishnet-style risk-index tables/geospatial products. | Optional downstream cross-check, not M1 dependency. |
| GridRad-Severe | NSF NCAR RDA/GDEX download. | Public/free, registration typical. | NetCDF event radar volumes; event subset, large. | Research input only; not V1 operational spine. |

The access decision is part of why MRMS wins V1: it is precomputed, public, gridded, and reproducible from a
cloud bucket even though the processing burden is large. NOAA is much easier to download, but it does not
provide the spatial object the model needs.

## MRMS Product Grain And Grid Scaleout

The V1 source is not "all MRMS." It is one narrow MRMS product slice:

```text
source family:
  NOAA MRMS public data

bucket:
  s3://noaa-mrms-pds   (anonymous/public)

selected product path:
  CONUS/MESH_Max_1440min_00.50

selected variable:
  MESH = Maximum Estimated Size of Hail, in mm

temporal grain:
  MESH_Max_1440min = running maximum over 1440 minutes = 24 hours
  many rolling tiles can exist per day
  V1 selects one daily representative tile per accepted date

spatial grain:
  native MRMS grid is about 1 km / 0.01 degree
  grid product aggregates native pixels into 0.25 degree benchmark cells
```

Interpretation:

```text
MESH_Max_1440min tile
  ~= "for each ~1 km patch, what is the largest radar-estimated hail size seen in the last 24 hours?"
```

That product grain is the scalability decision. We do **not** ingest the full MRMS archive, all MRMS variables,
all sub-hourly updates, or raw radar volumes. For V1 hail, those would add volume without changing the event
unit we chose: a severe hail-day / severe cell-day.

Scale note:

```text
full MRMS family / sub-hourly archive:
  very large; many products and many updates per day

our selected slice:
  one MESH_Max_1440min product
  one selected daily representative tile per accepted date
  GB-scale selected source slice over the V1 window, not the full MRMS archive
```

```text
AWS public source bucket
  s3://noaa-mrms-pds
    |
    | selected product only:
    | CONUS/MESH_Max_1440min_00.50/<YYYYMMDD>/...
    |   - daily 24h max MESH
    |   - many rolling source files can exist per day
    |   - one selected tile per accepted date
    |   - raw source remains in NOAA/AWS; we do not mirror it
    v
Cloud Run task-indexed fanout
  148 tasks over 2,071 accepted dates
    |
    | each task:
    |   fetch selected tiles
    |   read GRIB2
    |   aggregate ~1 km native pixels into 0.25 degree cells
    |   write compact M0 partition
    v
derived hazard artifacts
  M0 reconciled cell-day evidence: 27,099,035 rows
  M1 hazard layer: 13,085 served CONUS cells
  M2-M4 grid loss layer: 13,085 cells x policy variants (about 26k rows in the current two-policy run)
```

The tractability comes from three decisions:

1. **Product selection.** We choose daily-max MESH, not every MRMS product or every sub-hourly update. This is
   the biggest volume reduction.
2. **Read from source, do not mirror raw.** NOAA/AWS is the raw source of truth. Raw tiles can be cached during
   processing, but they are not a canonical platform artifact.
3. **Reduce at ingest.** The heavy M0 step immediately turns native pixels into 0.25 degree cell-day evidence.
   The objects we keep are compact enough for M1/M2/M3/M4 to run locally or in ordinary batch jobs.

The tradeoff is explicit: this reduction discards sub-cell and sub-daily detail. If a later version needs
sub-daily storm splitting, finer cells, or a different MRMS product, we should re-fetch and reprocess from the
public source rather than pre-store the full raw archive.

The durable product we keep is the compact derived evidence: cell-day rows, M1 cell summaries, manifests, and
QA outputs.

This is why the same selected source supports both use cases:

| Use case | What changes | What stays the same |
|---|---|---|
| Deep asset analysis | Read selected daily MESH tiles around one asset window/region, then build site-specific hail-day events. | Same MRMS product, same severe threshold, same daily grain. |
| CONUS grid map | Read selected daily MESH tiles for all served CONUS cells through a batch fanout, then aggregate to 0.25 degree cell-days. | Same MRMS product, same severe threshold, same daily grain. |

The product choice makes the grid possible: enough spatial structure for footprint/cell evidence, but not the
multi-product, sub-hourly, multi-TB radar archive.

## Current V1 Implementation Meaning

The same source decision supports both deployments, but the spatial bucket changes.

| Deployment | MRMS bucket | Event/count unit | Frequency model |
|---|---|---|---|
| Deep per-asset run | 50-mile region around the asset. | Severe hail-day footprint events. | Negative Binomial where annual counts support dispersion. |
| CONUS grid | One 0.25 degree benchmark cell. | Severe hail cell-day evidence. | Poisson V1 default; dispersion diagnostics, no sparse-cell overfit. |

The source choice does not mean the spatial math is the same. It means the evidence spine is the same:

```text
MRMS field -> severe hail evidence -> M1 object
```

## QA/QC Gates

MRMS can drive V1 only with explicit gates:

```text
[x] source inventory defines accepted source-date denominator
[x] no-data is separated from observed zero / sub-severe hail
[x] severe threshold is fixed at MESH >= 25.4 mm
[x] raw MESH severity is preserved for audit
[x] implausible MESH tails are flagged/capped for modeling
[x] NOAA reports are used as validation/context, not event additions
[ ] MYRORSS promotion requires source qualification + homogeneity checks
[ ] de-biased MESH / EVT severity tail remains V1.5/V2
```

## What This Page Prevents

The page should stop three common mistakes:

```text
Mistake 1:
  "NOAA has a longer record, so use NOAA."
  -> wrong, because long biased points do not supply footprints or observed-zero denominators.

Mistake 2:
  "MRMS has bad extreme sizes, so reject MRMS."
  -> wrong, because MRMS is still the best gridded occurrence/footprint spine; severity needs QC.

Mistake 3:
  "NRI has hail EAL, so use it as hazard input."
  -> wrong, because NRI is already a risk/loss index, not a physical M1 hazard field.
```

## Revisit Triggers

Promote or revise the source strategy when:

- MYRORSS source qualification passes and we can document cross-era homogeneity with MRMS;
- a calibrated NOAA extension is built against the MRMS overlap;
- Murillo & Homeyer-style de-biasing is implemented or their fields become available;
- Das & Allen gridded tail data is confirmed public and can be reconciled with our occurrence model;
- V1 loss outputs need reportable 1-in-250+ tail metrics rather than screening/provisional tails.

## Cross-References

- Hail anchor: [`README.md`](README.md).
- Hail fundamentals: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Deep-run decisions: [`plans/hail/decisions.md`](../../plans/hail/decisions.md), especially DD-1 and DD-3.
- Grid V1 plan: [`plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`](../../plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md).
- Hail source research and triage:
  [`00_m1_data_products_research.md`](../../extra/discussion/conus_grid/hail/00_m1_data_products_research.md) and
  [`01_m1_sourcing_triage.md`](../../extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md).
- MRMS M0/M1 QA policy:
  [`03_mrms_tail_qa_and_m1_policy.md`](../../extra/discussion/conus_grid/hail/03_mrms_tail_qa_and_m1_policy.md).
- Source-onboarding lesson: [`LL03`](../../learning_logs/03_meet_complex_raw_data_from_scratch.md).
- Multi-source lesson: [`LL04`](../../learning_logs/04_two_datasets_one_peril_decompose.md).
- Notebooks:
  [`Notebooks/hail/`](../../../Notebooks/hail/README.md) and
  [`Notebooks/hazard_conus_grid/hail/`](../../../Notebooks/hazard_conus_grid/hail/README.md).
