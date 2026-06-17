# Handoff — read me first (next session / model switch)

## 60-second summary (what happened, not how)

1. **Built the wind-hazard route-zero** (hazard **3 of 3**: hail ✅ · wildfire ✅ · wind). 15 planning docs —
   `docs/plans/convective_wind/` (11) + `docs/extra/discussion/convective_wind/` (4). **Plans only, no notebooks/data yet.** This is
   the doc set the *next* chat builds from.
2. **Route = inland-convective.** Build **strong / straight-line wind first** (site-conditioned), **then
   tornado** (areal). **Hurricane deferred** (field-intensity — the one unbuilt coupling bucket). Settled in
   `DD-WN-2`.
3. **NEW layer-0 = the hazard-definition layer.** Wind is the first peril where **no data product pre-defines
   the event** (MESH did for hail, FSim for wildfire) — so we **author** the definition from standards. The
   plan-of-record is [`plans/convective_wind/00_hazard_definition.md`](../../../plans/convective_wind/00_hazard_definition.md).
4. **Coupling — wind tours all three buckets** (the "sub-perils matter" payoff): **tornado = areal hit-or-miss**
   (reuse hail's Minkowski, path-aware), **strong wind = site-conditioned** (reuse wildfire's M2; the **ASCE
   7-22 RP gust surface = a pre-integrated return-level profile**, the FSim analogue), **hurricane =
   field-intensity** (deferred). Deep-dive that teaches it: [`discussion/convective_wind/02`](../../discussion/convective_wind/02_coupling_buckets_and_wind.md).
5. **Thresholds anchored in standards:** 3-s gust observable; μ = NWS ≥58 mph (strong) / EF scale (tornado);
   bound L ≈ EF5 113 m/s; **two thresholds kept distinct** — meteorological event (counts λ) vs IEC-61400
   turbine survival (damage onset, ~52–70 m/s) → **anchored** curve. Severity = bounded GPD (EVT-on-intensity).
6. **Two sites** (renewablesinfo boundary DB, mirroring Hayhurst/Matrix): **Traverse Wind Energy Center, OK**
   (~999 MW, high/proving) · **Shepherds Flat, OR** (~845 MW, low/baseline). `DD-WN-10`.
7. **13 decisions** (`DD-WN-1..13`) + assumptions (`AWN-*`). Built + adversarially reviewed + fixed via **two
   workflows**; review caught a **stale DD-WN cross-ref numbering** in the m-plans → fixed → **verified 5/5**.
8. **Notebook structure (settled):** shared `layer0`/`m0`/`m1`; **fork at M2** (`strong_wind/` + `tornado/`);
   **shared M3**; **M4 combines** both sub-perils into one annual-loss distribution + per-sub-peril attribution.
9. **Also done earlier this session (already committed + pushed):** wildfire **M4 close-out** (Hayhurst EAL
   0.0004% / ~$151·yr⁻¹ — negligible; Matrix EAL 0.29% / ~$1.12M, PML250 14%) → **wildfire × solar M0–M4
   complete**; the **Monte-Carlo effective-sample-size learning** (repo: [`learning_logs/10`](../../../learning_logs/10_monte_carlo_effective_sample_size.md); personal-KB note `hazard_math/06` — see loose ends).
   Commits `20ac205` (hail clarifications) · `e7486f3` (wildfire M0–M4 pipeline) · `78ec5ff` (learnings 07–10),
   CI green.
10. **This task's commits:** `5010a61` (wind route-zero) + this handoff — on `main`, pushed.

## Read these before starting (in order)

1. [`plans/convective_wind/00_hazard_definition.md`](../../../plans/convective_wind/00_hazard_definition.md) — **layer-0**: the "why
   this layer exists" table, the coupling-taxonomy primer, the two-thresholds anchored-curve.
2. [`discussion/convective_wind/02_coupling_buckets_and_wind.md`](../../discussion/convective_wind/02_coupling_buckets_and_wind.md) —
   the coupling deep-dive (site-conditioned vs field-intensity; the old-repo "got strong-wind coupling wrong"
   evidence).
3. [`plans/convective_wind/decisions.md`](../../../plans/convective_wind/decisions.md) — `DD-WN-1..13` (settled choices + revisit
   triggers).
4. [`plans/convective_wind/README.md`](../../../plans/convective_wind/README.md) (phase table) +
   [`m0_input_data.md`](../../../plans/convective_wind/m0_input_data.md) + [`m1_catalog.md`](../../../plans/convective_wind/m1_catalog.md).
5. **Prior art to mine** (symlink `hazard_analysis/`): `src/mag_sim/mag_sim_methodology.md` (the bounded-GPD
   μ/L analytic solve; `HAZARD_CONFIG` μ=25.92 m/s, L=113 m/s); `docs/suggested_architecture/issues/strong-wind-var-worked-example.md`
   (the Method-0-vs-3 ~12× proof); `config/subsystems/wind_config_default.csv` (the turbine subsystem split);
   `src/noaastorm_fetcher.py` (the SPC/Storm-Events pull). **Mine, then it can be deleted** (temporary symlink).
6. **Connected learnings/notes:** [`learning_logs/09`](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)
   (pre-integrated vs extracted → why ASCE-surface = profile-assembly) · [`learning_logs/10`](../../../learning_logs/10_monte_carlo_effective_sample_size.md)
   (effective sample size → tornado sparse tail); `hazard_math/05` (EVT-on-intensity) + `06` (MC error) *— note
   06 is in the personal KB (`Learning/`), not this repo.*
7. **The reference:** `docs/google_drive_docs/Hazard_Data_Reference.docx` (the §"Tornado & Strong Wind" section
   grounds every threshold; extract it with the zipfile snippet in [`notes.md`](notes.md)).

## Repro / verify current state

```bash
source .venv/bin/activate                          # python3.12, kernel "hazard_modeling"
git remote -v                                       # origin = git@github.com-work:D-ivyy/Hazard_Modeling.git (push via SSH)
git log --oneline -2                                # 5010a61 wind route-zero ; <hash> session handoff
# every DD-WN reference in the m-plans resolves to a real decision header:
for d in $(grep -rohE "DD-WN-[0-9]+" docs/plans/convective_wind/m*.md | sort -u); do
  grep -q "## $d " docs/plans/convective_wind/decisions.md && echo "OK $d" || echo "MISSING $d"; done
# NO wind notebooks/data yet — nothing to execute. The build starts fresh from layer-0/M0.
```

## Available vs needs-fetching (for the wind build)

- **In repo:** the 15 route-zero docs; canonical `DD-WN-*` / `AWN-*`. **No wind notebooks, no wind data.**
- **Fetch at M0 (none pulled yet):** **ASCE 7-22** basic-wind RP maps + Ch 32 tornado maps · **SPC SVRGIS**
  (~70k tornado tracks 1950+, severe-wind reports 1955+) · **NOAA Storm Events** · **EF** bins · **USWTDB**
  turbine points · the **boundary polygons** for Traverse + Shepherds Flat
  (`renewablesinfo_org/data/dimensions/boundary/powerplants_enriched_v2.parquet`, OSM `source`=fuel,
  `output`=capacity).
- **Symlinks (gitignored, local-only):** `hazard_analysis` (prior art — mine then delete) · `model-gpr` ·
  `infrasure-damage-curves` (the turbine curve lands here) · `Learning` (personal KB — `hazard_math/06`) ·
  `renewablesinfo_org` (boundary DB).

---

## ▶ NEXT ACTION (primary focus) — build the wind notebooks, layer-0 → M4

Mirror the hail/wildfire notebooks-first rhythm — one notebook at a time, each cell legible (description → code
→ output → plots → tables), every basic verified against a known answer. Build order:

### Phase A — layer-0 + M0 (`Notebooks/convective_wind/m0_input_data/`)
Per [`m0_input_data.md`](../../../plans/convective_wind/m0_input_data.md), three M0 notebooks:
**`01_asce_hazard`** (the ASCE RP gust surfaces — strong-wind basic-wind + Ch 32 tornado; the **pre-integrated
profiles** — build FIRST, fastest path to a real number, the FSim parallel), **`02_spc_storm_record`** (the
SPC/Storm-Events extraction — the catalog-fit cross-check + tornado path stats), **`03_asset_geometry`** (the
two sites: boundary polygon + USWTDB turbine points; two exposure views). **Bias-correct SPC** (population bias)
*before* any frequency fit (`AWN-1`). Honor the exploratory-data-notebook principle.

### Phase B — M1 catalog (`Notebooks/convective_wind/m1_catalog/01_catalog`, one notebook, split by sub-peril)
**Strong wind = profile-assembly** from the ASCE RP surface (pre-integrated, **no λ-fit** — `DD-WN-3`,
learning-09). **Tornado = Poisson λ + EF/path-stats** fit from SPC (`DD-WN-5`). **Severity = bounded GPD**
(μ-anchored, L-truncated, ξ<0; **fit μ_mean to observed gusts, NOT back-solved from an EAL target** — the old
repo's weakness — `DD-WN-8`).

### Phase C — M2 coupling (FORK)
**`m2_coupling/strong_wind`** = site-conditioned (reuse wildfire's thin M2; p_hit≈1, no spatial factor;
`DD-WN-4`). **`m2_coupling/tornado`** = areal hit-or-miss (reuse hail's Minkowski, **path-aware thin-rectangle**
`(L+a)(w+a)`; `DD-WN-5`). Tornado is sparse → invoke **learning-10** (report SE; TVaR alongside VaR — VaR floors
to $0 in the sparse tail). Note per-turbine point-cloud (USWTDB) vs areal-footprint.

### Phase D — M3 damage (`Notebooks/convective_wind/m3_damage/01_damage`, SHARED)
Anchored subsystem logistic on 3-s gust, IEC-survival onset, operational-state aware (`DD-WN-11`); subsystem
reach differs by sub-peril (strong wind = aero; EF-level tornado also takes the tower). Build the turbine curve
in `infrasure-damage-curves`. **Approximate now, accurate later** (like hail/wildfire).

### Phase E — M4 loss & metrics (`Notebooks/convective_wind/m4_loss_metrics/01_loss_metrics`, SHARED + COMBINED)
Shared compound-Poisson/NegBin MC; **combine both sub-perils** into one annual-loss distribution + a
strong-wind/tornado split. EAL/VaR/PML/TVaR off the **sampled** distribution, **% of TIV alongside $**. Strong
wind well-populated; tornado rare. **Never Method 0** (the expected-loss shortcut — `DD-WN-13`).

### Gotchas the next session must know
- **No public stochastic tornado/convective-wind catalog** (proprietary: Verisk/RMS) → the **ASCE RP surfaces
  are the pre-integrated spine**; the SPC-fit is the documented cross-check (`DD-WN-3`).
- **IEC 61400 numbers + L = 113 m/s come from the settled framing / old-repo `HAZARD_LIMITS`, NOT the Hazard
  Data Reference** — `AWN-*` to confirm against the actual turbine model per site. The 58 mph / EF bins / 3-s
  gust / ASCE surfaces **are** from the reference.
- **Reuse, don't reinvent, M2:** strong wind = wildfire's site-conditioned M2; tornado = hail's areal Minkowski.
  The shared MC engine is **untouched** by either.
- **Push** via SSH `github.com-work` (gh HTTPS token lacks `workflow` scope). Repo is **public** → no secrets.
- **Loose ends (uncommitted):** (1) the **personal-KB note `hazard_math/06`** (Monte-Carlo error & effective
  sample size) + its 04/05 cross-ref edits live in `~/Desktop/Learning` — a **separate git repo, uncommitted
  there**; (2) **`docs/extra/discussion/conus_grid/`** — a *separate* CONUS-gridded-product discussion set
  (use-case 2) from another session, **untracked**, left as-is (not part of this work).
- **The 3 `docs/google_drive_docs/*.docx`** show modified (binary churn; Drive is source of truth) —
  intentionally left unstaged.
