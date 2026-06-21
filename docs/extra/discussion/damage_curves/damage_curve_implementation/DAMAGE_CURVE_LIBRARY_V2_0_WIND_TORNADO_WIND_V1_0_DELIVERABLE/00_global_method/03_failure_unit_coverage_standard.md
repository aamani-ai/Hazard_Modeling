# 03 · Failure-Unit Coverage Standard

This document defines how every cell decides what gets a damage curve and what is explicitly reviewed but not modeled.

## 1. Why coverage matters

A damage model can fail in two opposite ways:

```text
Overbroad:
  one asset-level curve applies damage to the whole TIV

Overfragmented:
  every subsystem gets a weak curve even when the hazard does not materially affect it
```

The correct middle path is:

```text
one hazard × asset cell
    └─ one or more primary failure-unit curves
       + explicit reviewed secondary / DR≈0 rows
```

## 2. Decision tree

```text
candidate subsystem/component
   │
   ├─ Is there a direct physical failure mechanism for this hazard?
   │      └─ no → DR≈0 direct effect or out-of-scope
   │
   ├─ Is the mechanism distinct from another modeled failure-unit?
   │      └─ no → include in existing curve or value bucket
   │
   ├─ Is the affected value material enough to matter?
   │      └─ no → secondary / low-materiality
   │
   ├─ Is there evidence to define a curve or credible placeholder?
   │      └─ no → open seam / future curve
   │
   └─ yes to all
          └─ create primary nonzero failure-unit curve
```

## 3. Coverage categories

### 3.1 Primary nonzero failure-unit

A failure-unit gets a primary curve when:

```text
- the hazard directly causes damage,
- the failure mechanism is distinct,
- the value affected is material,
- the x-axis can be defined,
- and the curve can be curated or responsibly parameterized.
```

Example:

```text
hail × solar:
  PV_MODULE glass/cell replacement trigger
```

### 3.2 Conditioner-only equipment

Some equipment does not need its own damage curve but changes the damage state of another failure-unit.

Example:

```text
MOUNTING / TRACKER in hail × solar
  tracker stow changes effective module exposure,
  but tracker steel itself is not the main direct-hail loss bucket in v1.
```

### 3.3 Secondary / low-materiality equipment

A subsystem may plausibly be affected but not enough to justify a separate v1 curve.

Example:

```text
SCADA / MET_STATION in hail × solar
  exposed sensors could be damaged,
  but expected value share and evidence are thin.
```

This should be documented, not silently omitted.

### 3.4 DR≈0 direct-effect bucket

A subsystem can hold value but have approximately zero direct damage for this hazard.

Example:

```text
FOUNDATION under direct hail
  value exists,
  but direct hail does not physically damage the foundation in v1.
```

This preserves value reconciliation.

### 3.5 Out-of-scope pathway

A pathway may be real but outside the current cell.

Example:

```text
hail followed by water ingress days later
  could be a secondary degradation pathway,
  but v1 direct-hail cell models immediate replacement-trigger damage only.
```

## 4. When a cell needs multiple damage codes

Create multiple primary damage codes when different subsystems fail through materially different mechanisms.

Examples:

```text
flood × solar
├─ INVERTER electrical ingress curve
├─ SUBSTATION switchgear inundation curve
├─ ELECTRICAL_COLLECTION cable trench inundation curve
└─ FOUNDATION scour curve, if velocity/scour is included
```

```text
wind/tornado × wind
├─ BLADE structural failure curve
├─ TOWER structural failure curve
├─ NACELLE damage curve
└─ FOUNDATION overturning/scour curve, if relevant
```

Do not force these into one asset-level curve unless the evidence genuinely supports an aggregate loss curve and the value basis is explicit.

## 5. Coverage table template

| Subsystem | Component | v1 treatment | Reason | Update trigger |
|---|---|---|---|---|
| `<SUBSYSTEM>` | `<COMPONENT>` | primary / conditioner-only / secondary / DR≈0 / out-of-scope | Why | What evidence or use-case would change this |

## 6. Rule of thumb

```text
If excluding the unit would materially bias the damage code, model it.
If including it would create a weak false-precision curve, document it as secondary or DR≈0.
```
