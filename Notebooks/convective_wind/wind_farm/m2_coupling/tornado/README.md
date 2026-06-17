# M2 — Tornado coupling (areal hit-or-miss · path-aware Minkowski)

*The **fork's areal branch**: thin M1's **regional** tornado rate (`λ_collection`, over the 150 km circle) down to
**this farm** (`λ_asset`), and compute how much of the farm a strike sweeps. Reuses **hail's Minkowski** machinery,
made **path-aware** (a tornado is a thin rectangle, not a compact disk).*

**Where this sits:** [M1 catalog](../../../m1_catalog/README.md) → **M2 (tornado)** → M3 damage → M4 loss. Sibling
fork: [`m2_coupling/strong_wind`](../../m2_coupling/strong_wind/README.md) (site-conditioned). Plan:
[`docs/plans/convective_wind/m2_coupling.md`](../../../../../docs/plans/convective_wind/m2_coupling.md). Notebook: [`01_coupling`](01_coupling.ipynb) (built).

## The method
`p_hit(EF) = (L+a)(w+a)/A` (capped at 1) — path length `L` × width `w` (per EF, from M0/02) + farm extent `a` =
√(farm area), over the collection region `A`. Then **`λ_asset = λ_collection · Σ ef_mix·p_hit`** (Poisson-thin per
EF — engine unchanged). On a strike, the conditional loss is **`swept_fraction × DR(gust) × TIV`** (V1 swept ≈
`w·min(L,a)/s` — the path's chord through the farm ÷ farm area; refined per-turbine intersection deferred).

## What `01_coupling` found
- **λ_asset (tornado strikes the farm):** **0.24/yr ≈ once per 4 yr (Traverse)** vs **0.0025/yr ≈ once per ~400 yr
  (Shepherds Flat)** — the ~100× proving-vs-baseline contrast.
- **Path-aware ≫ naive point ratio** (23×–77,000×) — a centroid lookup massively under-counts a spread-out farm's
  strike exposure (AWN-23). This is the old-repo error avoided.
- **Swept fraction is small** (≤~7% even at EF5) — a narrow path clips few of a big farm's turbines → the farm
  **diversifies** the tornado tail (a small compact farm would be lumpier). Strikes **re-weight toward violent EF**
  (long/wide paths over-represented among hits).
- `A` **cancels** (learning-06): the 150 km radius is a homogeneity choice, never a magnitude tuner. **Rare per
  site → sparse MC** → M4 reports **TVaR + SE** (learning-10).

## Inputs → outputs
M1 manifest (`λ_coll`, EF mix, severity) + M0/02 SPC parquet (per-EF path L,w) + M0/03 geometry (farm area, TIV) →
`data/convective_wind/<asset>_wind_m2_tornado_coupling.parquet` (per-EF p_hit / swept / P(EF|strike)) + `…_manifest.json`.

## Decisions & assumptions
[DD-WN-5](../../../../../docs/plans/convective_wind/decisions.md) (areal, path-aware Minkowski) · **AWN-21** (thinning), **AWN-23**
(per-turbine vs areal), **AWN-16** (sparse → TVaR), swept-fraction V1 treatment. **Next → M3** (the anchored
turbine curve supplies `DR(gust)`) **→ M4** (combine with strong wind; aggregation rules in
[discussion/convective_wind/04](../../../../../docs/extra/discussion/convective_wind/04_aggregation_and_double_counting.md)).
