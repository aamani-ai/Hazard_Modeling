# M2 — Coupling (the fork: two coupling buckets, one interface)

*M2 is the **one layer where the two convective-wind sub-perils diverge** — because their *coupling physics*
differ. So M2 (and only M2) **forks**; layer-0/M0/M1 above are shared, and **M3/M4 below are shared** (one turbine
curve; M4 combines both sub-perils into one annual-loss distribution). The fork lives **inside** this layer:*

| fork | bucket | what it does |
|---|---|---|
| [`tornado/`](tornado/01_coupling.ipynb) | **areal hit-or-miss** | path-aware Minkowski thinning `λ_asset = λ_collection·E[p_hit]` + swept fraction (reuses hail's machinery) |
| [`strong_wind/`](strong_wind/01_coupling.ipynb) | **site-conditioned** | thin pass-through, `p_hit ≈ 1`, no spatial factor (reuses wildfire's machinery) |

**Where this sits:** [M1 catalog](../../m1_catalog/README.md) → **M2 (coupling — forks here)** →
[M3 damage](../m3_damage/README.md) *(shared)* → [M4 loss](../m4_loss_metrics/README.md) *(shared, combined)*.
Plan: [`docs/plans/convective_wind/m2_coupling.md`](../../../../docs/plans/convective_wind/m2_coupling.md).

> **Why the fork is *only* here.** Coupling = *how the hazard reaches the asset*, and that is the one thing that
> genuinely differs between a narrow tornado path (areal hit-or-miss) and a broad strong-wind swath
> (site-conditioned). Frequency (M1), the turbine curve (M3), and the loss engine (M4) are the *same* for both —
> *standard interface, not standard physics* ([P1](../../../../docs/principles/hazard_asset_specificity.md)). Each
> fork emits the **same typed contract**; M4 reunites them into one sampled distribution.

**Outputs:** `data/convective_wind/<asset>_wind_m2_{tornado,strongwind}_coupling.parquet` + manifests (per fork).
**Next → M3** (the shared anchored turbine curve consumes both forks' severity).
