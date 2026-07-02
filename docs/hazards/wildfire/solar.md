# Wildfire × Solar PV

The **(peril × asset)** cell for wildfire. This page is the *asset* half — how fire **couples to**,
**damages**, and produces **loss** for a solar farm. The asset-free hazard layer (BP, frequency, the
flame-length severity histogram, the FSim-ingest story) is in the [wildfire anchor](README.md); read that
first.

> **Coupling type: site-conditioned.** Wildfire is *not* a hit-or-miss footprint like hail. FSim already
> reports the burn probability and intensity **at the site**, so there is no overlap geometry to compute —
> the question is "given a fire here, how exposed and how damaged is the plant?" The hazard field is
> conditioned to the asset by location, then carried through damage and loss.

---

## How fire reaches a solar farm (M2 → M3 → M4)

```
  M2  COUPLING              M3  DAMAGE                M4  LOSS & METRICS
  "how exposed?"            "if it burns, how bad?"   "annual loss distribution"
  ┌──────────────────┐      ┌───────────────────┐     ┌──────────────────────┐
  │ site-conditioned │      │ kW/m → DR          │     │ compound-Poisson MC: │
  │ exposure = 1.0   │ ───► │ capex-weighted BoS │ ──► │ N ~ Poisson(λ);      │
  │ (whole-site)     │      │ logistic, ANCHORED │     │ per fire: draw class │
  │ no hit/miss      │      │ cap ~57% of TIV    │     │ → full conditional $ │
  └──────────────────┘      └───────────────────┘     └──────────┬───────────┘
                                                                 ▼
                                             EAL · VaR · PML · TVaR   ($ and % of TIV)
```

**M2 — coupling (site-conditioned).** There is **no Bernoulli hit/miss and no areal `p_hit`** — that's the
hail pattern, and it does not apply here. FSim's BP + intensity are already valued *at the footprint*, so M2's
job is to condition that field onto the asset and hand `(λ, conditional kW/m severity, exposure_fraction)` to
M3. V1 choices:

- **Exposure fraction = 1.0** — a fire that reaches the site exposes the whole plant. (Partial burn — a
  contiguous front taking only part of a large array — needs a fire-front sweep and is **deferred**, AW-28.)
- **Standoff `d = 10 m`** embedded as a line-source susceptibility (`q ∝ I/d`, not `1/d²` — a documented curve
  fix, AW-17). Explicit per-site defensible-space from imagery is **deferred** (AW-27).
- **Oozing guard (AW-15):** if the footprint pixel is "oozed" (developed land-cover suppressing intensity),
  the on-site severity is taken from the **surrounding fuel ring**, not the masked pixel — applied per-asset.
- **`λ` passes through unchanged** — site-conditioned means no spatial thinning.

**M3 — damage.** Fire intensity (kW/m) → damage ratio via a **capex-weighted Balance-of-System blend**
(InfraSure canonical `WILDFIRE × solar` curve): six BoS subsystems (PV array, mounting, inverter, substation,
electrical, civil), each a logistic on kW/m, weighted by capex share. Two things shape the result:

- **Anchored to zero (DD-W8 / AW-29).** The raw canonical logistics have a non-physical floor (`DR(0) ≈ 5–17 %`
  — damage with no fire), so each curve is shifted to `DR(0) = 0`. This is material: at one reference site it
  cut the conditional loss from 5.8 % → 1.0 %.
- **Caps at ~57 % of TIV.** The subsystem weights sum to ≈0.70, so ~30 % of asset value is non-damageable in
  V1 (AW-19); the modeled asset damage ratio saturates around 0.57.

This curve is **Low/Low-Medium confidence** — the dominant uncertainty in the whole cell (no empirical
solar-claim calibration; `d = 10 m` carries ±40 %). It is **Channel-1 physical fire only** — smoke-soiling and
PSPS grid de-energization are separate, deferred channels.

```
  conditional_loss_if_fire = E[ DR(kW/m) | fire ] × exposed_value      (exposed_fraction = 1.0)
  E[DR | fire] = Σ_class  P(class | fire) · DR_anchored(class kW/m)
```

Keep the two axes separate, exactly as in the anchor: `λ` (frequency) belongs to M4 sampling; `E[DR | fire]`
(conditional severity) belongs to M3. Never multiply them into a single "expected damage" and call it a loss —
that collapse is the old repo's bug (see **M4** below).

**M4 — loss & metrics.** Compound-Poisson Monte Carlo (the hail engine, ported): per simulated year draw
`N ~ Poisson(λ)` fires; for each fire draw its flame class from `P(class | fire)` and add the **full**
conditional loss; aggregate to AEP, take the max for OEP. Off the annual vectors we read EAL, VaR, PML, TVaR.
Known-answer checks pass (`EAL ≈ λ·E[loss|fire]`; zero-loss ≈ `e^(−λ)`; AEP ≥ OEP every year). The
**Method-0** shortcut (replace the distribution with its mean → "VaR99 ≈ EAL") understates the 1-in-100 by
**~6×** at a material site — which is exactly why we sample.

## The two deployments, side by side

The hazard-layer differences (spatial unit, frequency model) are in the
[anchor §3](README.md#3-how-we-model-it--two-deployments-of-one-engine). Here's how the *asset* result lands:

| | Deep per-asset run | CONUS grid |
|---|---|---|
| **Asset** | a real plant at its true footprint (boundary-zonal) | canonical: **100 MW** at each valued cell |
| **Footprint** | the real plant polygon (or capacity-radius circle if no boundary) | canonical dense 100 MW footprint |
| **`F`/coupling** | site-conditioned at the footprint | site-conditioned in the cell |
| **Frequency** | Poisson, `λ = −ln(1−BP)` at the site | Poisson, per-cell `λ` |
| **MC** | 300k years | 250k-year target |
| **Status** | **built end-to-end** | **planned — not built** |

## Headline numbers — the proof-of-flow, *not* a portfolio

These are **methodology illustrations**, not a deliverable asset list. The notebooks run a couple of
reference sites only to *prove the flow* end-to-end before the real system is built; the model is
**site-agnostic** and will run on the full asset universe. The two references are chosen to bracket the
hazard gradient — and the payoff is that **the same pipeline reads correctly at both ends**:

| Reference site | Hazard setting | BP (FSim) | EAL (% TIV / $) | PML₁₀₀ (% TIV / $) | Reads as |
|---|---|---|---|---|---|
| **Desert grassland** *(Hayhurst TX, ~$36.8M)* | near-zero fire | ~0.04 %/yr | **0.010 %** / ~$3.7k | 0.031 % / ~$11.4k | **~0 — the known-answer-low end** |
| **Sagebrush steppe** *(Matrix Pleasant Valley ID, ~$386M est)* | material fire | ~4.4 %/yr | **3.78 %** / ~$14.6M | 23.2 % / ~$89.4M | **material — real catastrophic tail** |

Read it as: a desert site lands at essentially **$0** (correct — fire is genuinely absent), while a
sagebrush-steppe site carries a **material EAL and a substantial 1-in-100 tail** (TVaR₉₉ ≈ 31 %). Same engine,
directionally right at both ends — that is the validation, not the two specific numbers.

- **Trust the *direction and contrast*; treat the *magnitude* as approximate.** Because FSim pre-integrates the
  climatology, these are **not record-limited** (unlike hail's short MRMS record) — but they **are
  curve-limited** by the Low-confidence M3 ([anchor §5a](README.md#5-challenges--limitations)) and the coarse
  6-class severity tail. Suitable for direction-setting and screening; **not** a final quotable loss.

## Assumptions specific to this pair

- Coupling = site-conditioned, **exposure = 1.0** (whole-site on a fire; partial-burn deferred, AW-28); standoff `d = 10 m` (AW-16/17); oozing guard per-asset (AW-15).
- Damage curve = capex-weighted BoS logistic, **anchored** to `DR(0)=0` (DD-W8/AW-29), ~30 % of TIV unmodeled → cap ~0.57 (AW-19); **Low/Low-Med confidence**, physical-fire channel only.
- TIV valuation basis unconfirmed; the material reference site's TIV is estimated at $1,483/kWp (AW-20).

## Deferred (V1.5 / V2)

Damage-curve calibration to PV fire claims · fire-front sweep (partial burn → a real PML tail) · continuous /
EVT severity tail · vintage-currency adjustment · smoke-soiling & PSPS channels · financial terms
(deductibles / limits / BI) · the CONUS grid build + scaleout.

## Go deeper

- **Deep-run code:** [`Notebooks/wildfire/solar/`](../../../Notebooks/wildfire/solar/m2_coupling/README.md) (M2 → M3 → M4).
- **Registers:** [`plans/wildfire/assumptions.md`](../../plans/wildfire/assumptions.md) · [`plans/wildfire/decisions.md`](../../plans/wildfire/decisions.md).
- **Reasoning:** [`discussion/wildfire/03_m2_site_conditioned_coupling.md`](../../extra/discussion/wildfire/03_m2_site_conditioned_coupling.md).
- **Hazard modeling choices:** [`modeling_choices.md`](modeling_choices.md).
- **Hazard layer:** [wildfire anchor](README.md).
