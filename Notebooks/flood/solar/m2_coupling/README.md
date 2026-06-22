# M2 — Coupling (site-conditioned, all three sub-perils)

*M2 turns the M1 hazard fields into the **coupling contract** M3 consumes — how much of the plant floods (**exposure**)
and how deep, given flooded (**conditional severity**). Flood is **site-conditioned (bucket 3)** — the field × per-asset
susceptibility, *not* hail's areal hit-or-miss — driven throughout by inundation **depth (ft above ground)**. **One
notebook** ([`01_coupling`](01_coupling.ipynb)) samples all three sub-perils — riverine + pluvial + coastal — at the
solar footprint.*

**Where this sits:** [M1 catalog](../../m1_catalog/README.md) → **M2 (coupling)** → [M3 damage](../m3_damage/README.md)
→ [M4 loss](../m4_loss_metrics/README.md). Plan:
[`docs/plans/flood/m2_coupling.md`](../../../../docs/plans/flood/m2_coupling.md).

> **Why bucket 3.** Coupling = *how the hazard reaches the asset*. For flood that is the **depth field met against
> equipment elevation** — the asset is never "missed" (if it's in the floodplain it floods), it reads its **own local
> depth**, modulated by micro-topography. No Minkowski, no hit-or-miss. M2 formalizes **areal exposure** + **conditional
> depth**; the per-subsystem **height conditioning** (effective depth = depth − mount height) lives in **M3** alongside
> the per-subsystem fragility, keeping M2 a clean exposure × severity emitter (*standard interface, not standard
> physics* — [P1](../../../../docs/principles/hazard_asset_specificity.md)).

## The three sub-perils, one notebook (JD-FL-19)
- **Riverine** — areal sampling of the **full-resolution BLE depth field** over the footprint: mask the field to the
  polygon, then reduce to an inundated fraction + inundated-cell mean depth. The lower return periods (10/25/50-yr) are
  densified from the M1 flow-frequency `Q(T)` rating, anchored to both the 100/500-yr BLE depths
  ([JD-FL-8](../../../../docs/plans/flood/decisions.md)). Return-period (annual-max) frame.
- **Pluvial** — pour the M1 runoff `Q` over the footprint's **1 m-lidar closed depressions** (The National Map 1 m DEM):
  the ponding fraction `f` (low-lying share of the pad) is the exposure; the wet-cell depth `= r·Q/f`, capped at the
  lidar depression depth. Return-period frame. `f` is lidar-grounded (AFL-P2).
- **Coastal** — areal **SLOSH MOM** surge over the footprint, **per hurricane category, per storm** → footprint-mean
  depth + inundated fraction, `event_family_id`-stamped (the M4 coastal-compound input). The SLOSH LZW tiles are read
  via a **GDAL-decompressed (DEFLATE, cached)** copy so this runs in the hazard env without `imagecodecs`. Event-based
  frame.

**Sites:** Hayhurst + Elizabeth + LA3 (inland: riverine + pluvial) · Discovery + LA3 (coastal). LA3 West Baton Rouge is
the all-three combine site; each site carries whatever sub-perils it has.

## The contract M2 emits

**Inland (per site × return period × sub-peril):**

| field | meaning | from M1 |
|---|---|---|
| `exposure_fraction` | fraction of the footprint (≈ value, AFL-14) inundated | inundated-cell count / footprint |
| `conditional_depth_m` | representative depth **given** inundated (the "severity") | inundated-cell mean |
| `depth_max_m` | footprint max depth (tail) | field max in footprint |

**Coastal (per site × hurricane category × storm):** footprint-mean surge, inundated fraction, conditional depth,
`event_family_id` — written to per-site `*_flood_solar_coastal_m2_coupling.parquet`.

**No double-count:** the conditional depth is the **inundated-cell mean** (not the footprint average, which already
folds exposure in) — M3 multiplies exposure × conditional-depth separately. **Value ∝ area** (AFL-14): areal inundation
proxies the fraction of asset *value* exposed (subsystems assumed spread uniformly over the footprint).

## What `01_coupling` finds
- **Exposure and conditional depth grow monotonically** with return period at the inland flood sites; both ≫ Hayhurst
  (the dry baseline) — the low-vs-high contrast carries through coupling.
- **Coastal SLOSH footprint-mean ladder:** Discovery Cat-5 ≈ **12.4 ft**, LA3 Cat-5 ≈ **14.5 ft** — the deep-surge
  regime that drives the coastal compound in M4.
- **Sub-peril key + `event_family_id`** carried into the manifest (JD-FL-4) so M4 can combine without double-counting.
- **Known-answer checks pass:** exposure + depth non-decreasing 100→500-yr at the high site; Hayhurst exposure×depth ≪
  high site; no double-counting (conditional depth = inundated-cell mean, exposure applied separately).

## Inputs → outputs
M1 catalog manifests (riverine + pluvial fields, coastal storm catalog) + 1 m-lidar DEMs (TNM) + SLOSH MOM tiles →
`data/flood/flood_solar_m2_coupling_manifest.json` (sub-peril-keyed RP rows + coastal site summary) +
`<slug>_flood_solar_coastal_m2_coupling.parquet` (per-storm); the coupling figure is shown inline.

## Key decisions & assumptions
Coupling = **site-conditioned** ([AFL-3](../../../../docs/plans/flood/assumptions.md), A21 §2.3) ·
**`depth = WSE − ground(DEM)`**, micro-elevation load-bearing (AFL-4/7) · **value ∝ area** (AFL-14) · per-node/footprint
coupling moved M1→M2 ([JD-FL-19](../../../../docs/plans/flood/decisions.md)) · sub-peril family schema (AFL-11) · coastal
SLOSH-MOM source ([JD-FL-14](../../../../docs/plans/flood/decisions.md)). Plan:
[`m2_coupling.md`](../../../../docs/plans/flood/m2_coupling.md).

**Next → M3 (damage):** the source-agnostic depth-damage curve on the conditional depth, capex-weighted —
`conditional_loss = exposure × Asset_DR(depth) × TIV`.
