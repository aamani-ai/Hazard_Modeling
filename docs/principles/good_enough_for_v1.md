# Good Enough for V1 — Ship Honest, Defer Accuracy

*Why a first version is a vertical slice that runs end-to-end and is honest about its limits — not a
calibrated product — and why a correct-minded, mistake-averse team needs this as an explicit guardrail.*

The other three principles are about **building correctly**. This one is about **how much to build before
you ship a V1** — the discipline that stops *getting the basics right* from sliding into *perfecting every
layer before anything runs end-to-end.*

---

## Why this document exists

This is the one principle grounded not in the old model's collapse, but in a tendency we watched in
*ourselves*. Building the hail catalog, we went deep — a data-product research pass, a sourcing triage, the
MESH-over-prediction literature (Murillo & Homeyer), MYRORSS record extension, an EVT severity tail. That
work is real and valuable. But each thread is a place you can spend weeks **improving a number** while the
end-to-end slice that would actually *deliver* still doesn't run.

The pull is strongest precisely because the team is conscientious: *basics spot-on* says get the foundation
right, and a mistake-averse instinct says don't ship something wrong. Both are correct — and together they
can quietly justify never stopping. This principle is the counterweight that makes that conscientiousness
productive: **get the structure right once; ship honest numbers; defer accuracy openly.**

---

## The principle

> **A V1 (hazard × asset) cell is a vertical slice that runs end-to-end and is *honest about its own
> limits* — not a calibrated, research-grade product.** Shipping the honest slice beats perfecting one layer
> while the others wait.

A V1 that runs M0→M4 with provisional labels teaches you more — and de-risks more — than a perfect M1 with
no M2–M4 behind it. The end-to-end slice is what surfaces the *real* dominant uncertainty (usually not the
one you were polishing).

## The stopping rule

> **V1 is *done* when the pipeline emits the target schema with (a) every known weakness flagged, and
> (b) nothing physically wrong silently entering a number.** Everything beyond that is V1.5 / V2 —
> **recorded as deferred, not done now.**

Honesty is the bar, not calibration. A flagged, provisional number that a reader can see the limits of is
shippable; a silently-wrong one never is.

## The test — one question, asked the moment you go deep

When you catch yourself going deep on a sub-problem, ask:

```
        does V1 NEED this to run end-to-end AND be honest?
                          │
              ┌───────────┴────────────┐
              ▼                         ▼
             YES                        NO  — it only makes the number *better*
        do it now                 ──►   DEFER: log it as V1.5/V2, flag the
   (honesty-load-bearing)               limitation in the doc, and move on
                                        (accuracy-load-bearing)
```

The distinction that resolves almost every case — **honesty-load-bearing vs. accuracy-load-bearing**:

| Load-bearing for HONESTY → **do now** | Load-bearing for ACCURACY → **defer** |
|---|---|
| *flag* the implausible MESH tail | *de-bias* the MESH (Murillo & Homeyer) |
| say "the deep tail is bootstrap-truncated" | fit an EVT severity tail |
| label grid loss "provisional · not reportable" | calibrate the damage curve to claims |
| Poisson + keep dispersion as a diagnostic | a pooled / regional Negative-Binomial fit |

The left column is cheap and mandatory. The right column is expensive and deferrable — and trying to do it
*before* the slice runs is the trap.

## The anti-pattern it guards against

> **The anti-pattern.** Research-spiralling to make a V1 *better* — reading papers to choose the optimal
> method, hand-validating individual cells, fitting a sophisticated model on top of an input you already
> know is the dominant uncertainty — before the end-to-end slice exists. It feels like rigor; it defers
> delivery and often polishes the wrong thing.

This is the delivery-side echo of *basics spot-on*'s warning ("more simulation is not more truth"): a fancy
severity fit on top of an uncalibrated curve is precise, confident, and not more true.

## Worked example — the MESH outlier decision

The first real application. Raw MESH produces physically impossible sizes (up to 1,437 mm). The
V1-good-enough handling:

```
  HONESTY-LOAD-BEARING (V1, now)            ACCURACY-LOAD-BEARING (V1.5 / V2, deferred)
  ─────────────────────────────            ───────────────────────────────────────────
  · physical-plausibility cap + flag        · MESH de-biasing (Murillo & Homeyer recipe)
  · keep the severe-day (frequency)         · EVT severity tail
  · lean on damage saturation (solar)       · pooled/regional frequency for sparse cells
  → the slice runs, honestly                → makes the number better, later
```

The principle says: **stop at the left column for V1.** That is not cutting a corner — it is shipping a
slice that is correct about what it claims and explicit about what it doesn't.

## Caveats and honest limitations

1. **This is not licence for sloppiness.** *Basics spot-on* is not negotiable — the math must be right and
   the units correct. "Good enough" applies to *calibration and coverage*, never to correctness.
2. **"Deferred" must be *recorded*, not forgotten.** The honesty only holds if every deferral is written
   down (assumptions register / the hazard anchor's limitations section) with the trigger to revisit it.
   A silent deferral is just a gap.
3. **Honesty-load-bearing items are mandatory.** Flagging a weakness is the price of shipping provisional —
   skip the flag and you've shipped a silently-wrong number, which this principle forbids as hard as
   *basics spot-on* does.

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [**Basics spot-on**](basics_spot_on.md) | The direct counterweight: basics-spot-on says *the foundation must be exactly right*; this says *don't gold-plate past correct-and-honest*. Together: right math, honest scope. |
| [**Modular from day one**](modularity_and_scaling.md) | Deferral is only safe because the deferred upgrade (EVT, de-biasing, pooling) slots in behind a stable interface later — modularity is what makes "ship now, improve later" a real option, not a rewrite. |
| [**Standard interface, not standard physics**](hazard_asset_specificity.md) | A V1 slice proves the *interface* end-to-end; per-pair accuracy is exactly the kind of thing you append later where the physics demands it. |

---

## Summary

A correct-minded, mistake-averse team's failure mode is not shipping garbage — it's never shipping, because
every layer can always be made *better*. The answer is an explicit ship line: a V1 cell runs end-to-end and
is honest about its limits; every known weakness is flagged; nothing physically wrong enters a number
silently; and everything past that is deferred *on the record*. Get the basics exactly right — then stop at
honest, and improve in the open.
