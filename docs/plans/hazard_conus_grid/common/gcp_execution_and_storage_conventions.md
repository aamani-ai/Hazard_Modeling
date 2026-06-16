# Common - GCP Execution and Storage Conventions

Status: active operating convention for CONUS-grid cloud execution.

## Purpose

This document records how `hazard_conus_grid` runs jobs on GCP and writes artifacts to GCS. It is intentionally
common: hail is the first user, but wildfire and wind should reuse the same operating rules unless they have a
documented reason not to.

The goal is to make cloud runs auditable and repeatable:

```text
same code + same input control files + same run_id
  -> same GCS artifact tree
  -> machine-readable metadata
  -> human-readable QA summaries
```

## Current GCP Decision

Use this project for the first CONUS-grid cloud execution:

```text
project: modeling-nonprod-svc-db5x
region:  us-central1
```

Use this runtime service account for Cloud Run Jobs:

```text
project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com
```

Do **not** rely on the default compute service account. Direct probes showed that local deploys fail when the
default compute service account is implicitly used. Every local Cloud Run Job command must pass the runtime
service account explicitly.

The established dashboard deployment guide also defines:

```text
deploy service account: gh-actions-deploy@modeling-nonprod-svc-db5x.iam.gserviceaccount.com
artifact registry:        us-central1-docker.pkg.dev/modeling-nonprod-svc-db5x/infrasuremodelingdocker
```

That is the durable build/deploy pattern once Workload Identity Federation accepts this repository. The current
remote `D-ivyy/Hazard_Modeling` is rejected by the existing WIF attribute condition, so the first successful
remote proof used local `gcloud` and a temporary bootstrap job.

## Execution Types

Use these names consistently.

| Type | Meaning | Allowed use |
|---|---|---|
| `local_proof` | Run from notebook or local script, usually one day or one small batch. | Source interpretation, row contract, visual QA. |
| `cloud_proof` | Cloud Run proof using the same contract as local proof. | Remote permissions, runtime, and GCS write validation. |
| `dev_full` | Full accepted denominator in `dev/`, before release QA. | Builds M0/M1 candidates. |
| `release` | QA-accepted artifact copied/promoted under `releases/`. | Product-facing input to downstream work. |

Proof runs are valuable, but they are not the main product. The main product starts at the reconciled
`dev_full` layer and only becomes release-grade after QA.

## Run ID Convention

Use run IDs as execution addresses, not model versions.

```text
YYYYMMDDTHHMMSSZ[_short_purpose]
```

Examples:

```text
20260616T172929Z
20260616T205852Z_cloudrun_bootstrap_7d
20260617T010000Z_m0_full_conus
```

Rules:

- no spaces;
- no local timezone;
- use UTC timestamp;
- suffix is optional and should be short;
- one full M0 fanout should share one `run_id` across all batches;
- do not reuse a `run_id` if the GCS prefix already exists unless the run is explicitly marked as a forced
  replacement in metadata.

## GCS Address Convention

Durable bucket root:

```text
gs://infrasure-benchmark/hazard_conus_grid/
```

Active development writes go under:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/
```

Use this layer shape:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/
  common/
    benchmark_grid/
  <hazard>/
    <variant>/
      <layer>/
        run_id=<RUN_ID>/
          batch=<BATCH_LABEL>/        # when batch-scoped
            date=<YYYY-MM-DD>/        # when date-partitioned
              part-000.parquet
            metadata_<BATCH>_<RUN_ID>.json
            *_manifest_*.csv
            *_summary_*.csv
```

For current hail V1:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/
  m0_source_inventory/
  m0_daily_cell_evidence/
  m1_hazard_layer/
  solar/m2_m4_risk_metrics/
  qa/
```

Use `releases/` only after QA promotion:

```text
gs://infrasure-benchmark/hazard_conus_grid/releases/<release_id>/
```

## Artifact Format Rule

Use each file format for the job it is good at.

| Format | Use for | Do not use for |
|---|---|---|
| Parquet | Row-level data, partitioned panels, M0/M1/M2-M4 layers. | Human-only status notes. |
| JSON | Authoritative metadata, nested provenance, run config, caveats, allowed-use rules. | Large row-level tables. |
| JSONL | Optional cross-run event logs or run registries where one JSON object per line is useful. | Final row-level model layers. |
| CSV | Flat QA summaries, small manifests, notebook-readable status tables. | Nested metadata or authoritative provenance. |
| PNG | Human QA maps and screenshots. | Machine-readable data. |
| Notebook | Inspectable analysis and explanation. | The only copy of an artifact or metadata record. |

Metadata should be JSON-first. CSV summaries are allowed because they are easy to inspect in notebooks and
spreadsheets, but they are not the source of truth for nested run metadata.

## Required Metadata JSON

Every batch/run metadata JSON should include at least:

- `artifact_family`;
- `run_id`;
- `execution_type`;
- `hazard`;
- `variant`;
- `layer`;
- input source URIs and source inventory run id;
- benchmark grid/served mask URI;
- record window or batch window;
- row counts and expected row counts;
- status counts and no-data counts;
- code provenance: git SHA when available, runner URI/image/job name when cloud-run;
- GCP provenance: project, region, job name, execution id, runtime service account when cloud-run;
- output URIs;
- upload status;
- overwrite policy;
- `allowed_use`;
- `not_allowed_use`;
- caveats and QA flags.

For batch outputs, the metadata JSON is authoritative. Flat CSV summaries are derived convenience files.

## Cloud Run Job Convention

Use Cloud Run **Jobs**, not Cloud Run Services, for M0/M1 grid processing.

Services are for web/API endpoints. The grid jobs are bounded batch transformations:

```text
read control inputs
  -> process accepted source dates
  -> write immutable GCS output prefix
  -> exit
```

Minimum Cloud Run Job command conventions:

```text
--project modeling-nonprod-svc-db5x
--region us-central1
--service-account project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com
--tasks 1
--max-retries 0 or 1
--task-timeout 3600
```

Use `--max-retries 0` for first proofs so failures are obvious. Use `--max-retries 1` only after the job is
known to be idempotent and overwrite-safe.

For full fanout, prefer a prebuilt Artifact Registry image. The bootstrap pattern that installs dependencies
inside `python:3.12-slim` is acceptable for a proof, but not the preferred repeated full-run path.

## Control Inputs

Remote jobs should read control files from GCS, not from local untracked files.

Current required hail MRMS control inputs:

```text
source inventory:
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/mrms_v1_source_inventory_20140101_20260615_20260616T165806Z.parquet

served mask:
gs://infrasure-benchmark/hazard_conus_grid/dev/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv
```

The local `data/` tree is a development mirror. It should not be the only place a cloud job can find required
control inputs.

## Output Write Policy

Default policy: no overwrite.

Rules:

- write into a run-scoped prefix;
- fail if the target run/batch prefix already has objects;
- retry failed batches into the same run id only when the failed batch prefix is absent or explicitly cleared;
- never write directly to `releases/`;
- reconcile `dev/` batches into a clean M0 layer before building M1;
- record failed jobs in metadata or a run registry, not by silently missing dates.

## Current Hail Cloud Proof

The first successful Cloud Run proof was:

```text
job:       hazard-conus-grid-mrms-m0-bootstrap
execution: hazard-conus-grid-mrms-m0-bootstrap-7jqj5
run_id:    20260616T205852Z_cloudrun_bootstrap_7d
batch:     2024-06-01 to 2024-06-07
```

Output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T205852Z_cloudrun_bootstrap_7d/batch=20240601_20240607/
```

Result:

- rows: 91,595;
- severe cell-days: 1,450;
- sub-severe cell-days: 21,134;
- no-hail cell-days: 69,011;
- maps skipped;
- runner processing elapsed: 29.474 seconds;
- Cloud Run execution elapsed: about 2 minutes 8 seconds, including bootstrap dependency installation.

This proves Cloud Run execution and GCS write behavior. It does not mean the full historical run is already
running.

## Full-Run Gate

Do not start the full accepted MRMS denominator until these are pinned:

- full-run `run_id`;
- batch list source;
- fanout mode: sequential, batched parallel, or task-indexed job;
- image strategy: durable prebuilt image or explicitly accepted bootstrap fallback;
- retry/overwrite policy;
- reconciliation notebook/script;
- success criteria for accepting M0 before M1.

Recommended next steps for hail:

1. Run one 14-day Cloud Run batch with a fresh run id using the same output contract.
2. Build/confirm a reconciliation step that can accept multiple batch prefixes.
3. Fix the durable image path by moving the workflow under an allowed WIF repo/org or updating the WIF
   condition for this repo.
4. Start the full 148-batch denominator only after the reconciliation step is ready.
