# M4 — Loss & metrics (shared engine, both sub-perils combined)

*The finale. Both convective-wind sub-perils' event streams sample into **one** annual-loss distribution per site —
each through **its own** M3 fragility curve — and every metric is read off that **one sampled distribution**, never
the expected-loss shortcut. The **basics-spot-on** core (the step the old model got wrong). Engine reused unchanged
from hail & wildfire.*

**Where this sits:** M3 (damage) → **M4 (loss & metrics)**. Plan:
[`docs/plans/convective_wind/m4_loss_metrics.md`](../../../../docs/plans/convective_wind/m4_loss_metrics.md) · aggregation rules:
[`discussion/convective_wind/04`](../../../../docs/extra/discussion/convective_wind/04_aggregation_and_double_counting.md). Notebook:
[`01_loss_metrics`](01_loss_metrics.ipynb) (built).

## The engine
One **compound-Poisson/NegBin Monte Carlo** (300k years). Per year: draw counts (strong wind Poisson; tornado
NegBin if over-dispersed), draw each event's **full realized loss** through **that sub-peril's own curve** (strong
wind: `dr_strongwind` × TIV; tornado: swept fraction × `dr_tornado` × TIV), **sum → AEP** (capped at TIV),
**max → OEP**. Both disjoint streams co-sampled into the same year. Metrics off the joint vector; **% of TIV
alongside $**.

## Results (real but small + approximate)
| | EAL | PML250 | TVaR99 |
|---|---|---|---|
| **Traverse** (proving) | 0.064% ($0.89M) | **3.99%** ($55.9M) | **4.88%** ($68.3M) |
| **Shepherds Flat** (baseline) | 0.006% ($0.07M) | 0.15% ($1.8M) | 0.35% ($4.2M) |

- **The low-vs-high payoff** on one unchanged engine: Traverse has a real catastrophic-tornado tail; Shepherds is
  near-flat — the correctly-small number where the hazard is genuinely low.
- **Strong wind ≈ 0** (EAL ~0.006–0.02% of TIV, by site) — the M3 known-answer check passes; the wind *damage* track
  is small-but-real, the disruption/degradation track is **deferred** (AWN-31).
- **Tornado is the tail** at Traverse (PML/TVaR ≫ EAL); **TVaR ≫ VaR** for the sparse tornado tail (AWN-16). The tail
  is *larger* than V1's reach-only curve because tornado now damages more at the same gust (AWN-32 mechanism).

## The doctrines, demonstrated
- **EAL additive** across sub-perils (linearity) — the attribution split sums to the total. ✓
- **Tail NOT additive**: summing per-sub-peril VaRs **mis-states** the joint — and **VaR is non-coherent**, so it
  is *not even a safe bound*. Here it **understates by ~26%** (joint VaR99 $13.1M vs sum $9.8M — *super-additive*
  for these zero-inflated, NegBin-clustered tails, the **opposite** of the textbook continuous case). Read every
  tail metric off the **joint**. *(The MC caught a wrong "overstate" claim in the prose — verification earned its keep.)*
- **Method 0 refused** for tails (DD-WN-13): EAL agrees (linearity survives), but the tail comes off the sampled
  distribution, never the expected-loss collapse.

## Inputs → outputs
M1 (λ, severity) + M2 (coupling) + M3 (two-curve LUT) + geometry (TIV) → `data/convective_wind/<asset>_wind_m4_metrics.json`
(EAL/VaR/PML/TVaR in $ and % of TIV + attribution) + `…_wind_m4_annual_vectors.parquet` (AEP/OEP per sim-year,
per sub-peril + combined).

## Decisions & assumptions
[DD-WN-12](../../../../docs/plans/convective_wind/decisions.md) (metrics off one shared MC, % of TIV) ·
[DD-WN-13](../../../../docs/plans/convective_wind/decisions.md) (never Method 0) ·
[DD-WN-16](../../../../docs/plans/convective_wind/decisions.md) (each sub-peril its own M3 curve). **AWN-16**
(tornado sparse → TVaR), **AWN-22** (single-site, portfolio correlation deferred), **AWN-26** (curves approximate),
**AWN-31** (strong wind ≈0), **AWN-32** (sub-peril severity differs).

**→ Wind × wind-farm M0→M4 is COMPLETE.** Deferred: calibrated turbine curves (`infrasure-damage-curves`), the
**disruption/degradation track** (AWN-31), hurricane (field-intensity), portfolio correlation, financial terms.
