# 00 — Hazard Definition (layer-0, the active plan) · *the field-intensity peril, and the cross-link spine*

*Hurricane needs a layer-0 — but for a **different reason** than convective wind did. Wind had **no product** that
defined the event, so we authored the definition from standards. Hurricane **has** products (RAFT/STORM catalogs,
the Holland method), so the event is not the hard part. What we must author here is (1) the **footprint-synthesis
method** — how a track becomes a continuous wind field sampled at the asset (the **field-intensity coupling**, the
third and last bucket) — and (2) the **primary→secondary cross-link discipline** that keeps surge/rain as *flood's*
sub-perils, owned once, never double-counted. That authoring earns its own layer, above M0.*

**Where this sits:** **layer-0 (hazard definition)** → [M0 (input data)](m0_input_data.md) →
[M1 (catalog)](m1_catalog.md) → [M2 (coupling)](m2_coupling.md) → [M3 (damage)](m3_damage.md) →
[M4 (loss & metrics)](m4_loss_metrics.md). Built for **four solar sites** (Everglades Solar Energy Center FL, high/proving
+ Hayhurst TX, baseline + Discovery Solar Center FL & LA3 West Baton Rouge LA, flood-coastal cross-link riders).
Written for a reader new to the domain — terms defined on first use.

---

## Why this layer exists (read this first)

| Peril | The data product | What layer-0 had to author |
|---|---|---|
| Hail | MRMS / MESH | nothing — the product *was* the event (≥ 1-inch footprint) |
| Wildfire | FSim (BP + FLP) | nothing — the product pre-integrated event + severity |
| **Convective wind** | — none — | **the whole event definition** (threshold, magnitude scale, bound) |
| **Hurricane** | **RAFT / STORM** (catalogs exist) | **the footprint-synthesis method** (track → wind field → asset sample) **+ the cross-link taxonomy** (wind primary; surge/rain = flood's, by reference) |

So hurricane sits between the two extremes: the *event* (a storm) and its *frequency* arrive in a product (RAFT
tracks), but **the field that reaches the asset is something we build** (Holland), and **the relationship to surge
and rain is a discipline we must state** (or repeat the old model's double-count). Both are authored here.

> **The honest framing.** What we author must be **defensible**: the field method traces to the published Holland
> (1980) model and is **validated against observed landfall winds** (IBTrACS/HURDAT2); the cross-link taxonomy
> traces to the Hazard Data Reference §1/§8. Where a value is to-be-confirmed-at-build, we say so. *basics-spot-on*
> applied to the hazard's own definition. (Decisions → [JD-TC-1..](decisions.md); assumptions → [ATC-1..](assumptions.md).)

---

## The hazard, defined quantitatively

### 1. The magnitude observable — the 3-second peak gust (shared with convective wind)

Hurricane's damage observable is the **3-second peak gust wind speed**, the *same* universal metric convective
wind committed to. `[REF]` Hazard Data Reference: *"3-second gust speed is the universal metric — map it to a
wind-load / fragility curve per asset."* This is why hurricane **shares the 3-s-gust wind-damage curve** with
convective wind ([DD-WN-9](../convective_wind/decisions.md)) — the *only* thing the two perils share. The structural
load scales with gust², not with a daily mean.

- **Reference basis:** 3-s gust at 33 ft (10 m), Exposure C — same convention as the convective-wind layer-0.
  Hub-height / terrain corrections are M2 adjustments, flagged as assumptions.
- **Unit discipline `[REF]`:** RAFT/STORM report wind in **m/s**; the damage curve uses **mph** → convert
  **×2.237 on ingest** (the single most common error — Hazard Data Reference §7).
- **Gust vs sustained / vs resource:** synthetic catalogs carry **maximum sustained wind** (1-min, the
  Saffir-Simpson basis); the damage observable is the **3-s gust**, obtained via a **gust factor** (≈1.1–1.3,
  to fix in M1). And neither is the *resource* wind that drives generation — that is the Performance tier
  ([DD-WN-2](../convective_wind/decisions.md)). One observable, one curve.

### 2. The event — a storm (a track object), not a return-period draw

Unlike the RP-grid alternative, the event here is a **physical storm**: a RAFT synthetic track with position,
along-track intensity (central pressure / max wind), and radius parameters over its life. This **storm-resolution
is load-bearing** — it is what gives every event an **identity** (the `event_family_id`), so the *same* storm's
wind, surge, and rain are recognizable as one event downstream. An RP grid has no events to identify; that is why
it cannot found coastal flood. ([JD-TC-3](decisions.md))

- **Frequency basis:** the RAFT catalog's storm set over its synthetic years → landfalling-storm rate near the
  site (decomposable by intensity — what category-SLOSH surge will later need). Validated vs the observed
  IBTrACS/HURDAT2 landfall record.

### 3. The footprint — a continuous wind field (Holland), the thing we author

A track is not yet a hazard at the asset. We turn each track into a **continuous wind field** with the **Holland
(1980) parametric radial wind profile** `[STD]` — central pressure deficit + radius-of-maximum-wind → a radial gust
profile, swept along the track → peak gust per location. `[REF]` Hazard Data Reference §5: *"take a track → apply
a Holland parametric wind field → rasterize peak wind per cell. Validate the field against observed landfall winds."*

- **This field is the field-intensity hazard.** It varies continuously in space (steep radial gradient, peaking at
  the radius-of-max-wind). Sampling it *at the asset* is the M2 coupling.
- **What we author / parameterize (M1):** central pressure & RMW (from RAFT), the **Holland B** shape parameter,
  storm **asymmetry** (forward-motion + inflow), and the **gust factor** (sustained → 3-s). V1 forms recorded as
  assumptions ([ATC-*](assumptions.md)); this is the heavier work RAFT's storm-resolution buys us over the RP grid.
- **Validation `[REF]`:** the Holland field at historical landfalls (replayed from IBTrACS/HURDAT2 best tracks)
  must reproduce observed landfall gusts; the catalog's RP winds cross-checked vs the STORM 10 km RP grid (noting
  STORM's empirical-Weibull RP runs low past ~100-yr vs EVD — Hazard Data Reference §7).

### 4. The coupling taxonomy — field-intensity (the third bucket), and where solar sits

`[FRAME]` The repo's three coupling types ([Notebooks/README](../../../Notebooks/README.md)):
**areal hit-or-miss** (a finite footprint covers/misses the asset) · **field-intensity** (a continuous field
sampled at the asset) · **site-conditioned** (a field × per-asset susceptibility). **Hurricane wind is
field-intensity** — and the *first primary build* of it.

- **On a wind farm (built):** turbines are scattered over tens of km; the radial field varies turbine-to-turbine
  within one storm → field-intensity in full (sample the field at *each* point). This is where the prize is proven —
  built at Amazon Wind Farm US East.
- **On solar V1 (degenerate, stated):** a ~1 km polygon is small vs the storm scale → the field is ~uniform across
  it → the coupling collapses to ≈ a **single centroid sample**, operationally like the site-conditioned perils
  already built. **V1 therefore does not *claim* to prove field-intensity** — it builds the field (M1) and applies
  it at a point (M2); the per-point proof is the wind-farm cell, **now built**. ([JD-TC-2](decisions.md))

### 5. The primary→secondary cross-link — wind is ours; surge & rain are flood's

`[REF]` This is the taxonomy ruling that keeps hurricane honest (Hazard Data Reference §1, §8):

> *"hurricane drives 3 distinct systems (wind / surge / rainfall)… but it is deliberately **NOT sub-peril-tagged**.
> Surge and rainfall are **secondary perils that are the same physics as flood's coastal `[C]` and flash `[F]`** —
> handled as a **primary→secondary cross-link** to the Flood doc… **Wind is the primary peril owned by this doc.**"*

So the definition is explicit about ownership:

| System | Owner | Status in hurricane V1 |
|---|---|---|
| **Wind** | **hurricane** (primary) | **modeled** (this pipeline, M0→M4) |
| Storm **surge** | **flood** — coastal `[C]` (SLOSH/ADCIRC) | **not modeled here**; `event_family_id` **active** (flood coastal built, consumes it) |
| TC **rainfall** | **flood** — pluvial `[F]` (Atlas 14 + future RAFT slice) | **not modeled here**; `event_family_id` active |

- **`event_family_id` (stamped in M1, now active):** the field that lets a flood coastal/pluvial event (coastal built)
  point back to its
  parent storm, so Total Loss treats one storm's wind+surge+rain as **one event** — the structural fix to the old
  model's separate-and-summed `Hurricane` + `Coastal Flood` double-count.
- **Why not tag surge/rain as hurricane sub-perils:** they are the *same physics* as an existing peril (flood) →
  tagging them here means two surge models that duplicate, drift, and double-count. One owner (flood), one model,
  one storm identity shared by reference. (Contrast convective wind, which *does* own its two sub-perils because
  tornado/strong-wind are not another peril's physics.)

---

## What layer-0 fixes (the spec the pipeline consumes)

- **Magnitude observable** = the **3-second peak gust** (shared 3-s-gust curve with convective wind).
- **Event** = a **storm (RAFT track object)** with identity (`event_family_id`) — storm-resolved, not an RP draw.
- **Footprint** = the **Holland (1980) continuous wind field**, swept along the track, **validated vs
  IBTrACS/HURDAT2 landfall winds** (STORM RP grid cross-check).
- **Coupling** = **field-intensity** (third bucket); **spatially degenerate on solar V1** (centroid sample),
  fully exercised at the **wind-farm** cell (**built**, Amazon Wind Farm US East).
- **Catalog** = the shared, storm-resolved **RAFT** TC catalog (North Atlantic; tracks + intensity + rainfall) —
  the reusable foundation for hurricane wind, coastal surge, and the pluvial TC slice.
- **Ownership** = **wind is hurricane's**; **surge = flood `[C]`, rain = flood `[F]`** — cross-linked via the
  now-active `event_family_id` (flood coastal built), not re-catalogued.
- **Units** = m/s → mph (**×2.237**) on ingest; sustained → 3-s gust via a gust factor.

## Decisions & assumptions

Decisions [JD-TC-1/2/3/4/6](decisions.md) (asset/order; degenerate-coupling honesty; RAFT storm-resolved catalog;
the cross-link + `event_family_id`; the pluvial hybrid consequence). Assumptions **ATC-*** (3-s gust observable;
Holland parameterization; gust factor; unit conversion; field-intensity-degenerate-on-solar; storm-resolved catalog;
cross-link hook). Register: [`assumptions.md`](assumptions.md).

**Next → [M0](m0_input_data.md):** meet the real evidence against this definition — RAFT tracks, the
IBTrACS/HURDAT2 landfall record, the STORM RP grid cross-check, and the four solar sites' geometry.
