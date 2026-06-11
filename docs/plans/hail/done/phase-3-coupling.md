# Phase 3 — Coupling (M1 → M2)

> **Status:** done (2026-06-09). Historical plan-of-record for the M1→M2 solar coupling step. Basis: A21 (coupling types),
> `hazard_math/01` (Bernoulli hit-miss), and the old repo's `issues/spatial-factor`. This is **the step the
> old repo got wrong** — so the math gets a known-answer check.

M1→M2 turns the regional event catalog into the **asset's** hazard: for each event, *does it hit Hayhurst,
and with what intensity?* Hail is an **areal hit-or-miss** peril (A21), so the coupling is a spatial
hit-probability + a thinning of the regional rate.

## The math

For an event of footprint area `F` and an asset of footprint area `s`, both within a region of area `A`, the
probability the event covers the asset (Minkowski sum / Robbins, disk approximation):

> **`p = (√F + √s)² / A`**

- **Per-event thinning.** Each catalog event carries its own `F` (and intensity), so we compute `pᵢ` per
  event — *not* one constant spatial factor (footprint and intensity correlate; a single factor breaks the
  joint relationship).
- **Rate.** `λ_asset = λ_collection · E[p]`; equivalently the **expected asset-hits over the observed
  catalog = Σ pᵢ** (computable now, no fitted λ needed).
- **`A` cancels.** `λ_collection` grows ∝ `A`; `p` shrinks ∝ `1/A` → `λ_asset` is independent of the region
  size. So the 50-mi radius doesn't bias the result — **as long as the rate and `p` use the same region**
  (the [DD-1](../decisions.md) rule). This is *why* the region→asset move converges.

**The old-repo error (basics-spot-on + known-answer check).** The old model used a point spatial factor
(≈ `F/A`), ignoring the asset's own size. The correct Minkowski form adds `2√(F·s) + s`. The ratio
`(√F+√s)²/F = (1+√(s/F))²` → the naive form **under-counts**, worst for **small footprints** (here:
1.05× for the biggest event, **1.81×** for the smallest). We verify the formula against hand-checked
known answers (s→0 recovers F/A; F,s→ touching cases).

## Inputs

- **M1 catalog** — `footprint_area_km2` (the `F`) + `peak_intensity_in` per event (the [GeoParquet](../../../../Notebooks/hail/m1_catalog/01_event_catalog.ipynb)).
- **Region area `A`** — the 50-mi circle ≈ **20,342 km²** (same region as the catalog).
- **Asset footprint `s`** — estimated from capacity: 24.8 MW × ~5 acres/MW (array footprint) ≈ **0.50 km²**
  (a *stated assumption*; the actual plant polygon — via the solar-boundary pipeline — is the refinement).
  Note `s ≪ F` for hail, so the result is insensitive to `s` here (it matters more for larger assets / smaller
  footprints / other perils).

## Build steps (the notebook → `solar/m2_coupling/01_coupling.ipynb`)

1. Load the M1 catalog; set `A` (region) and `s` (asset, stated assumption).
2. Compute **`pᵢ` (Minkowski)** per event; tabulate.
3. **Known-answer check + old-repo comparison** — `pᵢ` vs naive `F/A`, the correction factor, and the
   formula sanity checks.
4. **Expected asset-hits = Σ pᵢ** over the observed catalog (the per-event thinning result).
5. **Geometric cross-check** — which event polygons actually contain the asset point? Empirical hits vs the
   Σ pᵢ expectation (illustrates why the Minkowski *expectation* is the stable estimate and raw point-hits
   are noisy).
6. Carry **per-event intensity** (`peak_intensity_in`) onto the hit-weighted set → for M3.
7. Persist the **asset-coupled event set** (`…m2_coupled.parquet`) + a small M2 summary (A, s, Σpᵢ,
   assumptions) → `data/hail/`.

## Deferred / out of scope

- **Stable annual `λ_asset`** — `Σ pᵢ` is the expectation *over the observed window*; turning it into an
  unbiased annual rate needs the widened MRMS record (the window is one peak season — [DD-1](../decisions.md),
  [DD-2](../decisions.md), [`learning_logs/01`](../../../learning_logs/01_extending_a_short_hazard_record.md)).
- **Exposed fraction** (area-asset partial overlap). The methodology §4 treats a solar farm as an *area*
  asset where "a fraction of the asset is exposed per event." We computed the area-aware **hit probability**
  (Minkowski, which is correct), but approximated exposure as **full-on-hit** — sound here because
  `s ≪ F` (a hail swath that reaches the ~0.5 km² farm almost certainly covers all of it → exposed_fraction
  ≈ 1). State it as the assumption it is; it matters for larger assets / smaller footprints / line geometry.
- **Actual plant polygon** for `s` (estimate suffices while `s ≪ F`).
- **True geometric-overlap as the primary coupling** (vs the Minkowski thinning) — kept as a cross-check;
  the thinning is the v1 primary because it converges and feeds the stochastic frequency.

**Carried forward to M3 (damage):** each coupled event's `peak_intensity_in` → a PV hail-fragility curve →
event damage; combined with `pᵢ`/`λ_asset` in the M3 compound-Poisson Monte Carlo for EAL/VaR/PML.
