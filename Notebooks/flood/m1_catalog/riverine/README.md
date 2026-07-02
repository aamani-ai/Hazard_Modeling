# M1 — Riverine `[R]` catalog (the asset-independent flood-depth field)

*The **riverine branch** of the M1 fork: build the flood-depth **field** — inundation **depth (ft above ground)**
indexed by annual return period — for **every flood site of both assets** in one pass, picking the depth method
per site by data availability. The field is asset-independent; sampling it at the solar footprint (areal) or each
wind turbine (per-node) is **M2's** job (JD-FL-19).*

**Where this sits:** [M0 evidence](../../m0_input_data/README.md) → **M1 (catalog — riverine fork)** → M2 coupling →
M3 damage → M4 loss. Parent: [`m1_catalog/`](../README.md). Sibling forks: [`pluvial/`](../pluvial/README.md) ·
[`coastal/`](../coastal/README.md). Plan: [`m1_catalog.md`](../../../../docs/plans/flood/m1_catalog.md). Notebook:
[`01_catalog`](01_catalog.ipynb) (built).

## Method — per-site by data availability ([JD-FL-6](../../../../docs/plans/flood/decisions.md))

| method | when | field emitted | `Q(T)` source (lower RPs) |
|---|---|---|---|
| **`ble_image`** | a FEMA **BLE** depth grid covers the site | native-resolution depth raster ([JD-FL-18](../../../../docs/plans/flood/decisions.md)) | USGS **NLDI→NSS** regression ([JD-FL-8](../../../../docs/plans/flood/decisions.md)) |
| **`sfha_bathtub`** | only **SFHA Zone A** is mapped (no BLE grid) | 1% flood-area polygon + boundary water-surface contour off **3DEP** ([JD-FL-W4](../../../../docs/plans/flood/decisions.md)) | per-site USGS gauge **Log-Pearson III** ([JD-FL-W5](../../../../docs/plans/flood/decisions.md)) |
| **`dry`** | site outside the SFHA | — (structural zero) | — |

BLE carries the 1% (100-yr) + 0.2% (500-yr) tail; the lower RPs (10/25/50-yr) are **densified** from `Q(T)` + a
BLE-anchored rating (JD-FL-8). **Magnitude metric:** riverine flood **depth (ft above ground)** at return period —
the inundation depth the M3 curve consumes.

## What `01_catalog` found
- **`ble_image` (BLE + NLDI→NSS):** the solar sites — **Elizabeth** (Q₁₀₀ ≈ 854 cfs) and **LA3 West Baton Rouge**
  (Q₁₀₀ ≈ 2,610 cfs); **Hayhurst** reads the dry control.
- **`sfha_bathtub` (NFHL flood-area + 3DEP WSE + NWIS gauge):** the wind sites — **Green River** (gauge 05447000,
  Q₁₀₀ ≈ 7,055 cfs) and **Amazon Wind Farm US East** (gauge 0204382800, Q₁₀₀ ≈ 2,946 cfs). **Shepherds Flat** = `dry`.
- The JD-FL-8 rating exponent is **near-invariant to channel slope** (sensitivity-tested), so the densified lower-RP
  depths rest on real flow-frequency, not a flat-onset guess.
- **Known-answer checks pass:** depth rises monotonically with return period; dry sites read ≈ 0 at all RPs; RP labels
  map to AEP (100-yr = 1%).

## Inputs → outputs
FEMA BLE depth grids + FEMA NFHL + USGS 3DEP + USGS NLDI→NSS / NWIS gauges → one method-tagged **field** manifest
`data/flood/flood_riverine_m1_catalog_manifest.json` (rows tagged `asset` + `method`; `flow_frequency` for
`ble_image` sites, `gauge` for `sfha_bathtub` sites). Large flood-area polygons are written to gitignored
`data/flood/raw/flood_area/<slug>.wkt` and referenced by path; BLE rasters cached under `data/flood/raw/`.
`event_family_id` is **reserved** (unused for riverine).

## Decisions & assumptions
[JD-FL-6](../../../../docs/plans/flood/decisions.md) (BLE-preferred / bathtub fallback) ·
[JD-FL-8](../../../../docs/plans/flood/decisions.md) (lower-RP densification) ·
[JD-FL-W4/W5](../../../../docs/plans/flood/decisions.md) (Zone-A bathtub + gauge LP3) ·
[JD-FL-18](../../../../docs/plans/flood/decisions.md) (full-res BLE image) ·
[JD-FL-19](../../../../docs/plans/flood/decisions.md) (M1 = field, M2 = coupling). Assumptions **AFL-6/12/13**
(riverine source, lower-RP densify, datum) · **AFL-W5** (per-site gauge). Register:
[`assumptions.md`](../../../../docs/plans/flood/assumptions.md).

**Next → M2 (coupling):** each asset samples this field at its footprint — solar = areal inundated fraction ×
conditional depth; wind = per-node bathtub depth.

## Method In Plain English: `Q`, `D`, And The Rating Bridge

Riverine M1 uses two related but different quantities:

```text
Q(T) = river discharge / flow at return period T
       usually reported in cubic feet per second (cfs)
       tells us how much water is moving through the river system

D(T) = flood depth above local ground at return period T
       reported in feet or meters
       tells us how much water sits over the asset location
```

They are connected, but they are not the same:

```text
river cross-section view

            higher Q means a higher water surface
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  water surface, larger flood
             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  water surface, smaller flood
        ____/                                      \____ ground/channel

        Q = volume moving through the section per time
        D = vertical water depth above the asset ground
```

Where FEMA BLE gives real depth rasters, the strongest anchors are:

```text
D100 = depth from FEMA BLE 100-year raster
D500 = depth from FEMA BLE 500-year raster
```

The notebook still needs lower return periods for EAL, especially 10/25/50-year. Those are inferred with a monotone
rating bridge anchored to the BLE depths:

```text
D(T) = D100 * ( Q(T) / Q100 )^p

p is chosen so the same curve also matches D500.
```

Read the formula as:

```text
If Q50 is below Q100, then D50 should be below D100.
If Q500 is above Q100, then D500 should be above D100.
The BLE 100/500 depth rasters pin the curve at the important tail points.
```

ASCII shape:

```text
depth
  ^
  |                                x  BLE D500 anchor
  |
  |                    .
  |              .
  |        x  BLE D100 anchor
  |    .
  +-------------------------------------------------> discharge Q
       Q10     Q25     Q50     Q100           Q500
```

For the `sfha_bathtub` method, the source does not provide a BLE depth raster. M1 carries the flood-area/WSE evidence
and a gauge-grounded `Q(T)` curve; M2 then builds the per-node depth by comparing water surface, ground elevation, and
pad height.

The important confidence split:

```text
100/500-year BLE depths:
  strongest, because the raster is direct depth evidence

10/25/50-year densified depths:
  useful, but softer, because they depend on the Q(T)->D(T) bridge

dry rows:
  structural zeros only when the site is outside the mapped source in a way the notebook can defend
```

## What Riverine M1 Asks

```text
riverine M1 asks, for each site:
  is FEMA BLE depth available?
  if yes:
    what are the 100-year and 500-year depth rasters?
    what Q(T) curve lets us infer 10/25/50-year depths?
  if no BLE:
    is the site in SFHA Zone A?
    what WSE/ground/gauge evidence supports a bathtub fallback?
  if outside mapped flood evidence:
    is this a defensible structural dry row?
```

It does not ask:

```text
  how many solar pixels are wet?
  which wind turbines are wet?
  what is the damage ratio?
```

Those are M2 and M3 questions.
