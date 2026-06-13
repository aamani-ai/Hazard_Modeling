# M2 — Solar Coupling · completion record *(a deliberately thin layer)*

**Status:** ✅ built · 2026-06-13 · **Plan:** [`../m2_coupling.md`](../m2_coupling.md) · **How it works:**
[`discussion/wildfire/03`](../../../extra/discussion/wildfire/03_m2_site_conditioned_coupling.md) ·
**Notebook:** `Notebooks/wildfire/solar/m2_coupling/01_coupling`

## Objective

Turn M1's per-asset hazard profile into the coupled handoff M3/M4 consume — and **document why this layer is
thin** (the common M0–M4 structure earning its keep by being honest about a light layer).

## The finding: M2 is thin (and correct)

FSim **pre-integrated** the events ([learning_logs/09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md))
**and** wildfire is **site-conditioned** (no spatial factor) → **M1 already produced `(λ, kW/m severity)` at
the asset.** No Minkowski overlap, no `p_hit`. So M2's V1 work is small and mostly *declaration*.

## What shipped (both assets)

- **On-site source / oozing:** use the **burnable footprint**; oozing is **moot at 270 m** (a pixel spans
  array + surrounding fuel) — acute only at WRC 30 m (our cross-check). Documented per asset (Hayhurst pixel
  oozed at 30 m, but the 270 m FSim spine already sources real fuel). ([AW-15](../assumptions.md))
- **Exposure fraction = 1.0** (whole-site on a fire; partial-burn deferred — [AW-28](../assumptions.md)).
- **Susceptibility = embedded `d = 10 m`** (the M3 curve's reference; explicit per-site `d` deferred —
  [AW-27](../assumptions.md); `I/d²`→`I/d` doc fix queued — [AW-17](../assumptions.md)).
- **Contract emitted** (`<asset>_wildfire_m2_summary.json` + `…_m2_coupled.parquet`): `{lambda_per_yr,
  fano, exposure_fraction, susceptibility_d_m, conditional kW/m severity}` — the schema M3/M4 read.

## Verification

`λ` passes through **unchanged from M1** (no spatial factor ✓) · `exposure ∈ [0,1]` ✓ · severity sums to 1 ✓.

## Deferred (named — the value of a thin, honest layer)

Fire-front sweep (partial burn, explicit `d`/`t`, real PML tail) · explicit per-site susceptibility `d`
(defensible space / fences, via site data/imagery) · currency adjustment for the stale FSim vintage
(AW-25/26) · heat-flux/temperature curves (Gen 3). All in [`assumptions.md`](../assumptions.md) AW-25–28.

## Next

**M3 — solar damage:** map the coupled **kW/m** intensity → a **BoS-weighted damage ratio** (curves from
`infrasure-damage-curves`), then `loss = DR × exposure × TIV`. The new work resumes at M3 (curve) + M4
(shared engine) — exactly as the thin-M2 finding predicts.
