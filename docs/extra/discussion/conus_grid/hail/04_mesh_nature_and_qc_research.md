# 04 — MRMS MESH: Nature & Quality Control (factual research)

*A factual research record on **what MRMS MESH actually is**, how it behaves, why it can emit implausible
values, and how the community quality-controls / de-biases it. Findings + sources only — **no
recommendations** (those belong in the forthcoming plausibility-QC decision doc). This is the evidence base
for that decision. Marked `[REF]` = from the literature; `[OURS]` = our own observation.*

> **One-line takeaway:** MESH is a single empirical power-law estimate of hail size from radar — built to
> *over-shoot typical hail by design*, unreliable as a *size* (more skillful at *occurrence*), with a
> bias that is **bidirectional and event-dependent**, and a magnitude that **inflates under known radar
> sampling and contamination conditions**. Treating a single raw MESH value as literal hail size is not
> supported by the literature.

---

## 1. How MESH is computed

MESH is **one empirical power law** on top of the Severe Hail Index (SHI). The operational MRMS MESH is
identical to Witt et al. (1998)'s "MEHS" (Maximum Expected Hail Size); MRMS only changed the *integration
geometry* (multi-radar 3D grid) and the thermodynamic input source (model analysis), not the physics. `[REF]`

```
  3D reflectivity            Severe Hail Index  (SHI)                 MESH
  above the freezing level   ┌────────────────────────────────┐      ┌──────────────────┐
   Z (dBZ)  ───────────────► │ SHI = 0.1 · ∫ W_T(H) · Ė(Z) dH │ ───► │ MESH = 2.54·√SHI │ (mm)
                             │   Z→energy: 0 below 40 dBZ,     │ one  └──────────────────┘
                             │     full at ≥ 50 dBZ            │ power-law fit
                             │   W_T: 0 below 0°C level,       │ (Witt 1998), monotonic
                             │     1 above the −20°C level     │   → SHI up ⇒ MESH up
                             └────────────────────────────────┘
        ▲ residual bright-band, beam geometry,    ▲ freezing- / −20°C-level heights
          reflectivity miscalibration inflate Z     scale SHI (hence MESH) directly
```

- **`MESH = 2.54 · SHI^0.5`** (mm) — the entire SHI→size mapping is this one fit. `[REF]` (Witt et al. 1998)
- **SHI** integrates reflectivity-derived hail kinetic-energy flux, weighted to retain only the
  high-reflectivity hail core (40–50 dBZ transition) and only **above the freezing level** (0°C → −20°C
  temperature ramp). The 0°C and −20°C heights therefore scale SHI directly. `[REF]`

**Why it can emit implausible single-cell maxima.** MESH is a *monotonic* function of SHI, and SHI scales
with high reflectivity above the freezing level. Anything that inflates that reflectivity or the integration
depth inflates MESH: **residual bright-band (melting-layer) contamination** (survives QC — §5),
beam-broadening / non-uniform beam filling, reflectivity miscalibration, and a high −20°C level. The
*mechanism* for runaway values is well-supported. `[REF]` The literal extreme magnitudes we observe
(**max 1,437 mm; 585 CONUS cells ≥ 300 mm** over our record) are **our own data** `[OURS]` — the literature
explains *how* such values arise but the specific numbers are not from a cited source (see §8).

## 2. It is an upper-bound estimator by design

The Witt power law was fit to the **75th percentile** of observed hail sizes — so it is *designed* to
overshoot typical hail (≈75% of observed sizes fall below the estimate). It was fit on a **very small,
geographically narrow sample: 147 reports from only Oklahoma and Florida**, none below 0.75″ (~19 mm). `[REF]`

> This nuances our existing shorthand (assumption A5: *"MESH over-forecasts; ~75% of hail below it"*). The
> "75% below" is the **design percentile**, not a uniform bias — see §3.

## 3. Bias is bidirectional and event-dependent (not uniform over-prediction)

The most important correction to the casual "MESH over-predicts" framing: **a single MESH value does not map
consistently to hail severity.** `[REF]`

| MESH vs. reality | Direction | Source context |
|---|---|---|
| typical / median hail | **over**-predicts (75th-pct design) | Witt 1998 |
| **small** hail | **under**-predicts | Murillo & Homeyer 2019 |
| **large** hail | **over**-predicts | Murillo & Homeyer 2019; Picca & Ryzhkov 2012 |
| tilted storms in strong shear · left-movers · giant BWER · low-density dry hail | **under**-predicts | NOAA WDTD |
| low CAPE / high CIN / humid aloft | positive bias | Brook et al. 2024 |
| high CAPE+CIN / dry aloft | negative bias | Brook et al. 2024 |

Consensus across the refit literature: **MESH is more skillful at identifying hail *occurrence* than hail
*size*.** `[REF]`

## 4. Accuracy depends on radar sampling geometry

MESH degrades with how well radars sample the storm. `[REF]`

- Better with **multiple radars** sampling a cell; worse with **beam blockage, widely-spaced radars, far
  range, cone of silence**.
- **Range matters**: echoes only seen beyond ~**180 km** are low-confidence (GridRad-Severe drops them).
- Driven by **beam height** and the **freezing- / −20°C-level heights**.
- Produces **regional minima** where coverage is poor (Intermountain West; Appalachians).

## 5. Input QC — what's removed, what remains

MESH is built on the MRMS 3D reflectivity cube after dual-pol QC. `[REF]`

- **Removed:** ground clutter, anomalous propagation (AP), chaff, interference spikes, bioscatterers.
- **Remains:** **bright-band (melting-layer) contamination** — it shares the low-ρHV signature that the
  hail-preserving QC is tuned to keep, so it survives and can inflate SHI/MESH. (Mitigation improves across
  MRMS versions but is not eliminated.)

## 6. De-biasing — the Murillo & Homeyer refit

The principal published de-biasing re-fits the SHI→size power law against **~6,000 reports** (vs. the
original 147), to two percentiles: `[REF]`

```
  MESH75 = 16.566 · SHI^0.181      (75th percentile)
  MESH95 = 17.270 · SHI^0.272      (95th percentile)   ← best overall improvement over Witt MESH
```

- Used in the **GridRad-Severe** 23-yr hail climatology, which **also strips low-confidence distant /
  infrequently-sampled echoes**. `[REF]`
- **Operational MRMS still uses the original Witt (1998) formula** — the refits are research alternatives,
  not the operational product. `[REF]` (So the raw MRMS MESH we ingest is the un-refit Witt version.)
- Even refit, **MESH95 is calibrated slightly high** in most regions — **extreme overestimates over the
  Ohio Valley and southern Florida**, more reliable over the **Central Plains**. `[REF]`

## 7. Physical-plausibility ceiling — record hail size

A physically credible upper bound on hailstone *diameter*: `[REF]`

| Record | Value | Source |
|---|---|---|
| **US diameter record** — Vivian, SD, 23 Jul 2010 | **8.0 in ≈ 203 mm** (18.625″ circumference; 1.9375 lb) | NCEI / NWS |
| World heaviest hailstone — Gopalganj, Bangladesh, 1986 | ~1.02 kg | WMO |

So values materially above **~200 mm** have no physical precedent as hailstone diameter. *(Sourced from
NCEI/NWS/WMO; these were fetched but sit outside the formally vote-verified claim set — treat as
well-sourced, see §8.)*

## 8. What this research does **not** establish (open, honest gaps)

The adversarial verification flagged these as **not** directly supported by the verified claims:

1. **The literal extreme MESH magnitudes** (>300 mm, up to ~1,400 mm) are not from a cited source — the
   *mechanism* is supported, but the numbers are **our own observation** `[OURS]`, not literature. (We don't
   need an external cite to know our data hit 1,437 mm — we measured it — but no paper was found stating a
   canonical operational maximum.)
2. **Exact numeric QC parameters** of the gridded methods (GridRad-Severe's precise range / sampling-count
   cutoffs beyond ~180 km, any explicit MESH-magnitude cap, minimum-radar-count) were **not** captured.
3. **Spurious high-*frequency* cells** (repeated artifacts inflating a cell's severe-day count over a
   record): the literature here covers *magnitude* and *spatial* artifacts and coverage dependence, but
   **no explicit temporal frequency-inflation QC procedure was found.** This is the least literature-anchored
   part of our plausibility-QC problem `[OURS]`.

## Sources

Verification leaned on open mirrors / operational pages (AMS primary URLs frequently 403'd direct fetch);
all mutually corroborating. Primary:

- Witt et al. 1998, *Wea. Forecasting* 13(2) — the SHI/MEHS algorithm.
- Murillo & Homeyer 2019, *JAMC* 58(5):947 ([PMC8050948](https://pmc.ncbi.nlm.nih.gov/articles/PMC8050948/)) — MESH75/MESH95 refit.
- Murillo, Homeyer & Allen 2021, *JAMC* ([PMC8050942](https://pmc.ncbi.nlm.nih.gov/articles/PMC8050942/)) — GridRad-Severe climatology, size-unreliability.
- NOAA WDTD operational training — [SHI](https://vlab.noaa.gov/web/wdtd/-/severe-hail-index-shi-) · [MESH](https://vlab.noaa.gov/web/wdtd/-/maximum-estimated-size-of-hail-mes-1) · [POSH](https://vlab.noaa.gov/web/wdtd/-/probability-of-severe-hail-posh-).
- Wendt & Jirak 2021, *Wea. Forecasting* 36(2) — sampling/coverage dependence.
- Brook et al. 2024, *AMT* 17:407 — event-dependent bias.
- Zhang et al. 2016 *BAMS* + dpQC (*JTECH* 2020) — MRMS QC.
- NCEI/NWS Vivian hailstone report; WMO world records — physical ceiling.

---

## Cross-references

- The tail-QA pause this informs: [`03_mrms_tail_qa_and_m1_policy.md`](03_mrms_tail_qa_and_m1_policy.md).
- The hazard anchor's limitations section it feeds: [`../../../../hazards/hail/README.md`](../../../../hazards/hail/README.md).
- Our existing MESH-estimate caveat (A5) + footprint assumptions: [`../../../../plans/hail/assumptions.md`](../../../../plans/hail/assumptions.md).
- The sourcing triage that named the de-biasing path: [`01_m1_sourcing_triage.md`](01_m1_sourcing_triage.md).
