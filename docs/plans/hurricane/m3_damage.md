# M3 — Damage (the active plan) · *3-s gust → solar loss fraction*

*Map each event's **3-second peak gust** to a **damage ratio** on the solar asset, via the canonical
`infrasure-damage-curves` library — the same library every peril uses. Hurricane's one inheritance from convective
wind is exactly here: the **3-s-gust wind-damage basis** ([DD-WN-9](../convective_wind/decisions.md)).*

**Where this sits:** layer-0 → [M0](m0_input_data.md) → [M1](m1_catalog.md) → [M2](m2_coupling.md) →
**M3 (damage)** → [M4](m4_loss_metrics.md).

---

## The curve — `infrasure-damage-curves` hurricane-wind × solar ([ATC-14](assumptions.md))

- **Source:** the canonical [`infrasure-damage-curves`](../../../infrasure-damage-curves) library (peril × asset
  fragility) — **not** a literature-curated one-off. M3 is *source-agnostic*: it reads a curve, it doesn't author
  physics.
- **Observable:** **3-s peak gust (mph)** — the universal wind metric ([00_hazard_definition](00_hazard_definition.md)),
  shared with convective wind so the two perils are curve-consistent.
- **Form:** an anchored logistic/tabular `DR(gust)` over solar subsystems (panels, racking/trackers, inverters,
  combiners), **capex-weighted** to the asset damage ratio. Anchored so `DR ≈ 0` below the structural onset
  (design wind speed) and rising into the violent tail.
- **Built with a provisional HURRICANE × SOLAR curve** ([ATC-14](assumptions.md)) — the library provides one
  (caps ~48%, ATC-14 basis); it is flagged **provisional** and slated for replacement (the loss side is curve-limited
  while the hazard side is independently validated). The earlier open question ("confirm a curve exists, else use
  wind × solar") is **resolved** — a hurricane-specific curve was used.

## What M3 computes (per event)

```
conditional_loss = DR(gust_3s_mph) × value_exposed_fraction(=1.0) × TIV
conditional_DR   = DR(gust_3s_mph)                         # reported as % of TIV
```

- `value_exposed_fraction = 1.0` from M2 (degenerate field on a dense polygon).
- Output is **per event** (storm-resolved) — M4 aggregates to annual loss, no RP bridge.

## Subsystem / mitigation notes

- **Subsystem split** — carry the capex-weighted subsystem contributions (which subsystem drives loss at which gust)
  for legibility, as wind/flood M3 did.
- **Tracker stow** — single-axis trackers have a **stow position** that changes wind vulnerability; the built headline
  is on the **`tracker_stow`** curve variant (mirrors flood's PV-variant note, [AFL-15](../flood/assumptions.md));
  a harsher non-stow variant is carried as sensitivity.

## Validation — the M3 known-answer checks

1. **Anchor** — `DR(gust)` ≈ 0 below the design/onset wind; rises monotonically; bounded ≤ 1.
2. **Spot points** — a Cat-3-ish gust and a Cat-5-ish gust give plausible DRs vs the curve's published anchors.
3. **Baseline** — Hayhurst's near-zero gusts → DR ≈ 0 → ~no loss (the control behaves).
4. **Curve provenance** — exact library curve ID + version pinned in the manifest.

## Outputs

```text
data/hurricane/<asset>_tc_m3_damage.parquet     per-event conditional_loss + conditional_DR + subsystem split   (gitignored)
data/hurricane/<asset>_tc_m3_manifest.json      curve ID/version, gust basis, subsystem weights, stow state      (kept)
```

## Assumptions surfaced (this layer)

[ATC-14](assumptions.md) (curve = `infrasure-damage-curves` hurricane-wind × solar, 3-s-gust basis) ·
[ATC-4](assumptions.md) (3-s gust observable) · [ATC-2](assumptions.md) (physical loss only).

## Open questions *(curve availability resolved at build — kept for context)*

- **Curve availability** — ✅ **resolved**: a provisional library **HURRICANE × SOLAR** curve was used (caps ~48%,
  ATC-14); flagged provisional, slated for replacement.
- **Stow state** — ✅ resolved: headline on the **`tracker_stow`** variant (harsher non-stow carried as sensitivity).
- **Subsystem onset spread** — do inverters/trackers fail at different gusts than panels (changes the curve shape)?

**Next → [M4 (loss & metrics)](m4_loss_metrics.md):** sample the storm-resolved event catalog through the shared MC
engine → **EAL / VaR / PML / TVaR**, **% of TIV + $**.
