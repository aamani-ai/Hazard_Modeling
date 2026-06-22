# M2 — Coupling (the plan)

*Phase 3 of the flood × solar build. The deliverable is the **coupling contract** M3 consumes — how the M1 flood
depth-at-return-period becomes the asset's exposure × the depth its components experience.* Per-phase loop
([feature_workflow](../../workflows/feature_workflow.md)).

> **Coupling type = site-conditioned (bucket 3, A21) — deliberately thin.** Flood is bucket 3 (field × per-asset
> susceptibility), *not* hail's areal hit-or-miss. But BLE already delivered **depth-above-ground at the asset** in
> M1, so the field→asset step is done. M2 is therefore thin (mirroring wildfire's M2): it formalizes the **areal
> exposure** (what fraction of the plant floods) and the **conditional depth** (how deep, given flooded) — the two
> numbers M3's depth-damage curve needs. The **per-subsystem height conditioning** (effective depth = depth − mount
> height) lives in **M3** alongside the per-subsystem fragility, keeping M2 a clean exposure×severity emitter.

## The contract M2 emits (per site × return period)

| field | meaning | from M1 |
|---|---|---|
| `exposure_fraction` | fraction of the footprint (≈ value, V1 assumption) inundated | `inund_frac` |
| `conditional_depth_m` | representative depth **given** inundated (the "severity") | `depth_wet_m` |
| `depth_max_m` | footprint max depth (tail) | `depth_max_m` |

This mirrors wildfire's thin M2 `(λ, conditional severity, exposure)` — here `(exposure_fraction, conditional_depth)`
per RP (frequency is the RP itself; the RP→MC bridge is the open M4 event-model decision).

## Questions / assumptions
- **Value ∝ area (V1):** `exposure_fraction` (areal inundation) proxies the fraction of asset *value* exposed —
  subsystems assumed distributed proportionally to footprint area. (Refine later: site-specific subsystem layout.)
- **Representative depth = inundated-cell mean** (`depth_wet_m`); the footprint-average (`depth_fp_m`) already folds
  exposure in — M3 must use exposure × conditional-depth, not double-count.
- **Height conditioning deferred to M3** (per-subsystem mount heights → effective depth).

## Detailed plan — `solar/m2_coupling/01_coupling`
1. Load the M1 catalog manifest (per site × RP: inundated fraction + depth distribution).
2. Emit the coupling contract: `exposure_fraction`, `conditional_depth_m`, `depth_max_m` per site × RP.
3. Plot exposure × conditional-depth vs return period (the two sites).
4. Known-answer: exposure + depth **grow** with RP for the high site; high site exposure×depth ≫ Hayhurst.
5. Persist `flood_solar_m2_coupling_manifest.json` (sub-peril-keyed, `event_family_id` reserved — JD-FL-4).

## Verification checklist
- [ ] `exposure_fraction` and `conditional_depth` monotone (non-decreasing) 100-yr → 500-yr at the high site.
- [ ] Hayhurst exposure×depth ≪ high site (low-baseline control).
- [ ] No double-counting (conditional depth is inundated-cell mean, exposure applied separately).
- [ ] Sub-peril key + reserved `event_family_id` carried.

## Next
**M3 (damage)** — per-subsystem depth-damage curve on the **effective depth** (`conditional_depth − mount_height`),
capex-weighted (the house recipe), `conditional_loss = exposure × Σ wᵢ·DRᵢ × TIV`.
