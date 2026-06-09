# M0 to M4: Full Hazard-to-Financial-Metrics Modeling Journey

This note recaps the full modeling journey we are building:

```text
raw hazard event data
    -> hazard catalog
    -> hazard-asset coupling / exposure
    -> damage, duration, and frequency
    -> event-loss generation
    -> annual loss vectors
    -> financial transformation
    -> EAL, VaR, TVaR, PML, premium, capital, ROI
```

The important clarification is that **M0 to M4 are not alternative statistical methods** here. They are the staged journey from raw hazard evidence to final financial/risk metrics.

---

> **⚠️ Numbering note (read first).** This is an early sketch that **lumps raw evidence + catalog into one
> "M0," so it labels coupling "M1."** The repo we actually build uses the **finer A-series numbering**
> ([scope §6](../../00_scope_and_story.md), `A20`/`A21`/`A22`): raw evidence and the catalog are **split**
> into M0 and M1, so **coupling is M2**. *Same journey — the labels are just shifted by one at the front.*
>
> | The stage (the real thing) | This doc | **Our build** | Methodology doc (stages) |
> |---|---|---|---|
> | raw evidence (NOAA, MRMS) | M0 | **M0** ✅ | §3 inputs |
> | clean event catalog (footprints) | M0 | **M1** ✅ | §3 Catalog Input Contract |
> | coupling — did it hit? (hit probability) | **M1** | **M2** ✅ | §4 Coupling + §5 Frequency |
> | severity + duration | M2 | **M3** (next) | §6 Severity · §7 Duration |
> | event losses → annual AEP/OEP vectors | M3 | Phase 5 | §8 Event-Loss Generation |
> | financial metrics (EAL/VaR/PML) | M4 | Phase 5 | §9 Financial + Risk Metrics Reference |
>
> The **methodology doc** (`google_drive_docs/hazard_asset_loss_distribution_methodology`) uses descriptive
> *stages*, not M-numbers — those stages are the canonical truth, the M-numbers are just our module packaging,
> and our build matches the methodology **stage-for-stage**.

---

## The Full M0 → M4 Journey

```text
M0  Raw Hazard Evidence / Hazard Catalog
    "What physical events exist?"

M1  Hazard × Asset Coupling / Exposure
    "Did this event reach this asset, and at what intensity?"

M2  Damage, Duration, and Frequency
    "If it affects the asset, how bad is it, how long does it last,
     and how often do relevant events occur?"

M3  Event-Loss Generation + Annual Aggregation
    "Build actual simulated event losses and annual loss vectors."

M4  Financial Transformation + Risk Metrics
    "Convert physical/economic losses into decision metrics:
     EAL, VaR, TVaR, PML, premium, capital, ROI, etc."
```

Visual map:

```text
RAW HAZARD WORLD
      │
      v
┌────────────────────────────────────┐
│ M0  Hazard evidence/catalog         │
│     event_id, hazard_type,          │
│     footprint, intensity, rate      │
└────────────────────────────────────┘
      │
      v
┌────────────────────────────────────┐
│ M1  Coupling × exposure geometry    │
│     hit/miss, field intensity,      │
│     site-conditioned level          │
│     point/area/line/portfolio       │
└────────────────────────────────────┘
      │
      v
┌────────────────────────────────────┐
│ M2  Frequency + severity + duration │
│     count model, damage curve,      │
│     fragility, downtime, BI drivers │
└────────────────────────────────────┘
      │
      v
┌────────────────────────────────────┐
│ M3  Event loss + annual aggregation │
│     actual losses, not expected     │
│     AEP annual total, OEP max event │
└────────────────────────────────────┘
      │
      v
┌────────────────────────────────────┐
│ M4  Financial terms + metrics       │
│     deductibles, limits, caps,      │
│     EAL, VaR, TVaR, PML, ROI        │
└────────────────────────────────────┘
```

---

# M0 — Raw Hazard Evidence and Hazard Catalog

M0 answers:

```text
What hazard events exist in the world or simulation catalog?
```

At this stage, we do **not** have losses.

We only have hazard evidence:

```text
hail swath
flood depth raster
heat time series
wind field
wildfire perimeter
earthquake ground motion
```

Example M0 record:

```text
event_id:        HAIL_001
hazard_type:     hail
year:            2032
footprint:       swath polygon
peak_intensity:  60 mm hail
source:          radar / simulation / vendor catalog
```

Important:

```text
M0 is not a loss catalog.
M0 is an event catalog.
```

It says:

```text
what happened physically
```

It does **not** yet say:

```text
what it cost this asset
```

---

# M1 — Coupling and Exposure Geometry

M1 answers:

```text
How does this hazard event reach this specific asset?
```

This is where we combine:

```text
hazard event + asset location/shape
```

M1 produces things like:

```text
hit indicator
local intensity
exposed fraction
affected components
```

The key coupling types:

```text
hit-or-miss:
    Did the footprint touch the asset?

field intensity:
    What intensity did the asset experience?

site-conditioned:
    What local site level did the event create?
```

Example:

```text
HAIL_001 + SolarFarm_A

M1 output:
    hit = yes
    exposed_fraction = 40%
    local_hail_size = 60 mm
```

ASCII:

```text
hazard event
    │
    v
asset geometry
    │
    v
coupling logic
    │
    ├── miss -> event_loss = 0 later
    │
    └── hit  -> local intensity + exposed fraction
```

M1 still does not fully calculate financial loss. It prepares the physical contact information needed for damage.

---

# M2 — Frequency, Severity, and Duration

M2 is the big middle layer.

It answers:

```text
How often do relevant events occur?
How bad is the damage if an event affects the asset?
How long is the asset impaired?
```

This stage has three parallel pieces.

---

## M2a — Frequency

Frequency answers:

```text
How many relevant events happen per year?
```

For hit-or-miss hazards:

```text
λ_asset = λ_collection × spatial_factor
```

But the important rule is:

```text
spatial factor is hit probability,
not a damage haircut.
```

Wrong:

```text
event_loss = spatial_factor × conditional_loss
```

Correct:

```text
hit ~ Bernoulli(spatial_factor)

if hit:
    use full conditional loss

if miss:
    loss = 0
```

So frequency creates the random number of chances for loss.

---

## M2b — Severity / Damage

Severity answers:

```text
Given the event affected the asset,
what damage ratio should this intensity produce?
```

This is where the damage curve or fragility curve enters.

Example:

```text
60 mm hail -> 20% mean damage ratio
```

But it can emit different richness levels:

```text
scalar:
    damage_ratio = 20%

damage-state vector:
    none 20%, slight 30%, moderate 30%, extensive 15%, complete 5%

full distribution:
    probability over damage-ratio bins
```

So M2 severity converts:

```text
local intensity -> damage representation
```

---

## M2c — Duration

Duration answers:

```text
How long is the asset impaired?
```

This matters because energy assets lose revenue over time.

There are two duration types:

```text
damage-driven downtime:
    repair/replacement time after physical damage

hazard-persistence duration:
    how long the hazard itself lasts
```

Example:

```text
hail cracks panels -> 30 days repair downtime
heat wave lasts 5 days -> 5 days production derating
flood water remains for 4 days + 60 days repair
```

So M2 produces the ingredients for event loss:

```text
frequency
severity
duration
```

---

# M3 — Event-Loss Generation and Annual Aggregation

M3 answers:

```text
Now can we generate actual losses year by year?
```

This is where we stop talking about expected loss and start simulating actual annual outcomes.

For hit-or-miss hazards, the base loop is:

```text
for each simulated year:

    n_hits ~ Poisson(λ_asset)

    year_loss = 0
    year_max_event_loss = 0

    for each hit:
        sample severity
        sample duration if needed
        compute event_loss

        year_loss += event_loss
        year_max_event_loss = max(year_max_event_loss, event_loss)

    record:
        AEP_year = year_loss
        OEP_year = year_max_event_loss
```

This produces two important vectors:

```text
AEP vector:
    annual total loss per simulated year

OEP vector:
    annual maximum single-event loss per simulated year
```

Example:

```text
Year 1:
    event losses = []
    AEP_year = $0
    OEP_year = $0

Year 2:
    event losses = [$12M, $30M]
    AEP_year = $42M
    OEP_year = $30M

Year 3:
    event losses = [$75M]
    AEP_year = $75M
    OEP_year = $75M
```

So:

```text
M3 creates the actual loss vectors.
```

This is the central object the whole methodology is building.

---

# M4 — Financial Transformation and Metrics

M4 answers:

```text
What does this loss mean financially, and what metrics do we report?
```

At this stage we apply:

```text
deductibles
limits
waiting periods
annual aggregate caps
portfolio/treaty terms
BI terms
owner-retained loss
insurer-paid loss
reinsurer-layer loss
```

The order matters.

```text
per-event gross loss
    ↓
apply per-occurrence deductible / limit
    ↓
sum annual event losses
    ↓
apply annual aggregate deductible / limit
    ↓
apply portfolio / treaty terms
    ↓
final net annual loss vector
```

Then metrics are simple readings:

```text
EAL     = mean(annual loss vector)
VaR_99  = 99th percentile
TVaR_99 = average loss beyond VaR_99
AEP-PML = percentile of annual aggregate loss
OEP-PML = percentile of annual maximum event loss
```

Important:

```text
M4 does not create the physics.
M4 reshapes the loss into financial views.
```

And there is not just one final vector. There are several labeled vectors:

```text
gross_physical_annual_loss
gross_economic_annual_loss
owner_retained_net_loss
insurer_net_loss
reinsurer_layer_loss
portfolio_net_loss
```

So this is incomplete:

```text
VaR_99 = $80M
```

Unless we say:

```text
VaR_99 of which vector?
Gross physical?
Gross economic?
Owner retained?
Insurer net?
Portfolio net?
```

---

# The Whole Journey With Middle Steps

```text
M0 — Hazard catalog
-------------------
raw evidence
    ↓
standardized event catalog
    ↓
event_id, hazard_type, footprint, intensity, rate, provenance


M1 — Coupling / exposure
------------------------
event + asset
    ↓
coupling type
    ↓
asset geometry
    ↓
hit/miss OR local intensity OR local site level
    ↓
exposed fraction / affected components


M2 — Loss drivers
-----------------
frequency:
    count model / λ / hit probability

severity:
    intensity -> damage curve / fragility / damage distribution

duration:
    downtime / persistence / repair time

    ↓
event-level loss ingredients


M3 — Loss generation
--------------------
sample actual events
    ↓
sample hit/miss where needed
    ↓
sample severity/duration
    ↓
compute event losses
    ↓
sum annual total = AEP_year
    ↓
take annual max = OEP_year
    ↓
annual loss vectors


M4 — Financial metrics
----------------------
apply financial terms
    ↓
create labeled gross/net vectors
    ↓
read EAL, VaR, TVaR, PML
    ↓
decision outputs:
        premium benchmark
        capital at risk
        DSCR stress
        ROI
```

---

# One Concrete Example: Hail on Solar

## M0: Event Catalog

```text
HAIL_001:
    year = 2032
    footprint = swath polygon
    peak hail size = 60 mm
```

No loss yet.

---

## M1: Coupling

```text
HAIL_001 overlaps SolarFarm_A.

local_hail_size = 60 mm
exposed_fraction = 40%
```

Now we know the event reached the asset.

---

## M2: Frequency, Severity, Duration

Frequency:

```text
λ_collection = 45 regional events/year
spatial_factor = 0.03
λ_asset = 1.35 hits/year
```

Severity:

```text
60 mm hail -> damage distribution
or scalar mean damage ratio = 20%
```

Duration:

```text
repair downtime = sample from repair-time distribution
```

---

## M3: Event and Annual Loss

```text
simulate Year 2032:

n_hits = 2

event 1 loss = $12M
event 2 loss = $30M

AEP_year = $42M
OEP_year = $30M
```

After many simulated years:

```text
AEP_vector = [0, 42M, 75M, 0, 18M, ...]
OEP_vector = [0, 30M, 75M, 0, 18M, ...]
```

---

## M4: Financial Metrics

Apply terms:

```text
per-occurrence deductible
per-occurrence limit
annual aggregate cap
owner retention
insurance layer
```

Then read:

```text
EAL = mean(net annual vector)
VaR_99 = 99th percentile of net annual vector
TVaR_99 = mean beyond VaR_99
OEP-PML_100 = 99th percentile of annual max event vector
AEP-PML_100 = 99th percentile of annual aggregate vector
```

---

# The Key Distinction

The journey is not:

```text
hazard event -> expected loss -> metric
```

The correct journey is:

```text
hazard event
    -> asset coupling
    -> severity/duration/frequency
    -> actual event losses
    -> annual loss vectors
    -> financial transformations
    -> metrics
```

The whole reason we are building M0–M4 is to avoid this bad shortcut:

```text
loss = frequency × spatial_factor × mean_damage
```

That shortcut may give EAL in a simple gross case, but it does not build the distribution needed for VaR, TVaR, PML, AEP, and OEP.

---

# Suggested Naming

| Stage | Name | Main question | Output |
|---|---|---|---|
| M0 | Hazard Event Catalog | What events exist? | Standardized hazard events |
| M1 | Hazard-Asset Coupling | How does the event reach the asset? | Intensity / exposed fraction / hit |
| M2 | Loss Driver Modeling | How often, how severe, how long? | Frequency, damage, duration objects |
| M3 | Annual Loss Engine | What actual losses occur in simulated years? | AEP and OEP vectors |
| M4 | Financial Metrics Layer | What does this mean financially? | EAL, VaR, TVaR, PML, premium, ROI |

Shortest memory hook:

```text
M0 = event exists
M1 = event reaches asset
M2 = event causes damage/downtime
M3 = event losses become annual vectors
M4 = annual vectors become financial metrics
```
