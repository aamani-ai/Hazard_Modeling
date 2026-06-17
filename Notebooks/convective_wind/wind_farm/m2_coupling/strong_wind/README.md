# M2 — Strong-wind coupling (site-conditioned · p_hit ≈ 1)

*The **fork's site-conditioned branch** — and **deliberately thin**, which is *correct*, not a shortcut. A
broad-swath strong-wind event has **no hit-or-miss**: if it reaches the region the whole farm is inside it
(`p_hit ≈ 1`), and M1 already read the per-site rate + severity off the ASCE return-period surface. So M2 is the
**honest pass-through** — **no Minkowski, no spatial factor.** Reuses **wildfire's thin M2**.*

**Where this sits:** [M1 catalog](../../../m1_catalog/README.md) → **M2 (strong wind)** → M3 → M4. Sibling fork:
[`m2_coupling/tornado`](../../m2_coupling/tornado/README.md) (areal). Plan:
[`docs/plans/convective_wind/m2_coupling.md`](../../../../../docs/plans/convective_wind/m2_coupling.md). Notebook: [`01_coupling`](01_coupling.ipynb) (built).

## What `01_coupling` confirmed
- **Site-conditioned handoff:** `p_hit = 1`, `exposure_fraction = 1`, **`λ_asset = M1 λ` unchanged** (0.90/yr
  Traverse · 0.36/yr Shepherds Flat) — **no `λ_collection · p` thinning, no spatial factor.** The asset reads its
  local RP gust; severity (Gumbel/exponential, ξ≈0, capped at L) passed through unchanged.
- **This is a thin coupling × a ≈0-damage curve** (AWN-31): strong wind carries through M3/M4 end-to-end but
  contributes **≈0 catastrophic loss** (the honest small number + the M3 known-answer check). Its *material* impact
  — operational disruption + fatigue — is the **deferred disruption track**, not this damage track
  ([discussion/convective_wind/01 §7a](../../../../../docs/extra/discussion/convective_wind/01_scope_and_sub_peril_taxonomy.md)).
- **Portfolio correlation** (broad swath → correlated across farms) is **documented + deferred** (AWN-22) — V1 is
  single-site.

## Inputs → outputs
M1 strong-wind manifest (`λ`, Gumbel severity, TIV) → `data/convective_wind/<asset>_wind_m2_strongwind_coupling.parquet`
(λ_asset, p_hit=1, exposure=1) + `…_manifest.json` (severity passthrough, correlation-deferred flag).

## Decisions & assumptions
[DD-WN-4](../../../../../docs/plans/convective_wind/decisions.md) (site-conditioned, p_hit≈1; reuse wildfire) · **AWN-20**
(no spatial factor), **AWN-22** (single-site, portfolio correlation deferred), **AWN-31** (damage ≈0; disruption
deferred). **Next → M3** (the shared anchored curve returns ≈0 here) **→ M4** (combine with tornado; aggregation in
[discussion/convective_wind/04](../../../../../docs/extra/discussion/convective_wind/04_aggregation_and_double_counting.md)).
