# Hurricane × Wind-farm — the per-turbine field-intensity cell (M2 → M4)

The per-(peril × asset) cell that **realizes the per-turbine field-intensity coupling** (the solar field is degenerate;
a wind lease is ~18 km across, so the field genuinely varies). It reuses the shared **hurricane storm catalog**
(M0/M1) and adds wind-farm-specific **coupling → damage → loss**.

**Magnitude metric: the 3-second peak gust (mph)** at each turbine (from the Holland field). Surge / TC rain are
flood's `[C]`/`[F]` sub-perils, cross-linked via `event_family_id` — not modeled here.

**Site — Amazon Wind US East (NC), 104 × 2 MW (TIV $291M)** — the **all-three flood wind site**. It is the **same
asset** as flood-coastal × wind, so the per-storm wind loss **joins the surge leg on `event_family_id`** for the
[JD-FL-12](../../../docs/plans/flood/decisions.md) compound combine — this cell supplies that wind leg.

> **M0/M1 are SHARED, reused — not rebuilt here.** Which RAFT storms reach Amazon (with `event_family_id`, category,
> near-site vmax) is catalogued in **flood-coastal M1** over both assets (Path 2, [JD-FL-19](../../../docs/plans/flood/decisions.md)).
> This cell **forks the asset at M2** — the repo's standard "M0/M1 shared peril · M2–M4 per-asset" layout. The storm
> set + λ come from `data/flood/amazon_wind_us_east_flood_coastal_m1_catalog.parquet`; tracks from the shared RAFT `.nc`.

| Layer | Notebook | Status |
|---|---|---|
| M2 coupling | [`m2_coupling/01_coupling`](m2_coupling/01_coupling.ipynb) | ✅ **built** — **per-node** field-intensity (non-degenerate; demonstrated) |
| M3 damage | [`m3_damage/01_damage`](m3_damage/01_damage.ipynb) | ✅ **built** — reused turbine wind curve → per-storm **per-subsystem** DR + `event_family_id` |
| M4 loss & metrics | [`m4_loss_metrics/01_loss_metrics`](m4_loss_metrics/01_loss_metrics.ipynb) | ✅ **built** — wind-only EAL 0.067% / PML500 5.70% TIV (≤100 km wind screen) |

## The build, layer by layer

- **M2 — per-node field-intensity.** Samples the Holland 3-s gust at **all 105 nodes** (104 turbines + collector) for
  the shared catalog, and **demonstrates the field is non-degenerate** across the lease (per-storm gust spread
  **median 4.4%, p95 21%, max 23%** — vs solar's <2%) → per-node sampling is required, not a convenience. Identical
  field math (Holland B 1.3, gust factor 1.2) to hurricane M1/M2. Output: `data/hurricane/tc_windfarm_m2_coupling.parquet`.
- **M3 — damage, the deliverable.** Reuses **convective_wind's turbine wind curve** (*hurricane wind on a turbine ≈
  straight-line wind* — same fragility, different source): strong-wind / feathered-survival branch → **aero reach only**
  (rotor / nacelle / electrical / substation; tower / foundation / civil not defeated by straight-line loading), asset
  DR caps ~0.65 (no tower-collapse total-loss mode — the honest limitation). Emits **per-storm, per-subsystem** wind DR
  stamped `event_family_id` → `data/hurricane/tc_windfarm_m3_damage.parquet` (the exact compound-combine input).
  Bimodal: bulk tiny (median ~0.3%, storms below IEC survival), rare Cat-3 close passage ~11% of TIV.
- **M4 — loss & metrics.** Compound-Poisson MC at the **≤100 km wind** λ (0.0751/yr, ±28% — 13-storm anchor) → wind-only
  **EAL 0.067% / PML250 3.59% / PML500 5.70% of TIV** (~92.8% loss-free years). Wind is modest at Amazon, but the
  ≤100 km screen (vs the old, wrong 50 km surge radius) raises it ~6×. The cell's material hazard is still **surge**;
  this leg is also the compound join partner (surge events are a subset of these wind events).

## Honest caveats (carried in the manifests)

- **Curve Low-confidence** (reused convective_wind turbine curve, greenfield) — the dominant uncertainty; DR caps ~0.65.
- **λ is the ≤100 km wind-screen rate** ([JD-TC-8](../../../docs/plans/hurricane/decisions.md), unified hurricane M1 — wind
  reaches ~100 km, so it is no longer screened at the 50 km surge radius). The **surge** leg keeps its ≤50 km rate
  ([JD-FL-21](../../../docs/plans/flood/decisions.md)); the two join on `event_family_id` and the 50 km surge storms
  remain a strict subset of these 100 km wind storms, so the compound combine stays consistent.
- **Wind-only headline is the cell's own number**; the surge × wind **compound** combine is the separate flood-coastal
  × wind M4 step (reads M3's per-storm per-subsystem table, joins on `event_family_id`).

## What The Hurricane Wind-Farm Cell Asks

```text
wind-farm M2 asks:
  for each storm:
    what gust reaches each turbine and collector node?
    how large is the within-farm gust spread?
    is per-node field sampling required?

wind-farm M3 asks:
  for each storm and subsystem:
    what turbine wind damage ratio applies?
    what per-subsystem DR should be stamped with event_family_id?
    what table will flood-coastal join to surge?

wind-farm M4 asks:
  across simulated years:
    what wind-only annual loss distribution results?
    how does this leg read before flood adds surge?
```
