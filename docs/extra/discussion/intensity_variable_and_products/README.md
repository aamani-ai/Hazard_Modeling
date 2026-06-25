# discussion/intensity_variable_and_products/

**One hazard's intensity becomes a *different* variable in the catalog, in the damage curve, and in a
parametric product — and that's not sloppiness, it's structure.** This folder works out *why* the hazard
intensity variable `X` is **product-dependent** rather than agnostic, what reconciles the versions when they
diverge, and where a **parametric trigger** — a new kind of hazard consumer we haven't modeled before — fits
in the platform.

It started from a real confusion: looking across the versions, the same peril seemed to use one variable in
the event catalog (M0/M1), another in the damage curve (M3 / `damage_modeling`), and yet another in a
parametric insurance product (the Descartes solar-SCS reference). Is `X` something you pick **once per
hazard**, or **once per product**? This folder's answer: once per *product*, but principled — every consumer
reads off **one shared causal chain** and pins `X` at the node its own binding constraint forces.

> **This is a discussion, not a plan-of-record.** It reasons toward (a) a **learning log** entry that
> crystallizes the transferable lesson and (b) a decision on whether the **parametric product** becomes a
> tracked scope item. The canonical treatment of *how a damage curve picks its x-axis* already lives in
> `damage_modeling` (foundations `02` + standard `04`); we **link** it, we don't duplicate it.

## Read order

| # | Doc | What it works out |
|---|---|---|
| 01 | [`01_one_chain_many_products.md`](01_one_chain_many_products.md) | **The frame.** One causal chain; three consumers (catalog · damage curve · parametric trigger) each pin `X` at a different node under a different constraint; the two coordinates **Q-x2a (which quantity)** vs **Q-x2b (which node)**; the six-peril contrast panel; and **basis risk = the node-gap** (which is why a parametric product is a *hedge*, not a *replacement*). Grounded, with the `[GROUNDED]` / `[ILLUSTRATIVE]` / `[OURS]` split made explicit. |
| 02 | [`02_parametric_consumer_and_open_questions.md`](02_parametric_consumer_and_open_questions.md) | **The parametric trigger as a *new consumer*** — where it sits in the platform (it is a risk-transfer/product surface, deliberately *out* of `damage_modeling`'s scope), the hedge-vs-replacement reframe, the Drive-first path if it graduates to a real product, and the open decisions. |

## Status

🟡 **Open for discussion.** The frame (01) is grounded and adversarially verified across six perils
(hail, convective wind, wildfire, flood — built; ice, hurricane — forward). The crystallized lesson has
graduated to [`learning_logs/13`](../../../learning_logs/13_one_chain_many_products.md). What remains open is
**02**: whether the parametric product becomes a tracked scope item (it touches risk-transfer, not just
hazard), and if so its Drive-doc home. Awaiting the owner's read.

## Related (don't duplicate — link)

- **Canonical x-axis method** (the damage-side rule this builds on): `damage_modeling` foundations
  [`02_x_axis_intensity_variable`](../../../../damage_modeling/docs/damage_curves/damage_curve_foundations/questions/02_x_axis_intensity_variable.md)
  (the parsimony + chain-position rules) and global standard
  [`04_x_axis_decision_standard`](../../../../damage_modeling/docs/damage_curves/damage_curve_implementation/) (the chain-position table + native-axis-vs-physics-bridge).
- **The crystallized lesson:** [`learning_logs/13`](../../../learning_logs/13_one_chain_many_products.md);
  its sibling [`learning_logs/07`](../../../learning_logs/07_one_simulation_two_products.md) (one simulation,
  two products) is the same *shape* one layer over (one source object, multiple non-interchangeable consumers).
- **The hero peril's discussion:** [`../convective_wind/`](../convective_wind/README.md) (where the 3-s-gust
  reconciliation across ASCE/EF/NWS/IEC was settled — `DD-WN-6`, `AWN-5`, `AWN-15`).
- **The principles every choice here serves:** [`../../../principles/`](../../../principles/README.md)
  (*standard interface, not standard physics* governs this whole topic).
