# M2 — Coupling (the active plan) · *field-intensity, the third bucket — degenerate on solar*

*The first per-(peril × asset) layer: how the hurricane wind **field reaches the solar asset**. This is the repo's
first **field-intensity** primary build — and, honestly, its **spatially-degenerate** form on a small solar polygon
([JD-TC-2](decisions.md)). The full per-point field-intensity proof is the wind-farm cell (**built**, Amazon Wind Farm US East); here the coupling is
thin because M1 already sampled the field.*

**Where this sits:** layer-0 → [M0](m0_input_data.md) → [M1](m1_catalog.md) → **M2 (coupling)** →
[M3](m3_damage.md) → [M4](m4_loss_metrics.md).

---

## The coupling type — field-intensity (vs the two already built)

`[FRAME]` Three coupling types ([Notebooks/README](../../../Notebooks/README.md)): **areal hit-or-miss** ·
**field-intensity** · **site-conditioned**. **Hurricane wind = field-intensity** — *sample a continuous field at
the asset*. Contrast:
- **hail** (areal): a finite footprint covers or misses the plant → loss fraction from geometry (Minkowski).
- **wildfire/flood** (site-conditioned): a field × per-asset susceptibility (fuel / elevation).
- **hurricane** (field-intensity): the field is sampled *at the asset* and read straight into the damage curve —
  no hit-or-miss geometry, no susceptibility modifier.

## Why it's degenerate on solar (stated, not hidden)

A solar farm is a **dense areal polygon ~1 km across**; a hurricane field varies on the scale of the
radius-of-max-wind (~tens of km). So across the footprint the field is **~uniform** → sampling it reduces to **one
value at the centroid**. Operationally this looks like the site-conditioned perils already built (read one hazard
value at the site). **V1 says so plainly** ([JD-TC-2](decisions.md)): it builds the field-intensity *machinery* and
applies it at a point; the per-point variation that makes field-intensity distinctive is exercised at the **wind-farm
cell** (**built**, Amazon Wind Farm US East — turbines span tens of km → the field genuinely differs turbine-to-turbine).

## What M2 actually does (thin, because M1 pre-sampled)

M1 already produced the **3-s gust at the site centroid per event**. M2's job is just to turn that into the
**per-event exposure contract** M3 reads — a one-line coupling for solar:

```
per event:  gust_3s_mph  →  (value_exposed_fraction = 1.0 for a uniformly-covered dense polygon)
```

- **`value_exposed_fraction = 1.0`** — at storm scale the whole farm sees the same gust, so the entire TIV is
  exposed to that gust (contrast hail's areal fraction or flood's inundated fraction). ([ATC-12](assumptions.md),
  [ATC-13](assumptions.md))
- **No Minkowski, no susceptibility modifier** — those belong to the other two coupling types.
- **Optional robustness check** — if M1 emitted a small grid over the footprint, report the gust min/mean/max across
  the polygon to *demonstrate* the field is ~uniform (the evidence behind "degenerate"), then collapse to the mean.

## The contract M3 reads

```
event_id · event_family_id · site_id · gust_3s_mph · value_exposed_fraction(=1.0)
```

M3 maps `gust_3s_mph` through the hurricane-wind × solar damage curve; `conditional_loss = DR(gust) ×
value_exposed_fraction × TIV`.

## Validation — the M2 known-answer checks

1. **Uniformity check** — gust spread across the footprint ≪ the gust level (justifies `fraction = 1.0` and the
   "degenerate" label).
2. **Baseline** — Hayhurst events near-zero gust → exposure carries ~no damage downstream.
3. **Pass-through integrity** — every M1 event appears once in the M2 contract; gusts unchanged (M2 adds exposure,
   not magnitude).

## Outputs

```text
data/hurricane/<asset>_tc_m2_coupling.parquet    per-event gust + value_exposed_fraction (the M3 contract)   (gitignored)
data/hurricane/<asset>_tc_m2_manifest.json       coupling type, fraction rule, uniformity-check result        (kept)
```

## Assumptions surfaced (this layer)

[ATC-12](assumptions.md) (field-intensity, degenerate on solar) · [ATC-13](assumptions.md) (solar dense polygon,
`fraction=1.0`).

## Open questions

- **Grid vs centroid** — sample one value or a small footprint grid (to *show* uniformity)? Cheap; recommended for
  the uniformity check, then collapse.
- **Partial-coverage edge case** — a storm whose RMW is small and near the footprint edge could in principle vary
  across a large plant; flag if the uniformity check ever fails (would foreshadow V2's per-point need).

**Next → [M3 (damage)](m3_damage.md):** map the per-event 3-s gust through the **`infrasure-damage-curves`
hurricane-wind × solar** curve → conditional loss per event.
