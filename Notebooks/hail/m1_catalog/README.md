# M1 — Event Catalog (M0 → M1)

*Turn the raw evidence into one clean, reusable catalog of hail **events** — the object the old repo never
built. "What are the distinct hail events near the asset, each as a single tidy record?"*

**Where this sits:** [M0 evidence](../m0_input_data/) → **M1 (catalog)** → [M2 coupling](../solar/m2_coupling/) →
M3 damage → loss & metrics.

## What this layer does

It **normalizes** the M0 evidence into **one canonical record per physical hail event** — a *footprint
bundle*: the event's footprint **polygon**, its peak hail size, when, and where. This is **not** a 50/50
merge of the two sources:

- **MRMS is the spine** — it supplies the footprint geometry (the seam needs a *shape*, not a bare point).
- **NOAA is a cross-check** — it validates the spine and flags confidence; it **adds no events**.

One event = one **hail-day** (the natural unit of the 24-h-max radar product). The catalog also writes a
**manifest** — a self-description declaring its five choices (ontology, backbone, interface object, frequency
process, magnitude metric).

## Why it's built this way (and what it deliberately avoids)

- **Not a symmetric merge / dedup.** Combining two sources of the same peril = *one primary spine + one
  cross-check* ([DD-1](../../../docs/plans/hail/decisions.md)), not two parallel event streams.
- **Footprints, stored as real geometry.** Each event is a (Multi)Polygon (GeoParquet) so M2 can do true
  overlap — not just a centroid.
- **Frequency = Negative Binomial, fit deferred.** Hail counts cluster (over-dispersed), so the count
  distribution is declared NegBin with a prior, and the *rate* is fit later when the record widens
  ([DD-2](../../../docs/plans/hail/decisions.md)).
- **The undercount shows up for real:** the region's biggest hail day had **zero** NOAA reports — exactly the
  bias [learning_logs/01](../../../docs/learning_logs/01_extending_a_short_hazard_record.md) predicts.

## Inputs → outputs

M0 parquets → `data/hail/hayhurst_hail_m1_catalog.parquet` (**GeoParquet** — events with footprint polygons,
area, centroid, peak size, NOAA `confidence_flags`) + `…_m1_catalog.geojson` + `…_m1_manifest.json`.

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_event_catalog`](01_event_catalog.ipynb) | MRMS hail-days → canonical `Event` records + `CatalogManifest`; NOAA cross-check | the GeoParquet + GeoJSON + manifest |

## Key decisions & learnings

[DD-1](../../../docs/plans/hail/decisions.md), [DD-2](../../../docs/plans/hail/decisions.md) ·
[learning_logs/01](../../../docs/learning_logs/01_extending_a_short_hazard_record.md),
[/02](../../../docs/learning_logs/02_count_distribution_and_dispersion_prior.md) · plan:
[phase-2-event-catalog](../../../docs/plans/hail/phase-2-event-catalog.md).

## Assumptions (this layer)

A6 one event = one hail-day · A7 MRMS spine + NOAA cross-check (no events added) · A8 frequency = Negative
Binomial *(fit deferred)* · A9 dispersion prior (Fano φ ≈ 2) · A10 footprint = union of above-threshold cells
(no smoothing). Full detail + status: [assumptions register A6–A10](../../../docs/plans/hail/assumptions.md#m1--event-catalog).

**Next → [M2 (coupling)](../solar/m2_coupling/):** for each catalog event, does it hit the asset?
