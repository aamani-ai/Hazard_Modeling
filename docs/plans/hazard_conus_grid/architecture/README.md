# Grid Production Architecture — plan of record

The build plan for moving the CONUS grid off notebooks/scripts into a reusable **package**: a shared risk
engine, per-peril pipelines, and product drivers. Graduated from the discussion doc
[`../../../extra/discussion/conus_grid/04_production_architecture.md`](../../../extra/discussion/conus_grid/04_production_architecture.md)
and modelled on the layered-pipeline variant (`Learning/coding/project_structure/variants/layered-pipeline.md`).

**Read order:** this README (shape + decisions + relationships) → [`contracts.md`](contracts.md) (the typed
boundary objects) → [`migration_plan.md`](migration_plan.md) (Phase A–D + the function-extraction map).

> **Scope.** The CONUS grid (use case 2). The deep per-asset product stays in notebooks for now but is **not a
> separate engine** — it is a future *second driver* of this same engine (DD-G11). Settled inputs (not
> re-decided here): the 0.25° grid + `cell_id` (DD-G1), the two-layer durable products (DD-G2), the dedicated
> roots (DD-G3), the GCS root + dev/releases (DD-G6), runner-after-measured-batch (DD-G7), task-indexed fanout
> (DD-G9).

---

## The boundary — the one decision that matters most

Peril-specific logic ends, and the shared generic engine begins, at the **per-cell hazard-distribution
object** M1 emits (DD-G12). It is exactly our asset-free `M0/M1`-vs-`M2–M4` seam, made a typed, versioned
contract. Mapped to the layered-pipeline reference and to the source-qualification A/B/C boundary
([`../common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md)):

| Our layer | Reference / A·B·C | Side |
|---|---|---|
| **M0** raw | L1 Evidence + L2 Reconstruction · **A** Source-Qualification + **B** Extraction-Adapter | peril-specific |
| **M1** catalog · freq · severity | L3–L5 · **C** Modeling | peril-specific → **emits the boundary object** |
| — | **▶ typed, versioned per-cell hazard-distribution object ◀** | — |
| **M2** coupling | Exposure (event × asset) | shared framework + per-(peril×asset) coupling type |
| **M3** damage | Vulnerability (framework shared; curves peril-specific) | shared framework + peril curves |
| **M4** loss · metrics | Loss + Aggregation + Metrics + Outputs | shared engine |

**Nothing bypasses the boundary:** a peril never calls engine internals; the engine imports no peril. The
two contracts are defined field-by-field in [`contracts.md`](contracts.md).

## One engine, two drivers (DD-G11)

The engine consumes `(hazard distribution + an exposure input)`. The exposure input is the *only* difference
between products — canonical-asset-at-every-cell (grid driver, V1) vs one real asset (deep-per-asset driver,
future). Same engine, two drivers; the engine is never duplicated. This is off-grid==on-grid as code.

## Package layout

Monorepo with **extractable subpackages** (DD-G14): each is independently installable, so extraction to a
standalone repo later is mechanical, not a refactor. Layout follows the reference's root-level peers (this
refines `04`'s `src/` shorthand; a single `src/` umbrella is a cosmetic alternative). Annotations show the
*actual current code* each piece absorbs (verbatim from the grounding):

```
Hazard_modeling/
├── shared/                               ← the risk ENGINE — peer of pipelines; imports NO peril
│   ├── schemas/                          ← ★ typed, versioned contracts (see contracts.md)
│   │   ├── hazard_distribution.py        ←   the boundary object (M1 emits / engine consumes)
│   │   └── risk_metrics.py · exposure.py
│   ├── engine/                           ← M4, extracted from 03_full_m1_..._smoke.py, made generic
│   │   ├── monte_carlo.py                ←   run_cell_mc()  (generic p_hit / conditional_loss_usd cols)
│   │   ├── metrics.py                    ←   exceedance_metrics()  (RP & VaR ladders → config; capacity_kwp arg)
│   │   ├── quantile.py                   ←   weighted_quantile()
│   │   └── validate.py                   ←   analytic-EAL · zero-loss=exp(−λ) · aep≥oep checks (now inline)
│   ├── exposure/                         ← M2 framework: coupling-type dispatch (areal | field | site)
│   ├── vulnerability/                    ← M3 framework: apply(size, asset)→DR  (curves live with the peril)
│   ├── statistics/                       ← fitting · return periods · EVT (future seam)
│   ├── io_base/                          ← is_gcs_uri · split_gcs_uri · up/download · gcs_prefix_exists (today byte-duplicated across 2 scripts)
│   └── orchestration/engine.py           ←   run M2–M4 given (hazard dist + exposure + curves)
├── pipelines/
│   └── hail/                             ← peril-specific (M0/M1), installable
│       ├── adapter.py                    ←   SourceAdapter: read_mrms_grib · native_points_to_cell_id · build_daily_panel
│       ├── layers/  (l1_evidence … l5_hazard_distribution)
│       ├── plausibility_qc/              ←   ~200 mm cap + frequency flag (asset-free; see hail/05)
│       ├── vulnerability_curves/         ←   the canonical hail×solar curve artifact (clamp @ 100 mm)
│       ├── reconcile.py · io/ · validation/ · config/   ←   THRESHOLD_MM, PRODUCT, ALLOWED_STATUSES, 13085, 300 → config
├── drivers/
│   ├── conus_grid/                       ←   canonical asset / cell; fans out (DD-G9 task-indexed Cloud Run)
│   │   └── canonical_assets.py           ←   CANONICAL_SOLAR (100 MW / 1.5 km² / $148.3M) + future wind
│   └── (deep_per_asset/  ← future second driver of the same engine)
├── orchestration/                        ← Cloud Run job entrypoints + batch specs (reuse DD-G9 fanout)
├── docs/ · Notebooks/ · data/ · scripts/ ← unchanged; Notebooks go THIN (import the package; Hayhurst bridge = validation)
```

- **`shared/` is a peer of pipelines, not a child** — explicit dependency direction (pipelines + drivers import `shared`; `shared` imports nothing peril-specific).
- **`io/` isolates cloud/DB** so layers are pure and unit-testable without mocking GCS.
- **`orchestration/` separate from layers** — layers say *what*; orchestration says *how it runs*.

## New decisions (this plan) — `DD-G10`–`DD-G14`

Recorded in [`../decisions.md`](../decisions.md):

| ID | Decision |
|---|---|
| **DD-G10** | Grid code becomes an importable package; notebooks go thin. |
| **DD-G11** | One shared, exposure-agnostic risk engine; grid + deep-per-asset are two drivers of it. |
| **DD-G12** | The peril→engine boundary is the typed, **versioned** per-cell hazard-distribution object. |
| **DD-G13** | New perils plug in via a SourceAdapter — the five-blank contract; honor the A/B/C boundary + promotion gate. |
| **DD-G14** | In-repo monorepo with extractable subpackages; no repo split for the grid. |

## Relationship to existing docs

| Existing doc | This plan's relationship |
|---|---|
| [`../common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md) | **Builds out** — its adapter-config / output-contract tables + the A/B/C boundary + promotion gate are the seed this engine implements. Don't contradict. |
| [`../decisions.md`](../decisions.md) | **Cross-reference; new IDs `DD-G10+`.** Reference DD-G1/2/3/6/7/9; don't re-decide them. |
| [`../README.md`](../README.md) | **Extend** — add `architecture/` to the planning layout + read order. |
| [`../common/benchmark_grid.md`](../common/benchmark_grid.md) · [`../common/validation.md`](../common/validation.md) · [`../common/gcp_execution_and_storage_conventions.md`](../common/gcp_execution_and_storage_conventions.md) · [`../common/storage_artifacts.md`](../common/storage_artifacts.md) | **Cross-reference (canonical inputs / conventions / test targets)** — the engine conforms, doesn't re-specify. |
| [`../hail/v1_mrms_only_grid_build.md`](../hail/v1_mrms_only_grid_build.md) · [`../hail/m0_m1_scaleout_execution.md`](../hail/m0_m1_scaleout_execution.md) | **Generalizes** — these stay the hail-specific build spec + as-built execution log; this plan lifts their patterns to a hazard-agnostic engine. Reference, don't restate. |

## Validation families → enforcement points

The engine's test/contract plan maps the [`../common/validation.md`](../common/validation.md) families to layers:

| Family | Enforced at |
|---|---|
| Grid-join · Coverage (no-data ≠ zero) | **adapter layer** (B) |
| Metric identity (`PML_T = VaR_(1−1/T)`; AEP/OEP separate) · Tail-caveat | **risk/modeling layer** (C / engine) |
| External-anchor · Point-vs-cell (Hayhurst) | **cross-product validations** |

## Status & next

**Engine + hail pipeline + grid driver built and proven** — every extraction reproduces the worked
outputs (bit-identical, offline gates; no expensive re-runs):

| Layer | Home | Gate |
|---|---|---|
| **Phase A — shared engine** ✓ | `shared/risk_engine/engine` (`run_cell_mc` · `exceedance_metrics` · `weighted_quantile` · `validate`) + `io_base` | smoke metrics reproduced to ~2e-16 |
| **Phase B — hail M0/M1 adapter** ✓ | `pipelines/hail` (M0 `build_daily_panel`, M1 `build_m1_hazard_layer`) | reconciled M0 (27.1M rows) + the 13,085-cell M1 reproduced exactly; ingest script + Cloud Run image re-pointed |
| **M2/M3 + the grid driver** ✓ | `shared/{exposure,vulnerability,orchestration,config}` + `pipelines/hail/{coupling,damage}` + `drivers/conus_grid` | the 5 smoke cells × 2 policies reproduced to ~2e-16; the full 13,085-cell hail×solar risk layer is the first product |
| **Phase C — typed contracts** (next) | `shared/schemas` (hazard_distribution + risk_metrics, `schema_version`, typed enums) | every artifact validates; canonical RP/VaR ladder pinned in `shared/config` (the ladder already lives in `config.py`) |
| **Phase D — second peril (wildfire)** | the five blanks only | wildfire M1 + a canonical-solar smoke with no new `shared/` code |

Plus the deliberate **plausibility QC** (the ~200 mm cap + frequency flag) as a separate M1
numbers-changing step (not folded into the refactor).
