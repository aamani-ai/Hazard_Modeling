# Hurricane Modeling Choices

**Status:** notebooks imported to main for review from the branch snapshot carried by `origin/flood` @ `aff8649`.
Hurricane wind x solar and hurricane wind x wind-farm are built end-to-end in
[`Notebooks/hurricane/`](../../../Notebooks/hurricane/README.md). Hurricane plan/register docs are now imported
to main under [`docs/plans/hurricane/`](../../plans/hurricane/README.md). This file records the
modeling shape so the M0-M4 choices are visible before deeper notebook review. For the physics primer, read
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). For source roles, read
[`source_selection.md`](source_selection.md).

The core hurricane modeling fact:

```text
this hazard owns tropical-cyclone WIND only.
surge and rainfall are flood-owned and must join by event identity where available.

severity from RAFT synthetic storms;
frequency from HURDAT2 observed close-passage rates.
```

---

## M0-M4 In One Table

| Layer | Hurricane model object | Main choices |
|---|---|---|
| **Layer 0** | Wind-only tropical-cyclone scope. | Magnitude/intensity variable is 3-second peak gust. Surge/rain are not modeled as hurricane loss here; they route to flood. |
| **M0** | RAFT synthetic TC tracks and HURDAT2 observed storm record. | RAFT supplies storm structure / severity; HURDAT2 anchors frequency; ASCE validates return-period gust tail. Site geometry is M2 asset input. |
| **M1** | Storm event field model. | Holland wind-field synthesis from RAFT tracks; observed close-passage lambda from HURDAT2; RAFT genesis rate is not used as frequency. |
| **M2** | Field-intensity coupling. | Solar polygon is nearly spatially degenerate; wind farm samples gust per turbine / node across the lease. |
| **M3** | 3-second gust -> asset damage ratio. | Solar hurricane curve and wind-farm turbine curve are provisional; wind-farm curve reuses straight-line-wind mechanics from convective wind. |
| **M4** | Storm-resolved annual loss vectors. | Compound-Poisson storm count, sampled storm fields, per-event losses, AEP/OEP metrics; surge cross-link by `event_family_id` when combined with flood. |

---

## M1 Event Model Contract

Hurricane uses the **stochastic catalog path** from
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md), but with frequency separated from severity.

```text
source for severity:
  RAFT synthetic North Atlantic TC tracks
  storm structure: intensity, radius, track geometry

source for frequency:
  HURDAT2 observed hurricanes passing within the close-passage radius
  lambda = observed close passages / 173-year record

severity process:
  convert each RAFT storm to local 3-s gust through Holland wind-field model
  validate return-period gusts against ASCE 7-22

count process:
  compound-Poisson storm count anchored to HURDAT2 lambda

event identity:
  event_family_id exists for cross-peril join
  surge can join flood coastal on same TC event
  pluvial/rain tropical-cyclone join is deferred
```

Critical choice:

```text
RAFT is not used for frequency because its genesis rate is oversampled.
RAFT supplies severity / physics; HURDAT2 supplies observed frequency.
```

---

## Coupling Contract

Hurricane wind is **field-intensity**:

```text
storm wind field passes near / over the asset
M2 samples local gust intensity at asset locations
```

Solar:

```text
small footprint relative to hurricane wind field
gust variation across the plant is minimal
effective exposed_fraction = 1
one representative local gust is enough in V1
```

Wind farm:

```text
lease can span many kilometers
gust can vary across turbine point cloud
sample gust per turbine / node
aggregate component losses across the farm
```

M2 changes local intensity, not the storm frequency. Storm frequency is already anchored in M1.

---

## Damage Contract

M3 consumes:

```text
3-second peak gust at asset/component
asset type: solar or wind farm
```

M3 emits:

```text
damage ratio or component event loss
```

Current notebook shape:

```text
solar:
  hurricane wind x solar curve, provisional
  wind-immune / low-reach subsystems cap asset DR

wind farm:
  turbine curve aligned with straight-line wind mechanics
  low confidence / greenfield for hurricane application

dominant uncertainty:
  loss-side curve calibration, not hazard-side wind field
```

Hazard-side validation:

```text
HURDAT2 climatology matches published landfall rate
modeled return-period gusts match ASCE within roughly +/-5.5%
```

---

## M4 Sampling And Metrics

For each simulated year:

```text
draw hurricane count from Poisson(lambda_HURDAT2)

for each storm:
  sample / select RAFT storm severity and track structure
  synthesize local Holland wind field
  sample gust at the asset / turbine nodes
  apply M3 gust-damage curve
  assign event_family_id

A_y = sum(storm event losses)
O_y = max(single storm loss)
```

Metrics:

```text
EAL
AEP-PML / VaR
OEP-PML
TVaR
$ and % TIV
```

Cross-peril doctrine:

```text
hurricane wind + flood surge from the same storm should be joined by event_family_id
combined component loss should avoid double counting, e.g. max(wind, surge) where appropriate
pluvial/rain TC event join is deferred
do not combine storm agents with max(EAL_wind, EAL_surge) or by adding separate PMLs
```

The important distinction:

```text
max(wind, surge) can be a per-storm / per-component double-count guard
annual EAL / PML / VaR / TVaR must be read from the joined event-family annual vector
```

This follows the cross-hazard rule in
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md): combine event losses at the correct
grain first, then read metrics from the combined annual vector.

---

## Built Numbers And Confidence

Notebook-backed orientation figures, pending review:

| Asset/site | Hurricane wind metric | Interpretation |
|---|---:|---|
| Solar: Everglades, FL | EAL 2.23% TIV; PML500 41.5% TIV | high-exposure proof site; loss magnitude curve-limited |
| Solar: Hayhurst, TX | ~0 | true-zero / inland baseline |
| Wind: Amazon Wind US East, NC | EAL 0.012% TIV; PML500 1.43% TIV | wind leg for flood coastal compound; surge is expected to dominate combined storm loss |

Confidence state:

```text
hazard side:
  strong; independently validated against ASCE and HURDAT2 climatology

loss side:
  provisional; M3 curves dominate uncertainty

deep tail:
  catalog depth supports roughly 700-1000 year reads before extrapolation concerns

baseline sites:
  true-zero / low-exposure sites correctly return near zero
```

---

## Open Questions And Better Ways

Questions to resolve during notebook review:

```text
wind-field physics:
  Is symmetric Holland 1980 with fixed B / gust conversion enough for V1, or should forward-motion asymmetry,
  storm-size uncertainty, and terrain/exposure adjustments enter before product use?

frequency:
  Is the HURDAT2 close-passage lambda stable enough for site-level rates, and how should we express rate
  uncertainty for sparse sites?

tail depth:
  Does the accepted RAFT subset support PML500/PML1000 without extrapolation artifacts, or should a larger
  accepted catalog / explicit EVT tail be required?

damage:
  The hazard side validates against ASCE, but the M3 curves dominate loss uncertainty. Solar and wind curves
  need claims/Hazus/NRI-style benchmarking before product confidence.

cross-peril join:
  Surge joins flood through event_family_id. TC rainfall/pluvial and TC-spawned tornadoes remain open
  double-count / dependence questions.
```

Better-way candidates:

```text
hazard:
  larger RAFT subset, asymmetric Holland / parametric alternatives, local exposure/terrain adjustment

frequency:
  regional Bayesian close-passage rates or blended HURDAT2 + synthetic frequency calibration

loss:
  calibrated hurricane x solar curve, turbine hurricane validation, policy/BI terms

compound storm:
  one event-family loop carrying wind, surge, rainfall, and secondary perils
```

---

## Assumptions And Revisit Triggers

Load-bearing assumptions:

```text
hurricane peril = wind only
surge/rain are flood-owned
observable = 3-s peak gust
RAFT supplies severity / physics
HURDAT2 supplies frequency
wind field = Holland 1980 style, symmetric V1
solar coupling is spatially degenerate
wind-farm coupling samples per turbine/node
event_family_id is the cross-peril identity
financial terms and BI are not included
```

Revisit triggers:

```text
larger RAFT subset or deeper catalog enters scope
forward-motion asymmetry is implemented
damage curves are replaced/calibrated
Hazus/NRI or claims benchmark is applied
flood coastal surge is integrated on main
pluvial/rain tropical-cyclone event join is built
plans/registers are promoted to main and per-asset hazard docs are written
```

Authoritative references:

- Source selection: [`source_selection.md`](source_selection.md).
- Hurricane anchor: [`README.md`](README.md).
- Local notebooks: [`../../../Notebooks/hurricane/`](../../../Notebooks/hurricane/README.md).
- Local plans: [`../../plans/hurricane/`](../../plans/hurricane/README.md).

## Decision Stress-Test Questions

```text
source mode:
  does RAFT provide storm geometry/severity while HURDAT2 anchors frequency?

event identity:
  is event_family_id preserved on every storm-resolved row?

coupling:
  is solar treated as field-intensity-degenerate only after checking footprint spread?
  is wind farm sampled per turbine/node?

damage:
  are provisional curves clearly labeled as the dominant loss uncertainty?

M4:
  are storm losses sampled as event objects, not reduced to an RP bridge?
```

If surge or rain appears inside the hurricane wind loss layer, the ownership boundary has been crossed; those belong to
flood and join by `event_family_id`.
