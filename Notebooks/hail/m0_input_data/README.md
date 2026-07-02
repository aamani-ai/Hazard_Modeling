# M0 — Input Data (raw hazard evidence)

*The first layer: meet the raw hail data and **understand** it, before any modeling. "What hail actually
happened near the asset, and what do we really know about it?"*

**Where this sits:** **M0 (evidence)** → [M1 catalog](../m1_catalog/) → [M2 coupling](../solar/m2_coupling/) → M3
damage → loss & metrics. M0 has **no losses and no events-as-objects yet** — it is just the *evidence*, each
source explored on its own terms. Method-neutral (understanding, not the model).

## What this layer does

For each raw data **source**, it explores what the data *is* — its coverage, biases, what one record looks
like, the traps — and emits a clean per-source M0 record. The deep field-by-field interpretation lives in
the notebooks (per the [exploratory-notebook principle](../../../docs/principles/notebook_work/exploratory_data_notebooks.md)).

## Sources — different *kinds* of hail evidence

| Notebook | Source | What it is | Strength | Weakness |
|---|---|---|---|---|
| [`01_noaa_hydronos`](01_noaa_hydronos.ipynb) | NOAA Storm Events (API) | a **list of events** — point reports ("someone saw 1.5″ hail here, then") | long record (1996→); easy | population-biased; **no footprint** |
| [`02_mrms_aws`](02_mrms_aws.ipynb) | MRMS MESH (AWS files) | a **gridded radar field** — a hail-size number at every ~1 km pixel | complete coverage; **real footprints** | short record (~2020→); complex raw format |
| [`03_myrorss_reanalysis_source_qualification`](03_myrorss_reanalysis_source_qualification/README.md) | MYRORSS MESH reanalysis | an older **gridded radar reanalysis** source being qualified before use | longer gridded era (1998-2011); useful for record extension/source comparison | complex sparse netCDF; not yet a final climatology; current selected-cell outputs are grid-adapter proof only |

**Why multiple sources?** They're complementary — NOAA's length and ground reports vs MRMS/MYRORSS gridded
radar evidence. *Which one is primary* is decided in M1 ([DD-1](../../../docs/plans/hail/decisions.md): MRMS
is the first spine, NOAA the cross-check). MYRORSS is being qualified as a later long-record gridded
extension/comparison source; it should not be silently merged into the MRMS spine.

`02` and `03` use a from-scratch source-understanding style because gridded radar is genuinely harder to
read than a tidy API table (see
[learning_logs/03](../../../docs/learning_logs/03_meet_complex_raw_data_from_scratch.md)).

## Inputs → outputs

Live data (NOAA via Hydronos API, MRMS via AWS Open Data, MYRORSS via NOAA public object storage) →
`data/hail/hayhurst_hail_m0_noaa_50mi.parquet`, `…_m0_mrms_*.parquet`, and source-qualification artifacts.
The current MYRORSS selected-cell artifacts intentionally write under `data/hazard_conus_grid/hail/`
because they prove the benchmark-grid adapter, not because the source qualification is grid-only. Raw MRMS
tiles are cached under `data/hail/mrms_raw/`.

## Key decisions & learnings

[DD-1](../../../docs/plans/hail/decisions.md) (MRMS-only spine) · [learning_logs/01](../../../docs/learning_logs/01_extending_a_short_hazard_record.md)
(short record) · [learning_logs/03](../../../docs/learning_logs/03_meet_complex_raw_data_from_scratch.md) (complex raw data).

## Assumptions (this layer)

A1 region = 50-mi circle · A2 severe threshold = 25.4 mm (1″) · A3 window = Apr–Jun 2024 *(deferred — widen
for real λ)* · A4 daily grain = last tile ≈ 24-h max · A5 MESH is a radar *estimate*, not ground truth. Full
detail + status + revisit-triggers: [assumptions register A1–A5](../../../docs/plans/hail/assumptions.md#m0--input-data).

**Next → [M1 (catalog)](../m1_catalog/):** turn this evidence into one clean event catalog.

## What Hail M0 Asks

```text
M0 asks, for each source:
  what does the raw record represent?
  is it a point report or a gridded radar estimate?
  what spatial and temporal grain does it have?
  what threshold defines severe hail?
  what does the source miss or bias?
  what artifact can M1 safely consume?
```

It does not ask:

```text
  which event hits the asset?
  what is the damage curve?
  what is the annual loss?
```

Those are M2-M4 questions. M0 is source understanding and clean evidence extraction.
