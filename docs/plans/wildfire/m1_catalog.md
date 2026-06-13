# M1 — Catalog → Per-Asset Hazard Profile (the active plan)

*M0 met the raw hazard; **M1 turns it into the clean, typed handoff the loss engine consumes** — per asset, a
**frequency (λ)** + a **conditional severity distribution**, with a manifest declaring the catalog's choices.
Mirrors hail M1 — but wildfire's site-conditioned nature changes the *shape*, which we pin down first.*

**Where this sits:** [M0 evidence](m0_input_data.md) → **M1 (catalog)** → M2 coupling → M3 damage → M4 loss &
metrics. Built for **both assets** (Hayhurst baseline + Matrix proving). Notebook:
`Notebooks/wildfire/m1_catalog/01_catalog`.

---

## The structural twist — why wildfire M1 ≠ hail M1 (read this first)

Hail M1 *extracted discrete events* (hail-day footprint polygons) from raw radar and *fit* a regional rate
`λ_collection` from a short record (NegBin + dispersion). **Wildfire is different on every count, because FSim
already did the event simulation** (≥20,000 seasons) and pre-integrated it into per-pixel **BP + FLP**:

| | Hail (areal hit-or-miss) | **Wildfire (site-conditioned)** |
|---|---|---|
| Events | extract discrete hail-day footprints from MRMS | **FSim pre-integrated → BP + FLP per pixel** — *no event extraction* |
| Frequency | **fit** `λ_collection` from a short record (NegBin, dispersion) | **BP *is* the annualized rate** — *no short-record fit, no dispersion problem* |
| Catalog grain | one **regional** event set, shared across assets | **per-asset** hazard profile (the field is site-specific) |
| Severity | conditional-on-hit size distribution | **FLP1-6 histogram** → fire-line intensity (kW/m) |

> **So M1 here is not "build an event catalog from evidence" — it's "assemble the per-asset hazard profile
> (BP→λ, FLP→severity) and declare the process,"** ready for the *same* compound-NegBin engine. This contrast
> (areal builds a shared regional catalog; site-conditioned reads a per-asset profile FSim already integrated)
> is a **learning-log candidate** (09) once built.

---

## The five catalog choices (declared in the manifest, mirroring hail)

1. **Ontology** — the unit is a **per-asset hazard profile**: `{λ (annual burn rate), FLP1-6 conditional
   flame-length histogram}` over the asset footprint. *(A20's fire-perimeter polygon is the conceptual event
   identity; V1 uses FSim's pre-integrated BP+FLP, **not** a discrete perimeter event set — a documented V1
   simplification, revisit if a discrete-perimeter use-case arises.)*
2. **Backbone / spine** — **FSim FLP1-6 + BP** (`RDS-2016-0034-3`, 270 m) from M0 candidate 02; **WRC 30 m** as
   the cross-check ([DD-W4](decisions.md)).
3. **Interface object** — the typed M1→M2/M4 handoff, per asset:
   `{lambda_per_yr, fano_factor, severity_kwm_distribution, tiv, footprint}` — the **exact keys the shared
   engine reads** (a wildfire-shaped version of hail's `frequency_process_params`), or M4 KeyErrors.
4. **Frequency process** — annual occurrence ~ **Bernoulli(BP) ≈ Poisson(λ)**, `λ = −ln(1−BP) ≈ BP` at these
   small BPs; expressed as the engine's count stream (**Bernoulli/Poisson is a NegBin special case** → engine
   unchanged). **No short-record fit** (FSim pre-integrated the seasons); **fano ≈ 1** (single-site, no
   clustering modeled in V1); **stationary** (λ(t) deferred — [AW-13](assumptions.md)). → propose **DD-W7**.
5. **Magnitude metric** — **fire-line intensity (kW/m)**, via the FLP1-6 histogram → Byram `FL→I` (the FIL
   class table, [data-dictionary §3](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)). The
   conditional severity = the 6 FLP weights on their kW/m class-intensities. This is the M3 input.

---

## What M1 builds (both assets)

- **λ per asset** from BP (`λ = −ln(1−BP)`; ≈ BP here): Hayhurst ≈ **0.0004/yr**, Matrix ≈ **0.045/yr**.
- **Conditional severity distribution** per asset: the FLP1-6 weights mapped to **kW/m** (Byram + the FIL
  class table) — the discrete severity the engine samples in a "fire" year. (Keep the histogram; the engine
  samples a class, M3 maps class → damage.)
- **The one-time edge-rule sensitivity check ([AW-21](assumptions.md)):** footprint mean under **center-in vs
  all-touched vs area-weighted** for both assets → tabulate the delta, confirm it's a minor lever, document.
- **Manifest** per asset with the engine-contract keys (`frequency_process_params {lambda_per_yr,
  fano_factor}`, `magnitude_metric`, `severity_kwm_distribution`, `sources` = FSim spine + WRC cross-check,
  `provenance`, `spatial_resolution_m = 270`).

## Frequency decision (propose DD-W7)

**`frequency_process = poisson` with `λ = −ln(1−BP)` per asset** (Bernoulli-per-year is the BP-native form;
Poisson is its rare-event limit and a NegBin special case, so the **shared compound-NegBin engine is
untouched**). `fano = 1` (V1, single-site). **Rationale:** unlike hail, BP comes pre-integrated from FSim's
many-season Monte Carlo, so there is *no short record to fit* and *no over-dispersion to estimate* at the
single-site level — the dispersion already lives inside FSim's BP. **Revisit:** multi-fire-year clustering or
a portfolio (correlated BP across nearby assets) would reintroduce a dispersion/correlation term; `λ(t)` for
climate trend ([AW-13](assumptions.md)).

## Doctrine check — verified against the team's methodology (2026-06-13)

Read the source-of-truth docs (`hazard_asset_loss_distribution_methodology`, `Hazard_Data_Reference`): our
wildfire M1 is **consistent with doctrine, and several choices are explicitly backed** —

- **Site-conditioned → no spatial factor; rate from the site directly.** Methodology §4–5: *"for
  field-intensity and site-conditioned perils there is no 'miss', so λ_collection × spatial_factor does not
  apply; the relevant-event rate comes from the site intensity process directly."* → our `λ = BP` (per-site),
  **not** hail's `λ_collection·p`. ✓
- **The structural twist is doctrine, not just our observation.** Hazard-Data-Ref (wildfire): *"no track→swath
  step — the simulator outputs the footprint statistics directly."* FSim pre-integrates the event set into
  BP+FLP. ✓
- **BP = frequency (annualized), FLP/CFL = conditional severity; combine via BP × severity.** Hazard-Data-Ref:
  *"BP is annualized, CFL is conditional … multiplying raw CFL by exposure without BP overstates risk."* →
  our frame rule ([AW-4](assumptions.md)). ✓
- **Don't mix WRC v2 (WildEST) with FSim FLP.** Hazard-Data-Ref: *"switched the intensity layer from raw FSim
  FLPs to WildEST … don't mix v1 and v2 numbers … related-but-different engines."* → [DD-W4](decisions.md) +
  [learning_logs/07](../../learning_logs/07_one_simulation_two_products.md). ✓
- **270 m is screening-grade.** Hazard-Data-Ref: *"270 m … fine for portfolio screening, too coarse for
  single-substation siting (90 m local runs needed)."* → our resolution caveat (Hayhurst = 8 px). ✓
- **Never the expected-loss shortcut for *tails*.** Methodology §1/§13: build from sampled losses. The legacy's
  `EAL = BP·E[damage]·TIV` is the correct **mean** (the methodology even uses it as the *EAL sanity check*) —
  the error was fitting the **tail** to those expected-loss points. Our sampled compound-MC (M4) is the fix. ✓

**Refinement to DD-W7 (methodology §9).** The site-conditioned engine is framed as *"each simulated year draws
a site intensity and maps it through the response curve"* — **no separate Poisson hit-count**. For wildfire
that annual draw is a **mixture**: with prob BP, a flame length from the FLP histogram; else nothing — i.e.
**occurrence(BP) → conditional FLP severity**, identical to Poisson(BP) at small BP. So frame `λ` as the
**per-site annual burn rate (BP)**, *not* areal thinning, and feed the BP×FLP mixture to the shared engine.

**Honest caveat the docs surface.** Unlike hail, we **cannot empirically test count over-dispersion** — FSim
pre-integrated the seasons into a single BP, so there's no annual-count time series to test (the dispersion
lives *inside* FSim). So `fano = 1` is a **structural** choice, not a measured one. (We also rely on USFS's
FSim calibration vs MTBS/FPA-FOD; and FSim under-captures ember/WUI spread — relevant only if we add the ember
sub-peril.)

## Inputs → outputs

M0 parquets (`*_wildfire_m0_fsim.parquet` + `*_wildfire_m0_wrc.parquet`) →
`data/wildfire/<asset>_wildfire_m1_catalog.parquet` (per-asset λ + kW/m severity distribution) +
`…_wildfire_m1_manifest.json` (the typed contract M2/M4 read).

## Assumptions (this layer — to register when built)

[AW-21](assumptions.md) (edge rule, + the sensitivity check happens here) · **new:** `λ = −ln(1−BP)` from FSim
BP, no short-record fit · single-site `fano ≈ 1` (no multi-fire-year clustering) · severity = the **discrete
6-class FLP histogram** on kW/m (not a continuous tail — EVT-style tail deferred) · [AW-13](assumptions.md)
(stationarity).

## Open questions (resolve as we build)

- Confirm **DD-W7** (Poisson/Bernoulli(BP) frequency, fano=1, no fit).
- Confirm the **A20 perimeter-event ontology is deferred** for V1 (FSim BP+FLP profile, not discrete
  perimeters).
- **Severity granularity:** V1 = the 6 discrete FLP classes mapped to kW/m. The within-class intensity and the
  deep tail (FIL6 "12+ ft" is open-ended) are coarse — note as a severity-resolution caveat (EVT/continuous
  deferred).
- **Per-asset vs shared catalog:** wildfire M1 is **per-asset** (site-conditioned), unlike hail's shared
  regional catalog — confirm the folder/output convention (one catalog file per asset under `data/wildfire/`).

## How M1 runs / next

Same rhythm as M0: build `m1_catalog/01_catalog` for both assets (λ from BP, FLP→kW/m severity, the AW-21
sensitivity check, the manifest), interpret every output, verify the engine-contract keys against a
known-answer (`λ`, `fano`, severity sums). **The notebook opens with the structural-twist explanation**
(areal vs site-conditioned; why FSim pre-integrates the event set — doctrine-backed: hazard-data-ref's *"no
track→swath step"*), per the exploratory-notebook principle — *the interpretation is the deliverable*, and
it's a [learning_logs](../../learning_logs/README.md) candidate (09) once built. **Next → M2 (solar coupling):** the site-conditioned step —
susceptibility, the oozing/surrounding-fuel handling ([AW-15](assumptions.md)), emitting the `(p_hit,
conditional intensity)` pair the reused M3/M4 contract needs.
