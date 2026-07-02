# M4 — Loss & metrics (shared engine, all three sub-perils combined)

*The finale. The M3 conditional losses sample into **one** annual-loss distribution per site, and every metric is read
off that **one sampled distribution**, never the expected-loss shortcut. The **basics-spot-on** core (the step the old
model got wrong). The engine is reused unchanged from hail / wildfire / wind — flood specializes the **event model**
(annual-maximum inland, compound-Poisson coastal) and the **sub-peril combine** (worse-source-wins inland; per-subsystem
max for surge × wind). **One notebook** ([`01_loss_metrics`](01_loss_metrics.ipynb)) runs both frames under one roof and
sums them.*

**Where this sits:** M3 (damage) → **M4 (loss & metrics)**. Plan:
[`docs/plans/flood/m4_loss_metrics.md`](../../../../docs/plans/flood/m4_loss_metrics.md).

> **Two event-frames, one total.** **Inland** (riverine + pluvial) is annual-maximum worse-source-wins. **Coastal** is
> **compound-Poisson** — it joins the surge leg to the hurricane-wind leg on `event_family_id` and combines them **per
> subsystem** ([JD-FL-12](../../../../docs/plans/flood/decisions.md): `max` on the shared PV-array/substation, additive
> elsewhere). **Total flood = inland + coastal** (independent streams summed). Sites carry whatever sub-perils they
> have — absent sub-perils enter the engine as 0; **LA3 West Baton Rouge** is the all-three combine site.

## The inland engine (riverine + pluvial)
One **annual-maximum Monte Carlo** (N = 500k years — [JD-FL-7](../../../../docs/plans/flood/decisions.md)). Flood is
modeled as ~**1 damaging flood/year** (*not* compound-Poisson multi-event). Build a **loss-exceedance curve** from the
M3 conditional losses (a 5-point RP curve after the JD-FL-8 densification: 100/500-yr **real BLE**, 10/25/50-yr a
**regression rating anchored to both BLE depths**); each year draws `AEP ~ U(0,1)` → `loss(AEP)` by **log-AEP
interpolation** (bounded extrapolation below 0.002) → per-year loss vectors → EAL / VaR / PML / TVaR (% of TIV + $).

**Sub-peril combine ([JD-FL-11](../../../../docs/plans/flood/decisions.md)):** draw **one** annual AEP `u` per year,
read **both** sub-peril curves at `u` (co-sample **comonotonic** — one shared storm); the year's flood loss =
**max(loss_riverine(u), loss_pluvial(u))** (same ground drowns once) — the **headline**. The **additive-capped**
`min(TIV, L_r + L_p)` is recorded as the upper sensitivity **envelope**. Marginals kept. *(Flood **maxes**;
convective-wind **adds** — its sub-perils hit different subsystems. Intentional.)*

## The coastal stream (surge × hurricane wind)
Compound-Poisson at `λ_surge`: per qualifying storm, combine the **surge** leg (M3 coastal surge loss) and the
**hurricane-wind** leg (hurricane × solar, `data/hurricane/tc_m3_damage.parquet`) **per subsystem** — `combined_DRₛ =
max(wind_DRₛ, surge_DRₛ)`, joined on `event_family_id` ([JD-FL-12](../../../../docs/plans/flood/decisions.md)). Shared
subsystems = **PV_ARRAY + SUBSTATION**; wind-only = MOUNTING; surge-only = INVERTER / ELECTRICAL / CIVIL. One shared
storm draw → the per-realization compound ≥ each leg.

## Results (real, record-limited; total flood = inland + coastal, % of TIV)
| site | sub-perils | inland EAL | coastal EAL | **total EAL** | PML100 | PML500 |
|---|---|---|---|---|---|---|
| **LA3 West Baton Rouge** (all-three) | R + F + C | 0.653 | 0.107 | **0.761** | 7.00 | **12.24** |
| **Discovery Solar Center** (coastal) | C | 0.000 | 0.338 | **0.338** | 9.35 | **38.72** |
| **Elizabeth Solar Plant** (inland) | R + F | 0.163 | 0.000 | **0.163** | 2.60 | 4.26 |
| **Hayhurst Texas Solar** (dry) | R + F | 0.030 | 0.000 | **0.030** | 0.28 | 0.61 |

- **Inland is riverine-dominated.** Once ponding is grounded in 1 m lidar (closed-depression `f`, JD-FL-15), pluvial is
  small at every RP: Elizabeth riverine 0.163 vs pluvial ≈ 0; LA3 riverine 0.653 vs pluvial 0.026. Elizabeth carries a
  real riverine flood tail; Hayhurst (desert) is correctly near-zero.
- **Coastal compound is material on both legs.** Discovery: wind-only 0.251 + surge-only 0.140 → compound **0.338**; LA3:
  wind-only 0.093 + surge-only 0.020 → compound 0.107. The per-subsystem max lifts the compound above each marginal.
- **LA3 is the headline all-three site** — `max(riverine,pluvial)` annual-max (0.653) + coastal surge×wind compound
  (0.107) sum to total **0.761%** of TIV.

## The doctrines, demonstrated
- **PML anchored to real BLE.** By construction the inland percentiles reproduce the *worse* sub-peril's `Lₜ` at
  100/500-yr (a frame known-answer ✓) — **PML solid**. EAL is softer (it rests on the densified lower RPs, JD-FL-8) —
  stated honestly.
- **Riverine-led inland.** With ponding lidar-grounded, riverine outweighs pluvial at the inland sites — marginals are
  reported alongside the worse-wins headline.
- **Method 0 refused** for the tail — every metric off the **sampled** distribution, never the expected-loss collapse.

## External validation (sanity-check ✅)
- **USGS high-water marks** (Aug-2016 LA flood, runs in the notebook): surveyed marks near the proving site read
  ~0–7.9 ft (median ~2.1 ft); the modeled riverine depths (~1.0–1.75 ft across 10→500-yr) fall **inside** that range — a
  real-event regime check (regional, confirms the *scale*, not a to-the-inch calibration).
- **EAL** → implied AAL inside the **NFIP SFHA norm (0.5–1.5%/yr)** for the exposed area; **depth-damage** tracks HAZUS
  norms. Internal frame checks (PML100 = VaR99; PML monotone with RP) pass — no red flags.

## Inputs → outputs
M3 conditional losses (inland RP + coastal per-storm) + the hurricane wind leg + geometry (TIV) →
`data/flood/flood_solar_m4_metrics_manifest.json` (EAL/VaR/PML/TVaR in $ and % of TIV + marginals + envelope + coastal
compound + total) + `<site>_flood_solar_m4_annual_vectors[_total].parquet` (per-sim-year loss); the loss-metrics figure is shown inline.

## Metric schema (house standard — parity with hail / wildfire / convective-wind)
The manifest carries **two twin blocks with identical keys**, the block name carrying the unit: **`metrics_usd`** and
**`metrics_pct_of_tiv`**, each keyed **per site** on the **TOTAL flood** (inland + coastal). Keys: `EAL` ·
`VaR95 (AEP-PML20)` · `VaR99 (AEP-PML100)` (this *is* PML100) · `VaR99.6 (AEP-PML250)` · `PML500 (AEP-99.8)` (flood's
existing 500-yr point) · `TVaR99` · `OEP-PML100`. **AEP** = annual aggregate; **OEP** = occurrence basis. For the mixed
total the per-year occurrence set = *{inland annual-max as ONE occurrence}* ∪ *{each coastal storm's compound loss}*, so
**OEP_total = max(inland, largest coastal storm)** while **AEP_total = inland + Σ coastal storms** (no extra sampling — a
second reduction of the same MC draw). **Inland-only sites → OEP == AEP** (annual-max is one occurrence/yr; LA3/Discovery
show OEP-PML100 < AEP-PML100). Checks added: AEP ≥ OEP, OEP-PML100 ≤ AEP-PML100, TVaR99 ≥ VaR99, monotone + unit-consistency.

## Decisions & assumptions
[JD-FL-7](../../../../docs/plans/flood/decisions.md) (annual-max MC) · [JD-FL-8](../../../../docs/plans/flood/decisions.md)
(lower-RP densification) · [JD-FL-11](../../../../docs/plans/flood/decisions.md) (co-sample + worse-source-wins +
envelope) · [JD-FL-12](../../../../docs/plans/flood/decisions.md) (coastal per-subsystem surge×wind) ·
[JD-FL-17](../../../../docs/plans/flood/decisions.md) (unified all-three solar M4, LA3). Assumptions **AFL-17**
(annual-max), **AFL-18** (densified lower RPs), **AFL-16** (TIV basis), **AFL-19** (duration/BI unmodeled).

**→ Flood × solar M0→M4 is COMPLETE.** Deferred: claims-calibrated curves · regression-Q SE as an MC overlay · the PV
flood-stow lever · duration / business-interruption · full per-storm three-way Level-1 combine (inland event-ified).

## Method In Plain English: Conditional Losses Become Annual Metrics

M4 is where return-period losses and event losses become an annual loss distribution. Metrics are then read from that
distribution, not from a shortcut average.

Inland flood is sampled as one annual-maximum flood severity:

```text
one simulated year
        |
        v
draw u between 0 and 1
        |
        v
read riverine loss at AEP = u
read pluvial  loss at AEP = u
        |
        v
inland loss = max(riverine, pluvial)
```

Why `max` inland:

```text
same asset, same wet ground, same year
riverine and pluvial are alternative water sources in the annual flood frame
do not double-damage the same equipment
```

Coastal is sampled as a storm count plus storm severities:

```text
one simulated year
        |
        v
draw number of qualifying coastal storms ~ Poisson(lambda)
        |
        v
for each storm:
  pick event/category from catalog
  join surge and hurricane wind on event_family_id
  combine shared subsystems by max(wind_DR, surge_DR)
        |
        v
coastal annual loss = sum(compound storm losses)
```

Total flood:

```text
total annual loss = inland annual-max loss + coastal annual compound loss
```

Then the metric readout is standard:

```text
EAL       = mean(annual losses)
VaR99    = 99th percentile annual loss
PML100   = same annual-exceedance idea as VaR99
PML500   = 99.8th percentile / 500-year point where available
TVaR99   = mean of the tail beyond VaR99
OEP      = largest occurrence in the year, not the aggregate
```

For inland-only sites, AEP and OEP are effectively the same because there is one annual-maximum occurrence. For mixed
coastal sites, AEP can exceed OEP because several coastal storms can occur in the same simulated year.

## What Solar M4 Asks

```text
solar M4 asks, over many simulated years:
  what inland severity is drawn this year?
  what is riverine loss at that severity?
  what is pluvial loss at that severity?
  after worse-source-wins, what is inland loss?
  how many coastal storms occur this year?
  for each coastal storm, what surge and wind loss share event_family_id?
  what is total annual loss?
```

Then it asks the metric questions:

```text
  what is the mean annual loss?
  what is the 99th percentile annual loss?
  what is the 500-year point?
  what is the tail mean beyond VaR99?
  what is the largest occurrence loss in each year?
```
