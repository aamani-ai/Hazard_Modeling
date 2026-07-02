# M1 — Catalog (per-asset hazard profile)

*Turn the M0 evidence into the **typed handoff the loss engine consumes**: per asset, a **frequency (λ)** + a
**conditional severity distribution** on fire-line intensity (kW/m), with a manifest declaring the catalog's
choices. Shared peril layer (built per-asset because wildfire is site-conditioned).*

**Where this sits:** [M0 evidence](../m0_input_data/) → **M1 (catalog)** → M2 coupling → M3 damage → M4 loss.
Plan: [`docs/plans/wildfire/m1_catalog.md`](../../../docs/plans/wildfire/m1_catalog.md).

## The structural twist (read first)

Hail M1 *extracted* discrete events and *fit* a rate from a short record. Wildfire doesn't — **FSim already
ran the event simulation** (≥20,000 seasons) and pre-integrated it into per-pixel **BP** (frequency) + **FLP**
(conditional severity). Doctrine confirms it (Hazard-Data-Ref: *"no track→swath step — the simulator outputs
the footprint statistics directly"*). So M1 here **assembles the per-asset hazard profile and declares the
process**, rather than building an event catalog. The notebook opens by making this explicit.

## What it does

- **Frequency:** `λ = −ln(1−BP)` per asset (≈ BP; site-conditioned → the rate comes from the site directly, no
  areal thinning). `frequency_process = poisson`, `fano = 1` ([DD-W7](../../../docs/plans/wildfire/decisions.md)).
- **Severity:** the FLP1-6 histogram → **fire-line intensity (kW/m)** via Byram — the conditional severity the
  engine samples in a fire year.
- **Edge-rule sensitivity check** ([AW-21](../../../docs/plans/wildfire/assumptions.md)): footprint mean under
  center-in / all-touched / area-weighted — confirm the lever is minor, documented.
- **Manifest** with the exact engine-contract keys (`lambda_per_yr`, `fano_factor`, severity distribution).

## Inputs → outputs

M0 parquets + cached FSim rasters → `data/wildfire/<asset>_wildfire_m1_catalog.parquet` (severity distribution)
+ `…_m1_manifest.json` (the typed contract M2/M4 read), for both assets.

**Next → M2 (solar coupling):** the site-conditioned step (susceptibility, oozing/surrounding-fuel) emitting
the `(p_hit, conditional intensity)` pair.

## What Wildfire M1 Asks

```text
M1 asks, for each asset:
  what burn probability BP applies over the footprint?
  how should BP convert to annual frequency lambda?
  what flame-length probability histogram applies given a fire?
  what kW/m intensity should represent each flame class?
  what manifest keys should M2 and M4 consume?
```

It does not ask:

```text
  what independent event perimeters should be built?
  what regional collection rate should be thinned to the asset?
  what does the damage curve do?
```

FSim already pre-integrates the simulated seasons into BP and FLP. M1 assembles that profile; it does not reconstruct
the full simulated fire catalog.
