# M1 — Pluvial `[F]` catalog (the asset-independent rainfall-runoff field)

*The **pluvial branch** of the M1 fork: build the rainfall-runoff **source field** — SCS-CN runoff `Q` by annual
return period — for **every flood site of both assets** in one pass, with **one method everywhere**. Pluvial is
**the blind spot**: no free pluvial *depth* grid exists, so depth is **modeled**, not measured. The per-asset
ponded inundation depth (lidar ponding-fraction `f` / depression depth-cap) is derived in **M2** (JD-FL-19).*

**Where this sits:** [M0 evidence](../../m0_input_data/README.md) → **M1 (catalog — pluvial fork)** → M2 coupling →
M3 damage → M4 loss. Parent: [`m1_catalog/`](../README.md). Sibling forks: [`riverine/`](../riverine/README.md) ·
[`coastal/`](../coastal/README.md). Plan: [`m1_catalog.md`](../../../../docs/plans/flood/m1_catalog.md). Notebook:
[`01_catalog`](01_catalog.ipynb) (built).

## Method — Atlas 14 → SCS-CN, everywhere ([JD-FL-9](../../../../docs/plans/flood/decisions.md))
1. **Frequency** = **NOAA Atlas 14** point precipitation-frequency, **24-hr depth** at each RP (HDSC text service).
2. **Runoff** = **SCS Curve Number** (CN = 80, graded solar / soil-C): `Q = (P − 0.2S)²/(P + 0.8S)`, `S = 1000/CN − 10`.
3. **Field emitted** = the runoff `Q(site, RP)` — the *source term*. **Ponding** (`f`, depth-cap) is **M2's** job.

**Magnitude metric:** pluvial **runoff depth `Q`** (→ ponded inundation **depth, ft above ground** in M2) at return
period. Sites outside Atlas 14 coverage (Pacific NW = NOAA Atlas 2) → pluvial **0** (a low-rainfall control, not a
true zero).

## What `01_catalog` found
- 100-yr runoff `Q`: **Elizabeth ≈ 0.284 m · LA3 ≈ 0.247 m · Green River ≈ 0.113 m · Amazon ≈ 0.180 m.**
- **Shepherds Flat** is outside Atlas 14 (PNW) → pluvial **0** (AFL-W11).
- **Screening-grade** — no depth anchor (vs riverine's BLE), so pluvial depths are inherently softer/wider; the `r`/`f`
  ponding knobs are judgment, surfaced in M2 ([AFL-P2](../../../../docs/plans/flood/assumptions.md)).
- **Known-answer checks pass:** `Q` rises monotonically with return period; dry/uncovered sites read 0.

## Inputs → outputs
NOAA Atlas 14 (24-hr precip-frequency) → one shared **field** manifest
`data/flood/flood_pluvial_m1_catalog_manifest.json` (per-site runoff `Q` at each RP, rows tagged `asset`).
`event_family_id` is **reserved** (unused for pluvial). One method serves both assets; each asset's M2 filters to
its own sites and applies the terrain ponding.

## Decisions & assumptions
[JD-FL-9](../../../../docs/plans/flood/decisions.md) (Atlas 14 → SCS-CN pluvial) ·
[JD-FL-10](../../../../docs/plans/flood/decisions.md) (fork at M1) ·
[JD-FL-19](../../../../docs/plans/flood/decisions.md) (M1 = field, M2 = coupling). Assumptions **AFL-P1/P2** (pluvial
source + the `r`/`f` knobs, no depth anchor) · **AFL-W10/W11** (wind pad-gated ponding; PNW Atlas-2 gap). Register:
[`assumptions.md`](../../../../docs/plans/flood/assumptions.md).

**Next → M2 (coupling):** each asset pours `Q` over its terrain — solar = footprint ponding fraction × depth; wind =
per-node pad-gated ponding (raised pads shed the shallow sheet).

## Method In Plain English: Rainfall Becomes A Ponding Source Term

Pluvial flood is the hardest public-data branch because there is no national free depth raster equivalent to FEMA BLE.
So M1 does not pretend to know the final flood depth at the asset. It builds the rainfall-runoff source term that M2
can pour over local terrain.

```text
NOAA Atlas 14
  return period T -> 24-hour rainfall P(T)

SCS Curve Number
  rainfall P(T) -> runoff Q(T)

M2 terrain model
  runoff Q(T) + local depressions/pads -> ponded depth at the asset
```

The shape is:

```text
rainfall P
  |
  v
losses to infiltration / initial abstraction
  |
  v
runoff Q
  |
  v
local terrain storage
  |
  v
ponded inundation depth
```

Simple example:

```text
Return period: 100-year
Atlas 14 rainfall: P100
SCS-CN runoff:     Q100 = 0.284 m at Elizabeth

M1 stops here.
M2 decides how much of that runoff actually ponds on the solar footprint or reaches a wind pad.
```

Why M1 stops at runoff:

```text
Rainfall frequency is regional/public.
Ponding depth is local/topographic/asset-specific.

Flat solar field:
  shallow depressions can hold water across a share of the footprint

Raised wind turbine pad:
  the same shallow water may not reach equipment
```

That is why pluvial has lower confidence than riverine in this V1. The frequency source is real, but the depth bridge is
more modeled because no public pluvial depth grid anchors it.

## What Pluvial M1 Asks

```text
pluvial M1 asks, for each site:
  is the site inside Atlas 14 coverage?
  what is the 24-hour rainfall depth at each return period?
  using the chosen curve number, what runoff Q(T) does that create?
  is this runoff source strong enough to carry to M2?
```

It does not ask:

```text
  where exactly does water pond inside the solar footprint?
  does a raised turbine pad shed that water?
  what depth reaches equipment?
```

Those require asset terrain and pad/footprint geometry, so they belong in M2.
