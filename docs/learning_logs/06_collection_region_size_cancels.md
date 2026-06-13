# The Collection Region — Model Over an Area, and Its Size Cancels

*Why we model hail over a 50-mile region instead of "at the asset" — and why the radius we pick **washes
out** of the asset hit-rate, so the region is chosen for **homogeneity and data-consistency, not magnitude.***

**Status:** v1.0 · written 2026-06-11 · **Sourced from:** hail × solar, M0 (`01_noaa_hydronos`) + M2 coupling — the "why 50 miles?" question / [A1](../plans/hail/assumptions.md) · [DD-1](../plans/hail/decisions.md) · **Applies to:** any areal hit-or-miss peril whose asset rate is built as `λ_asset = λ_collection · p` over a collection region.

---

## Where this came from

M0 pulls NOAA Storm Events **within 50 miles** of Hayhurst, and M2 normalizes hit probability by that same
50-mi area `A ≈ 20,342 km²`. The natural question: **why 50? Isn't that an arbitrary knob — and didn't we
bias the answer by picking it?** Working it through, the answer is the opposite of what the worry assumes:
**the region size cancels out of the asset rate entirely.** 50 mi isn't a tuned parameter; it's a *consistent,
homogeneous* choice whose exact value doesn't move the result.

## Why it looks like a load-bearing knob — the trap

A region radius *looks* like it must change the answer, and you can argue it both ways, which is exactly why
it feels dangerous:

- *"Bigger region → more events counted → scarier."* (pushes the rate up), **or**
- *"Bigger region → any one event is less likely to hit our specific asset → safer."* (pushes hit-prob down).

Both are true — and that's the tell. If a parameter pushes two coupled terms in *opposite* directions, you
have to check whether it actually survives to the output, or whether it cancels. Here it cancels.

## The lesson

> **The lesson.** When the asset rate is built as `λ_asset = λ_collection · p`, the **collection-region size
> `A` cancels** — `λ_collection` grows with `A`, `p` shrinks with `A`, and the product doesn't depend on `A`
> *as long as the same region is used for both*. So choose the region for **homogeneity** (one uniform hazard
> climate) and **data-consistency** (match your data pull), **never** for its magnitude. The radius is not a
> tuning knob.

**The math, worked.** Let `ρ` = the regional event density (severe hail-events per km² per year, roughly
uniform over a homogeneous region). Then:

```
λ_collection  ≈  ρ · A                    (more area → proportionally more events)
p_i           =  (√Fᵢ + √s)² / A          (Minkowski hit prob — shrinks with area)

λ_asset  =  λ_collection · E[p]
         =  (ρ · A) · E[(√F + √s)²] / A
         =  ρ · E[(√F + √s)²]              ← A cancels exactly
```

`[OURS]` So **`λ_asset` depends only on the event *density* `ρ` and the footprint/asset sizes — the region
*radius* is gone.** `[REF]` This is the collection-area normalization standard in cat modeling (methodology
§5 / A21); what building added is the crisp realization that it makes the radius a *non-parameter*, and that
**homogeneity — not the radius — is the binding constraint.**

**Numerically.** Go from a 50-mi to a 100-mi region: `A` ×4, so `λ_collection` ≈ ×4 (≈29.6 → ≈118/yr) and
each `pᵢ` ≈ ÷4 — and `λ_asset` stays ≈ **0.26/yr**. The M2 known-answer checks show the same: `A` divides out.
50 mi is picked because it **matches NOAA's own query radius** (so the events we count and the area we
normalize by are the *same* footprint, and the NOAA↔MRMS cross-check is on one consistent region).

## What "spatially homogeneous" means here

This does **not** mean every square kilometre has identical storms. It means the chosen collection region is
treated as **one local hail regime**: event density per km², footprint-size mix, and hail-size/severity mix are
roughly stable across the 50-mi circle. Under that local-stationarity assumption, making `A` larger mostly
adds proportional event opportunities, which is the condition behind `λ_collection ∝ A`.

This is also different from **record homogeneity** in [DD-1](../plans/hail/decisions.md). DD-1 is about using
one consistent detection regime through time (MRMS rather than a raw NOAA+MRMS splice). This entry's
homogeneity constraint is spatial: the region should not cross into a meaningfully different hail climate.

So 50 mi is useful because it is large enough to collect events, but still local enough that Hayhurst is being
modeled inside one West Texas hail regime. A 500-mi region would not be acceptable just because `A` appears
in both terms; it would mix different storm climates and break the reason the cancellation is credible.

## How to recognize it next time (the same-region rule)

On every new areal peril/asset, the invariant to hold is: **estimate `λ_collection` and `p` over the *same*
region.** If you do, the radius is free — pick it for the two real constraints:

- **Homogeneity ceiling:** the region must be small enough that the hazard climate (the density `ρ` and the
  footprint-size mix) is ~uniform across it. Too big → it spans different regimes, `λ_collection ≈ ρ·A`
  breaks, and the cancellation degrades. *(Spatial cousin of the temporal "homogeneity > length" lesson —
  [learning_logs/01](01_extending_a_short_hazard_record.md).)*
- **Sample-size floor:** big enough to gather enough events that `λ_collection` isn't noise.
- **Data-consistency:** match the radius your data source already uses (here, NOAA's 50-mi query), so the
  rate and the cross-check live on one footprint.

The tell you've slipped: you're debating *what radius is "right"* as if it changes the loss, instead of
*"is my region homogeneous, well-sampled, and used consistently for both `λ` and `p`?"*

## Caveats and limits

- **Same region for both, or it doesn't cancel.** Estimate `λ_collection` over a 50-mi circle and `p` against
  a different area and the `A`'s no longer divide out — you'd get a real (spurious) dependence. This is the
  whole point of the "same-region rule" ([DD-1](../plans/hail/decisions.md)).
- **Cancellation needs homogeneity.** `λ_collection ∝ A` only holds if density `ρ` is ~uniform. The radius is
  free *within* the homogeneous range, not without bound.
- **Single-asset only.** For a **portfolio**, neighbouring assets' 50-mi circles overlap and share events —
  you can't treat each in its own independent circle without double-counting. Revisit then (A1's flagged
  trigger).
- **Areal hit-or-miss only.** This is the hail/tornado coupling. **Field-intensity** perils (hurricane,
  synoptic wind, earthquake) don't have a "hit probability" to thin — the asset is *always* in the field —
  so there's no `A` to cancel; the region question there is "where do I sample the field," a different shape
  (A21 coupling types).

## Cross-references

- **Assumption it explains:** [`../plans/hail/assumptions.md`](../plans/hail/assumptions.md) § **A1** (region = 50-mi circle).
- **Decision it rests on:** [`../plans/hail/decisions.md`](../plans/hail/decisions.md) § **DD-1** (MRMS spine + the same-region rule).
- **Siblings:** [`learning_logs/01`](01_extending_a_short_hazard_record.md) (homogeneity > length — the *temporal* version of the same instinct) · [`learning_logs/04`](04_two_datasets_one_peril_decompose.md) (the `λ_collection · p` decomposition this builds on).
- **Where it shows in code:** `Notebooks/hail/solar/m2_coupling/01_coupling.ipynb` (the `A` cancels in the known-answer checks).
- `[REF]` methodology §5 (coupling / collection-area normalization); A21 coupling types.
