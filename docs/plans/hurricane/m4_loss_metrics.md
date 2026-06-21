# M4 — Loss & Metrics (the active plan) · *storm-resolved MC → EAL / VaR / PML / TVaR*

*The last layer: turn the per-event conditional losses into a **sampled annual loss distribution** and read the
risk metrics off it — **EAL, VaR, PML, TVaR**, as **% of TIV alongside $** — on the **shared MC engine**, reused
unchanged from hail/wildfire/wind/flood. The engine never changes; only the event stream feeding it does.*

**Where this sits:** layer-0 → [M0](m0_input_data.md) → [M1](m1_catalog.md) → [M2](m2_coupling.md) →
[M3](m3_damage.md) → **M4 (loss & metrics)**.

---

## The event model — storm-resolved MC (a clean fit, no RP bridge)

Hurricane's catalog is **event-based** (discrete storms with per-event losses, M3), so it feeds the shared
**compound-Poisson / NegBin Monte-Carlo** engine **directly** — *like hail*, and **unlike flood**, which had to
bridge a sparse RP curve into the engine ([JD-FL-7](../flood/decisions.md)). No bridge is the point of choosing a
storm-resolved catalog ([JD-TC-3](decisions.md)).

**The MC ([ATC-15](assumptions.md)):**
1. **Frequency** — storms/year near the site (from M1, straight off the RAFT synthetic-year count) → the Poisson/
   NegBin rate `λ`.
2. **Per simulated year** — draw the number of site-affecting storms; for each, draw an event from the M1/M3 catalog
   (its 3-s gust → conditional loss); **sum losses within the year** → that year's loss.
   - *Within-year aggregation = sum* (multiple landfalls in one year are distinct events on the same asset — additive,
     unlike flood's within-storm max-depth). Most years = 0 (TC is rare at a point); the baseline ≈ all zeros.
3. **Repeat** over many simulated years → the **sampled annual-loss distribution**.

> **Tail off the *sampled* distribution, never the expected-loss shortcut** — the old model's cardinal error
> (M3-style loss-first lognormal back-solve). VaR/PML/TVaR are read off the simulated vector.

## The metrics (the shared frame — Total-Loss-combinable)

| Metric | Definition | Reported as |
|---|---|---|
| **EAL** | mean annual loss | % of TIV + $ |
| **VaR(p)** | p-quantile of annual loss (e.g. 99%) | % of TIV + $ |
| **PML(RP)** | loss at return period (e.g. 100/250/500-yr) | % of TIV + $ |
| **TVaR(p)** | mean loss beyond VaR(p) (tail-heavy TC) | % of TIV + $ |

- **% of TIV alongside $** — the house convention, so hurricane is combinable with hail/wildfire/wind/flood into
  Total Loss.
- **TVaR emphasized** — TC is a tail-driven peril (rare, severe); report TVaR beside VaR (as the rare-tornado cell did).

## Validation — the M4 known-answer checks

1. **Frequency reproduction** — simulated storms/year ≈ the M1 λ (engine sanity).
2. **RP reproduction** — simulated PML at 100/250/500-yr ≈ the catalog's empirical RP losses (frame known-answer).
3. **External benchmark** — EAL/PML vs **FEMA Hazus / NRI** hurricane-wind loss for the site's county/tract (order-
   of-magnitude anchor, as flood used NRI — [JD-FL-W5](../flood/decisions.md)); also a sanity check vs the STORM RP
   cross-check propagated through the curve.
4. **Baseline** — Hayhurst EAL ≈ 0 (near-zero TC control behaves).
5. **Coastal-site shape** — high site shows a material, tail-heavy distribution; the headline is honestly labeled
   **wind-only** (no surge/rain — [JD-TC-4](decisions.md)).

## The honest headline label

> Hurricane × solar V1: **wind-only** EAL/VaR/PML/TVaR (% of TIV + $), on a storm-resolved RAFT catalog. **Excludes
> surge and rain** (flood's `[C]`/`[F]`, hooked via `event_family_id`) — so for a coastal site this is a **floor on
> total TC loss**, not the whole storm. Field-intensity coupling is **spatially degenerate** (solar); the wind-farm
> V2 cell exercises it per-turbine.

## Outputs

```text
data/hurricane/<asset>_tc_m4_loss_metrics.parquet   sampled annual-loss vector + metrics (% TIV + $)             (gitignored)
data/hurricane/<asset>_tc_m4_metrics_manifest.json  λ, sim count, metrics, benchmark comparison, honest label    (kept)
data/hurricane/<asset>_tc_m4_*.png                  EP curve, annual-loss distribution, metric plots             (kept small)
```

## Assumptions surfaced (this layer)

[ATC-15](assumptions.md) (storm-resolved MC, shared engine) · [ATC-2](assumptions.md) (physical loss only) ·
[ATC-16](assumptions.md) (TIV basis) · [ATC-18](assumptions.md) (climate non-stationarity = overlay).

## Open questions

- **Within-year correlation** — are multiple landfalls in a year independent draws, or correlated (an active
  season)? RAFT's storm-resolution lets us preserve the *catalog's* per-year clustering — prefer that to an
  independence assumption.
- **Climate overlay** — apply the STORM climate-change set / CMIP6 factor as a reported overlay for a 2040+ horizon?
  (Flagged, not in the V1 headline — [ATC-18](assumptions.md).)
- **Benchmark availability** — confirm Hazus/NRI hurricane loss is pullable for the coastal site's county.

**This completes hurricane × solar V1.** The reusable products for what's next: the **storm-resolved RAFT catalog +
`event_family_id`** (→ founds flood coastal `[C]` + pluvial-TC `[F]`) and the validated **Holland field** (→ the
wind-farm V2 cell samples it per-turbine, reusing convective wind's 3-s-gust turbine curve).
