# M3 — Damage (the plan)

*Phase 4 of the flood × solar build. Map the M2 coupled **flood depth** → a **capex-weighted subsystem damage
ratio**, then `conditional_loss = exposure × Asset_DR(conditional_depth) × TIV`.* Per-phase loop
([feature_workflow](../../workflows/feature_workflow.md)).

> **Curve = the canonical `infrasure-damage-curves` RIVERINE_FLOOD × solar set** (`FLOOD_x_SOLAR.md`, in
> `master_curve_index.json`, priority 4) — **the same library hail / wildfire / convective_wind use**. A22's "no
> solar flood curve exists" is **superseded**: the library added it (medium confidence). So flood uses the house
> recipe with real canonical curves, not HAZUS-from-scratch.

## The recipe (house-standard, all perils)
- Per-subsystem logistic `DRᵢ(x) = Lᵢ/(1+exp(-kᵢ(x-x0ᵢ)))` on **flood depth (ft) above ground**, **anchored** so
  `DR(0)=0`.
- `Asset_DR(x) = Σ wᵢ·DRᵢ_anchored(x)` with **NREL capex weights** (peril-independent; vendored from
  `hail_solar_asset_capex_weighted.json`). Subsystems with no flood curve → **0** (flood-immune).
- `conditional_loss = exposure_fraction × Asset_DR(conditional_depth) × TIV` (no double-count — M2 already split
  exposure from conditional depth).

## The flood inversion (why `x0` matters)
The library bakes **component elevation into `x0`** — so **no separate mount-height step is needed**:

| subsystem | L | k | x0 (ft) | reading |
|---|---|---|---|---|
| INVERTER_SYSTEM | 0.95 | 3.5 | **0.75** | pad-mounted → drowns shallow (dominant) |
| SUBSTATION | 0.95 | 2.5 | 1.5 | transformer oil contamination |
| PV_ARRAY (SAT horiz.) | 0.9 | 1.8 | 2.5 | panels survive shallow; **flood-stow x0 7 ft = mitigation** |
| CIVIL_INFRA | 0.7 | 1.2 | 2.0 | scour/roads |
| ELECTRICAL (cables) | 0.55 | 1.0 | 3.0 | underground — resilient |
| MOUNTING, SCADA | — | — | — | no curve → flood-immune (0) |

## Decisions / assumptions
- **PV variant = single-axis horizontal stow** (typical utility tracker). Flood-stow (x0 7 ft) deferred to a
  resiliency-measures pass.
- **TIV** from $/MW (Hayhurst's hail basis $1.483 M/MW for coherence; Elizabeth estimated by capacity).
- **Confidence: medium**; **duration unmodeled** (Gen-1, a known gap); `value ∝ area` exposure inherited from M2.

## Built
`solar/m3_damage/01_damage` — curve vendored to `data/flood/damage_curves/flood_solar_asset_capex_weighted.json`;
result: Elizabeth conditional loss **2.6% (100-yr) → 4.4% (500-yr) of TIV**; Hayhurst 0.1–0.6%.

## Next
**M4 (loss & metrics)** — feed the depth-at-RP conditional losses through the **shared MC** →
EAL / VaR / PML / TVaR (% of TIV). Event-model bridge **settled** (JD-FL-7): inland (riverine + pluvial) =
**annual-max MC** off a **5-point densified** RP curve (JD-FL-8, not 2-point); coastal = **compound-Poisson
surge×wind** (JD-FL-12); total = inland + coastal.
