# M2 — Coupling (the plan)

*Phase 3 of the flood build. The deliverable is the **coupling contract** M3 consumes — how the M1 flood
depth field becomes the asset's exposure × the depth its components experience.* Per-phase loop
([feature_workflow](../../workflows/feature_workflow.md)).

> **Coupling type = site-conditioned (bucket 3, A21) — M2 does the coupling (JD-FL-19).** Flood is bucket 3 (field ×
> per-asset susceptibility), *not* hail's areal hit-or-miss. **M1 emits the asset-independent field** (riverine BLE
> raster / runoff `Q` / SLOSH surge); **the field→asset reduction is M2's job** — it samples that field at the asset:
> the **areal inundated mean** over the footprint for **solar**, **per-node depth** at each turbine pad + the collector
> substation for **wind**. So M2 is **no longer thin**: it owns the reduction that produces the **areal exposure**
> (what fraction of the plant floods) and the **conditional depth** (how deep, given flooded) M3 needs. The
> **per-subsystem height conditioning** (effective depth = depth − mount height) lives in **M3** alongside the
> per-subsystem fragility, keeping M2 the exposure×severity emitter.

## The contract M2 emits (per site × return period)

| field | meaning | computed in M2 (from the M1 field) |
|---|---|---|
| `exposure_fraction` | fraction of the footprint (≈ value, V1 assumption) inundated | areal reduction of the M1 field over the footprint |
| `conditional_depth_m` | representative depth **given** inundated (the "severity") | inundated-cell mean of the sampled field |
| `depth_max_m` | footprint max depth (tail) | footprint max of the sampled field |

M2 reduces the **M1 field** to `(exposure_fraction, conditional_depth)` per RP (frequency is the RP itself; the RP→MC
bridge is settled as the annual-max MC, JD-FL-7). For **wind**, the analogue is per-node: which turbine pads + the
collector flood and how deep, summed over flooded nodes (not areal) — see [m_wind_farm.md](m_wind_farm.md).

## Questions / assumptions
- **Value ∝ area (V1):** `exposure_fraction` (areal inundation) proxies the fraction of asset *value* exposed —
  subsystems assumed distributed proportionally to footprint area. (Refine later: site-specific subsystem layout.)
- **Representative depth = inundated-cell mean** (`depth_wet_m`); the footprint-average (`depth_fp_m`) already folds
  exposure in — M3 must use exposure × conditional-depth, not double-count.
- **Height conditioning deferred to M3** (per-subsystem mount heights → effective depth).

## Detailed plan — `solar/m2_coupling/01_coupling`
1. Load the **M1 field** (riverine BLE raster path / pluvial runoff `Q` / coastal SLOSH surge per site × RP) and
   **reduce it over the footprint polygon** — the field→asset coupling step (JD-FL-19).
2. Emit the coupling contract: `exposure_fraction`, `conditional_depth_m`, `depth_max_m` per site × RP.
3. Plot exposure × conditional-depth vs return period (across the solar sites).
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
