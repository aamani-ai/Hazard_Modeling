# 11 · Hail × Solar as the Reference Pattern

The hail × solar cell is the first worked example. Future cells should mimic its **logic**, not necessarily its exact number of curves.

## 1. The useful snapshot pattern

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

This does three important things at once:

```text
1. It identifies the primary modeled damage code.
2. It documents equipment that matters as a conditioner rather than as its own curve.
3. It records reviewed equipment that is not modeled as nonzero direct damage in v1.
```

## 2. Why this is not just formatting

The snapshot prevents two mistakes:

```text
Mistake A:
  Apply PV module damage to the whole solar TIV.

Mistake B:
  Create weak direct-hail curves for every subsystem just because the subsystem exists.
```

The correct model is:

```text
one primary failure-unit curve
+ explicit coverage/reconciliation rows
+ selector/conditioner/exposure metadata
```

## 3. How future cells may differ

Some cells will have multiple primary curves.

```text
flood × solar
├─ INVERTER_SYSTEM / INVERTER / electrical ingress
├─ SUBSTATION / SWITCHGEAR / inundation
├─ ELECTRICAL_COLLECTION / cable trench inundation
└─ FOUNDATION / scour, if velocity pathway is included
```

```text
wind/tornado × wind
├─ ROTOR_ASSEMBLY / BLADE / structural failure
├─ NACELLE / drivetrain or enclosure damage
├─ TOWER / structural failure
└─ FOUNDATION / overturning or foundation damage
```

The format is the same. The number of primary curves changes with the hazard mechanism.

## 4. What must carry forward

Every future cell should include:

```text
- one snapshot tree,
- one coverage table,
- one x-axis decision memo,
- one curve-form decision memo,
- one derivation dossier,
- one selector/conditioner/exposure map,
- one source-to-parameter map,
- one assumption register,
- and one damage-code interface spec.
```

## 5. How to read the hail × solar package as an example

```text
README_hail_solar_v1_3.md
  shows package map and the cell snapshot.

hail_solar_curve_derivation_dossier_v1_3.md
  shows evidence → anchors → curve form → parameters → adjustments.

damage_code_metadata_spec_hail_solar_v1_3.md
  shows the damage-code input/output contract.

damage_curve_records_v1_3_hail_solar_derivation_audit.xlsx
  shows workbook implementation and audit sheets.
```

Do not copy the hail curve into other cells. Copy the reasoning structure.
