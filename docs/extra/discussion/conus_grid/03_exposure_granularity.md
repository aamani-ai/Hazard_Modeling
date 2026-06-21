# 03 — Exposure Granularity (how granular we define the canonical asset)

*A discussion doc. The "first step" the owner called out: **decide how granular the canonical asset's exposure
is** — and recognise that "screening" carries a deliberate, well-defined assumption (a fixed generic plant),
not a vague approximation. The key move: granularity is **append-per-(hazard × asset)**, driven by the
coupling. Settles into `G*` rows in [`assumptions.md`](assumptions.md).*

---

## TL;DR

1. **"Screening" is still an approximate value — *on purpose*, and the assumption is precise.** The grid holds
   a **fixed generic plant** at each cell; it does **not** model the real turbine spacing, turbine model,
   panel type, or site layout that a deal-level run would use. That's not sloppiness — it's the deliberate
   choice that makes the map *comparable* (location varies, asset doesn't). The job here is to **state that
   assumption crisply** so it's defensible, because it drives a lot of downstream questions.
2. **We define exposure at the *coarsest* level the coupling needs — nothing finer.** Three tiers:
   **area** (a polygon/box) · **fractional point-cloud / density** (sparse turbines as expected affected
   capacity, not fake exact coordinates) · *(never)* component geometry. The grid asset uses the minimal tier
   that the coupling doesn't wash out.
3. **The deciding test is per-(hazard × asset): does the next granularity tier change the loss, or wash out?**
   Where it washes out (hail × solar — the area cancels), the generic is *plenty*. Where it's load-bearing
   (hail × wind — *which* turbines a swath hits), you **append** the next tier for that pair only.
4. **So granularity is an append register, not a global setting.** Each pair starts at the minimal tier; its
   coupling tells us "enough or not"; we append where needed. This is the **exposure-side analogue of the A21
   coupling dispatch** — "standard interface, not standard physics."

---

## 1. The principle — minimal generic exposure, stated precisely

The canonical asset is a **generic plant**, defined only as deeply as the coupling requires:

| Tier | What it is | Do we model it? |
|---|---|---|
| **Area** | a single footprint/polygon (or a bounding box) + total capacity → TIV | ✅ default for area-coupled perils |
| **Fractional point-cloud / density** | sparse damageable units represented by a count + density + expected affected fraction, not exact synthetic coordinates | ✅ **only where a swath hits a *subset*** of the asset |
| **Sub-asset config** | real turbine model, panel type, array layout, exact spacing, cable routing, owner-specific BoS layout | ❌ **never** (for the grid) — false precision at 0.25° |

**What we explicitly do NOT do:** define a real turbine model, a panel technology, an inverter layout, or true
spacing. None of that is knowable for a *generic* plant, and none of it survives at a 0.25° (~600 km²) cell —
so encoding it would be false precision dressed as detail. We use **fixed canonical defaults** only where the
loss model needs them (capacity, TIV, wind turbine count/density, hub height, IEC class, terrain exposure),
and keep those defaults constant across cells so the map remains a location comparison.

> **This is the assumption to write down (and it's a strength, not a hedge):** the per-cell number is *"loss
> to a **standard** plant of fixed configuration placed here."* Holding the asset constant is what makes the
> map a clean read on **location/hazard**, not asset idiosyncrasy.

## 2. The reusable asset-exposure guide

Use this guide for **every new asset type**, not only solar and wind:

1. **Fix capacity and value first.** The canonical grid asset is a fixed capacity/value object. This keeps the
   grid comparable and makes `% of TIV` the primary display.
2. **Choose the exposure tier from the coupling.** Dense assets start as area. Sparse assets start as
   capacity/value, then append a density / fractional point-cloud only if a hazard can hit a subset.
3. **Do not invent real layouts.** If exact coordinates, component types, or owner-specific site features are
   unavailable, do not synthesize them as if they were known. Use the coarsest expected-fraction logic that
   preserves the coupling math.
4. **Keep v1 defaults fixed across cells.** Terrain, turbine class, hub height, susceptibility, and similar
   inputs are fixed canonical assumptions in the grid product. If we later need more accuracy, add named
   scenarios or adjustments; do not silently vary the baseline asset by cell.
5. **Reserve high-detail geometry for real-asset runs.** Use case 1 can use actual turbine points, actual
   hub height, actual topography, actual turbine model, and actual site layout. The CONUS grid should not
   pretend to know those.

This makes "screening" precise: it is **not** "rough because we skipped the model"; it is "the full model
applied to a fixed, deliberately generic exposure."

## 3. The append rule — coupling decides what's "enough"

Whether the minimal tier suffices is **not** a global call — it's set by each pair's **coupling**, via one test:

```
   For a given (hazard × asset):
   ─────────────────────────────────────────────────────────────
   Does moving from the current granularity tier to the NEXT tier
   change the modelled loss?
        │
        ├── NO  → it WASHES OUT → the current (coarser) tier is enough.   ✓ stop
        │
        └── YES → it's LOAD-BEARING → APPEND the next tier for THIS pair.  ⤴ refine
   ─────────────────────────────────────────────────────────────
```

Worked across the pairs we care about:

| Hazard × asset | Coupling | Minimal tier | Does the next tier matter? | Granularity verdict |
|---|---|---|---|---|
| **Hail × solar** | areal hit-or-miss | **area** | **No — washes out.** `s ≪ F`, and the region `A` cancels (`λ_asset = ρ·E[(√F+√s)²]`) — the array geometry barely moves the rate. | **area is enough** `[OURS]` (learning-log 06) |
| **Hail × wind** | areal, but **sparse targets** | area/box | **Yes — load-bearing.** A swath clipping the 30 km² envelope hits *some* turbines, not all 100 MW. The box overstates the hit. | **append → fractional turbine-density exposure** (this is [assumptions G3-note](assumptions.md) generalised) |
| **Wildfire × solar** | site-conditioned (field × susceptibility) | area | Geometry: no. **Susceptibility: yes** — but susceptibility is held *canonical* (a separate, named assumption, not a geometry tier). | **area enough for hazard sampling**; susceptibility-held-fixed is the documented limit |
| **Wildfire × wind** | site-conditioned + **hub-height attenuation** | area/box | **No** — turbines near-immune (surface fire vs nacelle @ 80–130 m); the answer is ~0 regardless of geometry. | **box is enough** (loss ~floor) |

The pattern: **area-coupled + asset small relative to footprint → area suffices; sparse-target coupling →
fractional turbine-density needed; height-dominated coupling → geometry barely matters.** Granularity tracks
the *physics of the hit*, which is exactly the A21 coupling-type axis — so this register sits beside it.

## 4. The fixed v1 solar canonical asset

Solar is the simpler case because it is **dense, near-ground, and contiguous**. V1 fixes one canonical solar
asset:

| Field | V1 canonical value | Why |
|---|---:|---|
| Capacity | **100 MW** | Same canonical capacity as wind; supports direct comparison |
| Footprint | **1.5 km²** | Measured USPVDB median density, scaled to 100 MW |
| Capacity density | **66.7 MW/km²** | `100 / 1.5` |
| Geometry tier | **area / dense polygon** | A solar farm is treated as a compact damageable area |
| Sub-layout | **not modeled** | Panel row spacing, inverter layout, tracker details are real-asset inputs, not grid inputs |

For hail and similar areal-hit perils, area is enough because `s_solar` is tiny relative to typical event
footprints and the collection-region area cancels in the hit-rate math. For site-conditioned perils such as
wildfire, the same area footprint is used to sample / aggregate the local hazard, while susceptibility remains
a fixed canonical assumption.

## 5. The fixed v1 wind canonical asset

Wind needs special care because the physical asset is **sparse, tall, and point-like**, but the grid product
cannot know the real layout in each cell. V1 therefore fixes one canonical wind asset:

| Field | V1 canonical value | Why |
|---|---:|---|
| Capacity | **100 MW** | Same canonical capacity as solar; supports direct comparison |
| Turbine rating | **5 MW** | Fixed generic utility-scale turbine, not a real model |
| Turbine count | **20 turbines** | `100 MW / 5 MW` |
| Spacing envelope | **30 km²** | Planning-grade fixed project envelope |
| Turbine density | **0.667 turbines/km²** | `20 / 30` |
| Capacity density | **3.33 MW/km²** | `100 / 30` |
| Hub height | **100 m** | Fixed generic utility-scale hub height for grid v1 |
| IEC class | **Class II** | Fixed generic turbine-class assumption; not varied by cell |
| Terrain / exposure | **ASCE Exposure C / open terrain** | Standardized baseline; no topographic speed-up in v1 |

Those are not meant to describe the real turbine model or real site layout in a cell. They are the **fixed
standard plant** whose loss we compare across locations.

**Why 30 km² makes sense on a 0.25° grid.** The serving cell is roughly **25 km × 25 km**, not 25 km²; in area
terms it is ~500–700 km² depending on latitude. It also corresponds to about **25 × 25 native 0.01° MRMS
pixels**. A 30 km² wind envelope is therefore only ~4–6% of a serving cell (roughly a 5.5 km × 5.5 km square,
or a circle with ~3.1 km radius). So the canonical wind farm remains a **sub-cell exposure**, just larger and
sparser than solar. That is exactly why we keep the 30 km² envelope as project context but use
fractional-density exposure for narrow swaths.

The wind exposure then changes by coupling type:

| Hazard family | How canonical wind is exposed in v1 |
|---|---|
| **Broad field / site-conditioned wind** (strong wind, hurricane wind when built) | Treat the 100 MW asset as reading the local wind intensity under the fixed hub-height / exposure / IEC assumptions. Exact turbine coordinates are not needed. |
| **Narrow path / swath hazards** (hail, tornado) | Do **not** treat the 30 km² envelope as fully damageable. Use fractional turbine-density exposure: affected capacity fraction = expected overlap of the path/swath with the envelope, capped at 100%. |
| **Surface site-conditioned hazards** (wildfire flame, shallow flood) | Use the envelope only as project context; tall-turbine exposure and hub-height attenuation dominate, so loss may sit near a floor unless a separate substation/BoS exposure is added. |

Future improvements can add named scenarios — topographic speed-up, IEC class I/III, different hub height,
or a measured wind-boundary source — but these are **scenario layers**, not silent changes to the baseline.
For the comparative grid, the fixed canonical baseline is the product.

## 6. Why this answers other questions + strengthens assumptions.md

- It **defines what "an asset" *is*** for the grid before we argue about data — so the canonical-asset rows
  (G1–G3) gain a *granularity* dimension, and the wind point-cloud caveat (G3-note) stops being a one-off and
  becomes an instance of a rule.
- It **bounds the work**: we never chase real turbine/panel specs for the grid; the ceiling is area / fractional
  point-cloud / density.
- It makes **"screening" defensible**: not "a rough number," but "the loss to a precisely-specified standard
  asset, refined per pair exactly where the physics demands."
- It graduates to a new **assumptions.md** section: *Exposure granularity (append per hazard × asset)* — the
  framework + a per-pair sufficiency row, appended as each pair is built.

---

## Cross-references

- The canonical asset + area numbers this refines: [`assumptions.md`](assumptions.md) (G1–G4) + the new
  granularity section.
- Why area washes out for hail: [learning-log 06](../../../learning_logs/06_collection_region_size_cancels.md).
- Coupling types (the physics axis this mirrors): [`../gpt/03_coupling_types_…`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md).
- The output that consumes the exposure geometry: [`02_per_cell_output_schema.md`](02_per_cell_output_schema.md).
