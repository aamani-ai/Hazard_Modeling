# 02 — FSim / WRC Wildfire Data Dictionary

*A from-scratch "what is this dataset" reference, verified against authoritative USFS sources (web) **and**
the raw resources on disk, before we touch M0. Every layer: plain-English meaning, formal definition, units,
resolution, vintage, confidence, gotchas. This is the data we'd build the wildfire hazard surface from — so
we understand it exactly, not approximately. (The exploratory-notebook practice, applied to the source data.)*

> **Method.** Findings below were cross-checked by 4 source-readers (official WRC Methods white paper, the
> USFS Research Data Archive metadata, FSim/FlamMap/LANDFIRE docs, the live ArcGIS ImageServer metadata) and
> an adversarial verifier that tried to *refute* the surprising claims. Confidence is marked honestly; every
> load-bearing fact carries a citation.

---

## TL;DR

1. **"WRC/FSim" is actually TWO product lines** that get dangerously lumped together. Know which you're using.
2. **FLEP4 = FLP3+FLP4+FLP5+FLP6 and FLEP8 = FLP5+FLP6 — CONFIRMED, and it's a *verbatim-published USFS
   equation*** (not a legacy guess). It's a cumulative *tail* probability; the bins break exactly at 4 ft and
   8 ft, which are the hand-crew and equipment **fire-suppression limits**.
3. **BP is the only annualized layer.** CFL, FLEP4, FLEP8, FLP1-6 are **all conditional-on-fire** — you
   multiply by BP to annualize. (Getting this wrong = the kind of frame error our principles forbid.)
4. **Decision 6 resolved: native FLP1-6 *is* publicly fetchable** (FSim line, 270 m) — so we can avoid the
   lossy WRC reconstruction. That's the recommended severity source.
5. **A solar-specific landmine:** WRC "oozes" BP into developed/non-burnable pixels but **suppresses intensity
   there** — so a PV array mapped as "developed" may carry BP but *zero* on-pixel flame length. On-site hazard
   likely has to come from *surrounding* fuel. This will shape M2.

---

## 1. The two product lines (don't conflate them)

```text
        USDA Forest Service wildfire-modeling stack
        ───────────────────────────────────────────
  ┌──────────────────────────────┐     ┌──────────────────────────────────┐
  │ (C) FSim Probabilistic        │     │ (A/B) Wildfire Risk to Communities │
  │     Wildfire Risk             │     │      (WRC) — wildfirerisk.org      │
  │  RDS-2016-0034 series         │     │  RDS-2020-0016 series              │
  │                               │     │                                    │
  │  NATIVE simulator output       │ ──▶ │  RISK-COMMUNICATION product        │
  │  • BP                          │     │  • BP (upsampled)                  │
  │  • FLP1-6  (full histogram)    │     │  • CFL, FLEP4, FLEP8  ← COLLAPSED   │
  │  270 m                         │     │  • WHP, RPS/cRPS, Exposure         │
  │                               │     │  30 m   (NO FLP1-6 histogram)      │
  └──────────────────────────────┘     └──────────────────────────────────┘
```

- **FSim Probabilistic Wildfire Risk** (`RDS-2016-0034` series) — the **native** Monte-Carlo simulator output
  (Finney et al. 2011): Burn Probability **+ the full six-class flame-length histogram FLP1-6**, at **270 m**.
  *The only place FLP1-6 is published as standalone rasters.* 3rd Edition = `RDS-2016-0034-3` (Dillon et al.
  2023, LANDFIRE 2020).
- **Wildfire Risk to Communities** (`RDS-2020-0016` series; the wildfirerisk.org site + the
  `imagery.geoplatform.gov` ImageServers the lab uses) — a risk-communication product that **collapses** the
  intensity histogram into summary metrics **CFL, FLEP4, FLEP8** (+ BP, WHP), at **30 m**. **Never publishes
  FLP1-6.** 1st Ed = `RDS-2020-0016` (LANDFIRE 2014); 2nd Ed ("V2.0") = `RDS-2020-0016-2` (LANDFIRE 2020).

> **Rule for M0:** pin the exact **DOI + edition string** in metadata, never the loose label "WRC 2.0" —
> vintage, resolution, and provenance all differ by edition.

---

## 2. Per-product data dictionary

| Layer | Plain English | Conditioning | Units | Native res | Confidence |
|---|---|---|---|---|---|
| **BP** Burn Probability | annual chance a spot burns | **annual (unconditional)** | probability 0–1 /yr | **270 m** (FSim) | ✅ CONFIRMED |
| **CFL** Conditional Flame Length | mean *headfire* flame length **if** it burns | conditional-on-fire | **feet** | 30 m (WildEST) | ✅ CONFIRMED |
| **FLEP4** | P(flame > 4 ft **if** it burns) | conditional-on-fire | probability 0–1 | 30 m | ✅ CONFIRMED |
| **FLEP8** | P(flame > 8 ft **if** it burns) | conditional-on-fire | probability 0–1 | 30 m | ✅ CONFIRMED |
| **FLP1-6** | 6-bin flame-length histogram given a fire | conditional-on-fire (Σ=1) | 6 probs summing to 1 | **270 m** (FSim) | ✅ CONFIRMED |
| **WHP** Wildfire Hazard Potential | ordinal "hard-to-control" **index** | index (neither) | **ordinal class** | 30 m | ✅ (an index) |

**BP — Burn Probability.** *"a 30-m raster representing the circa-2021 annual likelihood of burning"* (WRC 2.0
Methods). FSim runs ≥20,000 fire seasons across 136 pyromes, calibrated to the 1992–2020 record. **The only
already-annualized layer.** Non-burnable pixels = 0. ⚠️ The lab divides the U16 service value by **10000**
(observed max 1352 → ~0.135) — this divisor is **the lab's convention, NOT in the service metadata**; validate
against the source GeoTIFF before trusting absolute BP magnitude.
[[WRC Methods]](https://wildfirerisk.org/wp-content/uploads/2024/05/WildfireRiskToCommunities_V2_Methods_Landscape-wideRisk.pdf) · [[RDS-2020-0016-2]](https://www.fs.usda.gov/rds/archive/products/RDS-2020-0016-2/_metadata_RDS-2020-0016-2.html)

**CFL — Conditional Flame Length.** *"mean **headfire** flame length at a location if a fire were to occur"* —
a weather-weighted mean over 216 WildEST runs (9 wind-speed × 8 wind-direction × 3 fuel-moisture). Units =
**feet**. ⚠️ Two traps: (a) the popular site calls it "most likely" FL; the **Methods paper says *mean*** —
use mean. (b) CFL is **headfire-only**; FLEP integrates non-heading (backing/flanking) directions — *different
intensity populations, do not blend them.*

**FLEP4 / FLEP8 — Flame-Length Exceedance Probabilities.** *Conditional* (given a fire) probabilities that
flame length exceeds **4 ft** / **8 ft**. See §3 for the relationship and the suppression meaning. ⚠️ Nested
tails: `FLEP8 ≤ FLEP4` always.

**FLP1-6 — the six-class histogram.** *"of all simulated fires that burned a cell, the proportion in each
flame-length class … the six FLP layers sum to 1"* (`RDS-2016-0034-3`). Class breaks in §3. Published only in
the **FSim line at 270 m**; in WRC it exists only as an unpublished 30-m internal.

**WHP — Wildfire Hazard Potential.** An **ordinal index** (Very Low → Very High) integrating likelihood +
intensity + extra factors, built to prioritize fuel treatments. ⚠️ **It is not a probability and not a loss —
never multiply or annualize it.** For a loss pipeline, prefer explicit **BP × intensity** over WHP.

---

## 3. The FIL ↔ FLEP relationship — your question, answered ✅

**Yes: `FLEP4 = FLP3 + FLP4 + FLP5 + FLP6` and `FLEP8 = FLP5 + FLP6`.** And this is not a derivation we
inferred — it's a **verbatim-published USFS equation.** The `RDS-2020-0016` archive metadata literally states
`FLEP4 = FPL3 + FLP4 + FLP5 + FLP6` (sic — USFS typo, `FPL3` = `FLP3`) and `FLEP8 = FLP5 + FLP6`.

**Why it's a *sum* (the intuition):** FLEP is a **cumulative tail** (survival) probability. The six FLP classes
are a histogram of flame length that sums to 1; "exceeds 4 ft" = the total probability mass in every class
above the 4-ft line. It's exact because the class breaks fall **precisely** on 4 ft and 8 ft:

```text
flame length:   0 ──── 2 ──── 4 ──── 6 ──── 8 ──── 12 ────▶ ft
class:          │ FIL1 │ FIL2 │ FIL3 │ FIL4 │ FIL5 │ FIL6 │
                              ▲                ▲
                            4 ft             8 ft
                       FLEP4 break        FLEP8 break
                   (limit of MANUAL    (limit of MECHANICAL
                    / hand-crew control)   control — ceiling)

FLEP4 = P(FL > 4 ft) = FLP3 + FLP4 + FLP5 + FLP6   (everything right of 4 ft)
FLEP8 = P(FL > 8 ft) =               FLP5 + FLP6   (everything right of 8 ft)
```

**The 4 ft / 8 ft thresholds are real fire-suppression limits** — CONFIRMED in the WRC Methods paper (*"four
feet (FLEP4; the limit of manual control), eight feet (FLEP8; the limit of mechanical control)"*) and in the
canonical Andrews et al. **RMRS-GTR-253** "Hauling Chart" (Table 1): `<4 ft` → hand crews hold the line;
`4–8 ft` → too intense for hand crews, **but dozers/engines/aircraft can be effective**; `8–11 ft` → head
control "probably ineffective." Nuance worth recording: **8 ft is the *ceiling* of equipment effectiveness,
not where equipment starts** — equipment works in the 4–8 ft band.

### The verified FIL / FLP class table

Boundaries are **half-open intervals in feet** (exactly-4 ft → FIL3; exactly-8 ft → FIL5), verbatim across
three independent USFS pages. Metric values are exact conversions; the **kW/m column is approximate** (derived
via Byram `FL_m = 0.0775·I^0.46`; the SI 0.0775 coefficient is standard/derived, *not* primary-quoted).

| Class | Flame length (ft) | (m) | ≈ Fireline intensity (kW/m) *(approx)* | Suppression (GTR-253) |
|---|---|---|---|---|
| FIL1 | < 2 | < 0.61 | < ~50 | hand crews hold |
| FIL2 | 2–4 | 0.61–1.22 | ~50–220 | hand crews hold |
| *— 4 ft = FLEP4 break (manual-control limit) —* | | | | |
| FIL3 | 4–6 | 1.22–1.83 | ~220–520 | equipment effective |
| FIL4 | 6–8 | 1.83–2.44 | ~520–960 | equipment effective |
| *— 8 ft = FLEP8 break (mechanical-control ceiling) —* | | | | |
| FIL5 | 8–12 | 2.44–3.66 | ~960–2,400 | head control ~ineffective |
| FIL6 | 12+ | > 3.66 | > ~2,400 | crowning/spotting |

[[RDS-2016-0034]](https://www.fs.usda.gov/rds/archive/products/RDS-2016-0034/_metadata_RDS-2016-0034.html) · [[Scott 2020 FLEP-Gen]](http://pyrologix.com/wp-content/uploads/2019/11/Scott%202020%20FLEP-Gen.pdf) · [[GTR-253 Table 1]](https://www.fs.usda.gov/rm/pubs/rmrs_gtr253.pdf)

> ⚠️ **The tail-sum identity is exact only *within one edition/model*.** A WRC-2.0 30-m FLEP must **not** be
> paired with a different-vintage/different-model FSim 270-m FLP histogram and assumed exact. (This is exactly
> the trap our legacy-vs-lab comparison in [`01 §6`](01_v1_scope_and_framing.md) walked into.)

---

## 4. WRC editions & the vintage split

| Identity | DOI / archive | Landscape vintage | Resolution | Publishes |
|---|---|---|---|---|
| WRC 1st Ed | `RDS-2020-0016` | LANDFIRE 2014 | 30 m | BP, CFL, FLEP4/8, WHP, RPS *(no FLP1-6)* |
| **WRC 2nd Ed ("V2.0")** | `RDS-2020-0016-2` | LANDFIRE 2020 | 30 m | same 8 rasters *(no FLP1-6)* |
| **FSim 3rd Ed** | `RDS-2016-0034-3` | LANDFIRE 2020 | **270 m** | **BP + FLP1-6 histogram** |

The **WildEST/FlamMap switch happened in WRC 2nd Ed**: 1st-Ed intensity came from FSim flame-length results;
2nd Ed *"did not use FSim's flame-length probability results — instead, we used WildEST … at the native 30-m
resolution."* This creates a **vintage split inside WRC 2.0** the Methods paper itself flags:

- **BP** = circa-2021 (FSim, 270 m native, **upsampled** to 30 m → effective info content is still 270 m).
- **CFL / FLEP4 / FLEP8** = circa-2023 (WildEST, native 30 m, fuels end-2022).

> So "WRC 2.0 at 30 m" is **not one coherent vintage** — its BP and its intensity are ~2 years and one
> resolution-pathway apart.

---

## 5. Decision 6 — RESOLVED: fetch native FLP1-6, skip the reconstruction

**Native FLP1-6 *is* publicly available** (HIGH confidence) — we are **not** stuck reconstructing from WRC's
collapsed FLEP4/8. Two routes to the same product, no auth, no fee, CC BY 4.0:

1. **USFS Research Data Archive GeoTIFFs** — `RDS-2016-0034-3` (FSim 3rd Ed): ships standalone
   `{CONUS,AK,HI}_FLP1.tif … FLP6.tif` + `_BP.tif` (21 GeoTIFFs), 270 m, LANDFIRE 2020.
   [[metadata]](https://www.fs.usda.gov/rds/archive/products/RDS-2016-0034-3/_metadata_RDS-2016-0034-3.html)
2. **Live ArcGIS ImageServers** under the USFS `RDW_Wildfire` folder (per-class `…_FLP6_CONUS/ImageServer`,
   etc.) — corroborated public via the data.gov catalog.

**The trade-off (this is what Decision 6 actually is):**

| | Native **FLP1-6** (FSim line) — *recommended* | WRC 30-m FLEP path |
|---|---|---|
| Severity info | **full 6-class histogram, no loss** | only `{CFL, FLEP4, FLEP8}` → 6-bin reconstruction is **under-determined / lossy** |
| Vintage | **single, clean** (BP + histogram same 270-m FSim product) | **split** (BP end-2020 / intensity end-2022) |
| Resolution | 270 m | 30 m (but BP is upsampled 270 m anyway) |

For solar — panel arrays are large relative to fuel-pixel scale — **270 m native FLP1-6 is very likely
sufficient and is the cleaner, single-vintage, loss-free choice.** ⛔ **Avoid the legacy lab's reconstruction
heuristics** (`P(FL>2)=min(1.45·FLEP4,1)`, `P(FL>6)=√(FLEP4·FLEP8)`, `P(FL>12)=FLEP8^1.5/FLEP4^0.5`) — they
have **no cited provenance** and the lab itself documents them as approximations. If the 30-m path is ever
forced, register the reconstruction as an assumption and sensitivity-test it.

---

## 6. Gotchas that will bite M0 / M2 (read before coding)

1. **Conditional vs annual.** BP is annual; CFL/FLEP/FLP are **conditional on a fire**. To annualize anything
   intensity-related you multiply by BP. Never treat a FLEP as an annual probability.
2. **🔴 Solar-site "oozing."** WRC oozes BP into developed/non-burnable pixels **but suppresses intensity
   there** (*"FLEP4 was not oozed into developed areas"*). A PV array / gravel-pad site mapped as developed
   will carry BP but **little/no on-pixel CFL/FLEP** → on-site hazard likely must be derived from the
   **surrounding fuel**, not the asset pixel. **Confirm land-cover treatment of solar sites before M2.**
3. **BP scale divisor unverified.** The `/10000` is the lab's convention, not metadata — validate against the
   source GeoTIFF. (`FLEP /1000` and `CFL ×1 = ft` *are* consistent with the U16 ranges.)
4. **Headfire vs direction-integrated.** CFL = headfire (max-spread); FLEP/FLP integrate all directions. Decide
   which basis M2/M3 uses for asset-incident flame length; don't silently mix.
5. **WHP is an index, not a probability.** Don't feed it into loss math.
6. **kW/m is approximate.** If intensity (kW/m) becomes the M3 damage-curve x-axis, confirm the SI Byram
   coefficient `0.0775` against a FlamMap/BehavePlus primary source.

---

## 7. Open uncertainties → things to verify *during* M0

- [ ] **BP `/10000` divisor** — confirm against the downloadable GeoTIFF / `rasterFunctionInfos`.
- [ ] **Byram SI coefficient `0.0775`** — confirm against a primary source if kW/m is the M3 axis.
- [ ] **Solar-site land cover** — how do WRC/LANDFIRE treat PV arrays? (the oozing gotcha) — *decides M2*.
- [ ] **Exact edition/DOI to pin** — `RDS-2016-0034-3` (histogram, 270 m) vs `RDS-2020-0016-2` (WRC, 30 m).
- [ ] **WHP class breaks/formula** — only if WHP is actually used (recommend not, for loss).
- [ ] **CFL vs FLEP geometry basis** — settle the headfire-vs-integrated choice at M2.

---

## Sources (authoritative)

- **WRC 2.0 Methods white paper** (Scott, Dillon, Callahan et al. 2024) — definitions, suppression limits, the WildEST switch, the vintage split. <https://wildfirerisk.org/wp-content/uploads/2024/05/WildfireRiskToCommunities_V2_Methods_Landscape-wideRisk.pdf>
- **USFS RDS archive** — `RDS-2020-0016` / `-2` (WRC; the verbatim FLEP equations) · `RDS-2016-0034` / `-3` (FSim; FLP1-6 + class breaks). <https://www.fs.usda.gov/rds/archive/products/RDS-2020-0016/_metadata_RDS-2020-0016.html>
- **Scott 2020, FLEP-Gen** (Pyrologix) — FIL bin breaks + the FLP↔FLEP construction. <http://pyrologix.com/wp-content/uploads/2019/11/Scott%202020%20FLEP-Gen.pdf>
- **Andrews et al. RMRS-GTR-253** — the Hauling Chart (suppression interpretation of flame length). <https://www.fs.usda.gov/rm/pubs/rmrs_gtr253.pdf>
- **Live ImageServer metadata** (`imagery.geoplatform.gov/.../USFS_EDW_RMRS_WRC_*`) — U16 ranges + the lab's fetch path.
- Raw on-disk: `_legacy_wildfire/docs/.../fsim_data_guide.md` (conflates the two product lines — corrected here) · `wildfire_analysis_lab/docs/methodology/{grid_resolution_and_source_caveats,wildfire_eal_layer}.md`.

---

*Next: fold the confirmed facts (esp. the solar-site oozing question and the native-FLP1-6 source) into
`docs/plans/wildfire/` when M0 planning opens. Nothing here is built — this is the dataset understood on
paper, as agreed, before M0.*
