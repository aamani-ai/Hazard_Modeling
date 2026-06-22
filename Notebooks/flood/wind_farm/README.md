# Flood × Wind-farm — the asset cell (M2 → M3 → M4)

Built end-to-end (M0→M4), notebooks-first, every layer known-answer-checked. The flood **engine** on the **wind-farm
asset** — a sparse turbine point-cloud, not a dense areal footprint like solar — covering all three sub-perils
(riverine + pluvial annual-max, JD-FL-7; coastal surge × hurricane wind, compound-Poisson). One unified notebook per
layer.

> **M0/M1 are shared at the peril level (JD-FL-19).** Site screening/geometry and the per-sub-peril hazard **field**
> live in [`../m0_input_data/`](../m0_input_data/) and [`../m1_catalog/`](../m1_catalog/) over **both assets**; this
> folder holds only the wind-specific **M2–M4**. The M0/M1 rows below link to those shared notebooks for context.

**Assets (three wind farms, all three sub-perils):**
- **Green River IL** (~74 turbines, ~$272M TIV) — Green River valley · **riverine + pluvial** (~60% turbines in SFHA;
  the collector substation floods).
- **Shepherds Flat OR** (~384 turbines) — mapped-dry **baseline** (0% in SFHA; outside Atlas-14 → pluvial 0).
- **Amazon Wind US East NC** (~104 turbines, ~$291M TIV) — Albemarle Sound · **all three sub-perils** (76% turbines
  surge-exposed at Cat-3 + 11% in Zone A + pluvial).

| Layer | Notebook | What |
|---|---|---|
| M0 *(shared)* | [`../m0_input_data/02_wind_sites`](../m0_input_data/02_wind_sites.ipynb) | Locks all wind flood sites: SFHA-fraction sweep (selection evidence) → **Green River IL** (~60% SFHA) + **Shepherds Flat OR** (dry) with USWTDB turbine clouds, convex-hull boundary, collector substation & TIV; coastal screen → **Amazon Wind US East NC** (the all-three wind site, 76% turbines Cat-3 surge-exposed). |
| M1 (riverine, *shared*) | [`../m1_catalog/riverine/01_catalog`](../m1_catalog/riverine/01_catalog.ipynb) | Wind sites use **`sfha_bathtub`** — 1% **flood-area + boundary WSE contour** off 3DEP (JD-FL-W4) + **USGS-NWIS gauge** Log-Pearson III `Q(T)` (JD-FL-W5). The per-node bathtub is sampled in **M2** (JD-FL-19). |
| M1 (pluvial, *shared*) | [`../m1_catalog/pluvial/01_catalog`](../m1_catalog/pluvial/01_catalog.ipynb) | Emits the asset-independent **Atlas-14 → SCS-CN runoff `Q`** per site. Per-node pad-gated ponding (`f`+`d_cap` from 1 m lidar, JD-FL-15/W6) is computed in **M2**: lidar `d_cap` < pads → **floor pluvial ≈ 0**. |
| M1 (coastal, *shared*) | [`../m1_catalog/coastal/01_catalog`](../m1_catalog/coastal/01_catalog.ipynb) | Amazon Wind event catalog: **24 RAFT storms** (≤50 km, ≥64 kt), λ≈0.0116/yr from HURDAT2, each stamped `event_family_id`. SLOSH-MOM surge by category sampled per node in **M2**. |
| M2 | [`m2_coupling/01_coupling`](m2_coupling/01_coupling.ipynb) | **Per-node site-conditioned** coupling, **all three sub-perils** (one notebook): reads the shared M1 fields (filtered to wind), samples each node — riverine bathtub per turbine, pluvial pad-gated lidar ponding, coastal SLOSH surge per node + the substation. Loss summed over flooded nodes, **not areal**. |
| M3 | [`m3_damage/01_damage`](m3_damage/01_damage.ipynb) | **Greenfield** flood × wind curve (**source-agnostic** — applied to all three sub-perils): rotor/nacelle/tower **flood-immune** (0.63 of value); base vulnerable (~0.37) — foundation + electrical + civil + substation. A fully-flooded turbine loses ≤28%. Vendored. |
| M4 | [`m4_loss_metrics/01_loss_metrics`](m4_loss_metrics/01_loss_metrics.ipynb) | **Inland**: annual-max MC → riverine + pluvial worse-source-wins (JD-FL-11). **Coastal**: compound-Poisson surge × hurricane wind per subsystem (`max(wind_DR, surge_DR)`, joined on `event_family_id`). **Total = inland + coastal.** EAL/VaR/PML/TVaR, % TIV; **FEMA NRI**-validated. |

## Headline numbers (real, record-limited; total flood = inland + coastal)
| | Sub-perils | Inland EAL | Coastal EAL | **Total EAL** | PML100 | PML500 | TIV | Turbines |
|---|---|---|---|---|---|---|---|---|
| **Green River IL** (riverine) | R + F | 1.276% | — | **1.276%** | 10.89% | 11.42% | ~$272M | 74 |
| **Amazon Wind US East** (all-three) | R + F + C | 0.056% | 0.013% | **0.069%** | 0.47% | 1.43% | ~$291M | 104 |
| **Shepherds Flat OR** (dry) | R + F | 0.000% | — | **0.000%** | 0.00% | 0.00% | ~$1183M | 384 |

- **Green River is riverine-dominated** — the farm's **own west-edge 138 kV collector substation** sits in the river
  valley and **floods** (0.88–1.00 m from the 10-yr on), carrying **~75% of the headline EAL**. The **turbines-only
  floor** (collector excluded) is EAL **0.31%** / PML500 ~3.2% — the with-vs-without bracket. The collector is found
  generically as the in-hull `substation=generation` node (portfolio-scalable, JD-FL-W7). Externally validated vs
  **FEMA NRI** (~13× Lee Co. avg riverine rate; NRI 0.93 floods/yr ≈ our annual-max).
- **Amazon Wind is the all-three site** — inland riverine + pluvial (0.056) plus coastal surge × wind compound (0.013)
  sum to total **0.069%**. Coastal surge is **spatially broad but rare** (Cat-3 floods 64 of 104 turbines, but
  λ≈0.0116/yr); the worst storm reaches ~14% of TIV. Per-subsystem combine: wind-only 0.012 + surge-only 0.003 →
  compound 0.013 (the max-on-shared-subsystem lift).
- **Shepherds Flat is a true zero** — mapped-dry, and outside Atlas-14 coverage (PNW = Atlas 2) so pluvial is set to 0
  (a low-rainfall control, AFL-W11).

## Three keeper findings
1. **Wind mostly avoids floodplains** — the median wind project has ~0% of turbines in the SFHA; flood is a minor
   peril for wind. *But a minority straddle river floodplains or surge-exposed coasts* — Green River IL (~60% in the
   SFHA) and Amazon Wind NC (76% surge-exposed). (JD-FL-W2.)
2. **Wind flood is capped at the turbines, but the collector carries it** — rotor/nacelle/tower (0.63 of value) are
   flood-immune (a fully-inundated turbine loses only ~28%), so the **turbines-only floor is small (EAL 0.31% at Green
   River)**. The farm's **own collector substation** (~9% of TIV, steep curve) sits in the valley and **floods** → it
   dominates the headline. **Getting the substation *location* right is load-bearing** (the `substation=generation`
   node inside the turbine hull, JD-FL-W7).
3. **Pluvial is even smaller than riverine for wind — the pad, not the floodplain, sheds the rain (JD-FL-W6 +
   JD-FL-15).** Turbines sit on raised ~0.30 m pads; with `f` + `d_cap` grounded per node from 1 m lidar, the terrain
   depression depth `d_cap` (~0.07–0.09 m) sits **below the pads** → **floor pluvial ≈ 0 at every node**. The headline
   stays **riverine-dominated** — the clean asset contrast to **flood × solar**, which is likewise riverine-led once
   ponding is lidar-grounded.

Plan: [`docs/plans/flood/m_wind_farm.md`](../../../docs/plans/flood/m_wind_farm.md) · Decisions: JD-FL-W1…7 (+
JD-FL-9/10/11/12/15) · Assumptions: AFL-W1…12.
