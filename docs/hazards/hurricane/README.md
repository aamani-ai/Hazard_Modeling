# Hurricane — hazard anchor  ·  *preview from the `hurricane` branch*

> **Where this lives.** The hurricane pipeline is built on the **`hurricane` branch** (by another team, at
> `origin/hurricane` @ `b7937e6`), **under cross-review** — the same status as every hazard on main (we
> cross-review each other's work). This page is a **high-level synthesis** of that branch so the whole picture
> is visible from main; the code, plans, and registers land on main when review completes. Numbers below are
> the branch's as-built results, quoted for orientation, not yet main-blessed.

**The shareable snapshot of how we model hurricane.** This page is *asset-free* — it covers the peril itself
(`M0/M1`): what a hurricane is in this model, how we turn synthetic storm tracks into a credible wind field,
how the two deployments differ, and what's reliable vs. not. How hurricane *damages a specific asset* will
live in per-asset pages (deferred until the branch lands).

> **New to hurricane physics/data?** Start with
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md): the prerequisite mental model for wind-only
> hurricane scope, RAFT-vs-HURDAT2 roles, Holland field synthesis, and the flood cross-link.

> **For the source decision preview, read [`source_selection.md`](source_selection.md):** why RAFT supplies
> severity/physics, HURDAT2 anchors frequency, ASCE validates the tail, and surge/rain are routed to flood.

> **One-line state:** hurricane is the **wind peril of tropical cyclones** — the intensity variable is the
> **3-s peak gust** (the *same observable* as convective wind, but a **separate peril**: a continuous,
> field-intensity wind, not a hit-or-miss footprint). The **hazard side is independently validated** (return-
> period gusts match ASCE 7-22 within ±5.5 %); the **loss side is provisional** (the damage curve is the
> dominant open uncertainty). **Surge and rain are not modeled here — they belong to flood**, joined back to
> the same storm so it's counted once.

---

## 1. What hurricane is, and the magnitude we model

We model the **wind** of a tropical cyclone. The intensity variable is the **3-second peak gust** (mph, at
33 ft, Exposure C) — the universal structural-wind metric, *shared with convective wind*. But hurricane is a
**distinct peril** with a distinct coupling: a TC is a large, coherent, moving **wind field**, so the question
is "what gust does the storm field deliver *at* the asset?" — **field-intensity**, the third coupling bucket
(vs. hail's areal hit-or-miss or wildfire's site-conditioning).

A hurricane brings three damage agents; this peril owns **only the wind**, and the other two are routed to the
flood peril so no storm is double-counted:

```
                          ┌─ WIND  (3-s gust field) ─────────►  HURRICANE peril  (this page)
   tropical cyclone ──────┼─ STORM SURGE ───────────────────►  FLOOD · coastal [C]  ┐ joined back to the
   (one RAFT storm)       └─ RAINFALL ──────────────────────►  FLOOD · pluvial [F]  ┘ same storm via
                                                                                       event_family_id
                                                              → one storm, owned once, no double-count
```

The storm taxonomy is the standard Saffir-Simpson reference (major = ≥ Cat 3, ≥ 111 mph sustained); the
loss-driving major-storm tail is well resolved in the catalog.

## 2. Data source & curation

Hurricane splits its evidence cleanly: **one source for the *physics/severity*, a different source for the
*frequency*** — because the synthetic catalog is rich on storm structure but cannot be trusted for rates.

| | |
|---|---|
| **Severity / physics** | **RAFT** synthetic TC catalog (North-Atlantic tracks: 40,000 storms over 40 environmental years) — gives storm structure (intensity, radius) to build the wind field. **Not used for frequency** (it over-samples genesis ~71×). |
| **Frequency** | **HURDAT2** observed record (1851–2023) — λ = distinct hurricanes (≥64 kt) passing within 100 km of the site ÷ 173 yr (a close-passage rule, not landfall-only). |
| **Geometry** | screened coastal sites (a high-exposure Gulf/Atlantic site + a zero-exposure baseline), capacity-circle + centroid (enough for a field-intensity read on solar). |
| **Validation** | HURDAT2 reproduces published landfall climatology (**1.69/yr vs ~1.7/yr**); modeled RP gusts match **ASCE 7-22 within ±5.5 %, no low bias**. |

The curation move that makes this work: **take severity from RAFT and frequency from HURDAT2**, so the
catalog's genesis over-sampling never leaks into the rate. The ASCE cross-check is the key reassurance — it
**resolves the "is the tail silently low?" worry** that haunts a synthetic catalog.

## 3. How we model it — one engine, two deployments

```
                    ONE engine    M0 ─► M1 ─► M2 ─► M3 ─► M4
                                   │
      ┌────────────────────────────┴────────────────────────────┐
      ▼                                                          ▼
  real asset, true location                         canonical asset, every cell
  Holland wind field along each track               exact 0.25° cell
  ▶ DEEP PER-ASSET RUN   (built ✅, on branch)        ▶ CONUS SCREENING GRID  (planned)
    (one trustworthy number)                          (a comparable map)

  └────────── M0 / M1 identical & asset-free ──────────┘   asset enters only at M2 ▶
```

- **M1 (catalog):** each RAFT track is turned into a **Holland (1980) parametric wind field** swept along its
  path → a peak 3-s gust per location. Frequency is the observed HURDAT2 close-passage rate; severity is the
  RAFT/Holland field. Validated by replaying the field on historical tracks and against ASCE RP gusts.
- **M2 (coupling) = field-intensity.** Sample the storm's wind field at the asset. This is *spatially
  degenerate on a solar polygon* — the gust varies < 2 % across a ~1.4 km site, so the whole farm sees one
  effective gust (`exposed_fraction = 1.0`). It is *non-degenerate on a wind farm* — across a ~18 km lease the
  gust spreads up to ~20 %, so each turbine is sampled individually (the genuine per-point field-intensity
  case).
- **M3 (damage):** 3-s gust → damage via a capex-weighted subsystem curve; the wind-farm cell reuses the
  **convective-wind turbine curve** (hurricane wind on a turbine ≈ straight-line wind — same fragility,
  different source).
- **M4 (loss):** a storm-resolved compound-Poisson Monte Carlo → EAL · VaR · PML · TVaR · OEP ($ and % of TIV).
- **Cross-peril:** surge (flood coastal) and rain (flood pluvial) for the *same* storm join back on
  `event_family_id`, combined per subsystem (`max(wind, surge)`), so the storm is counted once.

## 4. Assumptions (load-bearing; registers on the branch)

- **Magnitude = 3-s peak gust** at 33 ft, Exposure C (shared observable with convective wind) (ATC-4).
- **Severity from RAFT, frequency from HURDAT2** close-passage rate (≥64 kt within 100 km ÷ 173 yr) (ATC-9).
- **Wind field = Holland (1980)**, B = 1.3, sustained→gust factor 1.2; symmetric in V1 (ATC-6/7).
- **Coupling = field-intensity** — degenerate on solar (`exposed_fraction = 1.0`), per-node on wind (ATC-12/13).
- **Damage curve provisional** — `infrasure-damage-curves` HURRICANE × solar; wind-immune subsystems cap the asset DR (ATC-14).
- **`event_family_id`** is the cross-peril identity that keeps surge/rain from double-counting (ATC-11).
- Registers (on the branch): decisions `JD-TC-*`, assumptions `ATC-*` — see [Go deeper](#7-go-deeper).

## 5. Challenges & limitations

**(a) The damage curve is the dominant uncertainty.** Unlike the hazard side (independently ASCE-validated),
the **M3 HURRICANE × solar curve is provisional** and slated for replacement, and a loss-side benchmark
(Hazus/NRI) is not yet applied. The wind-farm turbine curve is reused from convective wind — greenfield on
hurricane, low confidence.

**(b) Catalog depth (~1,300 yr).** PML is trustworthy to roughly the 700–1,000-yr return period; deeper tails
need extrapolation or a larger storm subset.

**(c) Small per-site frequency samples.** Close-passage counts are small, so λ has a real uncertainty band
(±~17–28 %); a true-zero baseline site correctly returns EAL ≈ 0 (no regional floor).

**(d) Symmetric wind field in V1.** Forward-motion asymmetry (rare but real for direct hits) is deferred.

The honest split to carry around: **hazard side validated, loss side provisional.**

## 6. Maturity — what's built

| | Reportable / solid | Provisional | Deferred |
|---|---|---|---|
| **Hazard layer** | the wind field + frequency — **independently validated** (ASCE ±5.5 %, HURDAT2 climatology); RP gusts to ~700–1,000 yr | deeper tail (extrapolation) | a larger RAFT subset for deep return periods |
| **Loss layer** | direction + the field-intensity coupling (degenerate solar, per-node wind) | the **loss magnitude** (curve-limited M3) | curve replacement + Hazus/NRI benchmark, field asymmetry, pluvial-TC rain, CONUS grid |

Both **solar and wind farm are built end-to-end (M0→M4)** on the branch; the wind-farm cell is the genuine
per-point field-intensity proof and supplies the wind leg of flood's coastal compound. The guiding line holds:
a V1 cell runs end-to-end and is honest about its limits — here, the hazard is validated and the loss awaits a
calibrated curve. Headline figures and the per-site numbers belong in per-asset pages, to be written when the
branch lands on main.

## 7. Go deeper

The work lives on the **`hurricane` branch** (`origin/hurricane` @ `b7937e6`). On GitHub:

- **Code:** [`Notebooks/hurricane/`](https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/Notebooks/hurricane) (M0 {RAFT · HURDAT2 · geometry} → M1 catalog + tail validation → solar / wind_farm cells).
- **Plan-of-record:** [`docs/plans/hurricane/`](https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/docs/plans/hurricane) — decisions `JD-TC-*`, assumptions `ATC-*`, per-layer plans.
- **Cross-peril:** the surge/rain ↔ wind join is the seam with the [flood anchor](../flood/README.md) (flood owns surge `[C]` and rain `[F]`).
- **Sibling peril:** shares the 3-s-gust observable with [convective wind](../convective_wind/README.md) (separate peril — watch the TC↔tornado double-count flag).
- **Index:** back to the [hazard matrix](../README.md).
