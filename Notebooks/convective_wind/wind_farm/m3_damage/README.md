# M3 — Damage (shared turbine object, two sub-peril fragility curves)

*The damage layer — **one turbine** (one subsystem/capex split, one IEC anchor) but **two sub-peril fragility
curves**, because the damage a gust does depends on which sub-peril delivered it (DD-WN-16). Turns a 3-s gust into a
damage ratio `DR(gust, sub-peril)`. Like hail & wildfire, **curated, approximate, anchored** curves (*approximate
now, accurate later*) — the **dominant, irreducible uncertainty** and **greenfield** (the old repo had no turbine
wind curve). Structured as a reusable **turbine-fragility object** → graduates to the shared
`infrasure-damage-curves` library.*

**Where this sits:** M2 (coupling, forked) → **M3 (damage)** → M4 (loss). Plan:
[`docs/plans/convective_wind/m3_damage.md`](../../../../docs/plans/convective_wind/m3_damage.md). Notebook: [`01_damage`](01_damage.ipynb) (built).

## The two curves (assumed, AWN-26)
**Anchored subsystem logistic** `DR(v) = Σ wᵢ/(1+exp(-kᵢ(v-x0ᵢ)))`, capex-weighted (rotor 0.26 · nacelle 0.21 ·
tower 0.16 · foundation 0.12 · substation/electrical 0.09 · civil 0.07) — **shared**. The fork is **per sub-peril
fragility** (AWN-32 — mechanism, not just reach):
- **strong / straight-line wind** — feathered-survival **overload**: **aero** subsystems only, onset at the **IEC
  61400 survival speed** (~60 m/s), max DR ≈ 0.65 (cannot take tower/foundation).
- **tornado** — rotation **defeats feathering** + vertical / pressure-drop / debris loads, EF damage-calibrated:
  **all** subsystems, **lower onset & steeper** → `DR_tornado(v) > DR_strongwind(v)` at every gust, DR → 1.

## What `01_damage` found
- **Both anchored**: DR(μ=58 mph) ≈ 0 · DR_tornado(L=EF5) → 1 · DR_strongwind caps at ~0.65. (All 10 known-answer
  checks pass, incl. *tornado ≥ strong wind at every gust* and *tornado onset below strong-wind onset*.)
- **DR by EF (tornado vs strong wind):** EF2 ~36% / 7% · EF3 ~77% / 50% · EF4 ~94% / 65% · EF5 near-total / 65%.
  Tornado onset (DR≥5%) ≈ 44 m/s vs strong wind ≈ 54 m/s.
- **Strong-wind DR ≈ 0**: E[DR|event] ≈ 2e-4 → EAL ≈ **0.02% of TIV** — gusts stay below onset. The **M4
  known-answer check** (if strong-wind EAL comes out large, the curve is mis-anchored). Strong wind's real impact is
  the **deferred disruption/degradation track** (AWN-31), not this curve.
- **Approximate (Low confidence)** — the dominant uncertainty; IEC class assumed; calibrated curves from
  `infrasure-damage-curves` are the deferred upgrade.

## Inputs → outputs
M1/M2 thresholds + the old-repo subsystem split → `data/convective_wind/wind_m3_damage_curve_lut.parquet`
(gust → dr_tornado, dr_strongwind) + `wind_m3_damage_manifest.json` (capex split, per-sub-peril fragility, the
mechanism rule, the M4 known-answer check).

## Decisions & assumptions
[DD-WN-11](../../../../docs/plans/convective_wind/decisions.md) (anchored subsystem logistic) ·
[DD-WN-16](../../../../docs/plans/convective_wind/decisions.md) (one turbine, two sub-peril curves) · **AWN-24**
(subsystem blend), **AWN-9** (IEC anchor), **AWN-25** (operational state noted), **AWN-32** (sub-peril severity
differs), **AWN-26** (approximate now), **AWN-31** (strong wind ≈0). **Next → M4** (sample each sub-peril through its
own curve → one annual-loss distribution).
