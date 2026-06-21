# Workbook Sheet Manifest Template

Use this template to document what each workbook sheet does.

| Sheet | Required? | Purpose | Key columns / outputs | Reviewer question answered |
|---|---|---|---|---|
| `README_SHORT` | yes | workbook navigation | scope, version, read order | What is this workbook? |
| `Cell_Index` | yes | cell identity and status | cell_id, hazard, asset, maturity | What cell is modeled? |
| `Curve_Records` | yes | one row per failure-unit curve | curve_id, failure_unit, x_axis, y_axis | What curves exist? |
| `Value_Link` | yes | maps curves to value buckets | subsystem, component, basis, f_kind | What dollars does DR apply to? |
| `X_Axis_Map` | yes | hazard x-axis definitions | x_axis_id, units, bridge | What intensity variable is used? |
| `Evidence_Log` | yes | source inventory | source_id, link, supports | Which evidence supports the curve? |
| `<Cell>_Base_Curve_Fit` | yes for derived cells | curve math and anchors | anchors, D50, k, formula | How was the curve fitted? |
| `<Cell>_Adjustment_Rules` | conditional | selector/conditioner transformations | variable, type, effect | How are variants produced? |
| `<Cell>_Variant_Catalog` | conditional | curve variants | variant_id, parameters | Which curves can be selected? |
| `<Cell>_Assumption_Register` | yes | assumptions and update triggers | assumption_id, affects, confidence | What is assumed? |
| `QA_Checks` | yes | model checks | check, status, notes | Is the package reviewable? |
| `Dashboard` | optional | visual summary | charts | What does the curve look like? |
