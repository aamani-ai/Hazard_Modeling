# Hurricane × Solar — the asset cell (M2 → M4)

The per-(peril × asset) cell: it reuses the shared **hurricane catalog** (M0/M1) and adds solar-specific
**coupling → damage → loss**. Plan: [`docs/plans/hurricane/`](../../../docs/plans/hurricane/README.md).

**Magnitude metric: the 3-second peak gust (mph)** at the site (from M1's Holland field) drives this cell. Surge / TC
rain are flood's `[C]`/`[F]` sub-perils, cross-linked via `event_family_id` — not modeled here.

| Layer | Notebook | Status |
|---|---|---|
| M2 coupling | [`m2_coupling/01_coupling`](m2_coupling/01_coupling.ipynb) | ✅ **built** — field-intensity, degenerate (footprint spread median 0.5%) |
| M3 damage | [`m3_damage/01_damage`](m3_damage/01_damage.ipynb) | ✅ **built** — library HURRICANE×SOLAR (provisional); worst Cat-5 ≈ 41% TIV |
| M4 loss & metrics | [`m4_loss_metrics/01_loss_metrics`](m4_loss_metrics/01_loss_metrics.ipynb) | ✅ **built** — EAL 2.23% / PML500 41.5% TIV (point, provisional curve); Hayhurst 0 |

## Sites

Four solar sites ride the pipeline:

- **Hayhurst Texas Solar** (TX) — true-zero baseline (inland, no landfalls; λ=0).
- **Everglades Solar Energy Center** (FL) — the proving / high-TC end-to-end example.
- **Discovery Solar Center** (FL) — cross-link rider for flood-coastal's wind+surge compound combine.
- **LA3 West Baton Rouge** (LA) — the **all-three flood solar site**, present so flood-coastal × solar M4 has its
  hurricane-wind leg.

The cross-link / all-three riders (Discovery, LA3) ride the pipeline only to supply a wind leg for flood's compound
combine ([JD-FL-16](../../../docs/plans/flood/decisions.md)); they are **excluded from the hurricane headline** (M4
filters `cross-link`). Everglades + Hayhurst are the example pair.

## The build, layer by layer

- **M2 — field-intensity coupling (degenerate on solar).** On a ~1.4 km solar polygon at storm scale the field is
  **uniform** — demonstrated, not asserted: gust spread across the footprint is **median 0.5%, p95 1.1%**. So the plant
  sees one effective gust → **`value_exposed_fraction = 1.0`** ([JD-TC-2](../../../docs/plans/hurricane/decisions.md)).
  A rare ~8% max spread for a near-eye direct hit foreshadows why the wind-farm cell needs per-point field-intensity.
  Output: `data/hurricane/tc_m2_coupling.parquet`.
- **M3 — damage.** Maps each event's 3-s gust through the capex-weighted **HURRICANE × SOLAR** library curve
  (tracker-stow headline). Wind-immune subsystems → asset DR saturates ≈48% (no total-loss mode); the worst storm in
  the catalog (~175 mph Cat-5 at Everglades) reaches **≈41% of TIV**. Curve is **provisional** (the dominant
  uncertainty, owner-flagged). Output: `data/hurricane/tc_m3_damage.parquet` + vendored curve.
- **M4 — loss & metrics.** Compound-Poisson MC (event-based, no RP bridge) → **EAL 2.23% · PML250 37.4% · PML500
  41.5% of TIV** at Everglades (point estimate, tracker-stow curve; ±17% storm-rate uncertainty); Hayhurst = 0
  (true-zero control). Hazard side ASCE-validated; loss side curve-limited.

## Honest caveats (carried in the manifests)

- **Provisional damage curve** is the dominant uncertainty — swapping it (then re-running M3/M4) is the top upgrade;
  a loss-side benchmark (Hazus/NRI) is the missing second opinion on the loss number.
- **% of TIV is the headline**; dollars ride on the $/MW TIV estimate (secondary).
- **PML reported to 500-yr** (~1,000-yr catalog depth); annual-aggregate, bounded at 100% TIV.
