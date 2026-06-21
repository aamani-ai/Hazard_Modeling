# 02 - Metric Operators & Joint Distributions

*A discussion doc, not a plan. This file handles the second aggregation question: after event identity is clean,
which mathematical operator is valid for the metric? Double-counting and event-family hygiene are handled in
[`01_double_counting_and_event_identity.md`](01_double_counting_and_event_identity.md).*

**Source key.** `[REF]` means the rule comes from the Drive methodology / Risk Metrics Reference. `[OURS]`
means a repo build assumption or proposed architecture convention. Drive remains the source of truth; if an
`[OURS]` rule becomes platform doctrine, update the Drive method first.

---

## 1. The core rule

Metrics should generally read from **vectors**, not from other metrics.

```text
clean event losses
        |
        v
annual vectors
        |
        +-- AEP_year = sum(event losses in the year)
        +-- OEP_year = max(event losses in the year)
        |
        v
metric readouts
        |
        +-- EAL      = mean(AEP_year)
        +-- VaR      = quantile(AEP_year)
        +-- AEP-PML  = quantile(AEP_year)
        +-- OEP-PML  = quantile(OEP_year)
        +-- TVaR     = mean(AEP_year beyond VaR)
```

The operator is attached to the object:

```text
events in one year -> sum for AEP
events in one year -> max for OEP
annual vector      -> quantile for PML/VaR
annual vector      -> tail mean for TVaR
```

---

## 2. Operator Table

| Object | Question | Operator | Output |
|---|---|---|---|
| Event losses in one year | What did the year lose in total? | `sum` | `AEP_year` |
| Event losses in one year | What was the worst single event? | `max` | `OEP_year` |
| Annual aggregate vector | What is the average annual loss? | `mean` | EAL |
| Annual aggregate vector | What is the 1-in-T annual total loss? | `quantile` | AEP-PML / VaR |
| Annual max-event vector | What is the 1-in-T worst-event loss? | `quantile` | OEP-PML |
| Annual aggregate tail | How bad are years beyond VaR? | conditional mean | TVaR |
| Per-peril metrics | What is total risk? | generally none | Need joint vector first |

---

## 3. A/B/C perils: what is valid?

Let:

```text
A = annual loss vector for hail
B = annual loss vector for convective wind
C = annual loss vector for wildfire
```

If A/B/C are clean and sampled on the same annual frame:

```text
T_year = A_year + B_year + C_year
```

Then:

```text
EAL_total     = mean(T_year)
VaR99_total   = quantile(T_year, 0.99)
PML100_total  = quantile(T_year, 0.99)       # AEP frame
TVaR99_total  = mean(T_year | T_year >= VaR99_total)
```

Not:

```text
PML100_total = PML100_A + PML100_B + PML100_C
PML100_total = max(PML100_A, PML100_B, PML100_C)
```

ASCII example:

```text
Same simulated years

year      A hail      B wind      C fire      total = A+B+C
----      ------      ------      ------      -------------
0001        0           0          12             12
0002       30           0           0             30
0003        0          45           0             45
0004       20          25           0             45
0005        0           0           0              0

max(A_year,B_year,C_year) in year 0004 = 25
sum(A_year,B_year,C_year) in year 0004 = 45

If the decision is total annual loss, max is wrong.
If the decision is largest standalone peril that year, max is a different dashboard metric.
```

---

## 4. Why sum of PMLs fails

PML is a quantile. Quantiles do not generally add.

```text
Correct:
  PML100_total = quantile(A_year + B_year + C_year, 0.99)

Wrong:
  PML100_total = quantile(A_year,0.99)
               + quantile(B_year,0.99)
               + quantile(C_year,0.99)
```

Intuition:

```text
Peril A bad tail year may be year 120.
Peril B bad tail year may be year 483.
Peril C bad tail year may be year 902.

Adding their PMLs assumes those marginal tail outcomes line up in one year.
They may not.
```

But the opposite error is also possible:

```text
If A/B/C are positively dependent, the joint bad year may be worse than any standalone max.
If losses are zero-inflated or clustered, VaR can behave counter-intuitively.
```

So neither `sum(PML_i)` nor `max(PML_i)` is probability-consistent total PML. The joint vector is the object.

---

## 5. When `max(A,B,C)` is valid as a metric operator

There are three separate `max` concepts.

### 5.1 OEP max - valid

```text
OEP_year = max(event_loss_1, event_loss_2, ..., event_loss_n)
```

This answers:

```text
What was the worst single event in the year?
```

It is not total annual loss.

### 5.2 Largest standalone peril - valid dashboard, not total risk

```text
largest_standalone_peril_pml = max(PML_A, PML_B, PML_C)
```

This can be useful as a dashboard label:

```text
Which standalone peril dominates the marginal PML table?
```

But it should never be labeled:

```text
Total PML
Total VaR
Total annual risk
```

### 5.3 Mutually exclusive annual states - rarely valid

```text
T_year = max(A_year, B_year, C_year)
```

This is valid only if A/B/C are mutually exclusive alternative labels for the same annual loss state. That is
rare for physical hazards. It is more plausible for competing models, not competing real perils.

---

## 6. EAL additivity and its caveats

Gross uncapped EAL is additive:

```text
EAL_total = E[A + B + C]
          = E[A] + E[B] + E[C]
```

This does **not** require independence.

But the caveats are load-bearing:

```text
E[min(A + B + C, TIV)] != min(E[A] + E[B] + E[C], TIV)

E[max(0, A + B - deductible)] != max(0, E[A] + E[B] - deductible)

E[BI(duration(A + B))] != BI(duration(E[A] + E[B]))
```

So the rule is:

| Loss basis | Can EAL be summed? | Caveat |
|---|---|---|
| Gross uncapped physical/economic loss | Yes, for attribution. | Event identity must already be clean. |
| Physical loss capped by shared TIV | Usually no. | Cap is nonlinear. |
| Net of deductible/limit | No. | Terms must apply inside simulation. |
| Gross economic with BI/duration | Usually no shortcut. | Duration and revenue are nonlinear/time-dependent. |
| Portfolio net | No. | Portfolio terms and dependence matter. |

---

## 7. Dependence: independent streams vs joint sampling

If A/B/C are independent and disjoint, independent sampling is a defensible V1 default.

```text
year y:
  draw A_y
  draw B_y
  draw C_y
  total_y = A_y + B_y + C_y
```

If A/B/C share a parent event, independent sampling is wrong.

```text
wrong:
  year 0010: hurricane wind
  year 0522: hurricane surge
  year 8844: hurricane tornado

right:
  year 0010: hurricane family = wind + surge + rainfall + TC tornado
```

If A/B/C are correlated but no event-family catalog exists, possible discussion options:

| Option | What it does | Caveat |
|---|---|---|
| Independent V1 | Sample streams independently and label assumption. | Understates or misstates joint tail when correlation is real. |
| Shared climate-year factor | A common activity multiplier affects several perils. | Captures broad dependence, not event-level co-occurrence. |
| Copula | Samples marginal annual vectors with dependence. | Can match correlation but not physical event structure. |
| Event-family catalog | Parent event produces child losses directly. | Best but most data/model work. |

Discussion lean: use event-family catalogs where parent events are concrete (hurricane, winter storm, wildfire,
portfolio swath). Use shared factors only as interim approximations.

---

## 8. Operator options and labels

| Option | Formula | Valid label | Invalid label |
|---|---|---|---|
| Joint sampled vector | `T_y = A_y + B_y + C_y` | Total annual loss distribution | - |
| Gross EAL sum | `EAL_A + EAL_B + EAL_C` | Gross uncapped EAL attribution | Net/capped EAL unless checked |
| Max standalone metric | `max(PML_A,PML_B,PML_C)` | Largest standalone peril PML | Total PML |
| Sum standalone PMLs | `sum(PML_i)` | Non-probabilistic stress / conservative stack | AEP-PML / VaR |
| OEP max by year | `max(event_losses in year)` | OEP annual max-event vector | AEP annual total |
| Same-component max | `max(A_component,B_component)` | De-dup/model selection | Total event loss |

---

## 9. Visual summary

```text
                         CLEAN EVENT LOSSES
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
          AEP annual vector                 OEP annual vector
          sum events/year                   max event/year
                 |                                 |
     +-----------+-----------+                     |
     |           |           |                     |
     v           v           v                     v
    EAL         VaR       AEP-PML               OEP-PML
   mean      quantile    quantile              quantile
                 |
                 v
               TVaR
             tail mean
```

No arrow in that diagram goes:

```text
PML_A + PML_B -> PML_total
max(PML_A,PML_B) -> total PML
```

Those can be scenario or dashboard views, but they are not total-risk metrics.

---

## 10. Open Decisions

| Decision | Options | Discussion lean |
|---|---|---|
| Cross-peril Total Loss V1 | independent / shared factor / event-family | Independent except explicit event families, loudly labeled. |
| `max(PML_A,PML_B,PML_C)` display | omit / dashboard only / total-risk metric | Dashboard only, never total-risk metric. |
| Sum of PMLs | prohibit / stress scenario | Stress scenario only, not probability-consistent PML. |
| Capped EAL reporting | sum capped EALs / joint capped mean | Joint capped mean. |
| Portfolio tail | sum asset PMLs / independent sum / shared event simulation | Shared event simulation when portfolio matters. |

---

## 11. Practical Rule

Do not ask:

```text
Which metric arithmetic is easiest?
```

Ask:

```text
Which annual vector does the decision require?
```

Then build that vector:

```text
AEP_year = total annual loss
OEP_year = worst single-event loss
```

and read the metric from it.
