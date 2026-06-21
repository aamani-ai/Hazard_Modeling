# 15 · Wind / tornado × wind reference pattern

This reference pattern is the global-method companion to the `wind_tornado_wind` cell package.

It exists so future wind-farm cells do not have to rediscover the architecture.

---

## 1. Why this cell is important

Wind/tornado × wind is the first cell that introduces all of the following at once:

```text
repeated units
  many turbines, not one continuous array

structural failure
  blade, tower, nacelle, foundation

operating-state conditioners
  feathered, yaw aligned, parked, braked, faulted

partial swath exposure
  only some turbines may be inside the damaging footprint
```

The correct model is not a single wind farm curve. It is a bundle of per-turbine failure-unit records plus plant-scope conditional rows.

---

## 2. Reference coverage tree

```text
strong wind / tornado × wind
├─ primary nonzero failure-units
│  ├─ ROTOR_ASSEMBLY / BLADE
│  ├─ TOWER / TOWER_SECTION
│  ├─ NACELLE / drivetrain-generator-housing
│  └─ FOUNDATION / FOUNDATION_BASE, if support/overturning pathway is included
│
├─ conditioner-only equipment / states
│  ├─ PITCH_SYSTEM / feathered state
│  ├─ BRAKE_SYSTEM / parked / emergency stop state
│  ├─ YAW_SYSTEM / yaw alignment or yaw error
│  └─ operating state / operating, parked, curtailed, faulted
│
├─ secondary / conditional units
│  ├─ POWER_ELECTRONICS
│  ├─ SCADA
│  ├─ ELECTRICAL_COLLECTION
│  ├─ SUBSTATION
│  └─ CIVIL_INFRA, if footprint/debris affects it
│
├─ exposure / protection modifiers
│  ├─ turbine exposure fraction / exposed turbine count
│  ├─ severe-wind or tornado swath
│  ├─ IEC class / Vref / design selector
│  └─ terrain and hub-height conversion
│
└─ DR≈0 reviewed buckets
   └─ turbines/components outside the footprint or below damage threshold
```

---

## 3. X-axis rule

Use the following distinction by default:

| Pathway | Primary x-axis | Notes |
|---|---|---|
| Straight-line / severe synoptic wind | Hub-height 3-second gust speed | Bridge from 10m/reference-height products when needed. |
| Tornado | Tornado wind proxy, or EF bridge | EF category is a damage-estimated bridge, not a direct continuous wind measurement. |
| IEC class / Vref | Selector / design anchor | Not an event x-axis. |
| Swath exposure | Exposure geometry | Not a fragility axis. |

---

## 4. Curve-form starting point

| Failure-unit | Candidate form |
|---|---|
| Blade | Fragility/logistic or state curve |
| Tower | Structural fragility/lognormal or piecewise collapse state |
| Nacelle | Dependency/state curve |
| Foundation | Threshold/state curve with load/geotech proxy |
| Pitch/yaw/brake | Conditioner transformation, not direct curve by default |
| Turbine swath | Exposure multiplier/count aggregation |

Do not copy the hail logistic just because it worked for module glass breakage. Curve form follows physics and evidence.

---

## 5. Minimum metadata pattern

```text
hazard inputs
├─ gust_3s_hub_mps
├─ tornado_wind_proxy_mps or tornado_ef_rating
└─ swath / footprint information

selectors
├─ IEC wind class / Vref
├─ turbine model
├─ hub height
├─ rotor diameter
├─ tower type
└─ foundation type

conditioners
├─ operating state
├─ feathered state
├─ yaw alignment
├─ brake status
└─ grid/control availability

exposure
├─ exposed turbine count
├─ turbine exposure fraction
└─ shared plant footprint hit
```

---

## 6. Anti-patterns

Avoid:

```text
wind speed → whole wind farm loss %
EF rating → full turbine loss without bridge/uncertainty
Vref → event x-axis
partial swath → new fragility curve
feathered state → hidden assumption
independent summing of tower + nacelle + rotor total losses without assembly precedence
```

The wind/tornado × wind cell is expected to require assembly rules in v1.0 because tower, nacelle, rotor, and foundation losses are physically coupled.

---

# v1.0 derived-curve reference update

The `wind_tornado_wind` cell now has a v1.0 derived package. The key modeling pattern is:

```text
strong wind / tornado × wind v1.0
├─ repeated turbine structural curves
│  ├─ blade
│  ├─ tower
│  ├─ nacelle
│  └─ foundation
├─ conditioner states
│  ├─ feathered state
│  ├─ yaw alignment
│  ├─ brake status
│  └─ operating / parked / faulted state
├─ exposure variables
│  ├─ exposed turbine count
│  ├─ exposed turbine fraction
│  └─ swath / direct-hit footprint
└─ value link
   └─ each failure-unit maps to a wind subsystem value bucket
```

## v1.0 curve form

```text
DR_i(V) = max_DR_i / (1 + exp[-k_i × (V/Ve50 - D50_ratio_i)])
```

This is a design-normalized logistic fragility-style curve. It is used because public turbine subsystem loss data is sparse, and because the problem is a structural exceedance/fragility problem rather than a flood-like state table.

## x-axis

```text
straight-line wind:
    hub-height 3-second gust

tornado:
    EF / tornado wind proxy bridge
    kept separate from measured hub-height gust
```

## v1.0 caution

The v1.0 curves are public-source-derived and auditable, but not private claims-calibrated. D50/k parameters are engineering-fit anchors and should be replaced by turbine-specific fragility, OEM load-case, forensic, or claims data when available.
