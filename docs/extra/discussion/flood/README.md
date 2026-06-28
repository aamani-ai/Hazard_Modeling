# discussion/flood/

**Where we pressure-test flood source choices before the branch lands on main.** Flood is already built on the
`flood` branch, but main needs a compact reasoning layer explaining why each sub-peril uses its chosen data source.

Flood is one peril with three sub-perils:

```text
riverine [R]  -> river/network overflow
pluvial  [F]  -> intense-rainfall ponding / flash flooding
coastal  [C]  -> storm-surge inundation
```

They share one damage driver, **inundation depth at the asset**, but they do not share one source.

## Read Order

| # | Doc | What it decides |
|---|---|---|
| 01 | [`01_source_selection_pressure_test.md`](01_source_selection_pressure_test.md) | Which public data source is the V1 spine for riverine, pluvial, and coastal flood; what is only support/validation; what caveats must stay visible in the hazard docs. |

## Related

- Main hazard source page: [`../../../hazards/flood/source_selection.md`](../../../hazards/flood/source_selection.md).
- Main flood anchor: [`../../../hazards/flood/README.md`](../../../hazards/flood/README.md).
- Flood branch notebooks: <https://github.com/aamani-ai/Hazard_Modeling/tree/flood/Notebooks/flood>
- Flood branch plans: <https://github.com/aamani-ai/Hazard_Modeling/tree/flood/docs/plans/flood>

## Status

Branch-preview discussion. Promote concise decisions to `docs/hazards/flood/source_selection.md`; leave detailed
reasoning here until the branch lands and the plan/register paths are local on main.
