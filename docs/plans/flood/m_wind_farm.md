# Plan: Flood × Wind-farm cell (built)

*The second asset for the flood peril — **built end-to-end (M0→M4)**, originally sequenced after the solar cell.
Mirrors the flood × solar build (M0→M4) but on the **wind-farm** asset — a
**sparse turbine point-cloud over a huge lease**, not a dense areal footprint. Reuses the flood engine (JD-FL-7
annual-max MC) and the convective_wind wind-farm asset template (USWTDB cloud + capex curve), with a genuinely new
M2 (per-node coupling) and M3 (greenfield flood × wind curve).*

> **Status: built end-to-end (M0→M4), gauge-grounded + externally validated, riverine + pluvial + coastal (parity with
> flood × solar — coastal × wind = **Amazon Wind Farm US East NC**, JD-FL-12…17); substation ownership resolved (JD-FL-W7).**
> High site **Green River, IL** (Lee Co., 74 turbines,
> ~194 MW, **60% of turbines in the SFHA**) + baseline **Shepherds Flat, OR** (reused, **mapped-dry**). **Green River
> combined EAL 1.27% / PML100 10.9% / PML500 11.4% TIV** — driven by the farm's **own collector substation**, which
> sits in the river valley and **floods** (0.88 m @ 100-yr; ~75% of EAL). **Turbines-only floor** (collector excluded)
> = EAL 0.31% / PML500 3.2% (the with-vs-without bracket). Adding pluvial doesn't move it — now on **1 m-lidar-grounded
> `f`** (JD-FL-15 ported): pluvial marginal EAL **0.000%** (water-limited floor; was 0.0007% under the f=0.40 guess;
> JD-FL-W6). Riverine RP curve grounded in a real USGS Log-Pearson III flood-frequency
> (JD-FL-W5); **substation = the farm's OWN west-edge 138 kV collector** found generically — the in-hull
> `substation=generation` node (JD-FL-W7, **portfolio-scalable**); validated vs FEMA NRI (~13× Lee Co. avg; 0.93
> floods/yr ≈ annual-max). **Correction:** the earlier "substation real & **dry** → EAL 0.31% / no load-bearing
> assumption" used the **adjacent Big Sky Wind farm's** collector by mistake (nearest-to-centroid bug); the substation
> *location method* was load-bearing and is now fixed. Decisions: (JD-FL-W1…W7, + JD-FL-9/10/11, the coastal decisions
> JD-FL-12…17 (incl. coastal × wind), and the flood-structure decisions JD-FL-18/19).

## The findings that shaped the build

1. **Wind mostly avoids floodplains — but not always (JD-FL-W2, corrected).** Unlike a solar farm (one contiguous
   footprint that floods as a unit), wind turbines are sited on **high ground**, so the **median** wind project has
   **~0% of turbines in the 1% SFHA** (both the TX and Midwest fleets). Flood is a **minor** peril for wind. *But a
   minority genuinely straddle river floodplains, in both regions* — **Green River, IL (~60%)** and **Lane City, TX
   (~42%, Colorado River)** lead. An earlier draft over-claimed "**TX wind is flood-immune (0/2,976 wet)**" — that was
   a **BLE-depth false zero** (the exposed TX sites are Zone A with no BLE coverage; BLE-NoData ≠ dry), caught and
   corrected by the `00_screening_sweep` reproducibility notebook.
2. **The exposed wind farms are Zone A (no BLE depth) — in both regions (JD-FL-W3/W4).** So the BLE-sampling path that
   worked for the solar high site (Elizabeth) **fails here**; depth comes from JD-FL-6's *national fallback* (an
   **extent-based bathtub** off 3DEP + gauge flow-frequency). **Green River is the high site because it is the *most*
   exposed**, not because TX is immune — TX's Lane City would serve equally under the same method.

## Phase breakdown (built)

| Phase | M-step | What we built | Notebook | Status |
|------:|--------|---------------|----------|--------|
| 1 | M0 *(shared)* | Wind site screen + geometry: Midwest river-corridor SFHA screen → **Green River**; reuse **Shepherds Flat**; USWTDB turbine clouds; convex-hull boundary; **collector substation = the farm's OWN in-hull `substation=generation` node** (portfolio-scalable; JD-FL-W7); TIV ($/kW). | `m0_input_data/02_wind_sites` | ✅ |
| 0 | M0 *(shared)* | **Screening sweep** (reproducibility artifact): TX-immune (0% in floodplain) + Midwest pick (Green River 60%) — the evidence behind site selection. | `m0_input_data/02_wind_sites` | ✅ |
| 2 | M1 (riverine, *shared*) | **Field**, method-per-site (JD-FL-19): wind sites use **`sfha_bathtub`** — emit the 1% flood-area + boundary WSE contour off 3DEP (JD-FL-W4) + **gauge** Log-Pearson III `Q(T)` (10/25/50/100/250/500; JD-FL-W5). The per-node bathtub (`WSE+ΔWSE(T)−ground−pad`) is sampled in **M2**. | `m1_catalog/riverine/01_catalog` | ✅ |
| 2b | M1 (pluvial, *shared*) | **Field**: asset-independent Atlas-14 → SCS-CN **runoff `Q`** per site. The per-node pad-gated ponding moved to **M2** (JD-FL-19): **`f` + `d_cap` grounded per node from 1 m lidar** (JD-FL-15/W6), `pond = min(r·Q/f, d_cap)`, node depth = `max(pond − pad, 0)`. The pad is the gate → **floor pluvial = 0** (lidar `d_cap` ~0.07–0.09 m < pads). **Regime water-limited** (ρ up to ~490 ≫ 1) → floor is a lower bound, but the no-drainage ceiling (Q ≤ 0.16 m) is still pad-shed and the valley substation is riverine-flooded → pluvial immaterial; **Rank-1 deferred**. | `m1_catalog/pluvial/01_catalog` | ✅ |
| 3 | M2 | **Per-node site-conditioned** coupling, **both sub-perils** (one code path) — which turbines flood + how deep, + the substation. Loss summed over flooded nodes, **not areal**. | `wind_farm/m2_coupling/01_coupling` | ✅ |
| 4 | M3 | **Greenfield flood × wind curve** (**source-agnostic** — applied to both sub-perils) — rotor/nacelle/tower **flood-immune** (0.63, DR 0); base vulnerable (~0.37); shapes borrowed from flood×solar + a foundation judgment. Vendored. | `wind_farm/m3_damage/01_damage` | ✅ |
| 5 | M4 | **Annual-max MC** (JD-FL-7) → **combine riverine + pluvial worse-source-wins** (JD-FL-11) → EAL/VaR/PML/TVaR, %TIV. **Real collector substation FLOODS** (JD-FL-W7) → collector-dominated headline (~75% of EAL) + turbines-only floor bracket; **FEMA NRI** external validation. | `wind_farm/m4_loss_metrics/01_loss_metrics` | ✅ |

## Key methods (vs flood × solar)

- **Asset geometry:** USWTDB turbine point cloud + a **convex-hull** boundary (the `renewablesinfo_org` boundary-DB
  symlink is absent here; the hull is the honest extent for a point cloud — AFL-W4). Baseline reuses convective_wind's
  cached boundary-DB polygon.
- **Depth (M1):** **extent-based bathtub** — Zone A has no BFE and no BLE, so the 1% floodplain *boundary* is the 1%
  water-surface contour; `depth = WSE(median of nearest SFHA-edge 3DEP samples) − turbine_ground − pad`. Sampled **at
  each turbine** (a point cloud), not over an areal footprint. Medium-low confidence (flat-water over a sloping Zone A
  floodplain) — StreamStats+HAND / detailed-study BFE is the documented upgrade.
- **Coupling (M2):** **per-node site-conditioned** — exposure = the identity + depth of **flooded turbines** + the
  substation; loss is a **sum over flooded nodes**, not solar's areal `exposure_fraction × conditional_depth`.
- **Damage (M3):** **greenfield** (no flood × wind in `infrasure-damage-curves`). Capex weights from the old-repo
  `wind_config`; rotor/nacelle/tower **immune** (elevated → DR 0); base vulnerable; curve shapes borrowed from the
  flood × solar library + a foundation-scour judgment. **Flood is a capped peril for wind** — a fully-inundated
  turbine loses only ~28% of its value (the immune top is 0.63).
- **Pluvial (M1, JD-FL-W6 + JD-FL-15):** Atlas 14 → SCS-CN, but **per node** and **pad-gated**, with **`f` + `d_cap`
  grounded per node from 1 m lidar** (closed-depression; JD-FL-15 ported from solar to wind): `pond = min(r·Q/f,
  d_cap)`, node depth = `max(pond − pad, 0)`. Per-node lidar (vs solar's per-footprint) fits the sparse 88 km² cloud —
  uplands `f≈0.005`, valley substation `f≈0.018`, `d_cap` ~0.07–0.09 m. The grounded `d_cap` sits **below the pads** →
  **floor pluvial = 0** (the flat `f=0.40` had given a 500-yr substation trace). **Regime test:** Green River is
  **water-limited** (ρ = Q/(f·d_cap) up to ~490 ≫ 1), so the closed-depression floor is a **lower bound** — but the
  no-drainage **ceiling** (full runoff Q ≤ 0.16 m) is still **pad-shed** (turbines dry), and the one run-on-receiving
  node, the valley substation, is **already riverine-flooded 0.88 m** → worse-source-wins makes pluvial **immaterial**.
  So the **Rank-1 volume-pour is deferred** (parity with solar; its payoff is at pluvial-driven water-limited sites).
- **Loss (M4):** the **same** JD-FL-7 annual-max MC + **JD-FL-11 worse-source-wins combine** as solar — the only
  difference is upstream (per-node summed L₁₀₀/L₅₀₀ + the collector). Pluvial being negligible, the combine is
  **riverine-dominated** (raised pads shed the sheet ponding a flat solar footprint catches), and within riverine the
  **collector substation dominates** (~75% of EAL).

## Honest limits (carried) / upgrades (seam-ready)

- **Substation: RESOLVED + method fixed (JD-FL-W7, corrects AFL-W5).** The collector is the farm's **OWN** node, found
  generically: the OSM **`substation=generation` substation INSIDE the turbine hull** (portfolio-scalable; fallbacks
  gen-adjacent → any-in-hull → HIFLD-in-hull → centroid; + name-mismatch guard). For Green River it is the **west-edge
  138 kV collector**, in the river valley → it **FLOODS** (0.88 m @ 100-yr) → ~75% of EAL → **headline EAL 1.27% /
  PML500 11.4%**. The previous "nearest-to-centroid" pick had grabbed the **adjacent Big Sky Wind farm's** (dry)
  collector — a wrong-substation bug (that node is `in_hull=False`). Bracket kept: **turbines-only floor** (collector
  excluded) = EAL 0.31% / PML500 3.2%. Residual: the collector depth is still the Zone-A bathtub (see next bullet).
- 1% bathtub depth (Zone A) is medium-low confidence → **StreamStats+HAND / detailed BFE** is the upgrade. The **RP
  rises are now gauge-grounded** (JD-FL-W5) — the residual is only the rating exponent `b` (sensitivity-tested).
- Greenfield M3 curve → graduates to `infrasure-damage-curves`; only the **foundation** curve is judgment
  (substation/civil are exact library component curves). Pad elevations assumed (AFL-W6); hull boundary; $/kW TIV.

## Files

- `decisions.md` — JD-FL-W1 (sites/baseline reuse), JD-FL-W2 (wind-avoids-floodplains finding; *corrected* the
  TX-immune overstatement), JD-FL-W3 (Green River = most-exposed high site), JD-FL-W4 (extent-based bathtub depth),
  JD-FL-W5 (gauge-grounded RP curve + NRI validation), JD-FL-W6 (per-node pad-gated pluvial + JD-FL-11 combine;
  confirmed negligible), **JD-FL-W7 (substation = the farm's OWN in-hull `generation` collector — corrects the
  nearest-to-centroid wrong-substation bug; the real collector floods → EAL 0.31% → 1.27%)**. Shared: JD-FL-9
  (pluvial method), JD-FL-10 (sub-peril fork), JD-FL-11 (combine), **JD-FL-15 (lidar-grounded pluvial `f`+`d_cap`;
  ported to wind — floor pluvial = 0, water-limited regime flagged, Rank-1 deferred)**.
- `assumptions.md` — AFL-W1…W12 (W10–W12 = wind pluvial: per-node pad-gating, the Atlas-14 PNW coverage gap, the combine).
