# Phase 2 — Event Catalog (M0 → M1)

> **Status:** building (2026-06-09). Plan-of-record for the M0→M1 step. Decision basis:
> [`decisions.md` § DD-1](decisions.md); methodology: [`../../learning_logs/01`](../../learning_logs/01_extending_a_short_hazard_record.md).

The M0→M1 seam turns raw evidence into a clean, reusable **hail event catalog** — the object the old repo
never built. Per A20/A12, this is **normalization to one canonical record per physical event**, *not* a
symmetric merge or per-event dedup across sources.

## The shape (per DD-1 + A20 §3.6/§6, A12 §10)

- **One primary spine + one cross-check.** MRMS MESH (gridded) is the spine — it supplies the **footprint**
  the seam requires (A20: *a swath must cross the seam, never a bare point list*). NOAA point reports are a
  **calibration / cross-check overlay** — they validate the spine and set `confidence_flags`; **they do not
  add events.** This is A20's `HYBRID_VALIDATED` backbone.
- **Event = hail-day (v1).** The MRMS product is `MESH_Max_1440min` (24-h max), so the natural, defensible
  event unit is a hail-day (the calibration literature: >95% of a day's severe reports fall in one ~4-h
  window). Sub-daily declustering and connected-component swath-splitting are **deferred** (need the
  finer-cadence MESH product).
- **Interface object = footprint raster bundle** (`RASTER_BUNDLE`); magnitude metric = **peak stone diameter
  (in)** = peak MESH mm ÷ 25.4 (A12 hail row).
- **Footprint is stored as real geometry.** Each event carries a **(Multi)Polygon swath** (the above-threshold
  MESH cells vectorized), persisted as **GeoParquet + GeoJSON** (EPSG:4326). Scalars are derived *from* the
  geometry — `footprint_area_km2` via an equal-area projection (EPSG:5070), polygon centroid, bbox — so `F`
  is geometrically correct and a *true geometric overlap* (not just areal `F`) is available downstream.

## The two records we emit (A20 §10, §6.4 · A12 §10)

**`CatalogManifest`** (one JSON): `catalog_id`, `peril`, `event_ontology=SWATH`,
`historical_backbone=HYBRID_VALIDATED`, `stochastic_method=NONE`, `forward_looking=NONE`,
`interface_object=RASTER_BUNDLE`, `magnitude_metric`, `spatial_resolution_m`, `temporal_resolution`,
`climate_baseline`, `coverage_geometry` (50-mi circle), `coverage_temporal` (the **stated** window),
`provenance`, and **`frequency_process=negative_binomial`** (A24 §4.5) + `frequency_process_params`.

**`Event`** (one row/event): `event_id`, `event_family_id` (null for hail, field kept for cross-peril
extensibility — A13 F7), `catalog_id`, `peril`, `ontology`, `time_start_utc`/`time_end_utc`, `valid_time_utc`,
`intensity_field_ref` (→ cached raster), **`geometry`** ((Multi)Polygon swath, EPSG:4326), `footprint_area_km2`
(equal-area), `cell_count`, `n_footprint_parts`, `resolution_m`, `centroid_lon`/`centroid_lat` (polygon
centroid), `bbox_*`, `peak_intensity_mm`, `peak_intensity_in`, `annual_rate`, `confidence_flags`.

## Build steps (the notebook)

1. Load M0 MRMS (hail-day proto-events) + NOAA (points, filtered to the overlap window).
2. **Materialize footprint bundles** — re-open each event-day raster, mask to region + threshold,
   **vectorize the above-threshold cells into a (Multi)Polygon**, and derive `footprint_area_km2`
   (equal-area), polygon `centroid`, `bbox`, `n_footprint_parts`, `peak`, `valid_time`, `intensity_field_ref`.
3. Assemble canonical `Event` rows (a GeoDataFrame).
4. **NOAA cross-check** — spatiotemporal match (±1 day, in-region) → `confidence_flags`; report the
   undercount (MRMS hail-days vs NOAA-reported days) and a MESH-vs-report size sanity check (MESH
   over-forecasts by design — [`learning_logs/01`](../../learning_logs/01_extending_a_short_hazard_record.md)).
5. Build the `CatalogManifest`; **persist** as **GeoParquet + GeoJSON** + manifest JSON → `data/hail/`.

## Stated window & deferred (no silent caps — `notebook_work`)

- **Window:** Apr–Jun 2024 (one peak season; MRMS-on-AWS spans ~2020-10→present). **Excluded:** the rest of
  the record. **Widening path:** extend the MRMS scan window and re-run (cache makes it incremental).
- **`λ` / NegBin fit is deferred:** a 3-month peak-season window cannot yield an unbiased annual λ — so
  `annual_rate` is left unset at v1 and the manifest records `frequency_process=negative_binomial` with
  `status=deferred` until the full multi-year region scan lands (A24 §4.3 already flags the test is
  underpowered even at ~16 yr). The catalog **machinery and schema** are the v1 deliverable; the fitted λ
  follows the widened record.
- **Also deferred:** **dilation / morphological-close** to consolidate the speckled above-threshold cells
  into coherent swaths (raw footprints are patchy — `n_footprint_parts` runs high, e.g. ~110 on the biggest
  day; the geometry is faithful, just not yet smoothed — H10's dilation step); connected-component
  swath-splitting (one event per consolidated swath); sub-daily declustering; the long-record
  calibrated-splice / gridded-extension ([`learning_logs/01`](../../learning_logs/01_extending_a_short_hazard_record.md)).

**Carried forward to M1→M2 (coupling):** each event carries `footprint_area_km2` (the `F` for Minkowski) and
`peak_intensity_in` (for conditional severity).
