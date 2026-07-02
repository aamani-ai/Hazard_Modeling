# Notes — implementation detail, verification, and key insights (2026-07-02)

## Summary
This session was mostly documentation and modeling-clarity work. The central theme was making the repo explain the
bridge from raw hazard evidence to M0-M4 financial metrics in a way the team can audit later.

The discussion started with convective wind return-period curves and event statistics, moved into general M0/M1 input
modes, then focused deeply on flood: riverine BLE + USGS flow-frequency densification, pluvial rainfall/terrain logic,
coastal surge physics, solar polygon coupling, and wind-farm node coupling.

The major unresolved finding is the flood x wind-farm scope issue: collector/substation mapping is useful, but physical
damage should not include that node unless it is owned and included in TIV. Otherwise it belongs in dependency /
disruption loss.

## Important explanations added
- M0 reads hazard evidence; M1 builds event/frequency/severity representation; M2 couples the hazard to the asset; M3
  maps intensity to damage; M4 simulates annual loss and metrics.
- Convective strong wind can use ASCE return-period gust curves to build event count and severity distributions when a
  raw catalog is not the best base.
- Riverine flood uses BLE 100/500-year depth anchors plus 10-year wet/dry extent and USGS `Q(T)` flow-frequency
  information to densify missing 10/25/50-year depths.
- `Q(T)` = discharge / flow at return period `T`; `D(T)` = flood depth at return period `T`.
- M2 for solar asks: which raster pixels in the polygon are wet, how many are wet, what is the average wet depth, and
  what is the max depth.
- M2 for wind farms is node-based: each turbine pad and candidate collector/dependency node reads its own water depth.
- Coastal flood feels like riverine because both become water surface elevation minus ground elevation at M2, but their
  physics and event clocks differ.

## Commands and checks used
Representative commands from the session:

```bash
git status -sb
git diff --stat
rg -n "pattern" docs Notebooks
sed -n 'start,endp' path/to/file
nl -ba path/to/file | sed -n 'start,endp'
perl -ne 'print "$ARGV:$.: trailing whitespace\n" if /[ \t]$/; print "$ARGV:$.: tab char\n" if /\t/;' <files>
```

Workbook/source inspection for the wind-farm value issue:

```bash
unzip -l damage_modeling/docs/damage_curves/damage_curve_implementation/solar_wind_value_breakdown.xlsx
unzip -p damage_modeling/docs/damage_curves/damage_curve_implementation/solar_wind_value_breakdown.xlsx xl/workbook.xml
unzip -p damage_modeling/docs/damage_curves/damage_curve_implementation/solar_wind_value_breakdown.xlsx xl/worksheets/sheet6.xml
```

Key workbook observation:

```text
Wind_Map row 12:
  subsystem/component rollup = ELECTRICAL_COLLECTION + SUBSTATION
  value = 72 $/kW
  physical_share ~= 4.4%
  note = public source does not split collection vs substation
```

This conflicts with the flood wind-farm notebook assumption:

```text
substation = 0.09 of farm TIV as a standalone physical-loss node
```

## Files and content to re-check before next changes
- `Notebooks/flood/wind_farm/m3_damage/01_damage.py` currently includes `substation: 0.09` in `CAPEX`.
- `Notebooks/flood/wind_farm/m4_loss_metrics/01_loss_metrics.py` currently uses the same 7-subsystem split for
  compound wind + surge logic.
- `docs/hazards/flood/fundamentals_before_m0.md` now frames collector mapping as dependency/exposure evidence.
- `docs/hazards/flood/modeling_choices.md` now says collector physical loss requires ownership/TIV confirmation.
- `Notebooks/flood/wind_farm/README.md` and `m2_coupling/README.md` now warn that collector mapping is not proof of
  physical-loss ownership.

## Verification performed
- Direct whitespace scans were run on edited flood docs and README files after multiple patches.
- `rg` checks were used to confirm new wording anchors such as `buffered convex hull`, `substation=generation`, and
  `nearest substation to centroid`.
- `git status -sb` confirmed the branch is `main` and aligned with `origin/main` before the final documentation commit
  was prepared.

## Known limitations
- Not all dirty files are part of this task. There are unrelated or broader code/data changes in the worktree.
- The flood x wind-farm notebooks may still contain the provisional collector-as-physical-loss implementation.
- The notebook README documentation is ahead of the final model-scope decision; read the caveats before relying on
  flood wind-farm loss metrics.
- No notebook execution was run as part of this close-out.

## Key insights
1. **A good exposure node is not automatically a physical-damage node.**
   The collector-substation finder is strong, but product scope decides whether it is priced as physical damage,
   disruption, or sensitivity.
2. **Return-period inputs are valid but assumption-heavy.**
   They can be better than raw event catalogs for some hazards, but the conversion bridge must be documented.
3. **README files should teach the method.**
   Cross-reference-only README files are not enough for a notebooks-first modeling repo.
4. **Solar and wind need different flood coupling.**
   Solar is polygon/raster-area dominated. Wind is node/elevation/dependency dominated.
5. **The next chat should start with scope, not code.**
   Changing flood x wind-farm M3/M4 without first deciding physical vs disruption would repeat the same boundary error.
