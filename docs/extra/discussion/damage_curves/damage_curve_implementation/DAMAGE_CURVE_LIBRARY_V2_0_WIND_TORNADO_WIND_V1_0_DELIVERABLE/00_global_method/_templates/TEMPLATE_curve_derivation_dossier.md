# Curve Derivation Dossier — `<hazard> × <asset>` `<version>`

## 1. Executive summary

State what curve was derived and what it should be used for.

## 2. Cell and failure-unit identity

```text
cell_id:
failure_unit_id:
subsystem:
component:
y_axis:
```

## 3. Modeled y-axis meaning

Define exactly what the damage ratio means.

Examples:

```text
module replacement DR
probability of component replacement trigger
expected repair-cost fraction of subsystem value
state-weighted expected damage ratio
```

## 4. X-axis decision

Selected x-axis:

```text
x_axis_id:
unit:
source-native units:
```

Alternative x-axes:

| Candidate | Pros | Cons | Decision |
|---|---|---|---|
| `<axis>` | `<pros>` | `<cons>` | selected / bridge / rejected / future |

## 5. Evidence inventory with links

| Source ID | Title | Organization / author | Year | Link / file path | Type | Supports | Limitation |
|---|---|---|---:|---|---|---|---|
| `<SRC_ID>` | `<title>` | `<org>` | `<year>` | `<url>` | lab / claims / standard / analytical / assumption | `<support>` | `<limitation>` |

## 6. Source-to-parameter mapping

| Parameter / rule | Value | Source / assumption ID | How used | Caveat |
|---|---:|---|---|---|
| `<parameter>` | `<value>` | `<SRC_OR_ASSUMP>` | `<used for>` | `<caveat>` |

## 7. Raw anchors and interpreted anchors

| Anchor ID | Raw source statement | Interpreted model anchor | Used for | Notes |
|---|---|---|---|---|
| `<A_ID>` | `<raw>` | `<model anchor>` | `<fit/validation>` | `<notes>` |

## 8. Curve-form alternatives considered

| Form | Why considered | Decision |
|---|---|---|
| Step threshold | `<reason>` | selected/rejected and why |
| Bounded logistic | `<reason>` | selected/rejected and why |
| Piecewise linear | `<reason>` | selected/rejected and why |
| Damage states | `<reason>` | selected/rejected and why |

## 9. Selected curve form and parameter derivation

Formula:

```text
<curve formula>
```

Parameter derivation:

```text
<math and explanation>
```

## 10. Base curve assumptions

| Assumption ID | Assumption | Affects | Confidence | Replacement evidence |
|---|---|---|---|---|
| `<ASSUMP_ID>` | `<assumption>` | `<field>` | low/medium/high | `<what would replace it>` |

## 11. Selector logic

| Selector | Values | Effect | Source support | Caveat |
|---|---|---|---|---|
| `<selector>` | `<values>` | chooses / shifts | `<source>` | `<caveat>` |

## 12. Conditioner logic

| Conditioner | Values | Effect | Source support | Caveat |
|---|---|---|---|---|
| `<conditioner>` | `<values>` | shifts / blends / state selection | `<source>` | `<caveat>` |

## 13. Exposure and value scaling logic

```text
engineering DR = <curve result>
loss fraction = engineering DR × value_share × f × exposure_fraction
```

## 14. Variant catalog

| Variant ID | Selector state | Conditioner state | Parameters | Use case |
|---|---|---|---|---|
| `<variant>` | `<selector>` | `<conditioner>` | `<params>` | `<use>` |

## 15. QA checks

```text
[ ] curve bounded
[ ] monotonic where expected
[ ] units clear
[ ] source-to-parameter map complete
[ ] assumptions registered
[ ] extrapolation policy clear
```

## 16. Open seams and update triggers

| Seam ID | Description | Impact | Update trigger |
|---|---|---|---|
| `<SEAM_ID>` | `<description>` | `<impact>` | `<trigger>` |
