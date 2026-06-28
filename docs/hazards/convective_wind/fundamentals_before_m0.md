# Convective Wind Fundamentals Before M0

This is the convective-wind prerequisite guide. Read it before the convective-wind layer-0 and M0 notebooks.

Cross-hazard pattern:

```text
physics -> data-source reality -> M0-M4 translation
```

For convective wind:

```text
physics       -> severe convective wind loading, expressed as 3-second peak gust
data reality  -> no single product defines the event; standards and reports are fragmented
pipeline      -> author layer-0 first, then fork M1 into tornado and strong-wind machinery
```

---

## 1. Why Convective Wind Needs Layer-0

Hail inherits its event from MESH. Wildfire inherits frequency/severity from FSim. Convective wind does not
inherit one complete event definition from any source.

Instead, it has partial sources:

```text
ASCE 7-22        -> return-period 3-s gust surface
SPC SVRGIS       -> tornado tracks and severe-wind reports
NOAA Storm Events -> additional report context
EF scale         -> damage-inferred tornado wind bins
IEC 61400        -> turbine design/survival context
```

None of these alone says:

```text
this is the event,
this is the intensity measure,
this is the frequency process,
this is the damage onset.
```

So convective wind needs a layer-0 definition before M0.

---

## 2. The Shared Physical Observable

Both sub-perils use the same damage-relevant intensity measure:

```text
3-second peak gust
```

This is the structural wind metric. It is not the same as:

```text
sustained wind
daily mean wind
resource wind for generation
```

The structural load grows roughly with wind speed squared:

```text
load ~ 0.5 * rho * V^2
```

So the peak gust is the right input for damage.

---

## 3. One Peril, Two Sub-Perils

Convective wind splits because the physics and data differ.

```text
                         3-second peak gust
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
          [T] tornado                     [W] strong wind
          narrow rotating path            broad straight-line field
          rare and violent                common and usually milder
          path hit/miss                   site gust profile
```

Table version:

| Sub-peril | Physical picture | Main data | Coupling picture |
|---|---|---|---|
| Tornado | Narrow rotating vortex/path. | SPC tornado tracks, EF ratings, ASCE tornado context. | Areal hit-or-miss, path-aware. |
| Strong wind | Broad straight-line / derecho / downburst gust field. | ASCE 7-22 return-period gust surface. | Site-conditioned; read local gust profile. |

This is not just naming. The two sub-perils have different frequency, severity, and M2 coupling.

---

## 4. The Two Thresholds

The most important concept is that event threshold and damage-onset threshold are different.

```text
event threshold:
    what the catalog counts

damage-onset threshold:
    where the turbine damage curve leaves zero
```

ASCII:

```text
gust speed

25.9 m/s        29 m/s             52-70 m/s                  113 m/s
 |               |                  |                           |
 v               v                  v                           v
 strong wind     tornado EF0        IEC turbine survival         EF5 ceiling
 event count     event count        damage onset region          physical cap

 |---- M1 event thresholds ----|     |---------- M3 damage ----------|
```

This is why strong wind can be frequent but still produce nearly zero catastrophic turbine damage. Most
"severe wind" events are severe meteorologically, but below the turbine structural damage onset.

---

## 5. Data-Source Reality

### Strong Wind

Strong wind uses the ASCE 7-22 return-period gust surface.

This is a pre-integrated product:

```text
ASCE/NIST wind statistics
    -> 3-s gust by mean recurrence interval / return period
    -> read the site profile
```

So for strong wind, M1 is profile assembly, not raw event extraction.

### Tornado

Tornado uses SPC/NOAA reports and tracks.

This is a biased historical record:

```text
SPC track/report record
    -> affected by population, detection, EF-scale changes, unrated events
    -> needs bias-aware fitting
```

The EF rating is damage-inferred:

```text
observed damage -> inferred wind speed bin
```

So rural/open-land tornadoes can be under-rated because there is less damage evidence. That matters for wind
farms, which often sit in open rural land.

---

## 6. What M0 Must Teach You

M0 must inspect the sources against the authored layer-0 definition.

```text
M0 strong wind:
    what ASCE returns
    units and reference conditions
    return periods / MRIs
    Exposure C basis

M0 tornado:
    what SPC tracks/reports look like
    path length and width
    EF category
    time window and reporting bias

M0 asset geometry:
    turbine point cloud
    wind-farm boundary / convex hull
    TIV basis
```

The key M0 skill is to avoid treating ASCE and SPC as interchangeable wind data. They are different evidence
types for different sub-perils.

---

## 7. What M1 Builds

M1 forks by sub-peril.

```text
strong wind:
    ASCE return-period gust profile
    -> local severity/frequency profile
    -> Poisson/light-tail profile

tornado:
    SPC path/EF record
    -> bias-corrected collection rate
    -> bounded severity distribution
    -> path geometry statistics
```

ASCII:

```text
ASCE RP gust surface             SPC tornado tracks
        |                               |
        v                               v
strong-wind profile              tornado rate + path/severity
        |                               |
        +---------------+---------------+
                        |
                        v
                 shared M2/M4 contract
```

---

## 8. M2 Coupling For A Wind Farm

A wind farm is a sparse point cloud, not one dense surface.

```text
turbines:    o       o       o
                 o       o
             o       o       S   S = collector substation
```

Tornado coupling:

```text
narrow path intersects some turbines
    -> areal hit-or-miss
    -> path-aware Minkowski / swept fraction
```

Strong-wind coupling:

```text
broad gust field covers the site
    -> no hit/miss thinning
    -> read local ASCE gust profile
```

For strong wind, `site-conditioned` means the local field still has to be interpreted through exposure
category, terrain/topography, height, and turbine class. See
[`LL15`](../../learning_logs/15_site_conditioned_is_not_one_thing.md) for the cross-hazard rule.

The same asset has two coupling pictures because the sub-peril physics differs.

---

## 9. M0-M4 Translation For Convective Wind

```text
Layer 0:
    author the wind definition: 3-s gust, sub-perils, thresholds, bounds

M0:
    inspect ASCE, SPC/NOAA, asset geometry

M1:
    fork catalog by sub-peril: strong wind profile, tornado fitted stream

M2:
    tornado path hit/miss; strong wind site-conditioned gust

M3:
    gust -> turbine/subsystem damage curve

M4:
    co-sample tornado and strong wind into one annual loss distribution
```

Important combine rule:

```text
EAL can add by expectation.
Tail metrics must be read from the joint annual-loss vector.
```

Do not sum per-sub-peril VaR/PML as if they were independent final answers.

---

## 10. What To Watch In Convective-Wind Results

```text
[ ] Is the 3-s gust basis explicit?
[ ] Are event threshold and damage-onset threshold kept separate?
[ ] Is tornado separated from strong wind?
[ ] Is ASCE treated as a pre-integrated RP surface, not a raw event catalog?
[ ] Is SPC treated as reporting-biased, especially for rural/open land?
[ ] Does tornado use path-aware hit/miss coupling?
[ ] Does strong wind avoid fake p_hit thinning?
[ ] Are strong-wind near-zero catastrophic losses interpreted as a damage-layer result, not "no operational risk"?
[ ] Are tail metrics computed from the joint annual distribution?
```

---

## Source Context

- `docs/hazards/convective_wind/README.md`
- `Notebooks/convective_wind/layer0/README.md`
- `docs/plans/convective_wind/00_hazard_definition.md`
- `docs/google_drive_docs/Hazard_Data_Reference.docx` - tornado/strong-wind source and ASCE/SPC framing.
- `docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` - coupling-type doctrine.
