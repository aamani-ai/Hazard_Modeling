# Hail — hazard anchor

**The shareable snapshot of how we model hail.** This page is *asset-free* — it covers the peril itself
(the hazard layer, `M0/M1`): what hail is, how we turn raw radar into a credible magnitude, how the two
deployments differ, and what's reliable vs. not. How hail *damages a specific asset* lives in the per-asset
pages ([hail × solar](solar.md)).

> **New to hail physics/data?** Start with
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md): the prerequisite mental model for MESH,
> hail-day footprints, MRMS-vs-NOAA roles, and areal hit-or-miss coupling.
> For the source decision itself, read [`source_selection.md`](source_selection.md): why MRMS is the V1
> spine, why NOAA reports are validation/calibration only, and why MYRORSS is deferred.

> **One-line state:** the hail catalog and frequency are built both ways (a deep per-asset run and a
> full-CONUS grid). Frequency is trustworthy; **raw radar severity has known outliers that are not yet
> resolved** — that's the open V1 quality-assessment item.

---

## 1. What hail is, and the magnitude we model

We model **severe hail** — convective storms dropping hailstones large enough to damage equipment. The
intensity variable is **hailstone size**, taken from radar as **MESH** (Maximum Estimated Size of Hail), in
**mm**. An event is *severe* at **MESH ≥ 25.4 mm (1 inch)** — the NWS severe-hail threshold.

Two facts about MESH drive everything downstream:

- **It is a radar *estimate*, not a measurement.** MESH is inferred from reflectivity; it over-forecasts
  (≈75% of real hail falls below the MESH value) and, at the extreme, produces **physically impossible
  values** (our CONUS scan tops out at **1,437 mm** — there is no 1.4-metre hailstone). Curating a credible
  magnitude out of this is the central hail problem (§5).
- **It is gridded, not a list of events.** Hail doesn't arrive as a table of "events"; it arrives as a daily
  field of estimated sizes over space. We construct events by thresholding and aggregating (§3).

```
  MESH daily field — a PICTURE, not a list      keep ≥ 25.4 mm          one hail-day EVENT
  ┌──────────────────────────┐                  ┌────────────┐          ┌──────────────────┐
  │  12  18  31  45   9   3   │                  │  ·   · ███  │          │ severe footprint │
  │  22  41  68  52  14   5   │  ─────────────►  │  ·  ██████  │  ─────►  │  + peak size     │
  │  17  29  55  38  11   2   │   threshold (mm) │  ·  █████   │ aggregate│  → frequency &   │
  │   8  13  24  19   6   1   │                  │  ·   ███    │          │     severity     │
  └──────────────────────────┘                  └────────────┘          └──────────────────┘
        raw radar estimate                        severe cells only         the M0 → M1 event
```

## 2. Data source & curation

| | |
|---|---|
| **Primary source** | NOAA **MRMS MESH** (`CONUS/MESH_Max_1440min_00.50`), public on AWS (`noaa-mrms-pds`) |
| **Record** | ~5.65 yr continuous (**2020-10-14 → 2026-06-15**) — the operational MRMS era |
| **Cross-check** | NOAA Storm Events / SPC point reports (long record, population-biased; validation only) |
| **Curation burden** | **high** — no ready-made product gives both per-cell frequency *and* a size distribution |

This is what makes hail the *hard* hazard, and the reference for the others. Wildfire gets a pre-integrated
field (FSim) it can largely ingest; hail must be **self-built and anchored** — build frequency + severity
from raw MESH, then validate against reports and (future) the published hail-climate literature. The
sourcing decision is summarized in [`source_selection.md`](source_selection.md), with deeper research in
[`discussion/conus_grid/hail/`](../../extra/discussion/conus_grid/hail/README.md) (`00` research → `01`
triage).

## 3. How we model it — two deployments of one engine

Hail feeds **two products off the same `M0→M4` engine** — a *deep per-asset run* (a real asset at its true
location) and a *CONUS screening grid* (a canonical asset at every 0.25° cell). They share the spine and
**the asset never enters until coupling (M2)** — so everything on this page (the catalog, the count, the
frequency, the severity) is identical regardless of what asset sits there.

```
                    ONE engine    M0 ─► M1 ─► M2 ─► M3 ─► M4
                                   │
      ┌────────────────────────────┴────────────────────────────┐
      ▼                                                          ▼
  real asset, true location                         canonical asset, every cell
  50-mi window · Negative Binomial                  exact 0.25° cell · Poisson
  ▶ DEEP PER-ASSET RUN                              ▶ CONUS SCREENING GRID
    (one trustworthy number)                          (a comparable map)

  └────────── M0 / M1 identical & asset-free ──────────┘   asset enters only at M2 ▶
```

Where the two **hazard layers** differ (asset-free), and why:

| Hazard-layer choice | Deep per-asset run | CONUS grid | Why they differ |
|---|---|---|---|
| **Collection window** | 50-mile circle around the asset (~20,342 km²) | the one 0.25° cell (~600 km²) | The deep run borrows a big neighborhood for sample support; the grid must stay exact-cell or it blurs neighbors and destroys the meaning of `cell_id`. Window *size* cancels in the hit-rate math ([LL06](../../learning_logs/06_collection_region_size_cancels.md)); what changes is *localization vs. sample size*. |
| **Frequency model** | Negative Binomial (over-dispersion φ≈3.37 detected) | Poisson (V1 default) | The 50-mi region has enough annual counts to *detect* clustering → NegBin. A single cell over ~5.65 yr can't support per-cell dispersion without fitting noise → Poisson is the stable screening default; dispersion is kept as a diagnostic. Future grid upgrade = *pooled/regional* dispersion, not naive per-cell NegBin. |
| **Footprint** | reconstructed footprint polygon per event | severe-pixel area within the cell (proxy) | The grid trades polygon fidelity for scale; labeled as a cell-clipped proxy. |

The coupling (`M2`) and damage (`M3`) — the *asset* side — are on the per-asset pages, e.g. [hail × solar](solar.md).

## 4. Assumptions (load-bearing; full registers linked)

- **Severe threshold = 25.4 mm**, **event = one hail-day** (24-h max product; >95% of a day's reports fall
  in one window), **MESH is an estimate** (data caveat, not corrected in V1).
- Deep-run register: [`docs/plans/hail/assumptions.md`](../../plans/hail/assumptions.md) (A1–A24).
- Grid register: [`docs/plans/hazard_conus_grid/assumptions.md`](../../plans/hazard_conus_grid/assumptions.md) (G1–G14).

## 5. Challenges & limitations

**(a) MESH plausibility QC — the V1 rule (decided).** MESH is skillful at hail *occurrence* but unreliable for
hail *size*, so frequency is robust (a severe day is severe regardless of estimated size) while the *magnitude*
is not: across CONUS **585 cells** have a day with MESH ≥ 300 mm, record max **1,437 mm** — physically
impossible. The decided rule (grounded in the [MESH research](../../extra/discussion/conus_grid/hail/04_mesh_nature_and_qc_research.md)
+ the canonical damage curve; full rationale in [`05_plausibility_qc_rule.md`](../../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md)):

- **M0/M1 (asset-free): physical-plausibility cap + flag at ~200 mm** (US record, Vivian SD 2010 ≈ 203 mm) —
  cap the severity summary, keep raw + flag, leave the severe-day count (frequency) untouched; **≥ 300 mm = hard artifact**, never delete.
- **M3 (solar): the damage curve clamps at 100 mm** (its declared valid range, ≥99% saturated) — so solar
  loss is *insensitive to MESH above 100 mm*. The grid's `cap_100mm` policy is exactly this.
- **Frequency spikes:** flag suspicious high-λ cells and hold them out of reportable loss; spatial pooling
  deferred (this rule is ours — no literature standard exists).

Applied *identically* in both deployments (it's a property of the MESH signal, not the asset). **Deferred to
V1.5/V2:** MESH de-biasing, EVT tail, frequency pooling.

**(b) Short record (~5.65 yr) — *not* a V1 problem to solve.** Frequencies and especially the deep tail are
real but noisy on five operational years. The planned fixes (MYRORSS back-fill to extend the record, MESH
de-biasing à la Murillo & Homeyer, an EVT severity tail) are deliberately **deferred to V1.5/V2** — see
[LL01](../../learning_logs/01_extending_a_short_hazard_record.md).

**(c) Daily event grain.** One event = one hail-day (the MRMS product is a 24-h max). Acceptable for hail
(most severe reports cluster in a single window); sub-daily / storm-splitting is a future refinement, noted.

**(d) Sparse cells (grid only).** Quiet cells have few or zero severe days, so their per-cell rate is noisy —
the cost of going local. Remedy on the roadmap: sparse-cell pooling / spatial shrinkage.

## 6. Maturity — V1 vs. deferred

| | Reportable now | Provisional / screening | Deferred (V1.5 / V2) |
|---|---|---|---|
| **Deep per-asset** | EAL, ~PML₁₀₀ (distribution *body*) | the deep tail (bootstrap-truncated) | EVT severity tail, damage-curve calibration, financial terms |
| **CONUS grid** | per-cell **frequency** screening | severity & all loss metrics (raw-MESH tail unresolved) | the severity QA decision (§5a), sparse-cell pooling, record extension |

The guiding line: **a V1 cell is a vertical slice that runs end-to-end and is honest about its limits — not a
calibrated product.** (Principle `good_enough_for_v1`, being formalized.)

## 7. Go deeper

- **Reasoning:** [`discussion/conus_grid/`](../../extra/discussion/conus_grid/README.md) (+ `hail/`).
- **Source selection:** [`source_selection.md`](source_selection.md).
- **Decisions / plan-of-record:** [`plans/hail/`](../../plans/hail/) (deep run) · [`plans/hazard_conus_grid/hail/`](../../plans/hazard_conus_grid/hail/) (grid).
- **Code:** [`Notebooks/hail/`](../../../Notebooks/hail/README.md) (deep) · [`Notebooks/hazard_conus_grid/hail/`](../../../Notebooks/hazard_conus_grid/hail/README.md) (grid).
- **Per-asset:** [hail × solar](solar.md).
