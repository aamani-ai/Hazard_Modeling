# done/ — completed wind layer write-ups

Completion records for built layers (the wind analogue of [`../../wildfire/done/`](../../wildfire/done/README.md)
and [`../../hail/done/`](../../hail/done/README.md)). Each is a short "what shipped + outcomes + pointers" record,
written when a layer is finished — distinct from the forward-looking plan docs (`../m0_input_data.md`, etc.).

Wind is **Hazard 3 of 3** (hail ✅ · wildfire ✅ · wind). V1 builds the **convective-wind peril** — its two
sub-perils, **strong / straight-line wind [W]** first (site-conditioned, ASCE pre-integrated surface) and
**tornado [T]** second (areal hit-or-miss, path-aware Minkowski). The **separate hurricane / tropical-cyclone
peril** (field-intensity) is a distinct, deferred peril — *not* a convective-wind sub-peril — sharing only the
3-s-gust damage curve. Records fork per sub-peril **only at M2** (where the coupling differs); layer-0 / M0 / M1
and **M3 / M4 are shared** (one turbine curve; M4 combines both sub-perils into one annual-loss distribution per
site — EAL additive across them, the tail read off the joint).

| Layer | Record | Status |
|---|---|---|
| layer-0 — hazard definition | `layer-0-hazard-definition.md` | ✅ built 2026-06-17 ([plan](../00_hazard_definition.md)) |
| M0 — input data | `m0-input-data.md` | ✅ built 2026-06-17 ([plan](../m0_input_data.md)) |
| M1 — catalog | `m1-catalog.md` | ✅ built 2026-06-17 ([plan](../m1_catalog.md)) |
| M2 — strong-wind coupling | `strong-wind-m2-coupling.md` | ✅ built 2026-06-17 ([plan](../m2_coupling.md)) |
| M2 — tornado coupling | `tornado-m2-coupling.md` | ✅ built 2026-06-17 ([plan](../m2_coupling.md)) |
| M3 — wind-farm damage (shared turbine, **two sub-peril curves**) | `m3-damage.md` | ✅ built 2026-06-17 — *DR(μ)≈0 both; tornado onset ~44 m/s < strong wind ~54 m/s; all 10 known-answer checks pass* ([plan](../m3_damage.md)) |
| M4 — wind-farm loss & metrics (shared, combined) | `m4-loss-metrics.md` | ✅ built 2026-06-17 — *Traverse EAL 0.064% / PML250 3.99% / TVaR99 4.88%; Shepherds ≈flat; strong wind ≈0; tail off the joint* ([plan](../m4_loss_metrics.md)) |

*(All rows ✅ — **convective-wind × wind-farm is built end-to-end** (2026-06-17). The `Record` column names each
layer's intended write-up; outcomes are tagged inline above and detailed in the per-layer folder READMEs + the plan
docs. The asset cell lives at [`Notebooks/convective_wind/wind_farm/`](../../../../Notebooks/convective_wind/wind_farm/README.md).)*
