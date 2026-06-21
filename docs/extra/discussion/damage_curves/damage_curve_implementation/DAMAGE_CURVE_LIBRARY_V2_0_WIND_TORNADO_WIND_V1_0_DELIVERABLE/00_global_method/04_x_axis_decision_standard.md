# 04 · X-Axis Decision Standard

Every curve must clearly answer:

```text
What is the hazard intensity variable on the x-axis?
Why this variable?
What alternatives were considered?
How do source-native units map into the model?
Is there a physics bridge or proxy transformation?
```

## 1. Required x-axis decision section

Each derivation dossier should include:

```text
1. selected x-axis
2. internal unit
3. source-native units accepted
4. source types that provide this variable
5. physical meaning
6. causal-chain position
7. rejected alternatives
8. bridge variables, if any
9. known limitations
```

## 2. Native hazard axis vs physics bridge

Sometimes the best operational x-axis is not the most physical variable.

```text
hazard catalog / provider data
      │
      ▼
source-native x-axis
      │
      ├─ used directly by damage code
      │
      └─ optionally mapped to physics bridge
             for derivation, calibration, sensitivity
```

Example:

```text
hail × solar
  primary operational x-axis: MESH-equivalent maximum hail diameter
  physics bridge: diameter → mass/velocity → per-stone impact kinetic energy proxy
```

This is preferable to forcing all providers to supply kinetic energy when most hail datasets provide size.

## 3. Causal-chain position

Declare where the x-axis sits in the hazard-to-damage chain.

| Chain position | Meaning | Example |
|---|---|---|
| Hazard source | Large-scale event parameter | hurricane category |
| Local hazard intensity | Site-level intensity | gust speed, flood depth, hail size |
| Contact intensity | Intensity at the component | water depth at inverter pad, effective hail impact angle |
| Damage state | Already a damage proxy | observed broken glass fraction |

Prefer local hazard intensity or contact intensity. Avoid x-axes that already include financial loss unless modeling a pure empirical loss curve.

## 4. Alternative x-axis table

Every cell should include a table like this:

| Candidate x-axis | Pros | Cons | Decision |
|---|---|---|---|
| `<axis>` | Why useful | Why not | selected / bridge / rejected / future |

Example for hail × solar:

| Candidate x-axis | Pros | Cons | Decision |
|---|---|---|---|
| MESH-equivalent hail diameter | Provider-native, operational, common in historical data | Proxy for actual impact energy | Selected primary x-axis |
| Per-stone kinetic energy | More physical for glass breakage | Requires mass/velocity assumptions rarely available from providers | Physics bridge |
| Kinetic energy flux J/m² | Captures aggregate storm exposure | Needs stone concentration and duration; not usually available | Future / not v1 |
| Hail reports by county/event | Easy to obtain | Too coarse for site overlay | Evidence/context, not curve x-axis |

## 5. Multivariate hazards

Do not jump to 2-D curves too early.

```text
apparent multivariate hazard
   │
   ├─ can variables be collapsed into one physical proxy?
   │      └─ yes → composite x-axis
   │
   ├─ do variables affect different failure-units?
   │      └─ yes → split into multiple univariate curves
   │
   └─ neither works
          └─ true 2-D curve or state model
```

Examples:

```text
hail size + velocity
  → diameter primary, KE proxy bridge for derivation

flood depth + velocity
  → depth for electrical ingress, velocity for scour/foundation

wildfire intensity + duration
  → fireline intensity v1, residence time documented as deferred axis unless evidence supports 2-D
```

## 6. Unit handling

Every x-axis record must include:

```text
x_axis_id
x_axis_display_name
unit_internal
unit_source_allowed
unit_conversion_rule
axis_range_min
axis_range_max
extrapolation_policy
```

If extrapolation is allowed, it must be labeled. If extrapolation is not allowed, the damage code should clamp or return a warning flag.
