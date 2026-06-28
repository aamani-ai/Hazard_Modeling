# 01 — CONUS Grid: Ideal Architecture, Compute, and Which Grid

*A discussion doc, not a plan. Opening position on three coupled questions the owner raised:
**(a) what does the ideal architecture look like, (b) how long does it take on Cloud Run — even for the hard
hazard (hail), and (c) which grid?** Each section ends with an open question; the owner's calls become
`DD-*` / `A-*` in `docs/plans/`.*

---

## TL;DR (the whole argument in one screen)

1. **The target is the ideal state, full-fidelity.** Place a canonical **100 MW solar + 100 MW wind** at each
   grid-cell centre and run the **exact same M0→M4** we run per asset → a per-cell risk matrix. No
   dumbed-down "screening math." *Screening ≠ low quality.*
2. **The grid is settled: reuse the wildfire-index grid** — `0.25°`, **17,543** full / **13,085** CONUS cells.
   Reusing it (not inventing one) is what makes the hazard tier *consistent* with the rest of the platform
   (Shruti's benchmark grid, Yuri's point-vs-cell validation, the wildfire index).
3. **The architecture is two stages with one storage boundary between them:**
   **Stage 1 — the hazard field (M0/M1)**, built **once per hazard** on the grid → persisted as a *compact
   per-cell distribution layer*. **Stage 2 — the loss engine (M2–M4)**, **embarrassingly parallel** per
   (cell × canonical asset). M2–M4 is **identical** across all hazards and cells; **all the per-hazard
   difficulty lives in Stage 1.**
4. **Hail is not "recreating GridRad" — at the grain we use.** The whole CONUS hail record at our
   **daily-max** grain (`MESH_Max_1440min`, 1 file/day) is **2,063 files ≈ 945 MB, already on disk.** The
   GridRad-scale fear is real only for *sub-daily* volume scans (tens of TB), which v1 doesn't use (A4).
5. **So the ideal hail grid is reachable on Cloud Run in ~hours, not weeks** — and wildfire/wind are easier.
   The honest bottleneck is engineering Stage 1 correctly per hazard, not raw compute.

---

## 1. The target (restating the ideal state so the doc stands alone)

```text
for each of the 13,085 CONUS cells:
    place canonical 100 MW solar  at cell centre  ─┐
    place canonical 100 MW wind   at cell centre  ─┤→ run FULL M0→M4 → {EAL, PML(AEP+OEP), VaR, TVaR}
                                                    │   per cell, per asset, per hazard
                                                    └   reported in $ AND % of TIV
```

This is the same engine as the per-asset product (use case 1) with the asset held canonical. We are **not**
building a second, lighter pipeline — the legitimate "fast layer" instinct, if we ever need it, survives only
as a **surrogate fitted to this engine's own outputs**, never as an independent method. *(Out of scope here;
noted so it isn't reopened as "Method A".)*

> **Open Q1 — canonical asset.** Lock `100 MW solar + 100 MW wind` as the canonical pair? Reporting in
> **% of TIV** makes the MW choice wash out of the headline metric (it scales dollars ~linearly); we'd carry
> absolute $ alongside. *(Lean: yes — clean, and % of TIV is already the house display.)*

---

## 2. The grid — reuse the wildfire index grid

`[REF]` Spec, from the wildfire lab's `grid_resolution_and_source_caveats.md`
(`renewablesinfo/wildfire_analysis_lab/docs/methodology/`):

| Property | Value |
|---|---|
| Resolution | **0.25° × 0.25°** (cell bounds = centre ± 0.125°) |
| Full benchmark grid | **17,543** cells (keeps Alaska + no-data rows for grid compatibility) |
| CONUS (valued) subset | **13,085** cells |
| Cell area | **~500–700 km²**, latitude-varying |
| N–S height | ~27.8 km (constant) |
| E–W width | 25.2 km @ 25°N → **18.2 km @ 49°N** (longitude narrows northward) |
| Per-cell stats convention | `mean` (primary), `max` (hotspot), `count` (QA) |

**The border / corner nuances the owner flagged:**
- **Latitude-varying width** → cells are not equal-area; a CONUS-corner cell (N border) is ~25% smaller E–W
  than a southern one. Matters when we normalise event *density* per km² (`[OURS]` learning-log 06's `ρ`).
- **Full vs CONUS rows** → the full 17,543 grid carries no-data/border rows; serve the **13,085** valued
  subset, but **distinguish "no coverage" from "genuinely zero risk"** (the legacy silently mapped null→0).
- **County-boundary discontinuities** → Yuri's validation already sees values jump at county lines (county
  statistics). Expected, not a bug; relevant because our *consistency* claim is judged against his point↔cell
  checks. `[REF]` (Thursday sync, Yuri.)

**Why reuse, not invent:** a cell is *"a regional screening unit, not a project boundary"* — and reusing the
platform grid is what lets the hazard tier plug straight into the benchmark grid / point model / validation
dashboards. Inventing a hazard-native grid would re-create the very grid-vs-point drift that produced the
current EAL-percentage bug (§4).

> **Open Q2 — grid lock.** Commit to the **0.25° benchmark grid (full 17,543 / serve 13,085)**, native hazard
> data aggregated *up* to it? *(Lean: yes.)* Sub-question: is `mean` the right primary per-cell statistic for
> *frequency-type* hazards (hail event rate), or do we need `max`/`p95` to avoid diluting a high-risk pocket
> in a 600 km² cell (the same dilution caveat the wildfire lab calls out)?

---

## 3. The ideal architecture — two stages, one storage boundary

```text
 ┌─────────────────────────── STAGE 1: HAZARD FIELD (M0 / M1) ───────────────────────────┐
 │  built ONCE per hazard, on the grid.  THIS is the expensive, hazard-specific part.     │
 │                                                                                         │
 │   raw hazard data ──→ event extraction / footprints ──→ aggregate to 0.25° cell ──┐    │
 │   (MRMS, FSim, …)      (threshold, label)                (this step = the spatial  │    │
 │                                                            smoothing MRMS needs)   │    │
 │                                                                                    ▼    │
 │                                          ╔══════════════════════════════════════════╗  │
 │                                          ║  PER-CELL HAZARD-DISTRIBUTION LAYER       ║  │
 │   ◄── THE STORAGE BOUNDARY (Colby:       ║  per cell: fitted frequency dist          ║  │
 │       "decide storage early") ──►        ║  (NegBin λ, φ) + magnitude/footprint dist ║  │
 │   persist THIS (tiny); raw rasters       ║  ~13k cells × a few params  →  < few MB   ║  │
 │   become a rebuildable cache.            ╚══════════════════════════════════════════╝  │
 └────────────────────────────────────────────────────────────────────│────────────────────┘
                                                                        │  (cheap to read)
 ┌─────────────────────────── STAGE 2: LOSS ENGINE (M2 / M3 / M4) ──────▼────────────────────┐
 │  EMBARRASSINGLY PARALLEL across (cell × canonical asset).  IDENTICAL code for ALL hazards. │
 │     read cell hazard dist → M2 couple to canonical asset → M3 damage → M4 compound-NegBin  │
 │     Monte Carlo → {EAL, PML, VaR, TVaR}.   13k cells × 2 assets → fan out → minutes.       │
 └────────────────────────────────────────────────────────────────────────────────────────────┘
```

Three consequences worth internalising:

- **The per-hazard "how" reduces to Stage 1 only.** M2–M4 never changes. So *"how do we reach the ideal state
  for hazard X"* ≡ *"how do we get hazard X's per-cell M1 distribution layer."* That splits hazards cleanly:

  | Bucket | Stage 1 is… | Cost | Example |
  |---|---|---|---|
  | **1 — ready-made field exists** | *ingest + interpret + fit* | cheap | **Wildfire**: FSim/WRC already ships per-cell burn-prob + flame-length. FSim *is* a pre-simulated catalog. |
  | **2 — build the field from raw** | *catalog → aggregate → fit* | heavier | **Hail** (MRMS), likely **tornado** |

- **The storage boundary is the decision Colby told us to make early.** M4's MC consumes the *fitted
  distributions*, **not** the raw event list — so persist the per-cell distribution layer (tiny, durable,
  versioned) and treat raw rasters as a rebuildable cache. This is identical whether we serve the grid or a
  single asset — more evidence the two use cases are one engine.

- **"Scale to CONUS" and "de-noise MRMS" are the same step.** Aggregating native ~1 km MESH up to the 0.25°
  serving cell *is* the spatial smoothing Colby said noisy MRMS needs. One operation, two birds. `[OURS]`

### 3b. The two saved products — hazard layer first, risk layer second

This is the distinction to keep explicit before adding more grid detail: the CONUS product has **two durable
layers**, and they answer different questions.

| Layer | Built by | One row means | Contains | Does it contain EAL / PML / VaR? |
|---|---|---|---|---|
| **1. Per-cell hazard-distribution layer** | **Stage 1 (M0/M1)** | "What is the hazard process in this cell?" | frequency distribution (`λ`, `φ`, family), magnitude / severity / footprint distribution, fitted-tail params, record span, data vintage, `n_events_cell`, QA flags | **No** — it is the reusable hazard input |
| **2. Per-cell risk-metrics layer** | **Stage 2 (M2–M4)** | "What loss does the canonical asset suffer in this cell?" | EAL, AEP/OEP curves, PML, VaR, TVaR, annual exceedance probabilities, all in `$` and `% of TIV`, for `solar` and `wind` | **Yes** — this is the map/query output |

So the storage boundary in Stage 1 is **not** the final map product. It is the durable hazard layer that makes
the final metrics reproducible. Stage 2 reads it, places the canonical asset, runs coupling + damage + annual
loss simulation, and writes the risk layer. In metric language:

```text
Stage 1 artifact:
  cell_id, hazard, frequency_dist, severity_dist, provenance, QA

Stage 2 artifact:
  cell_id, hazard, asset_type,
  eal, aep_curve, oep_curve,
  var_aep_95, var_aep_99, var_aep_99_5,
  pml_aep_rp100, pml_aep_rp200, pml_aep_rp250, pml_aep_rp500,
  tvar_aep_95, tvar_aep_99,
  exceedance probabilities,
  all dollar metrics also as % of TIV
```

`PML_T` and `VaR_{1-1/T}` are the **same readout** of the same curve (`PML100 ≡ VaR99`; `PML200 ≡ VaR99.5`;
`PML250 ≡ VaR99.6`; `PML500 ≡ VaR99.8`). We store named columns for map/query convenience, but they must
remain derived from the stored AEP/OEP curves — not separately simulated numbers. Full column detail lives in
[`02_per_cell_output_schema.md`](02_per_cell_output_schema.md).

### 3c. Why wildfire is easier than hail — the approach is set by how M1 arrives

This is the planning rule that should stop us from treating every hazard as the same engineering job:
**the grid difficulty is determined by how the M1 hazard layer arrives.** M2-M4 can stay shared; M0/M1 cannot.

| Hazard | How M1 arrives | What Stage 1 must do | Why that matters for the build |
|---|---|---|---|
| **Wildfire** | **Pre-integrated field**: FSim/WRC already gives annual burn probability plus conditional flame-length / intensity classes | Ingest, sample / aggregate to the grid, interpret BP as `λ`, carry the severity profile | Mostly a data-ingestion + interpretation job. The upstream simulator already produced frequency + severity. |
| **Hail** | **Raw gridded evidence**: MRMS/MYRORSS MESH grids estimate hail size by timestep/day, but do not give a fitted per-cell frequency or full size distribution | Threshold, label events / hail-days, aggregate native pixels to 0.25°, fit frequency, build size distribution, de-bias MESH, validate against reports, handle sparse cells and tail fitting | A real M1 construction job. We have to create the hazard-distribution layer before the loss engine can run. |

So **wildfire × solar is easier than hail × solar at the CONUS-grid stage** because wildfire's hazard product
already contains the stochastic profile we need, while hail's hazard product is only raw evidence from which
we must infer the profile. This does **not** mean wildfire is "perfect" — susceptibility and damage assumptions
still matter — but it means the hard work is different: wildfire's risk is mostly about honest interpretation
and canonical susceptibility; hail's risk starts with building a trustworthy per-cell frequency + size layer.

This distinction is the grid version of [learning-log 09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md):
classify the hazard by **how the data arrives** before choosing the M1 machinery. The hail-specific conclusion
is documented in [`hail/01_m1_sourcing_triage.md`](hail/01_m1_sourcing_triage.md): hail is **self-build,
anchored**, not a ready field.

---

## 4. Compute & timing on Cloud Run — including the hard case (hail)

**The reframing finding (grounded in the record on disk).** Colby's warning was *"2 km across the whole US
for however many time steps… almost recreating GridRad."* The killer is *"however many time steps."* But we
use the **daily-max** product (`MESH_Max_1440min`, A4 = 24-h max, **1 file/day**). At that grain:

```text
Hail CONUS record, daily-max grain  (data/hail/mrms_raw/_manifest.json)
  span      2020-10-15 → 2026-06-08   (~5.65 yr)
  files     2,063  national daily mosaics
  size      mean 0.46 MB · max 1.76 MB · TOTAL ≈ 945 MB     ← already downloaded
  native    ~1 km (0.01°) national grid ≈ 3,500 × 7,000 ≈ 24.5M cells/day
            (a 0.25° serving cell ≈ 25×25 ≈ 625 native cells)
```

**945 MB, not tens of TB.** The national daily-max files were *already pulled* for the single-site build
(the site pipeline downloads the national mosaic, then clips) — so going CONUS-wide adds **~zero download**
and only widens the spatial extent of processing. `[OURS]` *(Verify-cheaply: confirm a cached file is the full
3,500×7,000 grid via one `cfgrib` read — the filename + sparse-compressed size strongly imply national.)*

**Rough wall-clock on Cloud Run** (order-of-magnitude — arithmetic shown, to confirm by a 100-cell pilot):

| Step | Work | Single-thread | Parallel (Cloud Run Jobs) |
|---|---|---|---|
| S1 download | 945 MB from `noaa-mrms-pds` (AWS) — or 0 if cached | minutes | minutes |
| S1 process | 2,063 daily grids × {threshold ≥25.4 mm, label footprints, aggregate→0.25°} @ ~1–5 s/day | ~0.5–3 h | **minutes** (per-day independent) |
| S1 fit | fit NegBin λ,φ + size dist for ~13k cells | minutes | minutes |
| S2 loss | 13k cells × 2 assets × MC | ~hours¹ | **minutes–~1 h** (task array) |

> ¹ S2 single-thread depends on MC depth. **300k years/cell** (what a single *deep* asset uses) × 26k runs is
> overkill; a grid likely needs **~50–100k years/cell** for stable body metrics → seconds/run. **Open Q3.**

**Cloud Run mapping:** use **Cloud Run *Jobs*** (batch), not a Service. Stage 1 = one job (a few large
containers, sharded by date-range). Stage 2 = a **task array** (`--tasks N`), each task owns a slice of cells,
all reading the shared per-cell distribution layer from GCS. Embarrassing parallelism → wall-clock collapses
to the slowest shard.

**Headline:** the **entire hail CONUS grid is reachable in ~1–2 h wall-clock** with modest parallelism — and
hail is the *hard* hazard. Wildfire (Bucket 1) is dominated by raster download, not modelling.

> **The fork to never cross silently:** if we ever need **sub-daily** footprint evolution (every ~2-min volume
> scan), the data jumps to **~1.5M timesteps → tens of TB** — *that* is GridRad scale. v1's daily-max grain
> (A4) is precisely what keeps us out of it. Any future move to sub-daily must re-open this estimate.

> **Open Q4 — storage boundary.** Confirm the durable artifact is the **per-cell hazard-distribution layer**
> (versioned, in GCS), with raw rasters as a rebuildable cache? *(Lean: yes.)*

---

## 5. One nuance that *is* hazard-dependent — what the canonical asset captures

The ideal state (full M0→M4 per cell) is the right target for **every** hazard. But what a **canonical** asset
*measures* per cell differs:

- **Hail (and areal hit-or-miss perils):** the canonical asset is a **mild** assumption — region area `A` and
  asset footprint `s` largely **cancel**, and `s ≪ F`, so the per-cell number barely moves with the exact
  plant geometry. The grid ≈ the asset-level answer. `[OURS]` ([learning-log 06](../../../learning_logs/06_collection_region_size_cancels.md)).
- **Wildfire (site-conditioned perils):** site susceptibility (defensible space, fuel against the array, BoS
  layout) swings the damage curve hugely and is **not** in the canonical asset. So the per-cell wildfire
  number is honestly *"loss to a **standard** 100 MW plant placed here"* — which is exactly the right question
  for a **comparable** map (hold the asset fixed → the map reflects *location/hazard* differences, not asset
  differences). But the absolute level is conditional on the assumed susceptibility.

This doesn't change the architecture; it changes the **label/interpretation** per hazard, and possibly argues
for running *N susceptibility scenarios* per cell for susceptibility-dominated perils. → **Open Q5.**

---

## 6. Open questions for the next round

1. **Q1 canonical asset** — lock `100 MW solar + 100 MW wind`, report % of TIV + $? *(Lean: yes.)*
2. **Q2 grid** — lock 0.25° benchmark grid (full 17,543 / serve 13,085); `mean` vs `max`/`p95` as the primary
   per-cell statistic for frequency hazards? *(Lean: lock the grid; revisit the statistic per hazard.)*
3. **Q3 MC depth for the grid** — 50–100k years/cell with a documented accuracy target, vs the 300k a deep
   asset uses?
4. **Q4 storage boundary** — persist the per-cell distribution layer as the durable artifact; raw rasters as
   cache? *(Lean: yes.)*
5. **Q5 next deep-dive** — the **per-hazard M0/M1 sourcing triage, starting with hail**: build hail's field
   from the MRMS daily-max record we already hold, **or** first check for a ready **GridRad-Severe /
   MESH-climatology** product (the wildfire-style "ready field" — which would be *higher* quality, not a
   shortcut)? And do susceptibility-dominated perils get N scenarios per cell?

---

## Cross-references

- The two use cases + why this is one engine: [`README.md`](README.md).
- Wildfire = the Bucket-1 "ready field" case: [`../wildfire/01_v1_scope_and_framing.md`](../wildfire/01_v1_scope_and_framing.md).
- Canonical-asset robustness for hail (`A`, `s` cancel): [`../../../learning_logs/06_collection_region_size_cancels.md`](../../../learning_logs/06_collection_region_size_cancels.md).
- Hail assumptions (A4 daily-max grain; A8 NegBin frequency): [`../../../plans/hail/assumptions.md`](../../../plans/hail/assumptions.md).
- The shared M0→M4 journey: [`../gpt/05_m0_to_m4_full_modeling_journey.md`](../gpt/05_m0_to_m4_full_modeling_journey.md).
- `[REF]` grid spec: `renewablesinfo/wildfire_analysis_lab/docs/methodology/grid_resolution_and_source_caveats.md`.
- `[REF]` Thursday sync (Colby on MRMS noise + GridRad scale; Yuri on point↔cell validation):
  `~/Desktop/infrasure/meets/thursday-data-modeling-sync-meeting.md`.
