# 03 · Value-allocation & TIV — the sleeper  🔴 OPEN

The cap is set by **allocation, not physics** (`Asset_DR` caps at `Σ wᵢ·Lᵢ`). So how we allocate value across
subsystems, and what TIV we divide by, silently drives **every % -of-TIV metric** we report (%-of-TIV is the
[house display](../../../plans/hail/assumptions.md)).

```
   TIV |<================================ 100% ================================>|
       [ PV modules | tracker ][ inverter, substation, civil  (immune, DR=0) ][ sunk/soft ]
         w.32,L.95    w.10,L.4                                                  land/IDC/fin
       |<- AT-RISK: cap = sum(wi*Li) ~ 34% ->|<------ contributes 0 ------>|<- not at-risk ->|

   the CAP is set by ALLOCATION, not physics.
   leaving sunk/soft in the denominator makes %-of-TIV read artificially LOW.
```

## The decision (Q4)

| Option | Basis | Trade |
|---|---|---|
| **(a) Generic capex** ← today | NREL ATB / LBNL default weights | fast, consistent; %-of-TIV reads low & unreconciled (capex includes sunk/soft costs not truly at-risk) |
| **(b) Plant-specific at-risk value** | replaceable physical value per subsystem, per asset | most accurate; needs per-asset data |
| **(c) Generic + mandatory TIV reconciliation** | defaults, but a reconciliation step against the true valuation basis | pragmatic middle |

## The two distinct issues

- **Allocation across subsystems** — sets the cap and the blend. Generic NREL vs plant-specific.
- **The TIV denominator** — generic capex includes interconnection, land, financing (sunk/soft) that aren't
  at-risk to a hail swath; dividing physical loss by full capex makes %-of-TIV read artificially low. The
  valuation basis (TIV vs replacement vs insured) is **unpinned** (hail A19 caveat) and scales every dollar
  metric linearly.

## Current stance & status

Generic capex defaults, user-overridable (library `aggregation-model.md`); TIV = canonical per-kW × capacity,
basis unstated. 🔴 **Open** — flagged as the "sleeper" financial decision in
[learning-log 05](../../../learning_logs/05_damage_curve_three_coupled_choices.md).

## To decide

1. (a) / (b) / (c) for v1.
2. Pin the valuation basis (TIV vs replacement vs insured).
3. If reconciling: which cost lines are "at-risk physical" vs "sunk/soft".

*Links:* [`00 §3/§5`](00_context_and_scope.md) · [LL05](../../../learning_logs/05_damage_curve_three_coupled_choices.md) ·
[hail A19](../../../plans/hail/assumptions.md).
