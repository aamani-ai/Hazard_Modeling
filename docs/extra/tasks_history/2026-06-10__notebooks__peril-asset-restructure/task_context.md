# Task context — Notebooks peril→asset restructure + doc-sync + team share

## Objective

Get the hail pipeline **ready to share with the team** (and go public for feedback): restructure the
notebooks so the **asset axis is explicit**, verify + sharpen the M4 narrative, and de-stale the docs —
ahead of adding a second asset (a wind farm) and a third peril (wildfire).

## Background

Last session built **hail × solar end-to-end (M0→M4)** ([`2026-06-09__hail-pipeline__m0-m4-end-to-end`](../2026-06-09__hail-pipeline__m0-m4-end-to-end/handoff.md)).
This session prepped that work for **communication**. The trigger: the flat `Notebooks/hail/` silently
meant *hail × solar* — fine for one cell, but it breaks the moment a **wind farm** (a different asset,
different coupling geometry) arrives. The owner wanted the structure right *before* publishing a repo
link to the team.

## Problems encountered

1. **A user-authored M4 README needed verification** — M4 is the math-critical layer the old repo broke;
   a wrong explanation there is worse than none.
2. **Stale "illustrative" metrics claim** in 3 docs (the λ has been *fitted* since the record-widening).
3. **Dangling `A24` reference** — cited from A8/A20/manifest/notebook but never defined as a row.
4. **Flat notebook structure** didn't express the (peril × asset) matrix the model actually is.
5. **Discovered mid-restructure:** the `m2/m3` *folder* READMEs were stale (old literature damage curve,
   pre-widening rate numbers) — and the **top-level overview docs** (README, AGENTS, docs index) still
   said "early scaffold / foundation phase / no modeling code yet."

## What we did

1. **Answered the magnitude-distribution question** — no parametric magnitude/severity fit; we
   bootstrap the empirical 158-event sizes through a deterministic (scalar-mean) capex-weighted curve.
   The fits (EVT-GPD size tail = A23; conditional-DR distribution = A17) are deferred, not skipped.
2. **Verified the M4 README** with an 18-agent workflow (3 lenses → adversarial verify) → **sound, no
   blockers**. Applied Tier-1+2 fixes: killed the stale "illustrative" claim across 3 docs, **defined
   assumption A24** (dispersion test underpowered at small n), and sharpened M4 precision (Poisson-only
   zero-loss check; EVT joint-sampling caveat; frequency-body vs severity-tail split; A19 citation).
   → commit **`a65c13e`**.
3. **Restructured the notebooks `peril → asset`** — `git mv` `m2_coupling/ m3_damage/ m4_loss_metrics/`
   → `Notebooks/hail/solar/`; `m0_input_data/ m1_catalog/` stay at the peril level (asset-independent).
   New [`Notebooks/README.md`](../../../../Notebooks/README.md) (peril × asset matrix), rewritten
   [`Notebooks/hail/README.md`](../../../../Notebooks/hail/README.md) (peril overview + why a wind farm
   differs), new [`Notebooks/hail/solar/README.md`](../../../../Notebooks/hail/solar/README.md)
   (hail × solar detail). Repointed all inbound/outbound links. **Also fixed the discovered stale m2/m3
   folder-README content** to the current curve/fit. → commit **`0387091`**.
4. **Drafted the team Slack message** (NOAA→MRMS data tilt + peril→asset navigation + what's next).
   Held for send; the owner sent a refined version (wildfire = *conditioning* difference, wind farm =
   *geometry* difference).
5. **De-staled the top-level overview docs** (README, AGENTS, docs index) → current reality.
   → commit **`61abd1d`**.
6. **Repo going public** for open feedback (history safety-scanned — no secrets/data ever committed);
   to go private + collaborators once the production architecture lands.

## Files touched

- **Created:** `Notebooks/README.md` (overwrote a stub), `Notebooks/hail/solar/README.md`, the `A24` row
  in `docs/plans/hail/assumptions.md`, this task-history folder.
- **Moved (git mv, history preserved):** `Notebooks/hail/{m2_coupling,m3_damage,m4_loss_metrics}/` →
  `Notebooks/hail/solar/…` (`.py`/`.ipynb` renames at 99%).
- **Rewritten/edited:** `Notebooks/hail/README.md`; the 3 moved folder READMEs (links + m2/m3 content
  sync); `m0_input_data/`+`m1_catalog/` READMEs (links); `docs/plans/hail/{README,phase-3,phase-4,phase-5}.md`;
  `AGENTS.md`, `README.md`, `docs/README.md`; the 3 moved `.py` (+ synced `.ipynb`, one docs link each).
- **Commits:** `a65c13e` (M4 narrative), `0387091` (restructure), `61abd1d` (overview de-stale) — all on
  `main`, pushed to `D-ivyy/Hazard_Modeling`.

## Current status

- ✅ All three commits pushed to `main`. Repo content correct + consistent (verified: no stale paths,
  links resolve, `_repo_root()` data resolution intact, jupytext outputs preserved, no secrets in history).
- ✅ Team message sent by the owner; repo going public for feedback.

## Next steps

- **Wildfire × solar** (new *peril* on solar — **site-conditioned** coupling, not areal hit-or-miss).
- **Hail × wind farm** (new *asset* — **per-turbine point-cloud** coupling; needs turbine lat/longs; the
  A21 "wind-farm open question").
- **Then** the production folder architecture (after 2–3 cells, not before).
- Deferred backlog unchanged: NOAA-calibrated λ extension (DD-3 Stage 2), EVT-GPD tail (A23),
  conditional-DR distribution (A17), financial terms, damage-curve revamp.
- **Optional now:** a deeper doc-drift sweep (per-phase plans, `00_scope_and_story.md`, principles) — the
  top-level + m2/m3 docs are synced, but lower-traffic docs weren't audited this session.
