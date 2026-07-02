# M3 — Solar Damage (capex-weighted BoS curve, kW/m)

*Map the coupled **fire-line intensity (kW/m)** → a **capex-weighted BoS damage ratio**, then
`conditional_loss = Asset_DR × exposure × TIV`. Like hail: a curated **approximate** curve now (the InfraSure
library), accurate curves later. The InfraSure wedge — no incumbent has renewable-specific wildfire curves.*

**Where this sits:** M0 → M1 → M2 → **M3 (solar damage)** → M4 loss. Both solar assets. Plan:
[`docs/plans/wildfire/m3_damage.md`](../../../../docs/plans/wildfire/m3_damage.md).

## The curve (DD-W8)

**InfraSure `WILDFIRE × solar`** — 6 BoS subsystem logistic curves `DRᵢ(I)=Lᵢ/(1+exp(−kᵢ(I−x0ᵢ)))` on Byram
**kW/m**, sourced from the canonical `infrasure-damage-curves/data/master_curve_index.json` (params) +
midpoint capex weights. **Channel-1 physical only, d=10 m.** *(Legacy First-Street curve discarded — generic,
wrong axis.)* Approximate/temporary: Low/Low-Med confidence, d=10 m ±40%.

- **Blend:** `Asset_DR(I) = Σ wᵢ·DRᵢ(I)`. Weights sum ~0.70 → ~30% TIV unmodeled → **(A) non-damageable** in
  V1 (cap ~61% TIV), [AW-19](../../../../docs/plans/wildfire/assumptions.md). **LOTV:** emits the *conditional*
  loss (given a fire); occurrence/λ stays separate (reunited in M4's sampled engine).

## Inputs → outputs

M2 coupled (conditional kW/m severity × exposure) + the canonical curves + TIV →
`data/wildfire/<asset>_wildfire_m3_damage.parquet` (per-class conditional DR + loss) + `…_m3_summary.json`,
both assets.

**Next → M4 (solar loss & metrics):** the shared compound Poisson/NegBin Monte-Carlo — sample fires/yr, draw
per-fire conditional loss, aggregate → EAL/VaR/PML/TVaR off the sampled distribution, % of TIV.

## What Wildfire Solar M3 Asks

```text
M3 asks, for each conditional intensity class:
  what fire-line intensity in kW/m is being priced?
  which solar BoS subsystem curves apply?
  what damage ratio does each subsystem get?
  how do capex weights combine into Asset_DR?
  what full conditional loss is emitted given a fire in this class?
```

It does not ask:

```text
  how often does fire occur?
  how many fires happen this simulated year?
  what annual percentile is this?
```

Those are M1 and M4 questions. M3 prices severity conditional on occurrence.
