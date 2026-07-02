# Hail — peril overview

The **hail** hazard, organized `peril → asset`. This folder holds the **shared hail catalog**
(asset-independent); the per-asset pipelines (coupling → damage → loss) live in the asset subfolders.
Driven by the plan in [`../../docs/plans/hail/`](../../docs/plans/hail/README.md). Kernel: `.venv`
(`hazard_modeling`).

```
hail/
  m0_input_data/   ← raw evidence: NOAA reports + MRMS/MYRORSS gridded radar       ┐ the PERIL
  m1_catalog/      ← canonical events (footprint polygons) + NegBin frequency fit ┘ (asset-independent)
  solar/           ← hail × SOLAR — coupling · damage · loss & metrics    ✅ built end-to-end
  # wind/          ← hail × WIND FARM — next (see "how a wind farm differs" below)
```

> **New here?** Read the shared catalog below (M0 → M1), then open **[`solar/`](solar/README.md)** for
> the full M2→M4 worked example and the headline risk numbers.

---

## The shared hazard catalog (M0 → M1) — built once, reused by every asset

A hail event catalog over the region is the same regardless of what sits underneath it, so M0/M1 live
at the **peril** level. Only M2–M4 (coupling/damage/loss) specialize per asset.

### M0 — input data  ·  [📖 folder README](m0_input_data/README.md)

Multiple sources behind one interface; each notebook does a complete-pass field dictionary (per
`docs/principles/notebook_work/`).

| Notebook | Source | Grain | Status |
|----------|--------|-------|--------|
| `m0_input_data/01_noaa_hydronos.ipynb` | NOAA Storm Events (Hydronos API) + FEMA NRI (reference-only) | **point reports** (hail size + location; no footprint) | ✅ built + executed |
| `m0_input_data/02_mrms_aws.ipynb` | MRMS MESH (AWS Open Data) | **gridded** → real event **footprints**; opens with a from-scratch "what is this data" walkthrough (§1–§7) | ✅ built + executed |
| `m0_input_data/03_myrorss_reanalysis_source_qualification/` | MYRORSS MESH reanalysis | **gridded** source qualification; current outputs include a selected-cell grid adapter proof, not a final climatology | research/qualification in progress |

### M1 — event catalog + frequency  ·  [📖 folder README](m1_catalog/README.md)

MRMS hail-days → one canonical `Event` per physical event (real footprint-swath polygons) +
`CatalogManifest`; NOAA cross-checks (adds no events). **Frequency fitted** on the ~5.65-yr record:
`λ_collection = 29.6/yr`, over-dispersed → **Negative Binomial** (Fano `φ = 3.37`).

| Notebook | What | Output | Status |
|----------|------|--------|--------|
| `m1_catalog/01_event_catalog.ipynb` | MRMS hail-days → canonical `Event` records + manifest; NOAA cross-check → `confidence_flags`; NegBin frequency fit | `data/hail/hayhurst_hail_m1_catalog.parquet` (**GeoParquet**) + `…_catalog.geojson` + `…_m1_manifest.json` | ✅ built + executed |

### Why two sources — and why they don't merge (DD-1 / DD-3)

```text
        NOAA (long, biased, points)        MRMS (short, clean, footprints)
                 │                                   │
                 │     ✗ naive splice                │
                 │       (rate jump at seam)         │
                 │                                   │
                 ▼                                   ▼
        ┌─────────────────┐               ┌─────────────────────┐
        │ cross-check /   │               │ THE SPINE:          │
        │ calibration     │──validates──► │ events, footprints, │
        │ (adds 0 events) │               │ λ_collection, p     │
        └─────────────────┘               └─────────────────────┘
                 │
                 └─► later (Stage 2): bias-correct MESH FAR → extend λ record
```

MRMS is the **spine** (footprints + current rate); NOAA's value is its **decades of length**, used —
bias-corrected against MRMS — to *extend* the rate to a longer, more credible record (DD-3 Stage 2,
not yet done). A naive temporal splice would fabricate a rate discontinuity at the seam. See
[`learning_logs/01`](../../docs/learning_logs/01_extending_a_short_hazard_record.md) +
[`04`](../../docs/learning_logs/04_two_datasets_one_peril_decompose.md) and
[`decisions.md`](../../docs/plans/hail/decisions.md) (DD-1, DD-3).

### Catalog artifact lineage (M0 → M1)

```text
 Hydronos API          AWS Open Data (MRMS GRIB tiles)
      │                        │
      ▼                        ▼ (scripts/scan_mrms_record.py — cache-first, resumable)
 …_m0_noaa_50mi.parquet   …_m0_mrms_202010_202606.parquet      data/hail/mrms_raw/ (~905 MB, gitignored)
      │  (cross-check)         │  (spine)
      └──────────┬─────────────┘
                 ▼  m1_catalog/01_event_catalog
 …_m1_catalog.parquet (GeoParquet) + …_catalog.geojson + …_m1_manifest.json
            (the shared catalog → handed to every asset's M2)
```

---

## The per-asset pipelines

### ✅ Solar PV — [`solar/`](solar/README.md)

Hayhurst Texas Solar (EIA 66880, TIV $36.78M). A solar farm is a **dense areal polygon**, so hail
couples **areal hit-or-miss** — Minkowski `p = (√F + √s)² / A`. Built end-to-end **M2 → M3 → M4**
(coupling → damage → annual loss → EAL/VaR/PML/TVaR). Open [`solar/README.md`](solar/README.md) for
the full walkthrough and the headline numbers.

### Wind farm — next, and how it differs

The same shared catalog feeds a wind farm, but the **coupling changes** — the live test of
*"standard interface, not standard physics."*

- **Solar = dense areal polygon** → one footprint-vs-polygon overlap → Minkowski `(√F + √s)² / A`.
- **Wind farm = sparse cloud of point turbines** (we have the turbine lat/longs) scattered over a
  large lease → a bounding-polygon area *overcounts*; you intersect the footprint with the **turbine
  points** (which turbines got hit) — **per-turbine hit-or-miss** for hail, and **field-intensity**
  (sample the wind field at each turbine) for wind loads.

Same M0→M4 interface, genuinely different M2 physics. (A21 coupling-type dispatch; A12 onshore/offshore
asset split — `wind/` is reserved for the **onshore** wind farm, offshore a later sibling. A21 flags
this as the *"wind-farm open question."*) Method provenance — external citations + A-series links — is in
[`docs/references/`](../../docs/references/README.md).

---

## Production path (peril-level)

Widen the MRMS record → a more credible λ (NOAA-calibrated extension, **DD-3 Stage 2** — the main lever
on the headline numbers); calibrate the damage curve to PV claims; add financial terms + an EVT-GPD
tail. The `deferred` rows in the [assumptions register](../../docs/plans/hail/assumptions.md) are the
backlog that turns this skeleton into a production model.

## M0-M4: What Each Layer Asks

```text
M0 asks:
  what hail evidence exists near the asset?
  is the source a point report, gridded radar field, or reanalysis?
  what does one raw record mean?
  what bias or coverage trap comes with the source?

M1 asks:
  what is one physical hail event?
  which source is the event spine?
  what footprint polygon and hail size does each event carry?
  what annual count model should generate future regional events?

M2 asks:
  for each event footprint:
    how big is the swath?
    how big is the asset?
    what is the probability the swath overlaps the asset?
    is that probability kept in frequency, not multiplied into loss?

M3 asks:
  if the event hits:
    what hail size reaches the asset?
    what solar components are vulnerable?
    what capex-weighted damage ratio applies?
    what is the full conditional loss?

M4 asks:
  over many simulated years:
    how many regional hail events occur?
    for each event, does the weighted hit coin land?
    if hit, what full conditional loss is applied?
    what annual AEP/OEP loss vectors and risk metrics result?
```

The core hail discipline is:

```text
p_hit belongs to frequency.
conditional_loss belongs to severity.
M4 combines them stochastically.

Do not use p_hit * loss as the simulated event loss.
```
