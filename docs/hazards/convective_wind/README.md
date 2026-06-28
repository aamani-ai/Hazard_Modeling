# Convective wind — hazard anchor

**The shareable snapshot of how we model convective wind.** This page is *asset-free* — it covers the peril
itself (the hazard layer, `M0/M1`): what convective wind is, the two sub-perils, how we turn two very
different data products into a credible frequency + severity, how the two deployments differ, and what's
reliable vs. not. How wind *damages a specific asset* lives in the per-asset pages
([convective wind × onshore wind](wind.md)).

> **New to convective-wind physics/data?** Start with
> [`fundamentals_before_m0.md`](fundamentals_before_m0.md): the prerequisite mental model for the authored
> layer-0 definition, 3-s gust, tornado-vs-strong-wind split, and the two different M2 coupling paths.
> For the source decision itself, read [`source_selection.md`](source_selection.md): why strong wind uses ASCE
> return-period gusts while tornado uses SPC/NOAA path/report evidence.

> **One-line state:** convective wind is **one peril, two sub-perils** — *tornado* (rare, violent, narrow) and
> *strong / straight-line wind* (common, broad, mild) — sharing one observable (the **3-s peak gust**) but
> needing two catalog machineries. For a wind farm it is a **tail peril**: the headline risk is the rare
> tornado (a real PML/TVaR signal); strong wind does **≈0 catastrophic damage** (its real impact is operational,
> handled in the Performance tier). The hazard layer is sound; the **turbine fragility curve (M3) is the
> dominant uncertainty**.

---

## 1. What convective wind is, and the magnitude we model

Convective wind is severe wind from convective storms. It is **one peril with two sub-perils**, which look
nothing alike as hazards but share a turbine and an observable:

- **Tornado [T]** — rotating, narrow path, violent. (areal hit-or-miss for an asset)
- **Strong / straight-line wind [W]** — broad-swath synoptic / derecho / downburst. (site-conditioned)

The universal intensity variable is the **3-second peak gust** (m/s) — the structural-engineering standard
shared by ASCE 7-22, the EF scale, NWS, and IEC 61400. The single most important modeling discipline is that
convective wind has **two distinct thresholds**, and collapsing them is *the* anti-pattern the old repo fell
into:

```
  CONVECTIVE WIND = one observable (3-s peak gust), two sub-perils

   gust →   25.9      29          ~52–70                              113 m/s
            │ μ(W)    │ μ(T)        │ IEC 61400 survival                │ EF5 ceiling  L
            ▼         ▼             ▼                                   ▼
   ─────────┼─────────┼─────────────┼───────────────────────────────────┤──►
            └ EVENT THRESHOLD μ ┘    └────────── DAMAGE-ONSET ───────────┘
              what the CATALOG          where the DAMAGE CURVE
              counts (for λ)            leaves zero (M3)

              DR(μ) ≈ 0   ←  most "severe wind" barely scratches a turbine
```

| | Threshold | Governs | Lives in |
|---|---|---|---|
| **Meteorological event** μ | 58 mph ≈ **25.9 m/s** (NWS severe, W) / 65 mph ≈ **29 m/s** (EF0, T) | what the **catalog counts** (for λ) | M1 |
| **Asset damage-onset** | IEC 61400 survival ≈ Ve50 ≈ **52–70 m/s** | where the **damage curve leaves zero** | M3 |

The gap between them is the whole story: a turbine is engineered to survive its design gust, so **`DR(μ) ≈ 0`**
— the *count* of severe-wind days is large, but almost none of them damage a turbine. Severity is **bounded**:
the physical ceiling is the **EF5 cap `L ≈ 113 m/s`** (~253 mph). Two caveats ride along: the **EF scale is
damage-inferred** (read backwards from observed destruction, so it under-rates events over open/rural land —
§5), and the gust, not the sustained wind, is what fails things (load ∝ ½ρV²).

## 2. Data source & curation

Convective wind is unusual: its two sub-perils need **two different data products with two different curation
patterns** — it contains both the *wildfire* pattern (a pre-integrated product to ingest) **and** the *hail*
pattern (a biased raw record to self-correct), under one roof.

| Source | What / grain | Feeds | Curation |
|---|---|---|---|
| **ASCE 7-22 RP gust surface** (`gis.asce.org` ArcGIS backend) | a **pre-integrated EVT** return-period 3-s-gust surface (read per site, *no fit*) | **strong wind [W]** spine | **low** — ingest, like wildfire/FSim |
| **SPC SVRGIS tracks + severe-wind reports + NOAA Storm Events** | point / track reports (1950→), **population- & detection-biased** | **tornado [T]** raw evidence | **high** — must bias-correct *before* any λ fit (AWN-1) |
| **USWTDB** turbine point-cloud + boundary polygon + $/kW | the wind-farm geometry (footprint for coupling, TIV for % of TIV) | asset side (M2/M4) | — |

The **tornado curation is the hard, hail-like half**: the SPC record's weak-event share rises over the decades
(detection improving, not climate), the F→EF scale changed in 2007, post-2010 carries ~1,546 unrated
tornadoes, and wind reports are ~92 % *estimated*. Fitting λ on this naively (the old repo's omission) bakes in
the reporting bias — so M1 bias-corrects on a detection-stable window and cross-checks against the EF2+
record. The **strong-wind half is the easy, wildfire-like one**: ASCE already integrated the EVT, so M1 just
*reads* the curve. Source-selection rationale: [`source_selection.md`](source_selection.md). Deeper reasoning:
[`discussion/convective_wind/`](../../extra/discussion/convective_wind/README.md) (`01` taxonomy → `03`
thresholds).

## 3. How we model it — two deployments, and the sub-peril fork

Convective wind feeds **two products off the same `M0→M4` engine** — a *deep per-asset run* (a real asset at
its true location) and a *CONUS screening grid* (a canonical asset at every 0.25° cell). They share the spine,
and **the asset never enters until coupling (M2)**.

```
                    ONE engine    M0 ─► M1 ─► M2 ─► M3 ─► M4
                                   │
      ┌────────────────────────────┴────────────────────────────┐
      ▼                                                          ▼
  real asset, true location                         canonical asset, every cell
  150-km tornado collection · site ASCE gust        exact 0.25° cell
  ▶ DEEP PER-ASSET RUN   (built ✅)                  ▶ CONUS SCREENING GRID  (planned)
    (one trustworthy number)                          (a comparable map)

  └────────── M0 / M1 identical & asset-free ──────────┘   asset enters only at M2 ▶
```

But the structure that *defines* convective wind's hazard layer is not the deployment split — it's that the
**M1 catalog forks by sub-peril** into two machineries (the live test of *standard interface, not standard
physics*):

```
        ASCE 7-22 RP surface (W)            SPC SVRGIS + Storm Events (T)
        pre-integrated EVT                  point/track reports, biased
                 │                                     │
                 ▼  read RP curve → λ (no fit)          ▼  bias-correct → fit λ_collection + bounded GPD
        ┌──────────────────────────────────────────────────────────────┐
        │   M1 CATALOG   (per sub-peril {λ, severity})  →  M2/M4 contract │
        └──────────────────────────────────────────────────────────────┘
```

| | Strong / straight-line wind [W] | Tornado [T] |
|---|---|---|
| **Frequency λ** | **read** the ASCE RP curve → λ (profile-assembly, *no fit*) — the *wildfire* pattern | **fit** λ_collection from bias-corrected SPC, thinned by `p_hit` in M2 — the *hail* pattern |
| **Severity** | Gumbel / light-exponential (ξ≈0), capped at `L` | bounded **GPD** (ξ<0), truncated at the EF5 ceiling `L = 113 m/s` |
| **Dispersion** | `fano = 1` structural (ASCE pre-integrated it) | **fit** from SPC (NegBin if over-dispersed — outbreak clustering is real) |

The two **deployments** differ only at the hazard-layer edges (the deep run uses a fixed ~150-km tornado
collection region — whose *size* cancels in `λ_collection · p_hit`, [LL06](../../learning_logs/06_collection_region_size_cancels.md) —
and reads the site's ASCE gust; the grid would read canonical cells). The **CONUS grid is planned, not yet
built** (the grid driver is finishing hail × solar first), but the methodology is the one above.

The coupling (`M2`) and damage (`M3`) — where the sub-peril fork plays out on the *asset* — are on the
per-asset pages, e.g. [convective wind × onshore wind](wind.md).

## 4. Assumptions (load-bearing; full registers linked)

- **Observable = 3-s peak gust**; **two thresholds kept distinct** — event μ (58/65 mph) vs. damage-onset (IEC ~52–70 m/s), so `DR(μ)≈0` (AWN-5/6/9/10).
- **Severity bounded at `L ≈ 113 m/s`** (EF5 ceiling; the old repo's 145 m/s rejected, AWN-8).
- **SPC record is reporting-biased** → bias-correct on a detection-stable window before fitting tornado λ (AWN-1, frequency-critical).
- **Severity forms:** W = Gumbel/exponential (ξ≈0), T = bounded GPD (ξ<0), fit to the record/curve — *not* back-solved from a target EAL (AWN-17/18).
- Register: [`docs/plans/convective_wind/assumptions.md`](../../plans/convective_wind/assumptions.md) (AWN-1…AWN-32).

## 5. Challenges & limitations

**(a) The turbine fragility curve (M3) is the dominant uncertainty — and it's greenfield (AWN-26).** The old
repo had no turbine wind curve at all; ours is a physically-reasoned, capex-weighted subsystem blend, but it is
**Low confidence** and uncalibrated. Because the hazard layer is comparatively solid (ASCE for W; a
bias-correctable record for T), this curve is the headline open item — see
[convective wind × onshore wind](wind.md).

**(b) SPC reporting bias — frequency-critical (AWN-1).** If under-corrected, tornado λ reads low; if
over-corrected, high. Handled on a detection-stable window with an EF2+ (turbine-relevant) cross-check, but it
is the load-bearing uncertainty on the *frequency* side.

**(c) EF is damage-inferred → biased low over open land (AWN-7).** The EF rating is read from observed
destruction, so rural/open-country tornadoes (exactly where wind farms sit) are systematically under-rated —
the true tornado tail is likely *higher* than the EF-based return periods suggest.

**(d) Strong wind does ≈0 catastrophic damage — but that is not "no risk" (AWN-31).** Straight-line gusts stay
below IEC survival, so `DR ≈ 0` and W contributes almost nothing to the loss distribution — a clean
known-answer check. Its **real** impact is *operational* (curtailment + fatigue), which is a deliberately
**deferred disruption/degradation track** belonging to the **Performance tier**, not this catastrophic-loss
engine. State this explicitly so "strong wind ≈ 0" is not misread as "wind farms are safe from wind."

**(e) Single-site only; portfolio correlation deferred (AWN-22).** A broad-swath derecho hits many farms at
once, so portfolio tails are *correlated* — not yet modeled. Per-site EAL is correct; the portfolio tail is
future work.

**(f) Sparse tornado tail → read TVaR, not VaR (AWN-16).** A tornado is rare per site, so the Monte-Carlo tail
is sparse and VaR can floor to $0; **TVaR + its standard error are the honest tail reads**
([LL10](../../learning_logs/10_monte_carlo_effective_sample_size.md)).

## 6. Maturity — V1 vs. deferred

| | Reportable now | Provisional / screening | Deferred (V1.5 / V2) |
|---|---|---|---|
| **Deep per-asset** | **frequency** (esp. EF2+), EAL, and the **direction/contrast**; the **strong-wind ≈0** known-answer | the **tornado tail** (PML/TVaR) — real but record- *and* curve-limited (treat as a floor; EF rural-bias pushes it higher) | calibrated turbine curves, EVT refinements, portfolio correlation, the hurricane peril, the strong-wind disruption track, financial terms |
| **CONUS grid** | — | — (**not built yet**) | the full grid build + scaleout (after the hail-grid driver) |

The guiding line: **a V1 cell is a vertical slice that runs end-to-end and is honest about its limits — not a
calibrated product.** Convective wind's honest state: the *structure* is right (two sub-perils, two thresholds,
co-sampled into one distribution) and the *direction* is trustworthy (a tornado-alley site shows a real
catastrophic tail; a quiet site reads ≈0); the *exact tail* awaits calibrated fragility + a longer/less-biased
tornado record.

## 7. Go deeper

- **Reasoning:** [`discussion/convective_wind/`](../../extra/discussion/convective_wind/README.md) (`01` sub-peril taxonomy · `02` coupling buckets · `03` thresholds · `04` aggregation & double-counting).
- **Source selection:** [`source_selection.md`](source_selection.md).
- **Decisions / plan-of-record:** [`plans/convective_wind/`](../../plans/convective_wind/README.md) (DD-WN-* + the authored [hazard definition](../../plans/convective_wind/00_hazard_definition.md)).
- **Code:** [`Notebooks/convective_wind/`](../../../Notebooks/convective_wind/README.md) (layer0 → M0 → M1 → the wind-farm cell).
- **Lessons:** [LL06 collection-size cancels](../../learning_logs/06_collection_region_size_cancels.md) · [LL09 pre-integrated vs. extracted](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) · [LL12 EVT for a new peril](../../learning_logs/12_evt_for_a_new_peril.md).
- **Per-asset:** [convective wind × onshore wind](wind.md).
