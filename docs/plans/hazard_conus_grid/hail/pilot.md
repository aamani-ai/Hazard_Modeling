# Hail — Selected-Cell Pilot

The pilot is a small proving run for the full CONUS hail grid. It is not a separate product, not a shortcut,
and not the final model. Its job is to verify the data contract before full fanout.

## Why the Pilot Exists

MRMS is large and raw. The final computation is not conceptually hard, but several upstream choices are easy
to get subtly wrong:

- daily MESH file interpretation;
- severe-hail thresholding (`>= 25.4 mm`);
- native pixel to benchmark `cell_id` aggregation;
- whether a hail-day count means what we think it means;
- how to store observed size samples per cell;
- sparse-cell behavior;
- QA against Storm Events and known hail regimes.

If these are wrong, a full-CONUS run only produces a bigger wrong artifact. The pilot gives us a small,
inspectable artifact with the exact same schema the full run will use.

## Pilot Cell Selection

Use a small set of representative 0.25° cells. The selected-cell manifest is now pinned for the M1 pilot and
documented in [`pilot_cell_selection.md`](pilot_cell_selection.md):

```text
data/hazard_conus_grid/hail/selected_pilot_cells_v2026_06_16.csv
```

This is a pilot lock only, not a production hail climatology.

| Cell type | Purpose | Acceptable selection basis |
|---|---|---|
| High-hail cell | Stress test frequent severe hail and size distribution. | MRMS exploratory counts and/or documented hail climatology in a known high-hail corridor. |
| Medium-hail cell | Check normal body behavior. | MRMS exploratory counts and/or climatology showing non-extreme but non-sparse hail. |
| Low-hail cell | Check sparse-cell flags and zero/near-zero handling. | MRMS exploratory counts and/or climatology showing a low-hail regime, with no-data clearly ruled out. |
| Hayhurst/reference cell | Bridge to the completed hail × solar deep asset work. | Benchmark-grid polygon containment or nearest-cell assignment from the documented Hayhurst coordinates. |

The detailed selection protocol is [`pilot_cell_selection.md`](pilot_cell_selection.md). The selected-cell
manifest lives under:

```text
data/hazard_conus_grid/hail/
```

The selected manifest includes the selection source, source window, metric used, join proof to the served
CONUS mask, and a note explaining why each cell is useful for the pilot.

Do **not** use unexplained legacy risk-output deliveries as the basis for pilot-cell selection. The hail M1
truth source is MRMS daily MESH first, with MYRORSS and tail/climatology work added later.

## Minimum MRMS-Only Flow

```text
MRMS daily MESH
  -> threshold >= 25.4 mm
  -> aggregate native ~1 km pixels to benchmark 0.25° cell_id
  -> sparse positive daily cell evidence table
  -> complete selected-cell x date panel with explicit zero-severe days
  -> hail-day counts and observed MESH sizes
  -> initial per-cell frequency and size summaries
  -> QA plots/tables
```

Current status: this MRMS-only selected-cell flow has produced the first tiny M1 pilot layer:

```text
data/hazard_conus_grid/hail/m1_selected_cell_daily_panel_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.csv
data/hazard_conus_grid/hail/m1_selected_cell_hazard_layer_v2026_06_16.json
```

The layer is intentionally small and bounded to 2024-04-01 through 2024-06-30. It proves the daily-panel and
summary-layer contract; it does not prove final hail climatology.

Current downstream status: the selected-cell hail x canonical-solar M2-M4 smoke test has also run:

```text
data/hazard_conus_grid/hail/solar/m2_solar_smoke_event_set_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/m4_solar_smoke_risk_metrics_v2026_06_16.json
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.csv
data/hazard_conus_grid/hail/solar/hayhurst_reference_bridge_v2026_06_16.json
```

This proves that the pilot M1 output can drive the final metric families. It does not make those metric values
reportable, because the M1 layer is still a bounded-window, raw-MRMS pilot.

The Hayhurst reference bridge status is `pass_for_interface_bridge_not_calibration`: differences versus the
deep Hayhurst asset run are explainable, but this is not a calibration claim.

## Future Source Additions

Additional sources are staged after the MRMS contract is readable and defensible:

| Source | When added | Why |
|---|---|---|
| MYRORSS | Next M0 source notebook | Longer-record gridded evidence using the same daily cell contract. |
| NOAA Storm Events / SPC | Validation/calibration | Report-side support and later calibration, not raw grid truth. |
| Murillo & Homeyer / climatology research | M1 validation/de-biasing | Broad spatial pattern and raw-MESH bias checks. |
| Das & Allen / EVT tail work | Before final high-return metrics | Size-tail modeling for PML/TVaR-style readouts. |
| FEMA NRI | Downstream QA | Coarse reasonableness check only. |

## Pilot Output Contract

The pilot should produce a tiny version of the M1 hazard layer with at least:

- `hazard = hail`;
- `cell_id`;
- `date`;
- `n_native_pixels_observed`;
- `n_native_pixels_severe`;
- `severe_area_km2` or equivalent;
- `mesh_max_mm`;
- `mesh_p50_mm`, `mesh_p90_mm`, `mesh_p95_mm`, where meaningful;
- `hail_day_flag`;
- `source_product`;
- `source_timestamp`;
- QA flags.

The fitted/summary layer should then expose:

- `lambda_cell`;
- `freq_dist`;
- `fano_phi` or sparse-cell fallback flag;
- empirical MESH size distribution summary;
- `n_hail_days`;
- `record_span`;
- `sparse_cell_flag`;
- provenance and QA flags.

## Success Criteria

- The selected cells join cleanly to benchmark `cell_id`.
- High/medium/low cells behave in the expected order, based on the selection evidence.
- Hayhurst/reference behavior is directionally consistent with the deep hail × solar work.
- No-data and zero-risk are distinct.
- The tiny M1 artifact can drive one solar M2-M4 risk-metrics run. **Status: done for selected-cell smoke
  test; not reportable.**
- The Hayhurst bridge explains grid-smoke versus deep-asset differences without claiming calibration.

## Non-Goals

- Full CONUS processing.
- MYRORSS extension.
- EVT tail fitting.
- Final reportable PML500/TVaR99.
- Production orchestration.

Those come after the pilot proves the shape.
