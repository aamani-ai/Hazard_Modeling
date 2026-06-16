# Hazard CONUS Grid — Output Schema

This is the planned per-cell contract for the CONUS grid. It is intentionally split into:

1. the reusable **hazard-distribution layer** from M0/M1; and
2. the platform-facing **risk-metrics layer** from M2-M4.

Detailed discussion lives in
[`docs/extra/discussion/conus_grid/02_per_cell_output_schema.md`](../../extra/discussion/conus_grid/02_per_cell_output_schema.md).

---

## Layer 1 — Per-Cell Hazard Distribution

One row per `hazard × cell_id` before asset damage/loss.

| Field family | Examples | Purpose |
|---|---|---|
| Identity | `hazard`, `cell_id`, `lat_center`, `lon_center`, `coverage_flag` | Join to benchmark grid and map coverage. |
| Frequency | `lambda_cell`, `freq_dist`, `fano_phi`, `freq_fit_status` | Annual event frequency distribution in the cell. |
| Severity / size | hail size distribution, wildfire flame-length distribution, wind gust profile | Hazard magnitude distribution before asset vulnerability. |
| Provenance | `hazard_vintage`, `record_span`, `source_product`, `source_version` | Auditable source lineage. |
| QA | `n_events_cell`, `sparse_cell_flag`, `validation_flags` | Identify cells that need pooling, caveats, or exclusion. |

The exact severity columns are hazard-specific. The interface requirement is that M2 can ask:

```text
given hazard, cell_id, asset_type -> event count distribution + conditional event severity distribution
```

## Layer 2 — Per-Cell Risk Metrics

One row per `hazard × asset_type × cell_id` after damage/loss simulation.

| Field family | Examples | Purpose |
|---|---|---|
| Identity | `hazard`, `asset_type`, `cell_id`, `capacity_mw`, `asset_area_km2`, `tiv_usd` | Comparable canonical exposure. |
| Coupling | `p_hit`, `lambda_asset`, `exposure_tier` | How the cell hazard becomes asset events. |
| Conditional severity | `cond_loss_mean`, `cond_loss_p50`, `cond_loss_p95`, `cond_loss_p99`, `cond_loss_max` | Loss given event/hit, before annual aggregation. |
| EAL | `eal_usd`, `eal_pct_tiv`, `eal_usd_per_kwp_yr` | Mean annual physical damage loss. |
| AEP curve | `aep_loss_rp2`, `aep_loss_rp5`, `aep_loss_rp10`, `aep_loss_rp25`, `aep_loss_rp50`, `aep_loss_rp100`, `aep_loss_rp250`, `aep_loss_rp500` | Annual aggregate exceedance curve. |
| OEP curve | `oep_loss_rp2`, `oep_loss_rp5`, `oep_loss_rp10`, `oep_loss_rp25`, `oep_loss_rp50`, `oep_loss_rp100`, `oep_loss_rp250`, `oep_loss_rp500` | Largest single occurrence per year. |
| Named readouts | `pml_aep_rp100`, `pml_aep_rp250`, `pml_aep_rp500`, `var_aep_95`, `var_aep_99`, `tvar_aep_95`, `tvar_aep_99` | Convenience columns for map selection and reports. |
| QA/provenance | `mc_years`, `model_version`, `engine_git_sha`, `tail_caveat_flag` | Prevent grid-vs-point drift and surface weak tails. |

All monetary metrics should have both `_usd` and `_pct_tiv` forms unless the field is already dimensionless.

## Coupling Rule For Canonical Assets

The CONUS grid should not silently inherit the single-site 50-mile collection radius. For the grid product:

```text
M0/M1:
  hazard evidence belongs to the benchmark cell_id

M2-M4:
  canonical asset is placed inside that cell_id
  coupling uses the cell hazard evidence plus the canonical asset footprint/exposure assumption
```

For example, a 100 MW canonical solar plant should be modeled as a fixed canonical exposure within the cell,
not as "everything within 50 miles of the cell center." If we later want a neighborhood/smoothing rule, it
must be a named coupling decision with its own fields, QA flags, and caveats.

## Metric Identity

PML and VaR are readouts of the same exceedance curve:

```text
PML_T = VaR_(1 - 1/T)
```

So:

- `PML100 = VaR99`
- `PML200 = VaR99.5`
- `PML250 = VaR99.6`
- `PML500 = VaR99.8`

AEP and OEP must stay separate. AEP is annual aggregate loss; OEP is the largest single occurrence in a year.
