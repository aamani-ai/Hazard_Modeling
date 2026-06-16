# scripts/ — testing & one-time utility scripts (NOT production code)

> **What this folder is:** ad-hoc, one-time, and utility scripts that *support the notebooks* — heavy data
> pulls, scans, smoke tests, scaffolding. **What it is NOT:** the production codebase or the start of the
> "real" architecture.

This is a deliberate, stated distinction (see [`docs/plans/00_build_strategy.md`](../docs/plans/00_build_strategy.md)).
We are **notebooks-first across three hazards**, and the production folder structure + database layer come
**later**, designed from that experience. Until then:

- The **notebooks** (`Notebooks/hail/…`) are the inspectable spec — the science lives there.
- **`scripts/`** holds the things too heavy or too one-off for a notebook cell — run once, produce an
  artifact the notebooks consume, then mostly sit idle.
- Nothing here is a service, a module API, or load-bearing production code. Don't build the architecture here.

## Contents

| Script | What | Notes |
|---|---|---|
| [`scan_mrms_record.py`](scan_mrms_record.py) | Full-record MRMS scan (2020-10→present) over the Hayhurst region → wide M0 parquet | concurrent, resumable, cache-first; Stage-1 frequency widening (DD-3). Run once; re-runs resume from cache. |
| [`run_myrorss_selected_cell_batches.py`](run_myrorss_selected_cell_batches.py) | Runs planned MYRORSS selected-cell chronological batches by executing `Notebooks/hail/m0_input_data/03_myrorss_reanalysis_source_qualification/03_selected_cell_full_record_batches.ipynb` | local/backend runner for common source qualification + grid selected-cell adapter proof; use only after the promotion-gate questions are documented. |
| [`run_mrms_v1_m0_daily_evidence_batch.py`](run_mrms_v1_m0_daily_evidence_batch.py) | Runs one MRMS-only hail CONUS-grid M0 daily-evidence batch from the accepted source inventory | backend runner for the notebook-defined V1 batch contract; supports local/VM/Cloud Run style execution, optional GCS upload, and task-indexed Cloud Run fanout from the inventory batch-spec CSV. Use `--skip-maps` for large fanout runs. |
| [`reconcile_mrms_v1_m0_batches.py`](reconcile_mrms_v1_m0_batches.py) | Reconciles explicit MRMS-only M0 batch prefixes into a validated partial/full M0 panel | validates row counts, duplicate `cell_id/date`, status counts, metadata JSON, and optional GCS upload before M1 consumes batch outputs. Use `--streaming` for full-denominator runs so it writes `date=YYYY-MM-DD/part-000.parquet` partitions without building one giant in-memory panel. |

*Add a row when you add a script. If something here grows into real, reusable production logic, that's a
signal the architecture phase has arrived — promote it deliberately, don't let it accrete here.*
