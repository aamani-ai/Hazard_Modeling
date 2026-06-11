# Notes — implementation, commands, verification, insights

## Commits this session (3)

| Hash | Date | What |
|---|---|---|
| `a65c13e` | 2026-06-09 | docs: sync M4 narrative — kill stale 'illustrative', define A24, sharpen M4 README |
| `0387091` | 2026-06-10 | refactor(notebooks): nest hail pipeline peril→asset (`Notebooks/hail/solar/`) + roadmap |
| `61abd1d` | 2026-06-10 | docs: de-stale the top-level overview docs (README, AGENTS, docs index) |

`git diff --stat 181ac75..HEAD` → 24 files, ~691 insertions / ~235 deletions.

## The restructure mechanics (the reusable recipe for the next asset)

```bash
mkdir Notebooks/hail/solar
git mv Notebooks/hail/m2_coupling      Notebooks/hail/solar/m2_coupling
git mv Notebooks/hail/m3_damage        Notebooks/hail/solar/m3_damage
git mv Notebooks/hail/m4_loss_metrics  Notebooks/hail/solar/m4_loss_metrics
# fix the ONE ../../../docs link in each moved .py, then sync the .ipynb WITHOUT losing outputs:
.venv/bin/jupytext --to notebook --update Notebooks/hail/solar/<layer>/01_*.py
```

- **Data paths are move-safe.** Every notebook resolves data via `_repo_root()` (walks up to
  `AGENTS.md`/`.env`) → `ROOT / "data/hail/..."`. Moving folders does **not** break data reads. Verified
  by simulating `_repo_root()` from each new dir + loading the full chain (158 events → 300k MC years).
- **Link-edit rule:** the three layers move *together*, so **sibling links among m2/m3/m4 stay
  unchanged**. Only links to the *staying* `m0_input_data`/`m1_catalog`, to `docs/`, and to repo-root gain
  **one extra `../`** (e.g. `../../../docs/` → `../../../../docs/`).
- **jupytext:** use `--update` (not a plain conversion) to preserve executed outputs (`execution_count`
  stayed 12/9/11). No jupytext config file; pairing is by basename+dir, so moving the pair together is safe.
- **git rename detection:** `.py`/`.ipynb` renamed at **99%**; the `m3_damage/README.md` shows as
  delete+create because its stale-curve content was rewritten (similarity dropped) — acceptable for a
  folder README.

## The M4 README review workflow

18 agents: **3 lenses** (engine/math fidelity vs the notebook + `hazard_math`; cross-doc numeric
consistency; pedagogy + future-improvements) → **adversarial verify** each finding against source. Verdict:
**sound, no blockers**; 13 confirmed findings (1 major = the stale-illustrative cross-doc contradiction;
the rest minor/nit precision). All fixed in `a65c13e` or flagged.

## Discovered staleness (fixed this session)

- **m2 folder README:** `Σpᵢ 0.135 → 1.39`; `λ_asset` "deferred" → **fitted 0.26/yr**; per-event `p` range
  stated as `0.01–9.7%` (from the parquet: min 0.0001, max 0.0971, mean 0.0088).
- **m3 folder README:** replaced the **old literature curve** description (anchors `25.4→0…75→40`, "67%",
  "95.5 mm", ">75 mm extrapolation") with the **capex-weighted subsystem blend** (PV_MODULE `L=0.95` +
  TRACKER `L=0.40` × NREL weights → `Asset_DR=Σwᵢ·DRᵢ`, **cap ~34%**, max conditional loss **$12.56M**,
  largest event **118.5 mm**).
- **M4 "anatomy of a sim year" map:** `~100k` → **300k** MC years (matches `N_YEARS`).
- **Overview docs:** README / AGENTS / docs-index "early scaffold / foundation phase / no modeling code
  yet" → current status, peril→asset repo map, real conventions.

## Verification (all passed)

```bash
# no live stale folder paths (only tasks_history snapshots + solar-internal siblings remain)
grep -rn "hail/m2_coupling\|hail/m3_damage\|hail/m4_loss_metrics" --include=*.md --include=*.py . \
  | grep -vE "/\.venv/|model-gpr|tasks_history|/solar/"
# moved-file docs links resolve (solar/<layer> → root is 4 hops → ../../../../docs/)
ls docs/plans/hail/{assumptions,decisions}.md docs/plans/hail/done/{phase-3-coupling,phase-4-damage,phase-5-loss-metrics}.md
# data resolution after move + chain loads
.venv/bin/python -c "..._repo_root() from each new dir; read m1/m2/m3/m4 parquets..."   # 158 / 300000 rows OK
# public-safety: nothing sensitive EVER committed
git log --all --pretty=format: --name-only --diff-filter=A | sort -u | grep -iE "\.env|\.parquet|\.gz|secret|key"  # → none
```

## Key insights / lessons

- **The pipeline's seam is the folder structure.** M0/M1 = peril (shared); M2–M4 = (peril × asset). The
  cleanest layout *is* that seam — peril folder holds the catalog, asset subfolders consume it.
- **Asset geometry, not just the peril, picks the coupling type** (A21). Solar polygon → areal; wind-farm
  point-cloud → per-turbine. This is the concrete proof of "standard interface, not standard physics."
- **Folder READMEs drift silently** when the notebooks/data change (the m2/m3 curve/rate staleness existed
  before this session). Worth a periodic doc-drift sweep — see the optional next step.
- **`_repo_root()` anchoring is what made the move cheap** — root-relative data paths survive any notebook
  relocation; only markdown relative links need depth fixes.
- **Communication is a first-class deliverable.** Most of this session was making correct work *legible*
  (matrix README, the NOAA→MRMS tilt story, de-staling) rather than new modeling.

## Reference audit addendum

Follow-up review of [`docs/references/`](../../../references/) found the reference map is useful, but
not fully source-locked yet. Treat it as a strong working bibliography until these cleanup items are
resolved:

- **Wendt & Jirak 2021:** fix the page range/title in `bibliography.md` (NOAA lists Weather and
  Forecasting `36(2), 645-659`, with the full title ending in "with Comparisons to Storm Data Hail
  Reports"). Also soften the `README.md` claim that this source supports a specific MESH
  over-forecast/FAR caveat; it more directly supports a MESH-vs-Storm-Data/reporting-caveat point.
- **Taszarek et al. 2020:** rename the short key from `Brooks/Taszarek et al. 2020` to
  `Taszarek et al. 2020` unless there is a deliberate house-style reason to keep the current key; the
  official citation appears first-authored by Taszarek.
- **Hussain et al. 2025:** keep it, but narrow the claim. It supports overdispersed convective-storm
  count modeling and negative-binomial-family comparisons; it does not prove that hail frequency must be
  Negative Binomial.
- **OASIS Keys:** good support for mapping exposure locations to model keys / area-peril IDs, but weak
  support by itself for a single-centroid or extended-risk geometry caveat. Pair it with OASIS
  disaggregation / methodology docs if that geometry-uncertainty claim stays.
- **EVT exceedance-count caveat:** keep the `~50-100 exceedances` point as a practical rule-of-thumb or
  internal A24/A23 caveat unless an exact external citation is added.
- **Commercial examples:** Moody's geocoding example checked out. The kWh `+300%` and Rudaviciute
  `-41%/+83%` examples are useful, but should be source-locked to the exact PDF/page before being treated
  as hard evidence.
- **References that looked supportable:** Allen & Tippett for hail-report bias / threshold changes;
  Schuster et al. for radar-reflectivity hail swath logic; FEMA Hazus for loss-methodology grounding;
  OASIS/IF for vulnerability and uncertainty concepts; Moody's for centroid/geocoding sensitivity.
