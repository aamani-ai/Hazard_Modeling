# M3 — Damage (the greenfield per-node curve)

*The damage layer — turns each M2 per-node **flood depth (ft above ground)** into a **capex-weighted damage ratio**, then
sums loss over the flooded turbines + the shared substation. Unlike flood × solar (which draws the canonical
`infrasure-damage-curves` set), flood × wind has **no library curve yet**, so M3 builds a **greenfield** flood × wind
curve here and vendors it — capex weights from the convective-wind `wind_config`, shapes borrowed from the solar flood
library + a foundation curve by judgment (low–medium confidence). **One notebook** ([`01_damage`](01_damage.ipynb))
prices all three sub-perils with the same curve.*

**Where this sits:** M2 (coupling) → **M3 (damage)** → M4 (loss). Plan:
[`docs/plans/flood/m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

> **Curve = source-agnostic.** **One curve applies to all three sub-perils** — inundation is inundation, the equipment
> doesn't care whether the water came from river, sky, or sea. Riverine/pluvial are priced per return period; coastal
> surge is priced per storm (by hurricane category), `event_family_id`-stamped.

## The capex split — flood-immune top, vulnerable base
One turbine's value splits rotor (0.26) / nacelle (0.21) / tower (0.16) / foundation (0.12) / electrical (0.09) / civil
(0.07); the shared **substation** = 0.09. The **height inversion at its limit**: rotor + nacelle + tower (**0.63** of
value) sit 80–140 m up on a sealed steel tower → **flood-immune (DR 0)**. Flood reaches only the **base** — foundation +
down-tower electrical + civil (**0.28** of a turbine) + the collector substation (**0.09**). So even a **fully-inundated
turbine loses ≤ ~28%** — flood is **capped per turbine**, and the **substation** carries the steep loss.

## The recipe + the per-node curves
Per-subsystem logistic `DR(x) = L/(1+exp(-k(x-x0)))` on **flood depth (ft) above grade**, **anchored** so `DR(0) = 0`.
Vulnerable subsystems (shapes borrowed from the solar flood library; foundation by judgment):

| subsystem | L | k | x0 (ft) | reading |
|---|---|---|---|---|
| electrical | 0.90 | 3.0 | 0.75 | down-tower switchgear drowns shallow (≈ solar inverter) |
| substation | 0.95 | 2.5 | 1.5 | collector transformer / switchgear (≈ solar substation) |
| civil | 0.70 | 1.2 | 2.0 | pad / road scour |
| foundation | 0.40 | 0.8 | 3.0 | massive RC pier — only deep/sustained flood scours/saturates it |

Loss rule: `loss = (1/N)·Σ_i Σ_s∈{found,elec,civil} wₛ·DRₛ(dᵢ)·TIV + w_sub·DR_sub(d_sub)·TIV` — node-summed over the
flooded turbines + the shared substation.

## What `01_damage` finds
- **Anchored:** `DR(0) = 0`. **Immune top:** even at 10 ft a turbine DR ≤ ~0.28. **Inversion:** electrical (x0 0.75)
  drowns before substation (1.5) before civil (2) before foundation (3).
- **Riverine** Green River grows 100→500-yr and ≫ the dry Shepherds Flat baseline; loss is driven by the in-valley
  collector substation on its steep curve.
- **Pluvial is the smaller peril, confirmed at the loss layer** — with `f`+`d_cap` lidar-grounded every node is pad-shed
  → pluvial conditional loss = **0** (water-limited floor).
- **Coastal (Amazon Wind)** — the same curve over the per-node SLOSH depths gives a per-category loss ladder; surge
  floods most of the farm and the collector at Cat-3+, so per-storm coastal loss far exceeds Amazon's riverine/pluvial,
  but only in rare strong storms (the event frame).

## Inputs → outputs
M2 per-node depth tables (riverine + pluvial + coastal) + the M0 site/TIV record → greenfield curve vendored to
`data/flood/damage_curves/flood_wind_asset_capex_weighted.json` + `data/flood/flood_wind_m3_damage_manifest.json`
(RP rows + coastal per-storm rows) + `<slug>_flood_wind_coastal_m2_*` per-storm losses; the damage curve is shown inline.

## Decisions & assumptions
Curve = **greenfield** flood × wind, capex-weighted, source-agnostic across all three sub-perils (graduates to the
library later) · capex from convective-wind `wind_config` · shapes from `infrasure-damage-curves` RIVERINE_FLOOD × solar
+ foundation by judgment · rotor/nacelle/tower **flood-immune** · pluvial pad-shed (JD-FL-15/W6) · combine deferred to M4
([JD-FL-11](../../../../docs/plans/flood/decisions.md) inland worse-wins; [JD-FL-12](../../../../docs/plans/flood/decisions.md)
coastal surge×wind). Plan: [`m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

**Next → M4 (loss & metrics):** the conditional losses through the shared engine → EAL / VaR / PML / TVaR (% of TIV) —
inland annual-max worse-source-wins, coastal compound-Poisson surge × hurricane-wind, total = inland + coastal.
