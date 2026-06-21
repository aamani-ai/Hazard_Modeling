# Cell Documentation Crosswalk — Flood × Solar v1.0

This crosswalk maps the global documentation standard to the flood × solar v1.0 cell files.

| Global requirement | Where it is satisfied |
|---|---|
| Cell package structure | `README_flood_solar_v1_0.md`; package folder layout. |
| Snapshot tree | `README_flood_solar_v1_0.md`; `Cell_Snapshot` workbook sheet. |
| Failure-unit coverage | `Flood_Coverage` workbook sheet; dossier §4. |
| X-axis decision and rejected alternatives | `Flood_X_Axis_Decision` workbook sheet; dossier §5. |
| Curve derivation proof trail | `flood_solar_curve_derivation_dossier_v1_0.md`; `Flood_Evidence_Params`; `Flood_Base_Curve_Fit`. |
| Curve form alternatives and rationale | Dossier §6; `Flood_Adjustment_Rules`. |
| Source links | `Sources` workbook sheet; dossier §3. |
| Selector / conditioner / exposure mapping | `Damage_Code_Interface`; metadata spec §§3–5. |
| New curve vs adjustment rules | `Flood_Adjustment_Rules`; dossier §10. |
| Value linkage | `Value_Link` workbook sheet. |
| QA / review checklist | `Flood_QA`; dossier §12. |
| Open seams | Dossier §13; `Flood_Assumption_Register`. |

## Framework discipline check

```text
same framework as hail × solar
but not the same physical pattern
```

Hail × solar had one primary failure-unit and material-share concentration. Flood × solar has multiple electrical failure-units and geometry/elevation exposure.
