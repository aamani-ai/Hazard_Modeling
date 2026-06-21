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
| M4 loss & metrics | [`m4_loss_metrics/01_loss_metrics`](m4_loss_metrics/01_loss_metrics.ipynb) | ✅ **built** — wind-only EAL 0.012% / PML500 1.43% TIV |

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
- **M4 — loss & metrics.** Compound-Poisson MC at the **shared** λ (0.0116/yr, ±71% — 2-storm anchor) → wind-only
  **EAL 0.012% / PML250 0.42% / PML500 1.43% of TIV** (98.85% loss-free years). Wind is small at Amazon — the cell's
  material hazard is **surge**; this leg is the compound join partner.

## Honest caveats (carried in the manifests)

- **Curve Low-confidence** (reused convective_wind turbine curve, greenfield) — the dominant uncertainty; DR caps ~0.65.
- **λ is the shared coastal-event rate** (≤50 km, [JD-FL-15](../../../docs/plans/flood/decisions.md)), reused so wind &
  surge share one event frame; a standalone ≤100 km wind screen ([JD-TC-8](../../../docs/plans/hurricane/decisions.md))
  would admit more distant-but-windy storms and raise it — the documented upgrade.
- **Wind-only headline is the cell's own number**; the surge × wind **compound** combine is the separate flood-coastal
  × wind M4 step (reads M3's per-storm per-subsystem table, joins on `event_family_id`).
