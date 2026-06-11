# Handoff — read me first (next session / model switch)

## 60-second summary (what happened, not how)

1. **Restructured the hail notebooks `peril → asset`.** `git mv` M2/M3/M4 into
   **`Notebooks/hail/solar/`**; **M0/M1 stay at `Notebooks/hail/`** (the catalog is asset-independent).
   This makes the asset axis explicit before a 2nd asset (a wind farm) arrives.
2. **Three READMEs now tell the story:** [`Notebooks/README.md`](../../../../Notebooks/README.md) = the
   **(peril × asset) matrix**; [`Notebooks/hail/README.md`](../../../../Notebooks/hail/README.md) = the
   **hail peril** (shared catalog + why a wind farm couples differently);
   [`Notebooks/hail/solar/README.md`](../../../../Notebooks/hail/solar/README.md) = **hail × solar** detail.
3. **The structural insight:** M0/M1 = the peril (shared); **M2–M4 = the (peril × asset) cell**. Coupling
   type is set by **(peril × asset) jointly** (A21) — solar = areal polygon (Minkowski); wind farm =
   sparse turbine point-cloud (per-turbine). "Standard interface, not standard physics."
4. **Verified the (user-authored) M4 README** with an 18-agent adversarial workflow → **sound, no
   blockers**; applied precision fixes.
5. **Defined assumption A24** (dispersion test underpowered at small n) — was a dangling reference.
6. **Killed the stale "illustrative" metrics claim** across 3 docs (λ has been *fitted* since the widening).
7. **Fixed discovered staleness** in the m2/m3 folder READMEs (old literature curve / pre-widening rate)
   and the M4 anatomy map (`100k`→`300k`).
8. **De-staled the top-level overview docs** (README, AGENTS, docs index) — "scaffold/foundation phase" →
   current reality.
9. **Shared with the team** (Slack message drafted here; owner sent a refined version) and the repo is
   **going public** for feedback (history safety-scanned — clean).
10. **3 commits, all on `main`, pushed:** `a65c13e` (M4 narrative) · `0387091` (restructure) ·
    `61abd1d` (overview de-stale).

## Read these before starting (in order)

1. [`Notebooks/README.md`](../../../../Notebooks/README.md) — the (peril × asset) matrix + coupling types.
2. [`Notebooks/hail/README.md`](../../../../Notebooks/hail/README.md) + [`hail/solar/README.md`](../../../../Notebooks/hail/solar/README.md) — the structure to **mirror** for the next asset/peril.
3. The reference coupling docs (in `infrasure-hazard-competitive-research/learnings/architecture/`):
   **`A12_peril_taxonomy_spine.md`** (peril × asset taxonomy) + **`A21_m1_m2_coupling_types.md`** (the
   coupling-type dispatch table — areal / field-intensity / site-conditioned) + the principle
   [`docs/principles/hazard_asset_specificity.md`](../../../principles/hazard_asset_specificity.md).
4. `docs/plans/hail/{decisions.md (DD-1..4), assumptions.md (A1–A24 — the deferred backlog)}`.
5. The prior handoff: [`2026-06-09__hail-pipeline__m0-m4-end-to-end/handoff.md`](../2026-06-09__hail-pipeline__m0-m4-end-to-end/handoff.md) (how the M0→M4 engine was built).

## Repro / verify current state

```bash
source .venv/bin/activate                       # python3.12, kernel "hazard_modeling"
git remote -v                                    # origin = git@github.com-work:D-ivyy/Hazard_Modeling.git
# data artifacts (parquets) + the ~905 MB MRMS cache are gitignored. To rebuild from scratch:
python scripts/scan_mrms_record.py 2020-10-15 2026-06-08   # re-pull MRMS → wide M0
# then the chain reads from the new locations (data paths are root-anchored, move-safe):
#   Notebooks/hail/m1_catalog → hail/solar/m2_coupling → m3_damage → m4_loss_metrics
cat data/hail/hayhurst_hail_m4_metrics.json      # headline: EAL 5.7%, PML100 54%, PML250 62%
```

## Available vs needs-fetching (unchanged from last session)

- **In repo:** all notebooks (`.py` + executed `.ipynb`), manifests/summaries/GeoJSON, the damage-curve
  spec, the MRMS `_manifest.json`, all docs. Repo is **public**.
- **Local-only / gitignored:** `.env` (HYDRONOS_API_KEY), `.venv/`, `data/hail/mrms_raw/` (~905 MB GRIB),
  all `*.parquet`. A fresh clone must re-run the scan before re-executing M1+.
- **Symlinks (gitignored):** `model-gpr`, `hazard_analysis`, `infrasure-hazard-competitive-research`,
  `infrasure-damage-curves`, `Learning`, `renewablesinfo_org`.

---

## ▶ NEXT ACTION (primary focus)

The whole point of the restructure: add cells that exercise a **different coupling**, proving the
interface generalizes. Two parallel expansion axes (this is the framing the owner sent the team):

### Phase A — New peril: **Wildfire × Solar** (M0→M4, mirror `hail/solar/`)
- **Coupling changes → site-conditioned** (field × per-asset susceptibility), **not** areal hit-or-miss
  → the M2 Minkowski formula does **not** apply (A21 dispatch row 5; principle doc's 3rd coupling type).
- New peril folder `Notebooks/wildfire/` with its own M0/M1 catalog (perimeters / FRP — MODIS/VIIRS /
  burn-probability; NRI wildfire), then `wildfire/solar/` for M2–M4.
- Damage curve: `infrasure-damage-curves` wildfire × solar.

### Phase B — New asset: **Hail × Wind farm** (reuse the existing hail catalog)
- **Coupling changes → per-turbine point-cloud** (intersect the footprint with turbine lat/longs), **not**
  a polygon overlap. The A21 **"wind-farm open question"** — decide bounding-polygon vs point-cloud.
- New `Notebooks/hail/wind/` (M2–M4) that **reads the same `data/hail/` catalog** at M2 (M0/M1 reused).
- Needs the **turbine lat/longs** (asset data) + a wind-turbine fragility curve.

### Phase C — *Then* the production folder architecture — **deferred** until A+B done (don't lock it
around one cell). Use the owner's `Learning/` project-structure reference then.

### Parallel / on-demand backlog (all `deferred` in `assumptions.md`)
- **NOAA-calibrated λ extension** (DD-3 Stage 2) — the main lever to bring EAL down from ~5.7%.
- **EVT-GPD severity tail** (A23) + **conditional-DR distribution** (A17) — the deep-tail upgrades.
- **Damage-curve revamp** (`infrasure-damage-curves`) + **financial terms** (deductibles/limits/BI).
- **Optional doc-drift sweep** — the top-level + m2/m3 docs are synced; the per-phase plans,
  `00_scope_and_story.md`, and principles index weren't audited this session.

### Gotchas the next session must know
- **The restructure recipe** is in this folder's `notes.md` (git mv → fix the one `.py` docs link →
  `jupytext --update` to preserve outputs → fix links by the "+1 `../` for staying/docs, siblings
  unchanged" rule). Data paths are **move-safe** via `_repo_root()`.
- **Reuse, don't rebuild, the hail catalog** for hail × wind farm — M0/M1 live at `Notebooks/hail/` and
  the parquet is in `data/hail/`; the wind-farm notebook starts at M2.
- **Push** to D-ivyy uses SSH `github.com-work` (the gh HTTPS token lacks `workflow` scope).
- **Repo is public now** → no secrets in commits (verified); it goes **private + collaborators** at
  production-architecture time.
- Metrics are **real but record-limited** — don't quote them as final.
- **`docs/references/` needs a cleanup pass before being treated as source-locked** — see the reference
  audit addendum in this folder's `notes.md` (Wendt/Jirak pages + MESH wording, Taszarek key, Hussain
  NegBin overclaim, OASIS Keys geometry overclaim, EVT exceedance-count caveat, and commercial example
  source-locking).
