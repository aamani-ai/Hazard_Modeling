# Convective Wind Modeling Choices

**Status:** built on main for **convective wind x onshore wind farm**. CONUS grid is planned. This file records
the modeling choices from M0 to M4. For the physics primer, read
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). For source roles, read
[`source_selection.md`](source_selection.md).

The core convective-wind modeling fact:

```text
one peril, two sub-perils, one observable:
  tornado [T]              -> narrow path, event-fit from SPC/NOAA
  strong / straight wind [W] -> broad local gust profile, ASCE return-period surface

both feed one joint annual loss distribution for the wind farm.
```

---

## M0-M4 In One Table

| Layer | Convective-wind model object | Main choices |
|---|---|---|
| **Layer 0** | Authored hazard definition. | Convective wind = tornado + strong/straight-line wind; hurricane is separate. Observable = 3-second peak gust. Event threshold and damage-onset threshold are kept distinct. |
| **M0** | Two hazard-source shapes. | Strong wind reads ASCE 7-22 return-period gusts; tornado reads SPC/NOAA path/report records. USWTDB/boundary geometry gives the M2/M4 asset input, not hazard M0. |
| **M1** | Per-sub-peril event model. | Strong wind: profile-derived Poisson/Gumbel model from ASCE. Tornado: regional rate, dispersion, EF mix, path geometry, bounded GPD from SPC with bias handling. |
| **M2** | Coupling fork. | Strong wind is site-conditioned with `p_hit = 1`; tornado is path-aware areal hit-or-miss with swept fraction. |
| **M3** | One turbine, two damage curves. | Strong-wind curve has IEC-survival onset and aero reach; tornado curve has lower onset, steeper damage, all-subsystem reach. |
| **M4** | One joint annual loss distribution. | Co-sample both sub-perils into the same simulated years; EAL attribution can split by sub-peril, but PML/VaR/TVaR are read from the joint annual vector. |

---

## M1 Event Model Contract

Convective wind uses two M1 routes from
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md).

### Strong / Straight-Line Wind

```text
source:
  ASCE 7-22 non-hurricane return-period 3-s gust surface

M0 object:
  return period -> gust at the site

M1 count process:
  Poisson(lambda)
  lambda read / derived from ASCE return-level curve
  fano = 1 structural

M1 severity process:
  Gumbel / exponential tail above severe-wind threshold
  xi = 0
  severity metric = 3-s peak gust, m/s

event identity:
  none; ASCE gives local return-level profile, not named storm/derecho events
  enough for single-site AEP/OEP
  portfolio correlation deferred
```

Built Traverse strong-wind parameters:

```text
mu = 25.92 m/s
lambda = 0.9035/year
sigma = 3.581
xi = 0
fano = 1
```

The ASCE profile is not loss. It becomes loss only after M2 says the whole farm is exposed, M3 maps gust to
damage, and M4 samples annual event losses.

### Tornado

```text
source:
  SPC SVRGIS tornado tracks and NOAA/SPC reports

M1 count process:
  regional collection-rate lambda
  fit on detection-stable window
  NegBin if over-dispersed, Poisson if sparse

M1 severity process:
  EF mix -> bounded GPD on 3-s gust
  mu = EF0 threshold
  L = EF5 ceiling ~= 113 m/s
  xi < 0

M1 path process:
  EF-conditioned path length / width / area
  carried to M2 for path-aware hit probability and swept fraction

event identity:
  path-event identity exists in the source record
  outbreak / portfolio correlation is still deferred in V1
```

Built Traverse tornado parameters:

```text
lambda_collection ~= 25.43/year within 150 km
fano ~= 12.0, so NegBin
lambda_asset ~= 0.2398/year after M2
```

---

## Coupling Contract

### Strong Wind

Coupling type:

```text
site-conditioned
```

M2 choices:

```text
p_hit = 1
exposure_fraction = 1
lambda_asset = lambda_M1
```

Reason:

```text
the ASCE curve is already local to the site;
a broad strong-wind field is not a small footprint that can miss the farm.
```

### Tornado

Coupling type:

```text
areal hit-or-miss, path-aware
```

M2 choices:

```text
p_hit(EF) = (path_length + asset_width) * (path_width + asset_width) / collection_area
lambda_asset = lambda_collection * E[p_hit]
event loss also receives swept_fraction(EF)
```

Reason:

```text
a tornado is a narrow path;
a wind farm is a sparse turbine cloud;
most strikes clip only part of the farm.
```

---

## Damage Contract

M3 consumes:

```text
3-second peak gust, m/s
sub-peril label: strong_wind or tornado
```

M3 emits:

```text
damage ratio for the wind-farm asset
```

Current curve family:

```text
capex-weighted subsystem logistic
```

Sub-peril differences:

| Choice | Strong wind | Tornado |
|---|---|---|
| Damage onset | IEC survival band, around 60 m/s | lower, around 44 m/s for 5% DR |
| Subsystem reach | aero/electrical subset; max DR around 0.65 | all subsystems; DR tends toward 1 |
| Mechanism | feathered turbine overload | rotation, vertical load, pressure/debris, EF damage calibration |
| Confidence | low | low |

Known-answer:

```text
DR at severe-wind threshold is near zero.
Tornado DR is greater than strong-wind DR at the same gust.
```

---

## M4 Sampling And Metrics

For each simulated year:

```text
draw strong-wind count:
  N_w ~ Poisson(lambda_w)

for each strong-wind event:
  gust ~ ASCE-derived Gumbel/exponential severity
  loss_w = DR_strongwind(gust) * TIV

draw tornado count:
  N_t ~ NegBin(lambda_t, fano_t) or Poisson(lambda_t)

for each tornado event:
  EF / gust ~ tornado severity model
  loss_t = swept_fraction(EF) * DR_tornado(gust) * TIV

A_y = min(sum(loss_w + loss_t), TIV)
O_y = max(single event loss)
```

Metrics:

```text
EAL
EAL attribution by sub-peril
AEP-PML / VaR
OEP-PML
TVaR
$ and % TIV
```

Aggregation doctrine:

```text
EAL_strong + EAL_tornado = EAL_joint
tail metrics are not additive
PML/VaR/TVaR are read from the joint annual vector
do not compute joint metrics as max(EAL_strong, EAL_tornado) or max(PML_strong, PML_tornado)
```

The MC caught the sign of the tail-aggregation issue: for Traverse, summing per-sub-peril VaR understated the
joint by about 26%.

This follows the cross-hazard rule in
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md): combine sub-peril event losses into the
annual vector first, then read metrics. `max()` is only a double-count guard at an event/component overlap
boundary; it is not an annual metric aggregation method.

---

## Built Numbers And Confidence

Reference sites:

| Site | EAL | PML250 | TVaR99 | Interpretation |
|---|---:|---:|---:|---|
| Traverse, OK | 0.064% TIV / ~$0.89M | 3.99% TIV | 4.88% TIV | real tornado tail |
| Shepherds Flat, OR | 0.006% TIV / ~$0.07M | 0.15% TIV | 0.35% TIV | near-zero baseline |

Confidence:

```text
hazard structure:       strong; two sub-perils and thresholds are correct
strong-wind loss:       known-answer near zero for catastrophic physical damage
tornado frequency:      useful but reporting-bias limited
M3 turbine curves:      dominant uncertainty, low confidence
portfolio correlation:  deferred
```

---

## Open Questions And Better Ways

Questions to resolve during review:

```text
tornado reporting bias:
  Is the detection-stable SPC window and EF2+ cross-check enough, or do we need a stronger homogenized
  tornado-rate model before product use?

EF rural bias:
  EF ratings are damage-inferred and likely low over open wind-farm land. Does the current bounded severity
  model understate the rural turbine tail?

turbine fragility:
  The turbine wind curves are greenfield. They need engineering calibration, claims evidence, or vendor
  design-limit review before exact PML/TVaR levels are trusted.

strong-wind scope:
  Strong wind is near-zero for catastrophic physical loss, but it may matter for fatigue, curtailment, and
  outage. That belongs in the Performance/disruption track, not this M4 physical-loss result.

dependence:
  Tornado and strong-wind streams are co-sampled into one annual distribution, but derecho/outbreak portfolio
  correlation and same-event identity are deferred.
```

Better-way candidates:

```text
hazard:
  homogenized tornado climatology, radar-derived tornado-path/wind-field data where available, regional
  Bayesian frequency/dispersion fits

coupling:
  path geometry with turbine-level exposure and event-family identity for portfolio work

damage:
  calibrated turbine subsystem fragility curves, conditional damage uncertainty, repair-cost validation

portfolio:
  derecho/outbreak event-family model and cross-asset correlation
```

---

## Assumptions And Revisit Triggers

Load-bearing assumptions:

```text
convective wind = tornado + strong/straight-line wind
hurricane wind is separate
observable = 3-s peak gust
strong wind ASCE profile is pre-integrated
strong wind fano = 1 structural
tornado SPC record needs bias-stable fitting
tornado and strong wind are disjoint V1 streams
single-site only
financial terms are not included
```

Revisit triggers:

```text
calibrated turbine fragility curves land
measured/homogenized tornado wind-field catalog becomes available
portfolio event-family correlation enters scope
strong-wind disruption / fatigue track enters Performance tier
hurricane + TC-spawned tornado aggregation is combined
CONUS wind grid is built
```

Authoritative registers:

- Assumptions: [`../../plans/convective_wind/assumptions.md`](../../plans/convective_wind/assumptions.md).
- Decisions: [`../../plans/convective_wind/decisions.md`](../../plans/convective_wind/decisions.md).
- Wind-farm asset page: [`wind.md`](wind.md).

## Decision Stress-Test Questions

```text
definition:
  are event threshold and turbine damage onset kept separate?

source mode:
  is strong wind read from ASCE as a return-period/profile surface?
  is tornado fitted from a bias-corrected SPC record?

coupling:
  is tornado path-aware areal hit/miss?
  is strong wind site-conditioned with p_hit near 1?

damage:
  are tornado and straight-line wind allowed different turbine fragility at the same gust?

M4:
  are both streams sampled into one joint annual vector before tail metrics are read?
```

If tail metrics are summed per sub-peril, the aggregation is wrong even when EAL attribution still adds cleanly.
