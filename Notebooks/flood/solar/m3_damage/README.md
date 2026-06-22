# M3 — Damage (the anchored depth-damage curve)

*The damage layer — turns the M2 coupled **flood depth (ft above ground)** into a **capex-weighted subsystem damage
ratio**, then `conditional_loss = exposure × Asset_DR(conditional_depth) × TIV`. Unlike convective-wind's greenfield
turbine curve, flood × solar uses the **canonical `infrasure-damage-curves` RIVERINE_FLOOD × solar** set — the same
library every peril draws from — so the curve is real (medium confidence), not built from scratch. **One notebook**
([`01_damage`](01_damage.ipynb)) prices all three sub-perils with the same curve.*

**Where this sits:** M2 (coupling) → **M3 (damage)** → M4 (loss). Plan:
[`docs/plans/flood/m3_damage.md`](../../../../docs/plans/flood/m3_damage.md).

> **Curve = canonical, source-agnostic.** The library carries a RIVERINE_FLOOD × solar set
> (the infrasure-damage-curves library, priority 4). The **same depth-damage curve applies to all three sub-perils** (riverine,
> pluvial *and* coastal surge): water has no memory of its source — depth → damage is depth → damage. Riverine/pluvial
> are priced per return period; coastal surge is priced per storm (by hurricane category), `event_family_id`-stamped.

## The recipe (house-standard, all perils)
- Per-subsystem logistic `DRᵢ(x) = Lᵢ/(1+exp(-kᵢ(x-x0ᵢ)))` on **flood depth (ft) above ground**, **anchored** so
  `DR(0) = 0`.
- `Asset_DR(x) = Σ wᵢ·DRᵢ(x)` with **NREL capex weights** (peril-independent, vendored). Subsystems with no flood
  curve → **0** (flood-immune).
- `conditional_loss = exposure_fraction × Asset_DR(conditional_depth) × TIV` (no double-count — M2 split exposure from
  conditional depth).

## The flood inversion (why `x0` matters)
The library bakes **component elevation into `x0`** — so **no separate mount-height step is needed**; the height
inversion (base electrical drowns shallow, elevated panels survive) *is* the curve:

| subsystem | L | k | x0 (ft) | reading |
|---|---|---|---|---|
| INVERTER_SYSTEM | 0.95 | 3.5 | **0.75** | pad-mounted → drowns shallow (the dominant loss) |
| SUBSTATION | 0.95 | 2.5 | 1.5 | transformer oil contamination |
| PV_ARRAY (SAT horiz.) | 0.9 | 1.8 | 2.5 | panels survive shallow; **flood-stow x0 7 ft = a mitigation lever** |
| CIVIL_INFRA | 0.7 | 1.2 | 2.0 | scour / roads |
| ELECTRICAL (cables) | 0.55 | 1.0 | 3.0 | underground → resilient |
| MOUNTING, SCADA | — | — | — | no curve → flood-immune (0) |

## What `01_damage` finds
- **Anchored:** `DR(0) = 0`; the curve leaves zero only as water reaches the inverter pad (~0.75 ft), then rises and
  caps (panels ride high) — the two-threshold story made concrete.
- **Inland conditional loss** grows monotonically 100→500-yr and the inland flood sites dominate the Hayhurst baseline.
  Tracks HAZUS electrical/contents norms (inverter heavy damage by 1–3 ft).
- **Coastal per-storm surge damage** from the same curve over the deep SLOSH depths **saturates**: Discovery max event
  ≈ **52% of TIV**, LA3 max event ≈ **52% of TIV** (deep-surge floods most subsystems). Per-storm losses are written
  `event_family_id`-stamped for the M4 coastal-compound join.
- **Confidence: medium**; **duration / business-interruption unmodeled** (Gen-1); `value ∝ area` exposure inherited
  from M2.

## Inputs → outputs
M2 coupling (inland RP rows + coastal per-storm parquets) + the canonical curve set + NREL capex weights → curve
vendored to `data/flood/damage_curves/flood_solar_asset_capex_weighted.json` +
`data/flood/flood_solar_m3_damage_manifest.json` + `<slug>_flood_solar_coastal_m3_surge_loss.parquet` (per storm); the damage curve (depth → Asset_DR) is shown inline.

## Decisions & assumptions
Curve = canonical `infrasure-damage-curves` RIVERINE_FLOOD × solar ([AFL-8](../../../../docs/plans/flood/assumptions.md)),
source-agnostic across all three sub-perils · **PV variant = single-axis horizontal stow**, flood-stow a mitigation
lever (AFL-15) · **TIV** from $/MW (Hayhurst hail basis $1.483 M/MW; Elizabeth/LA3 estimated by capacity, AFL-16) ·
duration/BI unmodeled (AFL-19).

**Next → M4 (loss & metrics):** feed the conditional losses through the shared engine → EAL / VaR / PML / TVaR (% of
TIV) — inland annual-max worse-source-wins, coastal compound-Poisson surge × hurricane-wind, total = inland + coastal.
