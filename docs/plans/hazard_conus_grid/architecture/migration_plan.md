# Architecture — migration plan (Phase A–D)

How we move from today's notebooks/scripts to the package **without breaking the working hail pipeline**. The
current hail outputs + the Hayhurst bridge are the **regression oracle**: each phase must reproduce them
before the next begins. Every phase ships working.

---

## The function-extraction map (what moves where)

Grounded in the actual code (verbatim line refs from the smoke notebook and the M0 scripts). The job is to
*relocate and parameterize*, not rewrite the math.

| Current code (file · symbol) | Moves to | Change on the way |
|---|---|---|
| `…/03_full_m1_..._smoke.py` · `weighted_quantile()` (L484) | `shared/engine/quantile.py` | none — already generic |
| ` ` · `run_cell_mc()` (L500) | `shared/engine/monte_carlo.py` | read **generic** columns `p_hit` / `conditional_loss_usd` (today hardcodes `p_hit_solar`, `conditional_loss_usd`) |
| ` ` · `exceedance_metrics()` (L529) | `shared/engine/metrics.py` | RP & VaR ladders + PML ladder → **config args** (today module-globals); take `capacity_kwp` arg (today reads `CANONICAL_SOLAR["capacity_mw"]` at L533) |
| ` ` · cap (`np.minimum(aep_uncapped, tiv_usd)`, L522) + analytic-EAL / zero-loss / `aep≥oep` checks (L648–666) | `shared/engine/validate.py` | lift the inline QA into a `validate_mc()` helper |
| `run_mrms_v1_...py` + `reconcile_...py` · `is_gcs_uri` · `split_gcs_uri` · `download_*` · `upload_*` · `gcs_prefix_exists` | `shared/io_base/` | de-duplicate (today byte-copied across both scripts) |
| `…_smoke.py` · `logistic()` (L399) · `damage_ratio()` (L403) · the inline `p_hit` Minkowski (L360–366) | `pipelines/hail/vulnerability_curves/` + `…/coupling` | stay peril/asset-specific; engine consumes a generic `p_hit` + `conditional_loss_usd` produced upstream |
| `…_smoke.py` · `CANONICAL_SOLAR` (L131–139) · `SEVERITY_POLICIES` (L144–150) | `drivers/conus_grid/canonical_assets.py` + config | per-asset exposure profile + the severity-policy axis — driver/config, not engine |
| `run_mrms_v1_...py` · `read_mrms_grib` · `native_points_to_cell_id` · `build_daily_panel` · `THRESHOLD_MM` · `PRODUCT` · `ALLOWED_STATUSES` · `--expected-cells 13085` · `--max-mesh-warning-mm 300` | `pipelines/hail/adapter.py` + `…/config/` | the MRMS SourceAdapter; the hail constants become per-peril config |
| Cloud Run job + `deploy-…yml` (`MRMS_M0_*`, task-indexed) | `orchestration/` + a generalized job | keep the DD-G9 task-indexed fanout pattern; parameterize the peril/source |

> **Engine-leak checklist (must be gone after Phase A):** no `*_solar` column names, no `CANONICAL_SOLAR`
> reference, no hardcoded RP/VaR ladders, no `mesh_*` names inside `shared/`. The engine knows only the two
> contracts ([`contracts.md`](contracts.md)).

## Phases & gates

```
  Phase A — Extract the ENGINE                                         (no behavior change)
    run_cell_mc · exceedance_metrics · weighted_quantile · validate · io_base → shared/
    re-wire the hail smoke notebook to IMPORT shared/ (delete the inline copies)
    ✓ GATE: identical hail M2–M4 metric rows for the 5 smoke cells, both severity policies;
            Hayhurst reference-bridge numbers unchanged (EAL 5.7% / PML₁₀₀ 54% / λ_asset 0.26).

  Phase B — Wrap hail M0/M1 as the first SourceAdapter
    read_mrms_grib · native_points_to_cell_id · build_daily_panel → pipelines/hail/adapter.py
    THRESHOLD_MM / PRODUCT / ALLOWED_STATUSES / 13085 / 300 → pipelines/hail/config/
    fold in plausibility QC (~200 mm cap + freq flag); reconcile via shared/io_base
    ✓ GATE: identical reconciled M0 (27,099,035 rows · 13,085 cells · 2,071 dates · 0 dup ·
            streaming_reconciliation_passed_row_contract) and identical M1 (13,085 rows).

  Phase C — Code-enforce the contracts; thin the notebooks
    shared/schemas/ : hazard_distribution + risk_metrics, with schema_version + typed enums (contracts.md)
    validate at the seams; pin the canonical RP/VaR ladder in config (reconcile the 200-RP discrepancy)
    notebooks become explore/validate harnesses that IMPORT the package
    ✓ GATE: every current artifact validates against its schema; the 6 validation.md families pass at their
            enforcement points; Hayhurst bridge still green.

  Phase D — Prove the seam: second peril
    add wildfire as a SourceAdapter (FSim) — the five blanks only; engine/drivers/orchestration untouched
    ✓ GATE: wildfire grid M1 + a canonical-solar smoke run with NO new shared/ code.
            If it isn't mostly "fill the five blanks," the abstraction is wrong — fix it before scaling.
```

**Sequencing rationale.** Engine first (Phase A) because it's pure relocation with a tight known-answer gate
(the smoke numbers) — lowest risk, immediate de-duplication. M0/M1 adapter next (Phase B) because the
reconciled-row contract is an exact, cheap oracle. Contracts (Phase C) once both ends exist to validate.
Phase D is the real test of reuse.

## The five blanks (DD-G13) — what each new peril fills

```
  1. SourceAdapter      raw source → per-cell-day evidence   (+ a plausibility-QC hook)
  2. M1 fit             frequency + severity → the hazard-distribution boundary object
  3. coupling type      areal | field-intensity | site-conditioned   (dispatched by shared/exposure)
  4. damage curve       a canonical curve artifact reference          (M3 contract)
  5. config             peril id · source URIs · thresholds · canonical asset(s)
  ───────────────────────────────────────────────────────────────────────────────────
  REUSED unchanged: shared/engine · both drivers · orchestration · the contracts · io_base · %-TIV reporting.
```

Honor the A/B/C source-qualification boundary + the **promotion gate** (coverage denominator · target
reference base · exact-target-vs-context · source-era comparability · bias treatment · frequency definition ·
tail treatment · provenance) from [`../common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md)
before a new source enters M1.

## Out of scope (leave clean seams, don't build now)

- The deep-per-asset *driver* + new database — a future second driver of this engine.
- V1.5/V2 accuracy: MESH de-biasing, EVT tail (→ `shared/statistics/` + the severity object), NegBin/pooled
  frequency (→ the `(family, params)` slot), conditional-DR distribution, financial terms (→ a future
  `shared/financial/` layer the deep per-asset will need first).

## Cross-references

- Shape + decisions: [`README.md`](README.md) · contracts: [`contracts.md`](contracts.md).
- The hail QC that the adapter folds in: [`../../../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md`](../../../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md).
- The as-built execution patterns this generalizes: [`../hail/m0_m1_scaleout_execution.md`](../hail/m0_m1_scaleout_execution.md) · [`../hail/v1_mrms_only_grid_build.md`](../hail/v1_mrms_only_grid_build.md).
