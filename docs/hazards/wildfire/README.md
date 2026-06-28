# Wildfire — hazard anchor

**The shareable snapshot of how we model wildfire.** This page is *asset-free* — it covers the peril itself
(the hazard layer, `M0/M1`): what wildfire hazard is, how we turn a published fire-simulation product into a
credible per-site frequency + severity, how the two deployments differ, and what's reliable vs. not. How
fire *damages a specific asset* lives in the per-asset pages ([wildfire × solar](solar.md)).

> **New to wildfire physics/data?** Start with
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md): the prerequisite mental model for FSim BP/FLP,
> conditional severity, site-conditioned coupling, and the oozing issue.
> For the source decision itself, read [`source_selection.md`](source_selection.md): why native FSim is the V1
> spine, why WRC is a cross-check, and which sources are deferred.

> **One-line state:** wildfire is the **"ingest a finished hazard product"** peril — we read frequency and
> severity straight off the USFS **FSim** simulation rather than building them from a raw record. The catalog
> and per-site frequency are trustworthy; the numbers are **real but approximate** — the severity *damage
> curve* (M3) and the on-site *oozing* handling (M2) are the open items, not the hazard field itself.

---

## 1. What wildfire is, and the magnitude we model

We model **exogenous wildfire reaching the asset** — a fire ignites and spreads across the landscape until
it arrives (or doesn't) at the plant. Wildfire has **no single intensity variable**; it is modeled as a
**frequency × severity pair**:

- **Frequency — Burn Probability (BP):** the annual probability a location burns (a pure number, 0–1/yr).
- **Severity — fire-line intensity (kW/m):** how hot the fire is *if* it burns, carried as the **flame-length
  histogram** (six **FIL** classes, conditional on a fire) and converted to kW/m via **Byram**
  (`FL_m = 0.0775·I^0.46`). There is no "severe threshold" like hail's 25.4 mm; instead the severity *is* the
  distribution, with the standard control breaks **FLEP4** (>4 ft, hand-crew limit) and **FLEP8** (>8 ft,
  equipment ceiling).

```
  FSim per-pixel product — a PRE-INTEGRATED field, not a raw record
  ┌─────────────────────────────────┐
  │  Burn Probability (BP)           │   annual P(burn)        ──►  FREQUENCY
  │     ~0.04 %/yr … ~4.7 %/yr       │   λ = −ln(1−BP)
  ├─────────────────────────────────┤
  │  Flame-length histogram          │   FIL1 ▏  <2 ft                 SEVERITY
  │  (conditional on a fire)         │   FIL2 ▇▇ 2–4 ft   →  kW/m      (conditional
  │   Σ FIL1..FIL6 = 100 %          │   FIL3 ▇  4–6 ft     (Byram)     flame-length
  │                                  │   FIL4 ▏  6–8 ft                distribution,
  │                                  │   FIL5 ▏  8–12 ft               not one number)
  │                                  │   FIL6 ▏  12+ ft
  └─────────────────────────────────┘
   ≥20,000 simulated fire seasons, already integrated  →  we INGEST a product, not build one
```

Two facts about this product drive everything downstream:

- **It is *pre-integrated*, not a raw record.** FSim has already simulated tens of thousands of fire seasons
  and shipped the answer as BP + a conditional flame-length histogram. So — unlike hail, where we must build
  frequency and severity out of raw radar — wildfire **inverts the hard problem**: curation burden is *low*,
  but we **inherit FSim's assumptions, fuel model, and vintage** ([§5](#5-challenges--limitations)). This is
  the cleanest example of *standard interface, not standard physics* — a totally different hazard machine
  behind the same `M0→M4` contract ([LL09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
- **It is gridded and split into frequency × severity.** BP is annual; the FIL histogram is *conditional on a
  fire*. We keep those two axes separate the whole way down — collapsing them is the classic error
  ([LL09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).

## 2. Data source & curation

| | |
|---|---|
| **Primary source** | USFS **FSim** native (`RDS-2016-0034-3`, 3rd ed., LANDFIRE 2020) — **270 m**, the **full FIL1–6 histogram** + BP. The **severity spine** ([DD-W4](../../plans/wildfire/decisions.md)). |
| **Cross-check** | **WRC 2.0** (`RDS-2020-0016-2`, geoplatform ImageServers) — **30 m**, but intensity *collapsed* (CFL, FLEP4, FLEP8). Fine-grain texture / independent vintage only. |
| **What they are** | **Two published product views of the *same* FSim run** — they differ in grain, vintage, and aggregation, *not* in the hazard they describe ([LL07](../../learning_logs/07_one_simulation_two_products.md)). |
| **Access** | Direct public USFS rasters, no auth, CC BY 4.0 ([DD-W3](../../plans/wildfire/decisions.md)). |
| **Curation burden** | **low** — the inverse of hail. The hazard is a finished product; the work is *ingest + reconcile + assemble onto the asset*, not *build*. |

This is the mirror image of hail. Hail must be **self-built and anchored** from raw MESH (no ready-made
product gives both frequency and a size distribution); wildfire gets a **pre-integrated field** it can largely
ingest, so the modeling effort moves *downstream* — to coupling the field onto a site (M2) and to the damage
curve (M3). Source-selection rationale: [`source_selection.md`](source_selection.md). Deeper reasoning:
[`discussion/wildfire/`](../../extra/discussion/wildfire/README.md) (`01` scope → `02` data dictionary → `03`
coupling).

## 3. How we model it — two deployments of one engine

Wildfire feeds **two products off the same `M0→M4` engine** — a *deep per-asset run* (a real asset at its
true footprint) and a *CONUS screening grid* (a canonical asset at every 0.25° cell). They share the spine,
and **the asset never enters until coupling (M2)** — so everything on this page (the BP, the frequency, the
severity histogram) is identical regardless of what sits there.

```
                    ONE engine    M0 ─► M1 ─► M2 ─► M3 ─► M4
                                   │
      ┌────────────────────────────┴────────────────────────────┐
      ▼                                                          ▼
  real asset, true footprint                        canonical asset, every cell
  boundary-zonal over the plant polygon             exact 0.25° cell
  ▶ DEEP PER-ASSET RUN   (built ✅)                  ▶ CONUS SCREENING GRID  (planned)
    (one trustworthy number)                          (a comparable map)

  └────────── M0 / M1 identical & asset-free ──────────┘   asset enters only at M2 ▶
```

Where the two **hazard layers** differ (asset-free), and why — note how *little* differs, because the hazard
is pre-integrated (the source of so much hail-grid tension simply isn't here):

| Hazard-layer choice | Deep per-asset run | CONUS grid (planned) | Why they differ |
|---|---|---|---|
| **Spatial unit** | boundary-zonal mean over the real plant polygon (or a capacity-radius circle if no boundary) | the one 0.25° cell | The deep run reads the field exactly under the asset; the grid reads one canonical cell so cells stay comparable. |
| **Frequency model** | **Poisson**, `λ = −ln(1−BP)` per asset | **Poisson**, same `λ = −ln(1−BP)` per cell | **Same both ways** — FSim already integrated the season-to-season dispersion into BP, so there's no per-cell over-dispersion to fit (`fano = 1` structurally). Contrast hail, where NegBin-vs-Poisson is a live deployment choice. |
| **Severity** | the FIL1–6 histogram at the footprint | the FIL1–6 histogram in the cell | Identical machinery; the grid just reads a coarser, canonical unit. |

Because the hazard is a finished field, the two deployments are **far closer** than hail's — the engine is
literally the same Poisson-on-FSim read at a different spatial unit. The CONUS grid for wildfire is **planned,
not yet built** (the grid driver is finishing hail × solar first), but the methodology is the one above.

The coupling (`M2`) and damage (`M3`) — the *asset* side — are on the per-asset pages, e.g.
[wildfire × solar](solar.md).

## 4. Assumptions (load-bearing; full registers linked)

- **FSim FLP1–6 is the severity spine**, WRC is the 30 m cross-check ([DD-W4](../../plans/wildfire/decisions.md)).
- **Frequency** `λ = −ln(1−BP)`, **`fano = 1` structural** (FSim pre-integrates dispersion; AW-22/23, [DD-W7](../../plans/wildfire/decisions.md)).
- **Boundary-zonal** extraction over the real plant footprint, all-touched mean ([DD-W5](../../plans/wildfire/decisions.md); AW-11/21).
- **BP ÷ 10000** to reach an annual probability (lab convention, **to-verify**; AW-5); severity = **6 discrete FIL classes**, FIL6 "12+ ft" open-ended (AW-24).
- Register: [`docs/plans/wildfire/assumptions.md`](../../plans/wildfire/assumptions.md) (AW-3…AW-29).

## 5. Challenges & limitations

**(a) The damage curve is the dominant uncertainty — *not* the hazard field.** Because FSim hands us a credible
frequency + severity, the weakest link moves downstream: the **M3 fire→damage curve is Low/Low-Medium
confidence** (a capex-weighted BoS logistic with a fixed standoff `d = 10 m` carrying ±40%, and no empirical
solar-claim calibration). This is the headline open item — see [wildfire × solar](solar.md).

**(b) "Oozing" of developed pixels — the M2-critical data subtlety (AW-15).** The 30 m WRC product *oozes*
burn probability onto developed/asset pixels while *suppressing* their intensity — so a naive read at the
plant pixel can show "it burns, but gently," which is an artifact of the land-cover mask, not the fire. The
on-site hazard must come from the **surrounding fuel ring**, and whether a pixel is oozed is **asset-specific**
(it happens at some sites, not others). Handled per-asset in M2 ([LL08](../../learning_logs/08_oozing_developed_pixels.md)).

**(c) Vintage staleness — the hazard "ages fast" (AW-25/26).** FSim BP ≈ end-2020 and intensity ≈ end-2022;
fuels change quickly (burn scars, treatment, regrowth), so a stale vintage can misstate today's hazard. A
currency adjustment is **deferred**.

**(d) Coarse severity tail (AW-24).** Severity is six discrete FIL classes with an open-ended "12+ ft" top —
fine for the body, coarse for deep return periods. A continuous / EVT severity tail is **deferred**.

**(e) ~30 % of TIV is unmodeled (AW-19).** The BoS subsystem weights sum to ≈0.70, so ~30 % of asset value is
treated as non-damageable in V1 (and the asset damage ratio caps at ~0.57). A curve revamp would classify the
remainder.

## 6. Maturity — V1 vs. deferred

| | Reportable now | Provisional / screening | Deferred (V1.5 / V2) |
|---|---|---|---|
| **Deep per-asset** | **direction + contrast** (EAL, the body) and the **frequency** — these are *real, not record-limited*, because FSim pre-integrates the climatology | the **magnitude** of loss (curve-limited, Low-confidence M3; coarse tail) | damage-curve calibration to PV claims, fire-front sweep (partial burn / real PML tail), continuous severity tail, currency adjustment, financial terms |
| **CONUS grid** | — | — (**not built yet**) | the full grid build + scaleout (after the hail-grid driver) |

The guiding line: **a V1 cell is a vertical slice that runs end-to-end and is honest about its limits — not a
calibrated product.** Wildfire's honest state: the *direction* is trustworthy (the pipeline reads near-zero
where fire is genuinely absent and material where it's real — the proof-of-flow contrast in
[wildfire × solar](solar.md)); the *exact loss* awaits a calibrated curve.

## 7. Go deeper

- **Reasoning:** [`discussion/wildfire/`](../../extra/discussion/wildfire/README.md) (`01` scope · `02` data dictionary · `03` coupling).
- **Source selection:** [`source_selection.md`](source_selection.md).
- **Decisions / plan-of-record:** [`plans/wildfire/`](../../plans/wildfire/README.md) (DD-W3…DD-W8 + per-layer plans).
- **Code:** [`Notebooks/wildfire/`](../../../Notebooks/wildfire/m0_input_data/README.md) (M0 → M1 → the solar cell).
- **Lessons:** [LL07 one simulation, two products](../../learning_logs/07_one_simulation_two_products.md) · [LL08 oozing](../../learning_logs/08_oozing_developed_pixels.md) · [LL09 pre-integrated vs. extracted](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md).
- **Per-asset:** [wildfire × solar](solar.md).
