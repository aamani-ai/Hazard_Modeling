# M2 — Coupling (M1 → M2)

*Does each event actually reach **our** asset — and with what probability? The layer that turns a regional
event catalog into the **asset's own** hazard.*

**Where this sits:** [M0 evidence](../../m0_input_data/) → [M1 catalog](../../m1_catalog/) → **M2 (coupling)** →
M3 damage → loss & metrics.

## The plain-English question

The M1 catalog has hail events scattered across the 50-mile region around Hayhurst. M2 asks, for each one:
**would its hail footprint land on our solar farm?** Hail is *areal hit-or-miss* — a storm either covers the
site or misses it. So the whole job of M2 is to compute, per event, a **hit probability**.

## What we did

For every event we computed **`pᵢ` — the probability that event's footprint covers the asset.** Bigger
footprint → more likely to hit (the region's biggest event: **~9.7%** chance; the smallest: **~0.01%**;
mean ≈ 0.9%). That is *all* M2 produces: a probability per event, plus carrying each event's hail size
forward for the damage step. Summed over the 158-event catalog, the **expected asset-hits `Σpᵢ ≈ 1.39`**,
and the **fitted annual rate `λ_asset = λ_collection · E[p] = 0.26/yr`** (~1 hit every 3.8 yr).

## Why this way — and not the naive way (two things that matter)

**1. The formula accounts for the asset's size.** A footprint of area `F` covering an asset of size `s`,
dropped in a region of area `A`, hits with probability:

> **`p = (√F + √s)² / A`**  (Minkowski)

The old repo used **`F/A`** — treating the asset as a dimensionless *point*. That **under-counts** the hit
chance (it ignores the asset's own size), badly for small footprints (here, up to **1.8×** too low). Fixing
this is part of why the rebuild exists; we verify the correct formula against hand-checked answers.

**2. It is a *probability*, never a loss multiplier — the single most important rule.** The hit probability
belongs to **frequency** (how *often* we get hit), not severity (how *bad*).

- ❌ **Wrong (the old repo):** `loss = pᵢ × damage`. This averages away the hit-or-miss coin-flip — it
  **destroys the tail** (VaR / PML) while still looking right on the average (EAL).
- ✅ **Right (ours, in the Phase-5 Monte Carlo):** flip a weighted coin `hit ~ Bernoulli(pᵢ)`; **if it hits,
  apply the FULL damage; if it misses, zero.** `pᵢ` is the coin's bias, never multiplied into the dollars.

`A` also **cancels** in `λ_asset = λ_collection · p` (rate grows with the region, `p` shrinks with it), so
the 50-mile radius doesn't bias the answer — as long as rate and `p` use the *same* region.

## Inputs → outputs

M1 catalog (each event's footprint `F`) → `data/hail/hayhurst_hail_m2_coupled.parquet` (each event + its
`pᵢ` + hail size, ready for M3) + `…_m2_summary.json` (region area `A`, asset `s`, `Σpᵢ`, assumptions).

## Deferred (stated, not hidden)

- **A longer, NOAA-calibrated rate** — `λ_collection` is now **fitted** on the ~5.65-yr MRMS record (so
  `λ_asset = 0.26/yr` is real but record-limited); the longer, bias-corrected record is the next lever
  ([DD-3 Stage 2](../../../../docs/plans/hail/decisions.md)).
- **Exposed fraction** — we assume *full* exposure on a hit, sound here because the farm (~0.5 km²) is tiny
  vs a hail swath (hundreds of km²); it matters for larger assets / line geometry.

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_coupling`](01_coupling.ipynb) | per-event Minkowski `pᵢ` + old-repo comparison + known-answer checks + geometric cross-check | the coupled parquet + summary |

## Key

Plan: [phase-3-coupling](../../../../docs/plans/hail/done/phase-3-coupling.md). Matches the methodology doctrine
(§4 Coupling + §5 Frequency — it prescribes the exact Minkowski form and the Bernoulli-not-multiplier rule).

## Assumptions (this layer)

A11 areal hit-or-miss, Minkowski `(√F+√s)²/A` · A12 asset footprint `s` ≈ 0.50 km² *(capacity estimate; `s ≪ F`
so insensitive)* · A13 full exposure on hit · A14 regional rate `λ_collection` *(**fitted** ≈ 29.6/yr on the ~5.65-yr record → `λ_asset` ≈ 0.26/yr; DD-3 Stage 1)*.
Full detail + status: [assumptions register A11–A14](../../../../docs/plans/hail/assumptions.md#m2--coupling).

**Next → M3 (damage):** for the events that hit, *how much damage?* — map each event's hail size through a
PV hail-fragility curve.
