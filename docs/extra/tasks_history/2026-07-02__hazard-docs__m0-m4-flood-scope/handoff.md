# Handoff — hazard docs improved; flood x wind-farm scope issue found (2026-07-02)

## 60-second summary
- We improved the hazard documentation so M0-M4 is easier to understand hazard-by-hazard and layer-by-layer.
- The docs now separate **source selection** from **modeling choices**.
- The M0-M4 contract now explains event-first, return-period/surface-first, and hybrid M0/M1 modes.
- Notebook README files are being upgraded from link indexes into method explanations with ASCII diagrams and "what this
  layer asks" blocks.
- Flood got the deepest treatment: riverine, pluvial, coastal, solar polygon coupling, and wind-farm node coupling.
- Solar flood V1 now documents the representative value-mix assumption: wet area fraction proxies wet value fraction.
- Inland flood combine is documented as worse-source-wins / max for overlapping equipment, not naive addition.
- The wind-farm collector/substation hull method is valuable, but now correctly framed as exposure/dependency mapping.
- Big unresolved issue: flood x wind-farm physical loss should not automatically include a mapped collector substation.
- Next chat should start by deciding flood x wind-farm product scope before touching M3/M4 code.

## Files to read first next session
1. `docs/hazards/flood/modeling_choices.md`
2. `docs/hazards/flood/fundamentals_before_m0.md`
3. `Notebooks/flood/wind_farm/m3_damage/01_damage.py`
4. `Notebooks/flood/wind_farm/m4_loss_metrics/01_loss_metrics.py`
5. `damage_modeling/docs/damage_curves/damage_curve_implementation/solar_wind_value_breakdown.xlsx`
6. `docs/hazards/m0_m4_event_loss_contract.md`
7. `docs/hazards/README.md`

## Primary next action
Decide the flood x wind-farm boundary:

```text
Option A — physical-only baseline
  price only turbine-owned physical components and owned collection/civil items with evidence
  exclude mapped standalone collector/substation unless ownership/TIV is confirmed

Option B — physical baseline + sensitivity
  baseline excludes uncertain collector
  sensitivity includes owned-collector assumption with explicit value weight and caveat

Option C — dependency/disruption product
  use collector/substation flood depth to model outage/downtime/revenue interruption
  keep this separate from M3 physical damage
```

Do not continue with the current `substation = 0.09 of TIV` physical-loss assumption as baseline unless the asset value
schedule proves it.

## Why this matters
The current flood wind-farm M3/M4 notebook logic can make the collector dominate physical loss. That is only defensible
if the collector is owned by the project and included in the physical replacement-cost/TIV basis. If the node is a POI,
utility substation, or grid dependency, flood exposure is still important, but it belongs in disruption/outage modeling.

## Evidence found
The local value-breakdown workbook has a wind row:

```text
ELECTRICAL_COLLECTION + SUBSTATION
72 $/kW
physical_share ~= 4.4%
source note: CWER does not split collection vs substation; row is a plant electrical rollup
```

That does not support a clean standalone `substation = 0.09` wind-farm physical-loss bucket.

## Current risky code paths
```text
Notebooks/flood/wind_farm/m3_damage/01_damage.py
  CAPEX includes "substation": 0.09
  substation_loss_frac(depth_ft) prices it directly as farm TIV physical loss

Notebooks/flood/wind_farm/m4_loss_metrics/01_loss_metrics.py
  CAPEX7 includes "substation": 0.09
  surge/wind compound max operates over that same split
```

## Repro / inspection commands
```bash
git status -sb
rg -n -i "substation|collector|CAPEX7|substation_loss_frac|ELECTRICAL_COLLECTION" \
  Notebooks/flood/wind_farm docs/hazards/flood damage_modeling

unzip -p damage_modeling/docs/damage_curves/damage_curve_implementation/solar_wind_value_breakdown.xlsx \
  xl/worksheets/sheet6.xml | rg -i "ELECTRICAL_COLLECTION|SUBSTATION|CWER does not split"
```

## What to avoid
- Do not treat USWTDB turbine-cloud hulls as official project boundaries.
- Do not treat OSM/HIFLD substation mapping as ownership proof.
- Do not mix disruption/outage loss into M3 physical damage.
- Do not push code/data changes from the dirty worktree unless they are intentionally scoped.

## Good changes worth preserving
- The ASCII diagrams and layer-question blocks are useful and should be propagated to other notebook README files.
- The M0/M1 input-mode discussion is important for every hazard that uses return-period surfaces or official simulated
  outputs instead of raw event catalogs.
- The source-selection/modeling-choice split is the right doc structure.
- The flood solar representative value-mix caveat is now clear and should remain.
