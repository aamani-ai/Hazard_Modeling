# layer-0 — Hazard Definition (the **orientation** layer, above M0)

*The layer flood needed for the **opposite** reason wind did. Wind had **no product** to define its event, so it had
to be **authored**. Flood's events **are** inherited — but "flood" is **three sub-perils at once** (riverine `[R]` ·
pluvial `[F]` · coastal `[C]`), each with a **different magnitude basis** from a **different data source**, sharing
only **one damage driver: inundation depth (ft above ground)**. The flood notebooks build that family end-to-end; what
they need up-front is a single statement of **(a) the magnitude observable per sub-peril** and **(b) the exact data
source per sub-peril**. This layer is that statement — it **orients** the family; it does **not** author or re-model.*

**Where this sits:** **layer-0 (definition)** → [M0 (evidence)](../m0_input_data/README.md) → M1 → M2 → M3 → M4.
Plan-of-record: [`docs/plans/flood/00_hazard_definition.md`](../../../docs/plans/flood/00_hazard_definition.md).

| Notebook | What it orients | Status |
|---|---|---|
| [`01_hazard_definition`](01_hazard_definition.ipynb) | the flood hazard family, defined quantitatively + the concepts it rests on | ✅ **built** |

## What `01_hazard_definition` fixes (the spec the pipeline consumes)

- **Magnitude observable + exact source, PER sub-peril** (stated up-front, prominently). All three share the damage
  driver **inundation depth (ft above ground)**; they differ in magnitude basis and source:
  - **[R] Riverine** = flood **depth** at return period — **FEMA BLE** depth grids (100/500-yr) where studies exist,
    else NFHL 1% flood-area + **3DEP** boundary WSE bathtub; **USGS NLDI→NSS** regression or **NWIS** gauge
    flow-frequency for lower RPs (JD-FL-8/W5); **FEMA NFHL** + **EIA-860** / **USWTDB** for screening.
  - **[F] Pluvial** = 24-hr **rainfall depth** at return period → modeled ponding — **NOAA Atlas 14** → **SCS Curve
    Number** → DEM / 1 m lidar; **no free pluvial depth grid exists** (the blind spot — flagged).
  - **[C] Coastal** = surge **depth** per storm, by hurricane category — **NOAA SLOSH MOM** + **RAFT** close-passage
    tracks + **HURDAT2** observed frequency, shared from hurricane via `event_family_id`.
- **Event basis** — **annual-maximum**, AEP-indexed (riverine + pluvial; JD-FL-7); **coastal is event-based**
  (compound-Poisson, λ × category mix), the deliberate exception, since it combines with hurricane wind on the same
  storm rather than the flood annual-max.
- **Practical bound** = the sourced RP tail (500-yr BLE) + the **equipment-submersion damage cap** (~28% wind / low
  solar) — flood has no single physical `L`.
- **The two thresholds, kept distinct** (on the depth axis) — flood-event basis (counts the flood) vs **damage-onset
  depth** (pad / `x0` height; where `DR ≈ 0`). Far apart → the curve is **anchored**.
- **Severity / event model** — annual-max MC on the loss-exceedance curve inland (PML anchored to BLE; EAL softer);
  inland sub-peril **combine = co-sample comonotonic + worse-source-wins** (JD-FL-11); coastal **surge + wind combine
  per subsystem** (`max(wind_DR, surge_DR)`) joined by `event_family_id` (JD-FL-12); **total flood = inland + coastal**.
- **Pre-integrated RP-depth surface** — riverine **reads** the BLE grid (profile-assembly, learning-09); pluvial has
  **none** and must **model** depth — the sharpest statement of the sub-peril asymmetry.
- **Coupling-taxonomy** — **site-conditioned (bucket 3) for every sub-peril** (depth × elevation, DEM-modulated;
  reuse wildfire's M2); the asset difference (areal solar vs per-node wind) is *within* the bucket.

> **This is a *definition / orientation* notebook, not an exploratory-*data* one** (M0 profiles the real grids). Its
> discipline is [*basics-spot-on*](../../../docs/principles/basics_spot_on.md) applied to the definition: every number
> is provenance-tagged (`[REF]` Flood Hazard-Data-Reference · `[STD]` named standard · `[A]` A-series · `[JD]`/`[AFL]`
> our logged decision/assumption), and the one piece of real math (the annual-max log-AEP interpolation) passes its
> known-answer checks (reproduces the BLE anchors; monotone in depth).

## Decisions & assumptions

Decisions [JD-FL-1](../../../docs/plans/flood/decisions.md) (family/scope), JD-FL-6/8/9 (sources), JD-FL-7
(event model), JD-FL-10/11 (catalog fork + combine), JD-FL-12/14/15/16 (coastal + `event_family_id` cross-link),
JD-FL-4 (`event_family_id`). Assumptions **AFL-6/12/13** (riverine source), **AFL-P1/P2/P3** (pluvial source + combine),
**AFL-3/4/7** (site-conditioned coupling), **AFL-8/W8** (anchored curve), **AFL-17** (annual-max). Registers:
[`decisions.md`](../../../docs/plans/flood/decisions.md) · [`assumptions.md`](../../../docs/plans/flood/assumptions.md).

**Next → [M0](../m0_input_data/README.md):** the real evidence met against this definition (FEMA NFHL + BLE + 3DEP +
NOAA CFEM/SLOSH ✅).

## Plain-English Mental Model

Layer-0 is the vocabulary layer. It does not calculate loss. It makes sure every later notebook means the same thing by
"flood event", "depth", and "frequency".

```text
Three ways water reaches the asset:

  [R] river leaves channel       [F] rain ponds on site       [C] ocean/surge moves inland
          |                              |                              |
          v                              v                              v
  riverine depth field          runoff -> ponding model       surge depth by storm/category
          |                              |                              |
          +-------------- common damage driver ---------------+
                                     |
                                     v
                         inundation depth above ground
```

Two thresholds must stay separate:

```text
Flood-event basis
  "Does this return period or storm create water at the site?"

Damage-onset basis
  "Is the water high enough to reach the equipment?"

depth axis:

0 ft ground
|-------------------|---------------------|-------------------->
                    equipment starts loss  deeper damage/cap
                    e.g. inverter pad
```

This distinction matters because a site can be "flooded" in the hydraulic sense but still have low damage if the water
does not reach vulnerable equipment. M2 measures the water at the asset; M3 decides what that water does to components.

## What This Layer Asks

```text
layer-0 asks:
  what do we mean by flood?
  what sub-perils are inside the flood family?
  what magnitude variable does each sub-peril use?
  what source will provide that variable?
  what is common across all sub-perils?
  what stays different until M4?
```

For flood, the short answer is:

```text
common:
  damage driver = inundation depth above ground

different:
  riverine = return-period depth field
  pluvial  = return-period rainfall/runoff, then modeled ponding
  coastal  = storm event surge field, joined to hurricane wind
```
