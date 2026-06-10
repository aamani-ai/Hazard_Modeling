# Decisions — peril→asset restructure (2026-06-10)

Session-level summary. Canonical ADRs remain in [`docs/plans/hail/decisions.md`](../../../plans/hail/decisions.md)
(DD-1..4); generalizable lessons in [`docs/learning_logs/`](../../../learning_logs/). This file is the
index + the *why* for this session's calls.

## 1. Notebook structure = `peril → asset` (not asset-first, not flat)

**Decision.** Perils are top-level folders; each asset is a subfolder. **M0/M1 (raw data + event catalog
+ frequency) stay at the peril level** (asset-independent); **M2–M4 (coupling, damage, loss) move into the
asset subfolder** (`Notebooks/hail/solar/`). **Rationale.** This maps the pipeline's natural seam exactly:
a hail catalog over a region is identical regardless of what sits under it; only coupling/damage/loss
specialize per asset. It also (a) mirrors the canonical **(peril × sub-peril × asset_type)** taxonomy
(A12), (b) matches the A21 dispatch tables (peril-row × asset-column), (c) fits the repo's identity (the
*hazard* engine), (d) keeps the shared catalog built **once** (asset-first would duplicate/bury it), and
(e) the data is already peril-scoped (`data/hail/`), so moving notebooks doesn't move data. *The owner
proposed peril-first; on inspection it was the better design than my initial asset-first lean, for the
reasons above.*

## 2. Coupling type is set by (peril × asset) jointly — the wind-farm point

**Decision.** Treat the **asset's exposure geometry** as the axis that changes the M2 physics. Solar farm
= a **dense areal polygon** → areal hit-or-miss (Minkowski `(√F+√s)²/A`). Wind farm = a **sparse cloud of
point turbines** (lat/longs) → **per-turbine hit-or-miss** for hail, **field-intensity** for wind loads.
**Rationale.** This is the live demonstration of *"standard interface, not standard physics"*
(`docs/principles/hazard_asset_specificity.md`): same M0→M4 contract, genuinely different coupling. A21
flags exactly this as the **"wind-farm open question."** The lat/longs are the *symptom*; the
coupling-type change is the *substance*.

## 3. Verify-before-trust on the M4 README (adversarial workflow)

**Decision.** Don't eyeball the math-critical layer's explainer — run independent checkers (engine/math
vs the notebook + `hazard_math`; cross-doc consistency; pedagogy) then adversarially confirm each finding
against source. **Rationale.** M4 is the layer the old repo broke; a confident-but-wrong explanation is a
liability. Result: sound, no blockers; 13 confirmed (mostly precision) findings, all fixed or flagged.

## 4. Define assumption A24 (don't leave a dangling reference)

**Decision.** Add **A24 = "dispersion test underpowered at small n"** (φ fitted on 5 yr; wants ~10–15) to
the M1 frequency block. **Rationale.** It was cited from A8/A20/the manifest/the notebook but never
defined — a dangling ref. Placed it in the frequency cluster (next to A8/A9) where its references point.

## 5. Fix discovered staleness in the publish path (beyond the literal move)

**Decision.** Sync the **m2/m3 folder READMEs** (and the M4 "anatomy" map's `100k`) to current reality —
not just fix their links. **Rationale.** They predated the Stage-1 widening + the capex-weighted curve
swap (m3 still described the *old literature curve*: anchors, "67%", 95.5 mm). Leaving a known-wrong doc
in a repo we're about to publish to the team would undercut the whole communication goal. Flagged the
scope expansion explicitly.

## 6. Leave historical task-history docs as point-in-time snapshots

**Decision.** Do **not** rewrite the prior session's `tasks_history/2026-06-09__…` paths to the new
`solar/` locations. **Rationale.** Those were accurate when written; revising them falsifies the record.
(A forward note can be added if ever needed, but the clean choice is untouched.)

## 7. Repo public-now, private-later

**Decision.** Make the repo **public** now for open team feedback; flip to **private + named
collaborators** once the production folder architecture lands. **Rationale.** Early-stage feedback is
worth more than access control right now; nothing sensitive is committed (history safety-scanned — no
`.env`, parquets, GRIB, or keys ever committed), so public exposure is safe.
