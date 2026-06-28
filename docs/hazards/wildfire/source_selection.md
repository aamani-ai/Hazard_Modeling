# Wildfire Source Selection — V1

This page records why wildfire V1 uses public USFS FSim products as the hazard spine, and why other products
are cross-checks or deferred.

**Status:** decided for V1 · written 2026-06-26 · **Applies to:** wildfire M0/M1 for the deep per-asset run
and the planned CONUS grid.

---

## Decision In One Screen

Wildfire V1 uses **native USFS FSim** as the primary hazard source:

```text
FSim burn probability (BP)
  -> annual fire frequency

FSim FLP1-6 flame-length histogram
  -> conditional severity distribution

BP + FLP1-6
  -> M1 site hazard profile
```

The key reason is simple: FSim is a **pre-integrated stochastic fire simulation product**. It already gives
the two things wildfire M1 needs:

```text
frequency:  probability the site burns
severity:   flame-length distribution conditional on burning
```

That makes wildfire the opposite of hail. Hail has to self-build from raw radar. Wildfire can ingest a
finished hazard product, then spend its modeling effort on M2 site-conditioning and M3 damage.

## Source Roles

| Source | Evidence type | Current role | Why not more? | Revisit trigger |
|---|---|---|---|---|
| **USFS native FSim** (`RDS-2016-0034-3`) | Public raster product: BP + full FLP1-6 histogram, 270 m. | **V1 spine** for frequency and severity. | Inherits FSim assumptions/vintage; 270 m may miss fine site features. | Newer FSim vintage, finer public severity product, or site-scale validation evidence. |
| **WRC 2.0** (`RDS-2020-0016-2`) | 30 m published product view: BP/CFL/FLEP4/FLEP8. | Cross-check and fine-grain texture. | Flame-length histogram is collapsed; reconstructing FLP1-6 is lossy. | If 30 m intensity texture becomes more important than full histogram fidelity. |
| **Historical perimeters / incident records** | Observed fire footprints. | Context / validation candidate. | Not a stochastic annual BP + conditional severity field by itself. | If calibrating FSim bias or recent-vintage fire activity. |
| **Commercial wildfire risk products** | Vendor hazard/risk fields. | Deferred / possible validation benchmark. | Not needed for V1 and may mix hazard with vulnerability/loss. | If public FSim becomes insufficient for reportable underwriting. |

## Pressure-Test Status And Caveats

**Pressure-test status:** strong for V1 on main. The detailed source comparison and caveats live in the wildfire
discussion notes and M0 notebooks; this page carries the compressed decision.

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| Native USFS FSim BP + FLP1-6 | Annual burn probability and full conditional flame-length histogram. | Passes the M1-object test directly: frequency and conditional severity are already pre-integrated by the simulator. | **Selected spine.** | Inherits FSim assumptions, vintage, 270 m resolution, and discrete FLP tail. |
| WRC 2.0 BP/CFL/FLEP4/FLEP8 | Finer 30 m texture and current public product view. | Good cross-check, but severity is collapsed; FLP1-6 cannot be reconstructed without assumptions. | **Cross-check / texture source.** | Developed-area oozing and collapsed severity must be handled explicitly. |
| Historical perimeters / incident records | Observed fire occurrence and validation context. | Useful for sanity/currency, but not a complete stochastic annual BP + conditional severity raster. | **Validation/context only.** | Historical perimeter incompleteness and suppression/fuel changes limit direct rate use. |
| Commercial wildfire products | Potentially higher-fidelity underwriting fields. | Not public V1; provenance, licensing, vulnerability mixing, and reproducibility are unresolved. | **Deferred benchmark / swap-in candidate.** | Must pass provenance/security/source-role review before use. |
| Rebuilding fire seasons ourselves | Full event simulation and scenario control. | Not needed for V1 because FSim already ran the stochastic simulation and published the collapsed hazard fields. | **Rejected for V1.** | If FSim is materially stale or unavailable, this becomes a research program, not a small ingest change. |

### Caveat Ledger

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| FSim is pre-integrated. | We cannot inspect annual count dispersion or individual simulated fire seasons from BP/FLP alone. | Treat `fano = 1` as structural for the profile; do not pretend we fitted dispersion. | Access to event-level simulations or a source with annual scenarios. |
| Fuel/vintage currency. | Burn scars, fuel treatments, and development after the product vintage can move BP/severity. | Carry stationarity/fuel-currency caveat; no site-specific burn-scar correction in V1. | Updated FSim/WRC vintage or MTBS/fuel-currency correction. |
| 270 m native FSim resolution. | Small assets and boundary pixels can be sensitive to sampling rule. | Use footprint/zonal extraction and record edge-rule sensitivity; WRC provides texture cross-check. | Area-weighted extraction, finer native FLP product, or validated 30 m histogram source. |
| FLP1-6 is discrete and open-ended at the top. | The high-intensity tail is coarse. | Use the six-class severity distribution; continuous/EVT flame-intensity tail deferred. | Calibrated continuous fire-line-intensity distribution. |
| WRC developed-area oozing. | BP can appear in developed/nonburnable pixels while intensity is zero, creating a false no-loss read. | Use WRC as diagnostic/cross-check; do not let BP>0/intensity=0 silently drive severity. | Site-condition model that separates fuel, defensible space, and developed-pixel behavior. |
| Exogenous wildfire only. | Equipment-caused PV fires and electrical fires are a different loss process. | Scope V1 as geographic wildfire exposure; endogenous fire deferred. | Separate reliability/equipment fire peril is built. |

### Surprising Findings / Watchlist

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| The finer 30 m product is not automatically the better M1 spine. | WRC has texture, but native FSim carries the full FLP1-6 severity histogram. | A public 30 m product with full conditional severity histogram and clean developed-pixel treatment. |
| FSim is strong because it is pre-integrated, but that also hides dispersion. | We can read BP/severity, but cannot inspect event-year clustering from BP/FLP rasters alone. | Access to event-level simulated fire seasons or annual scenario outputs. |
| Wildfire source choice pushes more uncertainty into M2 site conditioning. | Fuel breaks, defensible space, developed pixels, and boundaries can dominate whether flame reaches value. | Owner/site-condition data or a validated site-conditioned coupling layer. |
| Fuel/vintage currency can become the main source risk. | Burn scars, fuel treatment, and development can stale a good historical hazard product. | Updated FSim/WRC vintage or explicit burn-scar/fuel-currency correction. |

## Access And Dependency Profile

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| USFS native FSim | USFS Research Data Archive / public raster download for `RDS-2016-0034-3`. | Public, no secret dependency; CC BY 4.0. | Raster layers at 270 m; manageable enough for direct provider fetch and local cache. | Direct public download; no large cloud fanout required for V1 asset runs. |
| WRC 2.0 | USFS/GeoPlatform ImageServer-style public raster access for `RDS-2020-0016-2`. | Public. | 30 m raster/product view; larger than native FSim but still direct-source accessible by footprint/window. | Cross-check/fine-grain read; not the severity runtime spine. |
| Historical perimeters / incident records | Public incident/perimeter archives where used. | Public, source-dependent. | Vector footprints/tables. | Context/validation only; not required for V1 runtime. |
| Commercial wildfire risk products | Vendor-specific. | License/vendor dependency. | Product-dependent. | Deferred; would require provenance, licensing, and source-role review. |

The access decision is part of why native FSim is practical for V1: it is already a precomputed hazard product
and small enough to fetch directly from the provider. The work is not a massive raw-data reconstruction; it is
source reconciliation, footprint extraction, and M2/M3 handling.

## Product Grain And Runtime Flow

The V1 source is not "all wildfire data." It is a narrow pre-integrated FSim hazard profile:

```text
source family:
  USFS FSim probabilistic wildfire products

selected V1 spine:
  RDS-2016-0034-3 native FSim rasters

selected layers:
  BP       = annual burn probability
  FLP1-6   = conditional flame-length histogram, given fire

temporal grain:
  pre-integrated annual probability, not a historical event calendar

spatial grain:
  native FSim about 270 m
  WRC 2.0 cross-check about 30 m, but with collapsed severity metrics
```

Interpretation:

```text
FSim BP
  ~= "what is the annual probability this pixel burns?"

FSim FLP1-6
  ~= "if it burns, what flame-length class does the simulator assign?"
```

The runtime flow is therefore a profile read, not a raw fire reconstruction:

```text
USFS public source products
  RDS-2016-0034-3 native FSim
    |
    | selected layers only:
    |   BP + FLP1 + ... + FLP6
    |   raw national rasters remain provider/source artifacts
    v
M0 extraction / aggregation
    |
    | deep asset:
    |   sample or zonal-average over the asset footprint / buffer
    |
    | CONUS grid:
    |   aggregate source pixels into benchmark 0.25 degree cells
    v
derived hazard artifacts
  BP profile
  FLP1-6 conditional severity profile
  QA/provenance manifest
    |
    v
M1
  lambda = -ln(1 - BP)
  severity = FLP1-6 -> fire-line intensity distribution
```

The tractability comes from using the product at the level FSim already solved: simulated fire seasons have
already been collapsed into annual burn probability and conditional severity rasters. We keep the extracted
profile / grid artifact, not a copy of every upstream raster, and we do not try to recreate FSim's simulated
fire seasons.

WRC 2.0 remains a useful companion product:

```text
WRC 2.0
  -> 30 m texture and developed-area / boundary diagnostics
  -> cross-check for BP, CFL, FLEP4, FLEP8
  -> not the V1 severity spine because FLP1-6 is collapsed
```

## Why Native FSim Beats WRC As The Severity Spine

WRC is tempting because it is 30 m. But for V1, severity fidelity beats pixel fineness.

```text
native FSim:
  BP + full FLP1-6 histogram
  -> complete conditional severity distribution

WRC:
  BP + CFL + FLEP4 + FLEP8
  -> useful texture, but severity is collapsed
```

Recovering six flame-length probabilities from WRC's collapsed metrics is under-determined. Native FSim gives
the histogram directly, so it is the cleaner M1 severity source. WRC remains useful as an independent/finer
view, especially for boundary and oozing checks.

## QA/QC Burden

FSim is a strong source, but not a magic source. V1 still carries these checks:

```text
[x] BP and FLP1-6 read from the same native FSim product where possible
[x] BP converted to annual rate with lambda = -ln(1 - BP)
[x] WRC used as cross-check, not reconstructed severity spine
[x] asset-boundary / footprint read preferred over centroid read
[x] oozing / developed-pixel issue handled in M2, not hidden in M1
[ ] currency adjustment for fuels and burn scars deferred
[ ] continuous / EVT severity tail deferred
```

## What This Page Prevents

```text
Mistake 1:
  "Use the 30 m WRC product because it is finer."
  -> not automatically; it loses the full severity histogram.

Mistake 2:
  "Treat FSim like a raw historical record."
  -> wrong; it is pre-integrated, so M1 assembles a profile rather than extracting events.
```

## Deep References

- Wildfire anchor: [`README.md`](README.md).
- Wildfire fundamentals: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Source framing: [`01_v1_scope_and_framing.md`](../../extra/discussion/wildfire/01_v1_scope_and_framing.md).
- FSim/WRC dictionary: [`02_fsim_wrc_data_dictionary.md`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md).
- Site-conditioned coupling: [`03_m2_site_conditioned_coupling.md`](../../extra/discussion/wildfire/03_m2_site_conditioned_coupling.md).
- Decisions: [`plans/wildfire/decisions.md`](../../plans/wildfire/decisions.md), especially DD-W3, DD-W4,
  DD-W5, and DD-W7.
- Lessons: [`LL07`](../../learning_logs/07_one_simulation_two_products.md),
  [`LL08`](../../learning_logs/08_oozing_developed_pixels.md), and
  [`LL09`](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md).
- Code: [`Notebooks/wildfire/`](../../../Notebooks/wildfire/m0_input_data/README.md).
