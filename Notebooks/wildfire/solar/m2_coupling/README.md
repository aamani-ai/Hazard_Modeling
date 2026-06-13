# M2 — Solar Coupling *(a deliberately thin layer)*

*Turn M1's per-asset hazard profile into the **coupled handoff** M3/M4 consume. For a site-conditioned peril
this is **thin** — M1 already did the coupling (FSim pre-integrated; no areal "miss"), so M2 is mostly
**declaring assumptions + documenting why it's thin + what's deferred**. That honesty is the point of the
common M0–M4 structure.*

**Where this sits:** M0 → M1 → **M2 (solar coupling)** → M3 damage → M4 loss. Built for both solar assets.
Plan: [`docs/plans/wildfire/m2_coupling.md`](../../../../docs/plans/wildfire/m2_coupling.md) · How it works:
[`discussion/wildfire/03`](../../../../docs/extra/discussion/wildfire/03_m2_site_conditioned_coupling.md).

## Why thin (vs hail's Minkowski-heavy M2)

FSim pre-integrated the events **and** wildfire is site-conditioned (no spatial factor) → **M1 already produced
`(λ, kW/m severity)` at the asset.** No overlap to compute. M2's V1 work: confirm the on-site source (burnable
footprint; oozing is moot at 270 m), set **exposure = whole-site**, **embed `d = 10 m`** susceptibility, and
emit the clean handoff. The heavy physics (fire-front sweep; explicit site-feature `d`; currency) is
**deferred** and named ([AW-25–28](../../../../docs/plans/wildfire/assumptions.md)).

## Inputs → outputs

M1 catalog + manifest (+ M0 WRC oozing flag) → `data/wildfire/<asset>_wildfire_m2_coupled.parquet`
(conditional kW/m severity × exposure) + `…_m2_summary.json` (the λ + exposure + susceptibility contract),
both assets.

**Next → M3 (solar damage):** map the coupled kW/m intensity → BoS-weighted damage ratio.
