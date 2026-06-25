# Task context — CONUS grid → reusable package + plausibility QC + reuse guide (2026-06-25)

## Objective
Take the hail × solar CONUS grid from notebooks to a **reusable, production package** (one engine, two
drivers), apply the **decided plausibility QC** (the original point of the hail work), produce + visualize
the **full-CONUS risk layer**, document it as a system the next hazard/asset can build on, and **push**.

## Background
- The grid was notebooks-first: M0→M1 (full CONUS) + a selected-cell M2–M4 smoke were built; the
  architecture (DD-G10–G14, [`plans/hazard_conus_grid/architecture/`](../../../plans/hazard_conus_grid/architecture/))
  planned the package; the **plausibility QC was *decided* ([`05`](../../discussion/conus_grid/hail/05_plausibility_qc_rule.md)) but not implemented**.
- The user's priority order, in their words: build the production structure → **do the QC (the actual
  reason hail mattered)** → make it viewable → document for reuse → push.
- Held throughout: bias to action in the build phase, but **agree the shape first** on structural changes;
  the user is highly redo-sensitive; verify exhaustively (gates, link-checks).

## Problems encountered & fixed
- **QC was sequenced last, behind the reproduction-gate refactor.** Owned: the bit-identical "reproduce the
  old numbers" gates *structurally* forced the one numbers-changing step (QC) to the end — but that put the
  infrastructure ahead of the actual goal. Fixed by doing the QC immediately once the refactor was proven.
- **Viz §4 accuracy bug** — a relative-diff over near-zero-EAL cells printed "27%" next to an "≈0" claim
  (tiny-denominator blow-up). Corrected to the honest **absolute** diff (0.55 %TIV-pts) + relative only on
  material cells (≤7.8%).
- **"White cells = no data" was wrong** — verified coverage is complete (`observed_day_fraction ≈ 1.00`
  everywhere). The 974 white cells are **genuinely-rare hail on a short record**, not missing data.
- **Docker build context** — the script now imports the packages, so the image needs them; fixed with a
  repo-root build context + a `.dockerignore` that excludes the gitignored cross-repo symlinks.
- **Duplicated GCS helpers** in the ingest/reconcile scripts → de-duplicated into `risk_engine.io_base`.

## What we built / changed
- **3 installable packages** (proven bit-identical to the worked notebooks):
  `shared/risk_engine` (M4 engine + M2 `exposure` + M3 `vulnerability` + `orchestration` + `config` + `io_base`),
  `pipelines/hail` (M0 `mrms_m0`, M1 `m1_hazard_layer`, `plausibility_qc`, `coupling`, `damage`),
  `drivers/conus_grid` (`canonical_assets`, `grid_driver`, `entrypoint`).
- **Plausibility QC** applied → QC'd M1 (`run_id=20260625_m1_mrms_only_qcd`) → QC'd full-CONUS grid layer
  (`run_id=20260625_conus_grid_hail_solar_v1_qcd`, 26,170 rows). Loss proven **QC-invariant**.
- **Viz**: `Notebooks/.../04_conus_grid_risk_maps` + a shareable Artifact page.
- **Docs**: [`docs/guides/`](../../../guides/) (the reuse how-to) +
  [`discussion/deep_per_asset/`](../../discussion/deep_per_asset/) (the second-driver migration) +
  architecture-status + folder READMEs.
- **Deploy enablement**: re-pointed ingest/reconcile scripts + the Cloud Run Dockerfile/workflow/`.dockerignore`.

## Files touched (commits `f33c040` · `a2816e5` · `7f7158c`; pushed @ `7f7158c`)
- `shared/**`, `pipelines/hail/**`, `drivers/conus_grid/**` (new packages + tests)
- `scripts/{run_mrms_v1_m0_daily_evidence_batch,reconcile_mrms_v1_m0_batches}.py`, `cloudrun/**`, `.github/workflows/**`, `.dockerignore`
- `Notebooks/hazard_conus_grid/hail/**` (QC-wired M1 + the maps notebook + READMEs)
- `docs/guides/**`, `docs/extra/discussion/deep_per_asset/**`, `docs/plans/hazard_conus_grid/architecture/README.md`, `AGENTS.md`, `.gitignore`
- **Excluded by choice:** `data/` (150 manifests left untracked for a later curation pass; big parquets/maps gitignored)

## Status
**COMPLETE + pushed** (`aamani-ai/Hazard_Modeling` @ `7f7158c`). The grid is a package, QC'd, viewable, and
documented as a reusable system. **5 reproduction gates green** (`pytest shared/tests pipelines/hail/tests
drivers/conus_grid/tests` → 5 passed). Provisional V1 — `MRMS_ONLY`, provisional severity, not a reportable
loss layer.

## Next steps
Two the user explicitly named: **(1) schema documentation** (the typed/versioned contracts + a per-layer
schema doc, now that one implementation exists) and **(2) GCP-bucket documentation** (what we push to
`gs://infrasure-benchmark/...`). Then the deep-per-asset second driver, wildfire (Phase D), and the deferred
accuracy work. Loose ends: verify CI, verify the next Cloud Run deploy builds with the packages, curate
`data/` manifests. Full ordered roadmap in [`handoff.md`](handoff.md).
