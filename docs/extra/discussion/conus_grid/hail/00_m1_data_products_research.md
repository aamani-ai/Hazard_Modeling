# Hail — M1 Data-Product Research Findings

*Factual research record (findings only — no recommendations; those live in the decision doc
[`../03_hail_m0m1_sourcing_triage.md`](01_m1_sourcing_triage.md)). Sources consolidated at the end.
Compiled 2026-06-13 from a cited web sweep; honesty/uncertainty flags in the last section.*

**Scope of the question.** Does a ready-made, validated/bias-corrected gridded hail product exist that hands
us, per ~0.25° cell, **both** (1) an annual frequency of severe-hail (≥1″ / 25.4 mm) events **and** (2) a
hail-**size** (magnitude) distribution — a "Bucket 1 ready field" analogous to USFS FSim burn probability — so
we can skip/augment self-building from MRMS `MESH_Max_1440min`?

**Bottom line.** **No single public product hands you both (1) and (2) as a ready field.** The closest are
(a) **MRMS MESH** itself — which you'd still turn into a climatology yourself (the self-build path), and
(b) **Das & Allen 2024 (Bayesian GEV)** — natively on the 0.25° grid, giving a hail-*size* return-likelihood
field, but occurrence-conditioned on extremes and (as of this search) with no confirmed public download.
Everything else is an *index* (FEMA NRI), a *frequency-only* climatology not publicly downloadable (Murillo &
Homeyer), or *raw radar volumes* (GridRad-Severe, MYRORSS) that are inputs, not answers.

## Framing — two different statistical objects

The two deliverables are **fundamentally different objects, and no product was designed to serve both:**

- **(1) Annual frequency of severe-hail events** = an *occurrence/rate* field (events or hail-days per year
  per cell). MESH climatologies (Murillo & Homeyer; MRMS hourly climo) target this.
- **(2) Hail-size distribution per cell** = a *magnitude/severity* field (a distribution or return-period
  curve of sizes conditional on an event). Extreme-value work (Allen & Tippett 2017; Das & Allen 2024) targets
  this — but at the *extreme tail*, not the full distribution from 1″ up.

This split is the central trade-off in everything below.

---

## Per-product findings

### 1. GridRad-Severe (Murphy, Homeyer & Allen 2023)

| Field | Finding |
|---|---|
| What it delivers | **Per-event 3-D gridded radar volumes** for the ~100 highest-end severe days/yr (tornado+hail+wind), ~1.3M tracked storms. Variables: reflectivity, ZDR, KDP, ρhv, spectrum width, azimuthal shear, radial divergence. **An event radar database, NOT a climatology** — no per-cell annual frequency, no size distribution as products (MESH must be derived from reflectivity). |
| Native resolution | **0.02° (~1.5–2 km)** horizontal; 0.5–1 km vertical; 5-min volumes. Finer than 0.25° — needs aggregation. |
| Coverage / vintage | **2010→present**, event-based (only the ~100 selected days/yr, not continuous). |
| Access | Public via NSF NCAR RDA/GDEX, dataset **d841006**, netCDF-4. Free; registration typical. |
| Validation / bias | Raw radar composite; bias/false-alarm correction is added by the parent GridRad-MESH work (Murillo & Homeyer 2021), not by GridRad-Severe itself. |
| **Verdict** | **NOT a ready field.** A high-quality *input* (better-curated than raw MRMS for big events), but you'd self-build the climatology, and it covers only the top ~100 days/yr so it can't give an unbiased annual frequency alone. |

### 2. MRMS MESH — operational + `MESH_Max_1440min` daily (the self-build source)

| Field | Finding |
|---|---|
| What it delivers | **Radar-estimated maximum hail size** (MESH, from SHI integrated above the 0 °C level). `MESH_Max_1440min` = rolling 24-h max. **Raw gridded field per timestep — not a frequency, not a distribution, not bias-corrected.** You build (1) and (2) yourself by thresholding/accumulating. |
| Native resolution | **0.01° (~1 km)**, GRIB2. Maps cleanly to 0.25° (~25×25 native cells per 0.25° cell). |
| Coverage / vintage | **Operational MRMS: Oct 2014 → present.** Real-time rolling viewer back to Oct 2020; the continuous usable series runs from the 2014 NCEP implementation (**~11–12 yr** — short for return periods). |
| Access | **Free, public, no auth.** NCEP real-time `mrms.ncep.noaa.gov/2D/MESH_Max_1440min/`; AWS Open Data `s3://noaa-mrms-pds` (anonymous, `--no-sign-request`); Iowa Environmental Mesonet archive. GRIB2 throughout. |
| Validation / bias | **The core problem: MRMS MESH over-predicts hail / high false-alarm rate vs ground reports.** Raw MESH is *not* bias-corrected — exactly what Murillo & Homeyer and the hourly-climatology paper fix. |
| **Verdict** | **The self-build baseline, not a ready field.** Highest-resolution, longest cleanly-public continuous source, but raw, biased, ~11 yr. You'd derive both frequency and an empirical size distribution from it. |

### 2b. MRMS hourly MESH climatology (published worked-example of the self-build)

| Field | Finding |
|---|---|
| What it delivers | An **hourly climatology of operational MRMS MESH-diagnosed severe (≥1″) and significant (≥2″) hail**, compared against Storm Data. Demonstrates the method (gridded frequency from MESH) but is a research paper, not a packaged field. |
| Resolution / coverage | MRMS-native (~1 km); short operational record (post-2014-ish). |
| Validation / bias | Explicitly compares MESH to Storm Data — documents the over-prediction. |
| **Verdict** | **Not a ready field** — a published worked example of the self-build; useful as a methods reference + sanity-check target. |

### 3. Murillo & Homeyer (2021) — "A 23-Year Severe Hail Climatology Using GridRad MESH Observations"

> Almost certainly the "Murillo & Homeyer 2022" in the original brief. The size-refit (MESH75/MESH95) traces
> to **Murillo & Homeyer 2019**; the CONUS climatology is the **2021 MWR** paper. No separate 2022 paper found.

| Field | Finding |
|---|---|
| What it delivers | **Per-cell mean annual frequency of severe hail-days (≥1″) and significant severe hail-days (≥2″)**, plus **climatological maximum MESH size** per cell. So **(1) annual frequency ✅** (as hail-*days*/yr); **(2) full size distribution ✗** — only the *max* MESH. |
| Native resolution | **80 km × 80 km with 1σ Gaussian smoothing.** Coarser than 0.25° and *smoothed* — maps to 0.25° only by interpolation, and the smoothing means adjacent 0.25° cells aren't independent. |
| Coverage / vintage | **1995–2017 (23 yr).** Authors caveat: sparse pre-2000, increasing trend to 2006, roughly stationary only after ~2006 (78% of erroneous scans pre-2006) → effectively reliable ~2006–2017. |
| Access | **NOT publicly downloadable.** Underlying GridRad + reports are public (NCAR RDA), but the derived MESH climatology fields are "available from the authors upon request." No file/API. |
| Validation / bias | **Yes — best public bias-correction.** Fisher's LDA on precipitable water + 0–6 km bulk shear filters MESH environments, removing false alarms; MESH refit to 75th/95th percentiles of ~6,000 GridRad-matched reports (vs 147 in the original Witt 1998 fit). |
| **Verdict** | **Partial (1) field; not (2); not directly accessible.** Best-validated public *frequency* climatology, but coarse+smoothed (80 km), max-size-only, and email-for-data. Best used as a **bias-anchor / validation target** for a MRMS self-build. |

### 4. NOAA Storm Events Database / SPC hail reports

| Field | Finding |
|---|---|
| What it delivers | Point **hail reports** with date/time, lat/lon, **reported max size**. From these you can build both a frequency and an empirical size distribution — but as *point reports*, not a gridded field. ~97,752 hail events. |
| Native resolution | Point data; grid it yourself. Maps to 0.25° in principle. |
| Coverage / vintage | **1950→present** (size more reliable in recent decades). Long record — its main advantage. |
| Access | **Free, public.** NCEI Storm Events bulk CSV; SPC reports archive. No auth. |
| Validation / bias | **Severely biased** — under-reporting away from population/roads/daytime; size rounded to reference objects ("quarter," "golf ball"); temporally inhomogeneous. **Population/exposure bias is the *opposite* problem** to MRMS over-prediction. |
| **Verdict** | **Not a gridded ready field, but the indispensable ground-truth.** What every bias-corrected product is calibrated against, and the only long-record empirical *size* source. Use to calibrate/validate — not as M1 itself. |

### 5. FEMA National Risk Index (NRI) — hail component

| Field | Finding |
|---|---|
| What it delivers | Per geography: **Annualized Frequency**, **Exposure** (building+ag+population value), **Historic Loss Ratio (HLR)**, **EAL ($)**, relative **Risk Index 0–100**. Gives a frequency + dollar EAL, **but NO hail-size distribution** — severity enters only via a single empirical HLR. (NRI stratifies *tornado* into 3 severity sub-types but **not** hail → confirms no hail size/severity stratification.) |
| Native resolution | Frequency on a **~49 km "fishnet" grid**; final NRI delivered at **county + Census-tract**, not a regular lat/lon grid. **Does not map cleanly to 0.25°.** |
| Coverage / vintage | Occurrence from NCEI/Storm Events; HLR from **SHELDUS v19, 1996–2019**, to 2020 USD. Updated periodically (latest doc Dec 2025, v1.20). |
| Access | **Free, public.** OpenFEMA bulk (CSV + geospatial), RAPT, web map. County + tract. |
| Validation / bias | Frequency inherits Storm Events bias; EAL is a historic-loss-ratio fit. A *risk index*, not a physically validated hazard field. |
| **Verdict** | **NOT a ready hazard field — it's a hazard/risk INDEX.** Bakes in exposure + loss ratio → a *competing/complementary loss-model output*, not an input. Gives neither a clean 0.25° physical frequency nor a size distribution. Useful only as an **EAL cross-check**. |

### 6. Environment/reanalysis-based & extreme-value products

#### 6a. Das & Allen (2024) — Bayesian GEV likelihood of extreme hail sizes (most relevant non-radar candidate)

| Field | Finding |
|---|---|
| What it delivers | **Return likelihood of extreme hail SIZE** via a GEV model in a Bayesian framework, Gaussian-process-smoothed. Covers ≥25 mm/1″ and the extreme tail (>1.75″, >2″; multi-decade RPs). Targets **(2)** — but as a *tail* model (annual maxima / rare sizes), **not a full distribution from 1″ up, and not occurrence frequency**. |
| Native resolution | **0.25° × 0.25° — exactly the target grid.** Bayesian prior from coarse 1° report data + local 0.25° info. **Best resolution match here.** |
| Coverage / vintage | Long report records (predecessor used 1979–2013); lowers the per-cell record requirement to 15 yr (vs 30 yr at 1°). Published **Dec 2024**, *npj Natural Hazards*. |
| Access | **UNCONFIRMED.** Paper open-access, but **no confirmed public gridded data/code** surfaced (no Zenodo/GitHub found; Nature page blocked automated fetch). **Do not assume the field is downloadable until the Data Availability statement is checked.** |
| Validation / bias | Calibrated to multiple hail-size report datasets; Bayesian approach addresses sparse-report uncertainty; finds earlier work *underestimates* high-return-period hazard. Report-driven (inherits report bias) but smooths statistically. |
| **Verdict** | **Closest thing to a ready SIZE field on the grid — but the magnitude *tail*, not occurrence, and access unverified.** If the gridded GEV parameters are obtainable, a strong (2)-side augmentation. Does not give (1). |

#### 6b. Allen, Tippett et al. (2017) — "An Extreme Value Model for U.S. Hail Size"
- **Delivers:** Gumbel/GEV **return intervals of hail SIZE** (annual-max dithered reports). (2)-side.
- **Resolution:** **1° × 1°** — 4× coarser than 0.25°; needs downscaling (which Das & Allen 2024 improved).
- **Coverage:** 1979–2013 reports. **Access:** paper public; gridded output not clearly packaged.
- **Verdict:** **Superseded by Das & Allen 2024**; useful as the methodological foundation. Not a ready 0.25° field.

#### 6c. Allen, Tippett & Sobel (2015) — empirical monthly hail-occurrence model
- **Delivers:** monthly **hail occurrence** vs large-scale environment (CAPE, shear, …) — an (1)-side, environment-driven *rate* model.
- **Verdict:** a *frequency* approach (no size distribution); methodology, not a packaged 0.25° field.

#### 6d. SPC Significant Hail Parameter (SHIP) / mesoanalysis
- **Delivers:** a **diagnostic index** (CAPE·mixing-ratio·lapse-rate·temp·shear / 4.4e7); SHIP>1 ⇒ favorable for ≥2″. **Not a frequency, not a size distribution** — a dimensionless environmental discriminator on a 40 km RAP grid.
- **Verdict:** **Index only.** Could feed a *self-built* environment-conditioned frequency model; not itself a hazard field.

#### 6e. MYRORSS — Multi-Year Reanalysis of Remotely Sensed Storms (Ortega et al. 2022)

| Field | Finding |
|---|---|
| What it delivers | A **MRMS-framework radar reanalysis** including **derived hail-size (MESH)** + echo-top/az-shear, as 3-D gridded volumes. Like MRMS, **raw gridded fields — not a climatology/frequency/distribution** (you derive those). |
| Native resolution | **~1 km** (az-shear ~0.5 km). Maps to 0.25° by aggregation. |
| Coverage / vintage | **Apr 1998 – Dec 2011 (~14 yr)** — extends the radar record ~16 yr *before* operational MRMS (2014). Manually QC'd. |
| Access | **Free, public** — AWS Open Data `noaa-oar-myrorss-pds`. |
| **Verdict** | **Not a ready field, but the key to a *longer* self-build.** MYRORSS (1998–2011) + operational MRMS (2014→) ≈ **25 yr** of ~1 km MESH (with a 2012–2013 gap) — materially better for stable frequencies + empirical size distributions than MRMS-2014-on alone. Still needs the same bias-correction work. |

---

## Bucket classification

| Product | (1) Freq? | (2) Size dist? | Native res vs 0.25° | Record | Public DL? | Bias-corrected? | Bucket |
|---|---|---|---|---|---|---|---|
| GridRad-Severe | ✗ (raw volumes) | ✗ (derive MESH) | 0.02° (finer) | 2010→, ~100 days/yr | ✅ netCDF (RDA) | partial | **Input** |
| MRMS MESH (self-build) | ✗ (derive) | ✗ (derive empirical) | 0.01° (finer) | 2014→ (~11 yr) | ✅ GRIB2 | ❌ over-predicts | **Input (baseline)** |
| Murillo & Homeyer 2021 | ✅ days/yr (sev+sig) | ✗ (max MESH only) | 80 km (coarser+smoothed) | 1995–2017 (~2006+ reliable) | ❌ authors-on-request | ✅ best public | **Partial (1), not accessible** |
| NOAA Storm Events / SPC | build (points) | build (points) | points | 1955→ (long) | ✅ CSV | ❌ under-reported | **Ground-truth / calibration** |
| FEMA NRI (hail) | ✓ county/tract | ✗ (single HLR) | 49 km → polygons | HLR 1996–2019 | ✅ CSV | index | **Index / EAL cross-check** |
| Das & Allen 2024 (Bayesian GEV) | ✗ | ✅ size return-likelihood (tail) | **0.25° (exact)** | reports, 15-yr min/cell | ⚠️ unconfirmed | ✅ statistical | **Closest (2) field — verify access** |
| Allen & Tippett 2017 | ✗ | ✅ size RP (tail) | 1° (coarser) | 1979–2013 | ⚠️ not packaged | ✅ | superseded by Das & Allen |
| SHIP / mesoanalysis | ✗ | ✗ | 40 km | — | ✅ | index | **Index** |
| MYRORSS | ✗ (derive) | ✗ (derive) | ~1 km (finer) | 1998–2011 | ✅ AWS | manual QC | **Input (extends record)** |

## Key trade-offs

- **Resolution:** only **MRMS/MYRORSS (~1 km)** and **Das & Allen (0.25°)** sit at-or-below the grid. Murillo
  & Homeyer (80 km, smoothed) and NRI (49 km / polygons) are coarser and don't map cleanly.
- **Record length:** raw MRMS alone is short (~11 yr) for return periods; **MYRORSS roughly doubles it**;
  Storm Events is long but biased; Das & Allen statistically extends the tail.
- **Validation/bias:** raw MESH **over-predicts**; reports **under-report**; **Murillo & Homeyer** and **Das &
  Allen** are the two credibly bias-corrected public efforts — but the former isn't a download and the latter's
  access is unconfirmed.
- **The decisive gap — SIZE distribution:** **no public product gives a full per-cell hail-size distribution
  from 1″ up.** Murillo & Homeyer give *max* size only; Das & Allen the *extreme tail*; Storm Events and raw
  MESH are the only sources from which a *full empirical* size distribution can be built — both with known
  size-accuracy caveats.

## Honesty / uncertainty flags

- **"Murillo & Homeyer 2022":** no distinct 2022 paper found. The climatology is **Murillo, Homeyer & Allen
  2021 (MWR)**; the MESH75/95 size refit is **Murillo & Homeyer 2019 (JAMC)**. Treat "2022" as this body of work.
- **Das & Allen 2024 public data/code: UNVERIFIED** — open-access paper, no confirmed gridded download.
- **Publisher fetch blocks:** FEMA, AMS, ResearchGate, Nature pages returned 403/redirect to automated fetch;
  their specifics come from HTML landing pages, FEMA update docs, and abstracts. The load-bearing claims (NRI =
  freq×exposure×HLR, no hail-size stratification; Murillo & Homeyer = authors-on-request; MRMS = ~1 km / Oct
  2014 / over-predicts) are each corroborated across ≥2 sources, but exact author lists / DOIs for the WAF
  hourly-climatology paper and the precise MYRORSS citation should be confirmed at source before plan-of-record.

---

## Sources

- **MRMS MESH:** NSSL MRMS data access · `mrms.ncep.noaa.gov/2D/MESH_Max_1440min/` · AWS `s3://noaa-mrms-pds` (registry of open data) · Iowa Environmental Mesonet MRMS archive · NSSL hail detection / MESH.
- **GridRad-Severe:** Murphy, Homeyer & Allen 2023, *MWR* 151(9):2257–2277 · NOAA repository PDF · NCAR RDA d841006 · gridrad.org/data.
- **MRMS hourly MESH climatology:** *Weather and Forecasting* 36(2), WAF-D-20-0158.1 *(AMS page 403 to auto-fetch — verify authors/year at source)*.
- **Murillo & Homeyer 2021:** *MWR* 149(4):945–958, DOI 10.1175/MWR-D-20-0178.1 (PMC8050942) · AMS journal page · MESH75/95 lineage: *JAMC* 58(5):947 (Murillo & Homeyer 2019).
- **NOAA Storm Events / SPC:** NCEI Storm Events Database · SPC climatology · reliability critique arXiv:1606.06973.
- **FEMA NRI:** NRI Methodology & Hazards Overview (Dec 2025) · Annualized Frequency definition · NRI data on OpenFEMA · data version/update doc (Dec 2025) *(FEMA PDFs 403 to auto-fetch — corroborated via HTML pages)*.
- **Das & Allen 2024:** *npj Natural Hazards*, DOI 10.1038/s44304-024-00052-5 · Allen CMU publications.
- **Allen & Tippett 2017:** *MWR* 145(11):4501–4519 · author PDF (Columbia).
- **Allen, Tippett & Sobel 2015:** *JAMES*, DOI 10.1002/2014MS000397.
- **SHIP:** SPC mesoanalysis SHIP help.
- **MYRORSS:** Ortega et al. 2022, *BAMS* 103(3), BAMS-D-20-0316.1 · AWS `noaa-oar-myrorss-pds` · NOAA repository.
