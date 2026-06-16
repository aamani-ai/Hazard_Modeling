# Common — Storage Artifacts

Status: GCS root selected; V1 MRMS scale-out should use this contract.

Cloud execution, service-account, run-id, and artifact-format conventions live in
[`gcp_execution_and_storage_conventions.md`](gcp_execution_and_storage_conventions.md). This file focuses on
storage shape; the GCP convention file is the operating guide for actually running jobs.

## Storage Decision

Use the existing InfraSure benchmark bucket, under a dedicated product prefix:

```text
gs://infrasure-benchmark/hazard_conus_grid/
```

Access check on 2026-06-16:

- `gcloud auth list` active account: `divy@aamani.ai`;
- current local `gcloud` project: `vertexai-models`;
- `gcloud storage ls gs://infrasure-benchmark/` succeeded;
- existing top-level prefixes are `sources/` and `deliveries/`;
- write/read/delete probe under `hazard_conus_grid/_access_checks/` succeeded;
- first source-inventory proof upload created `hazard_conus_grid/dev/hail/v1_mrms_only/`.

Do not treat the current local `gcloud` project as the final execution/billing project. It proves local auth
is available; the runner/project choice still needs to be set before large jobs.

## Model-GPR Conventions To Reuse

From the neighboring `model-gpr` repo, reuse these storage habits:

| Convention | How it applies here |
|---|---|
| GCS is the durable lake; local data is a development mirror. | Large MRMS/M1/M2-M4 grid artifacts go to GCS; local `data/` keeps small proofs/manifests and temporary development outputs. |
| Bucket/root should be config-driven in code. | Scripts should default to `infrasure-benchmark` / `hazard_conus_grid`, but accept env/config overrides. |
| Manifest sidecars are required. | Every large parquet output needs metadata JSON plus row/source/QA summaries. |
| Do not overwrite existing GCS outputs accidentally. | Production upload code should fail if the destination exists unless an explicit `--force`/`overwrite=true` is passed. |
| Dry/local runs should preserve remote key shape. | Local development paths should mirror the GCS sub-tree under `data/hazard_conus_grid/`. |

Do **not** copy model-gpr's `plant_id/scope/variant` address shape. The grid product is keyed by product,
hazard, layer, version/run, record window, and sometimes asset type.

## Local Development Root

```text
data/hazard_conus_grid/
  common/
    benchmark_grid/
  hail/
    raw/
    m0_daily_cell_evidence/
    m1_hazard_layer/
    m2_m4_risk_metrics/
  wildfire/
    raw/
    m1_hazard_layer/
    m2_m4_risk_metrics/
```

Large rasters, large parquet files, and raw source caches should stay gitignored. Commit only manifests,
schemas, small summaries, and QA reports.

Local paths should mirror GCS where practical:

```text
data/hazard_conus_grid/hail/v1_mrms_only/...
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/...
```

The existing one-day proof remains at:

```text
data/hazard_conus_grid/hail/m0_mrms_v1_one_day_proof/
```

It is a local proof artifact, not the long-term GCS production layout.

The first run using this layout is:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T154907Z/
```

It is a seven-day source-inventory proof, not the final MRMS denominator.

The current full MRMS V1 source-denominator run using the same layout is:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/
```

It requested `2014-01-01` to `2026-06-15` and accepted 2,071 continuous source days from `2020-10-14`
through `2026-06-15`. This is a source-date denominator and batch contract only, not M0 cell evidence.

## GCS Prefix Layout

Use three top-level sub-prefixes under `hazard_conus_grid/`:

```text
gs://infrasure-benchmark/hazard_conus_grid/
  dev/                         <- active runs, rerunnable/intermediate
  releases/                    <- accepted product releases
  manifests/                   <- small cross-run indexes and release pointers
```

### Development / Active Build Prefix

MRMS-only hail V1 active outputs should use:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/
  m0_source_inventory/
    run_id=<YYYYMMDDTHHMMSSZ>/
      mrms_source_inventory.parquet
      mrms_source_inventory_summary.csv
      metadata.json
  m0_daily_cell_evidence/
    run_id=<YYYYMMDDTHHMMSSZ>/
      date=<YYYY-MM-DD>/
        part-*.parquet
      batch_manifest.parquet
      batch_summary.csv
      metadata.json
  m1_hazard_layer/
    run_id=<YYYYMMDDTHHMMSSZ>/
      m1_mrms_only_hazard_layer.parquet
      m1_mrms_only_hazard_layer_summary.csv
      metadata.json
  solar/
    m2_m4_risk_metrics/
      run_id=<YYYYMMDDTHHMMSSZ>/
        m4_risk_metrics.parquet
        m4_risk_metrics_summary.csv
        metadata.json
  qa/
    run_id=<YYYYMMDDTHHMMSSZ>/
      *.csv
      *.png
      metadata.json
```

`run_id` is an execution address, not a model version. It lets us rerun, compare, and discard intermediate
attempts without overwriting the previous attempt.

### Release Prefix

Only copy/promote here after QA:

```text
gs://infrasure-benchmark/hazard_conus_grid/releases/<release_id>/
  common/
    benchmark_grid_manifest.json
  hail/
    v1_mrms_only/
      m0_source_inventory/
      m0_daily_cell_evidence/
      m1_hazard_layer/
      solar/m2_m4_risk_metrics/
      qa/
  release_manifest.json
```

Use release ids like `v2026_06_hail_mrms_v1` or a later repo-standard release id. Release ids should be
event-driven, not automatic calendar churn.

### Manifest Prefix

Use this for small cross-run indexes:

```text
gs://infrasure-benchmark/hazard_conus_grid/manifests/
  active_dev_runs.csv
  releases.csv
```

These are convenience indexes only. The per-run and per-release metadata files remain authoritative.

## Durable Layer Rule

The grid should persist three build-facing layers and two durable product layers:

1. `m0_source_inventory`: accepted source-file denominator.
2. `m0_daily_cell_evidence`: daily target evidence by `hazard × cell_id × date`.
3. `m1_hazard_layer`: reusable hazard distribution by `hazard × cell_id`.
4. `m2_m4_risk_metrics`: final risk metrics by `hazard × asset_type × cell_id`.
5. `qa`: validation summaries, maps, and report/climatology sanity checks.

This keeps source validation separate from asset-loss fanout.

## Artifact Format Policy

Use:

- parquet for row-level layers and partitioned panels;
- JSON for authoritative metadata, nested provenance, run config, allowed-use rules, and caveats;
- CSV for flat human QA summaries and small manifests;
- PNG for visual QA only.

CSV should not be used as the source of truth for nested metadata. If a field is naturally hierarchical
or needs lists/dicts, it belongs in JSON.

## Metadata JSON Minimum

Each built artifact should have metadata JSON with:

- artifact name and relative/local/cloud path;
- hazard and asset scope;
- source products and vintages;
- grid version and `cell_id` convention;
- record span;
- row count;
- coverage/no-data count;
- model/code version when available;
- `run_id` and, when promoted, `release_id`;
- GCS path and local mirror path;
- write mode / overwrite policy;
- QA notes and caveat flags.

Small CSV manifests/summaries may mirror part of this information for human review, but the JSON metadata is
the authoritative sidecar.

## Write Policy

- First large remote write should be a controlled MRMS inventory output, not raw MRMS cache mirroring.
- Read NOAA public MRMS directly for V1 unless source mirroring is explicitly chosen later.
- Do not write into `sources/` or `deliveries/`; those are existing benchmark-grid prefixes with different
  semantics.
- Do not upload reportable/release artifacts directly to `releases/`; promote from a QA-passing `dev/run_id`.
- Do not overwrite an existing GCS object unless the run is explicitly marked `force`.
