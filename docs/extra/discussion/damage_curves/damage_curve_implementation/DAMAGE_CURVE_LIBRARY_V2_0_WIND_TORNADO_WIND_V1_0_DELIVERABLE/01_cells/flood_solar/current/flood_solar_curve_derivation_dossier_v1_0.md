# Flood × Solar Curve Derivation Dossier — v1.0

**Cell:** `FLOOD_SOLAR`  
**Status:** derived v1.0 curve package  
**Primary output:** failure-unit damage-ratio records for direct physical flood damage to solar PV assets.

This dossier is the **proof trail**. It explains why the v1.0 curves are structured as they are, which sources support each decision, which curve forms were rejected, and how selectors/conditioners/exposure variables should modify the curves.

---

## 1. Why flood × solar is different from hail × solar

The hail × solar cell was mostly single-primary-term:

```text
hail size → PV module glass/cell replacement DR
```

Flood × solar is not like that. The hazard does not hit one material surface uniformly. It interacts with equipment elevations, enclosure paths, cable paths, drainage, and water velocity.

```text
flood water surface elevation
      │
      ├─ inverter cabinet below water?       → inverter DR
      ├─ switchgear cabinet below water?     → switchgear DR
      ├─ transformer controls below water?   → transformer/control DR
      ├─ combiner/DC boxes below water?      → combiner/DC DR
      ├─ SCADA cabinet below water?          → SCADA DR
      ├─ cables/conduits wet/contaminated?   → collection DR
      ├─ flow velocity causes scour?         → foundation/civil DR
      └─ modules submerged/debris-hit?       → PV module secondary DR
```

So v1.0 uses a **multi-failure-unit** design.

---

## 2. Derivation architecture

```text
source evidence
   │
   ├─ solar-specific flood pathways
   │     DOE/FEMP PV flood guidance
   │
   ├─ electrical replacement/reconditioning logic
   │     NEMA water-damaged electrical equipment guidance
   │
   ├─ enclosure protection distinctions
   │     NEMA enclosure types
   │
   ├─ utility/equipment elevation logic
   │     FEMA P-348 / Building America Solution Center
   │
   └─ depth-percent curve form precedent
         USACE HEC-FIA

        ↓

failure-unit coverage
        ↓
axis decision
        ↓
piecewise/state curve form
        ↓
parameterized v1.0 curves
        ↓
damage-code interface
```

---

## 3. Evidence map

| Evidence ID | Source | Link | What it supports | What it does **not** support |
|---|---|---|---|---|
| `DOE_FEMP_PV_FLOOD` | DOE/FEMP solar PV flood mitigation guidance | https://www.energy.gov/femp/preventing-and-mitigating-flood-damage-solar-photovoltaic-systems | Solar-specific pathways: total submersion, raising equipment, conduit water paths, enclosure ratings, stormwater/scour mitigation. | Does not provide final numerical depth-damage curves for each utility-scale PV subsystem. |
| `NEMA_GD1_2019` | NEMA GD 1-2019, Evaluating Water-Damaged Electrical Equipment | https://www.nema.org/standards/view/evaluating-water-damaged-electrical-equipment | Replacement/reconditioning framing for water-exposed electrical equipment. | Does not give continuous flood-depth curves. |
| `NEMA_GD1_2016_PDF` | NEMA open PDF guide | https://www.nema.org/docs/default-source/standards-document-library/nema-gd-1-2016-evaluating-water-damaged-electrical-equipment-guide.pdf | Detailed table: switchgear, circuit breakers, electronics, transformers, wire/cable categories. | 2016 guide, not solar-specific, and manufacturer guidance can supersede. |
| `NEMA_ENCLOSURE_TYPES` | NEMA enclosure type definitions | https://www.nema.org/docs/default-source/products-document-library/nema-enclosure-types.pdf | Distinguishes rain/hosedown ratings from temporary/prolonged submersion protection. | Enclosure rating alone does not determine post-flood replacement cost. |
| `FEMA_P348` | FEMA / Building America Solution Center utility-system flood guide | https://basc.pnnl.gov/library/protecting-building-utility-systems-flood-damage-principles-and-practices-design-and | Elevation/protection framing for utility systems. | Building-utility context; not bespoke PV component curves. |
| `USACE_HEC_FIA` | HEC-FIA depth-percent damage relationships | https://www.hec.usace.army.mil/confluence/fiadocs/fiatechref/latest/direct-damage/depth-percent-damage-relationships-direct-damage | Supports tabular depth-percent curve form and interpolation. | Generic flood modeling method, not solar-specific values. |
| `SOLAR_VALUATION` | Internal solar/wind value workbook | `99_source_context/solar_wind_value_breakdown.xlsx` | Value-link basis for subsystem/component caps. | Does not define flood fragility. |
| `SUBSTRATE` | Internal substrate decomposition | `99_source_context/substrate_decomposition.md` | Solar subsystem/component vocabulary. | Does not carry final damage curves. |

---

## 4. Failure-unit coverage decision

The v1.0 coverage map is deliberately broader than hail because flood has multiple equipment-specific pathways.

```text
flood × solar v1.0
├─ primary nonzero depth-driven electrical failure-units
│  ├─ INVERTER_SYSTEM / INVERTER
│  ├─ SUBSTATION / SWITCHGEAR
│  ├─ SUBSTATION / TRANSFORMER_MAIN
│  ├─ INVERTER_SYSTEM / COMBINER_BOX + DC_PROTECTION
│  └─ SCADA / MONITORING_SYSTEM
│
├─ conditional / secondary failure-units
│  ├─ ELECTRICAL_COLLECTION / CABLE_AC + CABLE_DC
│  ├─ FOUNDATION / FOUNDATION_BASE
│  ├─ PV_ARRAY / PV_MODULE
│  └─ CIVIL_INFRA / roads-access-fencing
│
├─ protection / exposure modifiers
│  ├─ SITE_DRAINAGE / DRAINAGE_SYSTEM
│  ├─ SITE_DRAINAGE / FLOOD_DEFENSE
│  └─ equipment freeboard / conduit water path / shutdown state
│
└─ DR≈0 buckets
   └─ equipment above waterline with no alternate ingress path
```

### Why inverters are primary

DOE/FEMP explicitly discusses inverters as flood-sensitive electrical equipment and shows water-path examples where floodwater can enter pull boxes and reach inverters through conduits. NEMA's water-damage guidance treats power electronics and related electrical equipment as high concern after water exposure. Therefore, inverter inundation is a primary curve.

### Why switchgear is primary

NEMA water-damage guidance treats low- and medium-voltage switchgear and power equipment as replacement/evaluation categories after water exposure. Switchgear carries meaningful value and is a central grid-connection component, so it is a primary curve.

### Why transformer damage is primary but less vertical

Transformers are material value buckets, but NEMA guidance distinguishes transformer categories. Liquid-filled transformers may require analysis of insulating medium and professional evaluation rather than immediate 100% replacement in every case. Therefore the transformer curve rises more gradually than inverter/switchgear curves.

### Why PV modules are conditional/secondary

DOE/FEMP states that submerged PV components may be total loss, including modules, but utility-scale modules are often elevated above shallow water. Therefore modules are not the default primary flood failure-unit; they become material when water reaches the lower module edge or debris impact is modeled.

### Why foundation/civil is not folded into depth

Foundation/civil damage is not the same physical mechanism as cabinet water ingress. It depends on flow velocity, erosion, scour, wet-soil support, and site drainage. v1.0 carries a separate velocity/scour proxy and flags it as a placeholder pending site-specific engineering.

---

## 5. X-axis decision

### Rejected: one plant-level flood depth curve

```text
site flood depth → whole solar plant DR
```

Rejected because two pieces of equipment at the same site flood depth can have different local exposure depending on pad height, cabinet entry height, conduit routing, and freeboard.

### Rejected as default v1.0: full 2-D depth × duration curves

```text
DR = f(depth, duration)
```

Duration, contamination, salinity, and energized state matter. But v1.0 does not have enough public evidence to build separate 2-D curves for each failure-unit. These variables are captured as conditioners/open seams.

### Accepted: split by mechanism

```text
electrical ingress / submersion:
    h_i = max(0, WSE - z_i_crit)

foundation / civil scour:
    velocity or scour proxy
```

Where:

```text
h_i        = local water depth above component i's vulnerable datum
WSE        = water surface elevation or local flood depth translated to site datum
z_i_crit   = component-specific critical elevation
```

ASCII view:

```text
water surface elevation
        │
        ├─ above inverter critical elevation?      → h_inverter
        ├─ above switchgear critical elevation?    → h_switchgear
        ├─ above transformer control elevation?    → h_transformer
        ├─ above combiner box elevation?           → h_combiner
        └─ above module lower edge?                → h_module
```

---

## 6. Curve-form decision

### Why not logistic?

A bounded logistic curve was appropriate for hail module breakage because the underlying behavior is a gradual probability of breakage as hail size increases.

Flood electrical damage is more state-like:

```text
dry / below critical datum
      ↓
water reaches enclosure path
      ↓
partial ingress / contamination
      ↓
critical components wet
      ↓
full submersion / replacement likely
```

That behavior is better captured as a tabular/piecewise-linear state curve.

### Alternatives considered

| Curve form | Treatment | Reason |
|---|---|---|
| Step function | Rejected as too brittle | Real sites have uncertainty in elevation, entry path, sealing, contamination, and equipment construction. |
| Logistic | Rejected as default | Suggests a smooth biological/fragility transition; flood equipment guidance is more threshold/state-based. |
| Piecewise-linear depth-percent curve | Accepted | Matches the depth-damage modeling tradition and keeps thresholds auditable. |
| Discrete damage states only | Kept compatible | v1.0 data can be emitted as states later; workbook uses continuous interpolation for plotting. |

USACE HEC-FIA's depth-percent damage relationship precedent supports tabular depth-percent damage curves with interpolation. This is why v1.0 uses piecewise-linear state curves.

---

## 7. v1.0 base curves

### 7.1 Shared depth ordinates

```text
local depth above component datum, meters:
0.00, 0.02, 0.05, 0.15, 0.30, 0.60, 1.00, 1.50, 2.00
```

The first few centimeters matter because water entry into electrical enclosures, control sections, cable entries, or lower vents can trigger replacement/evaluation even before deep submersion.

### 7.2 Curve table

| Failure unit | 0.00m | 0.02m | 0.05m | 0.15m | 0.30m | 0.60m | 1.00m | 1.50m | 2.00m | Rationale |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Inverter cabinet / power electronics | 0% | 5% | 25% | 75% | 95% | 100% | 100% | 100% | 100% | Power electronics and controls are high-loss once water enters. |
| Switchgear / breaker cabinet | 0% | 10% | 40% | 85% | 100% | 100% | 100% | 100% | 100% | NEMA replacement logic supports steep curve after ingress. |
| Transformer/control area | 0% | 3% | 10% | 25% | 45% | 65% | 80% | 95% | 100% | Liquid-filled transformer default allows evaluation/reconditioning, so less vertical. |
| Combiner/DC protection | 0% | 10% | 35% | 80% | 100% | 100% | 100% | 100% | 100% | Small electrical enclosure, surge/protection/wiring devices are water-sensitive. |
| SCADA/control cabinet | 0% | 15% | 45% | 90% | 100% | 100% | 100% | 100% | 100% | Electronics/communications are high-loss once wet/contaminated. |
| Collection cable/conduit path | 0% | 2% | 5% | 10% | 15% | 25% | 40% | 55% | 65% | Wet-location cable may survive; terminations/conduit contamination dominate. |
| PV module submersion | 0% | 5% | 10% | 30% | 60% | 85% | 100% | 100% | 100% | Conditional; only applies when water reaches the module lower edge. |

### 7.3 Velocity/scour proxy

| Failure unit | Axis | 0.0 | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 | 4.0 | Rationale |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Foundation/pile scour | velocity/scour proxy | 0% | 0% | 5% | 15% | 35% | 70% | 100% | Placeholder proxy; must be replaced with site hydraulic/geotech assessment where material. |

---

## 8. What exactly is derived versus assumed?

### Source-anchored decisions

- Use local water depth above component datum instead of plant-level flood depth.
- Treat submerged PV/electrical components as potentially total-loss/high-loss.
- Treat conduit paths as an important water-ingress pathway.
- Distinguish normal outdoor enclosures from Type 6/6P submersion-rated enclosures.
- Treat transformer salvageability differently from switchgear/power electronics.
- Use tabular/piecewise depth-percent curves rather than a generic smooth curve.

### Engineering assumptions in v1.0

- Exact DR percentages at intermediate depths.
- Default critical elevations for the illustrative dashboard.
- Default value splits between transformer and switchgear within substation.
- Velocity/scour numeric curve.
- Conduit water-path numeric modifier.
- Duration, contamination, and salinity effects.

These are explicitly carried in `Flood_Assumption_Register` and should be replaced by claims/OEM/forensic/site-engineering evidence when available.

---

## 9. Selectors, conditioners, and exposure variables

| Type | Flood × solar examples | How it changes the model |
|---|---|---|
| Hazard input | `water_surface_elevation_m`, `site_depth_m`, `flow_velocity_mps` | Drives x-axis. |
| Exposure geometry | `component_critical_elevation_m`, `pad_height_m`, `module_lower_edge_m` | Horizontal shift through `h_i = max(0, WSE - z_i_crit)`. |
| Selector | `enclosure_rating`, `transformer_type`, `cable_wet_location_rating` | Selects a different curve family or curve variant. |
| Conditioner | `energized_state`, `shutdown_before_flood`, `conduit_water_path_present`, `duration_hr`, `contamination_class` | Adjusts severity or flags uncertainty. |
| Exposure multiplier | `fraction_of_component_value_exposed` | Scales affected value, not fragility. |

---

## 10. Adjustment rules

```text
Create a new curve when:
    the physical failure mechanism, electrical replacement logic,
    or equipment construction is distinct.

Horizontally shift/expose when:
    the same equipment is simply higher or lower relative to flood water.

Select a variant when:
    enclosure rating, transformer type, or cable rating changes resistance.

Condition/blend when:
    event-time operating state changes consequences.

Scale value when:
    only part of the value bucket is exposed.
```

Examples:

| Situation | Correct treatment |
|---|---|
| Inverter pad raised by 0.5m | Horizontal exposure shift: local depth is reduced. |
| Switchgear replaced by Type 6P submersible cabinet | Potential curve variant, not merely value scaling. |
| Equipment was energized during inundation | Conditioner; may increase severity/safety consequences. |
| Only half the inverter stations are in the flood swath | Exposure/value multiplier. |
| Conduit from flooded pull boxes drains to inverter | Metadata modifier/open seam; site design needed. |

---

## 11. Damage-code output grain

The damage code should emit failure-unit damage ratios, not EAL or portfolio financial metrics.

```yaml
damage_code_id: FLOOD_SOLAR_ELECTRICAL_INUNDATION_V1
hazard_asset_pair: flood_x_solar
primary_axis: FLOOD_LOCAL_DEPTH_COMPONENT_DATUM
failure_units:
  - FS_INV
  - FS_SWG
  - FS_XFMR
  - FS_COMB
  - FS_SCADA
secondary_units:
  - FS_CABLE
  - FS_FOUND
  - FS_PVMOD
outputs:
  - failure_unit_damage_ratio
  - curve_version
  - evidence_level
  - selector_conditioner_flags
  - open_seams
```

Downstream systems can then apply:

```text
loss_i = DR_i × value_i × exposure_fraction_i
```

and handle EAL, PML, return-period loss, and financial metrics separately.

---

## 12. QA status

| QA item | Status |
|---|---|
| Not a whole-plant curve | PASS |
| Failure-unit coverage map present | PASS |
| X-axis decisions and rejected alternatives present | PASS |
| Curve-form alternatives and rationale present | PASS |
| Evidence-to-parameter mapping present | PASS |
| Source links present | PASS |
| Selectors / conditioners / exposure variables separated | PASS |
| Value basis explicit | PASS |
| EAL/tail not overclaimed | PASS |
| Open seams documented | PASS |

---

## 13. Open seams and update triggers

| Seam | Why it matters | Update trigger |
|---|---|---|
| Claims-calibrated DR by equipment type | v1.0 uses engineering parameters | Insurer/claims/OEM dataset becomes available. |
| Exact equipment elevations | Local depth transform controls DR | Site survey / EPC drawings / digital twin available. |
| Conduit water-path routing | Can damage equipment even when cabinet appears elevated | Electrical one-line, civil grading, conduit layout available. |
| Duration / salinity / contamination | Can shift reconditioning versus replacement | Source with duration/contamination-based outcomes. |
| Transformer type | Dry-type vs liquid-filled changes replacement logic | Asset metadata available. |
| Scour/foundation curve | Site-specific geotech/hydraulics dominate | Hydraulic model or forensic failure data available. |
| Enclosure rating misuse | NEMA 4/4X is not submersion protection | Actual enclosure rating/installation details available. |

---

## 14. Implementation note

For flood × solar, the most important data fields to collect in the engineering substrate or asset metadata layer are:

```text
component critical elevation
pad height / freeboard
module lower edge elevation
inverter enclosure rating
switchgear enclosure rating
transformer type
cable wet-location rating
conduit path / drain routing
energized or shutdown state
flood defense / drainage state
flow velocity / scour risk
```

This is the value of the damage-code design: it tells future data ingestion what metadata actually matters.
