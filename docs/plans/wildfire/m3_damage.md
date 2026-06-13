# M3 — Solar Damage (the active plan)

*Map the coupled **fire-line intensity (kW/m)** → a **capex-weighted BoS damage ratio**, then
`conditional_loss = Asset_DR × exposure × TIV`. Like hail: a **curated, approximate curve now** (the
InfraSure library), **accurate curves attached later**. This is the InfraSure wedge — no incumbent has
renewable-specific wildfire vulnerability curves.*

**Where this sits:** M0 → M1 → M2 → **M3 (solar damage)** → M4 loss. Built for both solar assets. Notebook:
`Notebooks/wildfire/solar/m3_damage/01_damage`.

## The curve (decision → DD-W8)

**Use the InfraSure `WILDFIRE × solar` library** (`infrasure-damage-curves`, canonical `master_curve_index` +
`research/WILDFIRE_x_SOLAR.md`), **not** the legacy curve.

- **Why not legacy:** `Solar|Wildfire|Direct` = a *generic First Street* curve (identical to Real-Estate and
  Wind), on the **wrong axis** (flame-length feet), degenerate fit → **discard** (matches the M0 salvage ledger).
- **Why InfraSure:** **6 BoS subsystem** logistic curves `DRᵢ(I) = Lᵢ/(1+exp(−kᵢ(I−x0ᵢ)))` on **Byram kW/m**
  (the M1/M2 axis), curated by **component-threshold aggregation** (engineering thermal standards — not fitted
  to our losses), **Channel-1 physical only, d=10 m** — matching our V1 scope. Mirrors hail's M3 (A22).
- **Approximate/temporary:** confidence **Low / Low-Medium**, `d=10 m` embedded (±40% — the dominant
  uncertainty), zero empirical RE-asset calibration. Carry these caveats; the accurate-curve revamp is deferred.

**The 6 subsystems (canonical params):**

| subsystem | L | k | x0 (kW/m) | confidence | capex weight (V1) |
|---|---|---|---|---|---|
| PV_ARRAY | 0.95 | 0.0013 | 2100 | low-med | 0.30 |
| MOUNTING | 0.80 | 0.0006 | 3600 | low | 0.10 |
| INVERTER_SYSTEM (most vulnerable) | 0.95 | 0.0021 | 1300 | low-med | 0.08 |
| SUBSTATION | 0.95 | 0.0014 | 1900 | low | 0.07 |
| ELECTRICAL | 0.65 | 0.0008 | 2500 | low | 0.08 |
| CIVIL_INFRA | 0.75 | 0.0009 | 2100 | low | 0.07 |

*(Weights are midpoints of the canonical ranges; **source them from `infrasure-damage-curves`, not the lab's
hard-coded copy, to avoid drift.** If the canonical index lacks point weights, use these midpoints and record it.)*

## The blend + the 30%-unmodeled-TIV (AW-19)

`Asset_DR(I) = Σ wᵢ · DRᵢ(I)` over the 6 subsystems. The weights sum to **~0.70**, so **~30% of solar TIV has
no wildfire curve**. **V1 default (A): keep weights as-is** — the unmodeled 30% contributes **0** damage;
`Asset_DR` caps at **~0.61** (61% of TIV) at saturation. Conservative, honest, and consistent with hail
(which capped ~34%). *(Alternative (B) renormalize-to-1.0 over-counts non-damageable land/civil — rejected for
V1.)* Recorded as [AW-19](assumptions.md); revisit (classify the 30% non-damageable vs gap) when accurate
curves land.

## Mechanism

For each asset, evaluate `Asset_DR` at **each FLP class's kW/m** (from M2's conditional severity) → a
**per-class conditional damage ratio** → `conditional_loss_class = Asset_DR(Iclass) × exposure × TIV`. This is
the **conditional loss distribution given a fire** — the M4 input.

> **LOTV (basics-spot-on):** M3 emits the **conditional** loss (full loss *given a fire*); it does **not**
> multiply by the occurrence probability/λ. Keeping `p` (occurrence) separate from severity is the rule the
> old repo broke; M4's sampled compound engine reunites them — never an expected-loss collapse here.

**Doc fix ([AW-17](assumptions.md)):** the curve doc's causal chain writes `q ∝ I/d²` (point source) — wrong
for a fire **front** (`∝ I/d`). The curve *params* already embed `d=10 m` (so the numbers don't change), but
fix the doc before any explicit heat-flux work.

## Verification

Known-answer: hand-compute `Asset_DR` at a fixed `I` (e.g. 2000 kW/m) and confirm the blend; `DRᵢ, Asset_DR ∈
[0,1]`, monotone, saturating; provenance-as-deliverable (cite curve source + confidence per subsystem); report
the conditional `E[DR | fire]` per asset and sanity-check the low-vs-high contrast (Matrix ≫ Hayhurst).

## Inputs → outputs

M2 coupled (conditional kW/m severity × exposure) + the InfraSure curves + TIV →
`data/wildfire/<asset>_wildfire_m3_damage.parquet` (per-class conditional DR + loss) +
`…_m3_summary.json` (the `Asset_DR` curve, weights, cap, conditional `E[DR|fire]`, provenance), both assets.

## Assumptions / decisions

**DD-W8** (curve = InfraSure BoS-weighted, approximate; legacy discarded) · [AW-19](assumptions.md) (30% TIV
unmodeled → non-damageable, V1) · curve confidence Low/Low-Med + `d=10 m` ±40% (carry) · **scalar DR per
class** (a *conditional-DR distribution* — uncertainty around the mean DR — is deferred).

## Deferred (named)

Accurate / calibrated curves (the damage-curve revamp) · conditional-DR **distribution** (not a scalar mean) ·
explicit `d`-sensitivity (defensible space → larger d) · smoke (Channel 2) + PSPS (Channel 3) channels — all
separate, deferred.

**Next → M4 (solar loss & metrics):** the **shared compound-NegBin/Poisson Monte-Carlo**, reused — sample
`N ~ Poisson(λ)` fires/yr, draw per-fire conditional loss from M3, aggregate → EAL/VaR/PML/TVaR off the
**sampled** distribution, % of TIV.
