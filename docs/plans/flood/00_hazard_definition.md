# 00 — Hazard Definition (layer-0) · *the layer flood needed for the opposite reason wind did*

*Convective-wind needed a layer-0 because **no product defined its event** — so wind had to be **authored**. Flood
needs one for the **opposite** reason: its events **are** inherited (each sub-peril has its own data product), but
**"flood" is not one peril** — it is **three sub-perils at once** (riverine · pluvial · coastal), each with a
**different magnitude metric** and a **different data source**, sharing only **one damage driver: inundation depth**.
The flood notebooks build that family end-to-end (M0→M4, riverine + pluvial + coastal); what they lack is a single,
up-front statement of **(a) the magnitude observable per sub-peril** and **(b) the exact data source per sub-peril**.
This doc — and its notebook — is that statement. It **orients** the family quantitatively; it does **not** author or
re-model anything. Written for a reader new to the domain — terms defined on first use.*

**Where this sits:** **layer-0 (hazard definition / orientation)** → [M0 (input data)](m0_input_data.md) →
[M1 (catalog)](m1_catalog.md) → [M2 (coupling)](m2_coupling.md) → [M3 (damage)](m3_damage.md) →
[M4 (loss & metrics)](m4_loss_metrics.md). Built for the **solar** cell (Hayhurst TX dry · Elizabeth LA riverine ·
Discovery FL coastal · LA3 West Baton Rouge all-three) and the **wind** cell (Green River IL riverine · Shepherds Flat
OR dry · Amazon Wind Farm US East NC all-three — [m_wind_farm.md](m_wind_farm.md)). **Source material:**
`jdocs/Hazard_Data_Reference-Flood.md` (internal). **Notebook:**
[`Notebooks/flood/layer0/01_hazard_definition`](../../../Notebooks/flood/layer0/01_hazard_definition.ipynb).

---

## Why this layer exists (read this first)

Each prior peril sat at one end of a spectrum; flood sits at a third point:

| Peril | The data product(s) | What it pre-defined | layer-0 role |
|---|---|---|---|
| Hail | **MRMS / MESH** | "severe hail ≥ 1 inch" — one event, one threshold, one metric, baked in | **inherited** (empty layer-0) |
| Wildfire | **FSim (BP + FLP)** | "fire occurrence + flame-length classes" — event + conditional severity, pre-integrated | **inherited** (empty layer-0) |
| **Wind** | **— none —** | no single product defines the wind event (SPC / NOAA / ASCE / IEC / EF are fragmented) | **authored** (the centerpiece) |
| **Flood** | **three — one per sub-peril** | each sub-peril's event is defined by its own product, but **the magnitude metric and source differ per sub-peril** | **oriented** ← *here* |

Flood is an **inherited-definition** peril (like wildfire from FSim) — we do **not** author its events. But it is a
**sub-peril family**: the reference (`[REF]` §1) and the competitive-research A-series (`[A]` A12) split "flood" by a
**dual test** (*distinct footprint **and** distinct data*) into **Riverine `[R]`**, **Pluvial / flash `[F]`**, and
**Coastal / surge `[C]`**. Each measures a **different magnitude** from a **different product**, yet all three
reconverge on the **same damage driver — inundation depth**. So the question this layer answers is **not** wind's
*"what is one event, and how strong?"* but rather *"across this fragmented family, what exactly do we measure, and
precisely where does each number come from?"* — the orientation this layer provides up front. We state it
once, here, with full provenance, and *then* the (already-built) M0→M4 pipeline consumes it.

> **The honest framing.** Orientation is a *responsibility*, not a formality. Each sub-peril's magnitude **and** its
> source must be **named and traceable** — every number ties to a logged decision ([JD-FL-*](decisions.md)), an
> assumption ([AFL-*](assumptions.md)), the Flood Hazard-Data-Reference, or a named external standard. This is
> *basics-spot-on* applied to the hazard's own definition.

---

## The hazard, defined quantitatively

### 1. The magnitude observable — *and its exact source* — per sub-peril

The shared **damage** metric is **inundation depth** (`[REF]`: *"depth is the universal metric — sample a depth grid
at each asset and apply a depth-damage curve"*). But the **magnitude we observe**, and **where it comes from**,
**differ by sub-peril**. Stating both, paired, per sub-peril, is the whole point of this layer:

| Sub-peril | Magnitude observable | **Exact data source (role)** | Tracks |
|---|---|---|---|
| **[R] Riverine** | flood **depth** above ground at a return period (ft → m) | **FEMA BLE depth grids** (100/500-yr) — local-HEC-RAS quality, free, NAVD88 — *measured depth*; **USGS NLDI→NSS** regional-regression flow-frequency `Q(T)` for the **lower RPs** (10/25/50-yr, JD-FL-8); **3DEP DEM** for ground elevation | JD-FL-6/8 · AFL-6/12 |
| **[F] Pluvial / flash** | 24-hr rainfall **depth** at RP → **modeled** ponding depth | **NOAA Atlas 14** precipitation-frequency → **SCS Curve-Number** runoff → **3DEP DEM / 1 m lidar** ponding. **No free pluvial *depth* product exists** — the "blind spot" | JD-FL-9 · AFL-P1/P2 |
| **[C] Coastal / surge** *(built)* | surge **depth** (stillwater + wave) at RP | **NOAA SLOSH** surge — **shared from the hurricane peril**, not rebuilt | JD-FL-1/12 · [REF] §5 |

**Screening / support sources** (which asset, where, how high — not the depth itself): **FEMA NFHL** regulatory flood
zones (1% / 0.2% annual-chance) for site screening (*is the asset in the SFHA?*); **EIA-860** national plant registry
(*which assets to screen*); **3DEP DEM / 1 m lidar** for ground elevation (turns a water-surface elevation into a
*depth above the asset*).

**The honest asymmetry across sources** (the part that matters most):

- **`[R]` Riverine is the best-supported** (`[REF]` §5). FEMA BLE is a real **measured** depth product (HEC-RAS
  quality); the only modeled link is the rating curve between the two BLE depth anchors (JD-FL-8).
- **`[F]` Pluvial is the blind spot** (`[REF]` §7). FEMA NFHL **under-maps it ~3×** (Wing/Bates ~41 M Americans in the
  1% floodplain vs FEMA ~13 M), and **no free pluvial *depth* product exists**. So we have easy *frequency* (Atlas 14
  rainfall) but must **model** depth with **nothing observed to calibrate against** — the inherent weakness, flagged
  in AFL-P1/P2, not hidden.
- **`[C]` Coastal is built** off SLOSH surge depth (Discovery / LA3 solar + Amazon wind) but is the **same physical
  water as hurricane surge** — one source, **joined to hurricane on `event_family_id` (JD-FL-12)** and counted once.
- **Datum discipline** (`[REF]` §7, AFL-13): riverine BFEs (NAVD88), coastal levels (tidal datums), and asset
  elevations must reconcile to one datum (NOAA VDatum) or *every* depth is meaningless.

> **One driver, three sources.** Riverine **measures** depth (BLE); pluvial **models** it from rainfall (Atlas 14 →
> SCS-CN); coastal **borrows** it (SLOSH, shared from hurricane). Naming the source per sub-peril is this layer's reason to exist.

### 2. The event / catalog basis — what counts as a flood event

A wind event crosses a magnitude line μ; a **flood event** is framed as **annual-maximum** ([JD-FL-7](decisions.md)) —
roughly **one damaging flood per year** (validated against FEMA NRI's 0.93 floods/yr at the wind site, AFL-W9), **not**
a compound-Poisson multi-event stream (which mis-fits flood). So "what counts" is the **year's worst flood**, indexed
by its **annual-exceedance probability (AEP) / return period**: 10-yr (onset, AEP 0.10) · 100-yr (1% annual-chance,
the FEMA BLE anchor) · 500-yr (0.2%, the tail anchor); lower RPs densified by regression flow-frequency (JD-FL-8). The
return-period **is** the event basis — the slow-onset analogue of wind's μ-crossing.

### 3. The practical upper bound — where the magnitude distribution effectively ends

Wind truncates at a single physical gust ceiling `L`; **flood depth is bounded by two practical caps instead**:

1. **The RP tail we can source.** The free measured product (FEMA BLE) stops at the **0.2% (500-yr)** depth; FFRD
   reaches ~2000-yr but is pilot-only (`[REF]` §4/§8). So the *evidenced* distribution effectively ends at the 500-yr
   depth — beyond it is **bounded extrapolation** ([JD-FL-7](decisions.md)), flagged, not fabricated.
2. **The damage saturates first.** Long before any "maximum depth," the depth-damage curve **caps**: once the
   vulnerable equipment is fully submerged, deeper water adds no loss. For the wind asset this cap is **~28% of TIV at
   full turbine inundation** (rotor/nacelle/tower ride high above any flood — AFL-W8); for solar the inverter drowns
   shallow while elevated panels survive (AFL-8). The *loss* tail is short for a structural reason, regardless of depth.

So flood needs **no single physical `L`**: the sourced RP tail bounds the *frequency* side, equipment submersion bounds
the *severity* side. Both honest, both logged.

### 4. The severity / event model — per sub-peril, then combined

Given the per-sub-peril depth-at-RP, two settled pieces turn it into the per-year loss distribution the **shared
compound-Poisson/NegBin engine** consumes (`[JD]`):

- **Annual-maximum MC ([JD-FL-7](decisions.md)).** Build a **loss-exceedance curve** from the RP depths; each
  simulated year draws `AEP ~ U(0,1)` → `loss(AEP)` by **log-AEP interpolation** (bounded extrapolation below 0.002)
  → per-year loss vectors → the shared EAL / VaR / PML / TVaR (% of TIV). By construction the percentiles **reproduce
  the BLE anchors** at 100/500-yr — a known-answer the notebook verifies. **PML is anchored to real BLE; EAL is softer**
  (it rests on the densified lower RPs) — stated honestly.
- **Sub-peril combine = co-sample + worse-source-wins ([JD-FL-11](decisions.md)).** Research-backed
  (`flood_subperil_research_result.md`: Bates 2021 / Fathom "max depth at each pixel"; FFRD shared-storm; Oasis LMF):
  draw **one** annual AEP `u` per year, read **both** sub-peril loss curves at `u` (comonotonic occurrence — one shared
  storm); the year's flood loss = **max(loss_riverine(u), loss_pluvial(u))** (same ground drowns once) — the **headline**;
  the **additive-capped** `min(TIV, L_r + L_p)` is recorded as the upper sensitivity **envelope**. Marginals kept.

> ***Flood maxes; wind adds — intentional ([JD-FL-11](decisions.md)).*** Flood sub-perils act on the **same** equipment
> with the **same** water, so a component drowns once → **worse-source-wins (max)**. Convective-wind's sub-perils
> (tornado vs strong-wind) hit **different** subsystems via **different** physics → their losses **add**. Same M4
> interface, opposite combine, by design. The shared MC engine is **untouched** (*standard interface, not standard
> physics*).

### 5. The pre-integrated RP-depth surface — the severity tail, *already integrated* (for riverine)

For **riverine** there is the same shortcut wind had with the ASCE surface: the EVT is **already done**. `[REF]`/`[A]`
the **FEMA BLE / Risk-MAP / Fathom RP depth grids are pre-integrated return-period depth surfaces** — a hydraulic model
(HEC-RAS) ran the probabilistic analysis and baked depth-by-return-period into the grid. Reading the 100-yr and 500-yr
depths = **sampling the return-level curve at fixed exceedance probabilities** — the **wildfire move** (FSim
pre-integrated the seasons), governed by [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md):
*if an upstream simulator pre-integrated the stochastic set into an annualized RP field, M1 is **profile-assembly, not
extraction**.* Carry learning-09's caveat: **pre-integration is a borrow, not a free lunch** — we inherit FEMA/HEC-RAS's
assumptions, vintage, datum, and resolution; the uncertainty moved upstream, it did not vanish.

**The sub-peril split is sharpest here:** riverine **reads** a real pre-integrated surface; **pluvial has none to read**
(`[REF]` §7 — no free pluvial depth grid) and must **model** depth from Atlas 14 rainfall frequency via SCS-CN
(JD-FL-9). Frequency is pre-integrated for pluvial (Atlas 14); **depth is not**. Coastal's SLOSH surge grids are
pre-integrated too, shared from hurricane (built, JD-FL-12).

---

## The two thresholds — keep them distinct (the part that trips newcomers)

Exactly as for wind, flood has **two** thresholds in different layers — and the flood version lives on the **depth**
axis, which makes conflating them especially easy:

```
   FLOOD EVENT / RP BASIS                          ASSET DAMAGE-ONSET DEPTH
   "what the catalog COUNTS"                        "where the depth-damage curve LEAVES ZERO"
   → sets the annual loss (M4)                      → anchors the damage curve (M3)
   ─────────────────────────────                   ──────────────────────────────────────────
   the year's worst flood, indexed by AEP           solar: inverter/pad height (x0 ≈ 0.75 ft → drowns shallow)
   (10 / 100 / 500-yr depth at the site)            wind:  pad elevation (turbine 0.30 m · substation 0.15 m)
```

- **The RP basis** is what makes a flood *an event we count* — it sets the annual-max loss. A site in the 1%
  floodplain has its flood counted.
- **The damage-onset depth** is where the *equipment starts to suffer loss*. The coupling is `depth_at_asset =
  water_surface_elevation − ground_elevation(asset DEM)` (AFL-7); the depth-damage curve is **anchored** so
  `DR(depth ≤ onset) ≈ 0` and rises only once water reaches the vulnerable component (the `infrasure-damage-curves`
  `x0` *is* that component-elevation onset, AFL-8). It then **caps** at submersion (§3).

**The consequence — the curve is ANCHORED.** A site can sit in the floodplain (the catalog counts the flood) yet take
**zero loss** if the water stays below the pad/onset height. **Most shallow flooding barely scratches well-sited
equipment** — the direct analogue of "most severe wind barely scratches a turbine." This is why wind, with turbines
deliberately on high ground, is a **minor** flood peril (median project ~0% in the SFHA, AFL-W2).

---

## A coupling-taxonomy primer (newcomer-friendly) — *how the hazard reaches the asset*

Defining "how deep" is half the job; the other half is **how the flood reaches the asset** — the *coupling*. The
platform sorts every peril into **three buckets** by footprint (canonical table:
[principles/hazard_asset_specificity](../../principles/hazard_asset_specificity.md)).

| Bucket | One-liner | Footprint | The asset reads… | Math |
|---|---|---|---|---|
| **1. Areal hit-or-miss** | "the footprint covers you, or it doesn't" | point / narrow path | full loss **if hit**, **$0 if missed** | Bernoulli × Minkowski |
| **2. Field-intensity** | "you're always inside the field; your local value differs each event" | regional field | a continuous intensity at your location | sample-and-weight the field |
| **3. Site-conditioned** | "a model pre-baked your site's depth-by-RP; you look it up, modulated by your elevation" | broad swath (pre-integrated) | your own local depth profile (no miss) | depth field × elevation/height |

### Where each sub-peril sits — and why

**Flood is site-conditioned (bucket 3) for *every* sub-peril** — the asset is never "missed" (if it is in the
floodplain, it floods); it reads its **own local depth**, modulated by **micro-elevation (DEM)**. This **reuses
wildfire's site-conditioned M2 machinery** (AFL-3) — no Minkowski, no hit-or-miss. Micro-topography is **load-bearing**:
a metre of elevation changes the depth, so the asset's height relative to the flood surface *is* the coupling.

```
   [R] RIVERINE   broad swath (BLE pre-integrated)  →  BUCKET 3 (site-conditioned)   [built: reuse wildfire]
   [F] PLUVIAL    local rainfall ponding            →  BUCKET 3 (site-conditioned)   [built]
   [C] COASTAL    coastline surge (SLOSH)           →  BUCKET 3 (site-conditioned)   [built → joined to hurricane]
```

The asset-geometry difference is **within** the bucket, not across buckets:

- **Solar = dense areal polygon** → the **areal inundated fraction** × conditional depth proxies the value exposed
  (value ∝ area, AFL-14). One footprint floods as a unit.
- **Wind = sparse turbine point-cloud** → **per-node** depth (each turbine pad + the substation vs the flood surface,
  AFL-W2). Most turbines sit on high ground → flood is a **minor** peril for wind (median project ~0% SFHA; the
  raised pad even **sheds** pluvial rain — AFL-W10/W12); only valley-bottom nodes flood.

> **Cross-link note — no double-count ([JD-FL-1/4](decisions.md)).** Pluvial `[F]` and coastal `[C]` are **also
> secondary perils of the deferred hurricane**: a tropical cyclone drives surge **and** rainfall **and** river rise at
> once (compound flooding). The reserved **`event_family_id`** (JD-FL-4) is the hook that, when hurricane lands, binds
> a TC-driven surge/rain event to its parent storm so **one event is counted once** — not separately in the flood and
> hurricane pipelines (`[REF]` §7: *"use one surge source across both perils and avoid double-counting"*). This hook is
> now **realized**: coastal is **built** (compound-Poisson surge×wind per-subsystem on `event_family_id`, JD-FL-12) and
> **joined to hurricane** on that key rather than built standalone in isolation. The pluvial/rain leg of the
> same hook is **deferred** ([JD-FL-17](decisions.md)).

---

## How layer-0 feeds the pipeline

This layer fixes the **definition**; the (already-built) downstream layers consume it.

**→ M0 (input data)** ([m0_input_data.md](m0_input_data.md)) — the evidence already met this definition:

```text
   FEMA NFHL        regulatory flood zones (1% / 0.2%) — site screening (in the SFHA?)
   FEMA BLE         riverine RP depth grids (100-yr + 500-yr + 10% extent) — the pre-integrated depth surface
   USGS NLDI→NSS    regional-regression flow-frequency Q(T) — densifies the lower RPs (10/25/50-yr)
   NOAA Atlas 14    precipitation-frequency (24-hr depth by RP) — the pluvial frequency backbone
   3DEP DEM / lidar ground elevation — converts water-surface elevation to depth above the asset
   EIA-860 / HIFLD  asset + substation registry — which sites; where the low node is
   SLOSH            coastal surge — shared from hurricane (built; joined on event_family_id)
```

Honest M0 flags this layer mandates: **no free pluvial *depth* product exists** (the blind spot — model it from Atlas
14); **BLE gives only the 1% + 0.2% tail points** (lower RPs densified, JD-FL-8); **datum** must reconcile to NAVD88
(VDatum, AFL-13); **climate non-stationarity** (Atlas 14 aging; Atlas 15 ~Sept 2026) carried as an overlay.

**→ M1 (catalog)** ([m1_catalog.md](m1_catalog.md)) — **one notebook per sub-peril over both assets** (JD-FL-10/19):
**riverine** = read the BLE RP surface (profile-assembly) + regression densification; **pluvial** = Atlas 14 → SCS-CN
→ runoff; **coastal** = SLOSH surge. Each emits the **asset-independent field** tagged `sub_peril`, with a reserved
`event_family_id` (JD-FL-4); the field→asset reduction is **not** done here. The **RP basis** stays with M1 (it sets
the annual-max loss); the **damage-onset depth** travels to M3.

**→ M2 (coupling)** ([m2_coupling.md](m2_coupling.md)) — **site-conditioned** (bucket 3); M2 **does the coupling**
(JD-FL-19) — it samples the M1 field at the asset: areal inundated mean (solar) or per-node depth (wind), DEM-modulated.

**→ M3 (damage)** ([m3_damage.md](m3_damage.md)) — the **anchored** `infrasure-damage-curves` depth-damage curve
(`DR ≈ 0` below the component pad/`x0`, rising with depth, capping at submersion).

**→ M4 (loss & metrics)** ([m4_loss_metrics.md](m4_loss_metrics.md)) — **annual-maximum MC** on the shared engine,
sub-perils **co-sampled comonotonic + worse-source-wins** (headline) with the additive-capped **envelope** recorded;
every metric off the **sampled** distribution, **% of TIV alongside dollars**, never the expected-loss shortcut.

---

## Decisions & assumptions surfaced (this layer)

- **Decisions** ([decisions.md](decisions.md)): flood = a **sub-peril family** (R/F/C, dual-test split), **all three
  built**, coastal joined to hurricane on `event_family_id` (JD-FL-1/12) · depth source per sub-peril — BLE-preferred riverine
  (JD-FL-6) + lower-RP densification (JD-FL-8) + Atlas 14 → SCS-CN pluvial (JD-FL-9) · the catalog forked at M1 with a
  reserved `event_family_id` (JD-FL-4/10) · annual-maximum event model (JD-FL-7) · sub-peril combine = co-sample +
  worse-source-wins headline + additive envelope, **flood maxes (wind adds)** (JD-FL-11) · site-conditioned coupling
  for all sub-perils · pre-integrated BLE surface as the riverine tail (profile-assembly) · the two-threshold
  (RP basis vs damage-onset depth) split; coastal compound-Poisson surge×wind joined to hurricane (JD-FL-12); the
  shared-M0/M1 + M2-coupling structure (JD-FL-19). Logged **JD-FL-1…19** (+ the wind-cell **JD-FL-W1…W7**).
- **Assumptions** ([assumptions.md](assumptions.md)): depth product = FEMA BLE (AFL-6), lower RPs densified (AFL-12),
  datum via VDatum + climate/levee overlays (AFL-13) · pluvial = Atlas 14 → SCS-CN, **no depth anchor — the blind
  spot** (AFL-P1/P2) · coupling = `depth = WSE − ground(DEM)`, site-conditioned, micro-elevation load-bearing
  (AFL-3/4/7) · damage = anchored `infrasure-damage-curves` curve, equipment-submersion cap (AFL-8/15/W8) · event
  model = annual-maximum (AFL-17) · combine = co-sample + worse-source-wins + envelope (AFL-P3/W12) · physical loss
  only, BI excluded (AFL-2/19). Logged **AFL-1…19**, **AFL-P1…3**, **AFL-W1…12**.

**Next → [M0 (input data)](m0_input_data.md):** the raw evidence (FEMA NFHL / BLE, Atlas 14, 3DEP DEM) met against the
definitions oriented here (already built, M0→M4).
