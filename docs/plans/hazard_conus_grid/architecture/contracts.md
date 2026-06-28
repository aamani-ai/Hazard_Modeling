# Architecture — the typed boundary contracts

The two typed, **versioned** contracts the engine is built around, defined field-by-field from the *actual*
current outputs (so the package codifies what already runs, then fixes the gaps). Enforced in code
(`shared/schemas/`, dataclass/pydantic), `schema_version` from day one (DD-G12).

```
   pipeline (peril)  ──emits──▶  [ Layer-1: hazard-distribution object ]  ──▶  shared engine
   shared engine     ──emits──▶  [ Layer-2: per-cell risk-metrics object ]  ──▶  outputs / map
```

---

## Contract 1 — the per-cell hazard-distribution object (the boundary)

**Today:** the hail M1 layer emits **52 persisted columns** (one row per served `cell_id`), stringly-typed,
with no `schema_version`. The contract **codifies these**, grouped, and **fixes** the gaps the grounding
flagged. Current fields (verbatim), by group:

**Identity / scope:** `hazard` · `cell_id` · `lat_center` · `lon_center` · `state_abbr` · `iso_rto` ·
`source_set` · `source_product` · `threshold_mm` · `record_span_start` · `record_span_end` · `n_source_dates`
· `m1_run_id` · `input_m0_reconciled_run_id`.

**Frequency:** `n_observed_days` · `n_no_coverage_days` · `n_no_hail_days` · `n_sub_severe_days` ·
`n_severe_hail_days` · `observed_day_fraction` · `observed_years` · `lambda_cell_raw` · `freq_dist`
(`"poisson_v1_default"`) · `freq_fit_status` · `annual_count_*` + `fano_phi_complete_years` + `fano_phi_status`
(dispersion **diagnostics only**) · `sparse_cell_flag` (`n_severe_hail_days < 5`) · `zero_hail_flag`.

**Severity:** `mesh_max_mm_raw` · `mesh_mean_mm_raw_on_severe_days` · `mesh_p50/p90/p95/p99_mm_raw_on_severe_days`
· `n_severe_days_with_size_sample` · native-pixel footprint counts · `extreme_mesh_ge_300mm_flag` ·
`extreme_mesh_cell_day_count` · `max_mesh_mm_raw_any_day` · `severity_magnitude_status` · `size_dist_status`.

**QA / provenance / use-governance:** `qa_flags` (semicolon string) · `allowed_use` · `not_allowed_use`.

**Enum values (verbatim, to be pinned as typed enums):**
- `severity_magnitude_status` ∈ { `no_severe_days`, `raw_mesh_body_only`, `raw_mesh_tail_requires_qa` }
- `size_dist_status` ∈ { `no_observed_severe_days`, `raw_empirical_size_body_available`, `raw_empirical_size_provisional_tail_flag` }
- `fano_phi_status` ∈ { `diagnostic_complete_years_only`, `not_available_zero_or_sparse_complete_year_counts` }
- `coverage_status` (upstream, M0) ∈ { `no_native_pixel_coverage`, `observed_no_hail`, `observed_sub_severe_hail`, `observed_severe_hail` }

**The fixes the contract adds** (gaps the grounding found — none change a number; they make the boundary typed and non-drifting):

| Fix | Today | Contract |
|---|---|---|
| **`schema_version`** | absent; "V1" buried in strings (`freq_dist="poisson_v1_default"`, `qa_flags` prefix `mrms_only_v1`) | a first-class, machine-comparable version field |
| **Frequency as `(family, params)`** | a *label* `freq_dist` + a loose `lambda_cell_raw` | a typed distribution object: `family="poisson"`, `params={lambda: lambda_cell_raw}` — so NegBin/pooled (V1.5) slots in without a schema break |
| **Severity as a typed object** | raw empirical quantiles + status flags | a typed severity object (V1: empirical summaries + `severity_magnitude_status`); the EVT/parametric tail (V1.5) fills the same slot |
| **Typed enums** | stringly-typed (`np.select` branches) | closed enums (the values above) |
| **Units + dtypes + nullability** | units only in notebook prose; `mesh_*` NaN-bearing, flags numpy-bool, none declared | per-field unit + dtype + null-rules on the schema |
| **`qa_flags` structured** | one packed semicolon string | a typed list/set of flags |
| Drop the phantom column | `max_mesh_mm_log1p_display` computed but never persisted | not in the contract (display-only stays in the QA notebook) |

> **Peril-agnostic vs hail-specific:** identity, frequency `(family, params)`, the QA/use-governance fields,
> and the *shape* of the severity object are the **generic** boundary every peril emits. The `mesh_*`
> severity summaries are hail's **instance** of the severity object — wildfire fills the same slot with
> flame-length fields. The contract pins the shape; the peril fills it.

## Contract 2 — the per-cell risk-metrics object (engine output)

One row per `hazard × asset_type × cell_id`. Fields verbatim from [`../output_schema.md`](../output_schema.md)
(Layer 2):

- **Identity:** `hazard` · `asset_type` · `cell_id` · `capacity_mw` · `asset_area_km2` · `tiv_usd`
- **Coupling:** `p_hit` · `lambda_asset` · `exposure_tier`
- **Conditional severity:** `cond_loss_mean` · `cond_loss_p50` · `cond_loss_p95` · `cond_loss_p99` · `cond_loss_max`
- **EAL:** `eal_usd` · `eal_pct_tiv` · `eal_usd_per_kwp_yr`
- **AEP curve:** `aep_loss_rp{2,5,10,25,50,100,250,500}`
- **OEP curve:** `oep_loss_rp{2,5,10,25,50,100,250,500}`
- **Named readouts:** `pml_aep_rp{100,250,500}` · `var_aep_{95,99}` · `tvar_aep_{95,99}`
- **QA / provenance:** `mc_years` · `model_version` · `engine_git_sha` · `tail_caveat_flag`

**Invariants the engine enforces** (from `output_schema.md` + `validation.md`):
- **Metric identity:** `PML_T = VaR_(1 − 1/T)` (so `PML100=VaR99`, `PML250=VaR99.6`, `PML500=VaR99.8`). PML/VaR are readouts of one exceedance curve.
- **AEP and OEP stay separate** (annual aggregate vs largest single occurrence).
- **USD + %TIV:** every monetary metric carries both `_usd` and `_pct_tiv` unless already dimensionless.
- **Tail caveat:** `tail_caveat_flag` set when the cell is sparse / bootstrap-limited.

**One discrepancy to reconcile (decision needed):** the return-period ladder differs between code and schema —
the smoke `.py` uses `RETURN_PERIODS = [2,5,10,25,50,100,200,250,500]` (includes **200**) and a VaR ladder
`[0.95,0.99,0.995,0.996,0.998]`, while `output_schema.md` lists `{2,5,10,25,50,100,250,500}` (no 200) and named
VaR `{95,99}`. **Resolution:** the ladder is **engine config**, not hardcoded; the canonical ladder is pinned
once in `shared/` config and both code and `output_schema.md` reference it. (Proposed canonical: include 200,
since `PML200 = VaR99.5` is a named readout.)

## Enforcement & versioning

- Both contracts are **code** (`shared/schemas/`, dataclass/pydantic), validated **at the seams** — a break
  surfaces at the layer, not three layers downstream ([*basics spot-on*](../../../principles/basics_spot_on.md)).
- `schema_version` on both from day one; the engine refuses an unsupported version (forward-compatible
  consumption), and migration functions can auto-upgrade older artifacts.
- The contracts are **peril- and asset-agnostic in shape**; perils/assets fill the instance fields.

## Cross-references

- The boundary's place in the pipeline: [`README.md`](README.md) · the A/B/C layers: [`../common/gridded_radar_source_qualification.md`](../common/gridded_radar_source_qualification.md).
- The risk schema source: [`../output_schema.md`](../output_schema.md).
- The QC fields feeding the severity object: [`../../../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md`](../../../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md).
- Validation families: [`../common/validation.md`](../common/validation.md).
