# Flood × Solar v0.1 Documentation Crosswalk

This file maps the global v1.4 documentation standard to the current flood × solar v0.1 package.

| Standard section | Where it lives in this package | Notes |
|---|---|---|
| Cell package structure | `README_flood_solar_v0_1.md`; workbook `README` sheet | Defines the cell purpose, status, and files. |
| Snapshot tree | `README_flood_solar_v0_1.md`; workbook `Cell_Snapshot` | Shows primary, secondary, protection-only, and DR≈0 buckets. |
| Failure-unit coverage | workbook `Failure_Unit_Coverage`; README section 3 | Reviews all major solar subsystems, not just the primary curves. |
| X-axis decision | `flood_solar_curve_derivation_dossier_v0_1.md`; workbook `X_Axis_Decision` | Depth for electrical ingress; velocity/scour for civil/foundation. |
| Curve derivation proof trail | `flood_solar_curve_derivation_dossier_v0_1.md`; workbook `Evidence_Source_Map` and `Evidence_to_Parameter` | v0.1 maps evidence to future parameters but does not finalize numeric curves. |
| Curve form alternatives | `flood_solar_curve_derivation_dossier_v0_1.md`; workbook `Candidate_Curve_Forms` | Step, smoothed threshold, piecewise, state model, scour curve. |
| Selector / conditioner / exposure | `flood_solar_damage_code_metadata_spec_v0_1.md`; workbook `Selector_Conditioner_Map` and `Exposure_Geometry` | Separates fixed equipment attributes from event-time conditions and elevation geometry. |
| Evidence provenance and links | workbook `Evidence_Source_Map`; dossier section 2 | Each source has a URL and a “supports / does not support” mapping. |
| Damage-code interface | `flood_solar_damage_code_metadata_spec_v0_1.md`; workbook `Damage_Code_Interface` | Defines inputs/outputs by failure-unit. |
| QA / review checklist | workbook `QA_Review_Checklist` | Flags v0.1 as scaffold-ready, not curve-final. |
| Open seams | workbook `Open_Seams`; dossier section 9 | Documents unresolved numeric/metadata issues. |
