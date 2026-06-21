# Cell Documentation Crosswalk — Hail × Solar under v1.4 Framework

This file maps the global v1.4 documentation standard to the current hail × solar cell package.

The hail × solar curve content remains the v1.3 derivation-audit version. The v1.4 package adds a stronger global framework and this crosswalk; it does not change the curve parameters.

## Current cell files

```text
README_hail_solar_v1_3.md
hail_solar_curve_derivation_dossier_v1_3.md
damage_code_metadata_spec_hail_solar_v1_3.md
damage_curve_method_guide_v1_3_hail_solar_consolidated.md
damage_curve_records_v1_3_hail_solar_derivation_audit.xlsx
```

## Crosswalk

| v1.4 required item | Where it lives in hail × solar current package |
|---|---|
| Cell identity | `README_hail_solar_v1_3.md` |
| Snapshot tree | `README_hail_solar_v1_3.md`; workbook `Hail_Solar_Coverage` |
| Primary nonzero failure-unit | `README_hail_solar_v1_3.md`; `damage_code_metadata_spec_hail_solar_v1_3.md` |
| Conditioner-only equipment | `README_hail_solar_v1_3.md`; workbook `Selector_Conditioner_Map` |
| Reviewed secondary / DR≈0 buckets | workbook `Hail_Solar_Coverage` |
| X-axis decision | `hail_solar_curve_derivation_dossier_v1_3.md`; workbook `X_Axis_Map`, `Axis_Bridges` |
| Curve-form rationale | `hail_solar_curve_derivation_dossier_v1_3.md`; workbook `Hail_Base_Curve_Fit` |
| Source-to-parameter mapping | workbook `Hail_Evidence_Params`; dossier evidence section |
| Parameter derivation | dossier derivation section; workbook `Hail_Base_Curve_Fit` |
| Selector rules | `damage_code_metadata_spec_hail_solar_v1_3.md`; workbook `Hail_Variant_Catalog` |
| Conditioner rules | `damage_code_metadata_spec_hail_solar_v1_3.md`; workbook `Hail_Adjustment_Rules` |
| Exposure/value scaling | workbook `Value_Link`, `Hail_Site_Loss`, `Hail_Sensitivity` |
| Assumption register | workbook `Hail_Assumption_Register` |
| Open seams | workbook `Open_Seams_Index`; dossier open seams section |
| Damage-code interface | `damage_code_metadata_spec_hail_solar_v1_3.md` |

## The hail × solar snapshot to preserve

```text
hail × solar v1.3
├─ primary nonzero failure-unit
│  └─ PV_ARRAY / PV_MODULE / glass-cell replacement trigger
│
├─ conditioner-only equipment
│  └─ MOUNTING / TRACKER, because tracker stow changes module exposure
│
├─ reviewed secondary / low-materiality equipment
│  └─ SCADA / MET_STATION, exposed instruments
│
└─ DR≈0 direct-hail buckets in v1
   ├─ INVERTER_SYSTEM
   ├─ SUBSTATION
   ├─ CIVIL_INFRA
   ├─ FOUNDATION
   └─ SITE_DRAINAGE
```

## Notes for future cleanup

If the hail × solar cell is revised again, the next cell version should copy the v1.4 standard sections directly into the README and derivation dossier rather than relying on this crosswalk.
