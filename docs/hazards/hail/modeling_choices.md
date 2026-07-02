# Hail Modeling Choices

**Status:** built on main for **hail x solar** deep per-asset; hail x solar CONUS grid is packaged and QC'd but
still provisional as a screening layer. This file records the modeling choices from M0 to M4. For the physics
primer, read [`fundamentals_before_m0.md`](fundamentals_before_m0.md). For source roles, read
[`source_selection.md`](source_selection.md).

The core hail modeling fact:

```text
MESH is raw gridded evidence, not a ready event catalog.
M1 must turn daily MESH fields into hail-day event / cell frequency and severity objects.
```

---

## M0-M4 In One Table

| Layer | Hail model object | Main choices |
|---|---|---|
| **M0** | MRMS 24-hour max MESH daily fields, plus NOAA/SPC point reports for validation. | Selected MRMS product grain is `CONUS/MESH_Max_1440min_00.50`; raw radar tiles are cache/derived-source material, not committed. NOAA reports validate/cross-check but do not define V1 events. |
| **M1** | Hail-day event model: frequency plus hail-size severity. | Deep run reconstructs event footprints in a 50-mi collection window and fits NegBin over-dispersion; grid uses exact 0.25 degree cell rates with Poisson V1 default. MESH plausibility QC caps severity summary at 203.2 mm, flags hard artifacts/spikes, and leaves severe-day frequency untouched. |
| **M2** | Areal hit-or-miss coupling. | Solar is a dense polygon. Per-event hit probability uses the Minkowski form `p_hit = (sqrt(F) + sqrt(s))^2 / A`, capped at 1. Grid uses cell-clipped severe-pixel area as a footprint proxy. |
| **M3** | Hail size -> solar damage ratio. | Capex-weighted solar curve from PV module + tracker vulnerability; most value is hail-immune; current legacy curve caps around 34% TIV and saturates near 100 mm. Curated damage-modeling curve swap is a standalone deferred task. |
| **M4** | Annual AEP/OEP loss vectors and metrics. | Compound MC draws event counts, Bernoulli hits, full conditional event losses, and then reads EAL, VaR/PML, TVaR, OEP/AEP in dollars and % TIV. Never use `p_hit * loss` as the event loss for tail metrics. |

---

## M1 Event Model Contract

Hail uses the **raw observation path** from
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md).

### Deep Per-Asset Run

```text
source:
  MRMS MESH daily severe fields around the asset

event definition:
  one hail-day event from a 24-hour max MESH product
  severe threshold = 25.4 mm

count process:
  annual event count in the collection region
  Negative Binomial when over-dispersion is detected
  fitted on the available operational MRMS record

severity process:
  empirical observed event severities / footprint summaries
  EVT severity tail deferred

event identity:
  hail-day event identity exists within the reconstructed regional catalog
  portfolio correlation not yet generalized
```

Built deep-run parameters:

```text
lambda_collection ~= 29.6 hail-days/year
Fano / dispersion ~= 3.37
lambda_asset ~= 0.26 hits/year after M2 thinning
record ~= 5.65 years, 158 hail-day events
```

### CONUS Grid

```text
source:
  same MRMS daily MESH evidence, aggregated cell by cell

event definition:
  severe hail day in exact 0.25 degree benchmark cell

count process:
  Poisson per cell in V1
  per-cell over-dispersion is diagnostic only because the short record cannot support stable cell-level Fano fits

severity process:
  per-cell MESH severity summaries after plausibility QC
  raw severity retained; reportable severity capped/flagged

event identity:
  cell-day evidence; cross-cell event family / storm identity deferred
```

QC choices:

```text
physical cap:        203.2 mm
hard artifact flag:  MESH >= 300 mm
frequency spikes:    flagged/held out for reportable loss
frequency count:     unchanged
raw MESH:            retained
```

The important modeling line: MESH QC is an **M0/M1 hazard-layer** treatment, not an asset-specific M3 patch.

---

## Coupling Contract

Hail x solar is **areal hit-or-miss**:

```text
p_hit = (sqrt(F) + sqrt(s))^2 / A
lambda_asset = lambda_collection * E[p_hit]
```

Where:

```text
F = severe hail footprint area
s = solar footprint area
A = collection window area
```

M2 changes the frequency seen by the asset. It answers:

```text
does the hail footprint overlap the solar plant?
```

V1 exposure simplification:

```text
if hit:
  exposed_fraction = 1.0
  event_loss = DR(hail_size) * TIV
```

Do not multiply `p_hit` into the M3 event loss. `p_hit` belongs to the Bernoulli hit/miss draw in M4. Collapsing
the event to `p_hit * loss` preserves EAL but destroys VaR/PML/TVaR.

---

## Damage Contract

M3 consumes:

```text
hailstone size / MESH intensity in mm
```

M3 emits:

```text
damage ratio of solar asset value
```

Current V1 curve:

```text
family:
  capex-weighted blend of subsystem curves

main vulnerable components:
  PV modules
  trackers

mostly immune / low-reach components:
  inverters
  substation
  electrical
  civil

asset DR cap:
  around 34% of TIV in the legacy curve

conditional damage uncertainty:
  deferred; current curve is scalar mean DR
```

The solar curve saturates near 100 mm, which is why the CONUS plausibility cap above 200 mm is loss-invariant
for the current solar curve. It still matters for hazard-layer honesty and for future assets whose damage may
continue increasing above 100 mm.

---

## M4 Sampling And Metrics

Deep-run M4:

```text
for each simulated year:
  draw annual hail event count from NegBin
  for each event:
    draw / bootstrap event footprint and severity
    draw Bernoulli(p_hit)
    if hit:
      event_loss = DR(size) * TIV
    else:
      event_loss = 0

  A_y = sum(event_loss)
  O_y = max(event_loss)
```

Grid M4:

```text
for each cell:
  draw event count from Poisson(lambda_cell)
  sample severity according to the cell's severity policy
  apply canonical solar M2/M3
  emit the Contract-2 risk layer
```

Metrics:

```text
EAL
AEP VaR / PML
OEP PML
TVaR
dollars
% of TIV
```

Doctrine:

```text
EAL can be checked analytically.
Tail metrics must be read from sampled annual losses.
Never Method 0 for PML/VaR/TVaR.
```

---

## Built Numbers And Confidence

Deep hail x solar, Hayhurst:

```text
TIV:              $36.78M
lambda_asset:     ~0.26 hits/year
EAL:              ~$2.09M, 5.7% TIV
AEP-PML100:       ~54% TIV
AEP-PML250:       ~62% TIV
zero-loss years:  ~77%
```

Confidence:

```text
frequency body:       real but short-record-limited
M2 math:              validated; fixes old point-factor issue
M3 curve:             provisional / legacy
deep tail:            bootstrap-truncated; EVT deferred
grid loss layer:      provisional screening, not reportable product
```

---

## Open Questions And Better Ways

Questions to resolve during review:

```text
MESH severity:
  Is the 203.2 mm plausibility cap enough for V1, or should MESH be de-biased before any reportable severity
  / loss layer is published?

severity tail:
  Does a bootstrap over 5.65 years understate rare hail sizes? A censored / bounded EVT tail is the better
  candidate once the body is cleaned.

grid frequency:
  Per-cell Poisson is stable for V1, but sparse cells need pooled/regional dispersion or Bayesian shrinkage
  before the grid becomes product-grade.

damage:
  The legacy capex-weighted solar curve drives most loss uncertainty. It should be replaced by a curated,
  versioned damage_modeling curve before relying on exact EAL/PML levels.

event grain:
  One hail-day is acceptable now, but sub-daily storm splitting / storm-family identity may matter for
  portfolio correlation and event validation.
```

Better-way candidates:

```text
hazard:
  MYRORSS or another record extension, MESH de-biasing, physically bounded severity tail

frequency:
  spatial pooling / regional dispersion for the CONUS grid

coupling:
  storm-object footprints when available, especially for portfolio work

loss:
  calibrated solar hail curve, conditional damage uncertainty, policy terms / BI where in scope
```

---

## Assumptions And Revisit Triggers

Load-bearing assumptions:

```text
severe threshold = 25.4 mm
event grain = hail day / 24-hour max product
deep frequency = NegBin when over-dispersion detected
grid frequency = Poisson V1 default
solar on-hit exposure = full exposed array
damage curve = scalar mean, capex-weighted, legacy curve for current grid
financial terms = not included
```

Revisit triggers:

```text
MYRORSS or other record extension lands
MESH de-biasing / severity-tail model is adopted
pooled grid dispersion / spatial shrinkage is implemented
curated damage_modeling curve is swapped in
deductibles, limits, BI, or policy terms enter scope
hail x wind farm is added and needs point-cloud coupling
```

Authoritative registers:

- Deep-run assumptions: [`../../plans/hail/assumptions.md`](../../plans/hail/assumptions.md).
- Deep-run decisions: [`../../plans/hail/decisions.md`](../../plans/hail/decisions.md).
- Grid plans: [`../../plans/hazard_conus_grid/README.md`](../../plans/hazard_conus_grid/README.md).
- Hail x solar asset page: [`solar.md`](solar.md).

## Decision Stress-Test Questions

```text
source mode:
  are we using event footprints, point reports, or gridded cell evidence?

frequency:
  is p_hit kept as frequency information until M4?

severity:
  is hail size carried as conditional severity, not already expected loss?

damage:
  does the solar curve cap realistically and avoid total-loss extrapolation?

M4:
  are annual losses simulated with hit/miss coins and full conditional losses?
```

If any answer drifts toward `p_hit * loss` before M4, the model has fallen back into the old Method-0 shortcut.
