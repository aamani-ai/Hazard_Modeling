# One Chain, Many Products — Same Intensity Quantity ≠ Same Node, and Basis Risk Lives in the Node-Gap

*A hazard's intensity variable `X` is not picked once per hazard. Every consumer — the event catalog, the
damage curve, a parametric trigger — reads off the **same causal chain** and pins `X` at the node its own
binding constraint forces. They can share a **quantity** (3-s gust) yet sit at different **nodes**; and the
gap between a product's node and the damage node **is** its basis risk.*

**Status:** v1.0 · written 2026-06-21 · **Sourced from:** convective wind × wind farm M0/M1/M3
(`m1_catalog/01_catalog.py`, the `wind_tornado_wind` dossier) + the cross-repo `damage_modeling` x-axis
foundations (`02`, standard `04`) + the Descartes solar-SCS parametric reference · **Applies to:** any peril
read by more than one consumer (catalog · damage curve · parametric trigger), and choosing or critiquing the
hazard intensity variable for any new product. Sibling of [`07`](07_one_simulation_two_products.md) (one
simulation, two products) one layer over, and of [`05`](05_damage_curve_three_coupled_choices.md).

---

## Where this came from

Reading across the versions of the damage/hazard work, one peril seemed to wear three different intensity
variables: one in the **event catalog** (M0/M1), one in the **damage curve** (M3 / a `damage_modeling` cell),
one in a **parametric insurance product** (the Descartes solar-SCS reference). The confusion was concrete: is
`X` chosen **once per hazard** (so it should be the *same* everywhere), or **once per product**? Convective
wind sharpened it — the catalog, the turbine damage curve, and a straight-line-wind parametric trigger all
appeared to use *gust*, yet the numbers and references didn't line up cleanly.

## Why it looked fine — the trap

Two reasonable-sounding beliefs, both wrong:

1. **"One hazard → one intensity variable."** If hail "is about" hail size and wind "is about" gust, surely
   you pick the variable once and reuse it across catalog, damage, and any product. Tidy, and false: it
   conflates *which quantity* with *where on the chain*.
2. **"If two consumers use the same variable, there's no basis risk between them."** Once we realized the
   catalog, damage curve, and parametric trigger for wind all speak **3-s gust**, it was tempting to conclude
   the gap had closed. It hadn't — they speak the same quantity at *different nodes*.

Both are plausible because they're *almost* right: the **quantity** often does converge (especially for
wind). What they miss is the second coordinate — the **node**.

## The lesson

> **The lesson.** `X` is **product-dependent but principled**: every consumer reads off one shared causal
> chain (`hazard source → local intensity → contact intensity → load → damage → $`) and pins `X` at the node
> its binding constraint forces — the catalog at what the **source data emits**, the damage curve at the
> **most-downstream node the data can deliver** (chain-position rule), the parametric trigger at the
> **cheaply-sensed, legally-verifiable** node. Two consumers can share a **quantity** and still differ by
> **node** (Q-x2a vs Q-x2b). **Basis risk = the node-gap** — which is why a parametric product is a *hedge*,
> not a *replacement*. `X` is an **index to analyze against, never a forecast target** — and that is *why* the
> product, not the physics, selects the node.

`[REF]` The damage-side half is canonical in `damage_modeling`: foundations `02` gives the **parsimony rule**
(univariate by default) and the **chain-position rule** (*"put the x-axis at the most-downstream node your
hazard layer can actually deliver as data"*), and standard `04` separates the **operational axis** (what the
data speaks) from the **physics bridge** (what the mechanism responds to), with the `Hazard source / Local /
Contact / Damage-state` chain. `[OURS]` What building added: the *third consumer* (the parametric trigger) sits
on the **same** chain under a **different** constraint, the **same-quantity ≠ same-node** distinction, and
**basis-risk = node-gap = hedge-vs-replacement**.

### The two coordinates, and the contrast panel

Foundations `02` splits the choice into **Q-x2a (which quantity)** and **Q-x2b (where on the chain / which
node)**. Asking both per peril is the whole lesson in one table — verified across four built perils + two
forward:

| Peril | Q-x2a quantity collapses? | Q-x2b node collapses? | Shape it teaches |
|---|:--:|:--:|---|
| **Hail × solar** | yes (MESH mm) | yes (gridded-MESH) | **degenerate** — both collapse; residual grid→panel gap |
| **Convective wind × wind farm** | yes (3-s gust) | **no** (anemometer / hub-`r` / member) | **hero** — quantity collapses, node diverges |
| **Wildfire × solar** | catalog↔damage yes (kW/m) | catalog↔damage yes (zero gap) | **chain-position** — axis = what data delivers |
| **Flood × solar** | no (depth / velocity / gauge) | no | **split (E2)** — different quantities by mechanism |
| **Winter ice/snow** *(fwd)* | no (composite vs depth) | no | **composite (E1)** — inputs fuse to one scalar |
| **Hurricane** *(fwd)* | no (category / sustained / gust) | no | **split + averaging-time bridge** |

### Worked examples

**Convective wind — quantity collapses, node diverges (the hero).** Catalog `magnitude_metric='3s_gust_ms'`
(read off the ASCE return-period surface at **10 m, Exposure C**); damage curve at **hub height**,
design-normalized `r = V_3s_hub / Ve50_class`; parametric trigger at a **site anemometer** at sensor height.
`[REF: m1_catalog/01_catalog.py:321; dossier :99,106-107]` `[OURS — node assignment]` One quantity, three
nodes. The bridges connecting them — all on the same gust quantity — include **EF → gust** (tornado catalog,
bin-midpoints `{EF0:75 … EF5:226 mph}`, bounded GPD `ξ<0`), and **Vref 10-min-mean → Ve50 3-s-gust** (gust
factor ≈ 1.4, an **averaging-time** bridge). And the sharpest finding: the **10 m → hub-height** terrain
bridge — the central catalog→damage node-gap — is **declared (`AWN-15`, assigned to M2) but not built**; the
M2 code passes the gust through unconverted. `[REF: layer0 + AWN-15]` **So basis risk can hide *inside the
pipeline*, not only in an insurance product.** (Why one curve serves two sub-perils: *"the gust has no memory
of where it came from"* — `[REF: commit f6788d7]`.)

**Hail — degenerate (both collapse), plus the bridge-behind-the-axis.** All three speak **MESH diameter
(mm)** at the gridded-MESH node. `[REF: Notebooks/hail/m1_catalog/01_event_catalog.py:144,179-180]` Physics
hands a composite combiner — `KE = ½·m(D)·v(D)²` — but the axis stays **diameter**, because *catalogs provide
size, not energy*; KE is a **derived bridge, never the input axis**, and the built M3 doesn't even compute it.
`[REF: dossier:135-141,462-495]` Even with quantity *and* node collapsed, a residual gap remains —
gridded-MESH (estimated aloft) → the impact a panel actually takes — which the parametric trigger **monetizes**
and the damage curve **absorbs** into conditioners. *Caution `[REF]`:* hail has **two non-agreeing damage
curves** — the built capex-weighted *subsystem* blend (asset cap ≈ 0.344) vs the `damage_modeling` dossier
v1.3 *failure-unit* `P_break` (D50 ≈ 41/53/64 mm), not yet wired in — so "the hail damage axis" has two
instantiations; both on MESH mm, but they disagree on grain and numbers.

**Wildfire — the chain-position rule, vivid.** FSim emits **fireline intensity (kW/m)** and the damage curve
reads kW/m **directly** → catalog and damage at the **same node, zero gap.** `[REF:
Notebooks/wildfire/m1_catalog/01_catalog.py:64; solar/m3_damage/01_damage.py]` *Component temperature would be
more honest but is downstream of an unbuilt coupling model, so the axis sits where the data speaks* — the rule
in one sentence. `[REF: foundations 02 §5b]` It also owns the platform's **one** deferred 2-D axis —
residence-time burn-through, a *singleton* by design. `[REF: foundations 02 §5a]`

**Flood — the split (E2).** One hazard, **two univariate axes by mechanism**: **depth** shorts the
electricals, **velocity/scour** attacks the foundation — two curves, summed, not one 2-D surface. `[REF:
flood dossier:156-184]` Quantity does *not* collapse. (Precision: `h_i = max(0, WSE − z_i_crit)` is a
horizontal *datum re-reference* — same depth quantity, component frame — a Q-x2b shift, not a Q-x2a change.)
*(Forward: ice/snow is the clean **E1 composite** — ice + snow + density fuse to one areal-load kPa, where a
depth-only trigger is density-blind; hurricane is **split + averaging-time**, where "unqualified gust = 3-s"
breaks because NHC reports 1-min sustained.)*

## How to recognize it next time

- **For any new (hazard, product), ask Q-x2a and Q-x2b separately:** *which quantity* and *which node*.
  Agreement on the quantity is **not** agreement on the node.
- **The "same variable, no basis risk" tell:** you're about to conclude two consumers are aligned because they
  use the same units. Stop — locate each on the chain (sensor height? hub? component datum?). The gap is a
  *node* gap.
- **The unmodeled-node-gap tell:** a coupling/terrain/height bridge is *declared* (an assumption, a "to be
  done in M2") but the code passes the intensity through unchanged. That is silent basis risk *inside the
  model* — the wind 10 m→hub case (`AWN-15`).
- **The hedge-vs-replacement tell:** if a parametric trigger's node = the damage node, it's indemnity (slow,
  exact); if upstream, it's a hedge (fast, basis-risk = the gap). Pick the node by *what the product is for*,
  not by what's most physical.
- **The bridge-vs-axis tell:** physics offers a more-fundamental quantity (KE, component temperature, member
  load) — keep it as a *bridge behind* the axis; the axis is what the **data can speak**.

## Caveats and limits

- **All parametric legs here are `[ILLUSTRATIVE]`** — no repo grounding. Only the convective-wind dollar
  example (16% × $50M = $8M vs a $7.5M deductible on $150M TIV) is a worked case, and it is an external
  market reference (the Descartes PDF is a *product/commercial* source, **not** a modeling-methodology one).
- **The node vocabulary is partly `[OURS]`** — standard `04` grounds `Hazard source / Local / Contact /
  Damage-state`; the "load" intermediate and the "each consumer pins a node" overlay are our synthesis. Don't
  read the 5-node chain as a source quote.
- **The averaging-time bridge is wind-family-only** (1-min sustained / 10-min mean / 3-s gust, all ≈ 1.4×
  apart) — no clean non-wind instance. Don't generalize it to other perils. (`AWN-27`: never mix gust and
  sustained.)
- **Deferred-2D is a singleton** (wildfire residence-time) — it is the *at-most-one* genuine 2-D case in v1,
  not a pattern.
- **Quantity-collapse is the exception, not the rule** — only wind (and degenerately hail) collapse; flood,
  ice, hurricane are genuine splits/composites.

## Cross-references

- **The full open discussion this distills:**
  [`extra/discussion/intensity_variable_and_products/`](../extra/discussion/intensity_variable_and_products/README.md)
  (`01` the frame · `02` the parametric trigger as a new consumer).
- **Canonical x-axis method (the `[REF]` half):** `damage_modeling` foundations
  [`02_x_axis_intensity_variable`](../../damage_modeling/docs/damage_curves/damage_curve_foundations/questions/02_x_axis_intensity_variable.md)
  + standard [`04_x_axis_decision_standard`](../../damage_modeling/docs/damage_curves/damage_curve_implementation/).
- **Siblings:** [`07`](07_one_simulation_two_products.md) (one simulation, two non-interchangeable products —
  same shape, one layer over) · [`05`](05_damage_curve_three_coupled_choices.md) (the damage curve as coupled
  choices) · [`11`](11_return_period_conventions.md) (another "same word, different meaning" trap).
- **Where it shows in code/docs:** `Notebooks/convective_wind/m1_catalog/01_catalog.py` ·
  `Notebooks/hail/m1_catalog/01_event_catalog.py` · `Notebooks/wildfire/m1_catalog/01_catalog.py` ·
  `data/hail/damage_curves/hail_solar_asset_capex_weighted.json` · the `convective_wind` plans
  ([`DD-WN-6`, `AWN-5`, `AWN-15`](../plans/convective_wind/decisions.md)).
- **The principle it serves:** *standard interface, not standard physics*
  ([`principles/`](../principles/README.md)) — applied to the x-axis.
