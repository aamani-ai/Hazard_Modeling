# Notebooks — Hail → Solar pipeline

The executed, step-by-step end-to-end workflow for **hail**. Driven by the plan in
[`../../docs/plans/hail/`](../../docs/plans/hail/README.md) and the per-phase loop in
[`../../docs/workflows/feature_workflow.md`](../../docs/workflows/feature_workflow.md). Datasets are saved
under [`../../data/hail/`](../../data/hail). Kernel: `.venv` (`hazard_modeling`).

## `m0_input_data/` — the M0 (input-data) layer, **one notebook per source**  ·  [📖 folder README](m0_input_data/README.md)

The whole point of the M0→M3 architecture is to test *multiple* input datasets behind one interface, then
reconcile them. Each cell carries description → code → output/plot/table, and does a *complete-pass* field
dictionary (per `docs/principles/notebook_work/`).

| Notebook | Source | Grain | Status |
|----------|--------|-------|--------|
| `01_noaa_hydronos.ipynb` | NOAA Storm Events (Hydronos API) + FEMA NRI (reference-only) | **point reports** (hail size + location; no footprint) | ✅ built + executed |
| `02_mrms_aws.ipynb` | MRMS MESH (AWS Open Data) | **gridded** → real event **footprints**; **opens with a from-scratch "what is this data" walkthrough** (§1–§7) before exploring (§8–§11) | ✅ built + executed |

> **New to MRMS?** `02` now **starts from the very basics** — NOAA is a *list of events*; MRMS is a *picture*
> (a grid of hail-size numbers). §1–§7 explain it ground-up (mental model → the actual bytes/numbers → the
> field→threshold→polygon journey → how we fetch it) before §8–§11 explore the window and emit the M0 record.
> Complex raw data earns this pass — see [`learning_logs/03`](../../docs/learning_logs/03_meet_complex_raw_data_from_scratch.md).

> **Reconciling the sources is *not* a third M0 source.** Combining the sources into one clean event set is
> the front of **M0→M1 (the event catalog)** — A20's "catalog construction" — so it lives in `m1_catalog/`
> below, not here. `m0_input_data/` holds only the per-source M0 explorations.

## `m1_catalog/` — the M0 → M1 layer (the event catalog)  ·  [📖 folder README](m1_catalog/README.md)

Normalizes the M0 evidence into **one canonical event record per physical event** (a footprint raster
bundle). Per [`DD-1`](../../docs/plans/hail/decisions.md): **MRMS is the spine** (footprints), **NOAA is a
cross-check overlay** (calibration only — adds no events). Plan:
[`../../docs/plans/hail/phase-2-event-catalog.md`](../../docs/plans/hail/phase-2-event-catalog.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_event_catalog.ipynb` | MRMS hail-days → canonical `Event` records (real **footprint-swath polygons**) + `CatalogManifest`; NOAA cross-check → `confidence_flags` | `data/hail/hayhurst_hail_m1_catalog.parquet` (**GeoParquet**) + `…_catalog.geojson` + `…_m1_manifest.json` | ✅ built + executed |

## `m2_coupling/` — the M1 → M2 layer (does the event hit the asset?)  ·  [📖 folder README](m2_coupling/README.md)

Hail = **areal hit-or-miss**: per-event Minkowski hit probability `p = (√F + √s)² / A`, thinning the regional
rate to the asset — **fixing the old repo's point-factor (`F/A`) error**, with known-answer checks. Plan:
[`../../docs/plans/hail/phase-3-coupling.md`](../../docs/plans/hail/phase-3-coupling.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_coupling.ipynb` | per-event `pᵢ` (Minkowski) + old-repo comparison + geometric cross-check; carries intensity to M3 | `data/hail/hayhurst_hail_m2_coupled.parquet` + `…_m2_summary.json` | ✅ built + executed |

## `m3_damage/` — the M2 → M3 layer (how bad is it, if it hits?)  ·  [📖 folder README](m3_damage/README.md)

Severity: each event's hail size → a **curated** PV damage curve → a damage ratio → the **conditional** dollar
loss (the full loss *if it hits*; `pᵢ` carried, never multiplied in). Plan:
[`../../docs/plans/hail/phase-4-damage.md`](../../docs/plans/hail/phase-4-damage.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_damage.ipynb` | curated `size → damage ratio` curve → per-event damage ratio + conditional loss | `data/hail/hayhurst_hail_m3_damage.parquet` + `…_m3_summary.json` | ✅ built + executed |

## `m4_loss_metrics/` — the M3 → M4 layer (loss & metrics)  ·  [📖 folder README](m4_loss_metrics/README.md)

The finale: **compound-Poisson Monte Carlo** — per simulated year, `Bernoulli(pᵢ)` + full conditional loss →
annual AEP/OEP vectors → **EAL / VaR / PML / TVaR**. *The part the old repo broke* — done right, with a
Method-0 contrast + known-answer checks. Metrics are **illustrative** (placeholder λ — DD-2). Plan:
[`../../docs/plans/hail/phase-5-loss-metrics.md`](../../docs/plans/hail/phase-5-loss-metrics.md).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `01_loss_metrics.ipynb` | compound-Poisson MC → AEP/OEP → EAL/VaR/PML/TVaR; Method-0 contrast; λ sweep | `data/hail/hayhurst_hail_m4_annual_vectors.parquet` + `…_m4_metrics.json` | ✅ built + executed |

---

**🎉 The full M0 → M4 hail skeleton now runs end-to-end** — raw evidence → catalog → coupling → damage →
annual loss → risk metrics, the right way. Production path: widen the MRMS record (→ real λ), calibrate the
damage curve, add financial terms + an EVT tail (see each layer's `📖 folder README` and the
[assumptions register](../../docs/plans/hail/assumptions.md) `deferred` rows).
