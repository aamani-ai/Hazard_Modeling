# 00 · Context & scope — the settled ground

The shared ground everyone argues *from*. This doc holds what is **already decided** about the damage curve,
plus the reference material (vocabulary, current state, the library, the how-to-choose framework). The
**open** calls live in `01`–`07`; this doc is the part we are *not* re-litigating.

*Source key:* **Methodology** = Drive `hazard_asset_loss_distribution_methodology` (§6 severity · §7 duration ·
§9 financial); **Terminology** = Drive `hazard_modeling_terminology` (§5); library = `infrasure-damage-curves`;
per-cell ids under `docs/plans/{hail,wildfire,convective_wind}/`. `[REF]` = from the references; `[OURS]` =
derived by building.

---

## 1 · The v1 scope box

The curve as built in v1 is deliberately narrow. Every claim below lives inside this box unless a sub-doc
flags a Phase-2/3 extension.

| Boundary | v1 is… | Out of scope (→ where) |
|---|---|---|
| **Spatial** | single-site, one asset | portfolio / correlated multi-asset → [`04`](04_portfolio_extension.md) |
| **Loss kind** | gross **physical** repair/replacement cost | revenue-loss, curtailment, feathering, fatigue → disruption track / Performance tier → [`06`](06_financial_terms_and_scope_edges.md) |
| **Financial** | occurrence basis, gross of terms | deductibles, limits, claims-made, tax → [`06`](06_financial_terms_and_scope_edges.md) |
| **Climate** | current-climate intensity→damage | hazard-rate non-stationarity (catalog/coupling, not the curve) |

> The error mode is **silent scope creep** — a curve quietly read as if it already covered BI, curtailment,
> deductibles, or correlation. Label the boundary every time.

## 2 · Vocabulary — the curve family

(verbatim/near-verbatim from Terminology §5 + Methodology §6)

| Term | What it is | Emits | The confusion it kills |
|---|---|---|---|
| **Vulnerability / damage / loss function** | intensity → **mean damage ratio** | a number | the three are *synonyms*; "fragility" is **not** one of them |
| **Fragility curve** | intensity → **P(reach each damage state)** | a probability | categorically different — an *input you aggregate into* vulnerability, not a substitute |
| **Damage ratio (MDR)** | repair cost ÷ replacement value | fraction [0, 1+] | not a damage *state* (continuous vs discrete) |
| **Damage state** | discrete none/slight/moderate/extensive/complete | a category | not a ratio; the ratio = cost-weighted average over states |
| **Severity distribution** | loss sizes pooled across events | a distribution | not OEP/AEP — no calendar; per-event not annual |
| **Derating curve** | non-damaging stress → lost output | foregone MWh × price | **not a damage function** — revenue, no physical damage (out of v1 → [`06`](06_financial_terms_and_scope_edges.md)) |
| **Secondary uncertainty** | the spread *around* the mean DR at a fixed intensity | — | "carry the distribution around the curve, not just the point estimate" (Methodology §6) |

**Fragility → vulnerability (the conversion).** Difference adjacent exceedance curves → exclusive state
probabilities (e.g. None 20 / Slight 30 / Moderate 30 / Extensive 15 / Complete 5); attach a cost ratio to
each (0 / 5 / 20 / 55 / 100 %); probability-weight → `0.208`. That single **20.8 %** *is* the vulnerability
curve's value at that intensity. Fragility is the richer object; vulnerability is its costed expectation.

```
   intensity
      |
      v
   FRAGILITY  -->  P(state):  none .20 | slight .30 | mod .30 | ext .15 | comp .05
      |                cost:    x0     |    x.05    |  x.20   |  x.55   |  x1.0
      |                                 \____ probability-weighted average ____/
      v
   VULNERABILITY  -->  mean damage ratio = 0.208  -->  severity distribution
   (= the damage curve)                                (losses pooled over events)
```

## 3 · What's already settled

The calls we build *on*, not the ones we're debating.

- **Subsystem-decomposed, capex-weighted blend** `Asset_DR = Σ wᵢ·DRᵢ` is the architecture. Fixes the old
  "one curve per (hazard × asset)" failure that had nowhere to put stow angle (hail A15; library
  `aggregation-model.md`; `[Porter et al. 2001]`; [`hazard_asset_specificity.md`](../../../principles/hazard_asset_specificity.md)).
- **Logistic functional form per subsystem** `DR(x) = L/(1+exp(−k(x−x₀)))` — all 42 library curves, all three
  cells. Parameters are physical: `L` = cap, `x₀` = 50 %-damage midpoint, `k` = steepness. (The Methodology's
  PCHIP / physics / linear menu is the *construction-from-knots* fallback, not what the cells do.)
- **Saturation / no extrapolation** — caps at `Σ wᵢ·Lᵢ`; retires the old curve that ran to ~100 % (hail A16).
- **Anchoring applied selectively** to remove a non-physical floor `DR(0) > 0` — yes wildfire (DD-W8/AW-29),
  yes wind (DD-WN-11), **no hail** (IBHS curve already sharp; floor ≈ 0.17 %).
- **Curated, not loss-fitted** — provenance is the deliverable; for severity, curation/selection do the work
  and fitting is "mostly a convenience for sampling" (Methodology §6).
- **Cap physical damage, not total economic loss** (Methodology §9) — doctrine; BI itself is deferred ([`06`](06_financial_terms_and_scope_edges.md)).
- **v1 representation = scalar mean DR** in all three cells — settled *as the v1 choice, explicitly temporary*
  (hail A17, wind AWN-24, wildfire per-class). Whether to climb off it is [`01`](01_emit_object.md).

The shape these settled choices produce — a saturating logistic per subsystem, anchored where a raw floor exists:

```
   DR
   cap |- - - - - - - - ,-----------------   saturates at cap = sum(wi*Li)
       |              ,-'                     (no extrapolation past it)
       |            ,-'     DR = L / (1 + exp(-k*(x - x0)))
       |          ,-'       x0 = 50%-damage midpoint,  k = steepness
       |       ,-'
     0 +----'''-------------------------------> intensity
       :...   raw floor DR(0)>0  --anchor subtracts it-->  DR(0)=0
              (wildfire, wind;  NOT hail - already sharp)
```

## 4 · Current state per built cell

| Cell | Form | Emits | Notable |
|---|---|---|---|
| **Hail × Solar** (Hayhurst TX) | 2-subsystem logistic blend (PV_MODULE L=0.95 w=0.32 + TRACKER L=0.40 w=0.10), axis = hail mm | scalar mean DR/event; `loss = DR×value` on hit, pᵢ kept separate | no anchoring; saturates **~34 %**; *immune-share wording inconsistent — see [assumptions DC-c1](assumptions.md)* |
| **Wildfire × Solar** (Hayhurst + Matrix) | 6-subsystem **anchored** blend (weights Σ ≈ 0.70), axis = Byram kW/m | scalar mean DR per flame-length class | anchored (5.8 %→0 floor); cap **~57 %**; ~30 % TIV unmodelled (AW-19); E[DR\|fire] 1.0 % vs 6.5 % across sites |
| **Convective-Wind × Wind-Farm** (Traverse OK, Shepherds Flat OR) | **one turbine, two sub-peril curves** (7 subsystems Σ = 1.00), axis = 3-s gust m/s | scalar DR per gust per sub-peril (lookup table) | two-curve fork by *mechanism* (DD-WN-16): tornado reaches all subsystems → 1.0; strong-wind aero-only → cap **~0.65**; strong-wind EAL ≈ 0 is honest (AWN-31) |

**Convergences:** curated-not-fitted · capex-weighted subsystem blend · natural/anchored saturation ·
conditional full loss on hit (probability separate until M4) · scalar mean (v1) · subsystem **independence**
assumed (no cascade) · single-site.

## 5 · The library today (`infrasure-damage-curves`)

- **Produces** a single deterministic **scalar MDR per subsystem** — `DR(x) = L/(1+exp(−k(x−x₀)))`. **42
  curves** across 8 hazard×asset combos, 10 subsystems.
- **Aggregates** `Asset_DR = Σ wᵢ·DRᵢ`, capex-weighted (NREL ATB / LBNL defaults, user-overridable);
  uncovered subsystems contribute 0 and don't adjust the denominator (weights sum ~0.70–0.85). (`aggregation-model.md`)
- **Confidence** = a 6-tier scale (Very-Low → Medium-High; "High" unreached) — **metadata, not a scaling
  factor**; drives badges + a research-priority score `(1 − conf/5) × capex_weight × freq`. (`confidence-framework.md`)
- **Derivation** = 4-tier evidence hierarchy (empirical > standards > proxy > expert judgment). (`curve-derivation-methodology.md`)
- **Cannot today** emit fragility/state or a damage distribution — "point estimates; no probabilistic damage
  distribution yet." Fragility/state is a **Gen-2** plan. → directly relevant to [`01`](01_emit_object.md).

## 6 · How to choose — the framework so far

No universal rule (Methodology §11: "reason through the factors first; the table is a starting point").

1. **Start from per-peril data.** Fragility-derived source → state vector; published-MDR source → scalar. Let
   the source's native form set the floor.
2. **Specialize where the mechanism differs; standardize the interface.** Split into its own curve only if
   *both* the physical footprint **and** the data/metric differ (the dual test) — else share.
3. **Choose representation by the metric you price.** Scalar mean is fine for **EAL** (linearity preserves the
   mean); **VaR/PML/TVaR live in the tail** → you need the spread ([`01`](01_emit_object.md), [`02`](02_metrics_and_tail_honesty.md)).
4. **Dominant-uncertainty discipline.** The curve is the dominant uncertainty; "more simulation is not more
   truth." Get the curve + representation right, verify against absolute known-answers
   ([`basics_spot_on.md`](../../../principles/basics_spot_on.md)).
5. **Treat value-allocation as a financial decision** — allocate at-risk replaceable value, reconcile to TIV;
   the cap is set by allocation, not physics ([`03`](03_value_allocation_and_tiv.md)).
6. **Defer richness until the metric demands it.** v1 = simplest *correct* frame; Phase 2 = richest
   *necessary* output; Phase 3 = component attributes.
