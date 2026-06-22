# M2 — Coupling (per-node site-conditioned, all three sub-perils)

*M2 turns the M1 hazard fields into the **coupling contract** M3 consumes — which nodes flood and how deep. Flood is
**site-conditioned (bucket 3)**, driven throughout by inundation **depth (ft above ground)**. Unlike solar's dense areal
footprint, a wind farm is a **sparse point-cloud** — each turbine and the collector substation reads its **own local
depth, pad-gated**. **One notebook** ([`01_coupling`](01_coupling.ipynb)) samples all three sub-perils — riverine +
pluvial + coastal — at every node.*

**Where this sits:** [M1 catalog](../../m1_catalog/README.md) → **M2 (coupling)** → [M3 damage](../m3_damage/README.md)
→ [M4 loss](../m4_loss_metrics/README.md). Plan:
[`docs/plans/flood/m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

> **Per-node, not areal.** Where solar couples by areal inundated fraction over a polygon, wind couples **node by node**:
> sample the depth field at each turbine + the substation, subtract the **pad height** (turbine pad ~0.30 m, substation
> ~0.15 m), and keep the effective depth at that node. Loss in M3 is then **summed over the flooded nodes**, never an
> areal average. The pad is load-bearing — raised pads shed shallow water (*standard interface, not standard physics* —
> [P1](../../../../docs/principles/hazard_asset_specificity.md)).

## The three sub-perils, one notebook (JD-FL-19)
- **Riverine** — sample the 1% **water-surface contour** at each node, `depth = WSE + ΔWSE(T) − ground − pad`, gated to
  the SFHA; `ΔWSE(T)` ratings off the site's **own USGS-NWIS gauge** `Q(T)` (Log-Pearson III, JD-FL-W5). A per-node
  bathtub. Return-period (annual-max) frame.
- **Pluvial** — each pad's own **1 m-lidar** window → closed-depression `f` + depression-depth cap `d_cap`; ponding
  `= min(r·Q/f, d_cap)`; node equipment depth `= max(pond − pad, 0)`. The raised pads shed the shallow ponding
  (JD-FL-W6 / JD-FL-15 — pluvial negligible for wind). Return-period frame. Lidar cached.
- **Coastal** — sample the **SLOSH MOM** surge field at each node, **per hurricane category**, pad-gated → per-storm
  surge, `event_family_id`-stamped. The SLOSH LZW tiles are read via a **GDAL-decompressed (DEFLATE, cached)** copy so
  this runs in the hazard env without `imagecodecs`. Event-based frame; inland-only sites are skipped.

**Sites:** Green River IL + Shepherds Flat OR (inland) · Amazon Wind US East NC (all three sub-perils — riverine +
pluvial + coastal surge).

## The contract M2 emits
**Inland (per site × return period × sub-peril):** per-node depth tables (`*_flood_wind_m2_<sub>_depths.parquet`)
summarised to `n_flooded`, `flooded_fraction`, `turb_depth_mean_m`, `substation_depth_m`.

**Coastal (per site × hurricane category × storm):** per-node SLOSH depth table + per-storm `flooded_fraction`,
`turb_depth_mean_m`, `substation_depth_m`, `event_family_id` — the M4 coastal-compound input.

## What `01_coupling` finds
- **Green River** is the flood site: riverine grows monotonically 100→500-yr, the farm's **own collector substation**
  (in the valley) floods; **Shepherds Flat** is the dry baseline (0% in SFHA → riverine 0; outside Atlas-14 → pluvial 0).
- **Amazon Wind coastal surge is spatially broad** — Cat-3 floods ~62% of turbines — but only in the rare strong storms.
- **Pluvial is pad-shed:** lidar `d_cap` sits below the pads → ponding floor ≈ 0 at every node.
- **Known-answer checks pass:** riverine high site grows 100→500-yr; the baseline is dry; coastal node-flood ladder
  rises with category.

## Inputs → outputs
M1 catalog manifests (riverine field + gauge, pluvial runoff, coastal storm catalog) + USGS EPQS ground elevations +
1 m-lidar (TNM) + SLOSH MOM tiles → `data/flood/flood_wind_m2_coupling_manifest.json` (RP rows + coastal per-storm rows
+ node-flood ladder) + per-node depth parquets; the coupling figure is shown inline.

## Key decisions & assumptions
Coupling = **site-conditioned per node** · per-node coupling moved M1→M2
([JD-FL-19](../../../../docs/plans/flood/decisions.md)) · riverine `sfha_bathtub` + gauge `Q(T)` (JD-FL-W4/W5) · pluvial
pad-gated lidar `f`+`d_cap` (JD-FL-15/W6) · coastal SLOSH-MOM source ([JD-FL-14](../../../../docs/plans/flood/decisions.md))
· **value = node-summed, not areal** (the wind contrast to solar). Plan:
[`m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

**Next → M3 (damage):** the source-agnostic greenfield depth-damage curve over each node depth, summed over flooded
turbines + the substation.
