# discussion/hurricane/

**Where we pressure-test hurricane source choices before the branch lands on main.** Hurricane is built on the
`hurricane` branch; main carries a preview anchor and source-selection page so the cross-hazard picture is visible.

The hurricane hazard here is **tropical-cyclone wind**. Surge and rainfall are real tropical-cyclone damage agents,
but they are owned by flood and joined by `event_family_id`.

## Read Order

| # | Doc | What it decides |
|---|---|---|
| 01 | [`01_source_selection_pressure_test.md`](01_source_selection_pressure_test.md) | Why V1 uses RAFT for storm-resolved severity, HURDAT2 for observed frequency, ASCE for tail validation, and routes surge/rain to flood. |

## Related

- Main hazard source page: [`../../../hazards/hurricane/source_selection.md`](../../../hazards/hurricane/source_selection.md).
- Main hurricane anchor: [`../../../hazards/hurricane/README.md`](../../../hazards/hurricane/README.md).
- Hurricane branch notebooks: <https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/Notebooks/hurricane>
- Hurricane branch plans: <https://github.com/aamani-ai/Hazard_Modeling/tree/hurricane/docs/plans/hurricane>

## Status

Branch-preview discussion. Promote concise decisions to `docs/hazards/hurricane/source_selection.md`; keep detailed
tradeoffs here until the branch lands and the plan/register paths are local on main.
