# Task context — flood × solar, M0→M4 + EAL hardening

## Objective

Build a new hazard pipeline — **flood (riverine) × solar** — end-to-end (M0→M4) in the repo's notebooks-first style,
mirroring hail/wildfire/convective_wind: real public data, **hazard-first** (not the old model's loss-first
anti-pattern), known-answer checks at every layer. Then **harden the EAL** (this session).

## Background

- Flood is the repo's 4th peril cell (hail ✅, wildfire ✅, convective-wind ✅ were the first three). It's the first
  **site-conditioned** peril where *we* assemble the depth grid (vs wildfire's pre-integrated FSim).
- Decisions use the prefix **`JD-FL-*`** (user's preference; not `DD-`).
- Depth-source journey: no Fathom/commercial → single-gauge Bulletin 17C (doesn't scale, superseded) → **FEMA BLE**
  preferred where it exists, **StreamStats+HAND** as national fallback ([JD-FL-6](../../../plans/flood/decisions.md)).

## What we built / fixed (this session = the EAL hardening)

- **JD-FL-8 densification.** Replaced the assumed 10-yr onset depth with measurement-anchored 10/25/50-yr depths:
  USGS **NLDI** (snap to NHDPlus reach 15078158 → 1.91 mi² drainage) → **NSS** regression (LA Coastal Plain
  SIR 2024-5031) → Q(2…100-yr) → **power-law rating `depth = d₁₀₀·(Q/Q₁₀₀)^p`**, exponent pinned by both BLE depths.
- **Robustness result:** densified depths are **near-invariant to the (unmeasurable) channel slope** — the rating
  exponent absorbs it (10-yr depth 0.97 ft across slope 3/8/20 ft/mi). → learning log 13.
- **EAL 0.13% → 0.155% TIV** (+18%); densified value cross-checks against the old "assumed @1.0 ft" guess; PML@100/500
  unchanged (BLE-anchored). All M1–M4 known-answer checks pass; full chain re-runs clean.
- Architecture: densification lives in **M1** (emits a variable-length RP profile); M2/M3/M4 flowed through unchanged
  — the seam JD-FL-7 promised. M4's onset-depth hack removed; loss curve now built generically from M3's RPs.

## Files touched

**Notebooks** (jupytext-paired `.py` + executed `.ipynb`):
- `Notebooks/flood/m1_catalog/01_catalog.py` — **+ §1b densification** (NLDI/NSS/rating helpers, `cpost_json` cache),
  denser profile, densification known-answer check, `flow_frequency` provenance in manifest.
- `Notebooks/flood/solar/m4_loss_metrics/01_loss_metrics.py` — curve built generically from M3 RPs; **§2b** rewritten
  to densified-vs-assumed-onset EAL comparison; manifest/caveats updated.
- (M0 `01`/`02`, M2, M3 unchanged this session — M2/M3 re-ran to pass the denser rows through.)

**Docs:**
- `docs/plans/flood/decisions.md` — **+ JD-FL-8**.
- `docs/plans/flood/{m1_catalog,m4_loss_metrics}.md` + `assumptions.md` (AFL-12 built, AFL-18 superseded).
- `docs/learning_logs/13_densify_sparse_rp_anchor_the_shape.md` (+ index row).
- This `tasks_history/` folder.

**Data manifests** (kept; large parquets/cache gitignored): `data/flood/flood_m{1,3,4}_*manifest*.json`,
`flood_m4_metrics_manifest.json` now carry the flow-frequency provenance + RP-points-per-site.

## Status

**Flood × solar = complete (M0→M4) + EAL-hardened.** Real but record-limited numbers, math-validated, honestly
labeled. Not yet committed/pushed (prior flood build also uncommitted on `main` per git status).

## Next steps

See `handoff.md` → NEXT ACTION roadmap. Headline: (1) regression-Q uncertainty → distributional EAL; (2) national
generalization + live HAND (with the production folder architecture); (3) flood × wind-farm (separate chat).
