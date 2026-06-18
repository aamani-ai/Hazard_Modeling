# Handoff — flood × solar, M0→M4 complete + EAL-hardened (2026-06-17)

**Read me first.** 60-second summary, how to reproduce, and the next-action roadmap.

## 60-second summary

**Flood (riverine) × solar is built end-to-end (M0→M4) on real public data + canonical curves, and the EAL is now
hardened.** Two sites: **Elizabeth Solar Plant** (EIA 66111, Allen Parish **LA** — the proving/high-flood site) and
**Hayhurst Texas Solar** (EIA 66880, **TX** desert — the near-zero baseline control, reused from hail/wildfire).

- **Hazard-first, not loss-first.** Depth comes from **FEMA BLE** (HEC-RAS-grade depth grids) at 100/500-yr, sampled
  over the **real OSM footprint polygon**; damage from the **canonical `infrasure-damage-curves` RIVERINE_FLOOD ×
  solar** set (capex-weighted, the flood *height-inversion* baked into each `x0` — inverters drown at 0.75 ft, panels
  survive shallow). Loss via **annual-maximum Monte-Carlo** over the RP loss curve (shared DD-4 metric frame).
- **This session's work = the EAL hardening ([JD-FL-8](../../../plans/flood/decisions.md)).** BLE only gives the
  100/500-yr *tail*; the frequent floods that drive EAL had been a **flat 0.5 ft onset guess**. We densified the lower
  RPs (10/25/50-yr) with a **regression flow-frequency curve** (USGS NLDI drainage area → NSS LA Coastal Plain
  SIR 2024-5031 → Q(T)) fed into a **power-law rating anchored to both real BLE depths**. The 10-yr depth went
  0.5 → **0.97 ft** (measurement-anchored), and EAL **0.13% → 0.155% TIV** (+18%). PML@100/500 unchanged (still BLE).

**UPDATE (2026-06-18) — pluvial sub-peril added + sub-perils combined.** Flood × solar is now **riverine + pluvial**:
- **Pluvial built** ([JD-FL-9](../../../plans/flood/decisions.md)) — NOAA Atlas 14 rainfall → SCS-CN runoff → **sheet
  ponding** (we *rejected* DEM-hypsometry — 10 m σ is site slope, not micro-relief → absurd 5 ft pools). Screening-grade:
  **no depth anchor**, rests on soft knobs `r=0.5` (retention), `f=0.4` (ponding fraction). Catalog fork
  [JD-FL-10](../../../plans/flood/decisions.md): `m1_catalog/riverine/` + `m1_catalog/pluvial/`, shared M2/M3, combine at M4.
- **Combine** ([JD-FL-11](../../../plans/flood/decisions.md), backed by `jdocs/flood_subperil_research_result.md`) —
  co-sample comonotonic + **worse-source-wins** headline (φ=1; max-per-location, a component drowns once — Bates 2021);
  **additive-capped recorded as the upper envelope** (φ=0). Metrics on the joint vector; marginals kept.

**Final metrics (% TIV) — combined riverine + pluvial (headline = worse-wins):**
- **Elizabeth** EAL **0.27** (envelope 0.27–0.42) · PML100 **4.45** · PML500 **7.92** · TVaR99 **6.60**
- **Hayhurst** EAL 0.06 · PML500 1.78
- **Marginals:** Elizabeth riverine 0.15 + pluvial 0.27 (riverine-only metrics still in the manifest).
- **⚠️ Headline is pluvial-dominated** (driven by the screening-grade `f` knob) → the well-anchored riverine is masked;
  headline is screening-grade until pluvial gains a depth anchor. "Pluvial dominates" is a model statement, not a fact.

Every layer known-answer-checked; full chain (riverine + pluvial → M2 → M3 → M4) re-runs clean. + learning log 14.

## Reproduce

```bash
# activate a Python env with the repo deps (requirements.txt) + jupytext/nbconvert
cd Notebooks/flood
for nb in m1_catalog/01_catalog solar/m2_coupling/01_coupling solar/m3_damage/01_damage solar/m4_loss_metrics/01_loss_metrics; do
  jupytext --to ipynb $nb.py
  jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=python3 $nb.ipynb
done
# M0 (01 site-screen, 02 depth/DEM) only needs re-running if sites/geometry change.
```

All FEMA/BLE/OSM/3DEP/NLDI/NSS fetches are **file-cached** (`data/flood/raw/http_cache/`, ~456 files, gitignored) →
re-runs are deterministic + fast and survive the flaky USGS endpoints. Outputs land in `data/flood/*manifest*.json`.

## NEXT ACTION roadmap

1. **(modeling, next) Propagate the regression-Q standard error → a *distributional* EAL.** EAL is still a point
   estimate off the *best-estimate* flow; NSS publishes a ±40–60% standard error of prediction (already in the cached
   response). Carry it through the MC → "EAL = 0.12–0.20%, central 0.155%". Mostly wiring; closes the JD-FL-8 caveat.
2. **(deferred) National generalization** — run the NLDI→regression densification **per site with its own regional
   equation** (we did the LA proving site only); + **live HAND-SRC** depth for **no-BLE / ungauged** sites (the
   delineation service was 404 this session — swap-in seam is open in code). Do this with the **production folder
   architecture**, not mid-notebook.
3. **(separate chat) flood × wind-farm** — V2 asset off the same shared M0/M1 catalog; greenfield M3 (no flood × wind
   curve in the library). Prompt already drafted in the prior session.
4. **(polish) Jupyter Lab visual review** of the 4 flood plots; optional `/code-review` or `/simplify` pass.

See `task_context.md` (full objective/files/status), `decisions.md` (JD-FL index), `notes.md` (commands/metrics/insight).
```
```
