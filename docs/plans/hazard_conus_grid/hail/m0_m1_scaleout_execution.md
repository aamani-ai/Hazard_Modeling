# Hail V1 - M0/M1 Scale-Out Execution Strategy

Status: active execution plan for moving from proofs to full CONUS hail V1.

## Purpose

This document pins how we scale the MRMS-only hail grid work without rushing into an expensive or fragile
full run.

The end-to-end target is:

```text
M0 source inventory
  -> M0 full-grid daily cell evidence
  -> M1 per-cell frequency + observed size layer
  -> M2-M4 canonical solar risk metrics
  -> later wind risk metrics
```

The immediate lift is **M0 + M1 for served CONUS**. M2-M4 absolutely remains part of the grid product, but it
should wait until M1 is real. Risk metrics from an unstable or partial M1 layer can look precise while being
methodologically wrong.

## What Is Already Proven

| Gate | Status | Artifact / run |
|---|---|---|
| Served CONUS grid mask | done | `data/hazard_conus_grid/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv` |
| Selected-cell MRMS M1 interface | done | V0 pilot artifacts under `data/hazard_conus_grid/hail/` |
| Selected-cell solar M2-M4 interface | done | smoke-test artifacts under `data/hazard_conus_grid/hail/solar/` |
| One-day full-grid M0 row contract | done | `02_mrms_v1_full_grid_one_day_proof.ipynb` |
| GCS write/read/delete probe | done | `gs://infrasure-benchmark/hazard_conus_grid/_access_checks/` |
| Seven-day source-inventory proof + upload | done | `run_id=20260616T154907Z` |
| Full MRMS source inventory + batch contract | done | `run_id=20260616T165806Z` |
| Small full-grid M0 evidence batch | done locally and uploaded to GCS | `run_id=20260616T172929Z`, batch `20240601_20240607` |

The current GCS dev root is:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/
```

## Scale-Out Rule

Do not start the full M0 evidence run until the preceding gate is clean.

```text
inventory proof
  -> full inventory
  -> small M0 evidence batch
  -> runner decision
  -> scaled M0 evidence batches
  -> reconciliation
  -> M1
  -> M2-M4
```

This keeps the work measurable. Each stage should produce an artifact we can inspect, not just console logs.

## Stage 1 - Full MRMS Source Inventory

Run the inventory notebook over the intended V1 MRMS record window.

Current notebook:

```text
Notebooks/hazard_conus_grid/hail/m0_input_data/01_mrms_daily_mesh/
  03_mrms_v1_source_inventory.ipynb
```

Completed run:

| Item | Value |
|---|---:|
| `run_id` | `20260616T165806Z` |
| requested source window | `2014-01-01` to `2026-06-15` |
| requested source dates | 4,549 |
| accepted source dates | 2,071 |
| no-source dates | 2,478 |
| list-failed dates | 0 |
| first accepted source date | `2020-10-14` |
| last accepted source date | `2026-06-15` |
| missing accepted dates after first accepted | 0 |
| listed source files | 99,313 |
| planned 14-day M0 batches | 148 |

Artifacts:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=<RUN_ID>/
  mrms_v1_source_inventory_<WINDOW>_<RUN_ID>.parquet
  mrms_v1_source_files_manifest_<WINDOW>_<RUN_ID>.parquet
  mrms_v1_m0_daily_evidence_batch_spec_<WINDOW>_<RUN_ID>.csv
  mrms_v1_source_inventory_summary_<WINDOW>_<RUN_ID>.csv
  metadata_<WINDOW>_<RUN_ID>.json
```

Success criteria:

- one inventory row per requested date;
- source list failures explicitly recorded;
- accepted source dates clearly separated from missing/list-failed dates;
- selected daily tile convention documented;
- batch spec generated only from accepted dates;
- metadata contains local paths, GCS paths, counts, allowed use, and caveats.

The accepted denominator is continuous from `2020-10-14` through `2026-06-15`. The wider requested window was
intentional: dates from `2014-01-01` through `2020-10-13` are explicit `no_source_files` rows, not silent
zeros and not failed listings.

## Stage 2 - Small Full-Grid M0 Evidence Batch

After full inventory, run one small M0 daily-evidence batch from accepted dates. Use 7 or 14 source days.

Purpose:

- measure real runtime, memory, output size, and failure modes;
- validate row count: `13,085 cells x accepted dates`;
- verify coverage statuses and no-data/zero logic;
- confirm partitioning and metadata before any large fanout.

Expected output root:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=<RUN_ID>/
```

Expected artifact shape:

```text
date=<YYYY-MM-DD>/
  part-*.parquet
batch_manifest.parquet
batch_summary.csv
metadata.json
```

Success criteria:

- every accepted date has exactly one partition;
- each accepted date has exactly 13,085 cell rows unless a target-mask change is explicitly documented;
- source read failures are hard failures or explicit failed-date rows, not silent zeroes;
- selected source timestamp and source URI are carried through;
- GCS output is run-scoped and does not overwrite previous runs.

Completed local batch proof:

| Item | Value |
|---|---:|
| notebook | `04_mrms_v1_m0_daily_evidence_batch.ipynb` |
| `run_id` | `20260616T172929Z` |
| batch window | `2024-06-01` to `2024-06-07` |
| accepted source dates | 7 |
| served cells | 13,085 |
| expected rows | 91,595 |
| output rows | 91,595 |
| duplicate `cell_id/date` rows | 0 |
| total severe cell-days | 1,450 |
| total sub-severe cell-days | 21,134 |
| total no-hail cell-days | 69,011 |
| daily QA maps | 7 |
| local elapsed time | 7.535 seconds |
| combined parquet size | 0.512 MB |
| GCS upload | uploaded 19 objects |

Local artifacts:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T172929Z/batch=20240601_20240607/
```

GCS artifacts:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T172929Z/batch=20240601_20240607/
```

Important interpretation: both the local compute path and the remote write path are now clean for a small
batch.

## Stage 3 - Runner Decision

Cloud Run is a good option only if the small M0 evidence batch proves the job is stateless, bounded, and fits
Cloud Run limits.

| Runner | Use when | Avoid when |
|---|---|---|
| Local / workstation | inventory and very small proof batches | long unattended runs or high parallelism |
| Cloud Run Jobs | one batch can finish within service limits; container is stateless; simple fanout by date window | memory/runtime exceeds limits, or many retries/checkpointing are needed |
| Cloud Batch | many independent date-window jobs, longer runtime, more control over resources | setup overhead is not worth it for small runs |
| VM runner | quickest path for a controlled one-off long run with manual monitoring | repeated production-style runs need orchestration |

Decision rule:

```text
If 7-14 day M0 batch is clean and comfortably within Cloud Run limits:
  use Cloud Run Jobs for date-window fanout.
Else:
  use Cloud Batch or a VM runner, keeping the same batch contract.
```

The runner must not change the artifact contract. It only changes where the same batch code executes.

Current decision: use **task-indexed Cloud Run fanout** for the first full accepted MRMS denominator.

```text
Cloud Run task index
  -> batch-spec row
  -> date_start/date_end
  -> one normal M0 batch output prefix
```

Reason: the durable-image Cloud Run path is proven, normal 14-day batches fit comfortably, and task indexing
avoids manually updating/executing the same job 148 times. Keep `parallelism` bounded for the first full run
so source reads, GCS writes, and failures remain observable.

### Current GCP Execution Decision

Use `modeling-nonprod-svc-db5x` as the first Cloud Run target, not `vertexai-models`.

Reason:

- `modeling-nonprod-svc-db5x` already has Cloud Run, Cloud Build, and Artifact Registry APIs enabled;
- it can read/write the benchmark bucket prefix used by this work:
  `gs://infrasure-benchmark/hazard_conus_grid/dev/`;
- `vertexai-models` is the active local `gcloud` config project, but Cloud Run APIs are not enabled there
  and the current account cannot enable them.

Creating a new GCP project is not the current path because the active account does not expose billing account
or project-creation/admin visibility. If a new dedicated project is created later, it must still inherit the
same bucket access and run the same batch contract.

Default-service-account blocker:

```text
Permission 'iam.serviceaccounts.actAs' denied on service account
952205173464-compute@developer.gserviceaccount.com
```

Confirmed by a direct Cloud Run Job create probe on `2026-06-16`:

```text
gcloud run jobs create hazard-conus-grid-permission-probe \
  --project modeling-nonprod-svc-db5x \
  --region us-central1 \
  --image us-docker.pkg.dev/cloudrun/container/hello
```

The account can list Cloud Run services/jobs, but cannot deploy a job because the deploy action tries to use
the default compute service account and requires `iam.serviceaccounts.actAs`.

Resolution:

Use the established runtime service account explicitly:

```text
project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com
```

Confirmed by a direct Cloud Run Job create/delete probe on `2026-06-16`:

```text
gcloud run jobs create hazard-conus-grid-sa-probe \
  --project modeling-nonprod-svc-db5x \
  --region us-central1 \
  --image us-docker.pkg.dev/cloudrun/container/hello \
  --service-account project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com
```

The job was created successfully and then deleted. This means the account can deploy a Cloud Run Job when the
runtime service account is supplied explicitly.

Execution setup resolved:

- every Cloud Run Job command for this project must include
  `--service-account project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com`;
- local `divy@aamani.ai` still cannot inspect Artifact Registry or Cloud Build directly:
  `artifactregistry.repositories.get` and Cloud Build list permissions are denied;
- the attached dashboard deployment guide shows the established build/deploy path uses
  `gh-actions-deploy@modeling-nonprod-svc-db5x.iam.gserviceaccount.com` through GitHub Actions WIF, pushing to
  `us-central1-docker.pkg.dev/modeling-nonprod-svc-db5x/infrasuremodelingdocker`;
- the repo now lives under `aamani-ai/Hazard_Modeling`, which satisfies the WIF condition used by the
  deployment guide;
- the durable image build/push/deploy path has succeeded and should be used for repeated Cloud Run execution.

Pinned image build/deploy path:

```text
.github/workflows/deploy-hazard-conus-grid-mrms-m0-job.yml
```

This workflow is manual-only (`workflow_dispatch`). It follows the existing dashboard deployment pattern:

- authenticate through the org-wide GitHub Actions WIF provider;
- impersonate `gh-actions-deploy@modeling-nonprod-svc-db5x.iam.gserviceaccount.com`;
- push the image to
  `us-central1-docker.pkg.dev/modeling-nonprod-svc-db5x/infrasuremodelingdocker`;
- deploy a Cloud Run **Job** named `hazard-conus-grid-mrms-m0`;
- run the job as
  `project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com`;
- read control inputs from GCS, not from local untracked files:
  - `gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_source_inventory/run_id=20260616T165806Z/mrms_v1_source_inventory_20140101_20260615_20260616T165806Z.parquet`
  - `gs://infrasure-benchmark/hazard_conus_grid/dev/common/benchmark_grid/served_conus_cell_ids_v2026_06.csv`

The first successful GitHub Actions deploy used `execute_after_deploy=false`, then the deployed job was
executed manually for the already-proven batch window `2024-06-01` to `2024-06-07`.

First GitHub Actions result:

- run: `27647573897`;
- status: failed during `google-github-actions/auth@v3`;
- reason: `unauthorized_client`, credential rejected by the Workload Identity Federation attribute condition;
- interpretation: the deployment guide assumes an `aamani-ai` GitHub organization repository, while the
  current remote is `D-ivyy/Hazard_Modeling`;
- this is not a Cloud Run runtime service-account problem. The explicit runtime service account works from
  local `gcloud`.

Durable GitHub Actions result after repo move:

| Item | Value |
|---|---:|
| repository | `aamani-ai/Hazard_Modeling` |
| workflow run | `27649989510` |
| workflow status | succeeded |
| image | `us-central1-docker.pkg.dev/modeling-nonprod-svc-db5x/infrasuremodelingdocker/hazard-conus-grid-mrms-m0:be4be51072b07a8135a47b52d31a8d59614751f6` |
| Cloud Run Job | `hazard-conus-grid-mrms-m0` |
| execution | `hazard-conus-grid-mrms-m0-lcqqg` |
| execution status | succeeded |
| run id | `20260616T214036Z_wif_deploy_probe` |
| batch | `2024-06-01` to `2024-06-07` |
| rows | 91,595 |
| severe cell-days | 1,450 |
| sub-severe cell-days | 21,134 |
| no-hail cell-days | 69,011 |
| runner processing elapsed | 18.372 seconds |

GCS output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T214036Z_wif_deploy_probe/batch=20240601_20240607/
```

This proves the durable image path. Future repeated Cloud Run batches should use `hazard-conus-grid-mrms-m0`,
not the bootstrap job, unless there is a specific debugging reason.

Temporary remote-proof fallback:

- deploy the Cloud Run Job directly from local `gcloud`;
- use the public `python:3.12-slim` image only as a bootstrap image;
- download the pinned runner script from GCS at runtime;
- run as `project-service-account@modeling-nonprod-svc-db5x.iam.gserviceaccount.com`;
- keep this as historical proof infrastructure only. The durable path is now the organization-repo workflow
  and prebuilt Artifact Registry image.

Temporary fallback execution result:

| Item | Value |
|---|---:|
| Cloud Run Job | `hazard-conus-grid-mrms-m0-bootstrap` |
| execution | `hazard-conus-grid-mrms-m0-bootstrap-7jqj5` |
| execution status | succeeded |
| execution start | `2026-06-16T20:59:17Z` |
| execution complete | `2026-06-16T21:01:25Z` |
| run id | `20260616T205852Z_cloudrun_bootstrap_7d` |
| batch | `2024-06-01` to `2024-06-07` |
| rows | 91,595 |
| severe cell-days | 1,450 |
| sub-severe cell-days | 21,134 |
| no-hail cell-days | 69,011 |
| maps | skipped |
| runner processing elapsed | 29.474 seconds |

GCS output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T205852Z_cloudrun_bootstrap_7d/batch=20240601_20240607/
```

This matches the local 7-day proof row count and status counts. Do not blindly re-execute this temporary job:
the command contains a fixed run id and the runner intentionally refuses to overwrite existing GCS prefixes.
Historical note: this bootstrap job proved remote execution before the durable image path was available. Do
not use it for repeated fanout now that the durable image workflow works.

Fourteen-day Cloud Run proof:

| Item | Value |
|---|---:|
| Cloud Run Job | `hazard-conus-grid-mrms-m0-bootstrap` |
| execution | `hazard-conus-grid-mrms-m0-bootstrap-qzx4r` |
| execution status | succeeded |
| execution start | `2026-06-16T21:13:09Z` |
| execution complete | `2026-06-16T21:15:27Z` |
| run id | `20260616T211247Z_m0_batch0001_14d_cloud_proof` |
| batch | `2020-10-14` to `2020-10-27` |
| rows | 183,190 |
| severe cell-days | 251 |
| sub-severe cell-days | 10,610 |
| no-hail cell-days | 172,329 |
| maps | skipped |
| runner processing elapsed | 31.796 seconds |

GCS output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T211247Z_m0_batch0001_14d_cloud_proof/batch=20201014_20201027/
```

QA note: this batch has an extreme raw MRMS MESH value (`max_mesh_mm=1057.7` on `2020-10-27`). The value is
not corrected in M0; it is carried forward as a QA flag so M1 can decide whether to cap/filter/de-bias later.

## Stage 4 - Scaled M0 Daily Evidence

Once the runner is selected, process the full accepted source-date denominator in independent batches.

Requirements:

- each batch reads from the accepted inventory/batch spec;
- each batch writes a run-scoped manifest and metadata;
- failed batches can be retried without corrupting clean outputs;
- reconciliation decides which batches are accepted into the final M0 panel.

Do not build M1 directly from unreconciled batch outputs.

## Stage 5 - Reconcile M0 Batches

The reconciled M0 layer is the first real full-grid evidence layer.

It must prove:

- continuous intended date coverage or explicitly listed missing dates;
- one row per `cell_id x accepted_date`;
- no duplicate `cell_id x date` rows;
- source failures and no-hail days remain distinct;
- all accepted batches use the same grid mask, threshold, product, and aggregation rules.

First reconciliation proof:

| Item | Value |
|---|---:|
| script | `scripts/reconcile_mrms_v1_m0_batches.py` |
| run id | `20260616T211844Z_m0_reconcile_2batch_proof` |
| input batches | 2 |
| dates | 21 |
| rows | 274,785 |
| duplicate `cell_id/date` rows | 0 |
| severe cell-days | 1,701 |
| sub-severe cell-days | 31,744 |
| no-hail cell-days | 241,340 |
| QA flags | `extreme_mesh_ge_300mm` |

GCS output:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/
  run_id=20260616T211844Z_m0_reconcile_2batch_proof/
```

This proves multi-batch validation and upload. It is a partial, non-contiguous proof only; it is not the full
M0 layer for M1.

## Stage 6 - Build M1

M1 consumes only reconciled M0 evidence.

M1 outputs:

- observed years / observed days per cell;
- severe-hail-day count;
- `lambda_cell`;
- V1 frequency distribution label, default `poisson_v1`;
- empirical conditional MESH size summaries;
- sparse/no-data/tail/provenance flags.

M1 is still MRMS-only and observed-body. Deep-tail metrics must carry provisional-tail warnings until a fitted
severity / EVT decision is implemented.

## Stage 7 - M2-M4 Later

M2-M4 is part of the product, but not the next engineering step.

After M1 is validated:

```text
M1 MRMS-only hail layer
  -> canonical solar coupling
  -> damage/loss simulation
  -> EAL, AEP/OEP, PML, VaR, TVaR, %TIV
  -> QA and release candidate
```

The selected-cell solar smoke test already proved the interface. The full-grid M2-M4 run should be driven by
the real M1 layer, not by source-inventory or pilot artifacts.

Wind comes later because wind exposure/coupling is more nuanced and should reuse the M1 layer only after the
solar path is stable.

## Current Execution State

The scaled runner has now been proven and used for the first full MRMS-only hail M0 denominator. Earlier proof
outputs remain useful for debugging, but the main M0 layer is the reconciled full-run output below.

The completed local small batch to preserve is:

```text
data/hazard_conus_grid/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T172929Z/batch=20240601_20240607/
```

The completed Cloud Run proof to preserve is:

```text
gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/
  run_id=20260616T205852Z_cloudrun_bootstrap_7d/batch=20240601_20240607/
```

The task-indexed proof also succeeded:

```text
GitHub Actions run: 27650904912
Cloud Run execution: hazard-conus-grid-mrms-m0-bn9lk
run_id: 20260616T215911Z_task_index_2batch_proof
task_count / parallelism: 2 / 2
rows: 366,380 across two non-overlapping 14-day batches
```

The full task-indexed Cloud Run run then succeeded:

```text
GitHub Actions run: 27651275076
Cloud Run execution: hazard-conus-grid-mrms-m0-54dm7
run_id: 20260616T220624Z_m0_full_conus_task_indexed
task_count / parallelism: 148 / 8
task result: 148 succeeded, 0 failed
elapsed: about 40 minutes 31 seconds
gcs: gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/run_id=20260616T220624Z_m0_full_conus_task_indexed/
```

The full run was reconciled with streaming output:

```text
script: scripts/reconcile_mrms_v1_m0_batches.py --streaming
run_id: 20260616T225000Z_m0_full_conus_reconciled
gcs: gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_reconciled_daily_cell_evidence/run_id=20260616T225000Z_m0_full_conus_reconciled/
status: streaming_reconciliation_passed_row_contract
dates: 2,071
served cells/date: 13,085
rows: 27,099,035
duplicate cell-date rows: 0
row-count failures: 0
qa flags: extreme_mesh_ge_300mm
```

The active recommendation after the full run:

- project: `modeling-nonprod-svc-db5x`;
- output bucket prefix:
  `gs://infrasure-benchmark/hazard_conus_grid/dev/hail/v1_mrms_only/m0_daily_cell_evidence/`;
- fanout mode: task-indexed Cloud Run Job from the inventory batch-spec CSV;
- future full reruns: keep bounded `parallelism`; do not run all tasks at once unless measured evidence supports it;
- batch size: keep the inventory-generated 14-day batches unless a retry or future source change forces smaller
  windows;
- overwrite policy: never overwrite an existing run/batch prefix; failed batches get a new `run_id` or a
  deliberate retry prefix;
- maps: write QA PNG maps for proof batches only; use `--skip-maps` for full fanout and create review maps from
  reconciled summaries later.
- metadata format: JSON is authoritative; CSV is allowed only for flat summaries/manifests.

Next operational step: build M1 from the reconciled M0 root, after reviewing the `extreme_mesh_ge_300mm` QA
flag and producing a small set of review maps/tables from the reconciled sidecars.
