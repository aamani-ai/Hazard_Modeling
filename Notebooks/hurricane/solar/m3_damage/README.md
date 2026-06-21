# M3 — Severity / Damage (M2 → M3)

*Given a storm's wind reaches the asset, **how bad is it?** The layer that turns a 3-second gust into a damage ratio
and a conditional dollar loss.*

**Where this sits:** [M0 evidence](../../m0_input_data/) → [M1 catalog](../../m1_catalog/) →
[M2 coupling](../m2_coupling/) → **M3 (severity / damage)** → [M4 loss & metrics](../m4_loss_metrics/).

## The plain-English question

M2 said the whole farm sees one gust (`value_exposed_fraction = 1.0`). M3 says *how much it costs*: run each event's
**3-second gust** through a **damage curve** to get a capex-weighted asset damage ratio, then × asset value → the
conditional dollar loss.

## What we did

Built a **capex-weighted subsystem** `gust → damage ratio` curve from the canonical library and applied it per event.
Output: a per-event **damage ratio** + **conditional loss** (the *full* loss if the storm hits). The asset DR **caps
at ≈48%** of value; the worst storm in the catalog (a ~175 mph direct Cat-5 at Everglades) reaches **≈41% of TIV**.
Severity is steeply gust-driven, so the violent-tail storms carry most of the potential loss.

## Why this way (two rules that define the stage)

1. **Curve-driven, not fitted.** We have *gusts*, not a history of what hurricanes cost this plant — so we don't fit
   losses. We take the **HURRICANE × SOLAR** group from [`infrasure-damage-curves`](../../../../infrasure-damage-curves)
   — empirically anchored (FPL Hurricane Ian; Ceferino et al. 2023) on the
   **3-s-gust** basis (*exactly* our M1/M2 intensity, no unit mismatch). **Its provenance is the deliverable — change
   the curve, change the losses.**
2. **Conditional, full, and `λ`-free.** This is the loss *if it hits* — the **full** conditional loss. We **never**
   fold in the event rate `λ` here. Frequency (`λ`) and severity (conditional loss) stay separate until the M4
   Monte-Carlo combines them — multiplying them is the Method-0 shortcut that breaks the tail.

## The curve (v1) — 🟡 PROVISIONAL (owner-flagged for replacement)

**Capex-weighted subsystem blend** (`damage_curves/hurricane_solar_asset_capex_weighted.json`): logistic
`DR(x)=L/(1+exp(-k(x-x0)))`, anchored `DR(0)=0`, over the **wind-damageable** subsystems —
**PV array** (`w 0.35`, headline curve `pv_array_tracker_stow`, x0 148 mph), **mounting/racking** (`w 0.15`, x0 120),
**substation** (`w 0.08`, x0 120). The remaining **~42%** (inverters, cables, civil) is **wind-immune → 0**, so the
asset DR **saturates at ≈48%** (no total-loss representation).

- **Headline** = `pv_array_tracker_stow` (x0 148 — assumes the tracker stows; FPL-Ian-anchored). The harsher
  `tracker_midtilt` (x0 115, stow-failure) is a **recorded sensitivity**, not the headline (both are placeholders —
  no range, per the point-estimate convention of the other cells).
- These are **medium-confidence placeholders to be replaced** ([ATC-14](../../../../docs/plans/hurricane/assumptions.md)) —
  the **dominant, irreducible uncertainty** of the build.

## Inputs → outputs

[M2 coupled events](../m2_coupling/) (gust + `value_exposed_fraction`) + `tiv_usd` ($110.5M Everglades) →
`data/hurricane/tc_m3_damage.parquet` (event + `conditional_DR` + `conditional_loss_usd` + a `conditional_DR_stowfail`
sensitivity column) + the vendored curve JSON + `tc_m3_manifest.json`.

## Deferred (stated, not hidden)

- **The replacement curve** — the provisional library curve is the dominant uncertainty; swapping it (then re-running
  M3/M4) is the top V1→V2 upgrade.
- **A loss-side benchmark (Hazus / NRI)** — the independent sanity check on the loss number (the loss analog of the
  ASCE hazard validation); not yet applied here.
- **Total-loss / debris-driven remainder** — the ≈48% cap omits catastrophic destruction of the wind-immune
  electrical/civil share; a debris-vulnerability term would lift it.
- **Tracker stow as a probability** (vs the deterministic curve choice) — not modeled; premature on a placeholder curve.
- **Real footprint + registry TIV** — capacity-circle + $/MW estimate for now (% of TIV is the robust metric).

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_damage`](01_damage.ipynb) | library hurricane × solar capex-weighted curve → per-event damage ratio + conditional loss; known-answer checks (incl. the DR-cap) | the damage parquet + vendored curve + manifest |

## Key

Plan: [`m3_damage.md`](../../../../docs/plans/hurricane/m3_damage.md). Source-agnostic (the gust has no memory of its
peril) — shares the **3-s-gust** basis with convective wind ([DD-WN-9](../../../../docs/plans/convective_wind/decisions.md)).

## Assumptions (this layer)

[ATC-14](../../../../docs/plans/hurricane/assumptions.md) **library HURRICANE × SOLAR, capex-weighted** (PV 0.35 +
mounting 0.15 + substation 0.08; rest ≈ wind-immune → DR caps ~48%), **PROVISIONAL** — headline `tracker_stow`
(x0 148), stow-fail (x0 115) recorded as sensitivity · [ATC-4](../../../../docs/plans/hurricane/assumptions.md)
3-s-gust observable · [ATC-2](../../../../docs/plans/hurricane/assumptions.md) physical loss only.

**Next → M4 (loss & metrics):** the storm-resolved compound-Poisson Monte-Carlo — `Poisson(λ)` events × full
conditional loss → annual-loss vectors → EAL / VaR / PML / TVaR (% of TIV + $).
