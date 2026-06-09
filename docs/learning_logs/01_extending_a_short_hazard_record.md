# Extending a Short Hazard Record — The Inhomogeneity Trap, and Two Ways to Do It Right

*Why you can't just bolt a longer record onto a shorter one to get a better frequency — and the two methods
that actually work when you need the length.*

**Status:** v1.0 · written 2026-06-09 · **Sourced from:** hail × solar, Phase 1 / [DD-1](../plans/hail/decisions.md) (M1 catalog source strategy) · **Applies to:** any peril fitting an event-rate **λ** from a short or multi-source record (flood, wind, wildfire next).

---

## Where this came from

Choosing the hail M1 catalog source (**[DD-1](../plans/hail/decisions.md)**, 2026-06-09). The two candidate
records pull in opposite directions:

- **MRMS MESH** — gridded, spatially complete, *real footprints* — but a **short** record (clean
  ~2014/2016 → present; partial to ~2010/2012).
- **NOAA Storm Events** — **long** (1996 → present) — but *point reports*, no footprints, population-biased.

The tempting move, and the one that prompted this entry: *"use MRMS where it exists, NOAA before that"* — a
best-available-source-per-era splice, to get both length and footprints. That instinct is standard, and the
goal (a long, stable λ) is right. The trap is in the splice.

## Why it looked fine — the trap

A longer record obviously gives a more stable rate estimate — **if the detection regime is constant**. It
isn't. NOAA points and MRMS grid count events under *different* detection regimes:

- NOAA point reports **under-report** — they need a human present to see and call in hail. Counts track
  population, roads, and time-of-day, and the *reporting practice itself drifted upward* over time (NEXRAD
  buildout, spotter networks, phones, social media).
- MRMS MESH is **spatially complete** — it detects hail whether or not anyone was there.

Splice a population-biased point record onto a spatially-complete gridded one and λ appears to **jump** at
the boundary — a spurious rate discontinuity that is an *artifact of the source change, not a change in
hail*. Fit a frequency to that series and you read the reporting/sensing transition as a hazard signal.

## The lesson

> **The lesson.** Homogeneity of the record beats its length for a trustworthy λ. A longer record built by
> abutting two different detection regimes fabricates a rate discontinuity at the seam — so to *extend* a
> short record you must **harmonize** (calibrate or recompute to one regime), never naively splice.

`[REF]` The references already establish the surrounding commitments: hail V1 is **MRMS-only with explicit
pre-2010 blindness** (H10 §2.1); the count process is **Negative Binomial**, not Poisson, because SCS counts
are over-dispersed (A24 §4.5, §4.2; A20 §6.4); the MRMS / MYRORSS splice is a **named-but-unsolved V2
question** — A20 calls the harmonization *"non-trivial"* and *"the central technical decision for hail"* but
gives no method (A20 §9 Q1, H10 §6); and SPC reports must be **bias-corrected before fitting** because they
are population-biased and *"reporting practices changed over time"* (founder `Hazard_Data_Reference`).

`[OURS]` What the references do **not** contain — and what this entry adds — is (1) the framing that a
**source/regime change inflates or fractures λ** (the refs cover SPC *population* bias and reporting-practice
drift, and A24's caveat that the over-dispersion test is underpowered at ~16-yr n, but not the
source-seam-as-λ-artifact failure mode), and (2) the two concrete **harmonization methods** below that close
the gap A20 §9 Q1 flags. These are ours, derived to answer a question the references raised but left open.

## Two ways to do it right

Both replace "abut two regimes" with "reconcile to one." Method A keeps the point reports and *corrects*
them; Method B avoids points entirely and *extends the grid*. **For length, B is cleaner** (gridded ↔ gridded
is far more homogeneous than gridded ↔ points); A is the fallback when an older grid isn't available.

### Method A — Calibrated splice (point reports ↔ gridded radar) `[OURS]`

Learn the report-to-radar relationship in the overlap where the grid is trustworthy, invert it into an
undercount correction, apply that to the report-only era, *then* splice.

**The biases you're correcting** (all well-documented for SPC hail reports):

- **Population / road bias** — the undercount factor is **~5–6× even in populated areas, and far larger
  (10–30×+) in rural zones** (Wendt & Jirak 2021, MESH-vs-Storm-Data). It is a *spatial field*, not a scalar.
- **Diurnal bias** — nocturnal hail is systematically missed.
- **Secular reporting trend** — raw counts rise from observers/technology, not hazard (Tang et al. 2019;
  Allen & Tippett 2015 recommend post-2000 data).
- **Point-vs-area** — a report is one point a person stood on; a hail swath is ~3–10 km wide. Report count
  conflates footprint with exposure density. MESH gives the footprint directly.
- **Threshold break at 2010** — "severe" was **0.75 in before 5 Jan 2010, 1.00 in after**. Pre-2010 reports
  must be re-filtered to ≥ 1 in or the series steps at 2010 for non-hazard reasons.

**And MESH's own biases** (the calibration target is not ground truth): MESH was tuned to **overforecast** —
~75% of observed hail falls *below* the estimate (Witt et al. 1998, fit on only 147 reports; Murillo &
Homeyer 2019 refit MESH75/MESH95 on ~6,000). **MESH ≥ 29 mm** is the standard severe threshold (Cintineo et
al. 2012); false-alarm ratio is **~30–50%**. So deflate raw MESH by ~(1 − FAR) before trusting it.

**The recipe (per ~80-km cell or county, per season):**

1. **Overlap truth grid** — MESH severe-hail-*day* rate, QC'd (NLDN lightning mask, drop < 29 mm, cap
   > 127 mm), deflated by (1 − FAR).
2. **Overlap report rate** — same cells/threshold era.
3. **Undercount model — fit detection *probability*, not a constant ratio.** A Beta-binomial / logistic GLM:
   `logit p(cell,season) = f(log pop-density, log road-density, night, MESH-intensity, region, season)`, with
   undercount `U = 1/p`. The GLM matters because it lets you **extrapolate `U` to the past using covariates
   you also have historically** (decadal census population, roads), instead of freezing one number.
4. **Apply with *time-varying* covariates** to 1996–2016 reports — *this is what removes the spurious
   reporting trend* (more past-era undercount → larger past-era `U`), rather than re-importing it.
5. **Harmonize the 2010 threshold**, then **splice** the corrected report rate with the radar rate by
   inverse-variance weighting.
6. **Separate severity from frequency** — model conditional hail-*size* from MESH percentiles + an EVT tail
   (GPD/GEV) independently of λ.
7. **Propagate uncertainty** (GLM posterior on `U`, MESH threshold sweep 25–35 mm, Witt-vs-Murillo
   calibration, FAR 20–45%) and **always report λ as a band bracketed by pure-report (low) and pure-MESH
   (high)** — Wendt & Jirak: *"the true risk likely resides in between."* If your estimate leaves that
   bracket, debug before shipping.

> **Worked example (rural High Plains 80-km cell).** Overlap (10 yr): MESH severe-days = 7.0/yr; deflate by
> FAR 30% → radar-truth ≈ 4.9/yr. Storm-Data severe-days = 1.2/yr → `U_overlap ≈ 4.1×`. The GLM at
> 1996–2005 population (sparser observers) returns `U ≈ 6.5×`. Observed reports 1996–2005 = 0.7/yr →
> **corrected ≈ 4.6/yr**, vs the naive 0.7. The naive series would have shown a fake near-tripling
> (0.7 → 1.9/yr) over the record — pure reporting growth. Homogenized, it's flat at ~4.5–4.9/yr.
> 90% band ≈ **λ = 4.6 (3.0–6.5)**, sitting inside the [0.7 report, 7.0 MESH] bracket as expected for a
> low-population cell. The correction magnitude *and its uncertainty are themselves spatial fields.*

### Method B — Gridded-to-gridded extension (the cleaner long record) `[OURS]`

Don't splice grid onto points at all — extend the grid backward with an *older gridded radar product*, then
standardize one hail definition end-to-end. This is the path A20 §9 Q1 names ("MRMS + MYRORSS") but doesn't
specify.

**The datasets:**

| Product | Coverage | Res. | MESH? | Lineage vs MRMS | Access |
|---|---|---|---|---|---|
| **MYRORSS** | **1998–2011** | 0.01°, ~5-min | **Yes** (hail-size product) | **Same** WDSS-II/MRMS code family — closest splice | AWS Open Data `s3://noaa-oar-myrorss-pds`, no-sign-request |
| **GridRad / GridRad-Severe** | 1995–2017 / 2010–2021 | 0.02°, hourly / 5-min | **Compute it** (from reflectivity + reanalysis melt level) | *Independent* academic merge; Murillo-Homeyer MESH refit | NCAR RDA `ds841.0` |
| **Operational MRMS** | ~2014/2016 → present | ~0.01°, 2-min | Yes | — | AWS `s3://noaa-mrms-pds` |

**Recommended build:** MYRORSS (1998–2011, MRMS lineage) → GridRad bridge across the 2012–2013 seam →
operational MRMS (present). Then:

1. **One hail definition end-to-end** — recompute MESH from gridded reflectivity with a *single* single-pol
   SHI→MESH law (Witt to match MRMS/MYRORSS), applied to *all* segments including the modern one (mask out
   dual-pol enhancements). Don't let each source use its native MESH — that bakes in an algorithm step.
2. **One melt-level source** (e.g. ERA5) across all segments — not RUC-then-RAP.
3. **Common grid + daily-max MESH** to neutralize resolution/cadence differences.
4. **Quantile-match at overlaps** (MYRORSS↔GridRad 2008–2011, GridRad↔MRMS 2014–2017) — reconcile, don't
   merely abut.
5. **Model the radar-network step changes as known breakpoints** (see caveats) and carry a per-cell-per-year
   `n_radars` confidence weight.

> **The catch B does *not* escape.** A gridded splice removes the *point-report* bias, but **all** these
> products ride the same WSR-88D network, so they share three hard steps that survive: sparse coverage
> **pre-2000**, the **2008 super-resolution** upgrade, and the **2011–2013 dual-pol** rollout. The
> inhomogeneity moves from "points vs grid" to "the radar network itself" — quieter, but still there. Hence
> the breakpoint flags, the single-pol standardization, and treating pre-2006 as lower-confidence.

## Which, and when

| | Use when | v1 status |
|---|---|---|
| **Neither — MRMS-only** | the short homogeneous record covers your return periods | **chosen** ([DD-1](../plans/hail/decisions.md)) |
| **Method A** (calibrated splice) | you need length and only have points + a modern grid | V2 |
| **Method B** (gridded extension) | you need length *and* can get MYRORSS/GridRad — **preferred** | V2 |

**Revisit trigger:** when we need a longer record for **rare return periods** (1-in-250+, where ~9–16 yr of
MRMS is too thin for the tail). Until then, MRMS-only + NOAA-as-cross-check stands, with pre-2010 blindness
documented.

## How to recognize the trap next time

The early signal is a **step-change in apparent event rate that lines up exactly with a data-source onset
date** (a sensor going live, a network upgrade, a reporting-policy change). Before extending *any* record —
flood gauges, wind, wildfire perimeters — ask: **do the two eras count events under the same detection
regime?** If not, calibrate the overlap first (Method A), or recompute both eras to one regime (Method B), or
stay homogeneous and document the blindness. Never just abut.

## Caveats and limits

- **Bias is non-stationary *within* the long record** — a single overlap-derived correction, applied flat to
  the past, is itself biased (the past had fewer observers / fewer radars). This is why Method A must model
  `U` on time-varying covariates, and Method B must flag radar-era breakpoints.
- **The correction is a spatial field**, least constrained exactly where it matters most (rural, low-data).
- **MESH is a proxy, over-forecast by design, with 30–50% FAR and range/beam-height degradation** — and so
  are reports. Neither side is truth; report a band, not a point.
- **Frequency ≠ severity.** These methods homogenize the *rate* λ. The hail-*size* tail (≥ 2 in, which drives
  loss) is separately biased and must be modeled separately (MESH percentiles + EVT).
- **Literature magnitudes need reproduction on our own overlap** — the ~5–6×/10–30× undercount, 29 mm
  threshold, and 1998/1995 dataset spans are well-corroborated but region/grid/threshold-specific.
- **Citation/symlink caveat** — the `[REF]` paths below resolve via the gitignored, machine-local
  `infrasure-hazard-competitive-research` symlink; teammates without it should use the stable doc-IDs
  (A20 §9 Q1, etc.). `.docx` founder docs are cited by name + section, not as clickable links.

## Cross-references

- **Decision this generalizes:** [`../plans/hail/decisions.md`](../plans/hail/decisions.md) § DD-1.
- **Principle it serves:** [`basics_spot_on.md`](../principles/basics_spot_on.md) — a frequency seeded by a
  source-change artifact is a basics failure, the same *family* as the old repo's.
- `[REF]` **A20 §3.3, §3.8, §6.4, §9 Q1** — catalog seam, hail backbone, `frequency_process` field, the
  splice open-question: [`A20_m0_m1_hazard_catalog.md`](../../infrasure-hazard-competitive-research/learnings/architecture/A20_m0_m1_hazard_catalog.md).
- `[REF]` **A24 §4.2, §4.3, §4.5, OQ-A24-1** — NegBin default, small-n caveat:
  [`A24_distribution_choices.md`](../../infrasure-hazard-competitive-research/learnings/architecture/A24_distribution_choices.md).
- `[REF]` **H10 §2.1, §6** — MRMS-only V1, MYRORSS splice deferred:
  [`H10_m0_m1_catalog.md`](../../infrasure-hazard-competitive-research/learnings/architecture/perils/hail/H10_m0_m1_catalog.md).
- `[REF]` **founder `Hazard_Data_Reference` / `hazard_asset_loss_distribution_methodology`** (report bias;
  no public hail catalog; test-dispersion→NegBin): [`../google_drive_docs/README.md`](../google_drive_docs/README.md).
- **Key literature:** Wendt & Jirak 2021 (MESH-vs-Storm-Data undercount); Cintineo et al. 2012 (MESH ≥ 29 mm);
  Witt et al. 1998 / Murillo & Homeyer 2019 (SHI→MESH); Allen & Tippett 2015, Tang et al. 2019 (report
  trends); Murillo, Homeyer & Allen 2021 (23-yr GridRad MESH); MYRORSS (Ortega et al. 2022, BAMS).
