# Hurricane — hazard anchor

> **Current main state.** The hurricane notebooks now live locally under
> [`Notebooks/hurricane/`](../../../Notebooks/hurricane/README.md), imported for review from the branch snapshot
> carried by `origin/flood` @ `aff8649` after the hurricane/flood cross-link updates. The hurricane
> plan/register docs now live locally under [`docs/plans/hurricane/`](../../plans/hurricane/README.md). This
> page is the main-branch hazard anchor to read before notebook review; numbers below are notebook-backed
> orientation figures, not yet product-blessed.

**The shareable snapshot of how we model hurricane.** This page is *asset-free* — it covers the peril itself
(`M0/M1`): what a hurricane is in this model, how we turn synthetic storm tracks into a credible wind field,
how the two deployments differ, and what's reliable vs. not. Hurricane asset notebooks are local under
[`Notebooks/hurricane/solar/`](../../../Notebooks/hurricane/solar/README.md) and
[`Notebooks/hurricane/wind_farm/`](../../../Notebooks/hurricane/wind_farm/README.md); hazard-doc per-asset
pages are still deferred.

> **New to hurricane physics/data?** Start with
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md): the prerequisite mental model for wind-only
> hurricane scope, RAFT-vs-HURDAT2 roles, Holland field synthesis, and the flood cross-link.

> **For the source decision, read [`source_selection.md`](source_selection.md):** why RAFT supplies
> severity/physics, HURDAT2 anchors frequency, ASCE validates the tail, and surge/rain are routed to flood.
>
> **For the M0-M4 modeling choices, read [`modeling_choices.md`](modeling_choices.md):** how RAFT severity, HURDAT2 frequency,
> Holland wind fields, M2 field-intensity coupling, M3 damage curves, and M4 storm-resolved loss metrics fit
> together.

> **One-line state:** hurricane is the **wind peril of tropical cyclones** — the intensity variable is the
> **3-s peak gust** (the *same observable* as convective wind, but a **separate peril**: a continuous,
> field-intensity wind, not a hit-or-miss footprint). The **hazard side is independently validated** (return-
> period gusts match ASCE 7-22 within ±5.5 %); the **loss side is provisional** (the damage curve is the
> dominant open uncertainty). **Surge and rain are not modeled here — they belong to flood.** Surge joins
> back to the same storm (`event_family_id`) so it's counted once; the rainfall↔storm link is deferred.

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
   tropical cyclone ──────┼─ STORM SURGE ───────────────────►  FLOOD · coastal [C] ──┐ joined to the same
   (one RAFT storm)       │                                                           ┘ storm via event_family_id
                          └─ RAINFALL ──────────────────────►  FLOOD · pluvial [F]     (storm link deferred:
                                                                                        Atlas-14 frequency, no event id)
                                       → surge is counted once with wind; rain is not yet storm-linked
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
  ▶ DEEP PER-ASSET RUN   (built ✅, imported notebooks) ▶ CONUS SCREENING GRID  (planned)
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
- **Cross-peril:** surge (flood coastal) joins back to the *same* storm on `event_family_id`, combined per
  subsystem (`max(wind, surge)`), so the storm is counted once. Rain (flood pluvial) is **not** storm-linked
  yet — it's a storm-agnostic Atlas-14 frequency curve (`event_family_id` null); the rain↔storm join is
  deferred (JD-FL-17 / JD-TC-6).

### M0-M4 modeling flow

| Layer | Hurricane modeling object | Choice summary |
|---|---|---|
| **Layer 0** | Wind-only tropical-cyclone scope. | Hurricane owns wind; surge/rain route to flood. |
| **M0** | RAFT synthetic tracks and HURDAT2 observed record. | RAFT supplies severity/physics; HURDAT2 supplies observed frequency. Site geometry is asset input for M2, not hazard M0. |
| **M1** | Storm event field model. | Holland wind fields from RAFT tracks; close-passage lambda from HURDAT2; ASCE validates the tail. |
| **M2** | Field-intensity coupling. | Solar samples one effective gust; wind farms sample per turbine/node across the field. |
| **M3** | 3-s gust -> asset damage ratio. | Loss-side curves are provisional and dominate uncertainty. |
| **M4** | Storm-resolved annual loss distribution. | Draw storms, sample fields, apply M3, preserve `event_family_id` for flood surge joins. |

The detailed choice ledger is [`modeling_choices.md`](modeling_choices.md): RAFT-vs-HURDAT2 split, Holland field
choices, field-intensity coupling, M3 caveats, M4 storm sampling, and cross-peril event identity.

## 4. Assumptions (load-bearing; registers now local)

- **Magnitude = 3-s peak gust** at 33 ft, Exposure C (shared observable with convective wind) (ATC-4).
- **Severity from RAFT, frequency from HURDAT2** close-passage rate (≥64 kt within 100 km ÷ 173 yr) (ATC-9).
- **Wind field = Holland (1980)**, B = 1.3, sustained→gust factor 1.2; symmetric in V1 (ATC-6/7).
- **Coupling = field-intensity** — degenerate on solar (`exposed_fraction = 1.0`), per-node on wind (ATC-12/13).
- **Damage curve provisional** — `infrasure-damage-curves` HURRICANE × solar; wind-immune subsystems cap the asset DR (ATC-14).
- **`event_family_id`** is the cross-peril identity that keeps surge/rain from double-counting (ATC-11).
- Registers: [`decisions.md`](../../plans/hurricane/decisions.md) (`JD-TC-*`) and
  [`assumptions.md`](../../plans/hurricane/assumptions.md) (`ATC-*`) — see [Go deeper](#7-go-deeper).

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

Both **solar and wind farm are built end-to-end (M0→M4)** in the imported notebooks; the wind-farm cell is the
genuine per-point field-intensity proof and supplies the wind leg of flood's coastal compound. The guiding line
holds: a V1 cell runs end-to-end and is honest about its limits — here, the hazard is validated and the loss
awaits a calibrated curve. Headline figures are carried here and in [`modeling_choices.md`](modeling_choices.md);
hazard-doc per-asset pages can be written after notebook review.

## 7. Go deeper

Notebook work now lives locally on main for review:

- **Code:** [`Notebooks/hurricane/`](../../../Notebooks/hurricane/README.md) (M0 {RAFT · HURDAT2 · geometry} → M1 catalog + tail validation → solar / wind_farm cells).
- **Modeling choices:** [`modeling_choices.md`](modeling_choices.md).
- **Plan-of-record:** [`docs/plans/hurricane/`](../../plans/hurricane/README.md) — decisions `JD-TC-*`, assumptions `ATC-*`, per-layer plans.
- **Cross-peril:** the surge ↔ wind join is the seam with the [flood anchor](../flood/README.md) (flood owns surge `[C]` and rain `[F]`; only surge is storm-joined today — the rain link is deferred).
- **Sibling peril:** shares the 3-s-gust observable with [convective wind](../convective_wind/README.md) (separate peril — watch the TC↔tornado double-count flag).
- **Index:** back to the [hazard matrix](../README.md).

## Quick Layer Questions

```text
M0 asks:
  what RAFT tracks, HURDAT2 rate anchors, and site geometry exist?

M1 asks:
  what storm-resolved 3-second gust does the Holland field produce, and what event_family_id identifies it?

M2 asks:
  is field-intensity degenerate on the asset or does it need per-node sampling?

M3 asks:
  what solar or turbine wind damage curve maps gust to conditional loss?

M4 asks:
  in simulated years, what storm wind losses produce AEP/OEP metrics?
```

Keep the key split in mind: hurricane owns wind; flood owns surge/rain, joined later by `event_family_id`.
