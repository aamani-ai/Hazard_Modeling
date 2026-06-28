# 00 - Overview: Aggregation Has Two Questions

*A discussion overview, not a plan. This folder exists because "how do we combine overlapping losses?" is not one
question. It is at least two: first event identity, then metric algebra.*

**Source key.** `[REF]` means the rule comes from the Drive methodology / Risk Metrics Reference. `[OURS]`
means a repo build assumption or proposed architecture convention. Drive remains the source of truth; if an
`[OURS]` rule becomes platform doctrine, update the Drive method first.

---

## 1. The split

```text
QUESTION 1 - DOUBLE COUNTING / EVENT IDENTITY

Did the same physical event or same physical damaged value enter the model twice?

Primary files:
  -> 01_double_counting_and_event_identity.md

Primary tools:
  partition
  de-duplicate
  event_family_id
  component/value caps
  same-component max / model selection
```

```text
QUESTION 2 - METRIC OPERATORS / JOINT DISTRIBUTIONS

After event identity is clean, are we combining the right mathematical objects?

Primary files:
  -> 02_metric_operators_and_joint_distributions.md

Primary tools:
  joint annual AEP/OEP vectors
  EAL from mean
  PML/VaR/TVaR from quantiles/tail means
  dependence-aware sampling
```

These interact, but they are not interchangeable. You can fix duplicate events and still add PMLs incorrectly.
You can use the right quantile formula and still feed it duplicated parent events.

---

## 2. Correct flow

```text
raw source records
        |
        v
+----------------------------------+
| 1. event identity cleanup        |
|    same parent event?            |
|    same damaged component/value? |
|    partition, bind, cap, dedupe  |
+----------------------------------+
        |
        v
+----------------------------------+
| 2. event loss generation         |
|    physical damage               |
|    BI / downtime                 |
|    component caps                |
|    loss basis labels             |
+----------------------------------+
        |
        v
+----------------------------------+
| 3. annual vectors                |
|    AEP_year = sum(events)        |
|    OEP_year = max(events)        |
+----------------------------------+
        |
        v
+----------------------------------+
| 4. metric readouts               |
|    EAL  = mean(AEP)              |
|    VaR  = quantile(AEP)          |
|    PML  = quantile(AEP/OEP)      |
|    TVaR = tail mean(AEP)         |
+----------------------------------+
```

Wrong flow:

```text
peril A metric     peril B metric     peril C metric
     |                  |                  |
     +---------- arithmetic? -------------+
                    |
                    v
             "total risk number"

Problem:
  The event-year loss distribution was never built.
```

---

## 3. Where the two split files meet

The two files meet at the **event-year loss record**.

```text
double-counting file produces:
  clean event / event-family loss records

metric-operators file consumes:
  clean event / event-family loss records
  -> annual AEP/OEP vectors
  -> metrics
```

If a future architecture has one invariant, it should be this:

```text
Metrics never combine other metrics unless the metric is explicitly additive.
Metrics read from vectors.
Vectors come from clean event records.
```

---

## 4. Read order

| Step | Read | Why |
|---|---|---|
| 1 | [`01_double_counting_and_event_identity.md`](01_double_counting_and_event_identity.md) | Establish whether A/B/C are separate events, child consequences of one event, duplicate source records, or competing estimates of one damaged value. |
| 2 | [`02_metric_operators_and_joint_distributions.md`](02_metric_operators_and_joint_distributions.md) | Decide whether `sum`, `max`, caps, EAL attribution, joint sampling, or a stress-only shortcut is valid. |

---

## 5. The practical question to ask

Do not start with:

```text
Should total risk be sum(A,B,C) or max(A,B,C)?
```

Start with:

```text
What are A, B, and C?

Are they:
  - separate physical consequences?
  - competing estimates of the same consequence?
  - child consequences of the same parent event?
  - independent annual vectors?
  - already metric readouts instead of simulated losses?
```

Only after that can the operator be chosen.

---

## 6. Status

Open discussion. This is not plan-of-record architecture yet. The likely graduation path is:

```text
discussion/aggregation/
    -> docs/plans/common/aggregation.md
    -> production event/loss schema
    -> Overall Risk tier
```

The first specific target is a common event record that can carry:

```text
event_id
event_family_id
peril / sub_peril
asset_id
loss_basis
loss_components
component/value basis
event_loss
event_max_loss
sampled year
```
