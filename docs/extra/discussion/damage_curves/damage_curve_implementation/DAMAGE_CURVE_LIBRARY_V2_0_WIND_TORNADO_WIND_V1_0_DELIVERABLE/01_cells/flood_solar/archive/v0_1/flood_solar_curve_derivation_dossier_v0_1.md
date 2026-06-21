# Flood × Solar Curve Derivation Dossier v0.1

**Cell:** `FLOOD_SOLAR`  
**Status:** v0.1 derivation dossier scaffold  
**This version:** documents the logic, sources, candidate curve forms, and decision points before deriving final numeric curves.

---

## 1. Central derivation question

For hail × solar, one primary curve was enough because the damage mechanism concentrated on exposed modules. For flood × solar, the derivation question changes:

```text
Given a flood hazard at the site,
which solar components are below water, through which pathway,
and what damage ratio should each exposed failure-unit receive?
```

So the cell needs multiple failure-unit records and at least two x-axis families:

```text
depth above component datum  → electrical ingress / submersion
velocity or scour proxy      → foundation / erosion / structural pathways
```

---

## 2. Evidence map

| Evidence ID | Source | Link | What it supports | What it does not support |
|---|---|---|---|---|
| `DOE_FEMP_PV_FLOOD` | DOE/FEMP solar PV flood mitigation guidance | https://www.energy.gov/femp/preventing-and-mitigating-flood-damage-solar-photovoltaic-systems | Solar-specific failure pathways: total submersion, raising equipment, conduit water paths, enclosure ratings, stormwater/scour mitigation. | Does not provide final numerical depth-damage functions by utility-scale subsystem. |
| `NEMA_GD1_WATER_DAMAGE` | NEMA Evaluating Water-Damaged Electrical Equipment | https://www.nema.org/standards/view/evaluating-water-damaged-electrical-equipment | Replacement/reconditioning logic for water-exposed electrical equipment. | Does not give a continuous flood-depth damage curve. |
| `NEMA_WATER_DAMAGE_GUIDE` | NEMA guidelines for handling water-damaged electrical equipment | https://www.nema.org/docs/default-source/products-document-library/guidelines-handling-water-damaged-elect-equip.pdf | Why water exposure is dangerous; role of moisture, debris, contaminants, saltwater; need for evaluation/replacement. | Not solar-specific. |
| `FEMA_HAZUS_FLOOD` | FEMA Hazus Flood Model Technical Manual | https://www.fema.gov/sites/default/files/documents/fema_hazus-flood-model-technical-manual-6-1.pdf | Flood models use percent damage functions and component inventory value; utility components can use functional-depth thresholds and equipment-height assumptions. | Generic utility / building model, not a bespoke PV component curve. |
| `FEMA_P348_UTILITIES` | FEMA P-348 Protecting Building Utility Systems from Flood Damage | https://www.fema.gov/sites/default/files/2020-07/fema_p-348_protecting_building_utility_systems_from_flood_damage_2017.pdf | Utility-system elevation, floodproofing, and design logic. | Building-utility context; must be adapted to solar plant equipment. |
| `NEMA_ENCLOSURE_TYPES` | NEMA enclosure type definitions | https://www.nema.org/docs/default-source/products-document-library/nema-enclosure-types.pdf | Enclosure protection distinctions: rain/hosedown vs temporary/prolonged submersion. | Enclosure rating alone does not determine total replacement cost. |
| `ASCE_24` | ASCE 24 flood resistant design and construction | https://www.asce.org/publications-and-news/codes-and-standards/asce-sei-24-24 | Elevation, floodproofing, utility/equipment placement, flood-resistant design context. | Design standard, not a damage curve. |

---

## 3. Base x-axis decision

### 3.1 Rejected: one generic flood severity score

```text
flood severity score → whole solar plant DR
```

Rejected because different solar components fail through different flood pathways.

### 3.2 Rejected as v0.1 default: a true 2-D depth-duration curve for every component

```text
DR = f(depth, duration)
```

Realistic but too heavy for v0.1. Duration should be carried as a conditioner/deferred axis until evidence shows it materially changes the curve form for a specific failure-unit.

### 3.3 Accepted: split into mechanism-specific univariate curves

```text
depth above component datum → electrical ingress/submersion
velocity/scour proxy        → foundation/civil/scour damage
```

This preserves physical meaning without forcing a premature high-dimensional model.

---

## 4. Exposure transform

The most important formula in flood × solar is not the damage curve itself. It is the exposure transform:

```text
h_i = max(0, WSE - z_i_crit)
```

Where:

```text
h_i        = water depth above vulnerable part of component i
WSE        = water surface elevation
z_i_crit   = component-specific critical elevation
```

Examples:

```text
inverter:
    z_i_crit = inverter cabinet vulnerable entry elevation

switchgear:
    z_i_crit = switchgear cabinet base or critical electrical threshold

transformer:
    z_i_crit = transformer control cabinet / terminal box / vulnerable component elevation

combiner box:
    z_i_crit = box base or cable-entry height

SCADA cabinet:
    z_i_crit = cabinet entry / electronics elevation

foundation/scour:
    z_i_crit is not enough; use velocity/scour pathway
```

ASCII:

```text
water surface elevation
        │
        ├─ above inverter critical elevation?     yes/no → h_inverter
        ├─ above switchgear critical elevation?   yes/no → h_switchgear
        ├─ above combiner critical elevation?     yes/no → h_combiner
        └─ above SCADA critical elevation?        yes/no → h_SCADA
```

This is why flood `f` is a geometry/elevation share, not a material/BOM share.

---

## 5. Candidate curve forms

### 5.1 Step / trigger curve

```text
DR_i(h_i) = 0       if h_i <= 0
DR_i(h_i) = L_i     if h_i > 0
```

**Where it fits:** electrical equipment where any submersion triggers replacement or professional reconditioning.  
**Why plausible:** DOE/FEMP says submerged solar system components need replacement, and NEMA guidance frames water-exposed electrical equipment as requiring replacement or trained reconditioning.  
**Limitation:** can be too brittle if elevations are uncertain, components are sealed, or partial contact is less damaging.

### 5.2 Smoothed threshold / logistic curve

```text
DR_i(h_i) = L_i / (1 + exp(-k_i × (h_i - h50_i)))
```

**Where it fits:** when the physical threshold is sharp but actual site data has uncertainty: elevation survey error, waves, cabinet geometry, enclosure penetration heights, and partial submersion ambiguity.  
**Interpretation:** logistic smooths uncertainty around a threshold; it should not imply a biological dose-response unless evidence supports that.  
**Good for:** inverters, switchgear, SCADA cabinets, combiner boxes.

### 5.3 Piecewise ramp

```text
DR_i(h_i) =
  0                          below contact
  partial_repair_fraction     shallow contact / splash / cable entry
  high_repair_fraction        partial submersion
  replacement_cap             full submersion
```

**Where it fits:** when we can distinguish splash, cable-entry water path, partial cabinet flooding, and full submersion.  
**Good for:** inverter cabinets, control cabinets, cable/conduit paths.

### 5.4 State model

```text
state_0: dry / no contact
state_1: water reaches enclosure exterior
state_2: water enters enclosure or conduit path
state_3: partial submersion of energized equipment
state_4: full submersion / contaminated water / replacement trigger
```

**Where it fits:** when recovery outcome is categorical: no damage, inspect, recondition, replace.  
**Good for:** electrical equipment and NEMA water-damage guidance.

### 5.5 Separate scour curve

```text
DR_foundation = f(flow_velocity, depth, soil_erodibility, duration)
```

**Where it fits:** foundation, pile, pad, roads, drainage/civil damage.  
**v0.1 decision:** do not collapse scour into electrical depth curve.

---

## 6. Candidate failure-unit derivation plans

### 6.1 Inverter inundation

```text
failure_unit_id: FLOOD_SOLAR_INVERTER_INUNDATION
x-axis: water_depth_above_inverter_critical_elevation_m
candidate form: smoothed threshold or state model
curve cap: inverter replacement/reconditioning value bucket
key selectors: NEMA/IP rating, inverter topology, cabinet/skid elevation
key conditioners: energized state, contamination, duration, shutdown
```

Initial derivation logic:

```text
If h_inverter <= 0:
    DR ≈ 0, unless conduit-water-path modifier applies.

If h_inverter > 0 and water enters cabinet:
    DR should move toward inspection/reconditioning/replacement state.

If full submersion or contaminated/saltwater:
    DR likely approaches replacement cap.
```

### 6.2 Switchgear inundation

```text
failure_unit_id: FLOOD_SOLAR_SWITCHGEAR_INUNDATION
x-axis: water_depth_above_switchgear_critical_elevation_m
candidate form: state model or smoothed threshold
value bucket: SUBSTATION / SWITCHGEAR
```

Switchgear is a high-priority v1.0 curve because it is both material and safety-critical.

### 6.3 Transformer/control inundation

```text
failure_unit_id: FLOOD_SOLAR_TRANSFORMER_INUNDATION
x-axis: water_depth_above_transformer_or_control_critical_elevation_m
candidate form: state model with different caps for controls vs main transformer body
value bucket: SUBSTATION / TRANSFORMER_MAIN
```

Potential split in v1.0:

```text
control cabinet / terminal box / auxiliaries
    lower cap, lower critical elevation

main transformer tank / windings / oil contamination
    high cap, different submersion logic
```

### 6.4 Combiner / DC protection inundation

```text
failure_unit_id: FLOOD_SOLAR_COMBINER_DC_PROTECTION_INUNDATION
x-axis: water_depth_above_enclosure_critical_elevation_m
candidate form: smoothed threshold
value bucket: INVERTER_SYSTEM / COMBINER_BOX + DC_PROTECTION
```

May be secondary by value, but important because there are many distributed units.

### 6.5 SCADA/control cabinet inundation

```text
failure_unit_id: FLOOD_SOLAR_SCADA_CABINET_INUNDATION
x-axis: water_depth_above_scada_cabinet_critical_elevation_m
candidate form: threshold/state
value bucket: SCADA / MONITORING_SYSTEM
```

Likely low dollar materiality but high operational importance.

### 6.6 Collection/conduit water path

```text
failure_unit_id: FLOOD_SOLAR_COLLECTION_CONDUIT_WATER_PATH
x-axis: water_depth_above_pullbox_or_conduit_entry_m
candidate form: pathway modifier or separate cable/collection curve
value bucket: ELECTRICAL_COLLECTION
```

DOE/FEMP specifically highlights floodwater entering pull boxes and conduits and traveling to switchgear/inverters. That means this may be a **pathway modifier** for inverter/switchgear curves rather than a standalone cable damage curve.

### 6.7 Foundation / scour

```text
failure_unit_id: FLOOD_SOLAR_FOUNDATION_SCOUR
x-axis: flow_velocity_mps or depth_velocity_proxy
candidate form: separate scour threshold / piecewise curve
value bucket: FOUNDATION
```

This should not be derived from the electrical ingress curve. It is a separate structural/civil pathway.

---

## 7. New curve vs adjustment rule for flood

Create a **new curve** when:

```text
the failure mechanism changes:
    electrical ingress vs scour vs conduit transport vs submersion of modules

or the value cap changes materially:
    inverter vs switchgear vs transformer vs SCADA

or the critical x-axis changes:
    depth above cabinet datum vs flow velocity
```

Adjust an existing curve when:

```text
same failure mechanism remains, but resistance or exposure changes:
    NEMA/IP rating
    energized/shutdown state
    contamination class
    duration
    flood defense state
```

Do **not** use a curve adjustment when the variable is only exposure geometry:

```text
equipment elevation changes h_i before the curve.
It should not be mistaken for a new fragility curve unless the equipment design itself changes.
```

---

## 8. Source-to-parameter mapping for v1.0

| Parameter / rule | Candidate source support | v0.1 treatment |
|---|---|---|
| `total_submersion_replacement_trigger` | DOE/FEMP PV flood guidance; NEMA water-damage guidance | High-confidence direction; numeric cap from value ledger. |
| `depth_above_component_datum` | FEMA/Hazus equipment-height logic; ASCE/FEMA utility elevation logic | Adopt as core exposure transform. |
| `NEMA/IP_selector` | NEMA enclosure type definitions | Use as selector; do not treat NEMA 3/4 as submersion-proof. |
| `conduit_water_path_modifier` | DOE/FEMP conduit water-path examples | Include as modifier/open seam. |
| `scour_velocity_axis` | DOE/FEMP stormwater/scour mitigation guidance; civil/hydraulic sources needed | Include as separate pathway; derive later. |
| `duration_conditioner` | NEMA water-damage and corrosion/contamination logic | Carry as conditioner/deferred axis. |
| `contamination/salinity_conditioner` | NEMA water-damage guidance | Carry as conditioner; numeric multiplier TBD. |

---

## 9. Open seams

```text
SEAM_FLOOD_NUMERIC_DEPTH_DAMAGE:
    Need component-specific numeric curves or state thresholds.

SEAM_FLOOD_EQUIPMENT_ELEVATION_DATA:
    Utility-scale PV equipment elevations are often missing from public data.

SEAM_FLOOD_RECONDITION_VS_REPLACE:
    Need rule for whether DR means replacement cost, reconditioning cost, or expected weighted state.

SEAM_FLOOD_CONDUIT_PATHWAY:
    Need model for pullbox/conduit water transport to inverters/switchgear.

SEAM_FLOOD_DURATION_CONTAMINATION:
    Need numeric treatment for duration, saltwater, sewage/chemical contamination.

SEAM_FLOOD_SCOUR:
    Need separate hydraulic/civil evidence for pile/pad scour curves.

SEAM_FLOOD_SHARED_PLANT_ALLOCATION:
    Substation/SCADA damage may be plant-scope and shared across solar/BESS/hybrid assets.
```

---

## 10. v1.0 derivation checklist

```text
□ Gather component elevation defaults or site-input schema.
□ Decide whether inverter/switchgear/combiner use step, smoothed threshold, or state model.
□ Define replacement vs reconditioning DR states.
□ Assign curve caps from valuation buckets.
□ Define NEMA/IP selector rules.
□ Define conduit-path modifier.
□ Define contamination/duration assumptions.
□ Build first numeric depth-damage curves for top electrical failure-units.
□ Keep scour separate unless evidence supports coupling.
□ Add dashboard plots: water depth above component → DR by failure-unit.
```
