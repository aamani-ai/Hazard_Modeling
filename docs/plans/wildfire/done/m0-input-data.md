# M0 — Input Data · completion record

**Status:** ✅ built · 2026-06-13 · **Plan:** [`../m0_input_data.md`](../m0_input_data.md) · **Notebooks:**
[`Notebooks/wildfire/m0_input_data/`](../../../../Notebooks/wildfire/m0_input_data/README.md)

## Objective

Meet and *understand* the raw wildfire hazard data before any modeling — both public USFS products, two
reference assets, every variable interpreted with its base (notebook_work principle). Method-neutral; no
losses, no events-as-objects.

## What shipped

| Notebook | What | Source |
|---|---|---|
| `01_wrc_geoplatform` | WRC 2.0: BP + CFL/FLEP4/FLEP8 (30 m), both assets, real site boundaries, site-scale maps, scale-verified, oozing characterized | public geoplatform ImageServers (no auth) |
| `02_fsim_rds` | FSim native **FLP1-6 histogram** (270 m), both assets, ΣFLP=1 verified, per-site histograms | public geoplatform ImageServers (no auth) |
| `02b_fsim_via_hydronos` | **Validation cross-check** (not the pipeline): Hydronos API reproduces both public products | legacy Hydronos key, read at runtime, one-off |

**Assets (a deliberate low-vs-high contrast):** **Hayhurst Texas Solar** (TX desert, baseline; same as hail,
cross-peril coherence) + **Matrix Pleasant Valley** (ID sagebrush, the high-fire proving asset, picked from a
38-asset WRC screen). ~190× exogenous-exposure contrast.

**Data products:** all public, CC BY 4.0, **no Hydronos / no secret** in the pipeline (DD-W3). Real site
boundaries from the OSM/EIA `powerplants_enriched_v2` dataset (Matrix = true 5.0 km² MultiPolygon; Hayhurst =
capacity-radius circle fallback).

## Key results

- **Scale factors verified** (WRC BP ÷10000; FSim FLP ÷100 → ΣFLP≈1; BP ÷1e6). Nesting `FLEP8 ≤ FLEP4` holds.
- **Cross-candidate comparison** (the M0 payoff): **BP agrees** across products (shared FSim lineage);
  **intensity diverges by regime** — FSim `FLEP4` lower than WRC at desert Hayhurst (0.10 vs 0.21), higher at
  sagebrush Matrix (0.66 vs 0.38). → **FSim FLP1-6 = M1 severity spine** (DD-W4); WRC = 30 m cross-check.
- **Hydronos cross-check:** reproduces *both* public products to ~2–3 dp → **DD-W3 empirically validated**
  (public loses nothing; Hydronos = a wrapper, paid for convenience not data).
- **Honest signal:** Hayhurst near-zero (desert grass, mean FL 2.15 ft, thin tail); Matrix material (BP
  4.7%/yr, mean FL 4.85 ft, real >4 ft tail). The model behaves: small where fire is rare, material where common.

## Decisions / assumptions touched

DD-W3 (public, no Hydronos — **validated**) · DD-W4 (FSim FLP1-6 spine) · DD-W5 (boundary-zonal, realized) ·
AW-4/5/6 (frame + scale + FIL breaks, verified) · **AW-15 (oozing — confirmed real & asset-specific, M2-critical)**.

## Learnings spawned

- [`learning_logs/07`](../../../learning_logs/07_one_simulation_two_products.md) — one simulation, two
  products: not interchangeable; validate the paid wrapper before paying.
- [`learning_logs/08`](../../../learning_logs/08_oozing_developed_pixels.md) — the asset pixel can be a
  developed "hole"; read the surrounding-fuel footprint.

## Open items carried to later layers

- **M2:** detect oozing per-asset; source on-site hazard from the surrounding-fuel footprint (the Hydronos
  `buffer_ring` is a ready tool). Settle CFL(headfire) vs FLEP(direction-integrated) basis.
- **M3:** FSim FLP1-6 histogram → BoS-weighted damage on kW/m (Byram); 30% unmodeled solar TIV (AW-19).
- **General:** 270 m undersamples tiny assets (Hayhurst = 8 px) — a resolution caveat for small footprints.

## Next

**M1 — catalog:** turn this evidence into a per-asset hazard catalog + the frequency process (BP → λ),
carrying the FSim FLP1-6 histogram as the severity spine.
