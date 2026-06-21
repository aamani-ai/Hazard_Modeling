# Hail × Solar Curve Derivation Dossier v1.3

**Cell:** `hail × solar`  
**Primary damage code:** `HAIL_SOLAR_PV_MODULE_V1`  
**Primary failure-unit:** `PV_MODULE_GLASS_CELL` inside `PV_ARRAY`  
**Operational x-axis:** `HAIL_DIAMETER_MESH_EQUIV` — maximum hail diameter / MESH-equivalent hail size, internal unit `mm`  
**Curve output:** `failure_unit_damage_ratio` = PV module glass/cell replacement damage ratio  
**Status:** public-source-derived v1 curve, not private-claims-calibrated  

---

## 0. Why this dossier exists

This file is the proof trail for the hail × solar damage curve. It answers the reviewer question:

> “Show me exactly how you curated the curve, which sources supported which numbers, what was assumed, and how selectors/conditioners change the curve.”

A curve picture alone is not enough. A smooth curve can always be drawn by choosing a few nice-looking parameters. The purpose of this dossier is to make the curve auditable:

```text
source evidence
   │
   ▼
source interpretation
   │
   ▼
anchor selection
   │
   ▼
curve form
   │
   ▼
parameter fitting
   │
   ▼
selector / conditioner adjustment rules
   │
   ▼
damage-code output
```

The workbook version of this proof lives in these v1.3 sheets:

```text
Hail_Derivation_Index
Hail_Evidence_Params
Hail_Base_Curve_Fit
Hail_Adjustment_Rules
Hail_Variant_Catalog
Hail_Assumption_Register
```

---

## 1. Modeling decision: one primary curve, not one whole-asset curve

For v1, hail × solar is modeled as **single-primary-term**:

```text
MESH-equivalent hail diameter
   │
   ▼
PV_MODULE glass/cell replacement damage ratio
   │
   ▼
PV_ARRAY exposed value bucket
```

It is **not** modeled as:

```text
hail diameter → whole solar plant damage ratio
```

That distinction matters. Hail impact damage concentrates on the modules, especially the front glass/cell/module replacement trigger. Other subsystems are reviewed, but they are not forced into weak nonzero curves unless there is a distinct, material, sourceable direct-hail failure mechanism.

```text
hail × solar v1.3
├─ primary nonzero failure-unit
│  └─ PV_ARRAY / PV_MODULE / glass-cell replacement trigger
│
├─ conditioner-only equipment
│  └─ MOUNTING / TRACKER, because tracker stow changes module exposure
│
├─ reviewed secondary / low-materiality equipment
│  └─ SCADA / MET_STATION, exposed instruments
│
└─ DR≈0 direct-hail buckets in v1
   ├─ INVERTER_SYSTEM
   ├─ SUBSTATION
   ├─ CIVIL_INFRA
   ├─ FOUNDATION
   └─ SITE_DRAINAGE
```

The correct output grain for the damage code is therefore:

```text
failure_unit_damage_ratio = DR_PV_MODULE_GLASS_CELL(D)
```

Optional value-linked reporting can then convert this into:

```text
PV_ARRAY loss %
physical-base loss %
%TIV / installed-capex loss
loss dollars
```

But those are downstream value views, not the core damage-code definition.

---

## 2. X-axis decision: hail diameter as operational axis; kinetic energy as bridge

The primary operational x-axis is:

```text
HAIL_DIAMETER_MESH_EQUIV
    maximum hail diameter / MESH-equivalent hail size
    internal unit: mm
    source-native units allowed: inches, mm
```

The reason is practical: hazard catalogs and operational hail products usually provide hail size, not kinetic energy.

Evidence:

| Source | What it supports | URL |
|---|---|---|
| NOAA/NCEI Storm Events FAQ | Hail magnitude is reported as hail size in inches and hundredths of inches. | https://www.ncei.noaa.gov/stormevents/faq.jsp |
| NOAA/NWS WDTD MESH page | MESH estimates maximum hail size; displayed in inches; base units are mm. | https://vlab.noaa.gov/web/wdtd/-/maximum-estimated-size-of-hail-mes-2 |

Kinetic energy still matters physically:

```text
impact energy = 0.5 × mass × velocity²
```

But kinetic energy is retained as a **derived physics bridge**, not the required provider-native input.

```text
provider / hazard layer
   hail size / MESH diameter
        │
        ▼
normalized hail diameter D_mm
        │
        ▼
optional bridge
   m(D), v(D), E_proxy(D)
        │
        ▼
PV module breakage / replacement curve
```

The bridge is especially useful because IEC-style hail tests and PVEL/Kiwa hail stress tests specify controlled hail diameter, mass, velocity, and/or impact energy.

Important distinction:

```text
E_proxy_j_per_impact
    per-stone impact-energy proxy
    useful for lab-test interpretation

J_per_m2 or kinetic-energy flux
    event aggregate / areal concept
    not used in v1 unless a source explicitly provides stone concentration or flux
```

---

## 3. Evidence classes used

The curve is built from four evidence classes. They do not all have the same role.

| Evidence class | Source examples | Role in v1.3 | How much it constrains the curve |
|---|---|---|---|
| Operational hazard data | NOAA Storm Events, NOAA/NWS MESH | Selects x-axis and units | Strong for axis, not for damage |
| Standards / qualification | IEC 61215 hail test table via DOE/FEMP | Near-zero baseline and diameter→mass/velocity bridge | Strong for physical bridge, weak as field-loss curve |
| Lab aggregate breakage data | PVEL/Kiwa Hail Stress Sequence | Main module archetype breakage anchors | Strongest public curve evidence |
| Field performance context | NREL extreme weather PV performance; PVEL field-informed HSS whitepaper | Threshold/context/caveat | Useful context, not direct replacement-cost curve |

The v1.3 curve is therefore best described as:

```text
public-source-derived module replacement severity curve
```

not:

```text
private claims-calibrated loss curve
```

---

## 4. What the y-axis means

The base curve outputs:

```text
P_break(D)
```

In v1.3, we use:

```text
module replacement DR ≈ P_break(D)
```

This is a deliberate approximation. It is not saying that every hail impact immediately creates the same power loss. It says that, for physical-damage replacement modeling, **glass breakage is the best public, observable replacement trigger**.

Reasoning:

```text
hail impact can cause:
├─ visible glass breakage
│  └─ likely replacement / insurance-relevant physical damage
│
├─ cell cracking without glass breakage
│  └─ may cause low immediate power loss, latent degradation, or monitoring issue
│
└─ no material damage
```

PVEL/Kiwa materials emphasize that modules without broken glass can have limited power degradation after hail stress tests, while glass breakage is a clearer physical failure. So v1.3 uses glass breakage as the replacement trigger and keeps latent performance degradation out of this replacement-cost curve.

Open seam:

```text
If claims data shows replacement policy differs materially from glass breakage probability,
then the y-axis mapping should be recalibrated.
```

---

## 5. Curve form

The selected curve form is logistic:

```text
P_break(D) = 1 / (1 + exp(-k × (D - D50)))
```

Where:

| Parameter | Meaning |
|---|---|
| `D` | MESH-equivalent maximum hail diameter, mm |
| `D50` | Diameter where module replacement / glass breakage probability reaches 50% |
| `k` | Steepness of transition from low to high breakage probability |

Why logistic?

```text
1. Bounded between 0 and 1.
2. Monotonic with hail size.
3. Captures threshold-like behavior without an artificial step jump.
4. Fits sparse public anchor data without overfitting.
5. Easy to shift horizontally for vulnerability selectors.
```

The curve is not intended to imply that nature is exactly logistic. It is a controlled v1 functional form for damage-code use.

---

## 6. Base curve variants

v1.3 carries three base archetype curves.

| Curve ID | Archetype | D50 mm | k 1/mm | Status |
|---|---|---:|---:|---|
| `HAIL_SOLAR_FRAGILE_THIN_GG` | Fragile / thin 2.0 mm glass//glass | 41.07 | 0.220633 | public aggregate fit |
| `HAIL_SOLAR_DEFAULT_3P2_GBS` | Default / 3.2 mm glass//backsheet | 52.70 | 0.165912 | public anchor fit |
| `HAIL_SOLAR_HARDENED_THICKER` | Hail-hardened / thicker-glass design | 64.11 | 0.135331 | sparse-anchor extrapolated fit |

These are **not** manufacturer-specific warranty curves. They are generic archetype curves, designed to let the damage code respond to known module construction metadata.

---

## 7. Default 3.2 mm glass//backsheet curve derivation

The default curve is a two-anchor logistic fit.

### 7.1 Anchors

| Anchor | Diameter | Probability | Evidence role |
|---|---:|---:|---|
| IEC baseline near-zero anchor | 25 mm | 1% | Qualified modules should not have material replacement damage at baseline certification level. |
| PVEL 2023 glass//backsheet anchor | 50 mm | 39% | Public PVEL HSS breakage rate for 3.2 mm glass//backsheet modules at 50 mm. |

Source notes:

- DOE/FEMP summarizes IEC 61215 hail certification and optional larger ice-ball tests, including diameter, mass, and velocity. The baseline 25 mm test is treated as a near-zero replacement anchor, not as a field damage curve.
- PVEL’s 2023 Hail Stress Sequence reports 39% glass breakage for 3.2 mm glass//backsheet modules during 50 mm hail testing.

### 7.2 Formula

For a logistic curve:

```text
logit(p) = ln(p / (1 - p))
```

Given two anchors `(D1, p1)` and `(D2, p2)`:

```text
k = [logit(p2) - logit(p1)] / (D2 - D1)
D50 = D1 - logit(p1) / k
```

For the default curve:

```text
D1 = 25 mm
p1 = 0.01

D2 = 50 mm
p2 = 0.39
```

This gives:

```text
k    = 0.165912 1/mm
D50  = 52.696 mm
```

So:

```text
P_break_default(D)
  = 1 / (1 + exp(-0.165912 × (D - 52.696)))
```

### 7.3 Interpretation

This curve says:

```text
25 mm hail    → near-zero replacement probability
50 mm hail    → moderate breakage probability, aligned to PVEL public aggregate
>60 mm hail   → rapidly approaches severe module replacement regime
```

It does not say:

```text
all sites with 50 mm MESH lose exactly 39% of modules
```

Why not?

Because field outcomes still depend on:

```text
module BOM
hail density / shape / velocity / trajectory
impact location
tracker angle / stow state
storm footprint
claims replacement policy
```

---

## 8. Fragile thin glass//glass curve derivation

The fragile curve uses public PVEL/Kiwa aggregate anchors for 2.0 mm glass//glass modules.

Public anchors used:

| Source | Diameter | Breakage |
|---|---:|---:|
| PVEL 2023 HSS | 35 mm | 18% |
| PVEL 2023 HSS | 40 mm | 57% |
| Kiwa PVEL current HSS | 40 mm | 43% |
| Kiwa PVEL current HSS | 45 mm | 61% |
| PVEL 2023 HSS | 50 mm | 89% |

The fragile curve is fit using a least-squares method in logit space:

```text
logit(p_i) ≈ k × (D_i - D50)
```

Equivalent linear form:

```text
logit(p_i) = k × D_i - k × D50
```

The fitted parameters are:

```text
k    = 0.220633 1/mm
D50  = 41.074 mm
```

So:

```text
P_break_fragile(D)
  = 1 / (1 + exp(-0.220633 × (D - 41.074)))
```

Interpretation:

```text
thin glass//glass modules transition into high breakage probability at smaller hail diameters than the default 3.2 mm glass//backsheet archetype.
```

Caveat:

```text
This is still public aggregate lab evidence, not a module-specific BOM guarantee.
```

---

## 9. Hail-hardened / thicker-glass curve derivation

The hardened curve is intentionally more conservative about confidence. It uses fewer public numeric anchors.

Anchors:

| Anchor | Diameter | Probability | Role |
|---|---:|---:|---|
| IEC near-zero hardened assumption | 25 mm | 0.5% | Hardened modules should be no worse than baseline-certified modules. |
| PVEL/Kiwa hardened/thicker-glass public result | 45 mm | 7% | Public evidence that thicker/hail-hardened designs have lower breakage. |

The two-anchor logistic fit gives:

```text
k    = 0.135331 1/mm
D50  = 64.114 mm
```

So:

```text
P_break_hardened(D)
  = 1 / (1 + exp(-0.135331 × (D - 64.114)))
```

Interpretation:

```text
hail-hardened modules require larger hail diameters to reach the same breakage probability.
```

Caveat:

```text
The hardened tail is extrapolated. Use this curve only when module specs or test evidence justify a hardened archetype.
```

---

## 10. Diameter-to-kinetic-energy bridge

The base x-axis remains diameter. But the workbook includes a physics bridge:

```text
E_proxy(D) = 0.5 × m(D) × v(D)^2
```

Using the DOE/FEMP IEC hail test table:

| Diameter mm | Mass g | Velocity m/s |
|---:|---:|---:|
| 25 | 7.54 | 23.0 |
| 35 | 20.7 | 27.2 |
| 45 | 43.9 | 30.7 |
| 55 | 80.2 | 33.9 |
| 65 | 132 | 36.7 |
| 76 | 203 | 39.5 |

The workbook fits power-law approximations:

```text
mass_g(D)      = a_m × D^b_m
velocity_mps(D)= a_v × D^b_v
```

Current fitted values:

```text
mass_g(D)       = 0.0005290357 × D^2.973997
velocity_mps(D) = 4.812461 × D^0.486643
```

This gives a per-stone impact energy proxy. It is used for interpretation and future physics-based conditioning; it is not the required input axis.

---

## 11. Module archetype selector logic

`module_archetype` is a **fixed asset selector**.

It answers:

```text
What kind of module is installed, from a hail-fragility perspective?
```

It is not a hazard frequency variable. It is not an event-time state.

### 11.1 Current archetypes

```text
fragile_thin_glass_glass
    use HAIL_SOLAR_FRAGILE_THIN_GG

default_3_2mm_glass_backsheet
    use HAIL_SOLAR_DEFAULT_3P2_GBS

hail_hardened_thicker_glass
    use HAIL_SOLAR_HARDENED_THICKER
```

### 11.2 Mapping guidance

| Available metadata | v1.3 mapping |
|---|---|
| 2.0 mm glass//glass, heat-strengthened, bifacial thin glass | `fragile_thin_glass_glass` |
| 3.2 mm fully tempered glass//backsheet | `default_3_2mm_glass_backsheet` |
| 2.5 mm glass//glass with favorable hail testing | `hail_hardened_thicker_glass`, if supported by test evidence |
| 3.2 mm glass//2.0 mm glass marketed/tested as hail-hardened | `hail_hardened_thicker_glass`, if supported by test evidence |
| 4.0 mm front glass or enhanced hail certification | `hail_hardened_thicker_glass` or exact override |
| Unknown modern utility-scale module | default to `default_3_2mm_glass_backsheet`, flag unknown |

### 11.3 Do we have all module archetype curves?

For v1.3, we have three archetype curves:

```text
fragile
baseline/default
hardened
```

We do **not** yet have continuous curves for every glass thickness, every frame design, every manufacturer, or every bill of materials. Exact module/BOM data should override archetypes when available.

---

## 12. Glass thickness, tempered glass, and glass//backsheet vs glass//glass

These fields are selectors that help choose the archetype.

```text
front_glass_thickness_mm
    tells us the thickness and likely resistance of front glass

tempered_glass
    indicates stronger glass treatment; thin non-tempered or heat-strengthened glass is more fragile

glass_glass_vs_backsheet
    distinguishes module construction type
```

Current v1.3 treatment:

```text
These fields map to archetype.
They do not yet create a continuous glass-thickness formula.
```

Why not continuous?

Because public data is not yet dense enough to justify a formula like:

```text
D50 = f(glass_thickness_mm)
```

That would look precise but would be poorly supported.

Correct v1.3 approach:

```text
exact BOM test data available?
   ├─ yes → create exact override curve or calibrated parameter set
   └─ no  → map to closest archetype and flag confidence
```

---

## 13. Stow mode, stow state, and probability of stow

The correct word is **stow**, not store.

A tracker can rotate modules into a defensive position during severe weather. For hail, this is usually a high-tilt position intended to reduce direct impact.

```text
normal tracking
    tracker follows the sun

hail stow
    tracker rotates toward maximum vertical tilt
    hail strikes become more glancing
    exposed projected area and normal impact energy decrease
```

### 13.1 Metadata definitions

| Field | Type | Meaning |
|---|---|---|
| `mounting_type` | selector | fixed tilt, single-axis tracker, dual-axis tracker |
| `stow_applicable` | derived | whether active hail stow can apply |
| `stow_state` | conditioner | actual event-time state: stowed, unstowed, unknown |
| `stow_angle_deg` | conditioner detail | actual defensive tilt if known |
| `stow_trigger` | operational metadata | manual, automatic, weather alert, none |
| `stow_confirmation` | operational metadata | commanded vs confirmed by SCADA |
| `stow_success_probability` | uncertainty variable | probability tracker was actually stowed when damaging hail arrived |

### 13.2 Probability of stow

`P(stowed)` is:

```text
P(tracker was in hail-stow position | damaging hail arrived)
```

It is not:

```text
probability of hail
annual hail frequency
return period
EAL
```

If the state is known:

```text
confirmed stowed   → P(stowed)=1.0
confirmed unstowed → P(stowed)=0.0
```

If the state is unknown:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + [1 - P(stowed)] × DR_unstowed(D)
```

### 13.3 Current stow adjustment

The v1.3 workbook currently uses a simple transformed curve:

```text
D50_stowed = D50_selected + 8 mm
k_stowed   = k_selected
max_DR_stowed = 0.90
```

Then:

```text
DR_stowed(D)
  = 0.90 × 1 / (1 + exp(-k_selected × (D - (D50_selected + 8))))
```

This means stow is modeled as:

```text
horizontal shift right
    larger hail is required to cause the same damage probability

plus small vertical multiplier
    direct/exposed impact potential is reduced
```

### 13.4 Why this is a placeholder

DOE/FEMP and VDE support the direction of the effect: higher tilt / tracker stow reduces the direct impact angle and normal kinetic energy. FTC Solar’s 80° hail stow release shows that high-angle automated stow is an operational design being commercialized. But those public sources do not provide a generic, sourceable percentage reduction that applies to all trackers and all angles.

So the numeric stow adjustment is explicitly a placeholder. It should be replaced when available with:

```text
tracker-specific hail stow test data
angle-specific impact model
event-time SCADA confirmation
claims or lab evidence by stow angle
```

---

## 14. Should selectors and conditioners create new curves or adjust existing curves?

This is the rule:

```text
Create a new curve when:
    the physical failure mechanism or material construction is distinct,
    the value affected is material,
    and evidence supports different curve parameters.

Adjust an existing curve when:
    the same failure mechanism remains,
    but resistance, angle, exposure, or event-time state changes.
```

### 14.1 Horizontal adjustment

Use horizontal shifts for resistance/threshold changes.

```text
D50_adjusted = D50_base + ΔD
```

Examples:

```text
hail-hardened module → higher D50
stowed tracker       → higher effective D50
```

Interpretation:

```text
The same damage probability requires larger hail.
```

### 14.2 Vertical adjustment

Use vertical multipliers only when maximum affected fraction or exposed area changes.

```text
DR_adjusted(D) = multiplier × DR_base(D)
```

Examples:

```text
stow reduces exposed direct-impact area
partial mechanical shielding reduces max affected fraction
```

Do not use vertical scaling to represent stronger glass unless evidence says the asymptotic maximum loss is lower. Stronger glass usually shifts the threshold; sufficiently extreme hail can still break modules.

### 14.3 Probability-weighted mixture

Use mixtures when the event-time state is uncertain.

```text
DR_expected(D)
  = p_state_1 × DR_state_1(D)
  + p_state_2 × DR_state_2(D)
```

Example:

```text
unknown stow state:
DR = P(stowed) × DR_stowed + (1-P(stowed)) × DR_unstowed
```

### 14.4 Exposure multiplier

Use exposure multipliers for storm footprint.

```text
loss = DR × value × f × exposure_fraction
```

This does not change module fragility. It changes how much array value is hit.

---

## 15. Current loss/value linkage

The damage code produces a failure-unit DR. If value linkage is available:

```text
loss_$ = DR_module(D)
       × physical_base_$
       × PV_ARRAY_value_share
       × f_hail_material_share
       × array_exposure_fraction
```

v1.3 keeps these separate:

```text
DR_module(D)
    engineering damage output

PV_ARRAY_value_share
    valuation allocation

f_hail_material_share
    concentration inside PV_ARRAY

array_exposure_fraction
    spatial/event exposure
```

This prevents accidentally applying module damage to the whole project TIV.

---

## 16. Reviewed secondary equipment

The v1.3 package includes a coverage table because the curve library must be exhaustive in thought even when only one primary curve is nonzero.

| Subsystem | v1.3 treatment | Reason |
|---|---|---|
| `PV_ARRAY / PV_MODULE` | primary nonzero curve | Direct impact mechanism and material value. |
| `MOUNTING / TRACKER` | conditioner-only | Stow/angle affects module damage; direct steel tracker hail damage is secondary. |
| `RACKING_STRUCTURE` | secondary / open | Possible in extreme cases, but not first-order public-source curve. |
| `INVERTER_SYSTEM` | DR≈0 for direct hail v1 | Enclosed equipment; not first-order direct hail failure. |
| `SUBSTATION` | DR≈0 for direct hail v1 | Electrical internals not directly exposed like modules. |
| `SCADA / MET_STATION` | optional secondary | Exposed instruments can be damaged, but low materiality. |
| `CIVIL_INFRA / FOUNDATION / SITE_DRAINAGE` | DR≈0 for direct hail v1 | Direct hail does not normally drive civil/foundation replacement. |

This table is not decorative. It is the evidence that we reviewed the rest of the plant and did not simply forget it.

---

## 17. What would make v2 better

The main upgrade path is not “make the curve prettier.” It is to replace placeholders with better evidence.

Priority upgrades:

```text
1. BOM-specific hail test reports
   → replace archetype curves with exact curve parameters

2. Claims or repair-policy calibration
   → calibrate P_break to actual replacement DR

3. Module BOM / cost allocation
   → improve f_hail_material_share and cap_L

4. Tracker/stow angle testing
   → replace +8mm D50 and 0.90 max multiplier

5. SCADA/event logs
   → replace assumed P(stowed) with observed event-time state

6. Site MESH swath overlay
   → replace exposure_fraction=1.0 default
```

---

## 18. Reviewer checklist

Before using or approving the hail × solar curve, check:

```text
[ ] Is the x-axis diameter/MESH, not unlabeled kinetic energy?
[ ] Is the module archetype known or defaulted with a flag?
[ ] Are glass thickness and construction known?
[ ] Is the stow state known, or is probabilistic stow clearly labeled?
[ ] Is stow probability being confused with hail frequency? It should not be.
[ ] Is exposure_fraction site-specific or default full-site?
[ ] Is f_hail_material_share sourced or placeholder?
[ ] Are secondary subsystems explicitly reviewed?
[ ] Is the curve being applied only to PV_MODULE/PV_ARRAY exposed value, not whole TIV?
[ ] Are tail/EAL metrics handled downstream with hazard frequency and uncertainty, not inside this damage code?
```

---

## 19. One-screen summary

```text
HAIL × SOLAR DAMAGE CODE v1.3

Input:
    D = MESH-equivalent maximum hail diameter, mm

Base curve:
    P_break(D) = 1 / (1 + exp(-k × (D - D50)))

Selector:
    module_archetype
        fragile thin glass//glass        → D50 ≈ 41.1 mm
        default 3.2mm glass//backsheet   → D50 ≈ 52.7 mm
        hail-hardened/thicker glass      → D50 ≈ 64.1 mm

Conditioner:
    stow_state
        unstowed → selected base curve
        stowed   → D50 + 8mm, max_DR × 0.90 placeholder
        unknown  → probability-weighted blend

Exposure:
    array_exposure_fraction
        multiplies value-linked loss, not module DR

Output:
    failure_unit_damage_ratio
        PV_MODULE glass/cell replacement DR

Value link, if needed:
    loss = DR × physical_base × PV_ARRAY_share × f_hail × exposure_fraction
```

---

## 20. Source URLs used in this dossier

| Source | URL |
|---|---|
| NOAA/NCEI Storm Events FAQ | https://www.ncei.noaa.gov/stormevents/faq.jsp |
| NOAA/NWS WDTD MESH | https://vlab.noaa.gov/web/wdtd/-/maximum-estimated-size-of-hail-mes-2 |
| DOE/FEMP Hail Damage Mitigation for PV Systems | https://www.energy.gov/femp/hail-damage-mitigation-solar-photovoltaic-systems |
| PVEL 2023 Hail Stress Sequence | https://2023modulescorecard.pvel.com/hail-stress-sequence/ |
| Kiwa PVEL current Hail Stress Sequence | https://scorecard.pvel.com/hail-stress-sequence/ |
| Kiwa PVEL 2024 Hail Stress Sequence | https://2024modulescorecard.pvel.com/hail-stress-sequence/ |
| PVEL Hail Stress Sequence whitepaper | https://www.pvel.com/wp-content/uploads/PVEL_White-Paper_Hail-Stress-Sequence-for-PV-Modules.pdf |
| NREL Extreme Weather and PV Performance | https://research-hub.nrel.gov/en/publications/extreme-weather-and-pv-performance-2 |
| VDE Americas hail stow memo | https://www.vde.com/en/vde-americas/newsroom/hail-stow-tech-memo |
| FTC Solar 80° hail stow announcement | https://investor.ftcsolar.com/news-releases/news-release-details/ftc-solar-launches-automated-80deg-high-angle-stow-1p-pioneer/ |
