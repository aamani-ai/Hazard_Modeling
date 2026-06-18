# Flood pipeline — decisions log

Running record of the non-obvious design decisions for the flood → solar build (then wind in V2), ADR-style
(context → options → decision → why → revisit trigger). Newest on top. Prefix `JD-FL-*`.

> **Status: scope, frequency, sites, and the modularity hooks decided (proposed); one call still open.** The
> competitive-research architecture (`…/learnings/architecture/`) **pre-defines** flood's taxonomy (A12), catalog
> method (A20), coupling (A21), and damage form (A22). Settled below: scope/defer-coastal (JD-FL-1), frequency path
> (JD-FL-2), the two sites + national screen (JD-FL-3), the add-coastal-later hooks (JD-FL-4). **The one genuinely-open
> call is the event-model bridge** to our shared MC engine (bottom). **Update (2026-06-17):** depth-source research +
> a FEMA-BLE probe **supersede** the single-gauge route — the spine is now the **national StreamStats+HAND pipeline,
> FEMA-BLE-preferred where it exists** ([JD-FL-6](#jd-fl-6)); BLE *does* exist for Bayou Galion. **The event-model
> bridge is now settled** ([JD-FL-7](#jd-fl-7)) — annual-maximum MC sampling the loss-exceedance curve.

---

## JD-FL-11 · Sub-peril combine — **co-sample (comonotonic) + worse-source-wins headline; additive-capped as the recorded upper envelope** (research-confirmed)

**Date:** 2026-06-17 · **Status:** decided · The M4 combine for JD-FL-10 · **Backed by [`flood_subperil_research_result.md`](../../../jdocs/flood_subperil_research_result.md)** (Bates 2021; FFRD/HEC-WAT; Guan 2023; Ward 2018; Oasis LMF).

**Context.** With riverine + pluvial both built, M4 must turn two per-sub-peril loss curves into one annual flood loss.
Both are **rain-driven** → positively correlated (one storm often causes both); and they act through the **same
depth-damage curve on the same equipment**. The **old model** treats Riverine/Flash/Coastal as **independent perils
and sums** them — which **double-counts** the shared storm and mis-states occurrence dependence.

**Decision.** Two parts, both research-endorsed:
1. **Occurrence = co-sample comonotonic.** Draw one annual AEP `u ~ U(0,1)` per year; read **both** sub-peril loss
   curves at `u` (one shared storm — matches FFRD shared-storm logic / RMS single-event identity).
2. **Severity = worse-source-wins (per-location max depth → one damage eval).** The year's flood loss =
   **max(loss_riverine(u), loss_pluvial(u))** — physically correct for **shared ground** (a component drowns once; this
   is exactly what the Bates 2021 / Fathom / First Street engine does: *"max depth at each pixel"*). This is the
   **headline number** (single-valued, like every other peril → combinable into Total Loss). Metrics on the
   **combined per-year vector** (never summed marginals — Oasis LMF; comonotonic-sum is the upper bound, not the answer).
3. **Recorded envelope (not used in the math):** the general rule is `L = max + (1−φ)·min(L_r, L_p)`, φ = shared-ground
   overlap. For a **compact, flat solar footprint where both sources pond on the same low ground (Elizabeth), φ skews
   high (0.6–0.8)** → worse-wins (φ=1) is the defensible **headline**; **additive-capped** (φ=0, `min(TIV, L_r+L_p)`)
   is the **upper sensitivity bound** reported beside it. Keep per-sub-peril marginals.

**Why.** Worse-wins is the research's recommended default *when overlap is high* (our case) and avoids double-counting
the same drowned equipment; co-sampling is correlation-honest; single-valued headline keeps flood consistent +
Total-Loss-combinable; the envelope carries the honest spread without false precision in φ.

**Honest caveats.** (1) The **headline is pluvial-dominated** here (pluvial > riverine at every RP, driven by the
screening-grade `f` exposure knob) → the well-anchored riverine is masked in the combined; **report marginals**, treat
the headline as screening-grade until pluvial gains a depth anchor. (2) **Differs from convective_wind on purpose** —
wind *adds* its sub-perils (tornado/strong-wind hit *different* subsystems); flood *maxes* (same water, same equipment).
Intentional, not a bug. (3) Inland riverine↔pluvial dependence is a **published knowledge gap** (Guan 2023) → φ is
judgment, hence the reported envelope.

**Revisit trigger.** Sub-asset spatial-exposure data → drop the φ heuristic for true per-location max-then-sum; a
measured riverine↔pluvial copula → replace comonotonic occurrence; pluvial depth anchor → narrow the envelope.

---

## JD-FL-10 · Sub-peril structure — **fork the catalog (M1) per sub-peril; share M2/M3; combine at M4**

**Date:** 2026-06-17 · **Status:** decided · Realizes the [JD-FL-4](#jd-fl-4) family hooks · Sets the pluvial/coastal layout.

**Context.** Riverine shipped as a single implicit cell. Adding **pluvial** (then coastal) needs a folder/data shape.
The convective_wind precedent forks sub-perils at **M2** (tornado vs strong-wind *couple* differently, share M0/M1).
Flood is different: its sub-perils differ in **data + footprint** (BLE/streamflow vs Atlas-14 rainfall vs SLOSH surge)
but share **one damage driver — inundation depth** (the reference: *"handle each separately, then combine on the
shared depth metric"*).

**Decision.** Fork **at the catalog (M1)**, not at M2 and not a top-level `flood/riverine/` tree:
```
flood/ m0_input_data/                    # shared site geometry + DEM
       m1_catalog/ riverine/ 01_catalog  # BLE + streamflow densification  (built)
                   pluvial/  01_catalog  # NOAA Atlas-14 rainfall → ponding depth
       solar/ m2_coupling/ m3_damage/    # SHARED — depth→damage is identical per sub-peril
              m4_loss_metrics/           # reads ALL sub-peril catalogs, COMBINES (per JD-FL-?, the combine rule)
```
Each catalog emits the **same depth-at-RP schema** tagged `sub_peril`; M2/M3 process whatever rows arrive; M4 combines.

**Why.** Matches flood's actual shape (diverge at the data, re-converge at depth→damage) and the JD-FL-4 hooks
(`sub_peril` key already in every manifest). Avoids duplicating the shared M2/M3/M4 framework. Coastal slots in the
same way later — with its catalog **shared from hurricane** + the `event_family_id` link switched on (its extra twists).

**Revisit trigger.** A sub-peril whose *coupling* (not just data) differs would justify an M2 fork too (none yet).

---

## JD-FL-9 · Pluvial depth source — **NOAA Atlas 14 rainfall → SCS-CN runoff → DEM-hypsometry ponding** (no free pluvial grid exists)

**Date:** 2026-06-17 · **Status:** decided · The pluvial analogue of [JD-FL-6](#jd-fl-6) (riverine BLE). Reference-aligned (Flood-Data-Ref §2/§5/§7).

**Context.** Pluvial = intense-rainfall surface flooding — *"the blind spot"* (Flood-Data-Ref §7): FEMA NFHL
**under-maps it ~3×** (Wing/Bates 41M vs FEMA 13M in the 1% floodplain), and — unlike riverine — there is **no free
pluvial *depth* product** to anchor to (FFRD pilot-only; First Street/Fathom commercial). So we have easy *frequency*
(rainfall) but must *model* depth with **nothing observed to calibrate against** (the inherent weakness, flagged).

**Options.** (a) Atlas-14 rainfall → a **rainfall-driven depth model** on our 3DEP DEM (runnable, approximate);
(b) full **HEC-RAS rain-on-grid** 2-D (gold standard, not runnable here — the HAND problem again); (c) **FFRD** (pilot,
not at site) / **commercial** (paid, excluded); (d) NWC-FIM flash (HAND — more flash-riverine than pure pluvial).

**Decision — option (a), the free reference-recommended method.**
1. **Frequency = NOAA Atlas 14** point precipitation-frequency (24-hr depth at 10/25/50/100/500-yr; PFDS CSV — probed,
   reachable: Elizabeth 100-yr 24-hr ≈ 13.8″). *The pluvial frequency backbone, as StreamStats is for riverine.*
2. **Rainfall → runoff = SCS Curve-Number** (CN≈80, graded solar open-space/soil-C): `Q = (P−0.2S)²/(P+0.8S)`,
   `S=1000/CN−10` — the net runoff depth (the flood water available to pond).
3. **Runoff → ponding depth = DEM-hypsometry bathtub:** pour `Q` over the footprint's 3DEP elevation distribution
   (≈ Normal(μ,σ) from M0's `elev_mean`/`elev_std`); solve the ponded water surface so footprint-average depth = `Q`
   (the **conservative no-drainage** limit) → `inund_frac = Φ((WSE−μ)/σ)`, `conditional_depth = Q/inund_frac`.
   Emits the **same depth-at-RP schema** riverine does (JD-FL-10), `sub_peril="pluvial"`.

**Why.** The only **free, self-serve, reference-endorsed** pluvial path (Flood-Data-Ref §5: *"drive a rainfall-based
model from Atlas 14… or use FFRD/commercial"*). Reuses the DEM M0 already pulled; keeps us hazard-first.

**Honest caveats.** (1) **No depth anchor** (vs riverine's BLE) → pluvial depths are inherently **softer/wider** — the
reference's blind-spot, not a shortcut. (2) **No-drainage** assumption (all runoff ponds in place) → an **upper bound**;
real grading/drainage reduces it (the pluvial analogue of riverine's onset-depth — sensitivity-test). (3) `CN` and the
24-hr duration are assumptions. (4) Atlas-14 LA Vol-9 is stationary + aging (§8).

**Revisit trigger.** **Atlas 15** (climate-aware, CONUS ~Sept 2026) for the rainfall input; **FFRD** national / a free
pluvial depth grid → swap in and demote the rainfall-runoff model; commercial budget → Fathom/First-Street pluvial.

---

## JD-FL-W4 · Wind-cell depth — **extent-based bathtub off 3DEP** (Zone A has no BFE/BLE)

**Date:** 2026-06-17 · **Status:** decided · Specializes [JD-FL-6](#jd-fl-6) to the wind high site · *basics-spot-on*

**Context.** The solar high site (Elizabeth, LA) had a FEMA **BLE** depth grid. The wind high site (**Green River,
IL**, [JD-FL-W3](#jd-fl-w3)) does not: its floodplain is **Zone A** (approximate — `STATIC_BFE = -9999`, no BFE
lines) and **outside BLE coverage** — exactly the approximate/ungauged case JD-FL-6 reserved StreamStats+HAND for.

**Decision.** Sample depth **per node** (turbine + substation) via an **extent-based bathtub** off the **3DEP DEM**:
the 1% floodplain *boundary* is the 1% **water-surface contour**, so
`depth = WSE(median of nearest SFHA-edge 3DEP samples) − ground(3DEP) − pad_elevation` (clipped ≥0), a node flooding
iff inside the mapped SFHA. The **500-yr** surface = the 1% surface **raised by a freeboard** `ΔWSE ≈ 0.6 m` (≈2 ft;
**AFL-W7**) because no 0.2% band is mapped here — deepening floods *and* catching valley-edge turbines. Sampled **at
each turbine point** (a sparse cloud), not over an areal footprint.

**Why.** The only **public, self-contained** depth path for an approximate Zone A floodplain (no BFE, no BLE grid),
reusing the **3DEP DEM** the solar M0/02 established. It honours the asset's physics (most turbines above the
floodplain; valley-bottom ones flood; the substation is one low node).

**Honest caveats.** Medium-low confidence — a **flat-water** approximation of a sloping floodplain; the 500-yr
freeboard is an assumption (no mapped 0.2% band); two RPs only. **StreamStats+HAND** (JD-FL-6/JD-FL-8) or a
detailed-study BFE is the documented upgrade.

**Revisit trigger.** A detailed FEMA study (BFE) or a StreamStats+HAND run at Green River → swap in engineered depth.

---

## JD-FL-W3 · Wind high site = **Green River, IL** (Midwest river-valley wind), not Texas

**Date:** 2026-06-17 · **Status:** decided · Forced by [JD-FL-W2](#jd-fl-w2)

**Context.** JD-FL-W2 verified **Texas wind is flood-immune** (0/2,976 turbines wet) — so the solar high site's
region + BLE reuse cannot serve the wind cell. A corridor sweep of Midwest river-valley wind (upper-Mississippi/
Missouri/Illinois; 12,666 turbines, 316 projects) found genuine turbine-level flood exposure.

**Decision.** High site = **Green River (Lee Co., IL)** — **~60% of its 74 turbines in the 1% SFHA**, the clear
screen winner (next: Barton IA 16%, Walnut Ridge IL 9%). Baseline = **Shepherds Flat** reused. The cost is the depth
method (JD-FL-W4): Green River is Zone A + outside BLE → extent-based bathtub, not BLE.

**Why.** It is the genuine high-flood wind farm a "proving site" needs — a real fraction of turbines in the
floodplain. The flat, wide Midwest river valleys are where wind and water actually coincide; TX/coastal wind sits on
high ground.

**Honest caveats.** Leaves the clean BLE reuse (depth now via bathtub, JD-FL-W4). The substation location is unknown
(centroid proxy, AFL-W5).

**Revisit trigger.** A BLE-covered high-flood wind farm appears (full BLE CONUS coverage) → reconsider region.

---

## JD-FL-W2 · Finding — **wind turbines are flood-immune** (sited on high ground); exposure is per-node, not areal

**Date:** 2026-06-17 · **Status:** decided (empirical finding) · Reshapes the whole wind cell

**Context.** The solar cell treats flood as **areal** (one footprint floods as a unit); the plan assumed the wind
cell would screen a TX wind farm the same way. A FEMA SFHA + BLE probe of the TX wind fleet falsified that premise.

**Decision / finding.** A wind farm is **not** an areal flood asset: turbines are deliberately sited on **high
ground**. Verified across the **entire east/coastal TX wind fleet** — **44 farms, ~2,976 turbines, BLE coverage
confirmed → 0 turbines in even the 500-yr floodplain.** Flood exposure for wind is **per-node** — a *fraction* of
valley-bottom turbines + the **substation** (one low-lying, high-value collector node) — **not** an areal fraction.
This drives the M0 screen (SFHA *fraction*), the M2 coupling (per-node sum, not areal product), and the M3 curve
(only the base floods).

**Why it matters.** The load-bearing difference between flood × solar and flood × wind, and a portfolio insight:
**flood is a minor, capped peril for wind** (vs material for ground-mounted solar).

**Revisit trigger.** Turbine siting standards change, or floating/low-elevation turbines appear.

---

## JD-FL-W1 · Wind sites — **Shepherds Flat (reused, baseline) + a screened high-flood farm**; geometry = USWTDB cloud + hull

**Date:** 2026-06-17 · **Status:** decided · Mirrors [JD-FL-3](#jd-fl-3) (solar) on the wind asset

**Context.** The flood cell's V2 asset is the wind farm — it needs a low/high pair like solar's, and a geometry for
a **sparse turbine point cloud** (not solar's dense footprint).

**Decision.** **Baseline = reuse Shepherds Flat** (the convective_wind wind baseline — the *asset's* cross-peril
coherence axis, as Hayhurst is for solar); polygon WKT + turbine cloud cached in `data/convective_wind/`. **High =
screened** ([JD-FL-W3](#jd-fl-w3)). **Geometry = USWTDB turbine cloud + a convex-hull boundary** (the
`renewablesinfo_org` boundary-DB symlink is **absent** here, so the hull is the symlink-free honest extent for a
point cloud — **AFL-W4**). **TIV = $/kW** (AWN-14 basis). **Substation** = a centroid node (**AFL-W5**).

**Why.** Reusing Shepherds Flat preserves coherence and is a legitimate mapped-dry control (NFHL SFHA ≈ 0); the
USWTDB cloud is the per-turbine view flood needs; the hull is symlink-free.

**Revisit trigger.** The boundary-DB symlink returns / an OSM plant polygon is found → swap the hull for it.

---

## JD-FL-8 · Densify the lower return periods — **regression flow-frequency + a BLE-anchored rating curve** (not a live HAND raster)

**Date:** 2026-06-17 · **Status:** decided · Hardens [JD-FL-7](#jd-fl-7)'s EAL · Implements the JD-FL-6 seam, depth step swapped.

**Context.** JD-FL-7 shipped a 3-point loss curve where the **10-yr onset depth is an assumption** (`ONSET_DEPTH_FT`),
not a measurement — and EAL is driven by exactly that frequent region (PML@100/500 is BLE-solid, EAL is soft). The
hardening JD-FL-6/7 promised is "densify the lower RPs with StreamStats+HAND." On building it, two facts surfaced:
1. **The literal HAND path won't run here & is weakest here.** The USGS **watershed-delineation** service
   (`streamstatsservices/watershed`) is **down (404)**; the NOAA OWP HAND depth step needs multi-GB 3DEP/HAND rasters
   from an AWS S3 bucket. And the research doc itself flags **HAND as *least* accurate on low-order, low-relief
   streams** — exactly Elizabeth's flat Louisiana alluvial plain, where BLE already ran a HEC-RAS-quality study.
2. **The regression-equation service (NSS) *is* reachable** (HTTP 200) — so the **flow-frequency** half is live.

**Options.** (a) Full live StreamStats→HAND raster pipeline — most independent evidence, but not runnable here and
least reliable for this site. (b) **Regression flow-frequency Q(T) + a rating curve pinned to the two real BLE
depths** → read depth at the lower RPs. (c) JRC/GloFAS coarse depth grid — needs Google Earth Engine, ~1 km (too
coarse for this footprint). (d) Keep the flat onset assumption.

**Decision — option (b).** Get the **flow-frequency curve** `Q(T)` for T∈{2,5,10,25,50,100,500} at the site's reach
from real regression data, then build a **stage/depth–discharge rating curve anchored to the two genuinely-measured
BLE depths** (100-yr + 500-yr): with `(Q₁₀₀, d₁₀₀)` and `(Q₅₀₀, d₅₀₀)` as anchors, fit a monotone rating
`depth = f(Q)` (power-law / log form) and evaluate it at the lower-RP discharges → **measured-anchored depths at
2/5/10/25/50-yr**, replacing the flat `ONSET_DEPTH_FT`. Feed the now-denser depth→loss profile through the **same**
M4 seam (variable-length RP curve — no downstream change). **Also persist the raw `Q(T)`** so a future swap to full
HAND is just the depth step.

**Why.** It makes the lower-RP depths **rest on real data** (real flow-frequency shape + two real BLE depth anchors)
instead of a flat guess — the EAL-hardening goal — while staying runnable and honest. For a flat alluvial plain
where BLE exists, **anchoring to BLE beats raw HAND** (the research doc's own ranking: "prefer BLE; HAND weakest on
low-relief"). The single remaining assumption is the **shape of the rating between the two anchors** (vs. a flat
onset depth before) — strictly less assumption, and surfaced in an M4 sensitivity sweep.

**Honest caveats.** (1) Two BLE anchors fix the rating's *level*; its *curvature* is assumed (power-law) — sensitivity-
tested. (2) Flow-frequency is regional regression (tens-of-% standard error in the LA plains) — propagate later as an
MC overlay, not yet. (3) Still annual-maximum, physical-damage-only (JD-FL-1/7). (4) Elizabeth sits near a regression-
region boundary (Coastal Plain / Mississippi Alluvial Plain) — note which region's equation is used.

**Revisit trigger.** Watershed-delineation service back up **and** HAND rasters fetchable → swap the rating step for
live HAND-SRC depth and keep `Q(T)` as-is; or a hi-res national RP-depth grid appears → sample it directly (JD-FL-6
trigger). Either way re-validate EAL — it will move.

---

## JD-FL-7 · Event-model bridge — annual-maximum MC sampling the loss-exceedance curve (3-point, seam-ready)

**Date:** 2026-06-17 · **Status:** decided · Settles the long-open call. Mirrors convective_wind strong-wind (fit to an RP curve).

**Context.** M3 gives conditional loss at the BLE return periods (100-yr, 500-yr). The shared engine wants per-year
loss vectors (EAL/VaR/PML/TVaR off them — DD-4 frame). How does a sparse RP curve become that?

**Decision.** Model riverine flood as **annual-maximum** (~1 damaging flood/year — *not* compound-Poisson multi-event,
which mis-fits flood). Build a **loss-exceedance curve** from the real BLE points — `(AEP 0.01 → L₁₀₀, 0.002 → L₅₀₀)`
— plus a **10-yr onset anchor** `(AEP 0.1 → ~0)` where BLE's 10% *extent* shows inundation begins. The MC draws each
year's AEP ~ U(0,1) → `loss(AEP)` by **log-AEP interpolation** (bounded extrapolation below 0.002) → per-year loss
vectors → the **shared EAL/VaR/PML/TVaR** (% of TIV). This is the convective_wind strong-wind pattern (fit/sample an
RP curve) specialized to annual-max + 3 points.

**Why.** **PML at 100/500-yr is anchored to real BLE** (the percentiles reproduce L₁₀₀/L₅₀₀ by construction — a frame
known-answer). Keeps the **shared metric frame** → Total-Loss-combinable with hail/wildfire/wind. Avoids both the
old-model loss-first shortcut and a fabricated compound-Poisson fit from 2 points.

**Honest caveat.** **EAL is approximate** — it's driven by the frequent region (below 100-yr), which rests on the
onset anchor + interpolation, not measured depths. PML solid, EAL soft.

**Seam (easy upgrade).** M1 emits a **variable-length, source-tagged depth/loss-RP profile**; M4 fits/samples
generically. So adding lower-RP points (StreamStats+HAND, or JRC) is a **one-place change** — downstream untouched,
re-validate because EAL will move.

**Revisit trigger.** Lower-RP depths sourced (StreamStats+HAND primary, JRC coarse cross-check) → re-fit; EAL hardens.

---

## JD-FL-6 · Depth source (final) — **national pipeline: StreamStats + OWP-HAND, FEMA-BLE-preferred** (BLE used for the high site)

**Date:** 2026-06-17 · **Status:** decided · **Supersedes [JD-FL-5](#jd-fl-5)** · Source: [research](../../../jdocs/flood_research_result.md) + BLE probe.

**Context.** JD-FL-5 picked single-gauge extraction because no grid was available. A scaling review (we need *every*
CONUS asset, not one site) + a deep research pass reframed it: **single-gauge Bulletin 17C does NOT scale** — it
needs a hand-picked adequate gauge per site and fails at ungauged/short-record points (exactly Bayou Galion, whose
on-stream gauge has stage-only ~23 yr and whose discharge gauge drains too large an area). The only architecture
where **prototype == production at any CONUS point** is a national one.

**Decision.**
1. **Production spine (national, per-asset, automatable):** **USGS StreamStats** regional-regression discharge-at-RP
   → **NOAA OWP HAND + synthetic rating curve** → depth-above-ground (vs the 3DEP DEM). Works at any reach.
2. **Preferred where it exists:** sample a **FEMA BLE** depth grid (InFRM EstBFE / `txgeo.usgs.gov/.../FEMA_EBFE/EBFE`)
   — local-HEC-RAS quality, free, NAVD88, 1% + 0.2% depth/WSE.
3. **Coarse cross-check:** JRC/GloFAS global (~1 km).
4. **Single-gauge Bulletin 17C → demoted to local validation only**, never the engine.
5. **For Bayou Galion specifically (V1):** **BLE is available** (probe: Boeuf HUC8 `08050001`, "Data Available";
   0.2% depth ≈ 1.66 ft at the plant, WSE ≈ 88 ft matching our DEM) → **use BLE depth as the M1 source** for this
   site, with StreamStats+HAND as the scalable method for the no-BLE / ungauged general case.

**Why.** Nationwide queryability is the binding constraint; StreamStats+HAND is the only free method that satisfies
it, and BLE is the best free *depth* product where present. Accuracy (HAND ≈0.75 CSI / ~0.6 m) is acceptable for
portfolio EAL/VaR/PML (regression-Q error + the damage curve dominate), and BLE is better still. Keeps us hazard-first.

**Honest caveats.** BLE gives only **1% (100-yr) + 0.2% (500-yr)** depth (+10% extent) — the tail points, not the full
curve; lower RPs come from StreamStats+HAND or interpolation. HAND is weakest on low-order/low-relief streams (like
Bayou Galion) → prefer BLE there. Datum via NOAA VDatum; flag regulation/levees + climate non-stationarity as overlays.

**Revisit trigger.** A free hi-res national RP-*depth* grid appears (or BLE reaches full CONUS) → switch primary to
"sample the national depth grid per asset", demote StreamStats+HAND to gap-fill. Commercial budget → Fathom-US primary.

---

## JD-FL-5 · Depth source — USGS extraction (Log-Pearson III) — **SUPERSEDED by [JD-FL-6](#jd-fl-6)**

**Date:** 2026-06-17 · **Status:** ~~decided~~ **superseded** (single-gauge doesn't scale to all-US; see JD-FL-6).

**Context.** JD-FL-2 made pre-integrated RP depth grids the V1 spine, extraction the cross-check. The depth-source
probe + owner confirmation say no grid is available for **Bayou Galion**:
- **No depth product on hand** (owner confirmed — not Fathom, First Street, or otherwise).
- **FEMA** carries no depth here — Zone A is an *approximate* floodplain (`STATIC_BFE = -9999`, `DEPTH = -9999`); no
  detailed study → no Risk MAP depth grid.
- **JRC global** flood maps: old endpoint dead (moved to the JRC Data Catalogue) and coarse (~1 km) anyway.
- **But** 49 USGS peak-flow gauges sit within ~0.4° — incl. the **Ouachita River** and **Bayou Bartholomew**
  (through Morehouse Parish — the plant's likely flood source).

**Decision.** For V1, **flip the spine to extraction**: controlling-gauge peak-flow record → **Log-Pearson Type III**
(Bulletin 17C) → discharge-at-RP → **stage** (gauge rating) → **depth = stage − ground elevation** (3DEP DEM from
[`02`](../../../Notebooks/flood/m0_input_data/02_depth_grids_and_dem.ipynb)). Pre-integrated grids (Fathom / FEMA Risk
MAP / First Street) become the **future swap-in**, not the V1 path.

**Why.** It is the only **public, hazard-first** depth path that covers this site; gauge density is high; and the
site is **flat** (3.2 m relief — `02`), so `stage − DEM` is a defensible V1 depth without 2-D hydraulics. Keeps us
off the old model's loss-first shortcut (*basics-spot-on*).

**Honest caveats (carried into M1).** (1) The gauge is offset from the plant along the stream — V1 uses the nearest
gauge's water-surface as a proxy (flag the slope offset). (2) **Datum** — USGS gauge datum (often NGVD29) must be
reconciled to the DEM's NAVD88. (3) Regulation — check for upstream dams that break stationarity (Bulletin 17C
assumes a stationary, unregulated record).

**Revisit trigger.** A depth-grid product (Fathom / FEMA Risk MAP / First Street) becomes available → swap it in as
the spine and demote extraction to the cross-check (reverting to JD-FL-2's original ordering).

---

## JD-FL-4 · M1 built as a sub-peril *family* + a reserved `event_family_id` — the two "easy-to-add-coastal-later" hooks

**Date:** TBD · **Status:** proposed · Enables [JD-FL-1](#jd-fl-1)'s deferral · *modular-from-day-one*

**Context.** JD-FL-1 defers coastal (and pluvial may lag riverine). Deferral is only low-regret if the M1 catalog is
built so the deferred sub-perils slot in **without a refactor**. Wind's family (strong wind + tornado: shared M0/M1,
fork at M2, shared M3/M4) is the precedent.

**Decision (proposed) — two cheap hooks, built now even though V1 ships riverine(+pluvial) only:**
1. **Sub-peril-keyed catalog/manifest** — model flood as a *family* (a `sub_peril` key: `riverine` now, with the
   schema able to hold `pluvial`/`coastal` rows), **not** hardcoded "flood = riverine." Adding a sub-peril later = a
   new row, not a rebuild.
2. **Reserve `event_family_id`** in the catalog schema — unused in V1, but present — so a future coastal-surge event
   can be linked to its parent hurricane event (the A12 cross-link) to prevent double-counting. The *one* piece of
   future-proofing that's expensive to retrofit.

**Why.** Both cost almost nothing at build time and are the difference between "add coastal in a day" and "refactor
M1." The old repo's flood code (single conflated flood type, no event identity) is exactly what these avoid.

**Revisit trigger.** When pluvial or coastal is actually added — confirm the keys/field were sufficient; extend if not.

---

## JD-FL-3 · Two solar sites — **Hayhurst (low, reused) + a national-EIA flood-screen high site** (Lower-Mississippi riverine)

**Date:** TBD · **Status:** decided · **High site = Elizabeth Solar Plant** (EIA 66111, Allen Parish LA, 143 MW).

The SFHA-centroid screen first surfaced **Bayou Galion** (EIA 67104, Zone A) — but it has **no OSM/enriched polygon**
(circle-only), and flood needs a real footprint more than other perils. A **geometry + BLE-depth refinement** over the
exposed candidates selected **Elizabeth Solar**: a real **~3.9 km² OSM polygon** *and* the deepest BLE flood of the
polygon-bearing candidates (100-yr 16% @ 0.46 m / 500-yr 19% @ 0.60 m, sampled over the real polygon). Its centroid is
zone X but the footprint straddles the SFHA (BLE-confirmed). Both sites now use **real OSM polygons** (Hayhurst 0.73 km²,
Elizabeth 3.91 km²) — no circle fallback. Enriched-registry/Fathom remain future swap-ins.

**Context.** The low-vs-high contrast mirrors hail (single asset = Hayhurst) → wildfire (added the pair: Hayhurst
baseline + Matrix proving, Matrix chosen by screening 38 registry assets on burn probability). Flood needs the same
shape, with the high site chosen on a *flood* metric.

**Decision (proposed).**
- **Low / baseline = reuse Hayhurst Texas Solar** (EIA 66880, Culberson Co. TX, Chihuahuan desert) — genuinely
  near-zero flood **and** the same asset as hail + wildfire (cross-peril coherence; the owner's stated preference).
- **High / proving = screen the *national* EIA registry** (`powerplants_enriched_v2`, ~8.8k EIA-matched — the set
  wildfire screened, **not** the 66-site in-repo AIG portfolio, which has no MS/LA and only 2 AR sites) by a flood
  metric (FEMA flood zone / Fathom RP depth), targeting the **Lower-Mississippi alluvial plain** (LA/MS/AR Delta) —
  best depth-grid coverage + cleanest riverine contrast. The exact EIA asset is confirmed by that screen in M0.

**Why.** Reusing Hayhurst preserves coherence and is a *legitimate* low baseline (desert). The national screen keeps
the Lower-Mississippi high site reachable (the in-repo portfolio is TX/CA/Midwest-weighted). Method = wildfire's,
metric swapped to flood.

**Revisit trigger.** If the national screen's top Lower-Mississippi asset lacks depth-grid/DEM coverage, fall to the
next candidate or pivot region (Central Valley CA / Illinois riverine — both present even in the in-repo portfolio).

---

## JD-FL-2 · M1 frequency path — **pre-integrated return-period depth grids** (not Log-Pearson III extraction)

**Date:** TBD · **Status:** proposed (A-series-backed) · Generalizes [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)

**Context.** M1 needs a flood frequency basis. Two routes: **(a) pre-integrated** return-period depth rasters
(hydrodynamic-reanalysis output — Fathom-US / HEC-RAS / FEMA Risk MAP — tagged 10/50/100/200/500-yr), or **(b)
extracted** — fit Log-Pearson Type III (Bulletin 17C) to USGS annual peak streamflow, then route to depth.

**Decision (proposed).** **Pre-integrated depth grids = the V1 spine** (per A20 §3.3, "the hydrodynamic reanalysis
*is* the backbone for fluvial"). USGS gauge / Log-Pearson III kept as the **validation cross-check**, not the
primary path.

**Why.** Same logic as wildfire (FSim pre-integrated) and wind (ASCE RP surface): the frequency is already baked
into the product by a hydraulic model we can't out-build; extraction-from-gauges is labor-heavy and ungauged-stream
regionalization is its own project. Pre-integrated is the honest, fast, defensible V1 ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).

**Revisit trigger.** If the chosen grid product lacks the needed return periods or resolution at our sites, or if a
site is ungauged-and-ungridded → fall back to the extraction route. Confirm the actual public product (Fathom-US
2.0 vs FEMA Risk MAP depth grids vs licensed First Street) in M0.

---

## JD-FL-1 · Scope — flood as a **sub-peril family**; **riverine + pluvial** physical damage to solar first; coastal cross-linked to hurricane, deferred

**Date:** TBD · **Status:** proposed (A12-backed)

**Context.** "Flood" is not one peril. A12 splits it by the dual test (distinct footprint **and** distinct data)
into **Riverine `[R]`** (river-network-anchored), **Pluvial `[F]`** (grid-anchored local rainfall), and **Coastal
`[C]`** (coastline surge). Each is a separate catalog row; coastal surge is **cross-linked to hurricane** via a
shared `event_family_id` (A12 §3 / A20 §6.8), not double-listed as its own independent peril.

**Decision (proposed).** V1 = **riverine + pluvial inland inundation → physical equipment damage**, on a **solar
farm first** (wind farm V2, off the shared catalog). **Coastal `[C]` deferred** — it rides the deferred hurricane
field (surge frequency follows tropical-cyclone tracks). **Also out of scope:** foundation scour/erosion, corrosion,
water-quality, and **business-interruption loss** (physical loss only — A25's acute × damage cell; matches the
team's hazard-tier scope).

**Why — and the precise reason coastal is deferred (not "can't," but "shouldn't yet").** Coastal surge *depth* is
actually obtainable pre-integrated (Fathom-US coastal layer / NOAA SLOSH / FEMA coastal BFE), so the hazard is **not**
blocked by the deferred hurricane build. We defer coastal because: (1) **double-counting** — surge and hurricane wind
are the *same storm*; building coastal standalone now, then hurricane later, counts one event in two pipelines unless
the `event_family_id` cross-link exists — premature plumbing (the old repo's separate Hurricane + Coastal-Flood rows
are the live demo of this error); (2) **zero payoff for our V1 sites** — both are **inland** (Hayhurst desert;
Lower-Mississippi riverine), so surge never reaches them; (3) **scope/correlation cost** for no V1 benefit. R + F have
self-serve data + a committed pre-integrated method (JD-FL-2). Honest scope is *basics-spot-on* (mirrors DD-W1, DD-WN-1).

**Easy to add back — by design.** Coastal reuses the *same* site-conditioned coupling and pre-integrated-grid M1
pattern, so adding it later = a new M0 fetch (coastal grids) + a catalog row + a USACE coastal curve + a coastal site;
M2/M3-framework/M4 reused (wind's strong-wind+tornado family is the working precedent). The two cheap hooks that keep
it easy are recorded in **JD-FL-4**. Deferring does **not** make the one genuinely hurricane-gated part (surge↔wind
double-count reconciliation) any harder — that's hurricane-side work whenever hurricane lands.

**Revisit trigger.** When the hurricane / field-intensity bucket is built, coastal `[C]` attaches via the existing
cross-link without re-architecting. Decide R-only vs R+F for the *first* notebook in M0 (pluvial may lag riverine).

---

## Open — the genuinely undecided call

**JD-FL-? · Event model — RP-scenario + AAL vs the shared compound-Poisson MC (the bridge).** The flood reference
world (HAZUS / First Street) computes loss at each return period, then integrates the **exceedance curve → AAL**
(trapezoid). Our repo's shared M4 is a **compound-Poisson/NegBin Monte-Carlo** that samples events/year. These are
two different mathematical routes. **The decision:** convert the RP depth grids into an event stream the shared MC
can sample (the wildfire precedent — FSim's pre-integrated BP became a λ feeding the same MC), **or** run flood on
an RP+AAL track and reconcile the metrics. This must be settled before M4 — it is *the* load-bearing flood decision.
Frame it explicitly against [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) and
the engine contract.

*Also to record as we plan:*
- *JD-FL-? — **depth-damage curve**: tabular USACE building-archetype + per-asset DEM elevation offset (A22 §2.4/§7.6);
  subsystem split; solar-specific curve deferred (A22 Q7 — none exists publicly).*
