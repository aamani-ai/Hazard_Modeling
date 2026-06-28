# Decisions — CONUS grid packaging + QC session (2026-06-25)

Canonical log: [`../../../plans/hazard_conus_grid/decisions.md`](../../../plans/hazard_conus_grid/decisions.md) (DD-G*).
This indexes what was *realized, implemented, or corrected* this session.

## Implemented this session (the plan made real)
- **DD-G10–G14 realized in code** — the grid is now three installable packages ("one engine, two drivers"):
  `shared/risk_engine` (peril/asset-agnostic, **leak-clean** — no `*_solar`/`mesh_*`/hardcoded ladders),
  `pipelines/hail`, `drivers/conus_grid`. The deep-per-asset is the *future* second driver of the same engine.
- **Plausibility QC implemented** (the decided [`05`](../../discussion/conus_grid/hail/05_plausibility_qc_rule.md) rule),
  in `pipelines/hail/plausibility_qc.py` — **additive, non-destructive**: cap the severity *summary* at the US
  record (Vivian SD 2010 = **8.0 in = 203.2 mm**), flag **≥300 mm hard artifacts**, flag **frequency spikes**
  (λ > 99.5th-pct ≈ 8.9/yr) and hold them out of reportable loss; **raw severity + frequency counts left
  untouched**. Lands in *one* place (the package fn) and flows to the grid automatically.
- **The QC is asset-free → a cross-driver contract** — it lives at M0/M1, above the asset, so *both* drivers
  inherit it. The deep-per-asset driver **must adopt it** (esp. Ohio-Valley over-read / sparse-West sites);
  logged as the next architectural to-do.
- **Canonical RP/VaR ladder pinned** in `shared/risk_engine/config.py` (`CANONICAL_RETURN_PERIODS` includes
  **200** — `PML₂₀₀ ≡ VaR₉₉.₅`), resolving the code-vs-`output_schema.md` discrepancy.
- **Reproduction-gate discipline** — every extraction proven bit-identical *before* it moved (engine 2.1e-16,
  M0/M1 0.0 diff, driver 2.06e-16, QC validated). No expensive re-runs.
- **Docker: repo-root build context + `.dockerignore`** (Option B) so the Cloud Run image installs the
  packages; the `.dockerignore` excludes the gitignored cross-repo symlinks (which would break the context).
- **Guide home = `docs/guides/`** (distinct from plans/decisions and from the hazard anchors) — and the QC's
  **research-pass is a first-class prerequisite** (Step 0): you derive the QC rule from how the data fails
  (`00`→`01` sourcing, `04`→`05` QC), not by guessing.

## Realized / corrected this session
- **Solar loss is QC-invariant** (max abs diff vs pre-QC baseline = **0.0**) — the M3 curve saturates ~100 mm,
  so capping severity at 203 mm can't move solar loss. This is the decided design (the M1 cap is for
  hazard-layer honesty + future assets that fail >100 mm), **not a gap**. Documented, not hidden.
- **"White cells = no data" → corrected** to *full-coverage, genuinely-rare-hail, short-record-limited*. The
  remedies (pooling/shrinkage · record extension · de-biasing) are deferred — and stated as a V1 constraint.
- **Sequencing acknowledged** — the QC came after the refactor because the bit-identical gates required it;
  owned that this put infra ahead of the goal, then closed it.

## Carried (settled earlier, honored here)
- **DD-G1** 0.25° benchmark grid + `cell_id` (13,085 served) · **DD-G2** two durable layers · **DD-G6**
  GCS dev/releases · **DD-G7** runner-after-measured-batch · **DD-G9** task-indexed Cloud Run fanout.
- Canonical **100 MW solar** (1.5 km² / $148.3M TIV) at every cell · **MC 250k** · PML/VaR/TVaR as readouts
  of one exceedance curve · $ **and** % of TIV · M0/M1 = peril (asset-free), M2–M4 = peril × asset.
