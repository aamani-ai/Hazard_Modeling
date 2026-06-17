# Task context — wind hazard route-zero planning (+ wildfire M4 close-out + MC learning)

## Objective

Stand up **hazard 3 of 3 — wind** as a complete *route-zero* planning set (the layer-0 hazard definition +
decisions + M0–M4 plans + coupling discussion), mirroring the wildfire kickoff, so the next chat can build the
wind notebooks from a settled, defensible spec. Two precursor sub-tasks also closed this session: the **wildfire
M4 close-out** and a **Monte-Carlo effective-sample-size learning**.

## Background

Last session completed the **peril→asset restructure** and shared the repo. This session: (1) finished wildfire
× solar at M4 (the finale on the shared engine), (2) the owner asked to understand the rare-event EAL tolerance
→ produced a reusable MC-error learning, (3) pivoted to **hazard 3 = wind** — the owner's framing: pick the
hazard that *really matters* for wind farms (tornado / strong wind), and a hazard where **sub-perils matter**.
The owner is **new to this domain** and asked that the planning + decision + hazard-definition docs be
*enriching* — especially the coupling taxonomy (the "field-intensity vs the rest" distinction).

## Problems / questions worked

1. **Is the rare-peril EAL noisy, and was the 4% known-answer tolerance wrong?** Yes — verified: Hayhurst's EAL
   rests on ~114 fire-years out of 300k, relative SE 18.3%; a fixed 4% band fails on correct code. Fix =
   statistical tolerance `max(0.04·analytic, 4·SE)`.
2. **"Derived hazard threshold" caveat (the owner's key question):** does wind need a hazard-definition layer
   above M0, with defensible references? **Yes** — and the old repo already had it (`HAZARD_CONFIG` μ + L). The
   sharper framing: hail/wildfire inherited the event definition from the data product; **wind is the first
   peril we must author**, from standards.
3. **Coupling correction:** my earlier "inland-convective = areal hit-or-miss (reuse hail)" was half-wrong.
   Reading `Hazard_Data_Reference` corrected it — **strong wind = site-conditioned** (broad swath, never
   "missed"; ASCE RP surface = pre-integrated), **tornado = areal hit-or-miss** (narrow path). Wind tours two
   built buckets.
4. **Adversarial review found a real defect:** the m-plan drafter used a *pre-final* DD-WN numbering that
   collided with the canonical `decisions.md` — every DD link in m1/m2/m4 pointed to the wrong decision.

## What we did

1. **Wildfire M4 close-out.** Reported metrics (Hayhurst EAL 0.0004% / $151·yr⁻¹; Matrix EAL 0.29% / $1.12M,
   PML250 14% — the low-vs-high payoff on one unchanged engine); created `docs/plans/wildfire/done/m4-loss-metrics.md`,
   updated the wildfire plan README + done index. **Wildfire × solar M0–M4 is complete.**
2. **MC effective-sample-size learning.** Created the personal-KB note `hazard_math/06_monte_carlo_error_effective_sample_size.md`
   (effective sample size `λM` for the mean / `M(1−α)` for a quantile; the self-calibrating `max(rel, k·SE)`
   tolerance; the "continuous severity ≠ less sampling noise; the analytic Panjer/FFT route is the third way to
   kill MC noise" section) + cross-refs into notes 04/05; and the repo learning-log
   [`learning_logs/10`](../../../learning_logs/10_monte_carlo_effective_sample_size.md).
3. **Committed + pushed** (3 commits, CI green): `20ac205` hail pᵢ/spatial-homogeneity clarifications · `e7486f3`
   wildfire × solar M0–M4 pipeline · `78ec5ff` learnings 07–10. (PDF gitignored; the personal-KB note 06 is in a
   *separate* repo, not pushed.)
4. **Scoped hazard 3 = wind** with the owner: sub-peril family; inland-convective route (strong wind → tornado),
   hurricane deferred; two sites (Traverse / Shepherds Flat); the hazard-definition layer; the scope boundary
   (hazard-tier extreme wind vs performance-tier resource wind).
5. **Built the wind route-zero** (2 workflows): a build workflow (4 research readers → 4 drafters → 3 adversarial
   reviewers) wrote 15 docs; a fix-up workflow (8 per-file fixers → verify) repaired the DD-WN cross-refs,
   reconciled the notebook fork (M2 only), and added newcomer glosses (the site-conditioned-vs-field-intensity
   contrast box, F/s/A legend, derecho/μ_mean/λ definitions, EF5 "ceiling"→"truncation above the floor").
   **Verified 5/5** (DD-WN consistency, links, fork, pedagogy). Committed `5010a61`.

## Files touched

- **Created (committed `5010a61`):** `docs/plans/convective_wind/` — `README.md`, `00_intent.md`, `00_hazard_definition.md`,
  `decisions.md` (DD-WN-1..13), `assumptions.md` (AWN-*), `m0_input_data.md`, `m1_catalog.md`, `m2_coupling.md`,
  `m3_damage.md`, `m4_loss_metrics.md`, `done/README.md`; `docs/extra/discussion/convective_wind/` — `README.md`,
  `01_scope_and_sub_peril_taxonomy.md`, `02_coupling_buckets_and_wind.md`, `03_hazard_definition_and_thresholds.md`.
- **Created (this folder):** the 4 task-history files.
- **Earlier this session (committed `20ac205`/`e7486f3`/`78ec5ff`):** wildfire M4 notebook + plan/done docs;
  `learning_logs/{07,08,09,10}` + index; hail M2/M4 clarifications; `.gitignore` (raw rasters, the proprietary
  PDF) + `requirements.txt` (raster libs).
- **Personal KB (separate repo `~/Desktop/Learning`, NOT committed):** `hazard_math/06_*` + 04/05 cross-ref edits.
- **Left untouched / unstaged:** `docs/extra/discussion/conus_grid/` (separate, another session); the 3
  `docs/google_drive_docs/*.docx` (binary churn).

## Current status

- ✅ Wildfire × solar M0–M4 complete; M4 metrics reported + recorded.
- ✅ MC effective-sample-size learning captured (repo log + KB note).
- ✅ Wind **route-zero** complete: 15 docs, 13 decisions, adversarially reviewed + fixed, **verified 5/5**,
  committed + pushed (`5010a61`).
- ⏳ Wind **notebooks**: not started — the build is the next chat's job (layer-0 → M0 → … → M4).

## Next steps

- **Build the wind notebooks** layer-0 → M4 (see [`handoff.md`](handoff.md) ▶ NEXT ACTION). Start `01_asce_hazard`.
- **Loose ends:** commit the personal-KB note 06 (if wanted); decide what to do with `conus_grid/`; the wildfire
  × wind cell (M2–M4 on the shared wildfire M0/M1) remains parked at planning.
- **Deferred backlog (named in the plans):** hurricane / field-intensity (bucket 2); the calibrated RE turbine
  fragility curve (`infrasure-damage-curves`); portfolio correlation; financial terms.
