# M3 — Solar Damage · completion record

**Status:** ✅ built · 2026-06-13 · **Plan:** [`../m3_damage.md`](../m3_damage.md) · **Notebook:**
`Notebooks/wildfire/solar/m3_damage/01_damage`

## Objective

Map the coupled **fire-line intensity (kW/m)** → a **capex-weighted BoS damage ratio**, then the **conditional
loss given a fire**. Approximate curve now (InfraSure library), accurate curves later — like hail.

## What shipped (both assets, DD-W8)

- **Curve:** InfraSure `WILDFIRE × solar` — 6 BoS subsystem logistics on Byram kW/m, params read **live** from
  the canonical `master_curve_index` (not the lab copy → no drift), capex-weighted, **Channel-1 physical only**,
  `d = 10 m`. Legacy First-Street curve **discarded** (generic, wrong axis).
- **Anchored** (AW-29): subtracted each subsystem's `DR(0)` so `DR(0)=0` — the canonical raw logistics had a
  **non-physical ~5% floor** at zero intensity (`k·x0 ≈ 1.5–2.7` not sharp) that dominated the low-fire number.
- **30% TIV non-damageable** (AW-19; weights sum ~0.70) → anchored cap ≈ **0.56** of TIV.
- **LOTV kept clean:** emits the *conditional* loss given a fire — no `×λ` (M4's sampled engine reunites them).

## Key results

| | Hayhurst (low-fire) | Matrix (high-fire) | note |
|---|---|---|---|
| E[DR \| fire] (raw) | 5.8% | 11.2% | floor-inflated |
| **E[DR \| fire] (anchored)** | **1.0%** | **6.5%** | physical |
| ratio | masked | — | **~6×** (true severity gap) |

Anchoring caught a real artifact: Hayhurst's raw 5.8% was ~80% curve-floor (no-fire damage), not signal.
Owner confirmed the damage-curve library needs this fix and will address it in the revamp.

## Verification

Known-answer hand-recompute of `Asset_DR(2000 kW/m)` matches ✓ · `DR(0)=0` (anchored) ✓ · `DR ∈ [0,1]` monotone
saturating ✓ · `Σ prob = 1` ✓ · no `×λ` (LOTV) ✓.

## Decisions / assumptions

[DD-W8](../decisions.md) (curve = InfraSure BoS-weighted, **anchored**, approximate; legacy discarded) ·
[AW-19](../assumptions.md) (30% TIV non-damageable) · [AW-29](../assumptions.md) (anchoring) · [AW-20](../assumptions.md)
(Matrix TIV estimated via $/kWp) · curve confidence Low/Low-Med + `d=10 m` ±40% (carry).

## Deferred (named)

Accurate / RE-calibrated, **sharper-threshold** curves (the revamp — owner) · conditional-DR **distribution**
(not a scalar mean) · explicit `d`-sensitivity (defensible space) · smoke (Ch. 2) + PSPS (Ch. 3) channels.

## Next

**M4 — solar loss & metrics:** the **shared compound-Poisson/NegBin Monte-Carlo** (reused from hail) — sample
`N ~ Poisson(λ)` fires/yr, draw per-fire conditional loss from this M3 distribution, aggregate → EAL/VaR/PML/
TVaR off the **sampled** distribution, % of TIV. *The part the old repo broke — done right.*
