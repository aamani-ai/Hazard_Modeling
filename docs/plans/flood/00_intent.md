# 00 — Intent

*The seed for the flood pipeline. Captured before M0 planning — to be refined as we research and plan.*

## The goal

Take a **new peril — flood — and build the whole end-to-end workflow in notebooks**, step by step, exactly as hail,
wildfire, and wind were built. **Both the solar AND the wind-farm cells are now built end-to-end** (flood × solar and
flood × wind, M0→M4), off the same shared flood M0/M1, and **all three sub-perils — riverine, pluvial, and coastal —
are built** (solar-first, then wind, mirroring how wildfire was built). Flood is the **first peril owned outside the
hail/wildfire/wind line**, so
it proves the M0→M4 interface generalizes to a peril nobody on the team has staked. Each step legible, every basic
verified, the **shared loss engine untouched**.

## Why flood (this pick)

Three reasons it earns the slot. (1) **Lowest redundancy.** Hail, wildfire, and wind (incl. hail × wind-farm) are all
built or planned by the repo owner; **flood is untouched**, so every cell here is genuinely new rather than a second
pass at owned territory. (2) **It extends the proven `× solar` path.** Flood × solar reuses the **site-conditioned**
coupling machinery from wildfire × solar and the shared loss engine — so the new work concentrates on the *flood
physics* (M0/M1 data + frequency, M3 depth-damage), not on re-deriving asset geometry. (3) **Data-rich, self-serve,
and already defined in the references.** FEMA NFHL, USGS gauges, return-period depth grids, and public DEMs make the
input data fetchable without a private feed — and the competitive-research **A-series** (A12/A20/A21/A22) already
pre-defines flood's taxonomy, catalog method, coupling, and damage form. So flood is an **inherited-definition**
peril (like wildfire from FSim), *not* an authored one (like wind): we adopt the A-series spine and concentrate the
build on plumbing it into our pipeline ([`01_references.md`](01_references.md)).

## What flood is — and is NOT (the honest label — settled in JD-FL-1)

> **Flood is a sub-peril family** (A12): **Riverine `[R]`** (river-network-anchored), **Pluvial `[F]`** (grid-anchored
> local rainfall), **Coastal `[C]`** (coastline surge). **Flood models *exogenous riverine + pluvial + coastal
> inundation* causing *physical equipment damage* to utility-scale solar and wind-farm assets** — the asset as a
> **receptor** of an inundation depth that reaches its equipment. **Coastal `[C]` is built** (× solar: Discovery Solar
> Center + LA3 West Baton Rouge; × wind: Amazon Wind Farm US East) as a compound-Poisson surge×wind model, **joined to
> the hurricane peril** via a shared `event_family_id` (A12 §3 / A20 §6.8, JD-FL-12) so one TC-driven event is counted
> once rather than separately in both pipelines. **Also out of scope:** foundation scour / erosion, long-term
> corrosion, water-quality effects, and **business-interruption loss** (the BI bucket — physical loss only, the A25
> acute × damage cell; matches the team's hazard-tier scope). **Flood does not claim to cover total flood risk.**

This honesty is *basics-spot-on* applied to scope: a correct tail on a mislabeled or over-claimed peril is still a
credibility failure — the exact thing the rebuild exists to escape. (Mirrors wildfire's DD-W1 and wind's DD-WN-1.)

## The asset (V1) — solar farm

A **solar farm** is a **dense areal polygon** → flood couples as **site-conditioned** (bucket 3, the wildfire row):
the flood-depth field is sampled over the asset footprint, **modulated by micro-elevation (DEM)**, and the asset's
equipment **height** is the susceptibility — base-level electrical (inverters, combiners, transformers) is destroyed
at shallow depth while elevated panels survive it. No hail-style Minkowski areal hit-or-miss; the coupling is the
depth field met against equipment height. Unlike wildfire, **micro-topography is load-bearing** — flood depth varies
sharply with a metre of elevation, so the asset's height relative to the flood surface *is* the coupling.

## The second asset (built) — wind farm

The **wind-farm** cell is built off the **same shared flood M0/M1** ([m_wind_farm.md](m_wind_farm.md)). A wind
farm is a **sparse turbine point-cloud**, so flood is still site-conditioned but sampled **per-turbine pad elevation
vs the flood surface** (only low-lying turbines flood; foundation / base-electrical exposure — plus the farm's own
in-hull collector substation, which carries most of the loss when it sits in the river valley). The turbine-exposure
approach reuses the convective-wind wind-farm asset template (USWTDB cloud + capex curve) rather than diverging from
it. Built end-to-end across riverine, pluvial, and coastal (Green River IL · Shepherds Flat OR · Amazon Wind Farm US
East NC).

## Domain principles for this pipeline

- **Standard interface, not standard physics** — flood gets site-conditioned coupling *behind the interface hail and
  wildfire already defined*; the loss engine never changes.
- **Basics spot-on** — tail metrics off the *sampled* loss distribution (never the expected-loss shortcut / Method 0);
  two thresholds kept distinct — the **flood event / return-period basis** (what the catalog counts) vs the **damage-
  onset depth** (where the depth-damage curve leaves zero — e.g. inverter-pad height); depth-frequency anchored in the
  standard flood-frequency literature, not assumed.
- **Modular from day one** — M0 / M1 are the shared peril catalog (M0 = solar + wind sites; M1 = one notebook per
  sub-peril over both assets, emitting the asset-independent field). M1 emits the field; **M2 does the coupling** (the
  field→asset reduction — areal mean for solar, per-node for wind, JD-FL-19); M3 / M4 reuse the shared machinery.

## What success looks like (V1)

A reviewable, step-by-step notebook series that takes raw public flood data to a coherent *sampled* annual loss
distribution for a **solar farm** (EAL / VaR / PML / TVaR, **% of TIV**), honestly labeled as inland-riverine-and-
pluvial-only, built on site-conditioned coupling the platform already owns, every step legible, every basic verified —
and a shared M0/M1 catalog that also feeds the built wind-farm cell.

## Open questions (now resolved — kept for the reasoning trail)

*The A-series pre-settled much of the spine; the seeds below are now **all logged decisions** in
[`decisions.md`](decisions.md) (JD-FL-1…19, JD-FL-W1…W7). The ★ event-model bridge — once the genuinely-open call —
is settled as JD-FL-7.*

- **★ Event-model bridge — RP grids → the shared MC (SETTLED, [JD-FL-7](decisions.md)).** The flood reference world
  (HAZUS / First Street) computes loss at each return period then integrates the **exceedance curve → AAL**; our shared
  M4 is a Monte-Carlo engine. **Settled as an annual-maximum MC** sampling the loss-exceedance curve (inland riverine +
  pluvial, worse-source-wins) plus a compound-Poisson surge×wind track for coastal — both reconciled into the shared
  metric frame. ([JD-FL-7](decisions.md))
- **M1 frequency path** — *settled, [JD-FL-6](decisions.md) (supersedes JD-FL-2):* the depth spine is **FEMA BLE
  riverine depth grids** + SFHA-bathtub for Zone-A wind sites + NLDI→NSS / gauge `Q(T)` for the lower RPs, validated
  against Log-Pearson III ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
  **Fathom-US 2.0 is only a future commercial swap-in — never the V1 spine.** ([JD-FL-6](decisions.md))
- **Flood-type scope** — *settled, [JD-FL-1](decisions.md):* riverine + pluvial + **coastal — all three built**;
  coastal joined to hurricane on `event_family_id` ([JD-FL-12](decisions.md)).
- **Depth-damage curve source** — *settled (AFL-8):* the **canonical `infrasure-damage-curves` RIVERINE_FLOOD × solar**
  curve exists and is used (source-agnostic over all sub-perils); the old "tabular USACE building-archetype / no solar
  flood curve / solar-specific deferred" plan (A22 Q7) is **superseded**.
- **Sites** — *settled.* Solar = **Hayhurst** (dry), **Elizabeth** (riverine), **Discovery** (coastal), **LA3**
  (all-three); wind = **Green River IL** (riverine), **Shepherds Flat OR** (dry), **Amazon Wind Farm US East NC**
  (all-three). ([AFL-*](assumptions.md))
- **TIV basis** — estimate solar TIV from $/kW (no registry TIV yet); report % of TIV alongside dollars.
