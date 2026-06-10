# Notebooks — hazard modeling, organized `peril → asset`

Worked, end-to-end notebooks for the **Hazard Risk** tier. The folder layout mirrors the model
itself — a **(peril × asset)** matrix — and turns on one structural fact:

- **M0 (raw data) + M1 (event catalog + frequency) are the PERIL** — *asset-independent*. A hail
  catalog over a region is the same whether a solar farm or a wind farm sits under it.
- **M2 (coupling) → M3 (damage) → M4 (loss & metrics) are the (peril × asset) CELL** — they
  specialize to the asset's geometry, fragility, and value.

So perils are top-level folders; each asset is a subfolder that **reuses the shared catalog** and
adds its own coupling/damage/loss.

```
Notebooks/
  hail/                 ← peril: shared catalog (M0 raw data, M1 events + frequency)
    m0_input_data/  m1_catalog/
    solar/              ← asset: M2 coupling · M3 damage · M4 loss & metrics   ✅ built end-to-end
    # wind/             ← onshore wind farm — next
  # wildfire/ , windstorm/ , flood/ …   ← same shape, later
```

## The matrix — what's built, what's next

Rows = perils, columns = asset types; each cell = the **coupling type** (how the hazard *reaches* the
asset). This is the heart of **"standard interface, not standard physics"**
([principle](../docs/principles/hazard_asset_specificity.md)): every cell runs the *same* M0→M4
interface, but the **coupling physics changes per (peril × asset)**.

| Peril ↓ \ Asset → | Solar PV *(dense areal polygon)* | Onshore wind *(turbine point-cloud)* | Offshore wind | BESS |
|---|---|---|---|---|
| **Hail** | **areal hit-or-miss ✅ built** | per-turbine hit-or-miss — **next** | — | areal (point) |
| Tornado | areal hit-or-miss | per-turbine hit-or-miss | — | — |
| Straight-line / synoptic wind | field-intensity | field-intensity (per turbine) | field-intensity | field-intensity |
| Hurricane wind | field-intensity | field-intensity | field-intensity | field-intensity |
| Wildfire (flame) | site-conditioned | site-conditioned | — | site-conditioned |
| Flood | site-conditioned | site-conditioned | (surge) | site-conditioned |
| Winter (snow / ice) | field-intensity | field-intensity | — | field-intensity |

✅ = built end-to-end. Everything else is roadmap. **The three coupling types** (the M2 physics):
**areal hit-or-miss** (finite footprint covers the asset or misses — Minkowski `(√F+√s)²/A`) ·
**field-intensity** (continuous field sampled at the asset) · **site-conditioned** (field × per-asset
susceptibility, e.g. elevation / fuel). Source: A21 coupling-type dispatch + A12 peril×asset taxonomy
(in `infrasure-hazard-competitive-research/learnings/architecture/`).

## Start here

- **[`hail/`](hail/README.md)** — the hail peril (shared catalog + the per-asset pipelines).
- **[`hail/solar/`](hail/solar/README.md)** — hail × solar, the first cell built end-to-end (M2→M4),
  with the headline risk numbers.

## Why solar and a wind farm differ (the next build)

A **solar farm** is a *dense areal polygon* — panels fill a contiguous boundary, so "did the footprint
cover the plant?" ≈ loss fraction → **areal hit-or-miss**. A **wind farm** is a *sparse cloud of point
turbines* (we have the turbine lat/longs) scattered across a large lease — so a bounding-polygon area
*overcounts*; you intersect the footprint with the **turbine points** (which turbines are hit), and
wind loads sample a **continuous field at each turbine**. Same M0→M4 interface, genuinely different M2
coupling. (A21 flags this as the *"wind-farm open question"* — the coupling geometry is the design
decision, not yet built.)

## Environment

`source ../.venv/bin/activate`, then register the kernel:
`python -m ipykernel install --user --name hazard_modeling`. Keep heavy data out of git
([`../.gitignore`](../.gitignore)) — read from `data/` or cloud sources rather than committing large files.
