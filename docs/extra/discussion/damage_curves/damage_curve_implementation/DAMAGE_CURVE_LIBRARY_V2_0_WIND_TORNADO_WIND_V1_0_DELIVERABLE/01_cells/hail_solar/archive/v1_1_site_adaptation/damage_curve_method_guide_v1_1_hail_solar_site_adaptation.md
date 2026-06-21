# Hail × Solar v1.1 — Site Adaptation and Risk Interface

**Status:** v1.1 applied-interface scaffold  
**Build unit:** `HAIL_SOLAR` hazard × asset cell  
**Curve-record unit:** `PV_MODULE_GLASS_CELL` failure-unit  
**Primary operational x-axis:** MESH-equivalent maximum hail diameter, in **mm** internally  
**Main caution:** the default site frequency table is illustrative. Replace it before using EAL or return-period loss for underwriting.

---

## 1. What v1.1 adds

v1.0 gave us a **severity curve**:

```text
MESH-equivalent hail diameter
        │
        ▼
module replacement damage ratio
        │
        ▼
PV_ARRAY loss %
        │
        ▼
% physical replaceable base
        │
        ▼
% installed capex / TIV
```

v1.1 adds the layer needed to make that curve **site-adaptable**:

```text
site inputs
module archetype
stow condition
footprint exposure fraction
site hail frequency / return-period table
        │
        ▼
site-conditioned severity curve
        │
        ▼
return-period loss
        │
        ▼
illustrative EAL by hail-size bin
```

The point is to prove the full application chain once before moving to the next hazard × asset pairing.

---

## 2. Severity is not frequency

The most important separation:

```text
Severity curve
    "If hail of size D hits the plant, what loss occurs?"

Site frequency curve
    "How often does hail of size D occur at this site?"
```

The v1.0 curve answers the first question.

The new v1.1 sheets provide the interface for the second question.

```text
Severity only:
    D_mm → %TIV loss

Frequency + severity:
    return period → D_mm → %TIV loss
    AEP bin       → loss(D_mid) → EAL contribution
```

Do **not** treat the default frequency table as a sourced hazard model. It is an editable placeholder.

---

## 3. Workbook sheets added in v1.1

| Sheet | Purpose |
|---|---|
| `Hail_Site_Inputs` | Editable site, asset, valuation, module, stow, and exposure inputs. |
| `Hail_Conditioning` | Module archetype curves and stow-condition scenario logic. |
| `Hail_Hazard_Frequency` | Editable MESH exceedance table. Defaults are illustrative. |
| `Hail_Site_Loss` | Site-conditioned severity curve: MESH → DR → %TIV and dollars. |
| `Hail_Return_Period_Loss` | Return-period view using the MESH thresholds in the frequency table. |
| `Hail_EAL_By_Bin` | Discrete EAL approximation by hail-size bin. |
| `Hail_Sensitivity` | Scenario sensitivity at 50 mm and 65 mm MESH. |
| `Hail_V1_1_Dashboard` | Visual summary: severity, loss ladder, return-period loss, EAL bins, sensitivity, cap view. |
| `Hail_V1_1_QA` | Governance checks and use restrictions. |

---

## 4. Core formula chain

The primary loss formula remains:

```text
loss_$ at diameter D
  = DR_conditioned(D)
    × physical_base_$
    × PV_ARRAY_share
    × f_hail
    × footprint_exposure_fraction
```

The same loss can be shown under several denominators:

```text
% PV_ARRAY loss
  = DR_conditioned(D) × f_hail

% physical replaceable base
  = DR_conditioned(D)
    × PV_ARRAY_share
    × f_hail
    × exposure_fraction

% installed capex / TIV
  = % physical base loss
    × physical_base_$ / TIV_$
```

That ladder matters because a hail loss can look modest as `%TIV` while being severe within the affected subsystem.

---

## 5. Site inputs

The main editable inputs are:

| Input | Role |
|---|---|
| `Installed capex / TIV` | Financial denominator for %TIV. |
| `Physical replaceable base` | Physical-damage denominator. |
| `PV_ARRAY share of physical base` | Value link to the valuation workbook. |
| `Hail at-risk f` | Material-share estimate for exposed module glass/cell value. |
| `Footprint exposure fraction` | Fraction of plant footprint hit by the damaging hail swath. |
| `Module archetype` | Chooses fragile, default, or hardened module curve. |
| `Stow mode` | Unstowed, stowed, or probabilistic. |
| `P(stowed)` | Scenario probability for successful stow. |
| `Stow D50 shift` | Placeholder shift in effective curve when stowed. |
| `Stowed max DR multiplier` | Placeholder reduction in high-end stowed damage. |

The current `P(stowed)` logic is a scenario input. It is not yet a stochastic forecast/operations model.

---

## 6. Module archetype selector

v1.1 inherits the v1.0 three-scenario module severity curve:

```text
fragile thin glass//glass
default 3.2 mm glass//backsheet
hail-hardened / thicker glass
```

The selector changes the base logistic curve:

```text
P_break(D) = 1 / (1 + exp(-k × (D - D50)))
```

Conceptually:

```text
same hail size D
        │
        ▼
selected module archetype
        │
        ├─ fragile        → lower D50 → more damage
        ├─ default        → base D50
        └─ hail-hardened  → higher D50 → less damage
```

---

## 7. Stow conditioning

Stow is treated as a conditioner, not as a new hazard x-axis.

```text
MESH diameter D
      │
      ▼
base module curve
      │
      ├─ unstowed curve
      │
      ├─ stowed curve
      │     D50 shifted right by stow_D50_shift_mm
      │     capped by stowed_max_DR_multiplier
      │
      └─ probabilistic curve
            P(stowed) × stowed_DR(D)
          + [1 - P(stowed)] × unstowed_DR(D)
```

Formula:

```text
DR_conditioned(D)
  = P(stowed) × DR_stowed(D)
  + [1 - P(stowed)] × DR_unstowed(D)
```

This is intentionally simple. The open seam is a future model of:

```text
P(stowed | forecast skill, warning lead time, SCADA availability, operator action, storm timing)
```

---

## 8. Footprint exposure

The site loss model includes a `footprint_exposure_fraction`.

```text
exposure_fraction = 1.00
    full plant assumed inside damaging hail swath

exposure_fraction = 0.50
    half the plant footprint hit

exposure_fraction = 0.25
    quarter of the plant footprint hit
```

ASCII:

```text
Hail swath
████████████████
        │
        ▼
Solar field footprint
┌──────────────────────┐
│██████████            │  → partial exposure
│██████████            │
│                      │
└──────────────────────┘
```

A real implementation should compute this by intersecting the plant footprint with a MESH/hail swath raster.

---

## 9. Site hazard frequency

`Hail_Hazard_Frequency` expects an exceedance table:

```text
threshold_D_mm | annual_exceedance_probability
25             | λ(25)
35             | λ(35)
45             | λ(45)
...
```

The return period is:

```text
return_period_years = 1 / annual_exceedance_probability
```

The bin frequency for EAL is:

```text
frequency_bin_i
  = λ(D_low_i) - λ(D_high_i)
```

For example:

```text
λ(45mm) - λ(50mm)
  = annual rate of hail between 45mm and 50mm
```

The workbook then approximates EAL as:

```text
EAL ≈ Σ_i frequency_bin_i × loss(D_mid_i)
```

This is a useful first risk interface, but it is only as good as the frequency curve supplied.

---

## 10. Return-period loss

The return-period view is the simplest executive output.

```text
return period
      │
      ▼
site MESH threshold
      │
      ▼
conditioned module DR
      │
      ▼
loss dollars and %TIV
```

Example interpretation:

```text
100-year MESH threshold = 65mm
        │
        ▼
conditioned DR at 65mm
        │
        ▼
%TIV loss at 100-year hail intensity
```

This plot is useful for communicating severity, but it should not be confused with EAL.

---

## 11. EAL by bin

The EAL-by-bin view is useful because the biggest expected-loss contributor may not be the largest hail.

```text
small severe hail:
    lower loss, higher frequency

extreme hail:
    higher loss, lower frequency
```

The workbook plots:

```text
MESH bin → EAL contribution
```

This shows which hail-size intervals are driving expected annual loss under the supplied frequency table.

---

## 12. Cap-binding view

The failure-unit cap is:

```text
cap_L
  = physical_base_$
    × PV_ARRAY_share
    × f_hail
    × exposure_fraction
```

The cap-binding plot shows:

```text
MESH diameter → conditioned loss $
MESH diameter → failure-unit cap $
```

Interpretation:

```text
loss curve close to cap
    → scalar EAL may be sensitive to cap and f assumptions

loss curve far below cap
    → scalar EAL is less cap-sensitive
```

For hail × solar, this remains an important governance check because `f_hail` is still load-bearing.

---

## 13. Sensitivity view

`Hail_Sensitivity` compares scenarios at **50 mm** and **65 mm** MESH.

Current scenario rows include:

```text
Base
Low f_hail
High f_hail
No stow
High stow confidence
Half-footprint swath
Full-footprint swath
Fragile module
Hail-hardened module
```

This helps show whether the model is mainly driven by:

```text
module choice
stow behavior
exposure fraction
or f_hail / value cap
```

---

## 14. Current default outputs

Using the illustrative default site inputs:

```text
module archetype: Default 3.2mm glass//backsheet
stow mode:        Probabilistic
P(stowed):        60%
exposure:         100%
TIV:              $112.0M
physical base:    $87.8M
```

The dashboard reports approximately:

```text
50mm MESH loss:  ~4.9% of TIV
65mm MESH loss: ~14.9% of TIV
failure-unit cap: ~$23.3M
cap as %TIV: ~20.8%
illustrative EAL: ~$0.49M/year
```

The EAL number is **not final** because the frequency table is illustrative.

---

## 15. What is now ready vs not ready

Ready:

```text
generic severity curve
site input interface
module-class selector
stow scenario conditioner
footprint exposure multiplier
return-period loss view
EAL-by-bin mechanics
cap-binding view
sensitivity view
```

Not ready for final underwriting use until supplied:

```text
site-specific MESH exceedance curve
site-specific footprint / swath exposure
verified module BOM f_hail
site-specific module construction
site-specific stow protocol and stow success assumptions
tail hazard distribution for PML
curve uncertainty / spread for tail metrics
```

---

## 16. QA policy

`Hail_V1_1_QA` intentionally keeps several statuses conservative:

```text
EAL:
    illustrative / conditional until AEP source is real

Tail / PML:
    withheld until hazard tail and curve spread are sourced

Frequency:
    placeholder until replaced

Stow:
    scenario input, not stochastic operations model
```

This prevents the workbook from accidentally turning placeholder inputs into overconfident risk metrics.

---

## 17. Recommended next step after v1.1

After replacing the illustrative frequency table with a real site AEP curve for at least one example site, the next hazard × asset pairing should be:

```text
Flood × solar
```

Why flood next:

```text
hail f  = material-share exposure
flood f = site geometry / equipment elevation exposure
```

That contrast exercises the next major part of the framework.

---

## 18. Source notes

The workbook inherits the v1.0 hail severity sources and explicitly separates operational hail-size inputs from the physics bridge.

Primary source categories carried in the workbook:

```text
NOAA/NCEI Storm Events
NOAA/NWS MESH documentation
DOE/FEMP hail damage mitigation guidance
PVEL/Kiwa hail stress sequence public results
NREL PV weather/performance context
valuation workbook and valuation guide
engineering substrate decomposition
```

Plain-text URLs are stored in the workbook `Sources` sheet.
