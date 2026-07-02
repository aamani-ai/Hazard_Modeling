# Hail x Solar - M2-M4 Risk Metrics

Goal: prove the selected-cell hail M1 layer can drive the canonical solar downstream engine.

Notebooks (development progression). The **production path is now the package** —
`shared/` + `pipelines/hail/` + `drivers/conus_grid/`, driven by `conus_grid.entrypoint`. These notebooks
are the worked record, plus two that stay live. See the grid guide:
`docs/guides/building_a_hazard_asset_grid.md`.

```text
01_selected_cell_solar_smoke          earliest 4-cell smoke      [SUPERSEDED - kept as dev record]
02_hayhurst_reference_bridge          grid <-> deep cross-check  [SUPERSEDED - kept as dev record]
03_full_m1_selected_cell_solar_smoke  full-M1 5-cell smoke       [LIVE - the driver's reproduction-gate oracle]
04_conus_grid_risk_maps               full-CONUS risk maps       [LIVE - views the QC'd grid layer]
```

`01` and `02` predate the package (they carry inline engine code) and are **not** re-pointed - re-pointing
would rewrite history. The current engine + plausibility QC + full-CONUS driver live in the packages; `03`
stays because the driver reproduces it bit-for-bit as its gate, and `04` renders the full grid.

## Input - Older Four-Cell Pilot

```text
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_daily_panel_v2026_06_16.csv
data/hail/damage_curves/hail_solar_asset_capex_weighted.json
```

## Output - Older Four-Cell Pilot

```text
data/hazard_conus_grid/hail/solar/m2_solar_smoke_event_set_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.json
data/hazard_conus_grid/hail/solar/m4_solar_smoke_annual_vectors_v2026_06_16.parquet
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.json
```

The parquet annual vectors are an audit artifact and stay gitignored.

## Current Status - Full M1 Selected-Cell Smoke

The current smoke test has run from the **full-CONUS MRMS-only M1** artifact:

```text
notebook:
  Notebooks/hazard_conus_grid/hail/solar/m2_m4_risk_metrics/
    03_full_m1_selected_cell_solar_smoke.ipynb

run_id:
  20260618T045301Z_m2_m4_selected_cell_smoke

local:
  data/hazard_conus_grid/hail/solar/v1_mrms_only/m2_m4_selected_cell_smoke/
    run_id=20260618T045301Z_m2_m4_selected_cell_smoke/

gcs:
  gs://infrasure-benchmark/hazard_conus_grid/dev/hail/solar/v1_mrms_only/m2_m4_selected_cell_smoke/
    run_id=20260618T045301Z_m2_m4_selected_cell_smoke/
```

It used five selected cells:

| Role | Cell | State | Why |
|---|---:|---|---|
| `central_corridor_body` | 302001 | KS | Plains high-hail body cell. |
| `moderate_body` | 276114 | IA | Near-median severe-day cell. |
| `no_severe` | 306280 | AZ | Zero severe-day handling. |
| `high_frequency_suspicious` | 273305 | NY | Highest M1 frequency, explicit QA stress case. |
| `tail_qa` | 281823 | WY | Raw-MESH tail QA and capped-sensitivity test. |

The smoke produced:

```text
tables/mrms_v1_solar_smoke_cell_selection_20260618T045301Z_m2_m4_selected_cell_smoke.csv
tables/mrms_v1_solar_smoke_selected_cell_daily_panel_20260618T045301Z_m2_m4_selected_cell_smoke.csv
tables/mrms_v1_solar_smoke_event_set_20260618T045301Z_m2_m4_selected_cell_smoke.csv
tables/mrms_v1_solar_smoke_metrics_20260618T045301Z_m2_m4_selected_cell_smoke.csv
tables/mrms_v1_solar_smoke_annual_vectors_20260618T045301Z_m2_m4_selected_cell_smoke.parquet
metadata_20260618T045301Z_m2_m4_selected_cell_smoke.json
maps/*.png
```

QA status:

```text
all M4 engine checks passed
GCS upload_status = uploaded
uploaded objects = 9
```

The run used canonical solar:

- 100 MW capacity;
- 1.5 km2 solar footprint;
- 1,483 USD/kWp TIV basis;
- 250,000 simulated years per cell;
- Poisson V1 count model from the full M1 layer;
- capex-weighted solar hail damage curve;
- `raw_mrms` and `cap_100mm_sensitivity` severity-policy rows.

This is still not a reportable risk layer. It is a **provisional selected-cell smoke run** that proves the
metric schema and stochastic engine can consume full-M1 inputs while carrying frequency and severity QA flags.

The Hayhurst reference bridge has also run. It compares the `hayhurst_reference` grid smoke row to the deep
Hayhurst asset run and returns:

```text
pass_for_interface_bridge_not_calibration
```

That means the differences are explainable and no interface drift is apparent. It does not mean the grid smoke
metrics are calibrated.

## Modeling Notes

- M2 uses a gridded areal hit-or-miss approximation:
  `p_hit = min((sqrt(F_proxy) + sqrt(s_solar))^2 / A_proxy, 1)`.
- `F_proxy` is severe native-pixel area clipped to the cell, not a full connected storm footprint.
- M3 applies the existing solar hail damage curve to policy-specific MESH: raw or capped sensitivity.
- M4 samples annual event counts, then uses Bernoulli hit/miss and full conditional loss on hit.
- `p_hit` is never multiplied into loss as a deterministic shortcut.

## Next

Full-CONUS M2-M4 scaleout is **done**: the `conus_grid` driver runs all 13,085 cells off the QC'd M1 (both
`raw_mrms` and `cap_100mm_sensitivity` rows), with frequency-spike cells flagged + held out of reportable
loss. What remains is deferred accuracy + reuse work - see `docs/guides/building_a_hazard_asset_grid.md` §7:
the deep-per-asset driver adopting the same plausibility QC, MESH de-biasing, frequency pooling/shrinkage,
record extension, EVT/tail treatment, and the typed contracts. None is needed to *screen*; all are needed
before any grid loss is *reportable*.

## What The Grid Solar Risk Layer Asks

```text
grid solar M2-M4 asks:
  can the full-cell M1 hazard layer drive the canonical solar engine?
  what p_hit approximation is used inside a grid cell?
  what severity policy is used: raw MESH or capped sensitivity?
  do annual-vector and metric schemas match the deep asset engine?
  which cells are held out by plausibility QC?
```

It does not ask:

```text
  is the raw MRMS severity field fully calibrated?
  is the resulting loss layer reportable?
  are MESH de-biasing and EVT tail treatment complete?
```

This layer proves scale and interface discipline; reporting quality depends on the deferred accuracy work.
