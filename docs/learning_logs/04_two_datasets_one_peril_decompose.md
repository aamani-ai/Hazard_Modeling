# Two Datasets, One Peril — Decompose by Component, Don't Pick a Winner

*Why "which dataset is primary?" is the wrong question when two sources cover the same peril with different
strengths — and what to ask instead: which *part* of the model comes from which source.*

**Status:** v1.0 · written 2026-06-09 · **Sourced from:** hail × solar, the NOAA-vs-MRMS frequency question / [DD-3](../plans/hail/decisions.md) · **Applies to:** any peril with two or more datasets of differing nature (most of them).

---

## Where this came from

Getting the hail **frequency** right forced the question: *is NOAA or MRMS our primary source?* The honest
answer turned out to be **neither** — because the two are good at *different things*, and crowning one
"primary" forces you to use it for something it's bad at.

## Why "pick a primary" is a trap

The model isn't one number from one dataset — it's an *equation with components*, and each component has its
own data needs. For hail frequency:

```
λ_asset  =  λ_collection   ×   p
            (regional rate)    (spatial factor)
```

- **`p` needs footprints.** NOAA is point reports — it *cannot* produce a footprint. Only MRMS can.
- **`λ_collection` needs a long, homogeneous count.** NOAA has the **length** (~30 yr) but is
  **population-biased + drifts**; MRMS is **unbiased** but **short** (~5.7 yr).

Force a single "primary" and you lose: pick NOAA and you have no footprint; pick MRMS and your rate is short.
Each dataset is the *best* source for a *different* component.

## The lesson

> **The lesson.** When two datasets cover the same peril with different natures, **decompose the model into
> its components and take each component from the dataset best suited to it** — then **reconcile on one event
> definition**, and **never naively splice a biased series** (calibrate it against the unbiased one instead).
> "Which dataset is primary?" → "which *part* from each?"

`[OURS]` This decompose-by-component framing is the general principle. `[REF]` It rests on the methodology's
coupling/frequency split (§4/§5 — `p` is frequency, footprint-derived) and extends the hail-specific
short-record treatment in [`learning_logs/01`](01_extending_a_short_hazard_record.md) into a reusable rule.

## The recipe

1. **Write the model equation** and name its components (here: `λ_collection`, `p`).
2. **For each component, ask which dataset is genuinely best** — and *why* (footprints? length? completeness?
   unbiasedness?). Assign it there.
3. **Check the components are on a consistent event definition + region** (methodology: don't estimate `λ`
   from one regime and `p` from another). If they aren't, define *one* event and make both consistent.
4. **If a long-but-biased series is involved, calibrate it** against the unbiased source in their overlap —
   don't bolt raw biased counts onto a clean component (the [`learning_logs/01`](01_extending_a_short_hazard_record.md)
   calibrated splice).

## The hail use case (the worked example)

- **`p` ← MRMS** (footprints; NOAA can't).
- **`λ_collection`:** MRMS-widen now (homogeneous, short → "decent"); **NOAA-calibrated extension** later
  (length, bias-corrected → "ideal").
- **MRMS = the physics anchor + the calibration truth; NOAA = the rate-extender (calibrated).** Not "NOAA
  primary raw" — that would import NOAA's population bias into `λ`. See [DD-3](../plans/hail/decisions.md).

## How to recognize it next time

Almost every peril will have ≥2 datasets of differing nature — **wind** (point stations vs reanalysis grids),
**flood** (gauges vs hydraulic models vs satellite), **wildfire** (perimeters vs remote-sensing vs reports).
The tell that you're in the trap: you're arguing *"which dataset is primary"* instead of *"which component
does each dataset serve best, and are they on a consistent event definition?"*

## Caveats and limits

- **Consistency is the catch.** Components taken from different sources must describe the *same events in the
  same region* — otherwise `λ_collection × p` mixes apples and oranges. Reconcile the event definition first.
- **Calibration ≠ free length.** Using a long biased series requires *modeling* its bias against the clean
  source (a real effort — `learning_logs/01` Method A), not assuming it away.
- This is the **frequency/coupling** version; severity (the damage curve) is its own multi-source question
  (the founder's two damage-curve repos — a separate track).

## Cross-references

- **Decision it generalizes:** [`../plans/hail/decisions.md`](../plans/hail/decisions.md) § DD-3 (and § DD-1).
- **The short-record sibling:** [`learning_logs/01`](01_extending_a_short_hazard_record.md) (the splice methods this rule invokes).
- **Principle it serves:** [`hazard_asset_specificity.md`](../principles/hazard_asset_specificity.md) — *standard interface, not standard physics*; the same decompose-don't-conflate discipline.
- `[REF]` methodology §4 (coupling) + §5 (frequency); the M0→M1 catalog research.
