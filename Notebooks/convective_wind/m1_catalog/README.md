# M1 — Catalog (per-sub-peril hazard profile)

*M0 met the wind hazard as raw evidence (two data shapes); **M1 turns each into the typed handoff the shared loss
engine consumes** — a **frequency λ** + a **conditional severity distribution** on the 3-s gust, per sub-peril,
per site, with a manifest declaring the catalog's choices.*

**Where this sits:** [M0](../m0_input_data/README.md) → **M1 (catalog)** → M2 coupling → M3 damage → M4 loss.
Plan: [`docs/plans/convective_wind/m1_catalog.md`](../../../docs/plans/convective_wind/m1_catalog.md). Notebook:
[`01_catalog`](01_catalog.ipynb) (built).

## The fork — by coupling bucket, not physics invention

| | **Strong / straight-line wind** (site-conditioned) | **Tornado** (areal hit-or-miss) |
|---|---|---|
| frequency | **read** the ASCE RP curve → λ (profile-assembly, *no fit*) — the **wildfire** pattern | **fit** λ_collection from SPC (**bias-corrected**), thinned by p_hit in M2 — the **hail** pattern |
| severity | **Gumbel/exponential (ξ≈0)** on 3-s gust, log-linear, capped at L (the RP curve *is* the return-level — *not* a bounded GPD) | **bounded GPD (ξ<0)** on 3-s gust from the EF-mix, reaching the EF5 ceiling L |
| dispersion | **fano = 1 structural** (ASCE pre-integrated it) | **fit** Fano (NegBin if over-dispersed) |

Both routes emit the **same typed object** `{lambda_per_yr, fano_factor, magnitude_metric="3s_gust_ms",
severity_distribution{family:"bounded_gpd", mu, sigma, xi, L}, physical_bound_L_ms, tiv, footprint}`.

**Two separate per-sub-peril {λ, severity} profiles go out** — tornado [T] and strong wind [W] are treated as
**disjoint, independent event streams** (disjoint by data product: the ASCE basic-wind surface is **non-tornadic**
by construction, tornado = the SPC Tornado record — no shared physical event). M4 combines them **only** by
co-sampling both streams into one annual-loss distribution per simulated year; it never sums per-sub-peril tail
quantiles. The disjointness is a classification/data-product assumption, not a physical law (flagged) — in V1 it is
also safe because strong-wind damage is ~0 (gusts stay below the IEC survival onset).

## What `01_catalog` found

- **Strong wind = profile-assembly** off the ASCE curve (**R² ≈ 0.999** — Gumbel/log-linear, ξ=0): per-site
  λ ≈ **0.9/yr (Traverse)** / **0.4/yr (Shepherds)**. Even the 10⁶-yr gust (~75 m/s) sits **far below** IEC
  survival and L=113 → **strong wind contributes ~0 turbine damage** (the anchored-curve story, quantified).
- **Tornado = bias-corrected event-fit**: regional λ_collection ≈ **25/yr (Traverse — Fano≈12 → NegBin, real
  outbreak clustering)** vs **0.8/yr (Shepherds — Poisson)**; turbine-relevant **EF2+ ≈ 5.2/yr vs ~0.03/yr** —
  the catastrophic-tail contrast. Severity = bounded GPD (ξ<0) on the 3-s gust, μ-anchored, L-truncated.
- **Bias-correction (AWN-1)** done honestly: λ fit on the **1996+ detection-stable window** (shown + justified,
  *not* a silent filter), `-9` unrated excluded, **EF2+ full-record cross-check** (and EF2+ ≈ the turbine-relevant
  set, so the loss-relevant frequency is robust); rural-low EF bias flagged as pushing the true tail higher.
- **All 7 known-answer checks pass** (R²>0.99; ξ<0; severity support [μ,L]; integrates to 1; fano≥1).

## Inputs → outputs

M0 parquets (`*_wind_m0_asce/spc/geometry.parquet`) → `data/convective_wind/<asset>_wind_m1_catalog_{strongwind,tornado}.parquet`
(λ + bounded-GPD severity params) + `…_wind_m1_manifest.json` (the typed M2/M4 contract). Both sites.

## Key decisions & assumptions

[DD-WN-3](../../../docs/plans/convective_wind/decisions.md) (strong wind = ASCE profile-assembly, no fit) ·
[DD-WN-5](../../../docs/plans/convective_wind/decisions.md) (tornado = bias-corrected SPC fit, thinned in M2) ·
[DD-WN-8](../../../docs/plans/convective_wind/decisions.md) (bounded-GPD severity). Assumptions **AWN-15** (strong-wind λ from
ASCE, fano=1 structural), **AWN-1** (bias-corrected tornado λ), **AWN-17/18** (bounded GPD, μ_mean fit to the
curve not EAL), **AWN-16** (tornado sparse → TVaR+SE at M4), **AWN-19** (stationary λ).

**Next → M2 (coupling):** thin tornado λ_collection → λ_asset via the **path-aware Minkowski** (the §3b path stats
× the M0/03 polygon + turbine cloud); confirm strong wind's **p_hit ≈ 1** (site-conditioned, no thinning).
