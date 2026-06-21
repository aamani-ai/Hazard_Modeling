# Supporting Evaluation Guide  
## Financial valuation vs physical-damage valuation for solar and wind assets

**Purpose:** This guide explains the two different meanings of “valuation” that can appear when we talk about energy assets. One meaning is the normal **financial / investment valuation** of the project as a business. The other is the **physical-damage / insurance valuation** used to calculate hazard losses. The second one is the more important basis for `loss = damage ratio × value`.

This guide is meant to support the valuation workbook and the engineering substrate work. It is not a replacement for the value table. It explains the mental model, the basis choices, the plant/generator hierarchy, and how dollar values should be assigned to subsystems and components.

---

## 0. The one-line distinction

```text
FINANCIAL VALUATION
= What is the asset worth as a cash-flowing business?

PHYSICAL-DAMAGE VALUATION
= What physical equipment exists, and what would it cost to repair or replace after damage?
```

For hazard loss modeling, we usually need the second one.

A solar or wind project can be valuable because of its PPA, tax credits, market position, interconnection rights, or development scarcity. But a hailstorm, wildfire, flood, or wind event does not directly “break” the PPA value or the tax-credit value. It breaks physical things: modules, blades, inverters, towers, transformers, cables, foundations, roads, drainage, and controls.

So the relevant question becomes:

> **If a hazard damages part of the asset, what dollar base should the damage ratio apply to?**

---

## 1. The two valuation worlds

```text
FINANCIAL / INVESTMENT VALUATION
"What is this asset worth as a business?"

    future cash flows
    merchant revenue
    PPA revenue
    capacity revenue
    tax credits
    debt / equity structure
    terminal value
    buyer appetite
    scarcity value
          │
          ▼
    enterprise value / equity value / market value


PHYSICAL / INSURANCE VALUATION
"What physical thing exists, and what would it cost to repair or replace?"

    modules
    trackers / racking
    blades
    nacelle
    tower
    inverter / converter
    transformer
    switchgear
    cabling
    foundations
    roads / drainage
    SCADA / controls
          │
          ▼
    replacement value / insured value / physical damage base / TIV
```

Both are valid. They answer different questions.

| Evaluation type | Main question | Typical output | Main users | Good for hazard loss? |
|---|---|---|---|---|
| **Financial / investment valuation** | What is the project worth to an owner, buyer, lender, or investor? | Enterprise value, equity value, fair market value, DCF value | Investors, lenders, M&A teams, developers | Not directly |
| **Physical-damage / insurance valuation** | What physical equipment can be damaged, and what does it cost to repair or replace? | Replacement cost, physical TIV, insured schedule, subsystem value ledger | Insurers, brokers, risk engineers, asset owners | Yes |

The mistake is treating them as interchangeable.

---

## 2. Why this matters for `loss = DR × value`

At first, the loss formula looks simple:

```text
loss = DR × value
```

Where:

- `DR` = damage ratio
- `value` = dollar value exposed to that damage

But the word `value` hides three separate decisions.

```text
   loss = DR × value
                 │
                 ├─ 1. BASIS / DENOMINATOR
                 │    "Value of what?"
                 │    Installed capex? Replacement cost? Insured TIV?
                 │    Physical replaceable base? Market value?
                 │
                 ├─ 2. ALLOCATION
                 │    "Which subsystem owns what share of the value?"
                 │    PV array? Inverter? Rotor? Nacelle? Tower? Substation?
                 │
                 └─ 3. AT-RISK FRACTION
                      "Within that subsystem, what part is actually exposed to this hazard?"
                      Hail-exposed module glass? Below-waterline equipment? Blades?
```

These are not the same kind of number.

- **Basis** is the denominator.
- **Allocation** is the value split across subsystems/components.
- **At-risk fraction** is the hazard-specific exposed slice of a subsystem/component.

A lot of bad loss modeling comes from mixing these three.

---

## 3. Simple intuition: the house analogy

Imagine someone buys a house for **$1,000,000**.

```text
$1,000,000 purchase price
├─ $650,000 physical structure
│  ├─ roof
│  ├─ walls
│  ├─ plumbing
│  ├─ electrical
│  └─ HVAC
├─ $250,000 land
└─ $100,000 soft / transaction / sunk costs
   ├─ closing costs
   ├─ legal fees
   ├─ broker fees
   └─ financing costs
```

Now a hailstorm damages the roof by 50%.

Bad calculation:

```text
loss = 50% × total purchase price
     = 50% × $1,000,000
     = $500,000
```

That is wrong because hail did not damage the land, legal fees, broker fees, financing costs, plumbing, walls, or HVAC.

Better calculation:

```text
loss = 50% × roof replacement value
```

The same principle applies to solar and wind assets.

```text
TOTAL INSTALLED CAPEX
├─ physical replaceable value       ← hazard can damage this
│  ├─ modules / blades / towers
│  ├─ inverter / converter
│  ├─ transformer / switchgear
│  ├─ cabling / collection system
│  ├─ foundations / roads / drainage
│  └─ SCADA / controls
└─ sunk / soft / nonphysical value  ← hazard usually cannot "repair" this
   ├─ development cost
   ├─ engineering and permitting
   ├─ financing cost
   ├─ interconnection / network upgrades
   ├─ owner's costs
   └─ transaction / legal / advisory costs
```

For physical damage, the honest denominator is usually the **physical replaceable base**, not the full installed capex or investment value.

---

## 4. Basis: the denominator problem

A **basis** is the dollar denominator you are using.

Same asset. Different valid bases.

| Basis | Intuition | Good for | Danger if misused |
|---|---|---|---|
| **Original installed capex** | What was paid to build the project originally | Historical project cost, EPC comparison | Includes soft/sunk costs that may not be physically damageable |
| **Replacement cost new** | What it would cost to rebuild the asset today | Insurance and physical damage | May differ from original capex due to inflation/deflation |
| **Physical replaceable base** | Only the physical, repairable/replaceable portion | Clean hazard loss modeling | Requires stripping or parking soft/sunk/nonphysical costs |
| **Insured TIV** | What the insurance policy declares as insured value | Policy analytics and claims comparison | May be scheduled differently than engineering replacement value |
| **Book value** | Accounting value after depreciation | Financial statements | Not a physical damage basis |
| **Fair market value** | What a buyer would pay | M&A / transaction analysis | Includes cash-flow and market expectations |
| **Enterprise value** | DCF / business value | Investor valuation | Can be much higher or lower than replacement value |

The dangerous sentence is:

> “The loss is 5% of asset value.”

That is incomplete. We need to ask:

> “5% of which value basis?”

Example:

```text
Same physical loss = $10M

$10M / $100M installed capex          = 10.0%
$10M / $80M physical replaceable base = 12.5%
$10M / $60M insured TIV               = 16.7%
$10M / $150M market value             = 6.7%
```

Same damage. Four different percentages.

All four can be mathematically correct, but they mean different things. This is why every value share needs a **basis label**.

---

## 5. Installed capex vs physical replaceable value

This is one of the most important distinctions.

### 5.1 Installed capex

Installed capex answers:

> **What did it cost to get this project built and operational?**

It includes physical equipment plus everything required to make the project happen.

```text
INSTALLED CAPEX
├─ physical equipment
├─ physical construction labor
├─ EPC margin
├─ development cost
├─ engineering
├─ permitting
├─ financing / interest during construction
├─ interconnection / network upgrades
├─ owner's cost
└─ contingency / warranty / insurance / fees
```

Installed capex is useful. But it is not automatically the right denominator for physical hazard damage.

### 5.2 Physical replaceable value

Physical replaceable value answers:

> **What physical things would need to be repaired or replaced after damage?**

```text
PHYSICAL REPLACEABLE VALUE
├─ modules / blades / turbines
├─ racking / towers / foundations
├─ inverters / converters
├─ transformers / switchgear
├─ cabling / collection system
├─ SCADA / monitoring equipment
├─ roads / civil works, if damaged
└─ drainage / flood defense, if damaged
```

Physical replaceable value is generally the better denominator for physical damage ratios.

### 5.3 Sunk / soft / nonphysical slice

Soft and sunk costs can be economically real, but not physically repairable after a hazard.

```text
SUNK / SOFT / NONPHYSICAL VALUE
├─ development cost
├─ permitting
├─ financing
├─ legal
├─ advisory
├─ interconnection/network upgrades, depending on basis
├─ transaction costs
└─ tax structuring / owner overhead
```

For physical damage modeling, these should usually be represented as explicit `DR ≈ 0` or nonphysical slices, not silently left inside the denominator.

---

## 6. Cost share vs value share vs at-risk share

These terms sound similar, but they are different.

| Concept | Question | Example |
|---|---|---|
| **Cost share** | What share of original capex was spent here? | Modules were 30% of installed capex |
| **Value share** | What share of the physical replaceable base sits here? | PV array is 40% of physical value |
| **At-risk share** | What share is exposed to this hazard mechanism? | Only module glass/cells are hail-exposed |
| **Damage ratio** | Given the hazard, how damaged is that exposed thing? | Hail causes 25% module damage |
| **Loss** | What dollars are lost? | 25% × exposed module value |

A useful formula is:

```text
loss_hazard = Σ [ damage_ratio_c × value_c × at_risk_fraction_c,hazard ]
```

Or more intuitively:

```text
hazard intensity
      │
      ▼
damage curve
      │
      ▼
damage ratio
      │
      ▼
apply only to the exposed dollar bucket
      │
      ▼
loss dollars
```

The key rule:

```text
cost share ≠ value share ≠ at-risk share
```

Capex tells us what was paid. It does not automatically tell us what is physically at risk for a specific hazard.

---

## 7. The asset hierarchy: plant → generator → subsystem → component

For the engineering substrate, the asset is decomposed like this:

```text
plant / generator
  └─ SUBSYSTEM
        └─ COMPONENT
```

The hierarchy matters because not every dollar belongs directly to a generator. Some dollars belong to shared plant infrastructure.

```text
Plant / project
├─ shared plant-scope assets
│  ├─ substation
│  ├─ switchyard
│  ├─ SCADA
│  ├─ roads
│  ├─ fencing
│  ├─ drainage
│  └─ interconnection facilities
│
├─ Generator 1: solar PV
│  ├─ PV modules
│  ├─ trackers / racking
│  ├─ inverters
│  └─ DC cabling
│
└─ Generator 2: BESS, wind, or another unit
   ├─ battery packs / turbines / thermal unit
   ├─ converter / nacelle / boiler
   └─ technology-specific equipment
```

### Plant-scope

Plant-scope means shared across the plant.

Examples:

- substation
- switchgear
- SCADA
- roads
- civil infrastructure
- drainage
- fire protection
- grounding and lightning protection
- auxiliary power

### Generator-scope

Generator-scope means specific to a generating technology or unit.

Examples:

- solar PV array
- solar mounting / trackers
- solar inverter system
- wind rotor assembly
- wind nacelle
- wind tower
- wind pitch system
- BESS battery packs
- thermal boiler / turbine systems

This distinction is not just technical. It controls where value sits and how losses should be allocated.

---

## 8. Solar example: engineering anatomy and value buckets

### 8.1 Solar engineering decomposition

```text
solar generator
├─ PV_ARRAY              [generator-scope]
│  └─ PV_MODULE
├─ MOUNTING              [generator-scope]
│  └─ FIXED_MOUNT or TRACKER
│  └─ RACKING_STRUCTURE
├─ INVERTER_SYSTEM       [generator-scope]
│  └─ INVERTER
│  └─ COMBINER_BOX
│  └─ DC_PROTECTION
│
└─ shared plant assets
   ├─ SUBSTATION
   ├─ ELECTRICAL_COLLECTION
   ├─ SCADA
   ├─ CIVIL_INFRA
   ├─ FOUNDATION
   ├─ FIRE_PROTECTION
   ├─ GROUNDING_LIGHTNING
   ├─ AUXILIARY_POWER
   └─ SITE_DRAINAGE
```

### 8.2 Solar value ledger intuition

```text
SOLAR PHYSICAL REPLACEABLE BASE
├─ PV_ARRAY
│  └─ modules
├─ MOUNTING
│  ├─ trackers or fixed-tilt structure
│  └─ racking
├─ INVERTER_SYSTEM
│  ├─ inverters
│  ├─ combiner boxes
│  └─ DC protection
├─ ELECTRICAL_COLLECTION
│  ├─ AC/DC cabling
│  └─ collection equipment
├─ SUBSTATION
│  ├─ transformer
│  └─ switchgear
├─ SCADA / controls
├─ CIVIL_INFRA / roads / fencing
├─ FOUNDATION / piles
└─ SITE_DRAINAGE / flood defense
```

### 8.3 Solar hail example

Assume:

```text
100 MWdc solar plant
Installed capex = $112M
Physical replaceable base = $88M
Sunk / soft / nonphysical = $24M
PV array value = $35M
```

A hail event damages modules.

Bad calculation:

```text
loss = 30% × $112M
     = $33.6M
```

This applies module damage to the whole project, including inverters, substation, civil works, soft costs, development costs, and financing.

Better calculation:

```text
loss = 30% × PV_ARRAY value
     = 30% × $35M
     = $10.5M
```

Even better if only part of the PV array value is directly exposed to hail:

```text
loss = DR_module × PV_ARRAY value × f_hail
```

If:

```text
PV array value = $35M
hail damage ratio = 30%
at-risk fraction = 90%
```

Then:

```text
loss = 30% × $35M × 90%
     = $9.45M
```

Reporting:

```text
loss dollars                       = $9.45M
% of physical replaceable base      = $9.45M / $88M  = 10.7%
% of installed capex                = $9.45M / $112M = 8.4%
```

Both percentages are valid only if their basis is clearly labeled.

---

## 9. Wind example: engineering anatomy and value buckets

### 9.1 Wind engineering decomposition

```text
wind generator
├─ ROTOR_ASSEMBLY        [generator-scope]
│  ├─ BLADE
│  └─ HUB
├─ NACELLE               [generator-scope]
│  ├─ GEARBOX
│  ├─ GENERATOR_INTERNAL
│  └─ YAW_SYSTEM
├─ TOWER                 [generator-scope]
│  └─ TOWER_SECTION
├─ POWER_ELECTRONICS     [generator-scope]
│  └─ POWER_CONVERTER
├─ PITCH_SYSTEM          [generator-scope]
│  └─ PITCH_DRIVE
├─ BRAKE_SYSTEM          [generator-scope]
│  └─ MECHANICAL_BRAKE
├─ ICE_PROTECTION        [generator-scope]
│  └─ ICE_MITIGATION
│
└─ shared plant assets
   ├─ FOUNDATION
   ├─ SUBSTATION
   ├─ ELECTRICAL_COLLECTION
   ├─ SCADA
   ├─ CIVIL_INFRA
   ├─ FIRE_PROTECTION
   ├─ GROUNDING_LIGHTNING
   ├─ AUXILIARY_POWER
   └─ SITE_DRAINAGE
```

### 9.2 Wind value ledger intuition

```text
WIND PHYSICAL REPLACEABLE BASE
├─ ROTOR_ASSEMBLY
│  ├─ blades
│  └─ hub
├─ NACELLE
│  ├─ gearbox or direct-drive system
│  ├─ generator
│  └─ yaw system
├─ TOWER
│  └─ tower sections
├─ POWER_ELECTRONICS
│  └─ converter
├─ PITCH_SYSTEM
├─ BRAKE_SYSTEM
├─ FOUNDATION
├─ ELECTRICAL_COLLECTION
├─ SUBSTATION
├─ SCADA / controls
└─ CIVIL_INFRA / roads / crane pads / drainage
```

### 9.3 Wind blade damage example

Assume:

```text
200 MW wind project
Installed capex = $394M
Physical replaceable base = $325M
Sunk / soft / nonphysical = $69M
Rotor assembly value = $70M
Blade share within rotor = 75%
```

An extreme wind event damages blades.

Bad calculation:

```text
loss = blade damage ratio × whole project capex
```

Better calculation:

```text
loss = blade damage ratio × blade value
```

If we only know rotor-level value, use an at-risk/component share:

```text
loss = damage ratio × ROTOR_ASSEMBLY value × blade_share_within_rotor
```

If:

```text
ROTOR_ASSEMBLY value = $70M
blade share within rotor = 75%
damage ratio = 40%
```

Then:

```text
loss = 40% × $70M × 75%
     = $21M
```

This is why component detail is valuable only where the hazard mechanism actually concentrates. We do not need infinite component detail for every bolt, sensor, bearing, and cable if the damage model does not consume that resolution.

---

## 10. The value ledger concept

The cleanest way to think about physical-damage valuation is as a **ledger**.

```text
ASSET VALUE LEDGER

Total stated basis
├─ Physical replaceable value
│  ├─ subsystem A
│  │  ├─ component A1
│  │  └─ component A2
│  ├─ subsystem B
│  │  ├─ component B1
│  │  └─ component B2
│  └─ subsystem C
│
├─ Immune / low-damage physical value
│  └─ value exists, but DR ≈ 0 for this hazard
│
└─ Sunk / soft / nonphysical value
   └─ value exists in capex, but is not physically repaired
```

The reconciliation rule:

```text
physical subsystem shares
+ immune / DR≈0 slices
+ sunk / soft / nonphysical slices
= stated basis
```

If the ledger does not sum to 100%, something is missing or double-counted.

---

## 11. Shared plant assets: the common allocation problem

Shared assets are where valuation gets tricky.

Example: hybrid solar + BESS plant.

```text
Plant total physical value
├─ Solar-specific value
│  ├─ modules
│  ├─ racking
│  └─ solar inverters
├─ BESS-specific value
│  ├─ battery containers
│  ├─ PCS
│  └─ BMS
└─ Shared value
   ├─ substation
   ├─ SCADA
   ├─ roads
   ├─ fencing
   └─ drainage
```

Now suppose a flood damages the substation.

Is that solar loss? BESS loss? Plant loss?

It depends on the reporting lens.

| Lens | Treatment |
|---|---|
| **Asset-level loss** | Count full substation loss once |
| **Generator-level loss** | Allocate shared substation loss across solar/BESS |
| **Insurance policy loss** | Follow the insured schedule / TIV categories |
| **Reliability impact** | Allocate based on which generators are knocked offline |
| **Replacement cost** | Count actual damaged physical equipment |

This is why `plant-scope` vs `generator-scope` matters.

```text
Same damaged transformer
        │
        ├─ Asset-level view: one plant loss
        ├─ Generator-level view: allocated to affected generators
        ├─ Insurance view: follows schedule of values
        └─ Operational view: affects all generation behind it
```

---

## 12. Hazard-specific at-risk fractions

The at-risk fraction `f` is not one universal column. It is hazard-specific.

```text
value_c = subsystem or component value
f_c,h  = fraction of that value exposed to hazard h
DR_c,h = damage ratio from hazard h

loss_c,h = DR_c,h × value_c × f_c,h
```

Examples:

| Hazard | At-risk fraction type | Example |
|---|---|---|
| **Hail** | Material/component share | Module glass/cells within PV array |
| **Flood** | Site geometry/elevation | Equipment below waterline or below flood depth |
| **Wildfire** | Exposure/intensity zone | Equipment inside heat/smoke/ember zone |
| **Extreme wind** | Structural exposure | Blades, trackers, towers, racking, roof-mounted equipment |
| **Lightning** | Protection/electrical exposure | Converter, inverter, transformer, SCADA, grounding/lightning system |
| **Ice** | Cold-climate turbine exposure | Blades, pitch system, ice mitigation equipment |

The key insight:

```text
hail f      = material/component share
flood f     = geometry/elevation share
wildfire f  = exposure/intensity share
wind f      = structural/mechanical exposure share
```

So we should not build one generic `f` column and pretend it means the same thing across hazards.

---

## 13. End-to-end physical loss workflow

```text
1. Define asset
   └─ technology, size, location, configuration

2. Decompose asset
   └─ plant → generator → subsystem → component

3. Choose basis
   └─ installed capex?
      replacement cost?
      insured TIV?
      physical replaceable base?

4. Split basis
   └─ physical replaceable
      sunk / soft / nonphysical
      immune or low-damage slices

5. Allocate physical value
   └─ subsystem shares
      component shares where useful

6. Apply hazard-specific exposure logic
   └─ hail: module glass/cells
      wind: blades/tower/tracker stow
      flood: below-waterline equipment
      wildfire: exposed physical equipment

7. Apply damage curves
   └─ damage ratio by component/subsystem

8. Calculate loss
   └─ dollars
      % physical base
      % installed capex
      % insured TIV
      EAL / PML / VaR / TVaR as needed
```

Another view:

```text
                 FINANCIAL PROJECT VALUE
          "What is this asset worth as a business?"
                             │
                             │  not the main object for physical damage
                             ▼

                  STATED ASSET BASIS
        installed capex / replacement / TIV / insured
                             │
                             ▼
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
PHYSICAL REPLACEABLE BASE                SUNK / SOFT / NONPHYSICAL
"can be damaged/repaired"                "paid once / not physically repaired"
        │                                         │
        ▼                                         ▼
 plant + generator subsystems             DR ≈ 0 for physical hazard
        │
        ▼
 components where useful
        │
        ▼
 hazard-specific exposed fraction
        │
        ▼
 damage ratio from curve
        │
        ▼
 LOSS DOLLARS
```

---

## 14. Recommended dataset structure

A good value dataset should not just contain `subsystem` and `value_share`. It should carry provenance, basis, and hazard exposure logic.

Recommended columns:

| Field | Meaning |
|---|---|
| `tech` | solar, wind, bess, thermal |
| `asset_id` | optional asset-level identifier |
| `scope` | plant or generator |
| `generator_id` | optional if the plant has multiple generators |
| `subsystem_code` | PV_ARRAY, INVERTER_SYSTEM, ROTOR_ASSEMBLY, NACELLE, etc. |
| `component_code` | optional component-level code, if used |
| `basis` | physical_replaceable, installed_capex, insured_tiv, replacement_cost_new, etc. |
| `basis_value_usd` | total denominator value |
| `value_share` | share of the stated basis |
| `value_usd` | dollar value allocated to this row |
| `physical_flag` | physical, soft_sunk, nonphysical, immune_physical |
| `hazard_applicability` | which hazards can affect this row |
| `at_risk_f` | hazard-specific exposure fraction, if applicable |
| `f_kind` | material_share, site_geometry, exposure_zone, n/a |
| `source` | source used for value split |
| `vintage` | source year / benchmark year |
| `trust_tier` | high, medium, placeholder, asset_specific |
| `override_flag` | generic default vs asset-specific override |
| `notes` | basis caveats and mapping assumptions |

The dataset should satisfy this rule:

```text
Σ physical rows + Σ immune rows + Σ soft/sunk/nonphysical rows = stated basis
```

And for the physical-damage model:

```text
loss = Σ_c DR_c,h × value_c × f_c,h
```

---

## 15. What the current substrate gives us vs what valuation adds

The engineering substrate gives us the **vocabulary**.

```text
substrate decomposition
= what the asset is made of
= how subsystems and components are named
= which components belong under each subsystem
= which subsystems are plant-scope vs generator-scope
```

The valuation layer gives us the **dollars**.

```text
valuation layer
= which basis we are using
= how total value is split
= what share is physical vs soft/sunk
= which subsystem/component has which dollar value
= which hazard can touch which value bucket
```

Together:

```text
ENGINEERING SUBSTRATE                  VALUATION LAYER
"What exists?"                         "What is it worth on this basis?"

plant / generator                      basis
  └─ subsystem                         physical vs soft/sunk
      └─ component                     value share
                                       value dollars
                                       source / vintage / trust
                                       hazard-specific at-risk fraction

                 │
                 ▼
          LOSS MODEL
          DR × exposed value
```

This separation is healthy. The substrate should not silently embed uncertain value weights as if they are engineering facts. The valuation layer should be explicit, sourced, and overridable.

---

## 16. Common mistakes and how to avoid them

| Mistake | Why it is wrong | Better discipline |
|---|---|---|
| Applying a component damage ratio to total project value | Overstates loss by applying damage to unrelated value buckets | Apply DR only to exposed subsystem/component value |
| Reporting `% of asset value` without a basis | Ambiguous and potentially misleading | Always say `% of physical base`, `% of installed capex`, or `% of insured TIV` |
| Leaving soft/sunk costs inside the physical damage denominator | Makes physical loss ratios look artificially low | Split physical and nonphysical value explicitly |
| Treating cost share as at-risk share | Capex share does not equal hazard exposure | Add hazard-specific at-risk fraction where needed |
| Over-decomposing beyond damage model resolution | Creates false precision | Source values only to the grain the damage model consumes |
| Dropping immune assets from the ledger | Breaks reconciliation and understates total basis | Keep immune/DR≈0 slices explicitly |
| Double-counting shared plant assets | Inflates generator-level losses | Allocate plant-scope assets carefully or keep plant-level loss separate |
| Mixing AC and DC denominators for solar | Solar $/kWdc and $/kWac differ materially | Normalize units before comparing or allocating |
| Comparing wind and solar capex without basis normalization | Sources may include/exclude interconnection differently | Label and normalize basis before cross-tech comparison |
| Using book value for physical damage | Depreciated accounting value may not reflect repair cost | Use replacement or physical replaceable value for hazard loss |

---

## 17. How to explain this internally

A clean internal phrasing:

> We are not trying to value the project as an investment. We are building a physical-damage value ledger. The asset is decomposed into plant-scope and generator-scope subsystems, then into components where needed. For every dollar bucket, we label the basis: installed capex, replacement cost, insured TIV, or physical replaceable value. For physical hazard loss, the clean denominator is the physical replaceable base, not total installed capex, because soft/sunk costs like development, financing, and interconnection are not physically repaired after a hazard. Then each hazard applies damage ratios only to the exposed subsystem/component value, with at-risk fractions used where the damage mechanism concentrates.

Even shorter:

```text
Basis tells us the denominator.
Allocation tells us where the dollars sit.
At-risk fraction tells us which dollars the hazard can touch.
Damage ratio tells us how much of that exposed value is lost.
```

---

## 18. Solar and wind side-by-side

| Topic | Solar | Wind |
|---|---|---|
| Main generator-scope physical value | PV array, mounting, inverter system | rotor, nacelle, tower, converter, pitch/brake systems |
| Shared plant value | substation, collection, SCADA, civil, drainage, grounding | substation, collection, SCADA, civil, foundations, drainage, grounding |
| Common concentrated hazards | hail on modules, wind on trackers/racking, flood on electrical equipment, wildfire | extreme wind on blades/tower, lightning on electronics, fire in nacelle, ice on blades |
| Important denominator nuance | DC vs AC capacity; soft/interconnection costs may be embedded in some cost buckets | turbine vs BOS vs soft; interconnection may be excluded depending on source |
| Component detail needed? | Only where hazard concentrates, e.g., module glass/cells for hail | Only where hazard concentrates, e.g., blades within rotor, gearbox/generator where relevant |
| Good default grain | subsystem level plus limited component fractions | subsystem level plus limited component fractions |

---

## 19. Example: same physical loss, different reporting bases

Suppose a solar event creates a **$9.45M** physical loss.

```text
Installed capex = $112M
Physical replaceable base = $88M
Insured TIV = $95M
Market value = $140M
```

Then:

| Reporting basis | Calculation | Reported ratio |
|---|---:|---:|
| Physical replaceable base | $9.45M / $88M | 10.7% |
| Installed capex | $9.45M / $112M | 8.4% |
| Insured TIV | $9.45M / $95M | 9.9% |
| Market value | $9.45M / $140M | 6.8% |

The loss dollars are the same. The percentage changes because the denominator changes.

This is why basis labeling is not a minor accounting detail. It controls every `% of TIV`, `% of asset value`, and severity metric.

---

## 20. Decision tree for choosing the right valuation basis

```text
What question are we answering?

├─ What is the project worth to buy/sell/finance?
│      └─ Use financial valuation
│         ├─ DCF / market value / enterprise value
│         └─ revenue, PPA, tax credits, financing, terminal value
│
├─ What would it cost to rebuild the whole physical asset today?
│      └─ Use replacement cost new
│
├─ What physical denominator should a hazard damage ratio use?
│      └─ Use physical replaceable base
│         ├─ strip/park soft and sunk costs
│         └─ allocate to subsystems/components
│
├─ What does the insurance policy cover?
│      └─ Use insured TIV / schedule of values
│         ├─ follow policy categories
│         └─ compare modeled losses to limits/deductibles
│
└─ What is the accounting value?
       └─ Use book value
          └─ not recommended for physical damage severity
```

---

## 21. Practical checklist before using a value number

Before using any value share or dollar value in a loss model, ask:

```text
[ ] What is the basis? Installed capex, replacement cost, physical base, insured TIV, or market value?
[ ] Is this value physical, soft/sunk, nonphysical, or immune/low-damage?
[ ] Is it plant-scope or generator-scope?
[ ] Which subsystem owns the value?
[ ] Do we need component-level detail for this hazard, or is subsystem grain enough?
[ ] Is there an at-risk fraction f? If yes, what kind: material share, site geometry, or exposure zone?
[ ] Does the ledger reconcile to 100% of the stated basis?
[ ] Are shared plant assets counted once, not double-counted across generators?
[ ] Is the source vintage appropriate?
[ ] Is this a generic default or an asset-specific override?
```

---

## 22. Final mental model

```text
FINANCIAL VALUE
    tells you what the project is worth as a business.

PHYSICAL VALUE
    tells you what physical equipment can be damaged.

BASIS
    tells you the denominator.

ALLOCATION
    tells you where the dollars sit.

AT-RISK FRACTION
    tells you which part of those dollars the hazard can touch.

DAMAGE RATIO
    tells you how much of the exposed value is lost.

LOSS
    is the final dollar result.
```

The clean physical-damage equation is:

```text
loss_h = Σ_c DR_c,h × value_c,basis × f_c,h
```

Where:

- `h` = hazard
- `c` = component or subsystem
- `DR_c,h` = damage ratio for component/subsystem `c` under hazard `h`
- `value_c,basis` = value of component/subsystem `c` on the chosen basis
- `f_c,h` = hazard-specific at-risk fraction

The guide should always preserve this separation.

---

## 23. Source anchors

This guide is intended to sit beside:

- `03_valuation_guide.md` — method for assigning dollar value to subsystems/components, with the key distinction between allocation, at-risk fraction, and basis.
- `substrate_decomposition.md` — engineering vocabulary for plant/generator → subsystem → component decomposition across solar, wind, BESS, and thermal assets.
- `solar_wind_value_breakdown.xlsx` — sourced default value breakdown workbook for solar and wind, including physical replaceable basis and installed capex reconciliation.

---

## 24. Status

This is a supporting conceptual guide. It should be used to explain the difference between financial valuation and physical-damage valuation before using any value shares in a hazard, insurance, or risk-transfer model.
