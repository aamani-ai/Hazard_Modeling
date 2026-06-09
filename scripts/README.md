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

*Add a row when you add a script. If something here grows into real, reusable production logic, that's a
signal the architecture phase has arrived — promote it deliberately, don't let it accrete here.*
