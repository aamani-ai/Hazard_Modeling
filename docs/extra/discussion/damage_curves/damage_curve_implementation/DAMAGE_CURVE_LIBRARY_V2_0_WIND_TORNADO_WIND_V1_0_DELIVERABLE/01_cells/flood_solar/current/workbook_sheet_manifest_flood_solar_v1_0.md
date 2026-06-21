# Workbook Sheet Manifest — Flood × Solar v1.0

Workbook: `damage_curve_records_v1_0_flood_solar.xlsx`

| Sheet | Purpose |
|---|---|
| `README_SHORT` | Workbook scope, navigation, and caveats. |
| `Cell_Snapshot` | ASCII-style identity snapshot of the cell. |
| `Flood_Coverage` | Failure-unit coverage map: primary, secondary, modifiers, DR≈0. |
| `Flood_X_Axis_Decision` | Accepted/rejected x-axis decisions and formulas. |
| `Flood_Evidence_Params` | Source-to-parameter mapping. |
| `Flood_Base_Curve_Fit` | Curve form, anchor ordinates, and v1.0 parameter values. |
| `Flood_Adjustment_Rules` | New curve vs shift vs selector vs conditioner vs exposure multiplier. |
| `Flood_Variant_Catalog` | How equipment variants map to current/future curve treatment. |
| `Flood_Assumption_Register` | Load-bearing assumptions, materiality, and update triggers. |
| `Damage_Code_Interface` | Required hazard inputs, metadata, and outputs. |
| `Value_Link` | Failure-unit to value-bucket map. |
| `Site_Inputs` | Default illustrative site/asset assumptions. |
| `Flood_Curve_Data` | Curve data table used for plotting. |
| `Site_Applied_Loss` | Illustrative site flood depth → local DR → loss ladder. |
| `Flood_Dashboard` | Charts and KPI view for review. |
| `Flood_QA` | Governance and QA checks. |
| `Sources` | Raw source URLs and use notes. |

## Notes

- The workbook is a damage-record artifact, not a full financial model.
- `Site_Applied_Loss` and `Flood_Dashboard` are illustrative to verify the value linkage and scaling.
- The damage-code output of interest is the per-failure-unit DR.
- The source of truth for detailed derivation logic is `flood_solar_curve_derivation_dossier_v1_0.md`.
