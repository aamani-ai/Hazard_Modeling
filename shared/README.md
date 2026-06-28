# shared/ — `risk_engine` (the shared M2–M4 risk engine)

The generic risk engine, a **peer of the per-peril pipelines** (it imports no peril). It consumes a
hazard-distribution object + an exposure input and emits the per-cell risk-metrics object. The CONUS
grid and the (future) deep per-asset run are two **drivers** of this one engine — off-grid == on-grid
([`DD-G11`](../docs/plans/hazard_conus_grid/decisions.md)).

```
risk_engine/
  engine/        run_cell_mc · exceedance_metrics · weighted_quantile · validate_cell_mc  (M4)
  io_base/       GCS plumbing (is_gcs_uri · split_gcs_uri · up/download · gcs_prefix_exists)
```

## Status — Phase A (engine extraction)

This is the first slice of the [grid production architecture](../docs/plans/hazard_conus_grid/architecture/migration_plan.md).
The M4 functions are lifted **verbatim (behaviour-preserving)** from the hail × solar selected-cell
smoke notebook, with the asset/peril leaks parameterized away (array inputs instead of hard-coded
`p_hit_solar`/`conditional_loss_usd` columns; the RP/VaR/TVaR/PML ladders and `capacity_kwp` as
arguments). The RNG draw order is preserved, so results are bit-identical to the original.

**Gate:** `shared/tests/test_engine_reproduces_smoke.py` re-runs the extracted engine on the prior
smoke run's persisted `event_set` and asserts it reproduces the persisted `metrics` exactly.

## Use

```bash
pip install -e ./shared          # editable install into the repo .venv
python shared/tests/test_engine_reproduces_smoke.py   # run the Phase-A gate
```

```python
from risk_engine.engine import run_cell_mc, exceedance_metrics
aep, oep, aep_uncapped, counts = run_cell_mc(p_hit, conditional_loss_usd, lambda_cell, n_years, tiv_usd, rng)
metrics = exceedance_metrics(aep, oep, tiv_usd, capacity_kwp)
```

## Not in here (by design)

Coupling physics, damage curves, source ingest, and canonical-asset definitions are **peril-/asset-
specific** and live in `pipelines/<peril>/` and `drivers/` — not in the engine. See
[`architecture/contracts.md`](../docs/plans/hazard_conus_grid/architecture/contracts.md).
