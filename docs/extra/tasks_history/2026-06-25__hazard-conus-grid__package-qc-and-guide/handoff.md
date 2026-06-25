# Handoff — CONUS grid is a reusable package, QC'd, documented, pushed (2026-06-25)

**Read me first.** The hail × solar CONUS grid moved off notebooks into a **reusable package** (one engine,
two drivers), got its **plausibility QC**, produced the **full-CONUS risk layer**, and is **documented as a
system the next hazard/asset builds on** — pushed to `aamani-ai/Hazard_Modeling` @ `7f7158c` (commits
`f33c040` package · `a2816e5` notebooks · `7f7158c` docs). This is the "set in stone" for the next grid or
the deep-per-asset driver.

## 60-second summary
- **Packaged** the grid: `shared/risk_engine` (engine + M2 coupling + M3 curve framework + orchestration +
  config + io_base, **leak-clean**) · `pipelines/hail` (M0 adapter, M1 build, **plausibility_qc**, coupling,
  damage) · `drivers/conus_grid` (canonical asset + driver + entrypoint). Each extraction **bit-identical** to
  the worked notebooks (engine 2.1e-16 · M0/M1 0.0 · driver 2.06e-16).
- **Plausibility QC built + applied** ([`05`](../../discussion/conus_grid/hail/05_plausibility_qc_rule.md)):
  cap impossible MESH at the **203.2 mm** US record, flag **585** ≥300 mm hard artifacts + **61** frequency
  spikes (held out), **frequency untouched**, raw kept. → QC'd M1 → QC'd 13,085-cell grid layer.
- **Solar loss is QC-invariant** (0.0 diff vs baseline) — the M3 curve saturates ~100 mm, so the magnitude
  tail can't drive solar loss (the decided result, not a gap). The QC's hard-artifacts cluster over the **Ohio
  Valley** — exactly where the MESH literature says it over-reads (a real validation).
- **Viz**: `04_conus_grid_risk_maps` + a shareable map page (Artifact). **Docs**:
  [`docs/guides/building_a_hazard_asset_grid.md`](../../../guides/building_a_hazard_asset_grid.md) (the reuse
  how-to: system + the **cross-driver QC** + the **five-blank recipe** + the **research-pass Step 0** + the
  sparse-cell constraint) and
  [`discussion/deep_per_asset/`](../../discussion/deep_per_asset/01_notebooks_to_second_driver.md).

## Headline numbers (QC'd grid, % of TIV)
| | value | note |
|---|---|---|
| cells | 13,085 | canonical 100 MW solar at each |
| EAL | mean 1.77% · median 0.45% · max 33.7% | corridor ≫ West |
| national EAL | ~$34.4B | sum over the canonical grid |
| QC | 749 capped · 585 hard-artifact · 61 spikes held out | frequency untouched |
| zero-hail (white) cells | 974 (7.4%) | full coverage, genuinely rare — **not** no-data |

## Repro
```bash
cd Hazard_modeling && source .venv/bin/activate
pytest shared/tests pipelines/hail/tests drivers/conus_grid/tests   # 5 passed (the gates)
python -m conus_grid.entrypoint                                       # rebuild the full-CONUS QC'd layer
```
Run-id oracles + the per-gate results are in [`notes.md`](notes.md).

## NEXT ACTION roadmap (pick up here)
1. **Schema documentation** *(user-requested; one implementation now exists to anchor it).* Three pieces:
   (a) implement the **typed, versioned contracts** (Phase C) — `shared/risk_engine/schemas/`:
   `hazard_distribution` (M1 boundary) + `risk_metrics` (Contract-2), with `schema_version` + typed enums
   ([`contracts.md`](../../../plans/hazard_conus_grid/architecture/contracts.md));
   (b) a **per-layer schema doc** — the M0 cell-day evidence (25 cols), the M1 hazard layer (67 cols incl. the
   QC columns), the grid Contract-2 risk layer — field · unit · dtype · nullability;
   (c) **reconcile** [`output_schema.md`](../../../plans/hazard_conus_grid/output_schema.md) to the pinned
   canonical RP/VaR ladder (it now includes RP=200).
2. **GCP-bucket documentation** *(user-requested).* Document `gs://infrasure-benchmark/hazard_conus_grid/...`:
   the layer tree (`m0_source_inventory` → `m0_daily_cell_evidence` → `m0_reconciled_daily_cell_evidence` →
   `m1_hazard_layer` → `m2_m4_conus_grid`), the `dev/` vs releases convention (DD-G6), the `run_id=` structure,
   and **which runs are authoritative vs throwaway** (then prune throwaway per the GCP-cleanup habit). Extend
   [`common/storage_artifacts.md`](../../../plans/hazard_conus_grid/common/storage_artifacts.md) +
   [`common/gcp_execution_and_storage_conventions.md`](../../../plans/hazard_conus_grid/common/gcp_execution_and_storage_conventions.md).
3. **Deep-per-asset = the second driver** — the migration is mapped in
   [`discussion/deep_per_asset/01`](../../discussion/deep_per_asset/01_notebooks_to_second_driver.md). The one
   real engine change it needs: `run_cell_mc`'s count draw must dispatch on **`(family, params)`** (NegBin for
   the deep run; Poisson today). Gate = reproduce the Hayhurst deep-run numbers (EAL 5.7% / PML₁₀₀ 54% /
   λ_asset 0.26). **And it must adopt the plausibility QC** (the cross-driver gap, guide §7).
4. **Wildfire (Phase D)** — the real test of the five-blank recipe (guide §4). If adding it is more than
   "fill the five blanks," fix the engine, don't fork it.
5. **Deferred accuracy** — frequency pooling / spatial shrinkage (fixes sparse-cell hard-zeros), record
   extension (MYRORSS), MESH de-biasing (Murillo & Homeyer; fixes West under-detection), EVT severity tail.
6. **Loose ends** — verify CI is green after this push (`ci.yml` may have triggered); run the Cloud Run
   `workflow_dispatch` once to confirm the **image builds with the vendored packages** (by-construction
   correct, not yet exercised); curate the **150 untracked `data/` manifests** into a deliberate commit;
   **wire the 5 reproduction gates into `ci.yml`** so they run on every push (today they're manual `pytest`);
   and **scale the grid driver to Cloud Run** (DD-G9 task-indexed fanout) — it runs locally ~30 min today and
   only the M0 ingest is on Cloud Run, so a full-CONUS rebuild isn't yet a one-click job.

## Files the next session should read first
- [`docs/guides/building_a_hazard_asset_grid.md`](../../../guides/building_a_hazard_asset_grid.md) — the how-to (read this first).
- [`discussion/deep_per_asset/01_notebooks_to_second_driver.md`](../../discussion/deep_per_asset/01_notebooks_to_second_driver.md) — the second driver.
- [`architecture/`](../../../plans/hazard_conus_grid/architecture/) (README · contracts · migration_plan) + [`05_plausibility_qc_rule.md`](../../discussion/conus_grid/hail/05_plausibility_qc_rule.md).
- The code: [`shared/`](../../../../shared/README.md) · [`pipelines/hail/`](../../../../pipelines/hail/README.md) · `drivers/conus_grid/`.
- This task: [`task_context.md`](task_context.md) · [`decisions.md`](decisions.md) · [`notes.md`](notes.md).
