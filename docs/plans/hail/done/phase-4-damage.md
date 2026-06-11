# Phase 4 — Severity / Damage (M2 → M3)

> **Status:** done (2026-06-09). Historical plan-of-record for hail × solar severity/damage. Basis: A22
> (damage representation), methodology §6 (Severity) + §12
> (the hail-on-solar worked example, which hands us a starting curated curve).

M2→M3 answers: **given an event reaches the asset, how bad is it?** We map each event's hail size through a
**curated** PV damage curve → a damage ratio → the conditional dollar loss.

## The shape (per methodology §6)

- **Curated, not fitted.** We have *event data* (hail sizes), **not** a history of what hail cost this plant.
  So we do **not** fit losses — we **curate** a `hail size → damage ratio` curve (from panel hail-rating
  standards + post-event studies) and apply it to the event sizes. *Its provenance, not a fit statistic, is
  what the number rests on.*
- **Conditional on hit.** The damage is the loss **if the event hits** — the *full* conditional loss. We do
  **not** multiply by `pᵢ` here; `pᵢ` stays in frequency for Phase 5's Bernoulli draw (the LOTV rule — the
  single most important build rule, methodology §5/§8).

## The curve (v1)

Curated anchor points (mm → mean damage ratio), from methodology §12: **(25.4→0), 27→1.2%, 40→4.5%,
60→20%, 75→40%**; monotone-linear interpolation between; **0 below the 25.4 mm severe threshold**; **linear
extrapolation above 75 mm** (last-segment slope, capped at 100%) — *flagged as extrapolation, not curated*.
Our events span ~28–95 mm, so the top event (95.5 mm ≈ 3.76″) lands in the extrapolated region.

## Damage representation (A22 — the open choice)

V1 emits a **scalar mean damage ratio** per event (the methodology worked-example choice). Deferred richer
options: a **damage-state vector** or a **full conditional distribution** (matters for the tail — two same-size
events can damage differently); and **duration / business interruption** (v1 folds repair downtime into the
damage ratio and leaves revenue loss aside, exactly as the methodology worked example does).

## Inputs → outputs

[M2 coupled events](../../../../Notebooks/hail/solar/m2_coupling/) (each event's `peak_intensity_mm/in` + `pᵢ`) +
`asset_value_usd` ($36,778,400) → `data/hail/hayhurst_hail_m3_damage.parquet` (each event +
`damage_ratio` + `conditional_loss_usd` (= ratio × value, the *full* loss on a hit) + carried `pᵢ`) +
`…_m3_summary.json`.

## Deferred / out of scope

- **Conditional damage *distribution*** (vs the scalar mean) — the tail-relevant richness (A22); Phase 5
  will need a severity spread to sample, not just the mean.
- **Duration / BI** (downtime → revenue loss) — folded into the damage ratio for v1.
- **Curve calibration to PV claims / >75 mm extrapolation** — the curve is curated-from-literature; refine
  with asset/claims data and a real giant-hail anchor.

**Carried forward to Phase 5 (loss & metrics):** per-event `(pᵢ, conditional_loss)` → compound-Poisson Monte
Carlo (`Bernoulli(pᵢ)` → full loss on hit) → annual AEP/OEP vectors → EAL / VaR / PML (A24; methodology §8–§10).
