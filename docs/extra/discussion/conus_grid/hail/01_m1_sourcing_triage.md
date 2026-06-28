# 03 — Hail M0/M1 Sourcing Triage (the "ready field vs build-from-raw" decision)

*A discussion doc — the **decision** distilled from the research. Resolves Q5 from [`01`](../01_ideal_architecture_compute_and_grid.md):
for the hardest hazard (hail), do we **build** the per-cell M1 hazard field from raw radar, or is there a
**ready-made product** (an FSim-equivalent) we can ingest? **Full per-product evidence + sources live in
[`research/hail_m1_data_products.md`](00_m1_data_products_research.md)** — this doc carries only the
distilled triage + recommendation + decisions.*

---

## TL;DR (the bottom line up front)

1. **There is no FSim-equivalent for hail.** No single public product hands us, per 0.25° cell, **both** the
   two things M1 needs: **(1) an annual severe-hail frequency** *and* **(2) a hail-size distribution.** They
   are different statistical objects (an *occurrence rate* vs a *magnitude distribution*), and **nothing was
   built to serve both.** So hail is **not** a Bucket-1 "ready field" like wildfire — but it isn't a
   build-from-nothing job either.
2. **The decisive gap is the SIZE distribution.** *No public product* gives a full per-cell hail-size
   distribution from 1″ up. Frequency climatologies exist (some validated); size products give only the *max*
   or the *extreme tail*. **⇒ the severity half of M1 must be self-built** (from MESH and/or reports),
   whichever frequency source we pick. This is also why the deep-tail [EVT caveat (02 / A23)](../02_per_cell_output_schema.md) is unavoidable, not optional.
3. **Recommended: self-build, but well-anchored** — a three-piece strategy: **MRMS MESH (+MYRORSS to ~double
   the record)** as the gridded source for both (1) and (2); **Murillo & Homeyer 2021** as the
   bias-correction anchor + validation target (directly answers Colby's "MRMS over-predicts"); **NOAA Storm
   Events** as ground-truth. Optionally **Das & Allen 2024** for the size *tail* — *if* its data proves public.
4. **The `01` compute story holds.** The self-build is the ~hours-on-Cloud-Run job we already scoped (we hold
   the MRMS daily record, ~945 MB); MYRORSS adds a one-time back-fill. No GridRad rebuild.
5. **Do NOT use FEMA NRI or SHIP as M1.** NRI is a downstream *loss index* (freq × exposure × loss-ratio, no
   size) — it competes with our model; keep it as an EAL **cross-check** only.

---

## Source timeline and roles

This is the simple operating view for hail. The detailed evidence is in
[`00_m1_data_products_research.md`](00_m1_data_products_research.md); this table is the shorthand we should
use when planning notebooks and source joins.

| Source | Practical window for this work | Evidence type | Role in the CONUS-grid hail layer | Do not use as |
|---|---:|---|---|---|
| **NOAA Storm Events / SPC reports** | 1996-2024+ for current QA pulls; database is longer | Point reports with date/location/size | Report-side validation, date context, calibration evidence | Raw grid truth or exact-cell frequency by itself |
| **MYRORSS** | 1998-2011 | Older gridded radar reanalysis / MESH-like evidence | Long-record gridded extension before the MRMS operational era | Standalone final climatology before full scan + source-homogeneity checks |
| **MRMS MESH** | 2014-present operational era; current pilot only uses a short 2024 window | Newer gridded radar MESH evidence | Current selected-cell pilot spine and operational-era baseline | Final frequency/tail estimate from the short pilot window |
| **FEMA NRI** | Current product; hail loss-rate inputs use 1996-2019 HLR | County/tract risk index / loss proxy | Downstream sanity check against broad EAL pattern | M1 hazard source, size distribution, or direct solar loss input |

The key consequence is that **NOAA reports choose/check dates, MRMS/MYRORSS provide gridded evidence, and
NRI stays downstream**. The 2012-2013 gap between MYRORSS and MRMS must stay explicit; do not silently bridge
it when computing rates.

---

## 1. Why hail isn't a clean Bucket-1 ready field

`01` split hazards into **Bucket 1** (a ready per-cell field exists → ingest, cheap: wildfire/FSim) vs
**Bucket 2** (build the field from raw). The hail research forces a refinement: **the two things M1 needs are
different statistical objects, and the public ecosystem serves them separately:**

```
   M1 needs, per 0.25° cell:
   ┌─────────────────────────────────┐     ┌─────────────────────────────────┐
   │ (1) ANNUAL FREQUENCY            │     │ (2) HAIL-SIZE DISTRIBUTION       │
   │     severe-hail events / yr     │     │     P(size) | event, 1″ → tail   │
   │   = an OCCURRENCE / RATE field  │     │   = a MAGNITUDE / SEVERITY field │
   ├─────────────────────────────────┤     ├─────────────────────────────────┤
   │ served (partially) by:          │     │ served (partially) by:           │
   │  • Murillo & Homeyer (validated,│     │  • Das & Allen 2024 (0.25°, but  │
   │    80km, days/yr, not download) │     │    EXTREME TAIL only, access?)   │
   │  • NRI (county, index)          │     │  • Murillo&Homeyer: MAX size only│
   │  • self-build from MESH/reports │     │  • self-build from MESH/reports  │
   └─────────────────────────────────┘     └─────────────────────────────────┘
            no product spans BOTH at our grain  →  hail = "self-build, anchored"
```

FSim works for wildfire because it's *one* pre-simulated field that already encodes occurrence (burn
probability) and severity (flame-length classes). Hail has no such unified product. `[OURS]`

## 2. The product landscape

`[REF]` (full citations in the research log appended below; honesty flags in §6.)

| Product | (1) Freq? | (2) Size dist? | Native res vs 0.25° | Record | Public DL? | Bias-corrected? | Role |
|---|---|---|---|---|---|---|---|
| **MRMS MESH** (`MESH_Max_1440min`) | derive | derive (empirical) | 0.01° (finer) | **2014→ (~11 yr)** | ✅ GRIB2 | ❌ over-predicts | **self-build baseline** (we hold it) |
| **MYRORSS** (Ortega 2022) | derive | derive | ~1 km (finer) | **1998–2011** | ✅ AWS | manual QC | **extends record ~16 yr** |
| **GridRad-Severe** (Murphy 2023) | ✗ raw volumes | ✗ derive | 0.02° (finer) | 2010→, ~100 days/yr | ✅ netCDF | partial | high-quality *input*, event-subset only |
| **Murillo & Homeyer 2021** | ✅ days/yr (sev+sig) | ✗ *max* only | 80 km (coarser, smoothed) | 1995–2017 (~2006+ reliable) | ❌ authors-on-request | ✅ **best public** | **bias anchor + validation target** |
| **NOAA Storm Events / SPC** | build (points) | build (points) | points | **1955→ (long)** | ✅ CSV | ❌ under-reported | **ground-truth / calibration** |
| **Das & Allen 2024** (Bayesian GEV) | ✗ | **✅ size return-likelihood (tail)** | **0.25° (exact)** | 15-yr min/cell | ⚠️ **unconfirmed** | ✅ statistical | **closest (2) field — verify access** |
| **Allen & Tippett 2017** | ✗ | ✅ size RP (tail) | 1° (coarser) | 1979–2013 | ⚠️ not packaged | ✅ | superseded by Das & Allen |
| **FEMA NRI (hail)** | ✓ county/tract | ✗ single loss-ratio | 49 km → polygons | HLR 1996–2019 | ✅ CSV | index | **EAL cross-check only — NOT M1** |
| **SHIP / mesoanalysis** | ✗ | ✗ | 40 km | — | ✅ | index | environmental index — not a field |

**Three groupings that matter:**
- **Raw gridded inputs** (MRMS, MYRORSS, GridRad-Severe) — fine resolution, but you derive the climatology
  yourself and they're not bias-corrected.
- **Validated-but-unusable-as-drop-in** (Murillo & Homeyer = frequency-only + coarse + email-only; Das & Allen
  = size-tail-only + access-unconfirmed) — the credible science, but neither is a complete, downloadable,
  on-grid M1.
- **Don't-use-as-input** (NRI, SHIP) — indices, downstream of where M1 sits.

## 3. The decisive gap — the size distribution must be self-built

The single most important finding: **no public product gives a full per-cell hail-size distribution from 1″
upward.** Murillo & Homeyer give *max* MESH per cell; Das & Allen give the *extreme tail* (annual-maxima GEV);
Storm Events and raw MESH are the **only** sources from which a *full empirical* size distribution can be
built — both with known size-accuracy caveats (MESH over-estimates; reports round to "quarter/golf-ball" and
under-sample). `[REF]`

Consequence chain (ties three of our open threads together): `[OURS]`
- **Severity is self-built ⇒** the M3 conditional-loss distribution rests on our own MESH→size→damage fit.
- **The radar record under-samples large hail ⇒** the deep tail must be **EVT-fit**, not bootstrapped — which
  is exactly the [A23 / 02 deep-tail caveat](../02_per_cell_output_schema.md). **Das & Allen 2024 is a published
  EVT hail-size model we can mirror methodologically** even if its data isn't downloadable.
- **So "fix the deep tail" and "source the size distribution" are the same task** — and both point at a fitted
  parametric severity with an EVT tail, which is *also* the storage-boundary decision (persist fitted
  distributions, not raw catalogs). Three threads, one move.

## 4. Recommended M1 sourcing strategy

**Self-build, anchored** — each source playing to its strength:

```
  RECORD (extend it)            BIAS-CORRECT (de-noise it)         GROUND-TRUTH (calibrate it)
  ┌────────────────────┐        ┌──────────────────────────┐       ┌────────────────────────┐
  │ MRMS MESH 2014→     │  +     │ Murillo & Homeyer 2021   │       │ NOAA Storm Events       │
  │ MYRORSS  1998–2011  │ ─────► │ recipe: MESH75/95 refit  │ ────► │ (reports, 1955→)        │
  │  ≈ 25 yr @ ~1 km    │ build  │ + LDA environment filter │ valid │ population-bias + true  │
  │ (2012–13 gap;       │ climo  │ → removes the over-      │ ate   │ size calibration        │
  │  homogeneity check) │        │   prediction Colby flagged│       │                        │
  └────────────────────┘        └──────────────────────────┘       └────────────────────────┘
        aggregate ~1 km → 0.25°  →  per-cell {freq NegBin λ,φ} + {size dist + EVT tail}  →  the M1 layer
                                     (optional: Das & Allen 2024 GEV for the size TAIL, if data is public)
```

1. **MRMS MESH + MYRORSS** → both (1) frequency and (2) an empirical size distribution at ~1 km, aggregated to
   0.25°. Stitching the two extends the record to **~25 yr** (1998–2011 + 2014→) — the single biggest
   improvement for stable frequencies and tails (cf. [learning-log 01](../../../../learning_logs/01_extending_a_short_hazard_record.md): *homogeneity > length* — so **check cross-era homogeneity** between the WSR-88D-era MYRORSS and operational MRMS, and document the 2012–13 gap).
2. **Murillo & Homeyer 2021** → the bias-correction **anchor + validation target.** Either request their 80 km
   fields, or (more robust) **replicate their recipe** — MESH75/95 size refit + Fisher-LDA environmental
   filter (precipitable water + 0–6 km shear) — to de-bias raw MESH. **This is the concrete answer to Colby's
   "MRMS wildly over-predicts hail."** `[REF]`
3. **NOAA Storm Events** → ground-truth for calibrating both the frequency (population/exposure bias) and the
   size distribution (MESH→true-size error).
4. **(Optional) Das & Allen 2024** → adopt its 0.25° GEV size-return field for the **tail** *iff* the data is
   public (verify the paper's Data Availability statement first); otherwise mirror it methodologically as our
   EVT severity model.

**Per-cell M1 artifact** (the storage-boundary output): `{NegBin λ, φ}` + `{size distribution params + EVT
tail}` per cell — tiny, durable, recomputable. Raw MESH/MYRORSS rasters become a rebuildable cache.

## 5. How this updates the earlier docs

- **Refines the Bucket split (`01`):** hail is a *third* category — **"self-build, anchored"**: no ready field,
  but a validated bias-correction recipe (Murillo & Homeyer) + ground-truth (Storm Events) to anchor it.
  Wildfire (Bucket 1) remains the easy case; this is why we built wildfire's M0 from FSim directly and hail
  needs this triage.
- **EVT is now load-bearing, not deferred:** §3 shows the size half of M1 *requires* a fitted+EVT severity —
  so the `02` deep-tail caveat (`*_rp500`, `tvar_*_99` provisional) resolves *through this work*, not separately.
- **Sparse-cell pooling has precedents to borrow:** Murillo & Homeyer's 80 km Gaussian smoothing and Das &
  Allen's Bayesian Gaussian-process regression are both the spatial-pooling we flagged for quiet cells
  ([`01` §5](../01_ideal_architecture_compute_and_grid.md)) — adopt one of those approaches for `n_events_cell`-poor cells.
- **Compute unchanged:** still the ~hours-on-Cloud-Run Stage-1 job from `01`; MYRORSS is a one-time
  ~1998–2011 back-fill (free, AWS `noaa-oar-myrorss-pds`).

## 6. Open decisions for the owner

> **DEC-H1 (gating).** Adopt **self-build, anchored** for hail M1 (MRMS+MYRORSS · Murillo-&-Homeyer-recipe
> bias-correction · Storm-Events ground-truth)? *(Recommended: yes — it's the only path to {freq + size} at
> 0.25°, and it directly de-biases the MESH over-prediction Colby raised.)*

> **DEC-H2.** Pull **MYRORSS** to extend the record to ~25 yr (with the cross-era homogeneity check + 2012–13
> gap documented)? *(Recommended: yes — free, ~doubles the record, biggest single tail improvement.)*

> **DEC-H3.** Chase **Das & Allen 2024** data access for the size tail? *(Recommended: spend 30 min verifying
> the Data Availability statement; if public, adopt for the tail; else mirror it as our EVT severity model.)*

> **DEC-H4.** Replicate the **Murillo & Homeyer MESH75/95 + LDA** bias-correction recipe in M1 (vs raw MESH)?
> *(Recommended: yes — this is the de-noising step the validation conversation hinged on.)*

> **DEC-H5 (housekeeping).** Log **FEMA NRI hail** as an external **EAL cross-check** (alongside Yuri's EGS
> tables), explicitly **not** an M1 input? *(Recommended: yes.)*

## 7. Citation hygiene / honesty flags (carry these before anything graduates to a plan)

- **"Murillo & Homeyer 2022"** (the name in our Q5): no distinct 2022 paper found. The climatology is
  **Murillo, Homeyer & Allen 2021, *MWR* 149(4):945–958, [10.1175/MWR-D-20-0178.1](https://doi.org/10.1175/MWR-D-20-0178.1)**; the MESH75/95 size refit is **Murillo & Homeyer 2019** (*JAMC* 58(5):947). Treat "2022" as this body of work.
- **Das & Allen 2024 public data/code: UNVERIFIED.** Open-access *paper* ([10.1038/s44304-024-00052-5](https://doi.org/10.1038/s44304-024-00052-5)) but no confirmed gridded download — do not assume the 0.25° field is obtainable until checked (DEC-H3).
- **MYRORSS / WAF hourly-climatology exact citations:** confirm at source — several publisher pages (AMS,
  FEMA, Nature) 403'd automated fetch; load-bearing claims (MESH ~1 km/2014→/over-predicts; Murillo & Homeyer
  authors-on-request; NRI = freq×exposure×HLR with no size stratification) were each corroborated across ≥2
  sources, but exact author lists/DOIs for the WAF hourly-climatology and MYRORSS (Ortega et al. 2022, *BAMS*
  103(3)) should be re-verified before plan-of-record.

---

## Cross-references

- The triage this resolves (Q5) + the Bucket split: [`01_ideal_architecture_compute_and_grid.md`](../01_ideal_architecture_compute_and_grid.md).
- The EVT/deep-tail caveat this work closes: [`02_per_cell_output_schema.md`](../02_per_cell_output_schema.md) (MC-depth note).
- Hail data caveats already on record: [A5 MESH-is-an-estimate](../../../../plans/hail/assumptions.md), [A24 small-n dispersion](../../../../plans/hail/assumptions.md).
- Record-length vs homogeneity: [learning-log 01](../../../../learning_logs/01_extending_a_short_hazard_record.md).
- Wildfire = the Bucket-1 contrast: [`../wildfire/01_v1_scope_and_framing.md`](../../wildfire/01_v1_scope_and_framing.md).
- `[REF]` key sources: MRMS `s3://noaa-mrms-pds` · MYRORSS `s3://noaa-oar-myrorss-pds` · GridRad-Severe NCAR RDA d841006 · Murillo & Homeyer 2021 [PMC8050942](https://pmc.ncbi.nlm.nih.gov/articles/PMC8050942/) · Das & Allen 2024 [npj Nat. Hazards](https://www.nature.com/articles/s44304-024-00052-5) · NOAA Storm Events [ncei.noaa.gov/stormevents](https://www.ncei.noaa.gov/stormevents/) · FEMA NRI [OpenFEMA](https://www.fema.gov/about/openfema/data-sets/national-risk-index-data).
