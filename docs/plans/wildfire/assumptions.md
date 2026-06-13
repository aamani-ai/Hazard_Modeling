# Wildfire pipeline — assumptions register

Every input / simplification / curve the wildfire build rests on, tracked explicitly, by layer. `AW-*` =
wildfire-scoped (distinct from hail's `A*`). **Status** legend: `decided` · `assumed` · `to-verify` (must be
checked *during* the layer) · `deferred` (known gap, revisit later) · `confirmed` (evidence-backed).

Newest layer last. Sources: the discussion docs
([scope `01`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md),
[data dictionary `02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)).

## Scope

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| AW-1 | **V1 = exogenous geographic wildfire only** (asset as receptor); equipment-driven brushfire, BESS thermal runaway, smoke-soiling, PSPS are **distinct deferred perils** | kWh 2026; A12 dual-test; [DD-W1](decisions.md) | decided | a calibrated endogenous-ignition model is feasible |
| AW-2 | **Damage track only** — physical damage, not business interruption / contingent BI | mirrors hail's fence | deferred | financial-terms layer (deductibles/limits/BI) |

## M0 — input data

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| AW-3 | **Hazard source = public USFS rasters, fetched directly** (WRC 2.0 ImageServers + FSim RDS); **no Hydronos / no secret** | [DD-W3](decisions.md) | decided | — (owner must still rotate the leaked legacy key) |
| AW-4 | **BP is annual (unconditional); CFL / FLEP / FLP are conditional-on-fire** — annualize intensity via `× BP` | WRC 2.0 Methods; [`02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md) | confirmed | — |
| AW-5 | **BP service value ÷ 10000** (the lab's convention) gives the 0–1 annual probability | lab `wildfire_eal_layer.md`; **not** in service metadata | **verified** (M0/01 range-check: raw max 26 → 0.0026, inside [0,0.135]; CFL→ft, FLEP→[0,1] all consistent) | confirm vs the source GeoTIFF `rasterFunctionInfos` only if absolute BP magnitude becomes load-bearing |
| AW-6 | **FIL/FLP class breaks = {2,4,6,8,12} ft**; `FLEP4 = ΣFLP₃₋₆`, `FLEP8 = ΣFLP₅₊₆` (cumulative tail) | USFS-published verbatim (RDS-2020-0016 metadata; Scott 2020) | confirmed | — |
| AW-7 | **Severity histogram = native FSim FLP1-6 (270 m)**, not the WRC FLEP reconstruction | [DD-W4](decisions.md) | decided | reference asset small vs 270 m → reconsider 30 m WRC + tested reconstruction |
| AW-8 | **kW/m via Byram** `FL_m = 0.0775·I^0.46` — the SI coefficient is derived, not primary-quoted | [`02 §3`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md) | to-verify | if kW/m becomes the M3 damage-curve x-axis |
| AW-9 | **Record the exact edition/DOI** (`RDS-2016-0034-3` FSim 3rd Ed, LANDFIRE 2020) — never the loose label "WRC 2.0" | [`02 §4`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md) | decided | — |
| AW-10 | **CFL = headfire mean; FLEP/FLP = direction-integrated** — different intensity populations, do not blend | WRC 2.0 Methods (Scott 2020) | to-verify | settle which basis M2/M3 uses for asset-incident flame length |

## M1 — catalog *(stubs — detailed at M1)*

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| AW-11 | **Spatial grain = asset-boundary zonal** — real OSM/EIA plant polygons (`renewablesinfo_org/data/dimensions/boundary/powerplants_enriched_v2`, ~8.8k EIA-matched); **capacity-radius circle** (`r≈69√MW_DC`) fallback when absent | [DD-W5](decisions.md); **realized M0/01** (Matrix = real 5.0 km² MultiPolygon; Hayhurst = circle, not in dataset) | decided | localize the boundary parquet into the repo if the external symlink path is fragile |
| AW-12 | **Frequency** = annual occurrence from BP → severity draw, through the **shared compound-NegBin engine** (Bernoulli is a NegBin special case) | [`01 Decision 5`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md) | to-verify | confirm at M1; test whether multi-fire years matter at these BPs |
| AW-13 | **Stationary `λ`** (current-climate) — climate trend / `λ(t)` not modeled | mirrors hail; Verisk caps projections at 2050 | deferred | asset-life-matched (2050–60) climate conditioning |
| AW-21 | **Zonal edge-rule = `all_touched=True` + plain mean** (count any pixel the footprint touches; **no** fractional area-weighting). The edge rule is a **2nd-order lever** (≤~1% Matrix, a few % Hayhurst) — below product-choice (~2×), 270 m resolution, and damage-curve uncertainty | *basics-spot-on* (don't launder precision into a non-dominant term); [learning_logs/08](../../learning_logs/08_oozing_developed_pixels.md) | decided (v1); **check done (M1/01)** — Matrix spread 0.5–1.3% (immaterial); Hayhurst 11–30% but near-zero hazard → no decision change | adopt **area-weighting (or read at 30 m)** only for a **small footprint in a genuinely high-fire area** (few pixels AND real hazard) — the one case the edge rule swings a number that matters |

| AW-22 | **λ = −ln(1−BP)** per asset from FSim BP; **no short-record fit** (FSim pre-integrated the seasons) | [DD-W7](decisions.md); methodology §4–5 | decided · realized M1/01 | sub-annual occurrence model needed |
| AW-23 | **Single-site `fano = 1`** — dispersion lives inside FSim BP; no annual-count series to test (structural, not measured) | [DD-W7](decisions.md) | decided (structural) | multi-fire-year clustering / portfolio correlation |
| AW-24 | **Severity = 6 discrete FLP classes** on Byram kW/m; FIL6 "12+ ft" open-ended → 15 ft midpoint (coarse) | M1/01; data-dictionary §3 | decided (v1) | EVT / continuous-tail severity (deep return periods) |

## M2 — coupling *(stubs — detailed at M2)*

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| AW-14 | **Coupling = site-conditioned** (bucket 3), same row solar & wind | [DD-W2](decisions.md) | decided | discrete-perimeter use-case → add areal cross-check |
| AW-15 | 🔴 **Solar-site "oozing":** WRC oozes BP into developed pixels but **suppresses intensity** there — so on-site hazard derives from **surrounding fuel**, not the asset pixel | WRC 2.0 Methods ("FLEP4 was not oozed into developed areas") | **CONFIRMED real & ASSET-SPECIFIC** (M0/01: Hayhurst array pixel oozed — BP=5e-4, intensity=0; **Matrix NOT oozed** — real intensity at the pixel). Depends on whether the array is mapped developed — **M2-critical** | M2 must **detect oozing per-asset** and, where present, source on-site hazard from the surrounding-fuel footprint, not the asset pixel (the Hydronos `analysis="buffer_ring"` mode is a ready tool for the boundary ring — see `02b`) |
| AW-16 | **Fixed `d = 10 m`** (line-source `1/d`); imagery-derived `d`/fuel deferred to V1.5+ | [DD-W6](decisions.md) | decided | imagery / owner site layout available |
| AW-17 | **Doc fix:** `infrasure-damage-curves/docs/hazard-intensity-variables.md` writes `q∝I/d²` (point source) — wrong for a fire front; pin to `1/d` | [`01 §7`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md) | to-verify | fix before any heat-flux modeling (M3) |

| AW-25 | 🟡 **We consume a STALE pre-computed simulator OUTPUT, not a live run.** FSim/WRC rasters are a LANDFIRE fuel-vintage *snapshot* (BP ≈ end-2020, intensity ≈ end-2022); we do **not** run FSim on current fuels. Hazard "ages fast" — USFS re-runs every 1–2 yr | Hazard-Data-Ref (wildfire: *"don't treat a hazard map as stationary"*) | **assumed (V1)** — record the exact vintage; treat as a non-stationary snapshot | the currency adjustment (AW-26) is built |
| AW-26 | **Currency / recency adjustment** — the ideal (even approximate) fix for AW-25: an adjustment factor for vegetation change *since* the vintage (recent burn scars, fuel treatment, regrowth), e.g. an MTBS recent-burn + WFIGS overlay onto the stale BP/intensity | owner steer; the lab's documented currency-update plan | **deferred** | post-vintage fuel change materially moves a site's hazard |
| AW-27 | **Explicit site-feature susceptibility** (defensible space, fences / fire breaks, vegetation management, cleared land) → maps to the heat-flux **distance `d`** (more clearance → larger effective `d` → curve thresholds shift *up*, less damage). V1 **embeds** the curve's `d = 10 m`; explicit per-site `d` from site data / imagery is deferred | damage-curve `hazard-intensity-variables.md` (*"larger defensible space → thresholds shift up"*); [AW-16](#m2--coupling-stubs--detailed-at-m2) | **deferred** (V1 embeds `d=10 m`) | site layout / imagery available (Decision 4; Gen 2+) |
| AW-28 | **V1 coupling cut = intensity (kW/m) with `d`/duration EMBEDDED in the curve; no fire-front sweep** → whole-site exposure on a fire; **EAL ≈ right, but PML/tail smoothed** (partial-burn + contiguous-front correlation not modeled) | legacy Gen-2 spatial-correlation discussion; methodology §9 | **decided (V1)** | fire-front sweep (partial burn, explicit `d`/`t`, real tail) — Gen 2+ |

## M3 — damage *(stubs — detailed at M3)*

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| AW-18 | **BoS-weighted** logistic MDR on kW/m, curves from `infrasure-damage-curves` (Low/Very-Low confidence, zero empirical RE calibration) | competitive research (vulnerability is greenfield); [`01 §9`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md) | deferred (curve revamp) | damage-curve library calibration improves |
| AW-19 | **30% unmodeled solar TIV** — library solar subsystem weights sum to 0.70 | `infrasure-damage-curves` | **decided (v1): non-damageable** ([DD-W8](decisions.md)); anchored cap ≈ 0.56 of TIV | revisit at the curve revamp (classify the 30% / add subsystems) |
| AW-20 | **TIV valuation basis unconfirmed** (same caveat as hail A19) — report % of TIV alongside dollars; Matrix TIV estimated via $1483/kWp (no registry TIV) | asset registry | to-verify | TIV basis re-sourced/labeled |
| AW-29 | **Damage curve anchored** — subtract each subsystem's `DR(0)` so `DR(0)=0`. The canonical *raw* logistics give a **non-physical** ~5% DR at zero intensity (`k·x0 ≈ 1.5–2.7` not sharp); it dominated the low-fire conditional loss (Hayhurst 5.8%→1.0%). Matches the legacy 'anchored logistic' | [DD-W8](decisions.md); M3/01; legacy precedent | decided (v1) | the curve revamp ships sharper thresholds (floor won't arise) |
