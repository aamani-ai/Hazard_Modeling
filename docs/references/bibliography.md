# Bibliography — external references

The external sources that ground the methods in this repo, **reproduced here with DOIs/URLs so the repo
is self-sufficient** (no access to the research repo required to check provenance). Each is also
catalogued, with fuller "load-bearing content" notes, in the research repo's reference packs — primarily
[`A24_reference_pack.md`](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/architecture/references/A24_reference_pack.md)
and [`learnings/19` (single-centroid triplet)](https://github.com/D-ivyy/infrasure-hazard-competitive-research/blob/main/learnings/19_canonical-citation-triplet-for-single-centroid-error.md).

Short-keys (e.g. `[Klugman et al. 2012]`) are used in the provenance map ([`README.md`](README.md)).
Entries are grouped by theme; **(deferred)** marks sources that ground the *roadmap*, not what's built today.

> **Citation integrity:** every entry below was transcribed from the research-repo reference packs, not
> generated. **DOI hygiene:** for *books* the stable id is the ISBN/publisher; where a DOI points to a
> *review or catalog record* (not the work itself) it is labelled as such — a DOI is cited as *the source*
> only when it identifies that exact work. Where we couldn't confirm a precise identifier we name the
> dataset/standard and its issuing body rather than invent one.

---

## 1 · Frequency & count distributions

- **[Klugman et al. 2012]** — Klugman, S. A., Panjer, H. H., & Willmot, G. E. (2012).
  *Loss Models: From Data to Decisions* (4th ed.). Wiley. **ISBN 978-1-118-31532-3** (the book's stable id).
  *(The [10.2307/2669713](https://doi.org/10.2307/2669713) DOI is a JSTOR citation record, not the book itself.)*
  *Grounds:* the compound-Poisson frequency–severity backbone; when `Var(N) > E[N]` (over-dispersion) the
  Negative Binomial (Poisson–Gamma mixture) is the standard alternative — our M1/M4 frequency choice.
- **[Embrechts et al. 1997]** — Embrechts, P., Klüppelberg, C., & Mikosch, T. (1997). *Modelling Extremal
  Events for Insurance and Finance*. Springer (Applications of Mathematics 33).
  *([10.2143/AST.28.2.519071](https://doi.org/10.2143/AST.28.2.519071) is an ASTIN Bulletin **review** record — it identifies a review, not the Springer book.)*
  *Grounds:* compound-Poisson uniqueness + the NegBin-as-Poisson-mixture bridge (and EVT, §5 below).
- **[Allen & Tippett 2015]** — Allen, J. T., & Tippett, M. K. (2015). The characteristics of United States
  hail reports: 1955–2014. *Electronic J. of Severe Storms Meteorology*, 10(3). DOI
  [10.55599/ejssm.v10i3.60](https://doi.org/10.55599/ejssm.v10i3.60).
  *Grounds:* US hail report climatology + the 2010 0.75″→1.0″ severe-threshold redefinition (our A2); annual
  hail-count variance consistent with over-dispersion.
- **[Hussain et al. 2025]** — Hussain, T., Villamor, E., Shakil, M., Ahsanullah, M., & Kibria, B. M. G.
  (2025). On a Beta-Gamma Discrete Distribution for Thunderstorm Count Modeling with Risk Analysis.
  *Mathematics*, 13(24), 3913. DOI [10.3390/math13243913](https://doi.org/10.3390/math13243913).
  *Grounds:* empirical over-dispersion in **thunderstorm** counts (Poisson rejected) — supporting evidence
  that convective-storm counts are over-dispersed, hence the NegBin choice (our A8/DD-2). *(Thunderstorm-count
  evidence, not a hail-specific NegBin proof.)*
- **[Miralles et al. 2023]** — Bayesian modeling of insurance claims for hail damage.
  arXiv:2308.04926. DOI [10.48550/arXiv.2308.04926](https://doi.org/10.48550/arXiv.2308.04926).
  *Grounds:* over-dispersion in hail *claim* counts; also the swath-geometry link (§3) and the
  deterministic-curve-underestimates-variance motivation for a conditional-DR distribution.

*Climate-conditioned / regime-switching λ — **(deferred)**, grounds the non-stationary-frequency roadmap:*
- **[Lepore et al. 2021]** — Future Global Convective Environments in CMIP6 Models.
  *Earth's Future*, 9(11). DOI [10.1029/2021EF002277](https://doi.org/10.1029/2021EF002277).
- **[Brooks/Taszarek et al. 2020]** — Severe Convective Storms across Europe and the United States. Part I:
  Climatology. *J. Climate*, 33(23). DOI [10.1175/JCLI-D-20-0345.1](https://doi.org/10.1175/JCLI-D-20-0345.1).
- **[Goldenberg et al. 2001]** — The Recent Increase in Atlantic Hurricane Activity. *Science*, 293(5529),
  474–479. DOI [10.1126/science.1060040](https://doi.org/10.1126/science.1060040). *(AMO regime-switching λ.)*
- **[Lepore & Tippett 2021]** — ENSO-Based Predictability of a Regional Severe Thunderstorm Index.
  *Geophys. Res. Lett.*, 48. DOI [10.1029/2021GL094907](https://doi.org/10.1029/2021GL094907).
- **[Sena et al. 2025]** — Multidecadal Fluctuations in the Observed ENSO–Tropical Cyclone Teleconnection.
  *Geophys. Res. Lett.*, 52. DOI [10.1029/2025GL116968](https://doi.org/10.1029/2025GL116968).

## 2 · Coupling & exposure geometry

- **[Stoyan et al. 1995]** — Stoyan, D., Kendall, W. S., & Mecke, J. (1995). *Stochastic Geometry and Its
  Applications* (2nd ed.). Wiley. **ISBN 978-0-471-95099-0** (the book's stable id).
  *(The [10.2307/2531521](https://doi.org/10.2307/2531521) DOI is a JSTOR **review** record.)*
  *Grounds:* the Minkowski-sum / Boolean-model framework for the probability a random footprint intersects a
  fixed target — the stochastic-geometry basis for our M2 hit probability `p = (√F + √s)²/A` (A21 derives the
  specific convex-shape form). 3rd ed.: Chiu et al. (2013).
- **The single-centroid under-count triplet** *(the empirical case that point-exposure `F/A` is wrong for
  utility-scale renewables — the bug our M2 fixes):*
  - **[Thompson 2024 / kWh]** — Thompson, *Modeling Solar Hail Risk: From Industry Catalog to
    Catastrophe-Level Accuracy*, 2024 Solar Risk Assessment.
    [PDF](https://kwhanalytics.com/wp-content/uploads/2025/02/Solar-Risk-Assessment-2024-1.pdf). Industry
    catalogs **under-estimate hail AAL by ~300%** treating utility-scale solar as a single-centroid point
    (backtested vs. claims).
  - **[Sabbatelli & Goodyer 2025 / Moody's]** — *Applying Specialized Risk Treatment to a Solar Farm*,
    Jan 2025.
    [link](https://www.moodys.com/web/en/us/insights/insurance/applying-specialized-risk-treatment-to-a-solar-farm.html).
    Single→multi-centroid disaggregation shifts AAL **+230% (flood), +2% (windstorm)** on a 2,700-acre solar
    farm — the incumbent's own case study.
  - **[Rudaviciute 2022 / Moody's]** — *Risk Modeling and the Rise of Renewables*, 2022.
    [link](https://www.moodys.com/web/en/us/insights/insurance/risk-modeling-and-the-rise-of-renewables.html).
    A single structure-condition modifier swings wind-farm AAL **−41% to +83%** — engineering features
    dominate modeled loss.
- **[OASIS LMF Keys 2024]** — Oasis LMF Documentation.
  [link](https://oasislmf.github.io/sections/keys-service.html). *Grounds:* `area_peril_id` separates
  hazard-cell-hit from vulnerability; documents the single-centroid approximation for polygon/extended risks.
- **[Neuberger Berman 2025]** — *Catastrophe Modeling 101*.
  [PDF](https://www.nb.com/handlers/documents.ashx?id=55b7bbdd-7ae0-4540-8e9d-32f78a34ce99). *Grounds:*
  geocoding resolution alone produces ~3× loss differences — geometry is a first-order uncertainty (also §6).

## 3 · Severity-correlated footprint (hail swath ↔ peak size)

- **[Schuster et al. 2005]** — Characteristics of the 14 April 1999 Sydney hailstorm. *Nat. Hazards Earth
  Syst. Sci.*, 5, 613–620. DOI [10.5194/NHESS-5-613-2005](https://doi.org/10.5194/NHESS-5-613-2005).
  *Grounds:* radar reflectivity ≥55 dBZ ≈ the ground damage swath; larger stones ↔ larger/longer footprint —
  the basis for treating the MESH footprint as the damage footprint (our M1/M3).
- **[Wendt & Jirak 2021]** — An Hourly Climatology of Operational MRMS MESH-Diagnosed Severe and Significant
  Hail. *Weather and Forecasting*, 36(2), 461–478. DOI
  [10.1175/WAF-D-20-0158.1](https://doi.org/10.1175/WAF-D-20-0158.1). *Grounds:* the MRMS MESH product we use
  for M0/M1; documents MESH-vs-SPC undercount in low-population areas (our A5 MESH-bias caveat).

## 4 · Damage & vulnerability

- **[FEMA P-58 / ATC 2012]** — Applied Technology Council, *Seismic Performance Assessment of Buildings,
  Vol. 1 — Methodology*. [link](https://femap58.atcouncil.org). *Grounds:* the fragility (P(damage state |
  intensity)) vs. vulnerability (expected loss ratio) distinction; lognormal fragility form.
- **[Rossetto & Elnashai 2003]** — Derivation of vulnerability functions for European-type RC structures.
  *Engineering Structures*, 25(10), 1241–1263. DOI
  [10.1016/S0141-0296(03)00060-9](https://doi.org/10.1016/S0141-0296(03)00060-9). *Grounds:* the
  fragility→vulnerability integration; upper-damage-state data scarcity (why we cap, not extrapolate).
- **[HAZUS / FEMA 2022]** — *Hazus Earthquake / Flood / Hurricane Technical Manuals* (v5.1). FEMA.
  *Grounds:* the de-facto US fragility-parameter reference (lognormal CDF damage states); the benchmark
  vendor curves calibrate against.
- **[Cornell et al. 2002]** — Probabilistic Basis for 2000 SAC/FEMA Steel Moment Frame Guidelines. *J. Struct.
  Eng.*, 128(4), 526–533. DOI
  [10.1061/(ASCE)0733-9445(2002)128:4(526)](https://doi.org/10.1061/(ASCE)0733-9445(2002)128:4(526)).
  *Grounds:* why lognormal fragility is the cross-peril default (analytical tractability).
- **[Porter et al. 2001]** — Assembly-Based Vulnerability of Buildings. *Earthquake Spectra*,
  17(2), 291–312. DOI [10.1193/1.1586176](https://doi.org/10.1193/1.1586176). *Grounds:* component→asset
  vulnerability by convolving subcomponent fragilities — the engineering basis for our **capex-weighted
  subsystem blend** (M3).
- **[Fritsch & Carlson 1980]** — Monotone Piecewise Cubic Interpolation. *SIAM J. Numer. Anal.*, 17(2),
  238–246. DOI [10.1137/0717021](https://doi.org/10.1137/0717021). *Grounds:* PCHIP monotone interpolation
  for tabulated damage curves (no spurious oscillation) — the safe interpolation default.
- **[Verisk (AIR) 2018]** — *Modeling Fundamentals: Understanding Uncertainty*.
  [link](https://www.verisk.com/blog/Modeling-Fundamentals--Understanding-Uncertainty/). *Grounds:*
  primary vs. **secondary uncertainty** (a damage *distribution*, not just a mean curve) — the basis for our
  **(deferred)** conditional-DR upgrade (A17).
- **[OASIS/IF 2017]** — Understanding and managing damage uncertainty.
  [link](https://oasislmf.org/download_file/201/216). *Grounds:* empirical (non-parametric) vulnerability
  distributions; for hail, a single MDR is inadequate — **(deferred)** conditional-DR support.
- **[Sigona / CAS 2019]** — *Catastrophe Modeling Overview* (CAS Reinsurance Bootcamp).
  [PDF](https://www.casact.org/sites/default/files/old/las_2019_reinsurance_bootcamp_sigona.pdf). *Grounds:*
  how secondary uncertainty is encoded in the ELT (mean + CV, beta loss) — **(deferred)**.

## 5 · Risk metrics, Monte-Carlo engine & EVT

- **[McNeil et al. 2015]** — *Quantitative Risk Management: Concepts, Techniques and Tools* (rev.
  ed.). Princeton University Press.
  [ref](https://www.semanticscholar.org/paper/b3877f996625ef0467a0a2843970b119bfecc5b3). *Grounds:* unifies
  compound-Poisson with EVT; formalises frequency–severity independence (our M4 separation) and coherent tail
  risk (VaR/TVaR).
- **[American Academy of Actuaries 2018]** — *Uses of Catastrophe Model Output* (Catastrophe Management Work
  Group).
  [PDF](https://www.actuary.org/sites/default/files/files/publications/Catastrophe_Modeling_Monograph_07.25.2018.pdf).
  *Grounds:* the **OEP vs. AEP** distinction and why AEP > OEP for high-frequency perils like SCS — our DD-4
  frame-consistency rule.
- **[Klugman et al. 2012]** — *(see §1)* — also grounds the limited expected value `E[X∧d]` and
  stop-loss `E[(X−d)₊]`, i.e. why financial terms don't commute with expectation (§6).

*EVT tail — **(deferred)**, grounds the A23 deep-tail upgrade:*
- **[Coles 2001]** — Coles, S. (2001). *An Introduction to Statistical Modeling of Extreme Values*.
  Springer. *([10.1198/jasa.2002.s232](https://doi.org/10.1198/jasa.2002.s232) is a JASA **review** record.)* POT/GPD end-to-end; MRL & parameter-
  stability threshold selection; small-n MLE bias (relevant to our n=5 φ caveat, A24).
- **[Davison & Smith 1990]** — Models for Exceedances over High Thresholds. *JRSS-B*, 52(3), 393–442.
  [JSTOR](https://www.jstor.org/stable/2345667). The parameter-stability plot for GPD threshold selection.
- **[McNeil 1997]** — Estimating the Tails of Loss Severity Distributions Using EVT. *ASTIN Bulletin*, 27(1),
  117–137. DOI [10.2143/AST.27.1.563210](https://doi.org/10.2143/AST.27.1.563210). EVT VaR can differ 2–3×
  from lognormal in the tail; needs ≥50–100 exceedances (why our bootstrap tail is truncated, A23).

## 6 · Financial terms — **(deferred, methodology §9)**

- **[OASIS LMF fmcalc 2024]** — Oasis LMF Documentation.
  [link](https://oasislmf.github.io/sections/financial-module.html) ·
  [v2020 white paper](https://oasislmf.org/application/files/2016/1832/6318/OasisFinancialModule_v2020.pdf).
  *Grounds:* the 8-level deductible→limit ordering and recursive reinsurance inuring — why financial terms
  must be applied per-sample-path, not to the mean curve (our A21 gross-loss-only scope).
- **[Neuberger Berman 2025]** — *(see §2)* — practitioner explanation of why applying a deductible to the
  loss *distribution* (not each path) produces wrong AAL, especially in the tail.

## 7 · Fit diagnostics & small-sample

- **[Hosking 1990]** — L-moments. *JRSS-B*, 52(1), 105–124. DOI
  [10.1111/j.2517-6161.1990.tb01775.x](https://doi.org/10.1111/j.2517-6161.1990.tb01775.x). *Grounds:*
  robust fitting for small/heavy-tailed samples — relevant to fitting φ at small n and the future EVT tail.
- **[Das & Ghosh 2013]** — Weak Limits for Exploratory Plots in the Analysis of Extremes. *Bernoulli*, 19(1),
  105–143. DOI [10.3150/11-BEJ401](https://doi.org/10.3150/11-BEJ401). *Grounds:* prefer QQ diagnostics over
  p-value tests when n < 200 — the discipline behind our small-record honesty (A24).

## 8 · Data sources & standards

- **MRMS / MESH** (Multi-Radar Multi-Sensor, NOAA/NSSL) — gridded radar hail size; our M0 spine.
  [nssl.noaa.gov/projects/mrms](https://www.nssl.noaa.gov/projects/mrms/). Climatology: **[Wendt & Jirak
  2021]** (§3).
- **SPC / NCEI Storm Events** (NOAA) — point hail reports; our M0 cross-check.
  [spc.noaa.gov/climo/reports](https://www.spc.noaa.gov/climo/reports/) ·
  [ncdc.noaa.gov/stormevents](https://www.ncdc.noaa.gov/stormevents/).
- **NWS severe-hail threshold** — 1.0 in (25.4 mm) since 2010 (our A2; see **[Allen & Tippett 2015]**).
- **Damage-curve inputs** — the M3 curve is curated in the **`infrasure-damage-curves`** repo from
  **IBHS** PV-module hail testing + **IEC 61215 / UL 61730** module standards, weighted by **NREL ATB / SAM**
  capex shares. (See that repo for the per-source curve provenance.)
- **Asset value (TIV)** — the **asset registry** (EIA 66880); see assumptions A19 for the valuation-basis
  caveat.
