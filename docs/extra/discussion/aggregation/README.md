# discussion/aggregation/

**Where we think out loud about loss aggregation, event families, dependence, and double-counting across
sub-perils, perils, assets, and portfolios.** This is deliberately cross-cutting: the problem first became
visible in convective wind, but it is not a wind problem. It is a platform problem.

Nothing here is code or a plan-of-record. This folder exists to settle the reasoning before it graduates to
`docs/plans/` and, eventually, the shared M4 / Overall Risk machinery.

## Why this folder exists

The same question keeps reappearing under different names:

- tornado + strong wind inside convective wind;
- hurricane wind + storm surge + rainfall + TC-spawned tornadoes;
- hail + wind inside one severe-convective outbreak;
- wildfire flame damage + smoke/outage/disruption;
- heat + drought derating;
- one storm or fire hitting several assets in a portfolio.

Those are not all the same modeling problem, but they share one rule: **do not aggregate metrics before you
have built the right event-year loss object.** EAL, VaR, PML, TVaR, AEP, OEP, caps, and `max(...)` each live at a
specific stage. Applying the right operator at the wrong stage is how a plausible number becomes a false one.

## Read order

| # | Doc | What it decides |
|---|---|---|
| 00 | [`00_overview.md`](00_overview.md) | The map: why aggregation has two separate questions, what belongs in each file, and the platform-level rule of thumb. |
| 01 | [`01_double_counting_and_event_identity.md`](01_double_counting_and_event_identity.md) | Source/event hygiene: same physical parent event, same damaged value, partitioning, `event_family_id`, component caps, and when `max(A,B,C)` can be a de-dup rule for overlapping perils. |
| 02 | [`02_metric_operators_and_joint_distributions.md`](02_metric_operators_and_joint_distributions.md) | Metric math after event identity is clean: `sum`, `max`, caps, EAL, VaR/PML/TVaR, AEP/OEP, joint annual vectors, dependence, and stress/dashboard caveats. |

## Related - do not duplicate

- The wind-specific seed case: [`../convective_wind/04_aggregation_and_double_counting.md`](../convective_wind/04_aggregation_and_double_counting.md).
- Damage-curve scope edges: [`../damage_curves/04_portfolio_extension.md`](../damage_curves/04_portfolio_extension.md) and [`../damage_curves/06_financial_terms_and_scope_edges.md`](../damage_curves/06_financial_terms_and_scope_edges.md).
- The source-of-truth Drive references: [`../../../google_drive_docs/README.md`](../../../google_drive_docs/README.md), especially `hazard_asset_loss_distribution_methodology` and `risk_metrics_reference`.
- The principle that makes this non-negotiable: [`../../../principles/basics_spot_on.md`](../../../principles/basics_spot_on.md).

## Status

🟡 **Open for discussion.** Seeded from the Drive methodology, the Risk Metrics Reference, the convective-wind M4
discussion, and the damage-curve scope discussions. The first graduation target is a common M4 aggregation
contract: `event_id`, `event_family_id`, loss basis, event loss, annual AEP/OEP vectors, and clear rules for
sub-peril / peril / portfolio combination.
