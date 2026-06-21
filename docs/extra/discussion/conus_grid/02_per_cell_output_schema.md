# 02 — Per-Cell Output Schema

*A discussion doc → proposed output contract. The complete set of risk metrics stored **per cell**, so the
map can select **any one** at render time. Reviewed/approved in discussion; graduated into the plan scaffold at
`docs/plans/hazard_conus_grid/output_schema.md`.*

---

## How to read this (the one mental model that prevents redundancy)

We **store two exceedance curves + EAL + the conditional-severity distribution**. Every metric you'd put on
a map — PML, VaR, TVaR, exceedance probability — is a **labeled readout of those**, not an independent
quantity. Concretely:

```
        the per-cell loss distribution  (from the M4 Monte Carlo)
                          │
        ┌─────────────────┼──────────────────┐
   AEP curve          OEP curve          EAL (the mean)
   (annual            (largest single
    AGGREGATE loss)    OCCURRENCE / yr)
        │                  │
        └──── read at a RETURN PERIOD T  ──►  PML_T          ┐
        └──── read at a CONFIDENCE  c   ──►  VaR_c           │  same curve,
        └──── average BEYOND c          ──►  TVaR_c          │  different label
        └──── invert at a LOSS level X  ──►  P(loss > X)     ┘
```

**The identity to keep straight:** `PML at return period T  ≡  VaR at confidence (1 − 1/T)`. So
**AEP-PML₁₀₀ ≡ AEP-VaR₉₉ ≡ the 1-in-100 annual aggregate loss** — one number, three names. We store the curve
once and expose the named readouts as columns for convenience; they are not separately simulated.

**Two definitions to lock (basics-spot-on):**
- **AEP** (Aggregate Exceedance Probability) = distribution of the **annual total** loss (sum of all events
  in a year). The aggregate/annual view — relevant to a balance sheet, a lender, a portfolio.
- **OEP** (Occurrence Exceedance Probability) = distribution of the **single largest occurrence** in a year.
  The per-event view — relevant to underwriters/brokers. For high-frequency hazards (hail) `AEP > OEP` at a
  given return period; for rare hazards they converge. `[REF]` (team PML terminology decision, Thursday sync.)

---

## The two "doublings" (stated once, apply everywhere below)

1. **Per asset type:** every metric is produced for **`solar`** and **`wind`** (the two canonical assets) —
   column prefix `solar_*` / `wind_*`.
2. **Per unit:** every dollar metric is stored in **both `_usd` and `_pct_tiv`** (% of TIV). Naming mirrors
   the wildfire index (`solar_eal_usd`, `solar_eal_pct_tiv`) so the hazard grid is column-compatible with the
   rest of the platform.

So a single conceptual metric like "EAL" becomes 4 columns: `{solar,wind}_eal_{usd,pct_tiv}`. The tables
below list the **conceptual** metric once; multiply by these two axes for the physical column count.

**Return-period ladder** (where curves are sampled): `T ∈ {2, 5, 10, 25, 50, 100, 250, 500}` yr.
**Confidence ladder** (VaR/TVaR): `c ∈ {95, 99, 99.5}`.

---

## A. Identity & exposure

| Field | Unit | Note |
|---|---|---|
| `cell_id` | — | join key to the 0.25° benchmark grid |
| `lat_c`, `lon_c` | ° | cell centre (where the canonical asset is placed) |
| `state`, `iso` | — | optional context labels |
| `cell_area_km2` | km² | latitude-varying (~500–700); for density normalisation |
| `coverage_flag` | enum | `valued` / `no_data` — **"no coverage ≠ zero risk"** (the legacy bug) |
| `asset_type` | enum | `solar` / `wind` |
| `capacity_mw` | MW | 100 (canonical) |
| `asset_area_km2` | km² | **solar 1.5 · wind 30** — see [`assumptions.md`](assumptions.md) G2/G3 (solar measured; wind assumed) |
| `tiv_usd`, `tiv_usd_per_kwp` | $ | total insured value; per-kWp basis carried for cross-checks |

## B. Frequency & severity — the building blocks (from M1–M3)

| Field | Unit | Note |
|---|---|---|
| `lambda_cell` | /yr | regional event rate in the cell (collection rate) |
| `p_hit` | — | asset hit probability (areal perils; `1` or n/a for field/site-conditioned) |
| `lambda_asset` | /yr | `= lambda_cell · p_hit` — the asset's annual event rate |
| `fano_phi`, `freq_dist` | — | over-dispersion + distribution family (NegBin; Poisson special case) |
| `cond_loss_mean` | %TIV, $ | mean loss **given an event hits** (frequency-free severity) |
| `cond_loss_p50/p90/p95/p99` | %TIV, $ | conditional-severity percentiles — the M3 distribution, **not** annualised |
| `cond_loss_max` | %TIV, $ | largest modelled conditional loss (curve cap) |

## C. Headline

| Field | Unit | Note |
|---|---|---|
| `eal` | %TIV, $ | **Expected Annual Loss** — the distribution mean; matches the analytic `λ_asset·E[loss]` |
| `eal_usd_per_kwp_yr` | $/kWp/yr | per-kWp basis (platform-compatible) |
| `loss_ratio_pct` | % | **= EAL / TIV.** ⚠️ **Not** insurance ELR — there is no premium/policy/expense in the denominator. Label it "physical-damage loss ratio," never "expected loss ratio." `[REF]` (same caveat the wildfire screening doc makes.) |

## D. The two exceedance curves (the stored objects)

| Field | Unit | Note |
|---|---|---|
| `aep_loss_rp{T}` | %TIV, $ | **AEP** annual-aggregate loss at each return period `T` |
| `oep_loss_rp{T}` | %TIV, $ | **OEP** largest-occurrence loss at each return period `T` |

## E. Named readouts (derived from D — stored as columns for one-click map selection)

| Family | Columns | = which point on the curve |
|---|---|---|
| **PML — AEP** | `pml_aep_rp{100,250,500}` | aggregate/annual PML (lender / portfolio view) |
| **PML — OEP** | `pml_oep_rp{100,250}` | per-occurrence PML (underwriter / broker view) |
| **VaR** | `var_aep_{95,99,99.5}`, `var_oep_{95,99}` | `var_aep_99 ≡ pml_aep_rp100` (the identity above) |
| **TVaR** (expected shortfall) | `tvar_aep_{95,99}`, `tvar_oep_{95}` | mean loss **beyond** the VaR threshold — the genuine tail-average |
| **Annual exceedance prob.** | `prob_annual_loss_gt_{1,5,10,25}pct_tiv` | inverts the AEP curve: P(annual loss > X% TIV) |

## F. Provenance / QA

| Field | Note |
|---|---|
| `n_events_cell` | events feeding the cell's M1 fit — the small-n canary (sparse cells → unstable fits; see storage discussion) |
| `mc_years` | **250,000** (see MC-depth note below) |
| `hazard_vintage`, `record_span` | data currency |
| `model_version`, `engine_git_sha` | so grid ↔ point never drift unnoticed (the EAL-bug lesson, [`01` §4](01_ideal_architecture_compute_and_grid.md)) |

---

## MC depth & the deep-tail caveat (decided: 250k)

`mc_years = 250,000`. **Why not 100k:** the body (EAL, PML₁₀₀) is stable at 100k, but several columns above are
*deep tail* — a 1-in-500 loss has only ~200 samples at 100k, and `tvar_aep_99` averages the worst 1% (~1,000
yrs), both noisy. 250k roughly triples the tail sample at ~no marginal cost (Stage 2 is embarrassingly
parallel — compute isn't the constraint; tail stability is). **Standing caveat:** even at 250k, the deepest
readouts (`*_rp500`, `tvar_*_99`) inherit the **bootstrap-truncation** bias ([hail A23](../../../plans/hail/assumptions.md)) **until** severity is drawn from a *fitted distribution with an EVT tail* rather than resampled
observed events. That fix is the **same move** as the storage decision (persist fitted distributions, not raw
catalogs) — so flag `*_rp500` / `tvar_*_99` as *provisional* on every map until EVT lands. → [`assumptions.md`](assumptions.md) G5.

## What the map does with this

The grid stores **all** of A–F. A map view is just *"pick one column"* — e.g. `solar_eal_pct_tiv`,
`wind_pml_aep_rp100_usd`, `solar_prob_annual_loss_gt_10pct_tiv`. No recompute to switch views; the choice of
*which* to show is a display decision made at that time, exactly as you wanted.

---

## Cross-references

- The architecture that produces these columns (Stage 2): [`01_ideal_architecture_compute_and_grid.md`](01_ideal_architecture_compute_and_grid.md).
- The canonical-asset + area assumptions behind `tiv` / `asset_area_km2`: [`assumptions.md`](assumptions.md).
- Bootstrap-truncation tail caveat: [hail A23](../../../plans/hail/assumptions.md); EVT is the resolution.
- Column-naming lineage (`*_usd` / `*_pct_tiv` / `*_100mw_*`): the wildfire index delivery schema
  (`renewablesinfo/wildfire_analysis_lab/docs/delivery/schema/wildfire_risk_layer_schema.md`).
