# M4 — Loss & metrics (shared engine, all three sub-perils combined)

*The finale. The M3 per-node conditional losses sample into **one** annual-loss distribution per site, and every metric
is read off that **one sampled distribution**, never the expected-loss shortcut. The engine is reused unchanged from
hail / wildfire / solar — flood × wind specializes the **event model** (annual-maximum inland, compound-Poisson coastal)
and the **combine** (worse-source-wins inland; per-subsystem max for surge × wind). **One notebook**
([`01_loss_metrics`](01_loss_metrics.ipynb)) runs both frames under one roof and sums them.*

**Where this sits:** M3 (damage) → **M4 (loss & metrics)**. Plan:
[`docs/plans/flood/m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

> **Two event-frames, one total.** **Inland** (riverine + pluvial) is annual-maximum worse-source-wins. **Coastal** is
> **compound-Poisson** — it joins the surge leg to the hurricane-wind leg on `event_family_id` and combines them **per
> subsystem** ([JD-FL-12](../../../../docs/plans/flood/decisions.md): `combined_DRₛ = max(wind_DRₛ, surge_DRₛ)`).
> **Total flood = inland + coastal** (independent streams summed). Sites carry whatever sub-perils they have — absent
> sub-perils enter the engine as 0; **Amazon Wind US East** is the all-three combine site.

## The inland engine (riverine + pluvial)
One **annual-maximum Monte Carlo** (N = 500k years — [JD-FL-7](../../../../docs/plans/flood/decisions.md), ~1 damaging
flood/year). Build a per-`(site, sub-peril)` loss-exceedance curve from M3 (riverine 10/25/50/100/250/500-yr,
**gauge-grounded** JD-FL-W5; pluvial Atlas-14, pad-gated), with a 5-yr onset anchor; each year draws `AEP ~ U(0,1)` →
`loss(AEP)` by log-AEP interpolation → EAL / VaR / PML / TVaR (% of TIV + $).

**Sub-peril combine ([JD-FL-11](../../../../docs/plans/flood/decisions.md)):** one annual AEP `u` per year, read **both**
sub-peril curves at `u` (co-sample **comonotonic**); the year's flood loss = **max(riverine, pluvial)**. The
**additive-capped** envelope is recorded as the upper sensitivity bound. *(Flood **maxes**; convective-wind **adds**.)*

**Substation bracket (JD-FL-W7):** the headline is bracketed by a **turbines-only floor** (collector excluded). Green
River's **own** west-edge 138 kV collector (the in-hull `substation=generation` node) sits in the valley → it **floods**
and carries ~75% of EAL, so the full headline sits well above the turbines-only floor.

## The coastal stream (surge × hurricane wind)
Compound-Poisson at `λ_surge`: per qualifying storm, combine the **surge** leg (M3 coastal node losses) and the
**hurricane-wind** leg (hurricane × wind-farm, `data/hurricane/tc_windfarm_m3_damage.parquet`) **per subsystem** —
`max(wind_DRₛ, surge_DRₛ)`, joined on `event_family_id`. Both legs share the 7-subsystem capex split; shared subsystems =
**electrical + substation**; wind-only = rotor + nacelle; surge-only = foundation + civil.

## Results (real, record-limited; total flood = inland + coastal, % of TIV)
| site | sub-perils | inland EAL | coastal EAL | **total EAL** | PML100 | PML500 |
|---|---|---|---|---|---|---|
| **Green River IL** (riverine) | R + F | 1.276 | — | **1.276** | 10.89 | **11.42** |
| **Amazon Wind US East** (all-three) | R + F + C | 0.056 | 0.013 | **0.069** | 0.47 | 1.43 |
| **Shepherds Flat OR** (dry) | R + F | 0.000 | — | **0.000** | 0.00 | 0.00 |

- **Green River is riverine-dominated** — the farm's own valley-bottom collector substation floods (0.88–1.00 m from
  the 10-yr on) and carries **~75% of the headline EAL**. The turbines-only floor (collector excluded) is EAL ~0.31% /
  PML500 ~3.2% — the with-vs-without bracket. FEMA-NRI validated (~13× the Lee Co. avg riverine rate; NRI ~0.93
  floods/yr ≈ our annual-max).
- **Amazon Wind is the all-three site** — inland riverine + pluvial (0.056) plus coastal surge × wind compound (0.013)
  sum to total **0.069%**. Coastal surge is **spatially broad but temporally rare** (Cat-3 floods ~62% of turbines, but
  λ≈0.0116/yr); the worst storm reaches ~14% of TIV.
- **Shepherds Flat is a true zero** — mapped-dry, and outside Atlas-14 coverage (PNW = Atlas 2) so pluvial is set to 0.

## The doctrines, demonstrated
- **PML anchored.** The inland combined PML@T reproduces the *worse* sub-peril's `Lₜ` by construction (here riverine
  wins) — a frame known-answer ✓.
- **Pluvial confirmed negligible for wind** — lidar-grounded `f`+`d_cap` (JD-FL-15) puts the depression depth below the
  pads → floor 0 at every node; the headline stays **riverine-dominated** (the clean asset contrast to solar, also
  riverine-led).
- **Method 0 refused** — every metric off the **sampled** distribution.

## External validation (sanity-check ✅)
**FEMA National Risk Index** (Riverine Flooding EAL, Lee County IL — an independent HAZUS-based model): Green River's
combined EAL ≈ the riverine EAL ≈ **~13× the county average** rate (order-consistent for a high-exposure, valley-bottom
site), and NRI's annualized riverine frequency (~0.93/yr) ≈ our annual-maximum (~1/yr).

## Inputs → outputs
M3 conditional losses (RP + coastal per-storm) + per-node coastal SLOSH tables + the hurricane wind leg + the coastal
event rate λ → `data/flood/flood_wind_m4_metrics_manifest.json` (EAL/VaR/PML/TVaR in $ and % of TIV + marginals +
envelope + substation bracket + coastal compound + total) + `<slug>_flood_wind_m4_annual_vectors[_total].parquet`; the loss-metrics figure is shown inline.

## Decisions & assumptions
[JD-FL-7](../../../../docs/plans/flood/decisions.md) (annual-max MC) ·
[JD-FL-11](../../../../docs/plans/flood/decisions.md) (co-sample + worse-source-wins + envelope) ·
[JD-FL-12](../../../../docs/plans/flood/decisions.md) (coastal per-subsystem surge×wind) ·
[JD-FL-W5](../../../../docs/plans/flood/decisions.md) (gauge-grounded riverine RP curve) ·
[JD-FL-W7](../../../../docs/plans/flood/decisions.md) (the in-hull flooding collector) · JD-FL-15 (lidar-grounded
pluvial floor). Plan: [`m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

**→ Flood × wind-farm M0→M4 is COMPLETE.** Deferred: the greenfield curve graduating to the library · Rank-1
volume-pour pluvial · full per-storm three-way Level-1 combine (inland event-ified, JD-FL-17) · duration / BI.
