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

Plain-English reading of AFL-14:

```text
wet area fraction ~= wet value fraction

M2 does not know exact inverter pads, transformer pads, substation footprint, cable routes, or module-block layout.
It emits an areal exposure fraction, and M3 applies the full representative solar component mix to that exposed share.
```

So if 20% of the footprint is wet, the model treats that as 20% of the plant's representative value mix being wet, not
as "only the PV modules are wet" or "only the inverter pad is wet." This is a V1 simplification and the main reason a
future sub-asset layout would improve solar flood coupling.

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

## Method In Plain English: Raster Or Field Meets Solar Polygon

M2 is the first layer where the solar plant shape matters. M1 may know a flood depth at many pixels, but M2 asks which
of those pixels fall inside the solar footprint.

```text
M1 riverine depth field

    0   0   0   0   0
    0   0  0.2 0.3 0
    0  0.1 0.4 0.5 0
    0   0  0.2 0.3 0
    0   0   0   0   0

Solar polygon mask

        +-------------+
        |  cells in   |
        |  footprint  |
        +-------------+

M2 keeps only cells inside the polygon.
```

Then M2 reduces the inside-polygon cells to three numbers:

```text
wet cells = cells inside polygon with depth > 0

exposure_fraction = count(wet cells) / count(all inside-polygon cells)
conditional_depth = mean(depth of wet cells)
depth_max         = max(depth inside polygon)
```

Tiny worked example:

```text
inside-polygon depths in meters:

0.00  0.00  0.40
0.20  0.50  0.00

all cells = 6
wet cells = 3

exposure_fraction = 3 / 6 = 0.50
conditional_depth = (0.40 + 0.20 + 0.50) / 3 = 0.367 m
depth_max         = 0.50 m
```

Those are not three versions of the same thing. They answer different questions:

```text
exposure_fraction:
  "How much of the plant is touched by water?"

conditional_depth:
  "Where water exists, how deep is it?"

depth_max:
  "What is the deepest local tail inside the footprint?"
```

For the Elizabeth riverine example, the coupled curve is roughly:

```text
Return period   exposure_fraction   conditional_depth
10-year         10.2%               0.307 m
25-year         13.2%               0.359 m
50-year         15.4%               0.396 m
100-year        17.7%               0.433 m
500-year        21.8%               0.532 m
```

Read the 100-year row as:

```text
At the 100-year riverine flood,
about 17.7% of the solar footprint is wet,
and the wet part averages about 0.433 m of water.
```

The value-damage calculation happens later. M2 only emits the exposure/depth contract. M3 applies the solar damage curve
to the conditional depth, and M4 samples the annual distribution.

## What Solar M2 Asks

```text
solar M2 asks, inside the polygon:
  which pixels are wet?
  how many pixels are wet?
  what share of the polygon is wet?
  what is the average depth of the wet pixels?
  what is the max depth?
  which sub-peril produced the row?
  is the row return-period based or event-based?
```

It does not ask:

```text
  how fragile is the inverter?
  what is the dollar loss?
  how often does the annual loss exceed a threshold?
```

Those are M3 and M4 questions. M2 is only the asset-contact layer.
