# START HERE — Damage Curve Library v2.0

This package contains the current damage-curve library framework plus three worked cells. **v2.0 adds the derived wind/tornado × wind farm v1.0 cell**.

```text
01_cells/
├─ hail_solar/           current: v1.3 derivation-audit cell
├─ flood_solar/          current: v1.0 derived multi-failure-unit cell
└─ wind_tornado_wind/    current: v1.0 derived repeated-unit structural cell
```

## Recommended read order

```text
1. 00_global_method/00_index.md
2. 00_global_method/13_end_to_end_damage_work_architecture.md
3. 00_global_method/14_coverage_role_taxonomy.md
4. 00_global_method/15_wind_tornado_wind_reference_pattern.md
5. 01_cells/wind_tornado_wind/current/README_wind_tornado_wind_v1_0.md
6. 01_cells/wind_tornado_wind/current/wind_tornado_wind_curve_derivation_dossier_v1_0.md
7. 01_cells/wind_tornado_wind/current/wind_tornado_wind_damage_code_metadata_spec_v1_0.md
8. 01_cells/wind_tornado_wind/current/damage_curve_records_v1_0_wind_tornado_wind.xlsx
```

## What is new in v2.0

```text
Added wind/tornado × wind v1.0 derived curves:
    blade structural damage
    tower buckling/collapse
    nacelle direct/consequential damage
    foundation overturning/support failure
    power electronics acceleration-sensitive open seam

Derived x-axis and curve logic:
    hub-height 3-second gust for straight-line/severe wind
    EF-scale 3-second gust proxy bridge for tornado/direct-hit
    design-normalized speed ratio r = V_3s_hub / Ve50_class
    bounded logistic fragility-style structural curves

Documentation additions:
    derivation dossier with evidence-to-parameter mapping
    curve form rationale and rejected alternatives
    adjustment rules for IEC class selector, tornado direct-hit shift,
    feather/yaw/brake conditioners, and exposed turbine fraction
```

## Existing current cells

```text
hail_solar v1.3
    single-primary failure-unit
    PV module hail damage
    MESH-equivalent hail diameter axis

flood_solar v1.0
    multi-failure-unit cell
    local water depth above component datum
    piecewise/state electrical inundation curves
```

## Key reminder

The purpose of this library is not to own EAL, PML, or portfolio metrics. It defines the right **damage-code granularity**, x-axis, curve form, metadata, coverage roles, source evidence, and value linkage so downstream hazard and financial systems can compute those metrics correctly.

## Source context note

The raw foundation discussions are included under:

```text
99_source_context/damage_curve_foundations/
```

These are the original assembled-record and question docs behind the global method standards.
