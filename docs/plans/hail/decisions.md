# Hail pipeline — decisions log

Running record of the non-obvious design decisions for the hail → solar build, ADR-style
(context → options → decision → why → revisit trigger). Newest on top.

---

## DD-4 · Frame consistency — all tail metrics read off the same per-year AEP/OEP vectors

**Date:** 2026-06-09 · **Status:** decided · Confirmed by the math-validation pass (risk-metrics audit).

**Context.** The old repo's single worst error was a **frame mismatch** — comparing an OEP (per-occurrence)
number against an AEP (annual-aggregate) number (the impossible ~175× invariant violation). The
`risk_metrics_reference` calls this *the* most common structural mistake.

**Decision.** Every tail metric is read off the **same per-simulated-year vectors** built in one M4 pass:
`AEP_year` (annual total) and `OEP_year` (annual max single event). `VaR_q ≡ AEP-PML_T` (aggregate frame);
`OEP-PML_T` is its own occurrence-frame curve; **the two are never mixed in one comparison.** PML at return
period *T* = the **(1 − 1/T) percentile** of the matching vector (1-in-100 = 99th, 1-in-250 = 99.6th).

**Why.** The validation audit confirmed our labels and definitions match the reference and the frame is
internally consistent — recording it as a decision **pins the invariant** so it can't silently re-drift. The
old repo's worst failure, structurally foreclosed.

**Revisit trigger.** Any new metric or financial-terms layer must declare its frame (AEP vs OEP) and read off
the matching vector.

---

## DD-3 · Frequency & catalog sources — **by component** (`p` ← MRMS; `λ`: MRMS-widen now → NOAA-calibrated extension later)

**Date:** 2026-06-09 · **Status:** decided (Stage 1 now; Stage 2 = path to ideal) · Generalized in [`learning_logs/04`](../../learning_logs/04_two_datasets_one_peril_decompose.md); evolves [DD-1](#dd-1--m1-catalog-source-strategy--mrms-only-for-v1-why-not-a-naive-noaamrms-temporal-splice).

**Context.** `λ_asset = λ_collection × p`. The two pieces have *different* data needs, so "which dataset is
primary?" is the wrong question — the right one is **which *component* comes from which source**. DD-1
committed **MRMS-only for v1** (homogeneous, but short); we now need a longer/better `λ`, which forces this.

**The decomposition.**
- **`p` (spatial factor)** needs event **footprints** (area `F`). NOAA is points — *physically cannot* supply
  it. → **MRMS, always.**
- **`λ_collection` (regional rate)** trades **length** (NOAA, 1996→ ~30 yr) against **homogeneity** (MRMS,
  ~2020-10→ ~5.7 yr; spatially complete). NOAA's long record is **population-biased + drift** — raw NOAA
  counts give a long record of the *wrong* rate.

**Decision.**
1. **`p` ← MRMS**, unconditionally.
2. **`λ_collection`, Stage 1 (now — "decent"):** widen the MRMS scan to its **full ~5.7-yr record** → a
   homogeneous, unbiased (if short) `λ`. No splice, no bias headaches; MRMS stays the clean spine.
3. **`λ_collection`, Stage 2 (later — "ideal"):** **NOAA-calibrated extension** ([`learning_logs/01`](../../learning_logs/01_extending_a_short_hazard_record.md)
   Method A) — use NOAA's *length*, bias-corrected against MRMS in the overlap. NOAA **extends the rate,
   calibrated**; it does not contribute raw counts.

**Framing.** **MRMS owns the physics** — events, footprints, `p`, *and the calibration truth*; **NOAA's job
is to extend the rate, calibrated.** So it is *not* "NOAA primary raw" (that would import its bias); MRMS
remains the anchor. This is exactly DD-1's named revisit-trigger, now acted on, by component.

**Why.** `p` physically requires footprints (MRMS-only). For `λ`, **homogeneity beats naive length** (raw
NOAA is biased → wrong rate); MRMS-widen gives a clean decent `λ` immediately, and the calibrated NOAA
extension gives the ideal long `λ` later — *done right*. Consistent event-definition + region throughout
(methodology: don't mix `λ` from one regime and `p` from another).

**Revisit trigger.** Run Stage 2 (calibrated extension) when the **tail** (1-in-250+) needs the longer
record; at ~5.7 yr the NegBin dispersion fit (DD-2) is still underpowered, so Stage 1 `λ` is "decent, not
ideal." Damage-curve calibration (the founder's two reference repos) is a separate track.

---

## DD-2 · Hail frequency process — Negative Binomial **prior**, fit deferred (test dispersion, don't assume)

**Date:** 2026-06-09 · **Status:** decided (v1) · Full reasoning: [`learning_logs/02`](../../learning_logs/02_count_distribution_and_dispersion_prior.md)

**Context.** The M1 manifest must declare a `frequency_process` — the distribution of events-per-year `N`.
This is a **tail decision** (it barely moves EAL but strongly moves VaR/PML), *not* a cosmetic one. Poisson
forces `variance = mean`; SCS/hail counts empirically over-disperse (Fano ≈ 1.5–3) because active seasons
cluster. But our record is too short to *test* dispersion: ~5–6 annual counts (MRMS-on-AWS), and A24 §4.3
flags the test as underpowered below ~10–15 yr.

**Options considered.**

1. **Poisson** — *rejected*: forces var = mean → thin tail → PML understated; the OASIS-inherited default is
   empirically wrong for SCS (A24).
2. **Assume NegBin, no test** — *rejected*: swaps one unchecked assumption for another.
3. **Fit-and-check only** — necessary but *insufficient alone here*: at ~5–6 annual counts the test can't
   distinguish Poisson from mild over-dispersion.
4. **NegBin + a weakly-informative dispersion prior, fit deferred** ← **chosen.**

**Decision (v1).** `frequency_process = negative_binomial` (which *nests* Poisson at zero dispersion). Hold a
weakly-informative prior on the annual-count **Fano factor** `φ`: **median ≈ 2, 90% ≈ [1, 3.5]** (recorded in
the manifest `frequency_process_params.prior`). The **λ and dispersion fit is deferred** until the MRMS record
widens; then **test** (Fano factor, LRT/AIC, Bayesian shrinkage against this prior) and let the data choose.

**Why.** Tail-critical; NegBin contains Poisson, so the fit can collapse to Poisson if warranted (safe);
physics + literature say SCS over-disperses; and at small n the prior must carry it — an over-dispersed prior
is the conservative direction for PML.

**Revisit trigger.** When the record reaches enough annual counts (~10–15+ yr) to power the dispersion test,
run the fit; the posterior may move toward Poisson or higher dispersion — refine the prior per-region. (Note:
a *trend/regime* is a different fix — non-stationary `λ(t)` / regime-switching, A24 — not NegBin.)

---

## DD-1 · M1 catalog source strategy — MRMS-only for v1; why *not* a naive NOAA+MRMS temporal splice

**Date:** 2026-06-09 · **Status:** decided (v1)

**Context.** M1 (the event catalog) wants two things no single source gives us: a *long* frequency record
(for a stable λ) **and** event *footprints* (for the Minkowski coupling). We have:

- **MRMS MESH** — gridded, spatially complete, real footprints — but only **~2016 → present** (short).
- **NOAA Storm Events** — point reports, **1996 → present** (long) — but no footprints, and population-biased.

The natural idea (a common one): **splice by era** — MRMS where it exists (post-2016), NOAA before that.
Best-available-source-per-period.

**Why the naive splice is risky — record inhomogeneity (the crux).** NOAA points and MRMS grid count events
under *different detection regimes*:

- NOAA point reports **under-report** — tied to population, time-of-day, and reporting practices that have
  *changed over time* — and they're points, not footprints.
- MRMS MESH is **spatially complete** — it detects hail regardless of whether anyone reported it.

Splicing a population-biased point record onto a spatially-complete gridded record produces a **spurious
discontinuity in the apparent event rate** at the 2016 boundary: λ appears to *jump* when MRMS begins — an
**artifact of the source change, not a real change in hail**. That is the classic inhomogeneous-catalog
trap. The references warn about the *upstream* half of it — SPC reports are population-biased and
*"reporting practices changed over time"*, so they must be bias-corrected before fitting (founder
`Hazard_Data_Reference`); the framing of a **source/regime seam itself fracturing λ**, and the methods to
fix it, are our derived extension — written up in
[`learning_logs/01 — Extending a short hazard record`](../../learning_logs/01_extending_a_short_hazard_record.md).
Either way, baking a source-change artifact into λ is the same *family* of error the old repo made — a
frequency that looks longer/better but is quietly wrong.
**Homogeneity of the record matters more than its length for a trustworthy λ.**

**Options considered.**

1. **Naive temporal splice** (NOAA pre-2016 + MRMS post-2016) — *rejected for λ*: inhomogeneous → fake rate
   discontinuity at the boundary.
2. **MRMS-only, homogeneous, short record (~2016 →)** — clean λ over one consistent detection regime; lose
   pre-2016; NOAA used as cross-check. ← **v1 choice.**
3. **Calibrated splice** — use the **MRMS ↔ NOAA overlap** (2016 →) to *learn* NOAA's undercount factor,
   bias-correct NOAA's pre-2016 counts to the MRMS detection standard, *then* extend the record. Sound
   homogenization; meaningful work. ← v2 candidate.
4. **Gridded-to-gridded extension** — splice MRMS with a longer *gridded* radar reanalysis (**MYRORSS**
   ~1998 →, or **GridRad-Severe**). Both radar-derived → far more homogeneous than gridded+points. The
   architecture's named V2 path (A20 §9 Q1). ← **best long-record option (v2).**
5. **Role-split** — MRMS footprints always; λ from a homogenized long record; pre-MRMS events borrow a
   *typical* footprint drawn from MRMS-era statistics.

**Decision (v1).** **MRMS-only** event catalog (homogeneous, ~2016 → present); `frequency_process =`
**Negative Binomial** (SCS/hail counts are over-dispersed — not Poisson). **NOAA = cross-check / calibration
overlay**: does MRMS catch the reported hail days? bias-correct the MESH→ground size mapping; record the
outcome in each event's `confidence_flags`. Accept the short record and **document pre-2016 blindness**.

**Why.** Homogeneity > length for a trustworthy v1 λ; avoids the source-change artifact; simplest coherent
build; footprints come native from the grid. Matches the architecture's stated V1 target — A20 §9 Q1:
*"V1 can run on MRMS-only with explicit pre-2010s blindness; V2 needs the spliced backbone."*

**Revisit trigger.** When we need a longer record for **rarer return periods** (e.g. 1-in-250+, where ~9 yrs
of MRMS is too thin to estimate the tail), upgrade to the **calibrated splice (opt 3)** or the **gridded
MYRORSS / GridRad extension (opt 4)** — *never* the naive splice (opt 1). Both methods are worked out in
detail (datasets, recipe, worked examples, caveats) in
[`learning_logs/01`](../../learning_logs/01_extending_a_short_hazard_record.md).
