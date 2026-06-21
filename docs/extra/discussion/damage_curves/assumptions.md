# Damage-curve discussion — assumptions register (draft)

The `DC*` assumptions this discussion takes as given while the open calls (`01`–`07`) are argued. The analogue
of the [conus_grid `G*` register](../conus_grid/assumptions.md), but for the **damage-curve layer**. An
assumption here is an input/simplification we hold fixed to make the discussion tractable; per-peril curve
assumptions (the actual `A*` / `DD-*` ids) live in each peril's register and are linked, not duplicated.

**Status:** 🟡 draft (discussion). **Legend:** `decided` · `assumed` · `deferred` · `cleanup` (a known
inconsistency to fix).

---

## Settled frame (graduated from `00`)

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **DC1** | Damage curve = **physical destruction only** (repair cost ÷ replacement value). | Terminology §5 / Methodology §6; disruption/BI is a separate additive stage (§7 + §9). | decided | — |
| **DC2** | **Subsystem-decomposed, capex-weighted logistic blend** `Asset_DR = Σ wᵢ·DRᵢ`. | Fixes the old one-curve-per-(hazard×asset) failure; all 3 cells + library. | decided | — |
| **DC3** | **Saturation, no extrapolation**; anchoring applied **selectively** (only where a raw floor `DR(0) > 0` exists). | hail A16 (no anchor); wildfire DD-W8, wind DD-WN-11 (anchored). | decided | — |
| **DC4** | **v1 representation = scalar mean DR.** | All 3 cells; explicitly temporary. | assumed (temporary) | resolved in [`01`](01_emit_object.md) |
| **DC5** | **Scope = single-site · damage-track · occurrence-basis · current-climate.** | The v1 box (`00 §1`). | assumed | the relevant extension doc (`04` / `06`) closes |

## Open — owned by a sub-doc (no `DC` row until decided)

The open calls deliberately have **no** assumption row yet — they graduate here (or to `docs/plans/`) once
closed: emit object ([`01`](01_emit_object.md) / Q1, Q5) · metrics under scalar ([`02`](02_metrics_and_tail_honesty.md) / Q2) ·
value-allocation & TIV ([`03`](03_value_allocation_and_tiv.md) / Q4) · portfolio ([`04`](04_portfolio_extension.md) / Q3) ·
cascade ([`05`](05_aggregation_dependence.md) / Q6) · financial terms & disruption boundary ([`06`](06_financial_terms_and_scope_edges.md) / Q7) ·
component depth ([`07`](07_component_attribute_depth.md) / Q8).

## Cleanup (documentation hygiene, surfaced by the consolidation)

| # | Item | Where | Action |
|---|---|---|---|
| **DC-c1** | Hail "immune-share" wording is inconsistent — the notebook mixes **~36 %** and **~64 %**, while the weights imply cap **34 %**, modelled **42 %**, immune **58 %** (four different quantities). | hail M3 notebook §2 / findings + [hail A15](../../../plans/hail/assumptions.md) | reconcile to one clear statement, checked against the curve spec JSON (`data/hail/damage_curves/…json`). |
| **DC-c2** | A `0.3416` max-DR "known-answer" is referenced in a handoff but **not present** in the hail M3 notebook. | hail handoff vs M3 notebook | source it or drop it; don't cite an unverified known-answer. |

---

*How to use this: when a sub-doc closes a decision, add its `DC` row here (status `decided`) and, if it
affects a build, mirror it into the peril's `A*` / `DD-*` register. The `cleanup` rows should be cleared as
small standalone fixes.*
