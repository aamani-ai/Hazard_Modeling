# Fundamentals Before M0

This is the cross-hazard prerequisite guide. It explains what a modeler must understand before opening a
hazard's M0 notebooks.

It is not a methodology spec, a decision register, or a run log. The M0-M4 methodology says how the pipeline
runs. This guide says what the person doing the modeling needs to understand before the pipeline can be read
correctly.

Read this before any hazard-specific `fundamentals_before_m0.md` file.

---

## 1. What "Before M0" Means

M0 is where we meet raw data. But before M0, we need a mental model of the hazard itself.

The prerequisite has three parts:

```text
1. Physics
   What physical process causes damage, and what quantity actually drives the damage curve?

2. Data-source reality
   What public source exists, what does it actually measure, and what does it not measure?

3. Pipeline translation
   Given the physics and data limits, what should M0, M1, M2, M3, and M4 mean for this hazard?
```

This is the work that prevents a modeler from applying a formula just because it worked for another peril.

The platform rule is:

```text
standardize the interface, not the physics
```

So every hazard eventually emits comparable event/loss records, but the hazard-specific adapter behind those
records may be completely different.

---

## 2. The Target Object

Every hazard-specific notebook is trying to build the same final object:

```text
annual loss distribution for one hazard x asset pair
```

The hazard can be hail, wildfire, flood, hurricane, tornado, or anything else. The asset can be solar, wind,
transmission, storage, or a portfolio. The path differs, but the final object is the same because the business
questions are the same:

```text
What is the expected annual loss?
How bad is a 1-in-100 or 1-in-250 year?
What is the tail average beyond a chosen threshold?
How much does one occurrence cost versus one whole year of events?
```

Those questions are answered by reading metrics off annual loss vectors, not by computing each metric as a
separate model.

```text
For simulated / sampled year y:

    L_1, L_2, ..., L_N       event losses in that year

    A_y = sum(L_i)           aggregate annual loss
    O_y = max(L_i)           largest occurrence loss

Across many years:

    EAL      = mean(A_y)
    AEP-PML  = quantile(A_y)
    OEP-PML  = quantile(O_y)
    VaR      = quantile of the stated annual-loss frame
    TVaR     = mean of the tail beyond the chosen quantile
```

So the modeling target is:

```text
three ingredients  ->  two annual loss vectors  ->  financial metrics
```

The three ingredients are:

```text
1. Event frequency / count process
   How many events occur in a year?

2. Event intensity / coupling process
   How severe are those events, and what intensity reaches the asset?

3. Conditional damage / loss process
   Given the asset experiences that intensity, how much value is damaged?
```

This is the shortest way to understand M0-M4:

```text
M0/M1  build or read frequency + intensity evidence
M2     couple that evidence to the asset
M3     translate coupled intensity into damage/loss
M4     aggregate event losses into annual AEP/OEP vectors and read metrics
```

---

## 3. Many Paths To The Same Target

The platform standardizes the target object, not the route to it.

```text
raw observation path
    example: MRMS MESH for hail
    route: raw gridded fields -> thresholded events -> fitted frequency/severity

pre-integrated product path
    example: FSim BP + flame-length histogram for wildfire
    route: upstream simulation already provides burn probability + conditional severity

design / return-period surface path
    example: ASCE wind maps, FEMA BLE flood depths
    route: read/interpolate return-level profile; do not pretend to refit raw events

stochastic catalog path
    example: hurricane synthetic tracks
    route: convert each simulated storm into a local field/intensity event

proxy / model-chain path
    example: pluvial flood
    route: rainfall frequency + terrain/runoff logic -> modeled depth
```

All five routes can be valid. The discipline is that each route must declare which of the three ingredients it
provides directly, which it fits, and which it only proxies.

That is why source selection matters. A source is not "good" in the abstract; it is good if it supplies the
model ingredient we need at the right spatial grain, frequency frame, and confidence level.

---

## 4. The Word "Simulation" Has Several Meanings

The project uses the word `simulation` in several places. They are related, but they are not interchangeable.

```text
1. Upstream physical simulation
   A source provider simulates the hazard system.
   Example: FSim simulates many fire seasons; SLOSH models surge envelopes.
   Lives before or inside M0/M1 as source evidence.

2. Hazard/event simulation
   We or an upstream catalog generate possible events, magnitudes, tracks, depths, or fields.
   Example: synthetic hurricane tracks, sampled hail sizes, sampled gusts.
   Lives in M1 or between M1 and M2.

3. Damage/loss simulation
   We draw damage or event loss conditional on coupled intensity.
   Example: sample damage ratio from a conditional curve rather than using only mean DR.
   Lives in M3/M4.

4. Annual-loss Monte Carlo
   We draw many synthetic years, aggregate all event losses per year, and read metrics.
   Example: compound-Poisson or NegBin annual loss simulation in M4.
   Lives in M4.
```

The important warning:

```text
More M4 Monte Carlo years do not make the hazard source truer.
They only sample the model we already built more precisely.
```

So when a notebook says "simulated," ask which level it means: upstream physical simulation, event simulation,
damage simulation, or annual-loss Monte Carlo.

---

## 5. The Universal Questions

Every hazard-specific fundamentals guide should answer these before M0.

```text
PHYSICS
  What is the peril?
  Does it have one physical system or multiple sub-perils?
  What physical intensity actually damages the asset?
  Is that intensity a point value, a field, a depth/profile, or a distribution?
  What is the difference between event threshold and damage-onset threshold?

DATA
  What source gives the hazard evidence?
  Is it a raw historical record, a gridded observation, a pre-integrated model product,
  a design/return-period surface, or a stochastic catalog?
  Does the source give events directly, or do we construct events?
  Does it give frequency, severity, footprint, or only a proxy?
  What biases and missing pieces are load-bearing?

PIPELINE
  Does the hazard need layer-0 before M0?
  What does M0 inspect?
  What does M1 emit?
  What coupling type does M2 use?
  What does M3's damage curve consume?
  How does M4 sample annual losses?
```

---

## 6. The Four Confusions This Layer Prevents

### Magnitude vs Intensity

Magnitude is one event-level descriptor. Intensity is what the asset experiences.

```text
hurricane category       = event magnitude / classification
gust at one solar plant  = sampled intensity

hail-day peak MESH       = event severity summary
MESH over the plant      = sampled intensity / coupling input

flood return period      = annual probability frame
local inundation depth   = sampled intensity
```

The damage curve consumes the asset-relevant intensity measure, not a headline event label.

### Rate vs Annual Probability

Rate is events per year. Annual exceedance probability is probability of at least one exceedance in a year.

```text
rate lambda: events/year, can exceed 1
AEP p: probability, 0 to 1

under Poisson:
    p = 1 - exp(-lambda)
```

This matters most when events are frequent, such as hail.

### Footprint vs Sampled Intensity

A footprint is the whole spatial field. The asset sees one or more sampled values.

```text
hurricane wind field        -> gust at each turbine
flood depth grid            -> depth at each equipment/pad location
hail severe footprint       -> whether/how much of the asset is hit
wildfire BP/FLP raster      -> site hazard profile at/around the asset
```

Do not carry the whole field into a damage curve that expects one sampled intensity, and do not collapse a
field too early when the asset geometry matters.

### Hazard Return Period vs Loss Return Period

A 100-year hazard intensity is not automatically a 100-year loss.

```text
hazard RP  -> return period of wind/depth/rain/hail intensity
loss RP    -> return period of annual loss after coupling + damage + value + aggregation
```

M3 nonlinearity and M4 aggregation break any one-to-one mapping.

---

## 7. Coupling Types

M2 is where the hazard reaches the asset. This is the practical heart of "standard interface, not standard
physics."

```text
                             M2 coupling type

    areal hit-or-miss      field-intensity           site-conditioned
    -----------------      ---------------           ----------------
    footprint overlaps?    sample local field        local level/profile
    Bernoulli hit/miss     intensity varies          already site-specific

    hail                   hurricane wind            flood depth
    tornado path           wind field over farm      wildfire BP/FLP profile
```

`site-conditioned` is a family, not a full answer. After assigning that coupling type, classify the local
condition surfaces: natural terrain/elevation, engineered protection, managed vegetation, component placement,
event-time operations, and source-product artifacts can all change the model in different stages. See
[`LL15`](../learning_logs/15_site_conditioned_is_not_one_thing.md).

The same hazard can also change by asset geometry:

```text
solar farm      = dense area/polygon
wind farm       = sparse turbine point cloud + substation
transmission    = line/network
portfolio       = many assets sharing event correlation
```

Coupling type and asset geometry are separate axes.

---

## 8. How Data Shape Changes M1

The source shape determines whether M1 extracts events, assembles a profile, or builds a synthetic field.

```text
raw gridded observation
    example: MRMS MESH for hail
    M1 job: threshold/aggregate into events, fit frequency/severity

pre-integrated product
    example: FSim BP + flame-length histogram for wildfire
    M1 job: assemble the site profile, declare frequency/severity

design or return-period surface
    example: ASCE 7-22 wind gust maps; FEMA BLE depth grids
    M1 job: read/interpolate the return-level profile, do not pretend to fit what upstream already fit

stochastic catalog
    example: RAFT hurricane tracks
    M1 job: convert each storm into a field/intensity event and anchor frequency properly

biased historical reports
    example: SPC tornado/wind reports, NOAA Storm Events hail reports
    M1 job: use as cross-check or bias-corrected fit, not as naive truth
```

This is why the notebooks differ by hazard even though they all say M0-M4.

---

## 9. Hazard Map

| Hazard | Before-M0 issue | Data shape | M2 coupling picture |
|---|---|---|---|
| Hail | Radar-estimated hail size must become hail-day footprints. | Raw gridded MESH + biased point reports. | Areal hit-or-miss for solar. |
| Wildfire | FSim already pre-integrates burn probability and severity. | Pre-integrated BP + FLP field. | Site-conditioned; no hit/miss thinning. |
| Convective wind | The event definition must be authored from standards. | ASCE RP gust surface + biased SPC reports. | Tornado areal; strong wind site-conditioned. |
| Flood | One peril has three sub-perils with different data sources. | BLE/NFHL/Atlas/SLOSH depth or proxies. | Site-conditioned depth/elevation coupling. |
| Hurricane | Track must become wind field; surge/rain must be cross-linked to flood. | RAFT synthetic tracks + HURDAT2 frequency + ASCE validation. | Field-intensity wind sampling. |

---

## 10. How To Read Any Hazard Notebook

Use this checklist before reading M0/M1 output.

```text
[ ] What physical intensity does the damage curve ultimately consume?
[ ] Is the event definition inherited, authored, or oriented from several sub-perils?
[ ] Does the source measure the intensity directly, estimate it, or only proxy it?
[ ] Is frequency read from the source, fit from a record, or anchored to another source?
[ ] Does M2 need hit probability, field sampling, or site-conditioned depth/profile logic?
[ ] Does the asset geometry matter as area, point cloud, line, or portfolio?
[ ] Which caveat is most load-bearing: source bias, short record, curve confidence, or combine logic?
```

---

## References In This Repo

- `docs/google_drive_docs/hazard_modeling_terminology.docx` - magnitude vs intensity, rate vs AEP, footprint vs sampled intensity.
- `docs/google_drive_docs/Hazard_Data_Reference.docx` - per-peril source landscape and the rule for splitting sub-perils by physics plus data.
- `docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` - standard interface, coupling types, and event/loss record doctrine.
- `docs/principles/hazard_asset_specificity.md` - standard interface, not standard physics.
- `Notebooks/README.md` - peril vs peril-asset folder structure and coupling matrix.
