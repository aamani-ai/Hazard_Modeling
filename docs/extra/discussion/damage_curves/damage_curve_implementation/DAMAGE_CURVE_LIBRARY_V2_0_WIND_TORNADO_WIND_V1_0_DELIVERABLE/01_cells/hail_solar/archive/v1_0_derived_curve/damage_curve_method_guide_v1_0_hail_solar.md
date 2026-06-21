# Hail x Solar v1.0 damage curve derivation

**Deliverable status:** v1.0 public-source derived curve.

This file upgrades the earlier scaffold from a placeholder plotting curve into a first defensible **hail x solar PV module damage curve**. It remains a public-source curve, not a private claims-calibrated curve. The workbook contains the structured data, formulas, source rows, and charts.

Files produced with this guide:

- `damage_curve_records_v1_0_hail_solar_derived.xlsx`
- `hail_solar_v1_0_dashboard_preview.png`

---

## 1. Decision summary

For hail x solar, the right operational x-axis is:

```text
HAIL_DIAMETER_MESH_EQUIV
= maximum hail diameter / MESH-equivalent hail size
= mm internally, inches accepted as source-native input
```

Kinetic energy is still used, but only as a **physics bridge**:

```text
diameter D
   -> mass(D), velocity(D)
   -> KE_proxy = 0.5 x mass_kg(D) x velocity(D)^2
```

This is deliberately not a `J/m2` event-flux axis. It is a **per-stone impact-energy proxy** used for lab-test anchoring and physics interpretation.

Why this split exists:

```text
provider / hazard data usually gives:
   hail size, reported diameter, MESH, hail swath bins

damage physics wants:
   mass, velocity, impact angle, stone density, impact energy

v1 modeling compromise:
   ingest diameter/MESH natively,
   derive KE only through an explicit bridge.
```

---

## 2. Evidence used

| Evidence source | What it contributes | How used |
|---|---|---|
| NOAA/NCEI Storm Events FAQ | Hail magnitude is reported as hail size in inches/hundredths | Supports diameter as the operational axis |
| NOAA/NWS WDTD MESH | MESH estimates maximum hail size; AWIPS display in inches, base units mm | Supports MESH-equivalent diameter axis |
| DOE/FEMP PV hail mitigation guide | IEC 61215 hail-test table: 25/35/45/55/65/76 mm with mass and velocity; notes that PV module damage becomes significant in very large hail above about 44 mm | Supports KE bridge and threshold intuition |
| Kiwa PVEL 2023 HSS | Public breakage rates: 2.0 mm glass//glass at 35/40/50 mm; 3.2 mm glass//backsheet at 50 mm | Supports fragile and default curve anchors |
| Kiwa PVEL 2026 HSS | Current public breakage rates for 2.0 mm glass//glass and thicker-glass/hail-hardened designs | Supports scenario curves and hardened curve |
| NREL/IEEE Extreme Weather and PV Performance | Hail sizes >=25 mm associated with higher performance-loss rate in fielded PV systems | Field context, not replacement curve calibration |

Raw source URLs are recorded inside the workbook `Evidence_Log` and `Sources` sheets.

---

## 3. Curve object

The v1 failure-unit curve is:

```text
cell_id:          HAIL_SOLAR
failure_unit:     PV_MODULE_GLASS_CELL
subsystem:        PV_ARRAY
component:        PV_MODULE
x_axis:           HAIL_DIAMETER_MESH_EQUIV
unit:             mm
curve form:       diameter-native logistic
default curve:    3.2 mm glass//backsheet
```

The curve is intentionally a **replacement-damage curve**, not a pure production-loss curve. PVEL's public scorecard material indicates that unbroken modules can show low post-hail power loss, while glass breakage is the more meaningful replacement trigger. Therefore, for v1:

```text
DR_module_replacement(D) ~= P_glass_breakage(D)
```

Non-broken cell-crack power degradation is recognized, but it is not the main physical-replacement dollar driver in this v1 curve.

---

## 4. Logistic curve form

The curve form is:

```text
P_break(D) = 1 / (1 + exp(-k x (D - D50)))
```

where:

```text
D     = MESH-equivalent maximum hail diameter, mm
D50   = diameter where 50% of the module archetype breaks
k     = curve steepness, 1/mm
```

The workbook includes three scenario curves.

| Curve | D50 mm | k 1/mm | Public anchors | Confidence |
|---|---:|---:|---|---|
| Fragile thin 2.0 mm glass//glass | 41.07 | 0.2206 | PVEL 2023/2026 35-50 mm breakage rates | Medium |
| Default 3.2 mm glass//backsheet | 52.70 | 0.1659 | IEC 25 mm near-zero + PVEL 2023 50 mm 39% breakage | Medium |
| Hail-hardened / thicker glass | 64.11 | 0.1353 | IEC 25 mm near-zero + PVEL 2026 45 mm 7% breakage | Low/medium |

The **default selected curve** is the 3.2 mm glass//backsheet curve. That aligns with DOE/FEMP's recommendation to select modules with at least 3.2 mm front glass and with PVEL's public result showing much lower breakage for 3.2 mm glass//backsheet than 2.0 mm glass//glass at 50 mm.

---

## 5. Diameter-to-energy bridge

The workbook fits simple power laws to DOE/FEMP's IEC diameter/mass/velocity table:

```text
mass_g(D)     = 0.000529036 x D^2.973997
velocity(D)   = 4.812461 x D^0.486643
KE_proxy(D)   = 0.5 x mass_kg(D) x velocity(D)^2
```

Approximate bridge values:

| Diameter | KE proxy |
|---:|---:|
| 25 mm | 2.0 J/impact |
| 35 mm | 7.6 J/impact |
| 45 mm | 20.6 J/impact |
| 50 mm | 31.2 J/impact |
| 55 mm | 45.4 J/impact |
| 65 mm | 87.8 J/impact |
| 76 mm | 162.7 J/impact |

ASCII sketch:

```text
diameter (mm)       25      35      45      55      65      76
                    |-------|-------|-------|-------|-------|
KE / impact          2J      8J     21J     45J     88J    163J
```

The energy bridge rises much faster than diameter, which explains why 50-65 mm hail can be disproportionately damaging.

---

## 6. Value translation

The valuation layer supplies:

```text
physical_base_usd                  = $87,779,570
installed_capex_or_TIV_usd          = $112,000,000
PV_ARRAY value share of physical    = 33.176%
hail at-risk f                      = 80.0%
default exposure fraction           = 100.0%
```

Therefore the primary module-glass/cell failure-unit cap is:

```text
cap_L = physical_base_usd x PV_ARRAY_share x f_hail x exposure_fraction
      = $23,297,188

cap_L as % physical base = 26.5%
cap_L as % installed/TIV = 20.8%
```

Loss formulas:

```text
module_DR(D)           = P_break(D)

PV_ARRAY_loss_pct(D)   = module_DR(D) x f_hail

physical_loss_pct(D)   = module_DR(D)
                         x PV_ARRAY_share
                         x f_hail
                         x exposure_fraction

TIV_loss_pct(D)        = physical_loss_pct(D)
                         x physical_base_usd / installed_capex_or_TIV_usd

loss_usd(D)            = module_DR(D) x cap_L
```

Default curve outputs:

| MESH diameter | Default module DR | % installed capex / TIV | Loss dollars |
|---:|---:|---:|---:|
| 25 mm | 1.0% | 0.2% | $232,972 |
| 35 mm | 5.0% | 1.0% | $1,174,237 |
| 40 mm | 10.8% | 2.3% | $2,527,114 |
| 45 mm | 21.8% | 4.5% | $5,080,717 |
| 50 mm | 39.0% | 8.1% | $9,085,903 |
| 55 mm | 59.4% | 12.4% | $13,848,210 |
| 65 mm | 88.5% | 18.4% | $20,619,711 |
| 76 mm | 97.9% | 20.4% | $22,819,498 |

---

## 7. ASCII plot intuition

Default selected curve:

```text
Module replacement DR
100% |                                      ________
 80% |                                _____/
 60% |                          _____/
 40% |                    _____/
 20% |              _____/
  0% |____ ________/
      25   35   45   50   55   65   76 mm
```

Value translation ladder:

```text
MESH diameter
   |
   v
module replacement DR
   |
   v
PV_ARRAY loss % = DR x f_hail
   |
   v
physical-base loss % = DR x PV_ARRAY_share x f_hail
   |
   v
TIV loss % = physical-base loss % x physical_base / TIV
```

Why the two percentages differ:

```text
A 50 mm event on the default curve:
   module DR                         ~= 39.0%
   PV_ARRAY loss                     ~= 31.2%
   physical-base loss                ~= 10.4%
   installed-capex / TIV loss         ~= 8.1%
```

That is exactly why the workbook plots both subsystem-level and TIV-level losses.

---

## 8. Cap-binding interpretation

The module failure-unit cap is about **20.8% of installed capex / TIV** under the default valuation assumptions. The default curve approaches that cap in the 65-76 mm range.

```text
50 mm  -> ~8.1% TIV
55 mm  -> ~12.4% TIV
65 mm  -> ~18.4% TIV
76 mm  -> ~20.4% TIV
cap    -> ~20.8% TIV
```

Implication:

```text
Severity curve: ready for scenario plotting.
EAL: conditional, requires site hail-frequency / exceedance distribution.
Tail/PML: withheld until hazard distribution + curve spread are available.
```

This is not a failure of the curve. It is the correct metric-honesty outcome.

---

## 9. How to use the curves

Use the three curves this way:

| Curve | Use |
|---|---|
| Fragile thin 2.0 mm glass//glass | Upper / fragile sensitivity, especially thin bifacial glass-glass designs |
| Default 3.2 mm glass//backsheet | Generic default where no BOM-specific hail report exists |
| Hail-hardened / thicker glass | Lower / mitigation scenario, but tail remains extrapolated |

A plant-specific implementation should override the default when these are available:

```text
module BOM-specific hail test report
front/rear glass thickness
glass type: tempered vs heat-strengthened
module size and frame/support design
tracker stow capability
actual stow angle during event
hail swath exposure fraction from MESH raster overlay
insurance replacement criteria for cell cracks vs glass breakage
```

---

## 10. Open seams

The v1 curve is useful now, but these seams remain important:

| Seam | Why it matters | Current treatment |
|---|---|---|
| Module-BOM `f_hail` | It sets the exposed value cap | placeholder `f=0.8`; update when module BOM cost split is sourced |
| Stow/forecast correlation | Stow state is not independent of the event; it depends on warnings, controls, and execution | carried as conditioner/open seam |
| Lab-to-field translation | PVEL tests targeted impacts; field hail has stochastic stone concentration, angle, and swath variability | public curve labeled as lab-anchored scenario curve |
| Hail frequency | EAL requires a site-level frequency distribution for MESH diameter | not included in v1 severity curve |
| Tail uncertainty | PML requires hazard + curve spread | withheld until distribution/spread exists |

---

## 11. What changed vs v0.3

```text
v0.3:
   placeholder sigmoid for plotting mechanics

v1.0:
   source-derived scenario curves
   default curve selected
   PVEL/DOE/NOAA/NREL evidence rows added
   explicit D50/k parameters
   diameter-to-KE bridge quantified
   cap-binding interpretation updated
   dashboard plots updated
```

---

## 12. Files and workbook sheets

The v1 workbook adds:

```text
Hail_V1_Derivation
Hail_V1_Data
Hail_V1_Dashboard
Hail_V1_QA
```

And updates:

```text
Curve_Records
Curve_Params
Evidence_Log
Cap_Binding_Preflight
Sources
```
