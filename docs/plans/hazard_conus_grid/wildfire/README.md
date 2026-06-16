# Hazard CONUS Grid — Wildfire

Wildfire is expected to be easier than hail for the first CONUS grid build because FSim/WRC already provides a
pre-integrated hazard field: burn probability and intensity/severity information. The work is mostly source
selection, aggregation, vintage control, and canonical asset coupling.

Read order:

1. [`m0_m1_hazard_layer.md`](m0_m1_hazard_layer.md).
2. Existing plan: [`docs/plans/wildfire/`](../../wildfire/).
3. Discussion source: [`docs/extra/discussion/wildfire/`](../../../extra/discussion/wildfire/).
4. Historical/cautionary context: [`_legacy_wildfire/`](../../../../_legacy_wildfire/) only after validating
   any specific assumption in this repo.
5. Principles: [`docs/principles/README.md`](../../../principles/README.md).

## Intended Notebook Root

```text
Notebooks/hazard_conus_grid/wildfire/
  m0_input_data/
  m1_hazard_layer/
  solar/
    m2_m4_risk_metrics/
  wind/
    m2_m4_risk_metrics/
```
