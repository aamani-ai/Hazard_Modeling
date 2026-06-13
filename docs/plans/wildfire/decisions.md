# Wildfire pipeline — decisions log

Running record of the non-obvious design decisions for the wildfire → solar build, ADR-style
(context → options → decision → why → revisit trigger). `DD-W*` = wildfire-scoped (distinct from hail's
`DD-*`). Newest on top. Full reasoning lives in the discussion docs
([`01 scope/framing`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md),
[`02 data dictionary`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)).

---

## DD-W8 · Wildfire × solar damage curve = InfraSure BoS-weighted, **anchored**, approximate (legacy discarded)

**Date:** 2026-06-13 · **Status:** decided (v1) · **realized in M3** (`01_damage`).

**Context.** M3 needs a kW/m → damage curve. Two candidates: the **legacy** (`Solar|Wildfire|Direct` = a
*generic First Street* curve, identical across Real-Estate/Solar/Wind, on the wrong axis = flame-length feet,
degenerate) and the **InfraSure library** (6 BoS subsystem logistics on Byram kW/m, capex-weighted).

**Decision.** Use the **InfraSure `WILDFIRE × solar`** curves (canonical `master_curve_index`, params read
**live** — not the lab's hard-coded copy → no drift). Capex-weighted blend `Asset_DR(I) = Σ wᵢ·DRᵢ(I)`,
**Channel-1 physical only**, `d = 10 m`. **Anchored:** subtract each subsystem's `DRᵢ(0)` so `DR(0)=0`.
Weights sum ~0.70 → **30% TIV non-damageable** (V1, [AW-19](assumptions.md)); anchored cap ≈ **0.56**.
Approximate/temporary (Low/Low-Med confidence; `d=10 m` ±40%; zero empirical RE calibration). **Legacy
discarded.**

**Why.** Right axis (kW/m), BoS-structured (the InfraSure wedge), matches hail's M3 (A22) + the V1 scope. The
legacy is generic + wrong-axis. **Anchoring** removes a **non-physical floor** — the canonical *raw* logistics
give `DR(0) ≈ 5%` (no fire, yet damage) because `k·x0 ≈ 1.5–2.7` isn't sharp; it was dominating the low-fire
conditional loss (Hayhurst 5.8% → **1.0%** anchored). The legacy's own 'anchored logistic' did the same.

**Revisit trigger.** The **damage-curve revamp** (accurate, sharper-threshold, RE-calibrated curves; a
conditional-DR *distribution*; explicit `d`) — owner is updating `infrasure-damage-curves`.

---

## DD-W7 · Wildfire frequency = Poisson(λ = −ln(1−BP)) per asset, fano = 1 — no fit (FSim pre-integrated)

**Date:** 2026-06-13 · **Status:** decided (v1) · **realized in M1** (`01_catalog`) · doctrine: methodology §4–5/§9.

**Context.** M1 must declare a frequency process. Hail *fit* `λ_collection` from a short record (NegBin +
dispersion). Wildfire is different: FSim pre-integrates ≥20,000 seasons into a per-pixel **annual burn
probability BP**, and is **site-conditioned** (no areal "miss").

**Decision.** `frequency_process = poisson`, **`λ = −ln(1−BP)` per asset** (the rate s.t. `P(≥1 fire/yr) = BP`),
**`fano = 1`**. The rate comes from the **site BP directly** (site-conditioned), **not** `λ_collection ×
spatial_factor`. Bernoulli-per-year is the BP-native form; Poisson is its rare-event limit and a **NegBin
special case** → the **shared compound engine is untouched**.

**Why.** (1) **Doctrine** — methodology: site-conditioned perils take the rate "from the site intensity process
directly," no spatial factor. (2) **No short-record fit** — FSim already Monte-Carlo'd the seasons, so the
inter-annual dispersion lives *inside* BP; there's no annual-count series to fit (unlike hail). (3) The
`−ln(1−BP)` vs naive-BP correction is a real **~2% at Matrix** (BP 4.3%), negligible at Hayhurst — the proper
Poisson rate, free to compute.

**Caveat.** `fano = 1` is **structural** (we can't test dispersion — no count series; it's baked into FSim's
BP).

**Revisit trigger.** Multi-fire-year clustering, a **portfolio** (correlated BP across nearby assets →
dispersion/correlation term), or non-stationarity (`λ(t)`, [AW-13](assumptions.md)).

---

## DD-W6 · V1 site-conditioning = defensible proxy; imagery deferred to V1.5+

**Date:** 2026-06-12 · **Status:** decided (v1)

**Context.** Bucket-3 susceptibility is fundamentally a distance/fuel term. Real site conditions (defensible
space, vegetation against the array, equipment spacing, cable routing) are in **no public dataset** and would
need imagery/owner data.

**Decision.** V1 susceptibility = boundary-sampled BP + the conditional intensity distribution **conditioned
on LANDFIRE fuel class** + a **fixed, documented `d = 10 m`** (line-source `1/d`); for wind, a **hub-height
attenuation** factor. **No imagery in V1.** Expose cable-routing / defensible-space as *named hooks* for a
V1.5+ imagery/owner-data enhancement.

**Why.** Honest and buildable from data we have; imagery is a precision improvement, not a foundation (even
the legacy roadmap graded it Gen-2). Keeps all site-conditioning inside M2/M3; the loss engine is untouched.

**Revisit trigger.** When imagery-derived defensible-space / fuel-cover is available, or an owner supplies
site layout — fold it into the `d` and fuel terms (rescaling `x0`, not a free knob).

---

## DD-W5 · Spatial grain = asset-boundary zonal sampling (not the 0.25° screening cell)

**Date:** 2026-06-12 · **Status:** decided (v1)

**Context.** The `wildfire_analysis_lab` samples WRC to a **0.25° (~600 km²) cell mean** — its own docs call a
cell "a regional screening unit, not a project boundary." Wildfire is site-conditioned (largest single-centroid
penalty; cf. Sabbatelli-Goodyer flood +230%), so a regional mean dilutes the high-risk pocket a plant sits in.

**Decision.** Sample the hazard rasters **within each `asset_boundary` polygon** (zonal stats: mean + hotspot
max + pixel count for QA). For the ~36% of assets lacking a boundary, fall back to a **capacity→radius circle**
(`r ≈ 69·√(MW_DC)` m). Carry the hail single-centroid disaggregation discipline into wildfire M2.

**Why.** It's the correct bucket-3 grain and the cleanest step up from the lab's screening cell; the lab cell
*max* already showed it brackets the asset value while the *mean* dilutes it (see [`01 §6`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md)).

**Revisit trigger.** Boundary coverage improves, or a finer within-boundary sub-point scheme is warranted.

---

## DD-W4 · Severity flame-length source = native FSim FLP1-6 (avoid the lossy WRC reconstruction)

**Date:** 2026-06-12 · **Status:** decided (v1) · Evidence: [`02 §3,§5`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)

**Context.** WRC 2.0 publishes only the **collapsed** intensity metrics (CFL, FLEP4, FLEP8) — *not* the
6-class histogram. Recovering FLP1-6 from `{CFL, FLEP4, FLEP8}` is **under-determined / lossy** (the lab's
reconstruction heuristics have no cited provenance). But the **native FSim line publishes the full FLP1-6
histogram** as standalone public rasters (`RDS-2016-0034-3`, 270 m, CC BY 4.0).

**Options.** (i) WRC FLEP4/8 + reconstruct FLP6 (easy 30 m fetch, lossy). (ii) Native FSim FLP1-6 directly
(270 m, full histogram, no reconstruction). (iii) richer library FLP.

**Decision.** **(ii) native FSim FLP1-6** as the V1 severity histogram; explore WRC 2.0 as the 30 m comparison
candidate (M0 notebook 01). Fall back to (i) **only** if 30 m turns out to be a hard requirement — and if so,
register the reconstruction as an assumption and sensitivity-test it.

**Why.** Full 6-class histogram, single clean vintage (BP + histogram from the *same* 270 m FSim product — no
BP-vs-intensity vintage split), no reconstruction loss. For utility-scale solar, 270 m is very likely
sufficient. *Basics-spot-on:* don't build severity on an unprovenanced interpolation when the real histogram
is free.

**Revisit trigger.** If a reference asset is small relative to 270 m, or finer intensity texture is needed →
reconsider the 30 m WRC path with an explicit, tested reconstruction.

---

## DD-W3 · Data sourcing = public USFS rasters, fetched directly — NO Hydronos API, no secret dependency

**Date:** 2026-06-12 · **Status:** decided

**Context.** The legacy model pulled FSim BP + flame length via the paid **Hydronos "Wildfire Risk API"**
(hard-coded key at `_legacy_wildfire/scripts/wildfire_eal_pipeline.py:39`, in git history). The research
confirmed Hydronos is **just a hosted wrapper over public FSim data** — it buys query-by-geometry, not unique
data.

**Decision.** Source **both** candidates directly from **public, no-auth, CC BY 4.0 USFS rasters**: WRC 2.0
from the `imagery.geoplatform.gov` ArcGIS ImageServers (reuse the lab's tested fetch plumbing), and native
FSim FLP1-6 from the USFS RDS archive (`RDS-2016-0034-3`) / FSim ImageServers. The new pipeline has **no
secret dependency**. **Retire Hydronos.**

**Why.** (1) No unique data lost. (2) Honors our no-secret commitment (the leaked key must be **rotated by the
owner** regardless). (3) Lets us do our **own boundary-zonal sampling** ([DD-W5](#dd-w5--spatial-grain--asset-boundary-zonal-sampling-not-the-025-screening-cell)) instead of accepting Hydronos's pre-aggregation. (4) M0's
purpose is to meet the *raw* data — a pre-digested API response defeats that.

**Validation (2026-06-13).** Cross-checked live against the legacy Hydronos API (notebook `02b_fsim_via_hydronos`,
key read from legacy, not committed): Hydronos **reproduces both public candidates** — 270m FSim FLP1-6 *and*
30m WRC CFL/FLEP — to ~2–3 dp at the footprint (Matrix FLEP4 0.654 vs 0.662; 30m FLEP4 0.387 vs 0.382). So
Hydronos is confirmed to be the *same public USFS data aggregated server-side* → **public loses nothing**;
DD-W3 holds empirically. (Bonus: the API's `resolution` serves both candidates and `analysis="buffer_ring"`
is a handy surrounding-fuel tool — see AW-15.)

**Revisit trigger.** None expected. (If a future need genuinely required a hosted API, it would have to clear
the no-secret + own-the-grain bars first.)

> ⚠️ **Owner action (security, independent of modeling):** rotate/revoke the leaked Hydronos key.

---

## DD-W2 · Coupling type = site-conditioned (bucket 3) — same row for solar & wind; NOT hail's Minkowski

**Date:** 2026-06-12 · **Status:** decided · Corroborated A12 dual-test + A21 dispatch row 5.

**Context.** Hail is areal hit-or-miss (Minkowski `(√F+√s)²/A`). Wildfire's magnitude is **burn-probability ×
fire-line-intensity** — an intensity-field-×-probability quantity, *not* a footprint area `F` — so it
physically cannot feed Minkowski.

**Decision.** Wildfire coupling = **site-conditioned** (field × per-asset susceptibility), the **same coupling
row for both solar and wind**. The fire **perimeter polygon is the M1 *ontology*** (the event's identity);
**site-conditioned is the M2 *coupling***. The solar/wind difference lives on the orthogonal
**exposure-geometry** axis (solar = area-polygon; wind = turbine point-cloud + hub-height attenuation), *not*
the coupling type. The exact two-stage M2 mechanism is nailed down **at M2** (no jumps), with a known-answer
check.

**Why.** A12's dual-test keeps flame as one peril; A21 row 5 dispatches solar/onshore-wind to `site_conditioned`;
the empirical disaggregation signature patterns wildfire with flood (+230%), not wind (+2%). Importing hail's
Minkowski here would be the "standard physics" error the principles forbid.

**Revisit trigger.** If a discrete-perimeter "did a regional fire reach the polygon?" use-case emerges, an
areal cross-check could be added — documented as the considered alternative, not the V1 spine.

---

## DD-W1 · V1 scope = exogenous geographic wildfire, honestly labeled; equipment-driven brushfire (+ BESS, smoke, PSPS) named as distinct deferred perils

**Date:** 2026-06-12 · **Status:** decided · Evidence: kWh 2026 (p10–12); A12 dual-test.

**Context.** kWh's >$150B loss data: fire is the #2 PV loss driver, but **84% of fire loss events are
equipment-driven on-site brushfires** (inverters 44%, DC connectors), and only **4%** fall in high-wildfire-
risk geography. Every prior model (legacy, lab, and the vendor corpus) models the *exogenous* receptor peril —
the minority of loss.

**Options.** A: exogenous-only, silently called "wildfire" (✗ dishonest by omission). B: fold equipment fire
into V1 (✗ no calibrated endogenous frequency; fails the A12 dual-test). C: exogenous V1, **honestly labeled**,
endogenous named-deferred (✓).

**Decision.** **Option C.** Build the exogenous geographic receptor model; **label it honestly** (the verbatim
label in [`00_intent`](00_intent.md) / [`01 §4`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md));
record **equipment-driven brushfire, BESS thermal runaway, smoke-soiling, and PSPS** as **distinct deferred
perils**, each able to plug into the shared engine later.

**Why.** Architecturally clean and buildable now; honest about coverage; **low-regret** (the standard interface
means deferring endogenous fire costs nothing). *Basics-spot-on* is as much about not over-claiming coverage as
about the tail computation.

**Revisit trigger.** When a calibrated endogenous (equipment) ignition-frequency model becomes feasible →
stand it up as its **own peril** (not a wildfire sub-peril), consuming the same compound-NegBin engine.
