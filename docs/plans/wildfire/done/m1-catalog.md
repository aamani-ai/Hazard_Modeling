# M1 — Catalog · completion record

**Status:** ✅ built · 2026-06-13 · **Plan:** [`../m1_catalog.md`](../m1_catalog.md) · **Notebook:**
[`Notebooks/wildfire/m1_catalog/01_catalog`](../../../../Notebooks/wildfire/m1_catalog/README.md)

## Objective

Turn the M0 evidence into the **typed handoff the loss engine consumes** — per asset, a **frequency (λ)** and
a **conditional severity distribution** on fire-line intensity (kW/m), with a manifest declaring the catalog's
choices. Built for both assets.

## What shipped

- **The structural-twist explanation** up front (areal vs site-conditioned; FSim pre-integrates the event set
  → M1 is *profile-assembly*, not event-extraction) — doctrine-backed, and now [learning_logs/09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md).
- **Frequency** ([DD-W7](../decisions.md)): `λ = −ln(1−BP)` per asset, `frequency_process = poisson`,
  `fano = 1`. **No short-record fit** — FSim pre-integrated the seasons; the rate comes from the site BP
  directly (site-conditioned, no spatial factor).
- **Severity:** the FLP1-6 histogram → **fire-line intensity (kW/m)** via Byram — the conditional severity the
  engine samples in a fire year (flame length kept too, as the durable, re-derivable source).
- **AW-21 edge-rule sensitivity check** done (center-in / all-touched / area-weighted).
- **Per-asset manifest** with the engine-contract keys (`lambda_per_yr`, `fano_factor`,
  `severity_kwm_distribution`) + the severity-distribution parquet.

## Key results

| | Hayhurst (low-fire) | Matrix (high-fire) |
|---|---|---|
| **λ** (`−ln(1−BP)`) | 0.00037/yr | **0.044/yr** |
| `λ/BP` (Poisson correction) | 1.0002 | **1.022** (~2% — earns its keep where BP is non-trivial) |
| **mean intensity \| fire** | 159 kW/m | **710 kW/m** |
| **P(>4 ft \| fire)** | 0.10 | **0.66** |

- **AW-21 check (FSim 270 m):** Matrix spread **0.5–1.3%** across edge rules (immaterial — many pixels);
  Hayhurst 11–30% but on a **near-zero hazard** → no decision change. `all_touched` stands; area-weighting
  deferred to the small-footprint/high-fire trigger.
- The **low-vs-high contrast** carries cleanly into the catalog (Matrix ~4.5× Hayhurst on intensity, ~120× on λ).

## Decisions / assumptions

[DD-W7](../decisions.md) (frequency — Poisson(λ=−ln(1−BP)), fano=1, no fit) · [AW-21](../assumptions.md)
(edge rule — **check done**) · [AW-22](../assumptions.md) (λ from BP, no fit) · [AW-23](../assumptions.md)
(structural fano=1) · [AW-24](../assumptions.md) (discrete 6-class severity; coarse open-ended tail).

## Learnings spawned

[learning_logs/09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) — pre-integrated vs
extracted hazard: M1 is profile-assembly or event-extraction, and the frequency comes from a different place.

## Open items carried to later layers

- **M2:** the genuinely new wildfire physics — site-conditioned coupling, per-asset **oozing detection** +
  surrounding-fuel sourcing (AW-15; the Hydronos `buffer_ring` is a ready tool), emitting the `(p_hit,
  conditional intensity)` pair for the reused M3/M4 contract.
- **M3:** BoS-weighted damage on the kW/m axis (curves from `infrasure-damage-curves`); the 30%-unmodeled
  solar TIV question (AW-19).
- **Severity tail:** the 6 discrete FLP classes + open-ended "12+ ft" are coarse (AW-24) — EVT/continuous
  deferred for deep return periods.

## Next

**M2 — solar coupling** (site-conditioned): turn the per-asset hazard profile into per-"event" `(p_hit,
conditional intensity)`, handling oozing/surrounding-fuel, for the reused damage + loss engine.
