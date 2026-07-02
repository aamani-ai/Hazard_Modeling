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
- **Green River** is the flood site: riverine grows monotonically 100→500-yr, turbines are partially exposed, and the
  mapped collector/dependency node in the valley floods. Whether that node becomes direct physical loss is an M3/TIV
  scope decision, not an M2 fact. **Shepherds Flat** is the dry baseline (0% in SFHA → riverine 0; outside Atlas-14 →
  pluvial 0).
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

## Method In Plain English: Each Node Reads Its Own Water

M2 for wind is not an areal-average step. It is a node sampling step.

```text
wind farm nodes:

T = turbine
S = collector substation

        T1             T2

              T3

        S              T4

flood field sits underneath these points
```

The `S` node is found before M2 from the turbine cloud plus OSM/HIFLD substations:

```text
1. build a buffered convex hull around USWTDB turbine points
2. query nearby OSM/HIFLD substations
3. choose the farm collector:
   - best: OSM substation=generation inside hull
   - allowed: OSM generation substation near this farm's turbines (<0.6 km)
   - fallback: any in-hull OSM/HIFLD substation
   - last resort: turbine-cloud centroid, flagged weak
```

This is deliberately stronger than "nearest substation to centroid"; clustered wind regions can have neighboring farms
with nearby collectors. The hull is a containment guard, not an official lease boundary and not an areal
flood-averaging object. It also does not prove physical-loss ownership. M2 can report the collector as an exposed
dependency node; M3 should price it as wind-farm physical damage only when the collector is confirmed inside the
project's TIV / insured value schedule.

For each node and each flood severity, M2 computes an effective depth:

```text
effective_depth = flood_water_depth_at_node - pad_height

if effective_depth < 0:
  effective_depth = 0
```

Riverine:

```text
water surface at return period T
minus ground elevation at node
minus pad height
equals node depth
```

Pluvial:

```text
runoff source Q(T)
plus local lidar depression storage
minus raised pad
equals node ponding depth
```

Coastal:

```text
SLOSH surge by storm/category
sampled at turbine and substation nodes
minus pad height
equals per-storm node depth
```

The M2 summary rows intentionally keep turbine and substation signals separate:

```text
n_flooded:
  how many turbines have effective depth > 0

flooded_fraction:
  n_flooded / total turbines

turb_depth_mean_m:
  mean effective turbine depth among flooded turbines

substation_depth_m:
  effective depth at the collector substation
```

This distinction is important because turbine tops are mostly flood-immune, while the collector substation is low,
electrical, and steeply vulnerable in M3.

## What Wind M2 Asks

```text
wind M2 asks, for each node:
  is the node inside or reached by the flood field?
  what is the water depth at the node?
  what pad height should be subtracted?
  is effective depth above zero?
  is this a turbine node or the collector substation?
```

At the farm summary level it asks:

```text
  how many turbines flood?
  what fraction of turbines flood?
  what is the mean depth among flooded turbines?
  what is the substation depth?
```

It does not ask what those depths cost. M3 handles damage.
