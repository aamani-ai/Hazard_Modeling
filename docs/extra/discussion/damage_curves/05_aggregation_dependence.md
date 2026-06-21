# 05 · Aggregation dependence — independence vs cascade  🔴 OPEN

The blend `Asset_DR = Σ wᵢ·DRᵢ` treats subsystems as **independent**: subsystem *i* failing cannot raise
subsystem *j*'s damage. Real **cascade** (rotor loss → nacelle-bearing stress; an inverter fire spreading) is
not modelled.

```
   INDEPENDENCE (today)                  CASCADE (real, unmodelled)

   intensity --+--> rotor   (DRr)        intensity --> rotor --> nacelle --> ...
               +--> nacelle (DRn)                      (rotor loss raises nacelle
               +--> tower   (DRt)                       stress => extra damage)
               '--> ...
   Asset_DR = sum(wi * DRi)              Asset_DR > sum(wi*DRi) at high intensity
   (linear; subsystems independent)     (joint failure in the deep tail)
```

## The decision (Q6)

| Option | What it does | Trade |
|---|---|---|
| **(a) Keep independence** ← today | linear sum of subsystem DRs | simple; understates joint high-intensity failure |
| **(b) Pairwise conditional bumps** | add `i→j` damage coupling where evidence exists | targeted realism; needs evidence per pair |
| **(c) Full conditional model** | a damage-state dependency structure | most realistic; Gen-2 scope |

## Why it's lower-priority than Q1–Q4

It bites only at the **high-intensity tail** (where multiple subsystems fail together) and at lower event
frequency — so it caps how realistic the deep tail can be, but doesn't touch EAL or the body. The library
names conditional/cascade damage as a Gen-2 item (`aggregation-model.md`).

## To decide

1. (a) / (b) / (c) for v1 (likely (a), labelled).
2. If (b): which subsystem pairs have evidence, and for which peril?

*Links:* [`00 §3`](00_context_and_scope.md) · library `aggregation-model.md` ([infrasure-damage-curves](../../../../infrasure-damage-curves)).
