# 06 · Financial terms & scope edges  🔴 OPEN (the v1-box boundary)

Three exclusions from the v1 box that share a theme: the curve emits **gross physical occurrence loss**, and
several real layers sit *outside* it. This doc decides *when* each enters and how it interacts with the cap.

## (Q7) Financial terms — deductibles, limits, claims-made

| Option | What it does | Trade |
|---|---|---|
| **(a) Stay gross / occurrence** ← today | no terms applied at the curve | cleanest separation of physical from financial |
| **(b) Post-curve financial layer** | gross loss → net-of-deductible/limit before metrics | needed for a net number; adds nonlinearity |

```
   intensity -> [ DAMAGE CURVE ] -> gross physical loss -> [ deductible | limit ] -> NET
                  (this folder)      occurrence, capped       (06 / Q7: when?)        loss
                                     at REPLACEMENT value
                                     ( BI / economic loss can EXCEED the cap -- S9 )
```

**Cap interaction (watch this).** The "cap physical damage, not total loss" rule (Methodology §9) interacts
with deductibles/limits. v1 applies none, so the cap rarely binds and the capped-vs-uncapped EAL known-answer
check (hail A22) holds. **Once terms enter, the cap may bind frequently and that check breaks** — couples to
[`02`](02_metrics_and_tail_honesty.md).

**Claims-made vs occurrence.** Curves emit *occurrence* (date of damage); insurance triggers on *discovery*
(e.g. hail micro-cracks found at a later O&M visit). A financial layer must map occurrence → claims-made.

## The disruption boundary (operational vs permanent damage)

A damage curve assumes its output is **repair/replacement cost**. But below damage-onset much of the real loss
is **temporary outage / curtailment**, not destruction:

- **Wind** — below onset the turbine **feathers / cuts out** → generation loss, **zero physical damage**;
  strong wind is "mostly a disruption/degradation peril" (AWN-31). This is *why* strong-wind EAL ≈ 0 is an
  honest output, not a bug.
- **Wildfire** — low fire-line intensity may foul/derate without destroying → temporary capacity loss.
- **Duration / BI** — downtime → lost revenue; can dominate for energy assets (Methodology §7; hail A18).

```
   loss kind, by intensity:

     CURTAILMENT / FEATHER          |   PHYSICAL DAMAGE  (this curve)
     zero damage, generation lost   |   repair / replace cost
   --+-------------------------------+---------------------------------> intensity
     0                          damage onset
     |<-- disruption track / Performance tier -->|<------ damage track ------>|
        (this is why strong-wind EAL ~ 0 is an honest output, not a bug)
```

**Decision:** confirm these stay **out of the damage curve** (→ disruption track / Performance tier), and name
the seam where they re-attach. The curve must not be silently read as covering them.

## To decide

1. (a) / (b) for financial terms, and when (b) lands.
2. The occurrence → claims-made mapping owner.
3. Confirm disruption / derating / BI is out-of-curve, and where it re-enters (this tier's BI stage vs `model-gpr`).

*Links:* [`02 metrics`](02_metrics_and_tail_honesty.md) · [Methodology §7/§9](../../../google_drive_docs/README.md) ·
[convective-wind decisions (AWN-31)](../../../plans/convective_wind/decisions.md).
