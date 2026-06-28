# pipelines/hail/ — the hail peril pipeline (`hail`)

The **peril-specific** side of the layered pipeline: hail's M0/M1. It owns the MRMS **source
adapter** (raw MESH tile → per-cell-day evidence) and the **M1 fit** that emits the M1 hazard-layer
boundary object the shared [`risk_engine`](../../shared/README.md) consumes. It imports `risk_engine`
(for `io_base`); the engine never imports a peril.

```
hail/
  config.py           THRESHOLD_MM · PRODUCT · the 0.25° grid params · coverage_status enum · the M0 column contract
  mrms_m0.py          the source adapter: build_daily_panel + read_mrms_grib · native_points_to_cell_id · aggregate · …
  m1_hazard_layer.py  build_m1_hazard_layer: reconciled M0 cell-days → one M1 hazard row per cell
                      (severe-day frequency + raw MESH severity summaries + tail QA flags) · the 52-col M1 contract
```

## Status — M0 + M1 extracted (behaviour-preserving), both proven bit-identical

Both layers are lifted **verbatim** from the worked pipeline and consumed back by it (no drift):

- **M0 source adapter** (`mrms_m0.py`) — from `scripts/run_mrms_v1_m0_daily_evidence_batch.py`. The only
  change: the raw-tile cache dir is an explicit `cache_dir` argument (so the package carries no repo
  path). The script **and the Cloud Run image** now import this adapter + `risk_engine.io_base`;
  orchestration (batch loop, GCS I/O, metadata) stays in the script.
- **M1 hazard-layer build** (`m1_hazard_layer.py`) — from the full-CONUS build notebook (sections 2–3).
  The notebook now calls `build_m1_hazard_layer`; its QA maps, artifact writing, and GCS upload stay in
  the notebook. `max_mesh_mm_log1p_display` is a notebook display column, **not** part of the contract.

**Gates (offline — no Cloud Run, no expensive re-run):**

- `tests/test_adapter_reproduces_m0.py` — `build_daily_panel` on a sample of dates vs the reconciled M0
  partitions → exact.
- `tests/test_m1_reproduces.py` — `build_m1_hazard_layer` streamed over all 2,071 reconciled-M0
  partitions (~27M cell-days) vs the persisted 13,085-cell M1 → **max float diff 0.0** across all 52
  contract columns (+ the persisted 53rd column proven to be the `log1p` display transform).

The **plausibility QC** (the ~200 mm physical cap + frequency flag from
[`05_plausibility_qc_rule.md`](../../docs/extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md))
is a **separate, deliberate** numbers-changing step *after* this refactor — not folded in here.

## Use

```bash
pip install -e ./pipelines/hail      # editable install (depends on risk_engine for io_base)
python pipelines/hail/tests/test_adapter_reproduces_m0.py   # M0 adapter (sampled dates)
python pipelines/hail/tests/test_m1_reproduces.py           # M1 build (full-CONUS scan, ~13s)
```

## Not in here (by design)

The M2–M4 risk math (`risk_engine`), the canonical-asset / coupling / damage curves (the grid driver
+ the damage-curve contract), and the generic orchestration. See
[`architecture/README.md`](../../docs/plans/hazard_conus_grid/architecture/README.md).
