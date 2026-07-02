# Wildfire Modeling Choices

**Status:** built on main for **wildfire x solar** deep per-asset. A wildfire CONUS grid is planned but not
built. This file records the modeling choices from M0 to M4. For the physics primer, read
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). For source roles, read
[`source_selection.md`](source_selection.md).

The core wildfire modeling fact:

```text
FSim already pre-integrates fire seasons into burn probability and conditional flame-length severity.
M1 mostly assembles a finished hazard product rather than extracting events from raw observations.
```

---

## M0-M4 In One Table

| Layer | Wildfire model object | Main choices |
|---|---|---|
| **M0** | FSim native burn probability and FIL1-6 flame-length rasters; WRC 2.0 as cross-check. | Native FSim is the V1 spine because it preserves the full conditional severity histogram. WRC has finer grain but collapsed severity. |
| **M1** | Site or cell hazard profile: annual burn probability / lambda plus conditional flame-length class distribution. | Frequency is read from FSim BP; severity is the FIL1-6 histogram conditional on burning. Poisson count process with `lambda = -ln(1 - BP)`. |
| **M2** | Site-conditioned coupling. | Solar reads the local hazard profile over the plant footprint or surrounding fuel ring. No areal hit/miss thinning like hail. Oozed developed pixels are handled as an asset-specific M2 issue. |
| **M3** | Fire intensity / flame length -> solar damage ratio. | Current curve is approximate: capex-weighted BoS/PV vulnerability, fixed standoff assumption, low/low-medium confidence. |
| **M4** | Annual loss vectors and metrics. | Draw fire occurrence from BP/lambda, draw conditional flame-length class, apply M3, aggregate AEP/OEP. Directional contrast is trustworthy; exact loss magnitude is curve-limited. |

---

## M1 Event Model Contract

Wildfire uses the **pre-integrated product path** from
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md).

```text
source:
  USFS FSim native product

frequency object:
  burn probability BP at the site / footprint / cell
  lambda = -ln(1 - BP)
  fano = 1 structural in V1

severity object:
  conditional flame-length histogram FIL1-FIL6
  severity exists only conditional on burning
  converted to fire-line intensity where needed using Byram

event identity:
  not a historical named-fire catalog in V1
  FSim season/event identity is not preserved in the compact V1 profile
  portfolio fire-season correlation deferred
```

Important distinction:

```text
BP is annual probability of burning.
FIL histogram is severity conditional on burning.
```

Do not multiply BP into the severity histogram and then treat the result as conditional severity. The model keeps
frequency and conditional severity separate until M4.

---

## Coupling Contract

Wildfire x solar is **site-conditioned**:

```text
the hazard profile is read at / around the site
there is no footprint-overlap Bernoulli like hail
```

M2 changes local intensity / profile selection more than event frequency:

```text
if valid fuel pixels surround the plant:
  use surrounding fuel ring to avoid developed-pixel oozing artifacts

if boundary polygon exists:
  use boundary-zonal extraction

if boundary is missing:
  use capacity-radius fallback
```

The key M2 issue is **oozing**:

```text
developed asset pixels may inherit burn probability while suppressing intensity
```

So a naive pixel read can understate conditional severity. The model treats this as an asset-specific coupling
problem, not a source-selection problem.

---

## Damage Contract

M3 consumes:

```text
flame length / fire-line intensity
standoff / local exposure assumption
```

M3 emits:

```text
solar asset damage ratio
```

Current V1 curve:

```text
family:
  capex-weighted subsystem curve

main uncertainty:
  wildfire-to-solar empirical calibration is weak
  fixed standoff assumption carries large uncertainty

unmodeled / low-confidence:
  fire-front sweep across a full plant
  duration
  smoke/soiling/operational interruption
  claims calibration
  conditional damage-ratio distribution
```

The hazard field is stronger than the loss curve. In wildfire V1, the dominant uncertainty is M3, not FSim.

---

## M4 Sampling And Metrics

For a single site:

```text
for each simulated year:
  draw burn occurrence from Poisson/Bernoulli-equivalent lambda
  if burn occurs:
    draw flame-length class from FIL1-FIL6 conditional histogram
    convert severity if needed
    event_loss = DR(severity) * TIV
  else:
    event_loss = 0

  A_y = sum(event_loss)
  O_y = max(event_loss)
```

For V1, wildfire usually has a low event rate, so AEP/OEP can be similar for a single site. The same annual-vector
doctrine still holds: read EAL, VaR/PML, TVaR from sampled annual losses, not separate formulas.

---

## Built Numbers And Confidence

The built wildfire x solar notebooks use reference sites to prove the flow:

```text
Hayhurst: near-zero wildfire physical loss
Matrix:   material wildfire signal; EAL around 0.29% TIV and PML250 around 14% TIV in the task-history recap
```

Confidence:

```text
frequency / BP:        trustworthy as a pre-integrated FSim hazard product
severity profile:      useful but coarse; FIL6 open-ended
M2 oozing treatment:   important and asset-specific
M3 damage magnitude:   provisional / low confidence
tail:                  coarse severity bins; continuous tail deferred
```

---

## Open Questions And Better Ways

Questions to resolve during review:

```text
FSim vintage:
  How stale is the local fuel / burn-probability picture at each asset, especially after recent fires,
  treatments, regrowth, or development?

oozing:
  Is the surrounding-fuel-ring rule enough to handle developed-pixel oozing, or should M2 use a more formal
  exposure-zone model around assets?

severity:
  FIL1-FIL6 is a coarse conditional histogram with an open-ended top bin. Continuous flame length / fire-line
  intensity would be better for tail metrics.

damage:
  The wildfire x solar curve is the weak link. It needs claims, post-fire inspection, or engineering evidence
  before exact loss levels are product-grade.

event identity:
  The compact FSim profile is enough for single-site annual loss, but portfolio fire-season correlation and
  named-fire validation need a richer event/dependence model.
```

Better-way candidates:

```text
hazard:
  refreshed FSim / WRC vintages, local burn scars and fuel treatments, continuous severity tail

coupling:
  explicit fire-front sweep / partial-plant burn geometry instead of full-site exposure on burn

damage:
  calibrated PV / BoS wildfire curves, duration/heat flux treatment, smoke/soiling/PSPS only if in scope

portfolio:
  fire-season dependence model or stochastic event catalog with identity preserved
```

---

## Assumptions And Revisit Triggers

Load-bearing assumptions:

```text
native FSim FIL1-FIL6 is the severity spine
frequency uses lambda = -ln(1 - BP)
fano = 1 structural for V1
BP unit conversion follows the FSim lab convention
all-touched boundary-zonal extraction for real footprint
surrounding fuel ring handles developed-pixel oozing when needed
financial terms are not included
```

Revisit triggers:

```text
calibrated wildfire x solar damage curve lands
continuous flame-length / fire-line intensity tail is added
FSim / fuels vintage update is incorporated
fire-front sweep / partial plant burn model is built
portfolio fire-season correlation enters scope
business interruption or outage duration enters scope
```

Authoritative registers:

- Assumptions: [`../../plans/wildfire/assumptions.md`](../../plans/wildfire/assumptions.md).
- Decisions: [`../../plans/wildfire/decisions.md`](../../plans/wildfire/decisions.md).
- Wildfire x solar asset page: [`solar.md`](solar.md).

## Decision Stress-Test Questions

```text
source mode:
  are we reading a pre-integrated FSim/WRC surface rather than extracting events?

frequency:
  does lambda come from local BP with the documented unit conversion?

severity:
  is FLP/FIL treated as conditional intensity given fire?

coupling:
  is developed-pixel oozing handled as an asset-specific M2 issue?

damage:
  is the fixed wildfire x solar curve identified as the dominant uncertainty?

M4:
  are occurrence and conditional severity sampled, rather than multiplying lambda into losses?
```

If FSim already pre-integrated the event set, do not rebuild a fake event catalog just to make wildfire look like hail.
