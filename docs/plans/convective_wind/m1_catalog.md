# M1 — Catalog → Per-Sub-Peril Hazard Profile (the active plan)

*M0 met the raw hazard from **two data shapes**; **M1 turns each into the clean, typed handoff the loss engine
consumes** — a **frequency (λ)** + a **conditional severity distribution**, per sub-peril, per asset, with a
manifest declaring the catalog's choices. Wind's twist: the catalog **forks by coupling bucket** — strong wind is
**profile-assembly** (like wildfire), tornado is **event-fit** (like hail). Both feed the same engine.*

**Where this sits:** [M0 evidence](m0_input_data.md) → **M1 (catalog)** → [M2 coupling](m2_coupling.md) →
[M3 damage](m3_damage.md) → [M4 loss & metrics](m4_loss_metrics.md). Built for **both sites** (Traverse proving +
Shepherds Flat baseline). Thresholds μ and bound L are inherited from [00_hazard_definition](00_hazard_definition.md).
Notebook: `Notebooks/convective_wind/m1_catalog/01_catalog`.

---

## The structural twist — why wind M1 forks (read this first)

Hail M1 *extracted* discrete events and *fit* `λ_collection` from a short record (NegBin + dispersion). Wildfire
M1 *read* a pre-integrated profile (BP→λ, no fit) ([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
**Convective wind does both, in one notebook, split by sub-peril** — *one peril, two sub-perils* ([T] tornado +
[W] strong / straight-line wind), which sit in different coupling buckets
([discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)). *(Hurricane is a separate,
deferred peril, sharing only the 3-s-gust wind-damage curve — [DD-WN-9](decisions.md).)*

| | **Strong / straight-line wind** (site-conditioned) | **Tornado** (areal hit-or-miss) |
|---|---|---|
| Coupling bucket | bucket 3 — *no spatial miss* | bucket 1 — *footprint hits or misses* |
| Data shape (M0) | ASCE **pre-integrated RP gust surface** | SPC **path/strike record** |
| Frequency | **read the RP surface** (profile-assembly, no fit) — the *wildfire-analog* | **fit `λ_collection`** from SPC (bias-corrected), then thin by `p_hit` — the *hail-analog* |
| Severity | **Gumbel / exponential on 3-s gust (ξ ≈ 0)** above μ, capped at L — the ASCE RP curve is log-linear (R²≈0.999), *not* a bounded GPD with ξ<0 | **bounded GPD, ξ < 0** (reaches the EF5 ceiling L), or the F-scale posterior on 3-s gust, truncated at L |
| Analog built layer | wildfire ([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) | hail ([learning-06](../../learning_logs/06_collection_region_size_cancels.md), Minkowski) |

> **So M1 here is not one catalog — it's two profiles assembled by two routes, both emitting the *same* typed
> object** `{lambda_per_yr, fano_factor, magnitude_metric, severity_distribution, physical_bound_L, tiv,
> footprint}` to the shared compound-Poisson/NegBin engine. The fork is **by coupling bucket, not by physics
> invention** — strong wind *reuses* wildfire's M1 machinery, tornado *reuses* hail's. The "two shapes, one
> interface" pattern is a [learning-log](../../learning_logs/README.md) candidate once built.

---

## The five catalog choices (declared in the manifest, mirroring hail & wildfire)

1. **Ontology** — the unit is a **per-sub-peril, per-asset hazard profile**. Strong wind: `{λ (annual rate of a
   severe-wind event reaching the site), gust-severity distribution}`. Tornado: `{λ_collection (regional tornado
   rate), EF/gust-severity distribution, path-geometry stats}` → thinned to the asset in [M2](m2_coupling.md).
   The **magnitude observable is the 3-second peak gust** (the universal metric, [00_hazard_definition](00_hazard_definition.md)).
2. **Backbone / spine** — **strong wind: the ASCE 7-22 RP gust surface** (M0 `01_asce_hazard`); **tornado: the
   bias-corrected SPC SVRGIS record** (M0 `02_spc_storm_record`) for `λ` + path stats + EF severity. → [DD-WN-3](decisions.md) (strong wind), [DD-WN-5](decisions.md) (tornado), [DD-WN-8](decisions.md) (severity).
3. **Interface object** — the typed M1→M2/M4 handoff, per sub-peril per asset:
   `{lambda_per_yr, fano_factor, magnitude_metric = "3s_gust_ms", severity_distribution, physical_bound_L_ms,
   tiv, footprint}` — the **exact keys the shared engine reads** (a wind-shaped version of hail's
   `frequency_process_params` + severity), or M4 KeyErrors.
4. **Frequency process** — strong wind: occurrence ~ **Poisson(λ)** read from the RP surface, `fano = 1`
   (structural — the RP analysis pre-integrated the dispersion, *no count series to test*; the wildfire pattern).
   Tornado: `λ_collection` **fit** from the bias-corrected SPC count (NegBin allowed if the count is
   over-dispersed; **Poisson is a NegBin special case → engine unchanged**), then `λ_asset = λ_collection · p_hit`
   in [M2](m2_coupling.md). **Stationary** in V1; `λ(t)` for the documented eastward climate shift deferred
   ([AWN-19](assumptions.md)). → realizes **DD-WN-3** (strong wind) + **DD-WN-5** (tornado).
5. **Magnitude metric & severity** — **3-second peak gust (m/s)** above the meteorological threshold μ, with a
   **distinct tail shape per sub-peril** (both capped at the physical bound L; [00_hazard_definition](00_hazard_definition.md)):
   - **strong wind** — μ = **58 mph ≈ 25.92 m/s** (NWS severe); severity is **Gumbel / exponential, ξ ≈ 0**
     (the ASCE return-level curve is log-linear, R²≈0.999), **capped at L** — *not* a bounded GPD with ξ<0.
   - **tornado** — μ = **EF0 ≈ 29 m/s**; severity is a **bounded GPD, ξ < 0** (it reaches the EF5 ceiling L),
     truncated at **L ≈ 113 m/s (EF5 ceiling)**.

   This is **EVT-on-intensity** ([hazard_math/05](../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md)),
   the M3 input. **Continuous severity** — *unlike* wildfire's 6 discrete FLP classes — so convective wind cashes in
   the continuous-severity thread. → realizes **DD-WN-8**.

---

## Strong wind — profile-assembly from the ASCE RP surface (the wildfire-analog)

The **ASCE 7-22 design-wind map is a pre-integrated return-period 3-s-gust surface** — ASCE/NIST already did the
probabilistic tail analysis, exactly as FSim pre-integrated ≥20,000 fire seasons into BP+FLP
([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)). So M1 for strong wind is
**profile-assembly, not event-extraction**:

- **The RP→gust curve *is* the EVT return-level curve.** Each MRI map (RC I 300-yr … RC IV 3,000-yr; Appendix F to
  ~10⁶-yr) is one point on the per-site exceedance curve. Reading several MRIs = sampling the return-level curve at
  fixed exceedance probabilities — ASCE did the tail extrapolation for us. The strong-wind curve is **log-linear in
  return period (R²≈0.999), i.e. a Gumbel / light-exponential tail, ξ ≈ 0, capped at L** — *not* a bounded GPD with
  ξ<0 (that shape is tornado's). **No fit, no rate estimation.**
- **λ from the curve.** The annual rate of *severe* wind (gust ≥ μ = 58 mph) at the site is read from the
  low-MRI / high-frequency end of the curve (or anchored to the bias-corrected SPC convective-wind count as a
  cross-check); the high-MRI end gives the tail that drives PML.
- **Honest borrow ([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) caveat).**
  Pre-integration is *a borrow, not a free lunch* — we inherit ASCE/NIST's assumptions, vintage, terrain-exposure
  (C reference; B/D adjust), and RP convention, and **we can't re-test them**. The uncertainty moved upstream, it
  did not vanish — label it. Flag the EVT-vs-empirical RP convention (the hurricane reference's Weibull-vs-EVD
  caution) since the chosen convention drives the PML/VaR tail.
- **Alternative path (the extraction branch of [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)):**
  fit a catalog directly — **Poisson occurrence + Gumbel/exponential (ξ≈0) gust severity to the bias-corrected
  SPC/Storm-Events record**. Carry as a cross-check / fallback; the ASCE surface is primary (fastest path to a real number).

→ **DD-WN-3: strong-wind frequency = Poisson(λ) read from the ASCE RP surface, fano = 1, no fit** (the wildfire
pattern; site-conditioned → no spatial factor).

## Tornado — event-fit from the SPC record (the hail-analog)

Tornado is **areal hit-or-miss** — a regional rate thinned to the asset, with the thinning done in [M2](m2_coupling.md)
(path-aware Minkowski). M1's job is the **regional catalog**:

- **`λ_collection` (bias-corrected).** Fit the regional tornado rate from the SPC SVRGIS record near each site,
  **after the population/detection bias-correction** flagged in M0 (the old repo applied **none** — its cardinal
  data omission; SPC counts are population-biased, weak-event detection increased, F→EF broke in 2007). Window
  chosen to balance record length vs the F→EF discontinuity. NegBin if the corrected count is over-dispersed;
  Poisson otherwise (NegBin special case → engine unchanged).
- **EF / gust severity.** The conditional severity is the **EF-class distribution** (or a bounded GPD on the
  inferred 3-s gust), with EF midpoints F0≈33.5 … F5≈111.8 m/s and a **Dirichlet-Multinomial posterior** that
  blends the site's observed EF mix with the NOAA national prior (prior strength ~10 pseudo-events — a site needs
  ~10 observed tornadoes for local data to outweigh the national climatology). Truncated at **L ≈ 113 m/s**.
  *(Reuse the old repo's tornado F-scale compound model structure — commit `52db8e3`, the one piece it got
  structurally right — not its EAL-anchored magnitude back-solve.)*
- **Path-geometry statistics** for [M2](m2_coupling.md): per-EF-class mean path length × width and mean area (km²)
  — the input to the path-aware thin-rectangle Minkowski coupling. EF-class mean areas (reusable): EF0≈0.5, EF1≈1.5,
  EF2≈3.0, EF3≈6.0, EF4≈12.0, EF5≈20.0 km².
- **Rural-low EF bias.** Both sites are rural → historical EF severity is likely **understated** (ratings capped by
  the strongest damage indicator present, and violent tornadoes under-rated for near-ground vertical velocity).
  Carry as a severity caveat; it pushes the true tail *higher* than the record suggests.

→ **DD-WN-5: tornado frequency = bias-corrected `λ_collection` fit from SPC (NegBin-capable), thinned in M2;
severity = EF-posterior / bounded-GPD on 3-s gust, truncated at L.**

## What M1 builds (both sites, both sub-perils)

- **λ per sub-peril per asset** — strong wind from the ASCE RP surface (read, not fit); tornado as a bias-corrected
  `λ_collection` (the asset-level thinning is M2's job). Expect Traverse ≫ Shepherds Flat on both (OK tornado-alley
  + derecho vs the near-zero Gorge baseline).
- **Conditional severity distribution** per sub-peril — the tail shape differs by sub-peril:
  - **tornado** — a **bounded GPD on 3-s gust** (μ-anchored, L-truncated) with the analytic parameter solve
    (ξ < 0 → finite upper endpoint): `ξ = (μ_mean − μ)/(μ_mean − L)`, `σ = −ξ(L − μ)`,
    `scipy.stats.genpareto(c=ξ, loc=μ, scale=σ)` on `[μ, L]`.
  - **strong wind** — a **Gumbel / exponential tail (ξ ≈ 0)** on 3-s gust (the log-linear ASCE return-level curve),
    capped at L — *not* the bounded GPD.

  In both cases **fit the severity to the observed gust record / RP curve — *not* back-solved from a target EAL**
  (the old repo's `mag_sim` weakness we explicitly reject).
- **Manifest** per sub-peril with the engine-contract keys (`frequency_process_params {lambda_per_yr, fano_factor}`,
  `magnitude_metric = "3s_gust_ms"`, `severity_distribution` — **tornado** `{family: "bounded_gpd", mu, L, xi (<0), sigma}`,
  **strong wind** `{family: "gumbel"/"exponential", mu, L_cap, ξ ≈ 0}` — `physical_bound_L_ms ≈ 113`,
  `sources`, `provenance`, `bias_correction`).

## Doctrine check — to verify against the team's methodology when built

Mirror wildfire's doctrine check (`hazard_asset_loss_distribution_methodology`, `Hazard_Data_Reference`):

- **Site-conditioned → no spatial factor; rate from the site directly.** → strong wind's `λ` from the ASCE RP
  surface (per-site), **not** `λ_collection · p`. ✓ (the wildfire pattern).
- **Areal → rate fit then thinned.** → tornado's `λ_collection · p_hit`, **not** read from a surface. ✓ (the hail
  pattern).
- **EVT on intensity, not on loss** ([hazard_math/05](../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md))
  — fit the EVT tail on the **3-s gust** (one hazard tail feeds many asset curves), with the **shape per sub-peril**:
  **tornado = bounded GPD, ξ < 0** (it reaches the EF5 ceiling L); **strong wind = Gumbel/exponential, ξ ≈ 0**
  (log-linear ASCE curve), capped at L. Neither is an unbounded fat loss tail — both are bounded by L. ✓
- **Bias-correct SPC before fitting frequency** (Hazard_Data_Ref §7). The old repo did **not**. ✓
- **Never the expected-loss shortcut for *tails*** — λ and severity stay separate, reunited only in M4's sampled
  compound engine. ✓

**Honest caveats the docs surface.** Strong wind's `fano = 1` is **structural** (no count series — ASCE pre-integrated
the dispersion, as with FSim/wildfire). Tornado's frequency is **record-limited and bias-corrected** (the
correction itself is approximate). EF severity is **damage-inferred and rural-low-biased**. The ASCE RP convention
(EVD vs empirical) drives the tail — flag which is adopted.

## Inputs → outputs

M0 parquets (`*_wind_m0_asce.parquet` + `*_wind_m0_spc.parquet` + `*_wind_m0_geometry.parquet`) →
`data/convective_wind/<asset>_wind_m1_catalog_strongwind.parquet` + `…_tornado.parquet` (per-sub-peril λ + per-sub-peril gust
severity — strong wind Gumbel/exponential ξ≈0, tornado bounded GPD ξ<0) + `…_wind_m1_manifest.json` (the typed
contract M2/M4 read), both sites.

## Assumptions (this layer — to register when built)

[AWN-15](assumptions.md) (strong-wind λ from ASCE RP surface, no fit, fano=1 — structural) · [AWN-1](assumptions.md) (tornado
`λ_collection` fit from **bias-corrected** SPC; the old repo's no-correction is rejected) · [AWN-17/18](assumptions.md) (severity
= **per-sub-peril shape**: tornado = **bounded GPD on 3-s gust, ξ<0**, μ-anchored, **L≈113 m/s** truncated; strong
wind = **Gumbel/exponential, ξ≈0**, capped at L — the log-linear ASCE curve; fit to record **not** EAL-back-solved) ·
[AWN-17](assumptions.md) (continuous severity — convective wind cashes in the continuous thread vs wildfire's discrete FLP) · [AWN-19](assumptions.md) (stationary; `λ(t)`
eastward-shift deferred) · [AWN-1](assumptions.md) (EF damage-inferred, rural-low-biased — tail likely understated) ·
[AWN-28](assumptions.md) (tornado ⊥ strong wind — **disjoint, independent** event streams: disjoint by data product,
the ASCE basic-wind surface is non-tornadic by construction and tornado = the SPC Tornado record — a
classification/data-product assumption, not a physical law).

## Open questions (resolve as we build)

- Confirm **DD-WN-3/5/8** as realized at M1 (the two frequency routes + the per-sub-peril severity shapes —
  tornado bounded GPD ξ<0, strong wind Gumbel/exponential ξ≈0).
- **L for tornado — settled for V1: `L = 113 m/s` (EF5 ceiling, damage-inferred), with a revisit note.** This
  supersedes the old repo's tornado `L = 145 m/s` (observed Doppler max); note 113 appeared in the old repo as the
  *Strong-Wind* limit, not tornado. Document the chosen L and why ([00_hazard_definition](00_hazard_definition.md));
  revisit if turbine-relevant Doppler maxima warrant a higher ceiling. *(Not an open status — chosen.)*
- **Bias-correction approach** — pin the exact population/detection correction (decided in M0's audit, applied here).
- **NegBin vs Poisson for tornado** — test the corrected count for over-dispersion; default Poisson, NegBin if
  warranted (engine handles both).
- **Strong-wind λ source** — ASCE-derived vs SPC-anchored; confirm which sets the rate and which is the cross-check.

## How M1 runs / next

Same rhythm as M0: build `m1_catalog/01_catalog` for both sites and **both sub-perils** — strong wind (read the
ASCE RP curve, assemble the profile, fit the **Gumbel/exponential ξ≈0** tail to the log-linear curve/record) then
tornado (bias-correct `λ`, EF-posterior / **bounded-GPD ξ<0** severity, path stats), the manifest, and a
known-answer verification of the engine-contract keys (λ, fano, **per-sub-peril severity shape** — tornado ξ<0,
strong wind ξ≈0, severity support `[μ, L]`, severity integrates to 1). **The notebook opens with the structural-fork
explanation** (site-conditioned vs areal; why strong wind reads a pre-integrated surface while tornado fits a
record), per the exploratory-notebook principle — *the interpretation is the deliverable*, and it's a
[learning_logs](../../learning_logs/README.md) candidate once built. **Next → M2 (coupling):** thin the tornado
`λ_collection` to the asset via the **path-aware Minkowski** (thin-rectangle), and confirm strong wind's
**site-conditioned p_hit ≈ 1** (no thinning) — emitting the coupled handoff M3/M4 consume.
