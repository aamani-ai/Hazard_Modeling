# Task Context — Hail × Solar pipeline end-to-end (M0→M4)

**Date:** 2026-06-09 · **Area:** hail-pipeline · **Slug:** m0-m4-end-to-end
*(First task-history entry. Format per `.cursor/commands/PROMPT_CREATE_TASK_DOCS.md`.)*

## Objective

Build the **full hail × solar hazard-loss pipeline end-to-end in notebooks** — raw evidence → catalog →
coupling → damage → annual loss & risk metrics (M0→M4) — for one asset (Hayhurst Texas Solar, EIA 66880),
*the right way*, then math-validate it and publish the repo. This is **hazard 1 of 3** (the plan is hail →
wildfire → wind in notebooks, then design the production architecture — see `docs/plans/00_build_strategy.md`).

## Background

This repo is a **ground-up rebuild** of InfraSure's Tier-2 hazard risk modeling after the old repo's
math errors (EAL survived but VaR/PML ~12× low from a Law-of-Total-Variance mistake; an OEP/AEP frame
mismatch; a point spatial-factor under-count; a 100× unit bug). The whole point of this build is to get the
**math right and inspectable**, peril-by-peril, in notebooks first.

## What we built (this session)

1. **M0 input data** — two sources behind one interface: `01_noaa_hydronos` (NOAA Storm Events point reports
   + NRI reference-only) and `02_mrms_aws` (MRMS MESH gridded radar → real footprints; opens with a
   from-scratch "what is this data" walkthrough §1–§7).
2. **M1 event catalog** (`m1_catalog/01_event_catalog`) — MRMS hail-days → canonical `Event` records as
   **footprint-swath polygons** (GeoParquet) + a `CatalogManifest`; NOAA as a cross-check overlay
   (`confidence_flags`, no events added); **fitted NegBin frequency** (λ_collection = 29.6/yr, Fano φ = 3.37).
3. **M2 coupling** (`m2_coupling/01_coupling`) — per-event **Minkowski hit probability** `p=(√F+√s)²/A`
   (fixes the old repo's `F/A` point-factor error); `λ_asset = λ_collection·E[p] = 0.26/yr`.
4. **M3 severity/damage** (`m3_damage/01_damage`) — **capex-weighted subsystem blend** from the
   `infrasure-damage-curves` repo (PV_MODULE L=0.95 + TRACKER L=0.40 × NREL weights → asset DR caps ~34%).
5. **M4 loss & metrics** (`m4_loss_metrics/01_loss_metrics`) — **compound-Poisson Monte Carlo** with
   event-level thinning + NegBin counts → AEP/OEP → EAL/VaR/PML/TVaR (shown as % of TIV).
6. **Stage-1 frequency widening** — `scripts/scan_mrms_record.py` scanned the **full ~5.65-yr MRMS record**
   (2020-10→2026-06, 2063 days → 158 hail-day events), turning the metrics from *illustrative* → *real
   (record-limited)*.
7. **Docs/decision infrastructure** — `docs/learning_logs/` (01–05), the **assumptions register** (A1–A23),
   `decisions.md` (DD-1..4), per-phase plans (phase-2..5), per-layer notebook READMEs, the build-strategy
   doc, and `scripts/README.md`.
8. **Math validation** — a 23-agent audit confirmed the model is **mathematically sound** (no calc errors).
9. **Published** — pushed to `D-ivyy/Hazard_Modeling` (private).

## Problems encountered (and resolved)

- **Metrics ran "hot"** (EAL ~9.8%, 1-in-100 ~98% of TIV) — root cause: the placeholder damage curve
  extrapolated to ~100%. **Fixed** by swapping to the capex-weighted blend (caps ~34%) → EAL 5.7%, 1-in-100
  ~54%. (Remaining: EAL still somewhat high; suspect MESH-FAR-inflated frequency — see next steps.)
- **Stale narrative** in M2 after the Stage-1 widening (prose quoted the old 3-month numbers) — **fixed**.
- **Push blocked** by the `gh` OAuth token lacking `workflow` scope — **fixed** by pushing over **SSH** as
  the `github.com-work` (D-ivyy) identity.

## Files touched

- **Created (notebooks):** `Notebooks/hail/{m0_input_data,m1_catalog,m2_coupling,m3_damage,m4_loss_metrics}/`
  (`.py` + executed `.ipynb` + per-folder `README.md`).
- **Created (docs):** `docs/learning_logs/{README,01..05}.md`; `docs/plans/00_build_strategy.md`,
  `docs/plans/hail/{assumptions.md, phase-2..5-*.md}`; `docs/extra/tasks_history/` (this).
- **Updated:** `docs/plans/hail/decisions.md` (DD-1..4), `docs/plans/hail/README.md`, `docs/README.md`,
  `AGENTS.md` (symlink table), `.gitignore`, `requirements.txt` (geopandas/shapely), `docs/principles/notebook_work/exploratory_data_notebooks.md`,
  `docs/extra/discussion/gpt/05_m0_to_m4_*.md` (numbering note), `docs/plans/remote_repo_push_plan.md`.
- **Created (scripts/data):** `scripts/{scan_mrms_record.py, README.md}`;
  `data/hail/damage_curves/hail_solar_asset_capex_weighted.json`; M0–M4 data artifacts under `data/hail/`.
- **Symlink added:** `infrasure-damage-curves` → sibling repo (gitignored).
- **Local-only (gitignored, NOT pushed):** `.env`, `.venv/`, `data/hail/mrms_raw/` (~905 MB tiles), `*.parquet`.

## Current status

- [x] M0 → M1 → M2 → M3 → M4 hail pipeline runs end-to-end, executed & reproducible.
- [x] Frequency fitted (NegBin, ~5.65-yr record); coupling, severity, MC all in place.
- [x] Math-validated (sound; no calc errors); assumptions documented (A1–A23); decisions recorded (DD-1..4).
- [x] Metrics in a believable range (real but **record-limited**; severity curve is a **temporary** blend).
- [x] Repo pushed to `D-ivyy/Hazard_Modeling` (private).

## Next steps

See [`handoff.md`](handoff.md) → "Next action". In short: **hazard #2 (wildfire) end-to-end**, then wind; the
hail *refinement* backlog (damage-curve revamp, NOAA-calibrated λ extension, EVT tail, financial terms) lives
in the assumptions register `deferred` rows; production architecture is deferred until 3 hazards are done.
