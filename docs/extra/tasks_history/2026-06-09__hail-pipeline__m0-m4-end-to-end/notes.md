# Notes — implementation, commands, verification, metrics

## The pipeline (file → what it does → output)

| Layer | Notebook (`.py`+`.ipynb`) | Output (in `data/hail/`) |
|---|---|---|
| M0 | `m0_input_data/01_noaa_hydronos` | `hayhurst_hail_m0_noaa_50mi.parquet` (373 reports, 1996→2024) |
| M0 | `m0_input_data/02_mrms_aws` | demo-window M0 + raw tiles cache `mrms_raw/` |
| M0 (wide) | `scripts/scan_mrms_record.py` | `hayhurst_hail_m0_mrms_202010_202606.parquet` (2063 days, 158 hail-days) |
| M1 | `m1_catalog/01_event_catalog` | `…_m1_catalog.parquet` (GeoParquet, 158 events) + `.geojson` + `…_m1_manifest.json` |
| M2 | `m2_coupling/01_coupling` | `…_m2_coupled.parquet` + `…_m2_summary.json` |
| M3 | `m3_damage/01_damage` | `…_m3_damage.parquet` + `…_m3_summary.json` (curve spec: `damage_curves/hail_solar_asset_capex_weighted.json`) |
| M4 | `m4_loss_metrics/01_loss_metrics` | `…_m4_annual_vectors.parquet` + `…_m4_metrics.json` |

## Commands used

```bash
# Environment: .venv with python3.12 (kernel "hazard_modeling"); deps in requirements.txt (+ geopandas, shapely added this session)
source .venv/bin/activate

# Notebook authoring/execution (jupytext percent .py ↔ .ipynb):
jupytext --to notebook NB.py                      # generate .ipynb (no outputs)
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 NB.ipynb
jupytext --to notebook --update NB.py             # markdown-only change → preserve executed outputs (no re-run)

# Stage-1 widening (the heavy data pull — concurrent, resumable, cache-first; ~10-20 min):
python scripts/scan_mrms_record.py 2020-10-15 2026-06-08

# Re-run chain after a data/curve change: M1 → M2 → M3 → M4 (each reads the prior layer's parquet)

# Damage-curve repo (cloned + symlinked, gitignored):
git clone https://github.com/Divi-patel/infrasure-damage-curves.git   # into the siblings dir
ln -sfn /Users/divy/.../infrasure-damage-curves infrasure-damage-curves

# Publish (SSH as D-ivyy — NOT gh HTTPS, which lacks `workflow` scope):
git remote set-url origin git@github.com-work:D-ivyy/Hazard_Modeling.git
git push -u origin main
```

## Verification

- **Known-answer checks pass** in M2 (Minkowski identities) and M4 (EAL≈λ·E[p·loss]; Poisson zero≈exp(−λ_asset);
  NegBin Gamma-Poisson reproduces mean μ + Fano φ — confirmed by a 5M-draw sim in the validation audit).
- **Math-validation workflow** (23 agents, 6 areas × adversarial verify) → **sound, no calc errors**.
- **Push safety:** `git check-ignore` confirmed `.env`, `.venv`, `*.parquet`, `*.gz` tiles, symlinks all
  excluded; `git ls-files | grep -iE "\.env|\.gz|\.parquet|symlinks"` → empty on the remote.

## Metrics (real, record-limited)

| | value |
|---|---|
| λ_collection (regional hail-days/yr, fitted) | **29.6** (Fano φ = 3.37 → NegBin) |
| λ_asset (asset hit rate) | **0.26/yr** (~1 every 3.8 yr) |
| asset damage curve cap | **~34%** of TIV |
| **EAL** | $2.09M (**5.7%** of TIV) |
| VaR₉₉ (AEP-PML₁₀₀) | $19.97M (**54%**) |
| VaR₉₉.₆ (AEP-PML₂₅₀) | $22.73M (62%) |
| OEP-PML₁₀₀ | $12.52M (34%) |
| TIV (asset value, A19) | $36,778,400 (registry; = old model's asset_exposure) |

158 hail-days over 5.65 yr; sizes to 118.5 mm (4.67″); footprints to 1913 km². Zero-loss years ≈ 77%.

## Key insights / lessons

- **The whole rebuild exists to fix 3 old-repo bugs** — LOTV (spatial factor as a loss multiplier), OEP/AEP
  frame mismatch, point spatial-factor under-count. All three are now correctly handled **and validated**.
- **Homogeneity > length** for frequency; **decompose-by-component** for multi-source (`learning_logs/01,04`).
- **The damage curve is 3 coupled choices** (fragility × representation × value-allocation), and value-allocation
  is a *financial* decision — caps & levels come from it (`learning_logs/05`).
- **Complex raw data earns a from-scratch pass** (NOAA easy = a table; MRMS hard = a gridded field) (`learning_logs/03`).
- **Metrics honesty:** real but *record-limited* — deep tail (1-in-250+, OEP) is bootstrap-truncated (A23 → EVT);
  EAL ~5.7% is somewhat high, likely because **MESH over-forecasts** (FAR ~30–50%) inflating the hail-day count
  → the NOAA-calibrated extension (DD-3 Stage 2) should bring it down.
- **The `mrms_raw/` cache (905 MB) is gitignored** → a fresh clone must re-run `scripts/scan_mrms_record.py`
  before re-executing M1+ (or just trust the committed manifests/summaries).
- **Push gotcha:** use SSH `github.com-work` (= D-ivyy) for this account; gh HTTPS token lacks `workflow` scope.
