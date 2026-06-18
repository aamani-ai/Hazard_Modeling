# M4 — Loss & metrics (the plan)

*Phase 5 (final) of the flood × solar build. Turn M3 conditional losses → the **annual loss distribution** →
EAL / VaR / PML / TVaR (% of TIV + dollars), on the shared metric frame.* Per-phase loop
([feature_workflow](../../workflows/feature_workflow.md)).

> **Event-model bridge = [JD-FL-7](decisions.md).** Riverine flood = **annual-maximum** (~1 damaging flood/yr). Build
> a **loss-exceedance curve** straight from the M3 conditional losses — now a **5-point** RP curve for the proving site
> (10/25/50/100/500-yr) after the **[JD-FL-8](decisions.md) densification**: 100/500-yr are **real BLE**; 10/25/50-yr
> are a **regression flow-frequency rating anchored to both BLE depths** (no assumed onset). The MC draws `AEP ~ U(0,1)`
> → `loss(AEP)` (log-AEP interp, bounded extrap) → per-year loss vectors → the shared **EAL/VaR/PML/TVaR** (DD-4).

## Method
- **MC:** N=500k simulated years; annual loss = `loss(AEP)`; metrics off the per-year vectors. `PML_T = (1−1/T)`
  percentile (DD-4 frame, shared with hail/wildfire/wind → Total-Loss-combinable).
- **Seam:** M1 emits a variable-length, source-tagged RP→loss profile; `loss_at_aep` is generic → densifying (more
  RP points) is a one-place change.

## Result (built — `solar/m4_loss_metrics/01_loss_metrics`) — **combined riverine + pluvial** (JD-FL-11)
Headline = **worse-source-wins** (co-sampled comonotonic); single-valued like every peril → Total-Loss-combinable.
| site | EAL (headline) | VaR99 | PML100 | PML500 | TVaR99 | EAL envelope (worse-wins→additive UB) |
|---|---|---|---|---|---|---|
| **Elizabeth** (high) | **0.27% TIV** | 2.62% | 4.45% | **7.92%** | 6.60% | 0.27% – 0.42% |
| Hayhurst (low) | 0.06% | 0.13% | 0.97% | 1.78% | 1.46% | 0.06% – 0.08% |

**Marginals** (% TIV EAL): Elizabeth riverine **0.15** + pluvial **0.27**; Hayhurst riverine 0.02 + pluvial 0.06.
**Combine frame check ✓** PML@T reproduces the *worse* sub-peril's Lₜ by construction (max-combine).
**Densification (JD-FL-8) ✓** riverine 10-yr depth ≈ **0.97 ft** (regression rating); riverine EAL 0.13%→0.155%.

> **⚠️ The headline is pluvial-dominated.** Pluvial > riverine at every RP here (driven by the screening-grade
> ponding-fraction `f=0.4` — [AFL-P2](assumptions.md)), so worse-wins makes the combined ≈ pluvial and **masks the
> well-anchored riverine**. The headline is therefore **screening-grade** until pluvial gains a depth anchor; the
> marginals are reported so the solid riverine number stays visible. "Pluvial dominates" is a *model* statement
> (sensitive to `f`), not a robust fact.

## External validation (sanity-check ✅)
- **Observed flood depths (USGS high-water marks, §4b — runs in the notebook):** 21 USGS-surveyed marks near the
  proving site (Aug-2016 LA flood) read **0–7.9 ft** above ground (median **2.1 ft**); our modeled depths (**1.0–2.0 ft**
  across 10→500-yr) fall **inside** that range — a real-event regime check (asserted; persisted to the manifest).
  *Regional (~25–45 km, many marks near channels) → confirms the depth scale, not a to-the-inch calibration.*
- **Depth-damage** tracks HAZUS electrical/contents norms (heavy damage by 1–3 ft; inverter ~87% at 2 ft).
- **EAL** → implied AAL of the exposed area, inside the **NFIP SFHA norm (0.5–1.5%/yr)**.
- **Internal:** PML100=VaR99 (frame ✓); PML500/PML100 = 1.7×; EAL/PML100 ≈ 0.06 (rare heavy-tail). No red flags.
- **Not done:** FEMA **NRI** county-EAL benchmark — its public API/download was reorganized (now redirects to the RAPT
  tool); deferred until the current NRI data endpoint is confirmed.

## Honest caveats
- **EAL now densified** (JD-FL-8) — the frequent region rests on **measurement-anchored 10/25/50-yr depths** (regression
  flow-frequency rating pinned to both BLE depths), not a flat onset guess; **robust to channel slope** (the rating
  exponent absorbs it — M1 finding). **PML@100/500-yr stays BLE-grounded.**
- Regression-Q **standard error not yet propagated** as an MC overlay · `value ∝ area` exposure · Elizabeth TIV
  estimated · medium-confidence curves · **duration/BI unmodeled** (Gen-1).

## Hardening (seam-ready, no rework)
1. ~~Densify the frequent floods~~ **done (JD-FL-8)** — regression flow-frequency + BLE-anchored rating.
2. Propagate the **regression-Q standard error** as an MC overlay (distributional EAL); swap **live HAND-SRC** depth if
   the delineation service returns; the **enriched polygon / Fathom depth**; **duration/BI**; the **PV flood-stow** lever.
