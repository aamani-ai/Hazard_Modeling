# Convective wind × Onshore wind

The **(peril × asset)** cell for convective wind — the first cell built end-to-end for this peril, and the one
where the **two sub-perils** play out on the *asset*. This page is the *asset* half — how tornado and strong
wind **couple to**, **damage**, and produce **loss** for a wind farm. The asset-free hazard layer (the 3-s
gust, the two thresholds, the catalog fork) is in the [convective wind anchor](README.md); read that first.

> **Coupling type: the fork.** A wind farm is a **sparse cloud of point turbines** scattered across a large
> lease (we have the turbine lat/longs) — so the two sub-perils couple differently. A **tornado** is a narrow
> path that clips only a *fraction* of the turbines → **areal hit-or-miss, path-aware**. **Strong wind** is a
> broad swath that covers the whole farm at once → **site-conditioned**. Same turbine, two coupling physics.

---

## How convective wind reaches a wind farm (M2 → M3 → M4)

```
            ┌──── M2 COUPLING (forks by sub-peril) ────┐   M3 DAMAGE         M4 LOSS
            │                                          │   (1 turbine,       (ONE joint
  TORNADO   │  areal hit-or-miss, PATH-AWARE           │    2 curves)         distribution)
    [T] ───►│  p_hit=(L+a)(w+a)/A · swept fraction     │──► DR_tornado ───┐
            │                                          │                  ├─► co-sampled MC ─► EAL·VaR·PML·TVaR
  STRONG    │  site-conditioned (whole farm exposed,   │                  │   (300k yr)        ($ & % of TIV)
   WIND [W]►│  p_hit≈1, read the site's ASCE RP gust)  │──► DR_strongwind─┘
            └──────────────────────────────────────────┘
```

**M2 — coupling (the fork).**

- **Tornado — areal hit-or-miss, path-aware.** A tornado is a thin path, so a wind farm's *bounding polygon*
  badly overcounts exposure. We use the **path-aware Minkowski** form per EF rating:

  ```
  p_hit(EF) = (L + a)(w + a) / A           λ_asset = λ_collection · E[p_hit]
  ```

  `L` = path length, `w` = path width (both per-EF from the SPC record), `a = √(farm area)`, `A` = the
  collection-region area (~π·150² km²). The collection-region *size cancels* in `λ_collection · p_hit`
  ([LL06](../../learning_logs/06_collection_region_size_cancels.md)). On a strike, only a **swept fraction** of
  the farm is in the path (≤ ~7 % even at EF5) — a sparse turbine cloud *diversifies* the tornado tail, the
  opposite of a dense solar polygon. Path-aware coupling is **orders of magnitude** above a naive centroid
  lookup (which under-counts a spread-out farm's strike exposure, AWN-23).

- **Strong wind — site-conditioned (honest pass-through).** A broad swath that reaches the region covers the
  whole farm, so there is **no hit/miss and no spatial factor**: `p_hit ≈ 1`, exposure = whole farm, and
  `λ_asset = M1 λ` unchanged. The site's gust severity was already read off the ASCE RP surface upstream (M1).

**M3 — damage (one turbine, two curves).** The turbine is one object with one capex split (rotor, nacelle,
tower, foundation, substation, electrical, civil), but the **two sub-perils get two fragility curves because
the failure mechanism differs (AWN-32)** — not merely the reach:

| | Strong wind [W] | Tornado [T] |
|---|---|---|
| **Mechanism** | feathered-survival overload (blades pitch edge-on; aero loads only) | rotation defeats feathering; vertical / pressure-drop / debris loads the design never anticipated |
| **Subsystems reached** | aero only (rotor, nacelle, substation, electrical) | **all** (incl. tower + foundation) |
| **Damage onset** | IEC survival ~60 m/s | lower, ~44 m/s |
| **Cap (max DR)** | **~0.65** (feathering survives straight-line wind) | **→ 1.0** at `L` (EF damage-calibrated) |

So at the *same* gust, a tornado is strictly more damaging than straight-line wind, and **both have
`DR(μ) ≈ 0`** — the payoff of the two-thresholds discipline. The curve is **Low confidence** and uncalibrated —
the dominant uncertainty in the cell ([anchor §5a](README.md#5-challenges--limitations)); calibrated turbine
curves from `infrasure-damage-curves` are deferred.

**M4 — loss & metrics (co-sampled into one distribution).** Both sub-perils run through **one** compound Monte
Carlo (300k years): per simulated year draw each sub-peril's event count (tornado NegBin if over-dispersed;
strong wind Poisson), draw each event's **full** realized loss through *its own* M3 curve (tornado adds
`swept_fraction × DR_tornado(gust) × TIV`; strong wind adds `DR_strongwind(gust) × TIV`), and **sum into the
same calendar year**. The two cardinal rules:

- **EAL is additive** (linearity of expectation): `EAL(T) + EAL(W) = EAL(joint)` ✓.
- **The tail is *not* additive** — read every tail metric off the **joint** sampled distribution. Summing
  per-sub-peril VaRs misstates the joint (VaR is non-coherent; here it understates by ~26 %). Never collapse a
  stream to its expected loss for a tail — that's the old repo's bug (DD-WN-13). Sparse tornado tail →
  **TVaR + SE are the honest reads** ([LL10](../../learning_logs/10_monte_carlo_effective_sample_size.md)).

The important boundary: **M3 defines the damage function; M4 calls it for every sampled event**. M4 is not a
new damage model. It is the annual-loss simulator that repeatedly applies the M3 curves:

```text
strong wind event:
  gust sampled from ASCE-derived severity
  event_loss = DR_strongwind(gust) * TIV

tornado event:
  gust sampled from EF / tornado severity
  event_loss = swept_fraction * DR_tornado(gust) * TIV
```

Because M4 has synthetic per-event losses, it can compute both AEP and OEP even for the ASCE strong-wind branch,
which has no raw historical event table. What that branch lacks is event identity across multiple assets, so
portfolio correlation remains deferred. The cross-hazard version of this contract is documented in
[`../m0_m4_event_loss_contract.md`](../m0_m4_event_loss_contract.md).

## The two deployments, side by side

The hazard-layer differences (collection region, the catalog fork) are in the
[anchor §3](README.md#3-how-we-model-it--two-deployments-and-the-sub-peril-fork). Here's how the *asset* result
lands:

| | Deep per-asset run | CONUS grid |
|---|---|---|
| **Asset** | a real wind farm at its true turbine locations | canonical wind farm at each valued cell |
| **Tornado coupling** | path-aware Minkowski over a 150-km collection region | per-cell / regional (same form) |
| **Strong-wind coupling** | site-conditioned, read the site's ASCE gust | site-conditioned, read the cell's ASCE gust |
| **MC** | 300k years, both sub-perils co-sampled | 250k-year target |
| **Status** | **built end-to-end** | **planned — not built** |

## Headline numbers — the proof-of-flow, *not* a portfolio

These are **methodology illustrations**, not a deliverable asset list. The notebooks run a couple of reference
sites only to *prove the flow* end-to-end before the real system is built; the model is **site-agnostic** and
will run on the full asset universe. The references bracket the hazard gradient, and the payoff is that **the
same engine reads correctly at both ends** — and that convective wind is, for a wind farm, a **tail peril**
(EAL tiny, PML/TVaR the story):

| Reference site | Hazard setting | tornado λ_asset | EAL (% TIV / $) | PML₂₅₀ (% TIV / $) | TVaR₉₉ (% TIV / $) | Reads as |
|---|---|---|---|---|---|---|
| **Traverse, OK** *(tornado alley, ~$1.40B)* | high tornado exposure | ~0.24 /yr | **0.064 %** / ~$0.89M | **3.99 %** / ~$55.9M | **4.88 %** / ~$68.3M | real catastrophic **tornado tail** |
| **Shepherds Flat, OR** *(Columbia Gorge, ~$1.18B)* | minimal tornado exposure | ~0.0025 /yr | **0.006 %** / ~$0.07M | 0.15 % / ~$1.8M | 0.35 % / ~$4.2M | **≈0 — the known-answer-low end** |

Read it as: a tornado-alley site carries a **real catastrophic tail** (`EAL ≪ PML` — the rare-but-violent
tornado signature), while a quiet site reads **≈0 across every metric** (correct — the hazard is genuinely
low). And at *both* sites, **strong wind contributes ≈0 to catastrophic loss** — the anchored-curve
known-answer (gusts never reach IEC survival; its real impact is operational, [anchor §5d](README.md#5-challenges--limitations)).
Same engine, directionally right at both ends — that is the validation, not the specific numbers.

- **Trust the *structure and direction*; treat the *tail magnitude* as a floor.** The tornado PML/TVaR is both
  **record-limited** (a biased ~75-yr SPC record) and **curve-limited** (Low-confidence M3), and EF rural-bias
  pushes the true tail *higher* ([anchor §5c](README.md#5-challenges--limitations)). Suitable for
  direction-setting and screening; not a final quotable tail.

## Assumptions specific to this pair

- Tornado coupling = areal hit-or-miss, **path-aware Minkowski + swept fraction** (AWN-21/23); strong wind = **site-conditioned**, exposure = whole farm (AWN-20).
- M3 = **one turbine, two sub-peril curves**, capex-weighted anchored logistic, `DR(μ)≈0`, tornado ≥ strong wind at every gust (AWN-24/25/32); **Low confidence** (AWN-26).
- M4 = both sub-perils **co-sampled into one joint distribution**; EAL additive, tail off the joint (DD-WN-13).
- TIV placeholder $1,400/kW (AWN-14); **single-site** — portfolio correlation across farms deferred (AWN-22).

## Deferred (V1.5 / V2)

Calibrated turbine fragility curves (`infrasure-damage-curves`) · the **strong-wind disruption/degradation
track** (curtailment + fatigue — the Performance tier) · portfolio correlation across farms · the separate
**hurricane** peril (watch the TC–tornado double-count flag, AWN-30) · financial terms (deductibles / limits /
BI) · a `solar/` sibling cell on the same catalog · the CONUS grid build + scaleout.

## Go deeper

- **Deep-run code:** [`Notebooks/convective_wind/wind_farm/`](../../../Notebooks/convective_wind/wind_farm/README.md) (M2 fork → M3 → M4).
- **Registers:** [`plans/convective_wind/assumptions.md`](../../plans/convective_wind/assumptions.md) · [`plans/convective_wind/decisions.md`](../../plans/convective_wind/decisions.md).
- **Reasoning:** [`discussion/convective_wind/02_coupling_buckets_and_wind.md`](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md) · [`04_aggregation_and_double_counting.md`](../../extra/discussion/convective_wind/04_aggregation_and_double_counting.md).
- **Hazard modeling choices:** [`modeling_choices.md`](modeling_choices.md).
- **Hazard layer:** [convective wind anchor](README.md).
