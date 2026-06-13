# 01 — Wildfire × Solar V1: Scope & Framing

*A discussion doc, not a plan. It exists to settle **what V1 actually models** before we open M0. Every
section ends with a decision; the owner's calls turn into `DD-*` / `A-*` rows in `docs/plans/wildfire/`.*

---

## TL;DR (the whole argument in one screen)

1. **Three prior wildfire artifacts** exist. We **mine them for info and data plumbing, and rebuild all
   the loss math** — same stance the rebuild took everywhere.
2. **The kWh 2026 data reframes the problem.** Fire is the **#2 loss driver** on utility-scale solar, but
   **84% of fire *loss events* are equipment-driven brushfires that ignite *on-site*** — and only **4% of
   fire loss events** fall in high-wildfire-risk geography. Every existing model (ours and the vendors')
   models the *other* ~16%: **exogenous** wildfire reaching the site.
3. **The V1 decision is therefore as much about honesty as about math.** Recommended: build the exogenous
   geographic model (it's clean, public-data, and matches the architecture) but **label it honestly** and
   **name equipment-driven brushfire as a distinct, deferred peril** — don't let a 16%-of-loss number
   masquerade as "solar fire risk."
4. **Wildfire is coupling bucket 3 — site-conditioned** (field × per-asset susceptibility), the *same
   family as flood*, **not** hail's areal hit-or-miss. Same coupling row for solar *and* wind; the
   solar/wind difference lives on the **exposure-geometry** axis.
5. **Data source:** public **WRC 2.0 + WHP** rasters via the `wildfire_analysis_lab` download scripts —
   **no API, no secret**. But sample at the **asset boundary**, not the lab's 0.25° screening cell.
6. **Site-conditioning for V1:** a defensible proxy (boundary BP + LANDFIRE fuel + fixed `d=10 m` + wind
   hub-height attenuation). **Imagery-derived site conditions = V1.5+**, not a V1 dependency.
7. **The wedge:** no incumbent has renewable-specific wildfire *vulnerability* curves. Our **BoS-weighted
   damage curves on a public hazard substrate** is the differentiator.

---

## 1. Where we are, and why we're talking first

Hail × solar is built end-to-end (`Notebooks/hail/` shared catalog → `hail/solar/` M2–M4). Wildfire mirrors
that shape. But unlike hail — where the physics was novel but the *scope* was obvious — wildfire has a
**scope trap** baked into it by the data, so we settle scope here before writing M0.

The principles that decide the ties:

- **Basics spot-on** — *the math is the product* — but also: **don't over-claim coverage.** A correct tail
  on the wrong-labeled peril is still a credibility failure, which is exactly the kind of thing this rebuild
  exists to escape.
- **Standard interface, not standard physics** — wildfire gets its *own* coupling physics behind the *same*
  typed interface; that's what lets us **defer** the harder fire pathway at zero architectural cost.
- **Modular from day one** — the shared compound-NegBin Monte Carlo loss engine **does not change**.

---

## 2. The three prior artifacts (what each gives us)

| Artifact | What it is | What we KEEP | What we REBUILD / RETIRE |
|---|---|---|---|
| **(a) `_legacy_wildfire`** (temp symlink) | Old per-asset closed-form EAL via the paid **Hydronos "Wildfire Risk API"** | Asset-geometry resolution (`polygon / point+radius=69·√MW / centroid`), the FIL→Byram intensity bridge, proof the API is just a hosted layer over **public FSim** BP + flame-length | The **leaked hard-coded API key** (`wildfire_eal_pipeline.py:39`, in git history — **rotate**); the **cardinal-error tail** (fit lognorm/gamma/weibull to 6 expected-loss points); wind **mean-collapsing** 126 turbines |
| **(b) `wildfire_analysis_lab`** | Clean **public-data** cousin: WRC 2.0 + WHP → solar/wind EAL `$/kWp/yr` | **No-auth, CC BY 4.0 download/sampling plumbing** for WRC 2.0 (BP, Conditional Flame Length, FLEP4, FLEP8) + WHP 2023; the Byram + capital-weighted logistic damage math; the honest source-caveat docs | The **0.25° (~500–700 km²) cell-mean** grain; the **analytic 7-atom screening tail** (*not* the cardinal error — it anchors to EAL correctly — but **not** a sampled compound-frequency MC either) |
| **(c) kWh 2026 Solar Risk Assessment** | Industry loss evidence (>$150B of renewable loss data) | The **honest-labeling forcing function** (see §3) | — (it's evidence, not a model) |

> **Verdict, all three:** mine the info + the public data plumbing, rebuild every piece of loss math.

---

## 3. The central tension — exogenous vs endogenous fire

Here is the uncomfortable fact, straight from kWh (p10–12) and corroborated by the competitive research:

```text
PV fire loss, by where it actually lands
─────────────────────────────────────────────────────────────
 ~84% of fire EVENTS  →  EQUIPMENT-DRIVEN on-site brushfire
                          (inverters 44% of all PV fires;
                           DC connectors / combiner boxes;
                           junction-box defects ~30% of mfrs)
                          → the PLANT is the IGNITION SOURCE

 ~16% of fire EVENTS  →  geographic / wildland WILDFIRE
   (only 4% of loss      reaching the site
    events in USDA       → the PLANT is the RECEPTOR / victim
    high-risk geography)
─────────────────────────────────────────────────────────────
Severity either way: 0–80% of asset value, driven by SITE DESIGN
(spacing, firebreaks, vegetation mgmt, O&M) — not the ignition spark.
```

Every model we have — legacy (a), lab (b), **and the entire vendor corpus** (RMS, Verisk, First Street,
CLIMADA) — models the **exogenous receptor** peril. That captures the *minority* of where the dollars land.

The two fires are **different perils**, not two settings of one model:

| | Exogenous wildfire | Endogenous equipment brushfire |
|---|---|---|
| Ignition | fuel + weather + geography | equipment population / age / **manufacturer** |
| Frequency driver | burn-probability field (FSim) | installed-base reliability (no public per-site data) |
| Plant's role | **receptor** | **source** |
| Data we have | WRC 2.0 / WHP rasters ✅ | kWh *aggregates only* — no per-site calibration ❌ |

By our own **A12 dual-test** (distinct footprint **and** distinct data metric → split), endogenous fire is a
**separate peril**, not a wildfire sub-peril.

---

## 4. The V1 scope options

| | Option | Verdict |
|---|---|---|
| **A** | Exogenous geographic wildfire only, **silently** called "wildfire risk" | ❌ **Reject.** Math could be right, **label is wrong** — silently presents a ~16%-of-loss model as total fire risk. Repeats the old model's credibility problem in a new costume. Fails *basics-spot-on* on the honesty axis. |
| **B** | Broaden V1 to fold equipment-driven brushfire *into* wildfire | ❌ **Reject.** Forces two incompatible frequency models into one peril; we have **no calibrated endogenous frequency** (only kWh aggregates). Fails the A12 dual-test and *basics-spot-on*. |
| **C** | **Exogenous geographic wildfire, HONESTLY LABELED, with equipment-driven brushfire NAMED as a distinct deferred peril** | ✅ **Recommended.** Clean, buildable now, reuses the lab M0 plumbing, matches A12/A20/A21 and the vendor corpus, **honest about coverage**, and **low-regret**: the standard interface means deferring endogenous fire costs us *nothing* architecturally. |

### The honest V1 label (proposed verbatim for the scope doc + `DD-*`)

> *Wildfire × Solar V1 models **exogenous geographic (wildland) wildfire only** — the asset as a **receptor**
> of a landscape fire that reaches it. Magnitude = WRC 2.0 burn probability × fire-line-intensity (kW/m)
> severity, sampled per asset and aggregated through the shared compound-NegBin Monte Carlo. Per the kWh
> 2026 Solar Risk Assessment this captures the **minority** of PV fire loss: ~84% of PV fire events are
> **equipment-driven on-site brushfires** (inverters, DC connectors, junction boxes) and only ~4% of fire
> loss events occur in high-wildfire-risk geography. **Equipment-driven brushfire is a distinct, deferred
> peril** with an endogenous ignition/frequency process; **BESS thermal runaway, smoke-soiling, and PSPS**
> are further distinct deferred channels. V1 does **not** claim to cover total PV fire risk.*

> **DECISION 1 (gating).** Adopt Option **C** and lock the label above? *(Recommended: yes.)*

---

## 5. The coupling — bucket 3, site-conditioned (same row, solar and wind)

Wildfire is **site-conditioned** (field × per-asset susceptibility) — the flood family, **not** hail's
Minkowski hit-or-miss. Full background: [`../gpt/03`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md).
Confirmed by the architecture A-series: **A21 dispatch row 5** sends wildfire → `site_conditioned` for
solar/wind/BESS; **A20** fixes the M0→M1 ontology as a **fire-perimeter polygon + internal raster overlays**
(BP / fire-line intensity).

The nuance worth internalizing (and a likely learning-log):

- **"Fire perimeter" is the M1 *ontology* (the event's identity); "site-conditioned" is the M2 *coupling*.**
  These are not in conflict — they're different stages. **Do not** import hail's `(√F+√s)²/A` here; wildfire's
  magnitude is `burn-probability × fire-line-intensity`, an intensity-field-×-probability quantity, **not** a
  footprint area `F`.
- **Solar and wind share the coupling row** (unlike hail, where they split). The difference moves to the
  **exposure-geometry** axis: solar = area-polygon (aggregate susceptibility over the array); wind = sparse
  turbine points where the dominant physics is **hub-height attenuation** (surface fire at ground vs nacelle
  at 80–130 m → near-immune except tower base / ember-on-blade / crown fire).

We **don't finalize the M2 mechanism here** — that happens *at M2*, after M0/M1, with a known-answer check.

> **DECISION 2.** Confirm site-conditioned (bucket 3) as the committed coupling family, with the
> perimeter=ontology / site-conditioned=coupling nuance recorded? *(Recommended: yes — corroborated A12→A21.)*

---

## 6. Data source — public rasters, sampled at the asset boundary

| Candidate | Call | Why |
|---|---|---|
| Hydronos "Wildfire Risk API" (legacy) | ❌ **Reject** | Just a hosted layer over public FSim; adds cost, rate limits, vendor lock-in, and a **leaked-key liability**. New pipeline has **no secret dependency**. |
| **WRC 2.0 via the lab's public scripts** | ✅ **Use** | 5 layers (BP, Conditional Flame Length, FLEP4, FLEP8, WHP 2023) from `imagery.geoplatform.gov` ArcGIS `exportImage`, **no auth, CC BY 4.0**. Battle-tested tiling + gotchas (12-tile 4×3 CONUS grid in EPSG:3857; **size 4096 except FLEP4/FLEP8 must be 2048** — service returns blank tiles at 4096; scale BP/10000, FLEP/1000, CFL ×1 feet, WHP raw). |
| RDS-2020-0016 | 📎 **Cite** | The same WRC/FSim data as a **citable USFS archive product** — use as the provenance anchor in `docs/references` + assumptions; the ImageServer endpoints stay the practical fetch path. |

**The real resolution decision.** The lab samples to a **0.25° cell mean (~500–700 km²)** — its own caveat
doc calls a cell "a regional screening unit, not a project boundary." We are **site-conditioned**, so V1
should sample WRC **at the asset boundary** (zonal stats within `asset_boundary`), with a
**capacity→radius circle** (`r ≈ 69·√(MW_DC)` m) fallback. This is the cleanest step up from the lab and the
correct bucket-3 grain. *(Boundary geometry is populated for **41/64 assets = 64%**: 21/38 solar, 20/25 wind —
fallback handles the rest. Distinguish "no CONUS coverage" from "genuinely zero risk" — the legacy silently
mapped null BP → 0.)*

### Tested — are the legacy and lab the *same* data? (provenance check, 2026-06-12)

**Short answer: same burn-probability lineage, *different* flame-length product.** Compared the two legacy
assets with cached values against the lab's WRC 2.0 grid cell at the same location:

| | `altavista_solar` (VA) | `bakersfield_111` (CA) |
|---|---|---|
| **BP** — legacy FSim (asset) | 5.24 × 10⁻⁴ | 2.70 × 10⁻³ |
| **BP** — lab WRC 2.0 (0.25° cell mean) | 3.42 × 10⁻⁴ (0.65×) | 4.89 × 10⁻⁴ (0.18×) |
| **BP** — lab cell **max** | 1.0 × 10⁻³ ✅ brackets | 5.7 × 10⁻³ ✅ brackets |
| **P(FL > 4 ft \| fire)** — legacy (implied) | 0.119 | 0.519 |
| **P(FL > 4 ft \| fire)** — lab FLEP4 | 0.048 | 0.006 |

- **BP = same FSim foundation.** The lab cell-mean runs lower only because a 0.25° cell (~600 km², thousands
  of pixels) averages over mostly-non-burning area while the asset sits in a higher-BP pocket — the lab cell
  **max brackets the legacy value in both cases.** (Minor vintage caveat: legacy = FSim **3rd Edition 2023**;
  WRC BP foundation = end-2020 fuels.)
- **Flame length = different product + representation.** Legacy (FSim 3rd Ed via Hydronos) carries the full
  **6-class FLP1-6** histogram; WRC 2.0 ships only **FLEP4 + FLEP8 + CFL** (WildEST/FlamMap). The legacy docs
  prove the relationship is a **one-way lossy collapse**: `FLEP4 = P(FIL 3+4+5+6)`, `FLEP8 = P(FIL 5+6)` —
  FLP1-6 → FLEP4/8 exactly, but **not back.** That's *why* the lab must **reconstruct** FLP6 from FLEP4/8
  (r = 0.948 approximation) — the #1 severity-side uncertainty.
- The bakersfield intensity gap (0.519 vs 0.006) **compounds two causes**: grain (a single 270 m point vs a
  600 km² cell mean) **and** edition (FSim 3rd Ed FLP vs WRC 2.0 WildEST FLEP). With n = 2 and no raw rasters
  on disk, we can't fully separate them — a pixel-level raster comparison would. *(n = 2, directional.)*

**Implication.** WRC 2.0 (public, current) stays the recommended source, but on that path we **inherit
FLEP4/8 + CFL, not FLP1-6**, so the lossy reconstruction is unavoidable — *unless* we source the native
**FSim 3rd-Ed FLP1-6 rasters** directly (also public USFS), which preserve the full histogram and skip the
reconstruction. That trade-off now feeds Decision 6. And we must **never splice legacy FLP1-6 with WRC 2.0
FLEP** — different editions/engines, "not mixable."

> **DECISION 3.** WRC 2.0 (public) sampled **at the asset boundary**, RDS-2020-0016 as the citation,
> Hydronos retired? *(Recommended: yes — with the flame-length source itself decided in Decision 6.)*

---

## 7. Site-conditioning — how far V1 goes (and the imagery question)

Beyond burn probability, susceptibility is fundamentally a **distance/fuel** story. The damage-curve library
makes the receptor physics explicit: heat flux `q = 0.35 · I / d` for a fire **front** (a **line** source,
so **1/d** decay), calibrated at a canonical **`d = 10 m`** — and `d` is the **single dominant uncertainty**
(`d=5 m` doubles `q`, `d=20 m` halves it).

> 🐛 **Pre-build fix.** `infrasure-damage-curves/docs/hazard-intensity-variables.md:137` writes
> `q ∝ I/d²` (a **point** source) — wrong for a fire front, and it contradicts `WILDFIRE_x_SOLAR.md §4.1`.
> Since `d` is the dominant lever, the wrong decay law would systematically distort site-conditioning.
> **Pin V1 to `1/d` and fix that doc** before M3.

**Recommended V1 proxy (no imagery, uses data we already have):**

```text
(a) sample WRC at the ASSET BOUNDARY (zonal), not a 0.25° cell        ← grain
(b) keep the damage curve on fire-line-intensity I (kW/m) directly    ← axis
(c) condition the I-distribution on LANDFIRE 40-fuel class            ← biggest honest gain
       grass 500–2,000 vs chaparral/timber 3,000–10,000+ kW/m
(d) hold d = 10 m as a DOCUMENTED assumption (maybe one tier: 10 m / 20 m)
(e) for WIND: apply hub-height attenuation (USWTDB t_hh)              ← wind = a HEIGHT problem
       do NOT apply solar ground-fuel conditioning to wind
```

**Imagery for site conditions — assessed honestly.** A boundary polygon gives extent + centroid BP; it does
**not** give the susceptibility-defining conditions (vegetation against the array, cleared defensible-space
width, equipment spacing, cable routing above/below ground — which alone swings the electrical curve from
`L=0.10` to `L=0.85` and is in **no public dataset**). Satellite/aerial imagery (Sentinel-2 10 m, NAIP
~0.6 m, segmentation) *could* derive defensible-space width and fuel-cover fraction. **Value: real but
bounded** — it refines `d` and the fuel term, both only *assumed* at this maturity. **Cost: high** (a
segmentation pipeline, ground-truth, per-site processing). **When: V1.5+**, landing with the surface-vs-crown
split and a fire-front sweep (which yields real `d` + residence time "for free"). Even the legacy roadmap
grades imagery a *Gen-2 precision improvement*, not a foundation.

> **DECISION 4.** V1 site-conditioning = proxy **(b)** above (boundary BP + LANDFIRE fuel + fixed `d=10 m` +
> wind hub-height), **imagery deferred to V1.5+** as a named hook? *(Recommended: yes.)*

---

## 8. What we reuse from the lab vs rebuild

| Item | Call |
|---|---|
| WRC/WHP **download plumbing** (`scripts/02`, `01`) | **Port as-is** (adapt paths, re-verify endpoints) |
| **Sampling technique** (`scripts/03`) | **Reuse the technique, not the file** — re-express for asset-polygon zonal stats, not the 0.25° grid |
| **Byram + composite-logistic math** (`wildfire_loss_math.py`) | **Reuse the per-intensity kernel; source curves from `infrasure-damage-curves`** (don't copy params — they'd drift). **Replace `E[DR\|fire]` with per-event SAMPLED damage in M4** (else we reproduce the cardinal error) |
| **FLP6 reconstruction** from FLEP4/FLEP8 | **Revisit** — admitted approximation (`r=0.948` vs CFL-direct); the **#1 severity-side uncertainty**. Decide: keep, or pull a fuller flame-length distribution (see Decision 6) |
| **Source-caveat / grid-resolution docs** | **Port into our assumptions register**; the MTBS-currency fix (BP foundation is end-2020 LANDFIRE fuels — overstates risk in post-2020 burn scars) is a **named deferred enhancement** |
| **Screening risk-metrics / tail** (`scripts/06`) | **Rebuild entirely** — M4 is the shared SAMPLED compound-NegBin engine |
| Flat TIV + revenue-layer joins (`scripts/04`) | **Don't import** — we carry per-asset TIV and report **% of TIV** |

---

## 9. Competitive lessons (adopt / avoid)

- ✅ **The wedge: build BoS-weighted vulnerability on a public hazard substrate.** **No incumbent** has a
  renewable-specific wildfire vulnerability model (Verisk = construction-code categoricals only; RMS / Swiss
  Re / First Street / CLIMADA generic; HAZUS has **no wildfire module at all**). The hazard side is at
  parity; the **vulnerability side is greenfield**. Wildfire loss on solar is **asymmetric — mostly
  electrical BoS** (inverters, transformers, cables, substation), **not panels**. Build BoS-weighted MDR
  curves; avoid a panel-centric curve.
- ✅ **Carry the single-centroid disaggregation discipline from hail M2.** Moody's own Sabbatelli-Goodyer
  (Jan 2025) solar-farm case: multi-centroid disaggregation shifted **flood AAL +230%** vs **wind +2%** —
  wildfire patterns with **flood**. A perimeter clipping the inverter pads but missing the panels is a
  fundamentally different loss than a centroid sees. (This is *why* boundary-aware sampling matters — §6.)
- ✅ **Honest-labeling is corroborated.** RMS v2.0 explicitly models utility-triggered ignition +
  subrogation — the closest any incumbent comes to the ignition side — confirming a solar farm is **both
  source and victim.** We acknowledge-and-defer the source role; we don't build it into V1.
- ⛔ **Don't reproduce a proprietary stochastic ignition+spread catalog** (RMS 72M events × 3 footprints;
  Verisk 10k-yr YELT). That's the incumbents' moat and not where our value lives. Adopt only the **output
  shape** (BP + fire-line-intensity inside a perimeter) from a **public substrate**.
- 🅿️ **Park climate-conditioning for V1.** Verisk caps wildfire projections at 2050; Swiss Re ships a 5-yr
  forward ML score. Renewable assets reach 2050–60 → real future whitespace, but V1 is a **current-climate**
  damage track and the engine must not change.

---

## 10. Open decisions for the owner

The gating ones (1–4) are in their sections above. The rest:

> **DECISION 5 — frequency process.** Sample annual occurrence from BP, then a severity (flame-length /
> intensity) draw, expressed through the **same compound-NegBin engine** (a Bernoulli is a NegBin special
> case → engine genuinely unchanged). Decide whether multi-fire years are even relevant per single site
> (likely not at these BPs). *(Recommended: BP-occurrence → severity draw, shared engine.)*

> **DECISION 6 — severity axis & flame-length *source*. (Largely RESOLVED — see [`02`](02_fsim_wrc_data_dictionary.md).)**
> Stay on the `I` (kW/m) axis with `d=10 m` embedded (line-source `1/d`, fix the doc). For flame length, the
> data-dictionary research confirmed native **FSim 3rd-Ed FLP1-6 rasters ARE publicly fetchable**
> (`RDS-2016-0034-3`, 270 m, CC BY 4.0) — so the recommended source is **(ii) native FLP1-6** (full 6-class
> histogram, single clean vintage, *no lossy reconstruction*). Fall back to **(i)** WRC 2.0 FLEP4/8 + a
> reconstruction **only** if 30 m resolution turns out to be a hard requirement — and if so, register the
> reconstruction as an assumption and sensitivity-test it (the lab's heuristics have no cited provenance).
> *(Recommended: `I`-axis + LANDFIRE conditioning + **native FLP1-6 (270 m)**. The trade-off is res vs. a
> clean histogram — for large solar arrays, 270 m is very likely sufficient.)*

> **DECISION 7 — housekeeping (independent of modeling).**
> (i) **Rotate the leaked Hydronos API key** (`_legacy_wildfire/scripts/wildfire_eal_pipeline.py:39`, in git
>     history) — a live security liability regardless of any decision here.
> (ii) **The 30% unmodeled solar TIV:** the library's solar subsystem weights sum to **0.70** — 30% of solar
>     TIV has no wildfire curve. Conscious choice: genuinely non-damageable, or a known gap? This directly
>     scales EAL, so it can't be silent.

---

## 11. Light M0/M1 sketch (context only — we still plan these step by step)

```text
M0  Notebooks/wildfire/m0_input_data/   (peril-shared)
    └ port lab download plumbing → fetch 5 public rasters (BP, CFL, FLEP4, FLEP8, WHP 2023)
      from imagery.geoplatform.gov (no auth, CC BY 4.0); GeoTIFFs → data/wildfire/ (gitignored,
      manifest kept); interpret every layer (value + meaning + reference base); record the
      end-2020 fuel-currency caveat. Cite RDS-2020-0016.

M1  Notebooks/wildfire/m1_catalog/      (peril-shared)
    └ per-asset hazard catalog by ZONAL sampling within asset_boundary (NOT the 0.25° cell):
      BP (mean + hotspot-max + count for QA), flame-length exceedances, LANDFIRE fuel class, WHP.
      Capacity→radius fallback for the ~36% lacking a boundary. Distinguish "no coverage" from
      "zero risk". This is the bucket-3 hazard FIELD per asset.

    (then, step by step:) M2 site-conditioned coupling · M3 BoS-weighted MDR on I (kW/m),
    curves from infrasure-damage-curves · M4 the SHARED compound-NegBin MC, untouched,
    metrics read off the SAMPLED distribution, % of TIV alongside dollars.
```

---

*Next: once the owner settles Decisions 1–7, these graduate to `docs/plans/wildfire/` (`00_intent`,
`decisions.md` `DD-*`, `assumptions.md` `A-*`), and we open **M0** — one layer at a time, no jumps.*
