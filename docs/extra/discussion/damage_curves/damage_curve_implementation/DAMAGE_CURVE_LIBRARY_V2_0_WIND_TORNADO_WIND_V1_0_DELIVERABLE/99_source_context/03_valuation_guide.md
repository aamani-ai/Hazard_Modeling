# 03 · Valuation — how we assign dollar value to subsystems & components  🟡 GUIDE

A **guide and a map**, not the value database. This doc reasons out *how to think about assigning
value* to the parts of a solar or wind asset — the three questions hidden in `loss = DR · value`,
the basis trap that scales every metric, how deep to source (and why not deeper), what the public
data can and can't tell us, the nuances that bite, and the **spec the eventual value dataset must
satisfy**. The numbers themselves are sourced later, *against this frame*. Same relationship doc
[`08`](08_damage_curve_granularity.md) had to curve-building: reason out the *system* first, fill
it cell-by-cell later.

*Source key:* substrate = dev lookups (`typical_capex_weight` is **NULL** today → this doc is the
frame for filling it); principles = `basics_spot_on`, `system_coherence_over_local_elegance`,
`hazard_asset_specificity`, `modularity_and_scaling`. `[REF]` inherited; `[OURS]` derived;
`[SRC]` from the source survey (§4). **All dollar figures below are illustrative-of-structure, not
adopted values** — they show what the sources look like, not what we commit to.

> **Why a guide, not a table (per [`08`](08_damage_curve_granularity.md)'s precedent).** We did not
> enumerate "hail→curve-X"; we built the *method* for choosing. Same here: we don't list
> "PV_ARRAY = 0.40"; we build the *system* for sourcing, defaulting, and labeling values, so the
> numbers are defensible when they come.

---

## 1 · The question is actually THREE questions

`loss = DR · value` hides three distinct value decisions that get conflated. Separating them is
half the value of this doc.

```
   loss = DR · value
                 |
                 +-- (a) ALLOCATION  : what share of asset value does each subsystem carry?
                 |        -> sets the per-subsystem value base. (NREL/LBNL capex shares)
                 |
                 +-- (b) AT-RISK FRACTION f : within a subsystem a mechanism concentrates on,
                 |        what share is actually exposed?  (doc-08: only where concentration)
                 |        -> module-glass within PV_ARRAY for hail; below-waterline within a
                 |           subsystem for flood.
                 |
                 +-- (c) BASIS / DENOMINATOR : value-of-WHAT? the total we divide by.
                          -> TIV vs replacement vs insured vs capex; incl/excl sunk+soft.
                          -> scales EVERY %-of-TIV metric linearly. The sleeper.
```

These are not the same number and not even the same *kind* of number: (a) is a **cost-share**, (b)
is an **exposure-share**, (c) is a **definitional choice about scope of value**. Conflating
cost-share with exposure-share, or leaving the basis unstated, is the recurring error.

---

## 2 · The BASIS problem — surfaced first, because a share is meaningless without it

A "share" is share-*of-what*. Until the denominator is pinned, every allocation number is
ambiguous. The source survey (§4) makes this concrete and slightly alarming: **the canonical
sources don't even agree on the denominator with each other.**

### 2.1 · Three prices for the same system `[SRC]`

The NREL solar benchmark reports the *same* system at three different totals, by purpose:

| Basis | What it is | When it's the right denominator |
|---|---|---|
| **MSP** (minimum sustainable price) | the floor price a vendor can charge and survive | tracking tech progress; **not** valuation |
| **MMP** (modeled market price) | actual cash sales price in the period | closest to "what was paid" |
| **Overnight capital cost** | system cost excluding construction financing | ATB's basis; comparability across techs |

Pick the wrong one and every dollar metric shifts by the spread between them. **A value without its
basis label is not a number — it's three numbers wearing a trench coat.**

### 2.2 · The sunk/soft trap — and why physical-damage loss needs a *physical* denominator `[OURS]`

The deeper trap, and the one that silently understates %-of-TIV. Total installed capex includes
costs that are **not at-risk to a physical hazard**:

```
   total installed CAPEX  =  [ at-risk PHYSICAL ]  +  [ sunk / soft / non-physical ]
                              modules, inverter,       land, interconnection/network upgrades,
                              racking, transformer,     development, engineering, financing,
                              cabling, foundation       construction interest, contingency, warranty

   a HAIL swath destroys some of the LEFT box. It can destroy NONE of the right box
   (you don't "repair" financing or re-buy land after hail).

   => dividing physical loss by TOTAL capex makes %-of-TIV read ARTIFICIALLY LOW.
      the honest denominator for a physical-damage ratio is the PHYSICAL replaceable base,
      not full installed capex.
```

This is not hypothetical — the survey shows how *large* the non-physical slice is:

- **Solar** `[SRC]`: soft costs have run as high as ~50–68% of system cost in some sectors;
  utility-scale EBOS recently *grew* specifically because **interconnection / network-upgrade**
  costs were folded in — costs that are pure sunk/non-physical.
- **Wind** `[SRC]`: a representative land-based breakdown is ~**55–70% turbine**, ~**22–30% BOS**,
  ~**7–15% soft/financial** (construction finance, contingency, warranty, insurance). The financial
  slice alone is non-physical.

> **The basis rule `[OURS]`.** For a *physical-damage* loss ratio, reconcile against the **physical
> replaceable value**, and account for sunk/soft explicitly as a separate (DR ≈ 0) slice — never
> silently leave it in the denominator. State the basis on every value. (This is doc-08 §6's
> exhaustive-tiling discipline applied to the value ledger: physical + sunk/soft = stated basis.)

### 2.3 · The two techs disagree on the denominator — flag it `[SRC]`

A subtle landmine: **ATB land-based wind CAPEX *excludes* project interconnection**, while the NREL
solar benchmark's EBOS now *includes* network-upgrade costs. So if we naively take "NREL capex" for
both techs, solar and wind are on **different bases** before we even start. Any cross-tech
comparison (or a shared portfolio TIV) must normalize the basis first. Do not assume the sources
are commensurable.

---

## 3 · The GRAIN question — how deep to source (answered by doc 08)

How finely must we value? `system_coherence` warns against the seductive failure here: **chasing
precision the model can't use.** Doc [`08`](08_damage_curve_granularity.md) already fixed the grain
the damage model consumes, so this is settled, not open:

```
   SOURCE values to the grain the damage model CONSUMES, no finer:

   NEEDED:     subsystem-level value shares           (PV_ARRAY, INVERTER_SYSTEM, ... / ROTOR, NACELLE, TOWER)
   NEEDED:     a FEW at-risk fractions f               only where a mechanism concentrates (doc-08):
                                                        module-glass-within-PV_ARRAY (hail);
                                                        below-waterline-share (flood)
   NOT NEEDED: full component cost teardown            (within-nacelle gearbox-vs-generator split, etc.)
               -> the curve's own uncertainty dwarfs it; out-resolving it is wasted effort
```

**Lucky alignment `[SRC]`:** the public data happens to land right at the needed grain. NREL's Cost
of Wind Energy Review already reports turbine cost at **subsystem grain** (rotor / nacelle / tower,
and even blades / pitch / hub / drivetrain / nacelle-electrical / yaw) — which maps almost directly
onto the substrate's wind subsystems. Solar benchmarks report module / inverter / structural-BOS /
electrical-BOS / soft — also subsystem-ish. So the grain doc-08 demands is the grain the sources
supply. We are not forced finer, and we should not *go* finer.

---

## 4 · The SOURCE LANDSCAPE (the survey — characterize, don't mine)

What exists, at what grain, on what basis, how much to trust it. **Characterizing the terrain so the
later sourcing pass is informed — not extracting final values here.**

### 4.1 · Solar `[SRC]`

| Source | Grain | Basis | Vintage | Trust | What it answers / caveat |
|---|---|---|---|---|---|
| **NREL ATB** (utility-scale PV) | system $/kW_AC, scenario-level | overnight capital cost | annual (2024) | High | clean total + projections; **not** a fine component split; $/kW_AC unit (≠ DC) — watch the AC/DC trap |
| **NREL PV Cost Benchmark** (Ramasamy et al.) | **module / inverter / SBOS / EBOS / soft** | MSP **and** MMP | annual (Q1 2023+) | High | the component-share source; **EBOS now includes interconnection** (sunk) — must strip for physical basis |
| **LBNL "Utility-Scale Solar"** | project-level installed price, empirical | actual reported | annual | High | real market prices (vs modeled); good for basis reconciliation |
| **IRENA** | global total installed | total installed | annual | Med (global, not US-specific) | context / cross-check, not primary for US assets |

### 4.2 · Wind `[SRC]`

| Source | Grain | Basis | Vintage | Trust | What it answers / caveat |
|---|---|---|---|---|---|
| **NREL Cost of Wind Energy Review** | **rotor / nacelle / tower → blade, pitch, hub, drivetrain, nacelle-elec, yaw** | turbine + BOS + soft, $/kW | annual (2021–2024 eds) | High | best subsystem-grain match to substrate; turbine ≈ 55–70%, BOS ≈ 22–30%, soft ≈ 7–15% |
| **NREL ATB** (land-based wind) | system $/kW, scenario | overnight; **excludes interconnection** | annual | High | clean total + projections; **different basis than solar benchmark** (§2.3) |
| **LBNL "Land-Based Wind Market Report"** | project-level installed cost, empirical | actual reported | annual | High | real prices; regional variation; basis reconciliation |
| **LandBOSSE / WISDEM** (NREL models) | BOS / component, modeled | modeled | model | Med-High | derive site-specific splits where empirical data is thin |

### 4.3 · The "f" sources (the at-risk fraction within a subsystem) `[SRC / OURS]`

The hardest layer — the within-subsystem exposure share (doc-08's `f`). Public capex data goes to
subsystem, not always *inside* it. Where `f` needs finer:

- **Hail module-glass-and-cells within PV_ARRAY** — needs a *module BOM* cost share (glass vs cells
  vs frame vs backsheet vs jbox). Module-level BOM cost splits exist in PV manufacturing literature
  but are coarser/older than system capex. Candidate for a **labeled placeholder** (§5).
- **Below-waterline within a subsystem (flood)** — `f` here is **not a fixed material share at all**;
  it's *site-and-depth-dependent* (which equipment sits below H). This `f` is a **geometry/elevation
  fact**, sourced per-site or assumed, not from capex literature. (This is the doc-08 §5 multi-axis
  point resurfacing in the value layer.)

> Note `[OURS]`: `f` is a different *species* of number per hazard — a **material cost share** for
> hail, an **elevation geometry** for flood. The guide must not treat "f" as one sourceable column;
> it's hazard-specific in kind.

---

## 5 · The NUANCES & TRAPS (the honest caveats)

| # | Trap | Why it bites | Discipline |
|---|---|---|---|
| **N1** | **cost-share ≠ value-share ≠ at-risk-share** | capex tells you what was *paid*, not what's *at-risk* or *replaceable*. Three different quantities. | label which one each number is; never silently substitute |
| **N2** | **basis drift over time** | module prices fell → BOS/soft *share* rose without anything physical changing. A 2018 split misreads a 2024 plant. | tag vintage; prefer recent; treat shares as moving |
| **N3** | **AC vs DC denominators (solar)** | ATB is $/kW_AC, benchmarks often $/W_DC; ILR ≈ 1.2–1.4 means they differ by ~30%. | normalize unit before combining sources |
| **N4** | **interconnection/soft inflating "cost"** | recent EBOS growth is interconnection (sunk), not physical value | strip sunk/soft for the physical-damage basis (§2.2) |
| **N5** | **regional / project variation** | national averages ≠ any specific plant | generic default *with* an override path (substrate DD-076) |
| **N6** | **"f" is hazard-specific in kind** | hail-f is a material share; flood-f is site geometry | don't build one "f" column; build per-hazard |
| **N7** | **immune ≠ absent from the ledger** | a DR≈0 subsystem still holds value; dropping it breaks reconciliation | keep immune + sunk/soft as explicit DR≈0 slices (doc-08 §6) |

---

## 6 · WHAT THE DELIVERABLE SHOULD LOOK LIKE (the spec for the real thing)

The eventual value dataset (built elsewhere, *not* here) should satisfy this spec — derived from
everything above:

```
   a per-(tech, subsystem) VALUE-SHARE record, carrying:

   tech            solar | wind
   subsystem       PV_ARRAY | INVERTER_SYSTEM | ... | ROTOR | NACELLE | TOWER | ...
   value_share     fraction of the PHYSICAL replaceable base (NOT total capex)
   basis           which denominator (replacement | MMP | overnight | ...) — REQUIRED, never null
   source          NREL-CWER-2024 | NREL-PV-Benchmark-Q1'23 | LBNL-... | placeholder
   vintage         year of the source
   trust_tier      high | med | placeholder
   override_flag   is this a generic default or plant-specific?  (substrate DD-047/076)
   at_risk_f       { per hazard: the within-subsystem exposure fraction, where concentration applies }
   f_kind          material-share | site-geometry | n/a   (per N6)

   + RECONCILIATION RULE (doc-08 §6, applied to value):
        Σ subsystem value_share (physical)  +  immune(DR≈0)  +  sunk/soft  =  stated basis (1.0)
        exhaustive, non-overlapping. if it doesn't sum, a slice is missing or double-counted.

   + PLUG-IN: loss = Σ_c DR_c(x_c) · ( value_share_c · [·f if concentrated] · physical_base_$ )
```

The spec's non-negotiables: **basis is required on every value** (N1, §2), **the physical/sunk/soft
split is explicit** (N4, N7), and **f is per-hazard and typed** (N6). Everything else is fillable
incrementally.

---

## 7 · How this composes end-to-end (coherence check)

```
   curation:        pull subsystem shares from NREL/LBNL at the grain doc-08 needs (no finer)
   basis:           normalize to PHYSICAL replaceable base; strip+park sunk/soft
   value:           value_c = share_c · (f if concentrated) · physical_base
   application:     loss = Σ DR_c(x_c) · value_c     (doc-08's summation; no grouping object)
   multi-hazard:    f is re-read per hazard (hail material-share; flood geometry); shares stable
   reconcile:       physical + immune + sunk/soft = basis (exhaustive) -> %-of-TIV is honest
```

Every stage clears, and the basis discipline is what makes the final %-of-TIV trustworthy rather
than artificially low.

---

## 8 · What this guide commits us to

- Value is **three questions** (allocation / at-risk-f / basis), kept separate.
- **Basis-first**: every value carries a required basis label; physical-damage ratios reconcile to
  the **physical replaceable base**, with sunk/soft as an explicit DR≈0 slice.
- Source to the **subsystem grain doc-08 consumes**, no finer; `f` only where concentration applies,
  and `f` is **typed per hazard** (material-share vs site-geometry).
- **Placeholders-with-provenance are legitimate** (substrate DD-047/076) — a labeled, overridable
  default beats a missing number or a false-precision one.
- The deliverable is a **per-(tech, subsystem) value-share table** meeting the §6 spec, reconciled
  exhaustively (doc-08 §6).

**Parked / to the sourcing pass (not this doc):** the actual numbers; per-site flood-f geometry; the
module-BOM split for hail-f; cross-tech basis normalization constants.

---

## 9 · Open / to-research-later

- **The module-BOM source for hail-f.** Glass-vs-cells-vs-frame cost share inside a module — exists
  in PV manufacturing literature but coarse/older. Needs a dedicated dig; placeholder until then.
- **Flood-f is site geometry, not literature.** Confirm it's sourced per-site (elevation survey)
  rather than from any capex table — it may belong to the coupling/exposure layer, not here.
- **Cross-tech basis normalization.** ATB-wind excludes interconnection; solar-benchmark EBOS
  includes it. The constants to put them on one basis are unresolved (§2.3).
- **Replacement vs insured vs TIV.** §2 lays out the options; the *choice* for InfraSure's metrics is
  not yet made — it interacts with the risk-metrics reference and should be pinned with that doc.
- **Is there an internal default set?** Substrate `typical_capex_weight` is NULL today, pointing at a
  future `resiliency_subsystem` dim. This guide is the frame that dim should be filled against; if an
  internal position already exists, it supersedes the generic NREL defaults here.

---

## 10 · Status

🟡 **Guide drafted; source terrain surveyed, numbers deliberately not mined.** The valuation problem
is framed as three separate questions, basis-first; the public-source landscape is characterized for
both techs (NREL ATB, NREL benchmarks/CWER, LBNL, IRENA) with grain/basis/trust noted; the deliverable
spec is set. The load-bearing finding: **basis is the sleeper** — physical-damage ratios must
reconcile to a physical replaceable base, and the canonical sources disagree on the denominator, so
basis must be labeled and normalized before any number is trusted. Ready to hand to a sourcing pass —
or to move to the next reasoning topic (x-axis framing → [`01`](01_emit_object.md)).

*Links:* [`08 granularity`](08_damage_curve_granularity.md) (sets the grain) · [`01 emit`](01_emit_object.md) ·
[`00 §5`](00_context_and_scope.md) · risk-metrics reference (basis choice) ·
`system_coherence_over_local_elegance` · `basics_spot_on` · substrate (NULL capex_weight → this is its frame).
