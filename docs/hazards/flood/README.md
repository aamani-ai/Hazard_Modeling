# Flood — hazard anchor  ·  *preview from the `flood` branch*

> **Where this lives.** The flood pipeline is built on the **`flood` branch** (by another team, at
> `origin/flood` @ `88df3af`), **under cross-review** — the same status as every hazard on main (we
> cross-review each other's work). This page is a **high-level synthesis** of that branch so the whole picture
> is visible from main; the code, plans, and registers land on main when review completes. Numbers below are
> the branch's as-built results, quoted for orientation, not yet main-blessed.

**The shareable snapshot of how we model flood.** This page is *asset-free* — it covers the peril itself
(`M0/M1`): what flood is, its three sub-perils, how each becomes a credible depth, how they combine, and
what's solid vs. screening-grade. How flood *damages a specific asset* will live in per-asset pages (deferred
until the branch lands).

> **New to flood physics?** Start with the internal reader guide:
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md). It is not a methodology document; it is the
> prerequisite mental model for understanding why flood forks by sub-peril, why depth/elevation matter, and
> why M2 is site-conditioned rather than hit-or-miss.
> For the source decision preview, read [`source_selection.md`](source_selection.md): why riverine uses BLE
> where available, why pluvial is modeled from rainfall + terrain, and why coastal uses SLOSH envelopes.

> **One-line state:** flood is **one peril, three sub-perils** — *riverine*, *pluvial*, *coastal* — that share
> a single damage driver (**inundation depth**) but need three different data machineries. Riverine is
> **well-supported** (FEMA engineering-grade depth grids); pluvial is the **"blind spot"** (no depth product
> exists — depth is modeled, screening-grade); coastal is a **per-category worst-case envelope** cross-linked
> to the hurricane peril so a storm is counted once.

---

## 1. What flood is, and the magnitude we model

Flood is modeled as **one peril with three sub-perils**, which arrive by different physics but **all drown the
asset the same way — by depth**:

- **Riverine `[R]`** — river-network overflow / classic floodplain inundation.
- **Pluvial `[F]`** — intense-rainfall surface ponding, often *outside* the mapped floodplain (the blind spot).
- **Coastal `[C]`** — storm-surge inundation at the coast (event-based, tied to tropical cyclones).

```
   THREE sub-perils, ONE damage driver (inundation depth above ground)

   [R] riverine  ─ river overflow ───────┐
   [F] pluvial   ─ rainfall ponding ──────┼──►  inundation DEPTH (ft / m)  ──►  depth → damage
   [C] coastal   ─ storm surge ───────────┘         at the asset                 (shared M3 curve)
        │              │             │
     annual-max     annual-max    event-based (per storm,
     AEP curve      AEP curve     by hurricane category)
```

| | Riverine `[R]` | Pluvial `[F]` | Coastal `[C]` |
|---|---|---|---|
| **Source** | river network overflow | rainfall → surface ponding | storm surge |
| **Footprint** | mapped floodplain | anywhere (often off-floodplain) | coastal zone |
| **Frequency basis** | annual-max, RP-indexed (10–500 yr) | annual-max, RP-indexed (10–500 yr) | event-based, compound-Poisson (λ × category mix) |

Two thresholds drive the pipeline, as everywhere: the **event basis** (annual-max AEP for inland, hurricane
category for coastal) governs what the catalog counts; the **asset damage-onset depth** governs where the
damage curve leaves zero. The whole peril re-converges at M3, where every sub-peril is just *depth → damage*.

## 2. Data source & curation (per sub-peril)

Each sub-peril has its own evidence base and its own curation burden — this is what makes flood *three
problems wearing one coat*:

| Sub-peril | Primary source(s) | Curation | Grade |
|---|---|---|---|
| **Riverine** | **FEMA BLE** depth grids (100/500-yr, HEC-RAS quality) + SFHA "bathtub" (NFHL + 3DEP) where BLE is absent + USGS gauges | method-per-site dispatch; lower RPs (10/25/50-yr) **densified** from a regression/gauge rating, BLE-anchored | **best — engineering-grade** |
| **Pluvial** | **NOAA Atlas 14** rainfall-frequency → **SCS Curve-Number** runoff → **1 m lidar** terrain for ponding fraction & depth cap | one method everywhere; depth is **modeled**, not measured (no free pluvial depth grid exists) | **screening-grade (the blind spot)** |
| **Coastal** | **NOAA SLOSH MOM** surge-by-category + **RAFT** synthetic-TC catalog (close-passage screen) + **HURDAT2** observed frequency | per-storm catalog, `event_family_id`-stamped for the hurricane join; depth sampled per storm | **worst-case envelope (per-category, not per-event)** |

The honest hierarchy: **trust riverine, treat pluvial as a screen, read coastal as an envelope.** Notably,
once pluvial ponding is grounded in real lidar terrain (rather than a flat guess), the pluvial signal often
**collapses to near-zero** — raised pads and terrain shed shallow sheet-water — so riverine and coastal
dominate the loss. The source-selection preview is summarized in [`source_selection.md`](source_selection.md).

## 3. How we model it — the fork, then the combine

Flood is the clearest case of *standard interface, not standard physics*: the catalog **forks by sub-peril at
M1** (three different data machineries), then everything **re-converges on depth → damage at M3** and is
recombined at M4.

```
        [R] BLE / bathtub + gauges          [F] Atlas 14 → SCS-CN + lidar        [C] SLOSH × RAFT × HURDAT2
                 │                                       │                                  │
                 ▼  depth field, RP-indexed              ▼  modeled ponding, RP-indexed     ▼  per-storm surge catalog
        ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
        │  M1 CATALOG (per sub-peril)  →  M2 COUPLING (depth at the asset)  →  M3 depth→damage  →  M4    │
        └──────────────────────────────────────────────────────────────────────────────────────────────┘
              inland [R]+[F]  ── co-sampled (one shared annual draw), WORSE-SOURCE-WINS + envelope ──┐
              coastal [C]     ── compound-Poisson; joined to HURRICANE wind on event_family_id ──────┤
                                                                              total flood = inland + coastal ┘
```

- **Coupling is site-conditioned** — flood "reaches" an asset by *depth vs. equipment elevation*, not by a
  hit-or-miss footprint. (Per-asset specifics — areal exposure for a solar polygon vs. per-node depth at each
  turbine/substation — are deferred to per-asset pages.)
- **The combine is the subtle part** (the branch's two new learning logs):
  - **Inland (`R`+`F`):** co-sampled *comonotonic* (one shared annual severity draw — the same ground drowns
    once), reported **worse-source-wins** with an additive-capped envelope as the conservative bound.
  - **Coastal (`C`):** a compound-Poisson event stream, **cross-linked to the hurricane peril** — surge and
    hurricane wind from the *same storm* are joined on `event_family_id` and combined per subsystem
    (`max(wind, surge)`), so one storm is never double-counted across the two pipelines.
- **Deployment:** built as a **deep per-asset run** (proven across reference sites spanning dry / riverine /
  pluvial / coastal / all-three). A **CONUS screening grid** is the same program-level future as the other
  hazards (planned, not built).

## 4. Assumptions (load-bearing; registers on the branch)

- **Flood = riverine + pluvial + coastal** (one peril, three sub-perils); catalog **forks at M1**, re-converges at M3 (JD-FL-1, JD-FL-10).
- **Riverine** = FEMA-BLE-preferred depth grids; lower RPs **densified** from a BLE-anchored rating (JD-FL-6, JD-FL-8).
- **Pluvial** = Atlas 14 → SCS-CN runoff with lidar-grounded ponding; **no depth grid exists** (JD-FL-9, JD-FL-15).
- **Coastal** = SLOSH per-category envelope, compound-Poisson, `event_family_id`-joined to hurricane (JD-FL-12, JD-FL-14).
- **Inland combine** = co-sampled comonotonic, worse-source-wins (JD-FL-11).
- **Coupling** = site-conditioned (depth vs. micro-elevation); **M1 = asset-free field, M2 = coupling** (AFL-3/4, JD-FL-19).
- Registers (on the branch): decisions `JD-FL-*`, assumptions `AFL-*` — see [Go deeper](#7-go-deeper).

## 5. Challenges & limitations

**(a) Pluvial is the blind spot.** No free national pluvial depth product exists, so depth is *modeled*
(rainfall → runoff → terrain ponding), not measured. It's **screening-grade**, and once lidar-grounded the
signal usually collapses to near-zero — but it carries the widest confidence band.

**(b) Coastal is a per-category envelope.** SLOSH MOM is surge-by-category (worst-case), not per-event
hydrodynamics (ADCIRC). The footprint-mean depth is a deliberate simplification — screening-grade.

**(c) Lower-RP densification is softer than BLE.** The 10/25/50-yr depths are rated up from a regression/gauge
relationship anchored to the 100/500-yr BLE grids — robust in testing, but softer than the engineering grids.

**(d) The three-way compound isn't fully unified yet.** Inland-vs-coastal are summed as independent streams; a
single per-storm loop that stacks river + rain + surge + wind together (JD-FL-17) is deferred.

**(e) Curves are medium-confidence** (solar from the `infrasure-damage-curves` library; wind greenfield), and
**business interruption / duration are unmodeled** (physical loss only).

## 6. Maturity — what's built

| | Reportable / solid | Provisional / screening | Deferred |
|---|---|---|---|
| **Riverine** | depth + loss are **engineering-grade**; validated against USGS high-water marks (solar) and FEMA NRI rates (wind) | lower-RP densified tail | Fathom-US swap-in |
| **Pluvial** | direction (usually near-zero once terrain-grounded) | the magnitude (screening, no depth anchor) | Atlas 15, a national pluvial grid, level-pool routing |
| **Coastal** | direction + the wind↔surge cross-link | magnitude (per-category envelope) | per-event hydrodynamics |

All three sub-perils are **built end-to-end (M0→M4) for both solar and wind farms** on the branch — a real,
externally-cross-checked result. The guiding line holds: a V1 cell runs end-to-end and is honest about its
limits. Headline figures (and the site-by-site numbers) belong in per-asset pages, to be written when the
branch lands on main.

## 7. Go deeper

The work lives on the **`flood` branch** (`origin/flood` @ `88df3af`). On GitHub:

- **Code:** [`Notebooks/flood/`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood) (layer0 → M0 → M1 fork {riverine · pluvial · coastal} → solar / wind_farm cells).
- **Source selection:** [`source_selection.md`](source_selection.md).
- **Plan-of-record:** [`docs/plans/flood/`](https://github.com/aamani-ai/Hazard_Modeling/tree/flood/docs/plans/flood) — decisions `JD-FL-*`, assumptions `AFL-*`, per-layer plans.
- **Lessons:** the branch adds two learning logs — *densifying a sparse RP anchor* and *combining correlated sub-perils*.
- **Cross-peril:** the coastal surge ↔ wind join is the seam with the [hurricane anchor](../hurricane/README.md).
- **Index:** back to the [hazard matrix](../README.md).
