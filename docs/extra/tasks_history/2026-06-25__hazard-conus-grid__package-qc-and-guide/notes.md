# Notes — implementation, metrics, verification, insights (2026-06-25)

## The package layout (as built)
```
shared/risk_engine/   engine/{monte_carlo,metrics,quantile,validate} · exposure.py (couple_areal) ·
                      vulnerability.py (capex_weighted_damage_ratio) · orchestration.py (run_cell_risk) ·
                      config.py (canonical ladders) · io_base/        ← imports NO peril
pipelines/hail/       config · mrms_m0 (build_daily_panel) · m1_hazard_layer (build_m1_hazard_layer) ·
                      plausibility_qc (apply_plausibility_qc) · coupling (hail_event_p_hit) · damage
drivers/conus_grid/   canonical_assets (CANONICAL_SOLAR, SEVERITY_POLICIES, SEED, MC_YEARS) ·
                      grid_driver (load_severe_events, run_grid) · entrypoint
```
M2 split: generic Minkowski `couple_areal(F,s,A)` in `shared/exposure`; hail field-mapping in
`pipelines/hail/coupling`. M3: curve framework in `shared/vulnerability`; the vendored hail×solar curve
(`data/hail/damage_curves/hail_solar_asset_capex_weighted.json`, cap 0.344) loaded by `pipelines/hail/damage`.

## Plausibility QC (on the real M1)
| | Raw M1 | After QC |
|---|---|---|
| max MESH severity | 1,437.4 mm | **203.2 mm** (US record, 8.0 in) |
| cells capped (>203.2) | — | **749** (164 in 203–300, **585** hard artifacts ≥300) |
| frequency-spike cells | — | **61** (λ > 8.9/yr = 99.5th pct), held out of reportable loss |
| reportable-eligible | — | 13,024 |
| frequency rate | — | **untouched** (verified identical) · raw severity kept |
Columns: 53 → **67** (additive). QC is a pure fn of the M1 → flows to the grid by reading the QC'd M1.

## Full-CONUS grid (QC'd, `run_id=20260625_conus_grid_hail_solar_v1_qcd`, 26,170 rows)
- 13,085 cells × 2 severity policies. National EAL ≈ **$34.4B** over the canonical grid; **mean 1.77% /
  median 0.45% / max 33.7%** of TIV (raw policy). `max PML₁₀₀ = 100%` = the TIV-capped frequency-spike cells.
- **Loss QC-invariant**: max abs diff vs the pre-QC baseline = **0.000e+00** (same λ, same per-event mesh,
  same seeds; the QC cap sits above the M3 100 mm clamp). raw-vs-cap policy diff ≤ **0.55 %TIV-pts** (≤7.8% on
  material cells) — solar loss is tail-insensitive because the curve saturates ~100 mm.

## Reproduction gates (the discipline)
| Gate (test) | Proves | Result |
|---|---|---|
| `shared/tests` engine smoke | M4 engine == worked notebook | **2.1e-16** |
| `pipelines/hail` M0 adapter | `build_daily_panel` == reconciled M0 (3 dates) | **0.0** |
| `pipelines/hail` M1 | `build_m1_hazard_layer` == 13,085-cell M1 (27M cell-days, 52 cols) | **0.0** |
| `pipelines/hail` QC | cap/flags correct, frequency untouched | validated |
| `drivers/conus_grid` smoke | driver == 5-cell smoke × 2 policies | **2.06e-16** |

## Run-id oracles (the reproduction substrate — keep these)
- M0 reconciled: `20260616T225000Z_m0_full_conus_reconciled` (27,099,035 rows · 13,085 cells · 2,071 dates)
- M1 raw (gate oracle): `20260618T040000Z_m1_mrms_only` · M1 QC'd: `20260625_m1_mrms_only_qcd` (67 cols)
- M2–M4 smoke (driver gate oracle): `20260618T045301Z_m2_m4_selected_cell_smoke` (5 cells × 2 policies)
- grid baseline (pre-QC): `20260625_conus_grid_hail_solar_v1` · grid QC'd: `20260625_conus_grid_hail_solar_v1_qcd`

## Commands / verification
```bash
cd Hazard_modeling && source .venv/bin/activate
pytest shared/tests pipelines/hail/tests drivers/conus_grid/tests   # 5 passed
python -m conus_grid.entrypoint                                       # → the full-CONUS QC'd risk layer
MPLBACKEND=Agg python Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/04_conus_grid_risk_maps.py
```
Shareable map page (Artifact): `https://claude.ai/code/artifact/aa396b96-a34c-4421-9806-44efefec93c2`

## Key insights
- **The QC validates against the science.** The ≥300 mm hard-artifacts visibly cluster over the **Ohio
  Valley** — exactly where the MESH literature ([`04`](../../discussion/conus_grid/hail/04_mesh_nature_and_qc_research.md))
  says the estimator over-reads — plus the CO Front Range and a radar cone-of-silence ring. The flag isn't
  arbitrary; it lights up the known failure regions.
- **The boundary held.** M2/M3 split cleanly into generic-`shared` + peril-`pipelines`; the engine stayed
  leak-clean; the driver reproduced the smoke to machine epsilon — evidence the "one engine, two drivers"
  abstraction is real, not aspirational.
- **The QC is cross-driver by construction** — asset-free → both drivers inherit it; the deep-per-asset
  *must* use it for outlier/sparse sites. That reuse is the whole point of the architecture.
- **Deploy is by-construction correct, CI-verified later** — the Dockerfile/workflow change ships the
  packages in the image; it builds at the next `workflow_dispatch` deploy (not yet exercised).
