# 02 - Full-CONUS Hail M1 Build

Status: first MRMS-only full-CONUS M1 run completed locally.

Plan reference:
[`docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md`](../../../../../docs/plans/hazard_conus_grid/hail/v1_mrms_only_grid_build.md).

## V1 Scope

This folder is for the **MRMS-only V1** full-grid M1 build:

```text
MRMS daily cell evidence
  -> one row per served CONUS cell
  -> annual severe-hail-day frequency
  -> empirical observed MESH size summaries
  -> QA/provenance flags
```

MYRORSS is not an input here for V1.

## Expected Inputs

- Served CONUS `cell_id` mask.
- MRMS V1 daily cell evidence produced by the M0 full-grid production path.
- Source inventory / denominator manifest.
- V1 metadata with source window, threshold, and aggregation rule.

## Expected Outputs

```text
data/hazard_conus_grid/hail/m1_mrms_only_hazard_layer_v1.parquet
data/hazard_conus_grid/hail/m1_mrms_only_hazard_layer_v1_summary.csv
data/hazard_conus_grid/hail/m1_mrms_only_hazard_layer_v1_metadata.json
```

Exact date/version suffixes can be added when the first artifact is built.

## Current Run

Producing notebook:

```text
01_mrms_v1_full_grid_hazard_layer.ipynb
01_mrms_v1_full_grid_hazard_layer.py
```

Input:

```text
data/hazard_conus_grid/hail/v1_mrms_only/
  m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
```

Output:

```text
data/hazard_conus_grid/hail/v1_mrms_only/
  m1_hazard_layer/run_id=20260618T040000Z_m1_mrms_only/
```

Summary:

| Item | Value |
|---|---:|
| M1 rows | 13,085 |
| Input M0 dates | 2,071 |
| Input M0 cell-day rows | 27,099,035 |
| Cells with any severe hail day | 12,111 |
| Cells with no severe hail days | 974 |
| Cells with raw MESH >= 300 mm | 585 |
| Extreme raw-MESH cell-days | 613 |
| Max raw annualized severe-day rate | 44.972839 days/year |
| Max raw MESH | 1,437.400 mm |

GCS upload status: local run completed, but direct `gcloud storage cp` upload is blocked until the active
account refreshes auth non-interactively:

```text
gcloud auth login
```

No Cloud Run was needed for M1 because this layer streams compact reconciled parquet partitions rather than
reading raw MRMS GRIB files.

## What The Full-CONUS M1 Build Asks

```text
full-CONUS M1 asks:
  for every served CONUS cell:
    what accepted MRMS date denominator applies?
    how many severe hail days occurred?
    what annual severe-day frequency is emitted?
    what observed MESH summaries and extreme-source flags are carried?
    what QA/provenance metadata travel with the row?
```

It does not ask:

```text
  what canonical solar loss is reportable?
  how should raw MESH extremes be de-biased?
  what EVT tail should be used?
```

Those are downstream risk and accuracy-upgrade questions.
