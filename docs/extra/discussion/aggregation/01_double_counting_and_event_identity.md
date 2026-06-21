# 01 - Double Counting & Event Identity

*A discussion doc, not a plan. This file handles the first aggregation question: did the same physical event, or
the same physical damaged value, enter the model twice? It deliberately stops before VaR/PML math; that belongs
in [`02_metric_operators_and_joint_distributions.md`](02_metric_operators_and_joint_distributions.md).*

**Source key.** `[REF]` means the rule comes from the Drive methodology / Risk Metrics Reference. `[OURS]`
means a repo build assumption or proposed architecture convention. Drive remains the source of truth; if an
`[OURS]` rule becomes platform doctrine, update the Drive method first.

---

## 1. What double-counting is

Double-counting is not "two hazards occurred in one year." That can be real and should add.

Double-counting means one of these:

```text
1. The same physical parent event is represented as two independent modeled events.
2. The same damaged component/value is charged twice inside one parent event.
3. The same source event row is imported twice through two source paths.
4. The same loss component is counted under two names.
```

Those are different failure modes and need different fixes.

---

## 2. Event identity ladder

Use this ladder before deciding any metric operator.

```text
source row
  one record in one source product
  e.g. SPC row, ASCE lookup, Storm Events row, FSim grid value

modeled consequence
  one hazard effect on one asset/component
  e.g. H001 wind damages turbine blades

parent event / event family
  one physical event that can produce multiple consequences
  e.g. Hurricane H001 produces wind + surge + rainfall + TC tornado

annual simulation year
  one sampled year containing zero, one, or many parent events

portfolio year
  same sampled year across many assets
```

ASCII view:

```text
PARENT EVENT FAMILY: HURRICANE_H001
        |
        +-- consequence 1: wind field -> turbine damage
        +-- consequence 2: surge depth -> substation flood damage
        +-- consequence 3: rainfall -> access outage / BI
        +-- consequence 4: TC tornado -> local path damage
```

The parent event is sampled once. Its child consequences fire together.

---

## 3. Failure Mode A - same parent event counted twice

Example:

```text
Hurricane H001 exists in:

  hurricane catalog       -> wind loss
  flood catalog           -> coastal flood / surge loss
  tornado catalog         -> TC-spawned tornado loss
```

If modeled independently:

```text
year 0010: H001 wind
year 0522: H001 surge
year 8844: H001 tornado
```

That is physically wrong. It breaks timing and usually understates the joint tail because consequences that
should co-occur are scattered across different simulated years.

Better:

```text
year 0010:
  event_family_id = H001
  children = wind + surge + rainfall + TC tornado
```

### Options

| Option | What it does | Good when | Caveat |
|---|---|---|---|
| **Partition** | Assign the parent event to one owning peril stream; exclude it from others. | V1 needs clean simple streams. | Can hide child consequences unless scope is explicit. |
| **Bind** | Keep child consequences but link with `event_family_id`; sample together. | Hurricane, winter, wildfire outage, portfolio swaths. | Needs child dependency assumptions and schema support. |
| **Independent streams** | Treat event sets as disjoint/independent. | Sources are demonstrably disjoint, or V1 labels this assumption. | Wrong if parent events overlap. |

### Discussion lean

For V1, **partition where it keeps the build honest and small**. For richer peril families, **bind**.

Example:

```text
V1 convective wind:
  strong wind = ASCE non-tornadic surface
  tornado     = SPC Tornado record
  -> disjoint by data product

Future hurricane:
  hurricane wind + surge + rainfall + TC tornado
  -> bind or partition; do not sample independently
```

---

## 4. Failure Mode B - same damaged value counted twice

Example:

```text
Same transformer
replacement value = $1.0M

child A: wind says destroyed      = $1.0M
child B: flood says destroyed     = $1.0M
----------------------------------------
naive physical sum                = $2.0M   wrong
component physical cap            = $1.0M   right physical basis
```

But economic loss can stack:

```text
transformer replacement           = $1.0M
lost revenue during downtime      = $0.6M
extra expense / access cost       = $0.2M
----------------------------------------
gross economic loss               = $1.8M   possible
```

Physical damage cap and economic loss cap are not the same thing.

### Cap grain options

| Option | Cap level | Good when | Caveat |
|---|---|---|---|
| Whole asset TIV | `min(physical_loss, TIV)` | V1 fallback when component values are unknown. | Can hide duplicate component damage and distort multi-component events. |
| Subsystem value | cap by subsystem allocation | M3 has capex-weighted subsystem values. | Needs consistent subsystem map across perils. |
| Component value | cap by real component/replacement value | Best for substations, transformers, turbine components. | Highest data requirement. |
| No cap at event component stage | cap only after annual sum | Simple. | Can physically destroy same component multiple times before cap. |

Discussion lean: use the finest value basis M3 genuinely supports. Do not pretend to have component caps if the
asset data only supports subsystem or whole-asset caps.

---

## 5. Failure Mode C - same source record imported twice

This is source hygiene rather than risk math.

Example:

```text
NOAA Storm Events row
SPC row
local report row

all describe the same tornado
```

Options:

| Option | What it does | Caveat |
|---|---|---|
| Source hierarchy | Pick one authoritative row and retain others as validation. | Loses some fields unless merged deliberately. |
| Field merge | Merge rows into one event record with provenance. | Needs matching rules; can accidentally merge distinct events. |
| Keep separate with family link | Preserve rows but bind under one `event_family_id`. | Requires downstream code to avoid counting all rows as independent losses. |

Discussion lean: for event catalogs, source hierarchy or field merge is cleaner. Family links are better for
real child consequences, not duplicate rows.

---

## 6. Failure Mode D - same loss component counted under two names

Example:

```text
fire causes:
  direct equipment damage
  outage duration
  business interruption
  replacement power cost
```

Those may all be valid, but not if two labels represent the same dollars.

Questions:

```text
Is replacement power cost separate from lost PPA revenue, or an alternative valuation of the same missing MWh?
Is downtime embedded in the physical damage curve, or modeled separately as BI?
Is smoke derating included in disruption, or included in wildfire "damage"?
```

If the same dollars are valued twice, this is double-counting even if the event identity is clean.

---

## 7. `max(A,B,C)` for overlapping perils

You raised `max(A,B,C)` where A/B/C are **different overlapping perils**. That can be valid, but only for a narrow
case.

### Valid case: competing estimates of same physical loss

```text
Parent event: Hurricane H001
Component: substation transformer
Physical replacement value: $1.0M

A = wind model says transformer physical damage = $0.8M
B = surge model says transformer physical damage = $1.0M
C = rainfall/flood model says transformer physical damage = $0.6M

If A/B/C are competing explanations for the same physical destroyed transformer:
  component_physical_loss = max(A, B, C) = $1.0M
```

Here `max` is not a total-risk metric. It is a de-dup / component-cap approximation.

### Invalid case: distinct real consequences

```text
A = wind damages turbine blades
B = surge damages substation
C = rainfall blocks access and causes BI

total_event_loss != max(A, B, C)
```

Those are different consequences. Dropping all but the largest loses real loss.

### Ambiguous case: overlapping damage mechanisms on one component

```text
same component, two mechanisms:
  wind weakens structure
  flood shorts electronics
```

Options:

| Option | Meaning | Caveat |
|---|---|---|
| `max(A,B)` | Conservative non-double-count if mechanisms are alternative labels. | Understates if mechanisms cause distinct repair scopes. |
| `min(A+B, component_value)` | Allows both mechanisms but caps physical value. | Requires component value and repair-scope discipline. |
| engineered rule | mechanism-specific combination. | Best but needs evidence. |

Discussion lean: prefer `min(A+B, component_value)` when mechanisms can damage different repair scopes within the
same component; use `max` only when they are competing estimates for the same repair scope.

---

## 8. Pattern Library

| Case | Double-count risk | Discussion-level treatment |
|---|---|---|
| Tornado + strong wind inside convective wind | Same storm can produce both. | V1 treats as disjoint by data product: ASCE non-tornadic wind surface + SPC Tornado record. Re-audit if source changes. |
| Hurricane wind + surge + rainfall | One parent event produces multiple child hazards. | Bind under hurricane `event_family_id`; child losses sampled together. |
| Hurricane + TC-spawned tornado | Same tornado can appear in hurricane and SPC tornado streams. | Partition TC tornadoes into hurricane, or bind tornado child to hurricane family. |
| Hurricane surge + coastal flood | Same inundation can be cataloged as hurricane secondary peril and flood peril. | One owner source for surge/inundation, or shared event family. |
| Severe convective outbreak | Hail, wind, and tornado can share one parent system. | V1 may be independent; richer model binds outbreak family. |
| Wildfire flame + smoke + outage | One fire creates damage and disruption. | One fire family; separate loss components; avoid BI double valuation. |
| Heat + drought | Same climate episode drives multiple deratings. | Shared climate/system year factor or joint scenario. |
| Winter snow/ice/cold | One winter storm drives load damage, freeze-off, demand spike. | Parent winter family or explicit product partition. |
| Portfolio swath/fire/storm | One event hits multiple assets. | Shared event across assets; not independent asset sampling. |

---

## 9. Proposed schema fields

Minimum future event record fields for de-duplication and event-family handling:

| Field | Why |
|---|---|
| `event_id` | Unique consequence/event row. |
| `event_family_id` | Parent physical event linking child consequences. |
| `source_event_id` | Trace back to source row(s). |
| `peril`, `sub_peril` | Selects coupling/damage logic. |
| `asset_id` | Same parent can hit many assets. |
| `component_id` or `value_basis` | Prevents destroying same value twice. |
| `loss_component` | Physical damage, BI, extra expense, revenue, downtime, repair. |
| `loss_basis` | Gross physical, gross economic, owner net, insurer net. |
| `event_loss` | Loss contribution after valid event-level caps. |
| `sampled_year` | Annual aggregation frame. |

Open question: should `event_family_id` be mandatory nullable everywhere? Discussion lean: yes.

---

## 10. Handoff to metric operators

This file does **not** decide whether total risk is `sum`, `max`, or quantile. It produces clean event losses.

The handoff object is:

```text
clean event-family-aware loss records
```

Then [`02_metric_operators_and_joint_distributions.md`](02_metric_operators_and_joint_distributions.md) decides
how those records become AEP/OEP vectors and metrics.
