# 00 — Intent

*The seed for the hurricane / tropical-cyclone pipeline. Captured after the scope discussion, before the
detailed M0→M4 planning. Mirrors [convective_wind/00_intent](../convective_wind/00_intent.md) and
[flood/00_intent](../flood/00_intent.md).*

## The goal

Take the **fourth peril — tropical cyclone / hurricane — and build it end-to-end in notebooks**, M0→M4, exactly
as hail, wildfire, convective wind, and flood were built. Hurricane is the peril that finally builds the **third
coupling type — field-intensity** (a continuous hazard field sampled at the asset), which the repo has *defined*
but never built as a primary (hail = areal hit-or-miss; wildfire/flood = site-conditioned; convective wind toured
those two). Proving field-intensity is the **first architectural prize**. The **second** is that hurricane is the
**prerequisite for coastal flood**: its storm catalog is what flood's coastal `[C]` sub-peril (and the
compound TC-rain slice of pluvial `[F]`) plug into via the now-active `event_family_id` — flood coastal is built and consumes it.

## Why hurricane (fourth)

Three reasons it earns the slot. (1) **It builds the last unbuilt coupling type** — field-intensity. If the
M0→M4 contract holds for a continuous wind field sampled at the asset, the interface is *complete* across all
three coupling buckets. (2) **It is the keystone for compound flooding.** Surge and TC rainfall are the *same
physics* as flood's coastal `[C]` and pluvial `[F]` — they are flood's sub-perils, not hurricane's. The one thing
that lets a single storm's wind + surge + rain be combined without double-counting is a **shared, storm-resolved
TC catalog** plus the `event_family_id` cross-link. Hurricane owns that catalog. (3) **It replaces the old model's
single worst hurricane bug** — separate `Hurricane` and `Coastal Flood` peril rows, summed independently (see the
counter-example below).

## What V1 is — and is NOT (the honest label, settled)

> **Hurricane V1 models *tropical-cyclone WIND* causing *structural physical damage* to a *utility-scale solar PV*
> asset, producing an asset-level annual loss distribution (EAL/VaR/PML/TVaR, % of TIV + $) on the shared MC
> engine — wind only, solar first.** Storm **surge** and **TC rainfall** are **flood's** sub-perils (`[C]`/`[F]`),
> **not** hurricane's; V1 does not catalog or model them — it only **reserves the `event_family_id` hook** so they
> attach later without a refactor. The **wind-farm** asset is the **V2** cell (now **built** — where field-intensity is fully exercised, at Amazon Wind Farm US East);
> the **wind *resource*** (generation/revenue) is the Performance tier (`model-gpr`), out of scope here — V1 is
> *extreme wind that breaks equipment*, not *everyday wind that spins turbines* (the boundary
> [DD-WN-2](../convective_wind/decisions.md) already drew). **V1 does not claim to have *proven* field-intensity**:
> on a ~1 km solar polygon the storm-scale field is ~uniform, so the coupling is **spatially degenerate**
> (≈ a centroid sample) — the full per-point field-intensity proof is the wind-farm cell, **now built**. ([JD-TC-1/2](decisions.md))

This honesty is *basics-spot-on* applied to scope: V1's real deliverable is **a built-and-validated, storm-resolved
RAFT TC catalog** (the reusable foundation), proven end-to-end on the *simplest* asset. The spatial coupling and the
turbine reuse are built in the wind-farm cell; the surge/rain cross-link is built (flood coastal).

## The two dividends (why this peril is worth more than its own loss number)

1. **Completes the coupling taxonomy** — field-intensity is the third and last bucket. Built here (degenerate on
   solar V1, full at wind-farm — **built**), the M0→M4 interface is general across *all* coupling types.
2. **Unlocks coastal flood (and compound flooding)** — the shared, storm-resolved **RAFT** catalog + the
   `event_family_id` cross-link are exactly what flood's coastal `[C]` (**built**) and the TC slice of pluvial `[F]`
   need to recognize one storm's wind + surge + rain as **one event** (no double-count) — the link is now active. See
   [flood JD-FL-1/4/11](../flood/decisions.md).

## The asset (solar first; wind farm — both built) — and why order, not exclusion

Both solar and wind farm are eventual cells (peril × asset matrix). The choice is **order**. **M0 + M1 (the
catalog) are the peril — asset-independent and shared across both cells**, so building solar first does *not* waste
the field machinery (that lives in M1). Only the **M2 coupling** is spatially degenerate on solar; the wind-farm
cell (**now built**) exercises it fully, reusing the same M1 field **plus** convective wind's **3-s-gust turbine fragility
curve** ([DD-WN-16](../convective_wind/decisions.md)) and **turbine geometry** (Amazon Wind Farm US East). This
mirrors flood's own order (solar V1 → wind farm V2) and keeps the build coherent across perils. ([JD-TC-1](decisions.md))

## The sites (low-vs-high contrast, mirroring every other cell)

- **HIGH / proving — Everglades Solar Energy Center (FL)** (screened in M0, highest US landfall density). The coastal
  high site is the natural proving ground for field-intensity *and* the surge cross-link (surge only reaches the coast).
- **LOW / baseline — reuse the solar baseline (Hayhurst, TX)** — near-zero TC exposure (λ=0, true-zero), the
  cross-peril-coherent control (the same asset hail/wildfire/flood used). ([JD-TC-5](decisions.md))
- **CROSS-LINK riders — Discovery Solar Center (FL) + LA3 West Baton Rouge (LA)** — added so flood coastal's
  wind+surge compound combine (built) has its hurricane-wind leg. (Four solar sites total.)

## The catalog — a shared, storm-resolved RAFT TC catalog (the load-bearing choice)

The frequency basis could be **pre-integrated** (STORM 10 km wind-RP GeoTIFFs — a wind *surface*, fast) or
**storm-resolved** (RAFT tracks → Holland wind field — storm *objects*, heavier). The pre-integrated grid is faster
to a V1 wind number, **but it has no storm objects** — it cannot feed coastal flood's `event_family_id` link or a
landfall-by-intensity frequency. Since the *whole reason* hurricane comes before coastal flood is to lay that
foundation, the catalog must be **storm-resolved**, and specifically **RAFT** (North Atlantic; tracks + along-track
intensity + **rainfall** in one product) — so a single RAFT catalog serves **hurricane wind, coastal surge, and the
pluvial TC-rain slice** with shared storm identity. STORM RP grids + IBTrACS/HURDAT2 become the **validation
cross-checks**. ([JD-TC-3](decisions.md))

**Cross-peril consequence (recorded, not built in V1):** flood's pluvial becomes a **hybrid** — Atlas 14 (all-cause
baseline) **+** RAFT (the storm-resolved TC slice), reconciled so TC rain isn't double-counted. RAFT enters the
system **once**, owned by this TC catalog layer. ([JD-TC-6](decisions.md))

## The old model — the counter-example (what *not* asking the coupling question looks like)

The `old-hazard-model/` is the cautionary anchor here, as it was for hail/wildfire/flood:

- **No coupling at all.** [`config/hazard_spatial_sizes.csv`](../../../old-hazard-model/config/hazard_spatial_sizes.csv)
  lists only Hail/Strong Wind/Tornado — **hurricane has no footprint, no wind field, no spatial sampling.** It is a
  non-spatial dollar-loss draw. The "how does the hazard reach the asset" question is never asked.
- **Loss-first, back-solved.** [`config/lognormal_global_fit.csv`](../../../old-hazard-model/config/lognormal_global_fit.csv)
  pins `Hurricane` to `EAL 21.4 / VaR99 268` with `mu/sigma` reverse-engineered to reproduce that headline
  (benchmark "Katrina/Ian"). The hazard severity isn't physical — exactly the back-solve-from-EAL habit
  convective_wind's layer-0 bans.
- **The surge double-count, live.** The same file has **separate** `Hurricane` *and* `Coastal Flood`
  (benchmark "Sandy (2012) Surge") rows, **summed independently** — one storm counted twice, no event identity.
  This is the precise error the `event_family_id` cross-link exists to fix.

V1 is the opposite of all three: a physical, storm-resolved, field-coupled catalog with one storm identity shared
across perils.

## Domain principles for this pipeline

- **Standard interface, not standard physics** — hurricane introduces genuinely new physics (a continuous wind
  field) behind the *same* M0→M4 interface; the loss engine never changes.
- **Basics spot-on** — frequency/severity fit to the physical catalog (RAFT + Holland, validated vs
  IBTrACS/HURDAT2), **never** back-solved from a target loss; tail metrics off the *sampled* distribution; the
  spatially-degenerate solar coupling **labeled as such**, not papered over.
- **Modular from day one** — M0/M1 (the RAFT catalog) is the shared, asset-independent peril; solar is one cell,
  wind farm another; surge/rain are *flood's* sub-perils reached by cross-link, not re-cataloged here.

## What success looks like

A reviewable M0→M4 notebook series that takes the RAFT TC track catalog → Holland wind field → a coherent *sampled*
annual wind-loss distribution for a coastal solar farm (EAL/VaR/PML/TVaR, % of TIV), honestly labeled wind-only /
spatially-degenerate-coupling, **validated against IBTrACS/HURDAT2 landfall winds and the STORM RP grid** — with the
storm-resolved catalog and the `event_family_id` hook **now consumed by the built wind-farm cell and the built coastal-flood cell**.

## Open questions (to resolve as we plan / in layer-0 & M0)

- **High site** — confirm the Gulf/Atlantic-coast solar farm by an M0 screen (TC exposure + real footprint +
  reachable geometry). Baseline = Hayhurst reused.
- **RAFT reachability & version** — confirm the current RAFT NetCDF DOI is fetchable at build time (the reference
  warns to re-confirm repository DOIs; the 4TU STORM-tracks DOI was already 404 at probe). STORM RP GeoTIFFs
  (Zenodo 10931452) + IBTrACS (NCEI) + HURDAT2 (NHC) + SLOSH (NOAA) probed **live**.
- **Holland parameterization** — central pressure / RMW / Holland B / asymmetry / gust-factor choices for the
  track→field step (the heavier part RAFT's storm-resolution buys us). Decide the V1 form in M1.
- **STORM empirical-Weibull RP convention** — document where the RP cross-check runs low past ~100-yr vs EVD.
- **Unit discipline** — STORM/RAFT wind in m/s; damage curve in mph (×2.237) — guard on ingest.
- **TIV basis** *(resolved)* — solar $/MW (Hayhurst hail basis); high site = Everglades Solar Energy Center (~74.5 MW)
  by capacity; % of TIV alongside $.
