# M0-M4 Event And Loss Contract

This note documents the cross-hazard contract behind the notebooks. It explains what M0/M1 must hand to the
asset-specific layers, why a raw event catalog is useful but not always required, how M3 and M4 fit together,
and why a hazard return period is not the same thing as a loss return period.

Read this when a source looks unlike the last hazard. Hail has raw radar fields. Wildfire has a pre-integrated
burn-probability product. Strong wind has an ASCE return-period gust surface. Hurricane has synthetic storm
tracks plus observed frequency. Those are different routes, but they must all produce the same model object by
the time M4 runs.

---

## 1. The Contract In One Screen

By the end of M1, the hazard side must provide an event model:

```text
event count process
  how many potentially damaging events occur per year?

conditional event severity / intensity process
  given that an event occurs, how severe is it?

event identity / dependence information, when available
  which losses belong to the same storm, same outbreak, same fire season, or same portfolio event?
```

By the end of M2 and M3, the asset side must provide a loss rule:

```text
coupling rule
  does the event reach this asset, and at what local intensity / exposed fraction?

damage rule
  given local intensity, what damage ratio or event loss does the asset experience?
```

M4 combines those pieces into annual loss vectors:

```text
for each simulated year y:
  draw event count(s)
  for each event:
    draw or read event severity
    couple event to asset
    apply M3 damage function
    produce event loss L_i

  A_y = sum_i L_i       aggregate annual loss, AEP frame
  O_y = max_i L_i       largest occurrence loss, OEP frame

metrics:
  EAL      = mean(A_y)
  AEP-PML  = quantile(A_y)
  OEP-PML  = quantile(O_y)
  VaR      = quantile of the stated frame
  TVaR     = mean beyond the stated quantile
```

That is the common shape. The source path can vary.

---

## 2. Combine Events Before Metrics; Never Max EAL

For hazards with multiple sub-perils or overlapping damage agents, the model must combine **event losses**
before reading annual metrics. Do not combine finished metrics with a rule like `max(EAL_A, EAL_B)`.

The rule is:

```text
1. build event losses at the right event/component grain
2. apply any double-count guard at that grain
3. aggregate events into annual vectors
4. read EAL / PML / VaR / TVaR from the combined annual vectors
```

`max()` can be correct, but only at the right level:

```text
same event + same component + overlapping damage mechanism:
  event_component_loss = max(loss_from_agent_a, loss_from_agent_b)
  or event_component_loss = capped_sum(loss_a, loss_b, component_value)

different events or different components:
  add the losses, capped by component value / TIV where appropriate

annual metrics:
  EAL = mean(combined annual aggregate loss)
  PML / VaR / TVaR = read from the combined annual vector
```

What not to do:

```text
wrong:
  EAL_combined = max(EAL_riverine, EAL_pluvial)
  PML_combined = PML_wind + PML_surge
  TVaR_combined = max(TVaR_subperil_a, TVaR_subperil_b)
```

Those shortcuts lose dependence, double-counting, and same-year accumulation. EAL may be additive when streams
are distinct, but tail metrics are not additive and not max-able after the fact.

Examples:

| Case | Combination rule |
|---|---|
| Flood riverine + pluvial over the same ground | Co-sample the inland severity state, then use worse-source-wins or an additive-capped envelope at the depth/loss event grain. Do **not** use `max(EAL_R, EAL_F)`. |
| Hurricane wind + coastal flood surge from the same TC | Join by `event_family_id`; combine per subsystem/component with `max(wind, surge)` or capped component loss; then aggregate annual losses. |
| Convective wind tornado + strong wind | Co-sample both sub-peril streams into one annual vector. EAL attribution can split by sub-peril; PML/VaR/TVaR come from the joint annual vector. |
| Independent hazards with separate events | Add event losses in the simulated year, with TIV/component caps where needed; read metrics from the annual total. |

This is the clean boundary:

```text
max can be a per-event/per-component double-count guard.
max is not an annual metric aggregation method.
```

---

## 3. M1 Does Not Always Mean A Raw Event Catalog

The word `catalog` can be misleading. For some hazards, M1 really does emit event objects. For others, it emits
an equivalent statistical event model.

The contract is not:

```text
M1 must always contain historical rows like date, event_id, footprint, severity.
```

The contract is:

```text
M1 must provide enough event frequency and severity information for M2-M4 to generate event losses honestly.
```

Examples:

| Hazard/source path | What M0 sees | What M1 emits |
|---|---|---|
| **Hail / MRMS** | raw gridded MESH fields | hail-day event footprints, frequency, severity summaries |
| **Wildfire / FSim** | burn probability + flame-length histogram | annual burn probability / lambda plus conditional flame-length severity profile |
| **Strong wind / ASCE** | return period -> 3-second gust surface | Poisson count rate plus conditional gust severity distribution |
| **Tornado / SPC** | reported tracks, EF ratings, path lengths/widths | regional tornado rate, EF/severity mix, path geometry, dispersion |
| **Hurricane / RAFT + HURDAT2** | synthetic storm tracks plus observed storm rate | storm event field generator plus observed frequency anchor |
| **Flood / depth surfaces** | return-period depths or modeled depth curves | annual depth severity curve / event family where applicable |

So a raw event catalog is one way to satisfy M1, not the definition of M1.

### 3.1 The Three M0/M1 Input Modes

Before building a hazard, classify the M0/M1 source shape. Most confusion comes from treating every source as if
it were a raw event catalog.

| Input mode | What M0 sees | What M1 must do | Strength | Weakness |
|---|---|---|---|---|
| **Event-first** | historical or synthetic event objects: dates, tracks, footprints, severities | clean, QC, decluster, bias-correct, estimate event frequency/severity, preserve event identity | most flexible; best for AEP/OEP, portfolio correlation, named-event validation, compound joins, and custom asset coupling | more work and more judgment: short records, reporting bias, noisy geometry, duplicate events, missing low-severity events, and tail-fitting choices can dominate |
| **Return-period / surface-first** | already frequency-integrated intensity values: `T -> depth`, `T -> gust`, `T -> rainfall`, burn probability, etc. | convert the profile into the event-model contract or annual loss curve M4 can consume | cleaner starting point; strong for local tail anchors, engineering standards, and national coverage | less flexible; no event identity; EAL depends on interpolation/densification and event-frame assumptions that must be validated |
| **Hybrid** | a mix: event objects plus return-period/scenario surfaces or validation surfaces | keep event identity where needed, use RP/scenario surfaces for calibration, validation, or missing branches | balances storm identity with strong engineering surfaces; useful for compound hazards and validation | easiest to misuse: frequency bases can conflict, validation surfaces can accidentally become runtime sources, and double-counting must be guarded explicitly |

The classification is a modeling decision. It should appear in each hazard's `modeling_choices.md` because it
determines what M1 can honestly emit and what M4 can honestly claim.

### 3.1.1 Tradeoffs In Plain Language

Event-first is the most flexible path, but it is not automatically cleaner. It usually needs extra modeling work
before it becomes a trustworthy M1 object:

```text
event QC:
  remove duplicates, bad geometries, impossible intensities, unit mistakes, and source artifacts

event definition:
  decide what counts as one event, how to decluster, and how to handle multi-day / multi-cell systems

frequency correction:
  handle short records, under-reporting, population bias, radar/sensor changes, and over-dispersion

severity fitting:
  decide whether to use empirical sampling, EVT / POT, block maxima, bounded tails, or another severity model
```

That work is a cost, but it buys flexibility:

```text
named-event validation
portfolio correlation
event-family joins
asset-specific footprint coupling
separate AEP and OEP from actual event losses
```

Return-period / surface-first inputs move much of the hazard work upstream. They are often cleaner and more
standardized, but the assumptions move into the bridge:

```text
probability convention:
  is T = 1 / annual exceedance probability, MRI, or something else?

curve construction:
  how do we interpolate between source return periods?

densification:
  how do we infer missing frequent points such as 10/25/50-year depths?

event frame:
  annual maximum, compound-Poisson events, one event per year, or another process?

validation:
  do source anchors, external observations, or independent products support the converted curve?
```

That is the trade:

```text
event-first:
  more flexible, more event-real, more portfolio-ready
  but heavier QC and modeling burden

return-period / surface-first:
  cleaner and often better anchored for local tail intensity
  but less event-real and more dependent on bridge assumptions

hybrid:
  often the best practical path
  but only if frequency ownership and event-family ownership are written down clearly
```

### 3.2 What A Return-Period Source Means

A return-period source is not a loss model. It is a frequency-integrated **hazard intensity** statement:

```text
return period T
  -> annual exceedance probability p = 1 / T
  -> hazard intensity x_T at that probability
```

Examples:

```text
riverine flood:
  100-year depth grid = depth at 1% annual exceedance probability
  500-year depth grid = depth at 0.2% annual exceedance probability

strong wind:
  100-year / MRI gust = local 3-second gust speed at that hazard probability
```

That object is defensible because the upstream product has already performed the hydrologic, hydraulic,
meteorological, or simulation work. Our job is not to refit the raw physics unless we have better evidence. Our
job is to document:

```text
1. what probability convention the source uses
2. what intensity variable and units it emits
3. whether it is depth, water-surface elevation, discharge, gust, rainfall, burn probability, etc.
4. what interpolation / densification we add
5. what event identity, dependence, and portfolio work is lost
```

### 3.3 Example: Riverine Flood Return-Period Bridge

For riverine flood, the current solar M1/M2 path uses:

```text
FEMA BLE 100-year depth raster
FEMA BLE 500-year depth raster
FEMA BLE 10-year extent mask
USGS flow-frequency Q(T)
```

Those are not the same kind of object:

| Object | Meaning | What it gives |
|---|---|---|
| BLE 100-year depth raster | flood depth grid for the 1% annual-chance event | depth by pixel |
| BLE 500-year depth raster | flood depth grid for the 0.2% annual-chance event | depth by pixel |
| BLE 10-year extent mask | approximate wet/dry footprint for the 10% annual-chance event | inundated area, not depth |
| USGS `Q(T)` | peak flood discharge at selected annual exceedance probabilities | hydrologic scaling curve, usually in cubic feet per second |

The defensible chain is:

```text
M1:
  read the BLE depth field at real anchor probabilities
  read or derive USGS flow-frequency Q(T)
  preserve source tags and units

M2:
  sample the BLE fields over the asset footprint
  get D100 and D500 for the actual footprint
  use Q(T) to densify missing D10 / D25 / D50 points

M3:
  map depth -> damage

M4:
  sample annual severity from the loss-exceedance curve
```

The densification is the extra assumption. It says:

```text
Known:
  D100 and D500 from BLE depth rasters
  Q10, Q25, Q50, Q100, Q500 from USGS flow-frequency

Fit:
  D(T) = D100 * (Q(T) / Q100)^p

Choose p so:
  D(500) matches the BLE 500-year depth anchor

Then infer:
  D10, D25, D50
```

This is not inventing flood risk from nothing. It is using two real anchors from the hydraulic product and a
standard hydrologic frequency curve to fill the lower-return-period shape. It is still softer than having native
10/25/50-year depth rasters, so EAL should be marked softer than PML100/PML500.

### 3.4 Example: Strong-Wind Return-Period Bridge

For strong wind, the ASCE source is also a return-period / surface-first input:

```text
ASCE:
  return period / MRI -> local 3-second gust speed

M1:
  fit or assemble the return-level curve
  emit lambda + conditional gust severity distribution

M4:
  sample event counts and gust severities
```

The same common assumption appears:

```text
return-period profile -> event/loss generator
```

The hazard differs, but the modeling question is the same:

```text
How do we move from a frequency-integrated intensity profile to the count/severity object M4 needs?
```

### 3.5 Defensibility Checklist For Return-Period Inputs

When a hazard uses a return-period or pre-integrated source, document these before trusting M4:

```text
[ ] Source probability convention: annual exceedance probability, MRI, annual rate, or something else.
[ ] Intensity variable and units: depth, WSE, discharge, gust, rainfall, burn probability, flame length, etc.
[ ] Whether the product is an event catalog, a return-period surface, a simulated annualized product, or a hybrid.
[ ] Which points are directly read from source data and which points are interpolated / densified.
[ ] Whether interpolation is in return period, AEP, log-AEP, discharge, wind speed, or another physical variable.
[ ] Which metrics are strongly anchored by source points, usually PML at those return periods.
[ ] Which metrics rely on modeled curve shape, usually EAL and intermediate VaR/TVaR.
[ ] Whether event identity exists; if not, what portfolio, cross-asset, or compound-event work is deferred.
[ ] Whether a better source could replace the bridge later: more RP grids, local HEC-RAS, commercial grids,
    storm-resolved simulations, or owner/site survey data.
```

### 3.6 Source Anchors

The references below justify the vocabulary and units. They do not by themselves approve every interpolation
choice; the interpolation choice still belongs in the hazard's `modeling_choices.md`.

| Topic | Source anchor |
|---|---|
| FEMA Special Flood Hazard Area | FEMA defines SFHA as the area with a 1 percent or greater chance of flooding in a given year: <https://www.fema.gov/flood-maps/change-your-flood-zone>. FEMA's training glossary identifies SFHA zones A, AE, AH, AO, AR, V, VE, and A99: <https://emilms.fema.gov/is_0273/groups/157.html>. |
| FEMA flood depth grids | FEMA flood-depth guidance describes depth grids as the difference between water surface and ground, and states that flood depth grids may be produced for events such as 0.2%, 1%, 2%, 4%, and 10% annual chances: <https://www.fema.gov/sites/default/files/2020-02/Flood_Depth_and_Analysis_Grids_Guidance_Feb_2018.pdf>. |
| USGS `Q(T)` / flow-frequency | USGS StreamStats provides drainage-basin characteristics and flow-statistic estimates for selected sites: <https://www.usgs.gov/streamstats>. USGS flood-frequency reports estimate flood discharges at selected AEPs; the example USGS SIR maps 50%, 20%, 10%, 4%, 2%, 1%, 0.5%, and 0.2% AEPs to 2-, 5-, 10-, 25-, 50-, 100-, 200-, and 500-year recurrence intervals and reports discharge in cubic feet per second: <https://pubs.usgs.gov/publication/sir20255088/full>. |
| ASCE wind return-period / MRI gusts | ASCE's Hazard Tool describes three-second gust wind speeds at 33 ft / 10 m Exposure C and other MRI-based hazard values: <https://www.asce.org/publications-and-news/asce-hazard-tool/about>. |

### 3.7 Where The Reference Ends And The Model Begins

The source references prove the input object. They do not automatically prove every downstream conversion. The
model must keep this boundary explicit:

| Conversion | Source-backed part | Modeling-choice part | Validation / guardrail |
|---|---|---|---|
| BLE return-period depth -> M2 footprint depth | BLE/Risk MAP depth grid is a flood depth surface at stated annual-chance events. | Masking the raster to the asset footprint and reducing it to exposure fraction + conditional depth. | Preserve units/datum/source tag; check monotonicity; compare dry vs exposed controls; validate against observed high-water marks where available. |
| USGS `Q(T)` -> missing 10/25/50-year depths | USGS flow-frequency gives peak discharge estimates at selected AEPs, commonly reported in cubic feet per second. | The depth-discharge rating form `D(T) = D100 * (Q(T)/Q100)^p`, with `p` fitted to the BLE 500-year anchor. | Mark EAL softer than source-anchored PML; test sensitivity to rating form; replace with native multi-RP depth grids / local HEC-RAS when available. |
| ASCE return-period gust -> M1 strong-wind event severity | ASCE gives site-specific 3-second gust speeds by return period / MRI at 10 m Exposure C. | Fitting/approximating the return-level curve as an event severity distribution and deriving `lambda`. | Reproduce the ASCE source points; document the return-period convention; do not claim named-event identity or portfolio correlation from ASCE alone. |
| Hazard intensity -> asset damage | FEMA/USGS/ASCE define hazard intensity, not asset loss. | M3 damage curve maps depth or gust to damage ratio, with asset-specific fragility and TIV. | Reference damage-curve evidence separately; keep M3 swappable; report confidence and onset assumptions. |

So the robust statement is:

```text
source reference:
  proves what the input variable means

modeling bridge:
  converts that input into the M1/M2/M3 object we need

validation:
  checks that the bridge did not distort the source or overclaim precision
```

### 3.8 Confidence Statement For Return-Period Bridges

Every return-period / surface-first hazard should carry a short confidence statement. Put the general rule here,
then repeat the hazard-specific version in that hazard's `modeling_choices.md` and M4 notes.

```text
source variables:
  high confidence when the input comes from a trusted engineering / public-science product
  and the source variable, units, datum, and probability convention are preserved

bridge mechanics:
  reasonable V1 / medium confidence when the conversion is transparent, anchored to source points,
  monotone, sensitivity-tested, and externally checked where possible

production pricing / portfolio dependence:
  not final until uncertainty, event identity, dependence, and validation are strong enough for the use case
```

Where to document each piece:

| Layer / file | What to document |
|---|---|
| **M0 / source selection** | What the source actually says: variable, units, datum, probability convention, coverage, and source quality. |
| **M1 / modeling choices** | How the source is converted into frequency + severity, including interpolation, densification, tail fit, and event-frame assumptions. |
| **M2/M3** | How the hazard intensity is coupled to the asset and translated into damage; source confidence does not automatically transfer to damage confidence. |
| **M4** | Which metrics are source-anchored and which are bridge-driven. PML at source return periods is usually stronger than EAL when EAL depends on densified lower-return-period points. |

For the current bridge examples:

```text
flood riverine:
  source variables: strong where BLE / USGS coverage exists
  bridge mechanics: medium, because 10/25/50-year depths are densified from Q(T)
  production upgrade: native multi-RP depth grids, local HEC-RAS, or uncertainty propagation

strong wind:
  source variables: strong for ASCE return-period 3-second gust at the stated basis
  bridge mechanics: medium, because the ASCE curve is expressed as a lambda + severity sampler
  production upgrade: alternate tail fits, ASCE-point reproduction checks, and event-resolved catalogs if
  portfolio/event-family dependence matters
```

---

## 4. Example: ASCE Strong Wind

For strong / straight-line wind, ASCE gives a local return-level curve:

```text
return period T -> 3-second gust speed V
```

For Traverse Wind Energy Center, the M0 table includes:

```text
10 yr        -> 33.93 m/s
100 yr       -> 42.25 m/s
700 yr       -> 49.17 m/s
3,000 yr     -> 53.64 m/s
10,000 yr    -> 58.16 m/s
1,000,000 yr -> 75.46 m/s
```

M0 only reads that surface. No loss, no damage, no Monte Carlo.

M1 then converts the return-level curve into the event-model contract. The notebooks fit the ASCE points with:

```text
V(T) = c0 + sigma * ln(T)
```

This is a Gumbel / exponential-tail representation of the same ASCE return-level curve. For Traverse, the
M1 strong-wind contract is:

```text
event threshold mu = 25.92 m/s   # NWS 58 mph severe-wind threshold
lambda             = 0.9035 events/year
sigma              = 3.581
xi                 = 0.0
fano               = 1.0
```

M4 can now sample synthetic strong-wind events:

```text
N_events_this_year ~ Poisson(0.9035)

for each event:
  gust = 25.92 + Exponential(3.581)
```

That sampler is not an independent new wind climatology. It is the ASCE return-period curve expressed in the
form the annual-loss engine can consume.

Why this conversion is necessary:

```text
ASCE table:
  "the 100-year gust is 42.25 m/s"

M4 needs:
  "how many events occur this year?"
  "what gust does each event have?"
  "what loss does each event produce?"
```

The first object is a hazard profile. The second is an event model.

---

## 5. Where The Distribution Is Used

The event distribution is used where annual losses are generated, not everywhere.

For the ASCE strong-wind example:

| Layer | What happens | Distribution used? |
|---|---|---|
| **M0** | Query ASCE map at a site or grid cell; save return-period gust values. | No. M0 reads source evidence. |
| **M1** | Fit / assemble the ASCE curve into `lambda + severity_distribution`. | Yes, as the event-model contract. |
| **M2** | Declare site-conditioned coupling: `p_hit = 1`, `exposure_fraction = 1`, `lambda_asset = lambda_M1`. | No extra hit/miss distribution. |
| **M3** | Define the turbine damage curve: `gust -> damage ratio`. | Usually deterministic in V1; can later include conditional damage uncertainty. |
| **M4** | Draw event counts and event gusts, call M3 for each event, aggregate annual losses. | Yes. This is where synthetic years/events are sampled. |

The same idea holds for other hazards. The source path changes, but M4 needs an event-loss generator.

---

## 6. Why M2 Is Thin For Some Hazards

M2 answers:

```text
does this hazard event reach this asset, and at what local intensity / exposure?
```

For hail and tornado, the event has a finite footprint or path. It can miss the asset. M2 must compute a
hit probability or overlap:

```text
hail:
  severe footprint overlaps solar polygon?

tornado:
  path-aware hit probability and swept fraction over turbine cloud
```

For strong wind, the ASCE curve is already local to the site. The source says:

```text
at this site, the T-year gust is V
```

There is no extra footprint that might land elsewhere and miss the farm. So M2 is intentionally thin:

```text
p_hit = 1
exposure_fraction = 1
lambda_asset = lambda_M1
```

That thinness is not a shortcut. It prevents us from applying a hail/tornado spatial formula to a
site-conditioned wind surface.

---

## 7. M3 Is Separate, But M4 Calls It

M3 defines the conditional damage / loss function:

```text
local intensity -> damage ratio or event loss
```

M4 does not make the damage-curve decision. M4 repeatedly applies the M3 function while generating annual
losses.

Example for strong wind:

```text
M4 samples gust = 38 m/s
M4 calls M3: DR_strongwind(38 m/s) ~= 0
event_loss = DR * TIV
```

Example for tornado:

```text
M4 samples EF3-range gust
M4 calls M3: DR_tornado(gust) is high
event_loss = swept_fraction * DR * TIV
```

Conceptually:

```text
M3 = the damage function
M4 = the annual-loss simulation that uses that function
```

Implementation may inline a simple M3 curve inside an M4 notebook during prototyping, but the contract should
still stay separate. That separation lets us swap a better damage curve later without rewriting the annual-loss
engine.

---

## 8. AEP/OEP Do Not Require A Historical Event Catalog

OEP needs per-event losses inside each simulated year:

```text
O_y = max single-event loss in year y
```

Those per-event losses can come from a raw historical/synthetic event catalog, or from a statistical event
model.

For ASCE strong wind:

```text
N_events ~ Poisson(lambda)
for each event:
  gust ~ conditional severity distribution
  event_loss = DR(gust) * TIV
```

Those synthetic event losses are enough to compute single-site AEP and OEP metrics.

What we lose without raw event identity:

```text
storm date / name
same event hitting multiple assets
same outbreak producing multiple sub-peril losses
portfolio correlation
cross-hazard event-family joins
validation against named historical events
duration / outage timing
```

That is acceptable for a single-site V1 when the upstream return-period surface is trusted. It is not enough
for portfolio aggregation or event-family accounting. Those require event identity or a separate dependence
model.

---

## 9. Hazard Return Period Is Not Loss Return Period

A hazard return period is attached to an intensity:

```text
100-year ASCE gust = 42.25 m/s
100-year flood depth = 2.0 ft
100-year rainfall depth = 8 inches
```

A loss return period is attached to an annual loss after coupling, damage, value, and aggregation:

```text
PML100 = 99th percentile annual loss
PML250 = 99.6th percentile annual loss
```

They are not the same. A 100-year gust can produce near-zero loss if the damage curve has not reached onset. A
moderate event can produce large loss if coupling and fragility are unfavorable. Multiple events can accumulate
in the same year. M4 exists because the loss distribution is not a direct relabeling of the hazard
return-period curve.

For strong wind on a turbine, this distinction is the main lesson:

```text
ASCE can show frequent severe-wind gusts,
but M3 says most are below turbine damage onset,
so M4 returns near-zero catastrophic physical loss from strong wind.
```

The operational impact of those winds may still be real, but that belongs to the deferred disruption /
degradation / Performance-tier track, not the catastrophic physical-loss M4.

---

## 10. Checklist For A New Hazard x Asset Pair

Before building or reviewing M4, answer these:

```text
[ ] What is the M1 event count process?
[ ] What is the M1 conditional severity / intensity process?
[ ] Did it come from raw events, a pre-integrated surface, a return-period profile, a stochastic catalog, or a proxy chain?
[ ] Is any raw event identity available? If not, what portfolio/correlation work is deferred?
[ ] What coupling type does M2 use: areal hit-or-miss, field-intensity, or site-conditioned?
[ ] Does M2 change event frequency, local intensity, exposed fraction, or all three?
[ ] What exact intensity does M3 consume?
[ ] Is M3 deterministic mean damage, or does it include conditional damage uncertainty?
[ ] Does M4 sample full event losses, not just expected losses?
[ ] Are AEP and OEP read from annual vectors, not computed as unrelated one-off metrics?
[ ] For multi-sub-peril or compound hazards, are event/component losses combined before metrics are read?
[ ] Is any use of max() limited to event/component double-count guards, not max(EAL) or max(PML)?
[ ] Are hazard return periods clearly distinguished from loss return periods?
```

If those answers are clear, the hazard can use the standard interface even when its physics and source data are
different from the last hazard.
