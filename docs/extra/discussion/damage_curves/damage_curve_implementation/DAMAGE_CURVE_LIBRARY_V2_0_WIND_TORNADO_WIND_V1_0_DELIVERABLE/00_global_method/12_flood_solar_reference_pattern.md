# Flood × Solar Reference Pattern

This document is the reusable reference pattern for the second archetype cell: **flood × solar**.

It exists so future cell builders can copy the structure without copying the exact assumptions.

---

## 1. Why this cell matters

Flood × solar is the canonical example of:

```text
multi-failure-unit cell
+ geometry/elevation at-risk fraction
+ split x-axis logic
+ electrical ingress and civil/scour pathways
```

It is the contrast to hail × solar:

```text
hail × solar:
    mostly one primary failure-unit
    f_kind = material/component share

flood × solar:
    multiple failure-units
    f_kind = site geometry / elevation share
```

---

## 2. Required snapshot format

Every flood × solar README should include a tree like this:

```text
flood × solar
├─ primary nonzero failure-units
│  ├─ INVERTER_SYSTEM / INVERTER / cabinet-skid inundation
│  ├─ SUBSTATION / SWITCHGEAR / cabinet inundation
│  ├─ SUBSTATION / TRANSFORMER_MAIN / transformer/control inundation
│  ├─ INVERTER_SYSTEM / COMBINER_BOX + DC_PROTECTION / enclosure inundation
│  └─ SCADA / MONITORING_SYSTEM / control-cabinet inundation
│
├─ conditional / secondary failure-units
│  ├─ ELECTRICAL_COLLECTION / cable-trench-conduit water path
│  ├─ FOUNDATION / pile-pad scour
│  ├─ CIVIL_INFRA / access-road erosion
│  ├─ PV_ARRAY / total submersion or debris
│  └─ MOUNTING / debris-velocity loading
│
├─ protection / exposure modifiers
│  ├─ SITE_DRAINAGE / capacity exceedance
│  ├─ FLOOD_DEFENSE / overtopping
│  ├─ equipment elevation / freeboard
│  ├─ conduit sealing and drainage
│  └─ shutdown / energized state
│
└─ DR≈0 in v1
   └─ equipment above waterline with no alternate water path
```

---

## 3. X-axis rule

Do not use one flood score by default.

Use:

```text
depth above component datum
    for electrical ingress/submersion

velocity or scour proxy
    for foundation/civil/erosion damage
```

Duration, contamination, salinity, and energized state are conditioners unless evidence forces them to become axes.

---

## 4. Curve-form rule

Flood electrical equipment often behaves like a threshold/state problem:

```text
dry → inspect → recondition → replace
```

So candidate forms should include:

```text
step threshold
smoothed threshold/logistic
piecewise state curve
replacement/reconditioning state model
```

The logistic, if used, is not “because everything is logistic.” It is a way to smooth uncertainty around a physical threshold: imperfect elevation data, cabinet entry heights, waves, drainage, and partial submersion.

---

## 5. New curve vs adjustment

Create a new curve when the mechanism changes:

```text
electrical ingress
conduit water transport
transformer/control inundation
foundation scour
PV module total submersion/debris
```

Adjust a curve when the same mechanism remains but the equipment resistance or event state changes:

```text
NEMA/IP rating
energized/shutdown state
contamination/saltwater
duration
flood defense deployment
```

Do not confuse elevation with fragility. Elevation usually changes the **x value**:

```text
h_i = max(0, WSE - z_i_crit)
```

not the curve shape.

---

## 6. Evidence starting set

Each future flood × solar package should begin with at least:

- DOE/FEMP solar PV flood mitigation guidance
- NEMA water-damaged electrical equipment guidance
- FEMA Hazus Flood Model or equivalent depth-damage framework
- FEMA P-348 or equivalent utility-system floodproofing guidance
- NEMA enclosure type definitions
- ASCE 24 or equivalent flood-resistant design standard

Each source must be mapped to the exact parameter/rule it supports.


---

## v1.0 reference implementation note

The current reference implementation is located at:

```text
01_cells/flood_solar/current/
```

The v1.0 implementation follows this reference pattern and adds actual v1.0 curve ordinates:

```text
electrical ingress/submersion curves:
    inverter
    switchgear
    transformer/control area
    combiner/DC protection
    SCADA/control cabinet
    collection cable/conduit pathway
    PV module submersion, conditional

velocity/scour curve:
    foundation/pile scour, placeholder secondary
```

The implementation remains deliberately transparent: every curve is marked as public-source-anchored engineering parameterization, not claims-calibrated empirical severity.
