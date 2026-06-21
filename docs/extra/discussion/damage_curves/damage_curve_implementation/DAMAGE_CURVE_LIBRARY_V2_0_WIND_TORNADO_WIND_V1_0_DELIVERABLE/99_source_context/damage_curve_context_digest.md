# Damage-Curve Foundations — Context Digest for the Second Deliverable

**Purpose of this memo:** stabilize the project context before building the next large deliverable. The valuation workbook solved the value side of `loss = DR × value`. The zip file shows that the next deliverable is the damage-curve side: a governed, provenance-carrying record per hazard × failure-unit, assembled into asset-level loss by summation.

This memo is based on the uploaded `damage_curve_foundations.zip`, especially:

- `README.md`
- `00_assembled_curve_record.md`
- `questions/01_granularity.md`
- `questions/02_x_axis_intensity_variable.md`
- `questions/03_valuation_guide.md`
- `questions/04_curation_derivation.md`
- `questions/05_emit_object.md`
- `questions/06_metrics_and_tail_honesty.md`
- `principles/P1_system_coherence_over_local_elegance.md`
- `principles/P2_discussion_before_commitment.md`
- `principles/P3_reference_is_input_not_authority.md`

---

## 1. The big picture

The valuation deliverable answered:

```text
What dollar value sits behind each subsystem/component?
```

The next deliverable answers:

```text
Given a hazard intensity, what damage ratio applies to each failure-unit,
what evidence supports that curve, what object does it emit, and which
metrics can honestly be produced from it?
```

Together, the two pieces form the physical loss engine:

```text
                       ASSET / ENGINEERING SUBSTRATE
                  plant → generator → subsystem → component
                                      │
                                      ▼
                              VALUE LEDGER
              physical replaceable value by subsystem/component
                                      │
                                      ▼
                             DAMAGE CURVES
              DR_i(x) per hazard × failure-unit, with provenance
                                      │
                                      ▼
                               LOSS ENGINE
                    loss = Σ DR_i(x_i) × value_i
                                      │
                                      ▼
                               METRICS LAYER
                  EAL if honest; tail withheld unless spread exists
```

The valuation workbook is therefore not separate from the damage work. It provides the `value_i`, `basis`, and `cap_L` inputs that the curve records require.

---

## 2. The actual second deliverable

The zip makes clear that the next deliverable is not simply “a damage curve.” It is a structured **assembled curve record**.

The atomic object is:

```text
one failure-unit curve record
```

A hazard × asset cell is a collection of these records:

```text
CELL: hail × solar
├─ curve record: PV module / glass-cells unit
├─ curve record: tracker / mounting unit, if relevant
├─ curve record: inverter or electrical unit, if relevant
├─ curve record: immune / low-damage parts, DR ≈ 0
└─ assembly rule: loss = Σ DR_i(x_i) × value_i
```

The key implication:

```text
We do not build one giant asset-level curve by default.
We build per-failure-unit curves and sum their dollar losses.
```

This is consistent with the valuation workbook, which already decomposes value into physical buckets. The damage work now needs to map hazard response onto those buckets.

---

## 3. The six-question dependency chain

The zip’s README gives the dependency order. The docs are not independent essays; each governs a specific field group in the final record.

```text
01 granularity
   ↓
02 x-axis intensity variable
   ↓
03 valuation
   ↓
04 curation / derivation
   ↓
05 emit object
   ↓
06 metrics / tail honesty
   ↓
00 assembled curve record
```

A practical translation:

| Doc | Decision | What it controls in the deliverable |
|---|---|---|
| `01_granularity` | What grain to model damage at | `failure_unit`, tiling, summation rule |
| `02_x_axis` | What intensity variable the curve uses | `x_axis`, `chain_node`, conditioners |
| `03_valuation` | What value base the curve caps at | `value_share`, `basis`, `cap_L` |
| `04_curation` | How the curve is derived | `form`, `parameters`, `evidence_log`, `anchors`, `bridge` |
| `05_emit_object` | What the curve emits per event | `emit_object`, scalar/spread/states/distribution |
| `06_metrics` | Which metrics may be shipped | `metrics_shippable`, check-backed vs withheld |
| `00_assembled` | The spine tying all fields together | final record schema and fill order |

---

## 4. What the valuation workbook has already solved

The valuation deliverable solved the denominator/value side:

```text
loss = DR × value
          │
          ├─ value basis: physical replaceable, not silent total capex
          ├─ subsystem allocation: where physical dollars sit
          ├─ sunk/soft treatment: explicit DR≈0 or nonphysical slice
          └─ reconciliation: physical + sunk/soft = stated basis
```

The next deliverable should not re-litigate that. It should consume it.

The curve record needs to use the valuation output as follows:

```text
value_share  ← from valuation workbook
basis        ← physical replaceable base
cap_L        ← maximum loss fraction for that failure-unit
value_i      ← value_share_i × physical_base_$
```

This is the bridge:

```text
VALUATION WORKBOOK
  subsystem/component value shares
          │
          ▼
CURVE RECORD
  cap_L and value_i for each failure-unit
          │
          ▼
LOSS CALCULATION
  DR_i(x_i) × value_i
```

---

## 5. Principle stack: how we should think while building

The zip includes three principles. They are important because they constrain how we should approach the next deliverable.

### P1 — System coherence over local elegance

A locally beautiful curve, schema, or decomposition is not enough. It must work end-to-end:

```text
curation → curve → application → multi-hazard aggregation → value reconciliation → metrics
```

A new primitive, axis, distribution, or grouping must pay for itself across the full chain.

Practical consequence:

```text
Do not build a fancy representation just because one hazard example looks cleaner.
Build it only if summation, scalar emission, or subsystem grain actually fails.
```

### P2 — Discussion before commitment

The slow reasoning is part of the work. The zip repeatedly shows cases where the first plausible answer was later overturned.

Practical consequence:

```text
For the next deliverable, we should first lock the record schema and runbook.
Then fill cells.
Do not jump directly into source-mining curves.
```

### P3 — Reference is input, not authority

Schemas, standards, published curves, NREL cost data, existing model cells, and even prior drafts are references. They are evidence, not automatic truth.

Practical consequence:

```text
Use each source for the purpose it was built for.
Do not let a standard, benchmark, or prior model answer a question it was not built to answer.
```

Examples:

```text
asset substrate       → vocabulary, not necessarily damage grain
capex benchmarks      → cost evidence, not automatically at-risk value
IEC/ASCE/IP standards → boundary conditions, not full damage curves
built cells           → evidence of method, not unquestioned authority
```

---

## 6. Granularity: subsystem by default, finer only when forced

The first foundational decision is that we do **not** create a separate “failure-unit” aggregation primitive.

Default:

```text
one curve per subsystem or failure-relevant part
then sum dollar losses
```

The rejected idea was a new grouped “failure unit” object. The reason it was rejected:

```text
Geometric cross-cutting is not enough.
The real test is: joint ≠ sum?
```

If independent curves can be summed correctly, no grouping object is needed.

```text
WRONG test:
  Does the damaged set cross subsystem boundaries?

RIGHT test:
  Does treating the parts independently and summing losses get the joint loss wrong?
```

The method:

```text
For each hazard × asset:

1. Does damage concentrate in a sub-part?
   yes → go finer than subsystem
   no  → stay at subsystem

2. Does a part fail on a distinct intensity axis?
   yes → give it its own curve on its own x-axis
   no  → keep one curve

3. Is the curve curatable at that grain?
   yes → use that grain
   no  → aggregate upward and label the smearing
```

ASCII:

```text
mechanism
   │
   ├─ concentration?
   │      ├─ yes → finer than subsystem
   │      └─ no  → subsystem grain
   │
   ├─ distinct axis?
   │      ├─ yes → separate univariate curve
   │      └─ no  → same curve
   │
   └─ curatable?
          ├─ yes → use it
          └─ no  → aggregate up, label assumption
```

The final assembly remains:

```text
loss(x) = Σ_i DR_i(x_i) × value_i
```

---

## 7. Exhaustive tiling: a hazard × asset pair is a partition

One subtle but important idea: each hazard × asset cell should partition the value ledger.

```text
[ curve value 1 | curve value 2 | curve value 3 | immune DR≈0 value ] = physical basis
```

No value should appear twice. No at-risk value should be missing.

```text
BAD:
  model only the damaged modules and forget the rest of the plant

BETTER:
  include damaged module curve + other exposed curves + immune/DR≈0 rows
```

This is directly analogous to the valuation workbook’s reconciliation:

```text
physical subsystem value + sunk/soft/nonphysical = stated basis
```

For damage curves:

```text
hazard-exposed curve values + immune/DR≈0 curve values = physical damage basis
```

---

## 8. X-axis: univariate for v1

The second foundational decision is that v1 curves should be univariate unless a second axis survives two escape routes.

The three x-axis questions:

```text
Q1: how many axes?
Q2: which variable, and where on the causal chain?
Q3: what conditioners modify the curve but are not axes?
```

### The two escapes from multivariate complexity

```text
ESCAPE 1 — composite collapse
  If physics combines variables into one scalar, use the scalar.
  Example: hail diameter + density + speed → kinetic energy.

ESCAPE 2 — part split
  If variables damage different parts, split into multiple univariate curves.
  Example: flood depth damages electrical equipment; flood velocity scours foundations.
```

ASCII:

```text
apparent multivariate hazard
   │
   ├─ can physics combine variables?
   │      └─ yes → one composite x-axis
   │
   ├─ do variables hit different parts?
   │      └─ yes → multiple univariate curves, summed
   │
   └─ neither escape works
          └─ true 2-D curve required
```

### V1 hazard x-axis map

| Hazard × asset | V1 x-axis treatment | Notes |
|---|---|---|
| Hail × solar | univariate on kinetic energy / MESH | count belongs to frequency, not severity |
| Strong wind / tornado × wind | univariate on 3-second gust | fatigue is cross-event/lifetime, not event damage |
| Flood × solar | split into depth and velocity curves | depth for electricals, velocity for foundation/scour |
| Wildfire × solar | univariate on fireline intensity for v1 | residence time is real but deferred 2-D extension |
| Hurricane × solar/wind | split wind + flood pathway | gust plus surge/rain/flood branch |
| Winter ice/snow × solar/wind | univariate on areal load | composite gravity load |

---

## 9. Chain-position rule: where the x-axis sits

The x-axis should be placed at the most downstream node that the hazard layer can actually deliver.

```text
UPSTREAM                                  DOWNSTREAM
hazard output → coupling → component stress → damage
```

Examples:

```text
hail:
stone kinetic energy → impact force → glass stress → damage

wildfire:
fireline intensity → heat flux → component temperature → damage

flood:
water depth → ingress / hydrostatic load → shorting → damage

wind:
gust → aerodynamic load → structural stress → damage
```

Rule:

```text
Use the most downstream variable the hazard data can actually provide.
Everything downstream of that variable is baked into the curve and its assumptions.
```

This prevents two opposite errors:

```text
Error A: choose a too-upstream axis and hide too much physics without labeling it
Error B: choose a too-downstream axis that the hazard layer cannot actually supply
```

---

## 10. Conditioners are not x-axes

The zip is very clear that asset state variables should not become extra x-axes.

```text
x-axis        = hazard intensity
conditioner  = asset state at event time
selector     = fixed asset attribute choosing the curve
```

Examples:

| Role | Example | Meaning |
|---|---|---|
| x-axis | hail kinetic energy | what the event did |
| conditioner | tracker stow angle | state during the event that changes vulnerability |
| selector | glass thickness | fixed attribute that selects or shifts curve |

ASCII:

```text
hazard intensity x
   │
   ▼
base curve DR(x)
   │
   ├─ shifted by conditioner: stow angle, prior damage, wet/dry state
   ├─ selected by attribute: glass thickness, tracker type, tower class
   └─ applied to value: value_i from valuation ledger
```

This is important because otherwise every damage curve explodes into many dimensions.

---

## 11. Curation: how a curve is derived

The fourth question doc says that curve-building should follow an evidence hierarchy.

```text
STRONGER
  empirical evidence
  analytical / physics evidence
  standards / certified ratings
  expert judgment
WEAKER
```

Most real curves will be hybrids, not pure empirical curves.

The derivation skeleton:

```text
A. Scope
   hazard, failure-unit, use case, physical-damage boundary

B. Define
   what DR means and what assumptions condition it

C. Evidence
   gather strongest available evidence, label each piece

D. Anchor
   use standards to fix no/low-damage regions

E. Bridge
   convert hazard output to component-relevant stress

F. Component behavior
   thresholds and damage mechanics

G. Aggregate
   sum weighted failure-unit responses

H. Form
   choose step / sigmoid / states / distribution by rule

I. Uncertainty
   name dominant uncertainty and update triggers
```

---

## 12. Standards are boundary conditions, not curves

A standard tells you something like:

```text
This component should survive up to this test condition.
```

It does not tell you:

```text
What happens above that condition?
What is the full loss curve?
What is the tail distribution?
```

ASCII:

```text
DR
│                                      saturation
│                                  ___/---------
│                              ___/
│                          ___/
│_________________________/
│        no/low damage
│        anchored by standard
└──────────────────────────────────────── intensity
                         rating threshold
```

Examples:

```text
IEC hail test      → anchors low/no-damage region for modules
ASCE wind rating   → anchors low/no-damage region for structures
IP ingress rating  → anchors threshold for water ingress
thermal ratings    → anchor no-damage temperature region
```

A standard is therefore a boundary condition, not the curve itself.

---

## 13. Functional form: climb only when evidence or use-case forces it

The curation guide rejects reflexively using a lognormal CDF just because the broader fragility literature often does.

The form ladder:

```text
[1] STEP / THRESHOLD
    simplest; useful when evidence is just a rated limit

[2] SMOOTH SIGMOID
    continuous mean curve; often emerges from aggregating many thresholds

[3] DISCRETE STATES
    natural when evidence gives probabilities of damage states

[4] FULL DISTRIBUTION
    richest; needed for strong tail work; hardest to source
```

Rule:

```text
Choose the simplest form the evidence yields and the use-case requires.
```

This is the same anti-overbuilding philosophy as the valuation work:

```text
do not source deeper than the model can use
```

---

## 14. Emit object: the first nonlinearity decides

The emit object is what the damage stage outputs per event, per failure-unit.

The key principle:

```text
A scalar mean is safe only through linear operations.
If a nonlinearity sits downstream, the model must carry spread/distribution.
```

The nonlinearities:

```text
N-cap    saturation at failure-unit cap
N-fin    deductibles / limits / financial terms
N-quant  quantile metrics such as VaR, PML, TVaR
```

ASCII:

```text
emit object
   │
   ├─ only sums and scalar multiplies?
   │      └─ scalar mean is okay for EAL
   │
   ├─ cap binds materially?
   │      └─ need spread for even EAL
   │
   ├─ financial terms apply?
   │      └─ need spread/distribution
   │
   └─ tail metric requested?
          └─ need distribution; scalar has no quantile
```

The v1 interface should be distribution-ready even if many v1 cells only emit scalar content.

```text
interface: distribution-capable
content: scalar where path is linear; spread/states/distribution where forced
```

---

## 15. Metrics: ship EAL where honest, withhold tail under scalar

The metrics doc makes the sharp distinction:

```text
EAL-class metrics  = means
Tail-class metrics = quantiles / tail integrals
```

A scalar can support EAL only when the path is effectively linear:

```text
cap rarely binds
no financial terms
known-answer check passes
```

A scalar cannot support VaR/PML/TVaR because a mean carries no quantile.

The shipping policy:

```text
                         cap rarely binds        cap binds materially
EAL-class                ship if checked          do not ship as scalar
Tail-class               withhold                 withhold
```

Important distinction:

```text
Do not caveat tail metrics under scalar.
Withhold them.
```

Reason:

```text
A caveated bad tail number still travels as a number.
A withheld number honestly signals that the spread is not sourced.
```

---

## 16. The final curve-record schema

The assembled record should carry at least these fields.

| Field | Meaning | Governed by |
|---|---|---|
| `cell` | hazard × asset pair | record key |
| `failure_unit` | unit curve applies to | doc 01 |
| `x_axis` | intensity variable | doc 02 |
| `chain_node` | where the axis sits on causal chain | doc 02 |
| `conditioners` | asset state variables modifying curve | doc 02 / parked component-depth |
| `selectors` | fixed attributes choosing or shifting curve | doc 02 / substrate |
| `value_share` | fraction of physical base | doc 03 / valuation workbook |
| `basis` | physical replaceable, TIV, etc. | doc 03 |
| `cap_L` | saturation cap from value share | doc 03 → doc 04 |
| `form` | step, sigmoid, states, distribution | doc 04 |
| `parameters` | curve parameters | doc 04 |
| `evidence_log` | parameter-level provenance | doc 04 |
| `anchors` | standards fixing curve regions | doc 04 |
| `bridge` | hazard-output to component-stress logic | doc 04 + doc 02 |
| `emit_object` | scalar, spread, states, distribution | doc 05 |
| `uncertainty` | spread drivers / confidence / validation status | doc 04 ↔ doc 05 |
| `metrics_shippable` | EAL/tail policy | doc 06 |
| `assembly_rule` | how records sum within cell | doc 01 / 00 |

Possible spreadsheet columns:

```text
record_id
tech
asset_class
hazard
cell
failure_unit
substrate_subsystem
substrate_component
parent_scope
curve_grain
x_axis
x_axis_units
chain_node
conditioners
selectors
value_basis
physical_value_share
at_risk_fraction
cap_L
curve_form
curve_parameters_json
evidence_class_primary
evidence_log
anchors
bridge_assumptions
emit_interface
emit_content_v1
cap_bind_check
metrics_shippable
known_answer_check
confidence_tier
open_seams
notes
```

---

## 17. Fill-order runbook

The second deliverable should be filled in dependency order.

```text
1. Pick hazard × asset cell
   e.g. hail × solar, wind × wind, flood × solar

2. Choose grain
   subsystem default, finer if concentration, split if distinct axis

3. Choose x-axis
   univariate, most-downstream hazard-delivered node

4. Attach value
   from valuation workbook; basis must be physical replaceable

5. Set cap
   cap_L = at-risk value share for that failure-unit

6. Curate curve
   evidence hierarchy, anchors, bridge, functional form

7. Decide emit object
   scalar where linear; spread/states/distribution where nonlinearities force

8. Decide shippable metrics
   EAL if checked; tail withheld unless spread/distribution exists

9. Reconcile cell
   all value covered once; immune/DR≈0 records kept explicitly
```

ASCII:

```text
hazard × asset
   │
   ▼
choose failure-unit grain
   │
   ▼
choose x-axis + chain node
   │
   ▼
attach value + cap
   │
   ▼
curate curve + provenance
   │
   ▼
decide emit object
   │
   ▼
declare shippable metrics
   │
   ▼
cell assembly: Σ DR_i(x_i) × value_i
```

---

## 18. Worked skeleton: hail × solar module

This is the zip’s clearest example.

```text
cell:             hail × solar
failure_unit:     module / glass-cells unit inside PV_ARRAY
x_axis:           kinetic energy or MESH-equivalent
chain_node:       hazard-output node
value_share:      from PV_ARRAY/module value allocation
basis:            physical replaceable
cap_L:            module at-risk value share
form:             smooth sigmoid likely, because thresholds aggregate
anchors:          IEC hail test anchors low/no-damage region
evidence:         claims/empirical + lab standard + KE physics
emit:             scalar for EAL if cap rarely binds; spread needed for tail
metrics:          EAL shippable if checked; VaR/PML withheld under scalar
```

ASCII:

```text
hail size / speed / density
          │
          ▼
 kinetic energy / MESH
          │
          ▼
 module damage curve DR(KE)
          │
          ▼
 DR × module at-risk value
          │
          ▼
 hail loss dollars
```

---

## 19. Worked skeleton: flood × solar

Flood looks multivariate at the asset level, but the docs argue it should split at the unit level.

```text
asset-level impression:
DR_asset = f(depth, velocity)
```

Resolved version:

```text
DR_electrical(depth)   × electrical below-waterline value
+
DR_foundation(velocity) × foundation/scour-exposed value
+
DR_immune              × elevated/dry value
```

ASCII:

```text
flood event
   │
   ├─ water depth
   │     └─ electrical ingress / shorting curve
   │
   ├─ flow velocity
   │     └─ foundation / scour curve
   │
   └─ dry/elevated components
         └─ DR≈0 record
```

This is the key example where apparent 2-D complexity becomes multiple 1-D curves.

---

## 20. Worked skeleton: wind × wind turbine

For event damage, the x-axis is gust, not fatigue duration.

```text
cell:             strong wind / tornado × wind
failure_units:    rotor, nacelle, tower, power electronics, etc.
x_axis:           3-second gust
form:             standards/analytical-led, possibly saturation at extreme intensities
basis:            physical replaceable value from wind valuation ledger
emit:             scalar for EAL if cap rarely binds; spread needed for tail
```

ASCII:

```text
3-second gust
   │
   ├─ rotor aerodynamic load → blade / hub damage
   ├─ tower structural load  → tower damage
   ├─ nacelle exposure       → nacelle damage
   └─ balance-of-plant       → separate curves or DR≈0
```

Fatigue is not ignored; it is classified as cross-event/lifetime/disruption-side rather than per-event physical damage.

---

## 21. Worked skeleton: wildfire × solar

Wildfire has one real deferred complexity: residence time.

V1:

```text
x_axis: fireline intensity
curve: univariate
residence time: documented wall / deferred 2-D extension
```

Future extension:

```text
DR = f(fireline intensity, residence time)
```

ASCII:

```text
fireline intensity
   │
   ▼
heat flux / component temperature assumptions
   │
   ▼
component damage curve
   │
   ▼
loss = DR × exposed physical value

known deferred wall:
fireline intensity × residence time may be needed later
```

This is not denial of the second axis. It is a deliberate v1 boundary.

---

## 22. What not to do in the next deliverable

The zip repeatedly warns against several tempting mistakes.

### Mistake 1 — Build a new failure-unit primitive

Unless joint loss is not equal to the sum of marginal losses, do not create a grouping object.

```text
cross-cutting geometry ≠ required grouping primitive
```

### Mistake 2 — Build multivariate curves too early

Most apparent multi-axis damage dissolves into either:

```text
one composite scalar
```

or:

```text
several univariate curves on different parts
```

### Mistake 3 — Treat standards as full curves

A rating threshold anchors a region. It does not define the shape above the threshold.

### Mistake 4 — Emit scalar tail metrics

A scalar mean has no quantile. Tail metrics under scalar should be withheld, not caveated.

### Mistake 5 — Lose the basis label

Every loss percentage needs a denominator:

```text
% of physical replaceable base?
% of installed capex?
% of insured TIV?
```

### Mistake 6 — Drop immune rows

If a subsystem has value but DR≈0 for the hazard, keep it. It is needed for reconciliation.

---

## 23. Open seams we should carry explicitly

The zip identifies several genuine unresolved seams. These should be carried as fields or notes, not hidden.

| Open seam | Why it matters | How to handle in deliverable |
|---|---|---|
| Spread / uncertainty source | Needed for tail metrics and cap-binding checks | include `uncertainty_status`, `spread_source`, `tail_available` |
| Cap-binding check | Scalar EAL is safe only if cap rarely binds | include `cap_bind_check` and `known_answer_check` |
| Wildfire residence time | real deferred 2-D case | include `deferred_axis` / `v1_limitation` |
| Flood duration / corrosion | weak evidence, may be maintenance/disruption | flag as open assumption |
| State-to-cost map | needed for fragility-state curves | include if `form = states` |
| Financial terms | deductibles/limits are nonlinear and out of v1 | mark `gross_only_v1` |
| Component-depth attributes | stow angle, glass thickness, prior damage | track as conditioners/selectors, not axes |
| Cascade/interactions | one possible future reason for grouping | keep parked unless joint≠sum appears |

---

## 24. Recommended shape of the next actual deliverable

The next deliverable should probably be an Excel workbook plus a companion Markdown guide, similar to the valuation work.

### Workbook

Suggested sheets:

| Sheet | Purpose |
|---|---|
| `README` | scope, definitions, warnings |
| `Record_Schema` | field dictionary for curve records |
| `Cell_Index` | hazard × asset cells included |
| `Curve_Records` | one row per hazard × failure-unit |
| `Value_Link` | link from curve records to valuation workbook value buckets |
| `Evidence_Log` | parameter-level source/provenance evidence |
| `Anchors` | standards / ratings used as boundary conditions |
| `X_Axis_Map` | hazard x-axis choices and chain node |
| `Emit_Metrics` | emit object and shippable metrics by record |
| `Examples` | worked cells: hail×solar, flood×solar, wind×wind, wildfire×solar |
| `Open_Seams` | explicit unresolved seams and revisit triggers |

### Companion Markdown

Suggested document:

```text
supporting_damage_curve_record_guide.md
```

Contents:

```text
1. What the curve record is
2. Why it is per failure-unit, not one asset curve
3. How it plugs into valuation
4. Grain rules
5. X-axis rules
6. Curation/evidence rules
7. Emit object rules
8. Metrics honesty rules
9. Worked examples
10. Build checklist
```

---

## 25. The one-sentence stabilized mental model

```text
The second deliverable is a provenance-carrying damage-curve record library: one record per hazard × failure-unit, using the substrate as vocabulary, the valuation workbook as the value/cap ledger, univariate x-axes by default, evidence-class-labeled curve derivation, distribution-ready emit schema, and a metric policy that ships EAL only where scalar is honest while withholding tail metrics unless spread is sourced.
```

---

## 26. Practical next step

Before sourcing any actual curve numbers, define the workbook schema and choose the first cells to populate. A good initial scope would be:

```text
1. hail × solar
2. wind / tornado × wind
3. flood × solar
4. wildfire × solar
```

These four cells exercise almost every rule in the zip:

```text
hail      → concentration + composite x-axis + standards anchor
wind      → structural loading + gust x-axis + cap/saturation concern
flood     → split axes + geometry-based at-risk fractions
wildfire  → chain-position rule + deferred residence-time wall
```

That set would produce a useful first curve-record workbook without pretending to solve the full model universe.
