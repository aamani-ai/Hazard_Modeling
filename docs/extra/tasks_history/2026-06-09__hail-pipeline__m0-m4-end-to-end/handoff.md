# Handoff — read me first (next session / model switch)

## 60-second summary (what happened, not how)

1. Built the **full hail × solar pipeline end-to-end in notebooks: M0→M1→M2→M3→M4** — evidence → catalog →
   coupling → damage → annual loss & risk metrics. Hazard **1 of 3** (plan: hail → wildfire → wind, *then*
   architecture).
2. **M0:** NOAA Storm Events (point reports) + MRMS MESH (gridded radar footprints), two sources behind one
   interface. `02_mrms_aws` opens with a from-scratch "what is this data" walkthrough.
3. **M1 catalog:** MRMS hail-days → canonical `Event` records as **footprint polygons** (GeoParquet) +
   manifest; NOAA cross-checks (no events added); **NegBin frequency fitted** on the full ~5.65-yr record
   (λ_collection = 29.6/yr, φ = 3.37).
4. **M2 coupling:** per-event **Minkowski hit probability** `(√F+√s)²/A` (fixes the old repo's `F/A` bug);
   `λ_asset = 0.26/yr`.
5. **M3 severity:** **capex-weighted subsystem blend** from the `infrasure-damage-curves` repo (caps ~34% of
   TIV — a *temporary* asset-level curve; the repo gets a full revamp later).
6. **M4 metrics:** compound-Poisson MC (NegBin counts, LOTV rule, cap-per-year) → **EAL 5.7%, 1-in-100 ~54%,
   1-in-250 ~62% of TIV** (shown as % of TIV). Real but **record-limited**.
7. **Math-validated** by a 23-agent audit: **sound, no calc errors**; the old repo's 3 bugs (LOTV, frame
   mismatch, spatial factor) all correctly handled.
8. **Docs/decision infrastructure** stood up: `learning_logs/01–05`, assumptions register **A1–A23**,
   decisions **DD-1..4**, per-phase plans, per-layer READMEs, build-strategy doc, `scripts/README`.
9. **Published:** `D-ivyy/Hazard_Modeling` (private) via SSH (`github.com-work` identity).
10. **Honest caveats:** EAL ~5.7% is a touch high (likely MESH-FAR-inflated frequency); deep tail is
    bootstrap-truncated; the damage curve is temporary. All logged as `deferred` in the assumptions register.

## Read these before starting (in order)

1. `docs/plans/00_build_strategy.md` — **the plan**: notebooks-first, 3 hazards, then architecture.
2. `docs/plans/hail/decisions.md` (DD-1..4) + `docs/plans/hail/assumptions.md` (A1–A23, the **deferred-work
   backlog**).
3. `docs/learning_logs/README.md` → 01–05 (the derived knowledge: short-record splice, NegBin prior, complex
   raw data, multi-source decompose, the damage-curve's three coupled choices).
4. `Notebooks/hail/README.md` + each layer's folder `README.md` — the working pipeline to **mirror** for the
   next hazard.
5. `docs/principles/` (esp. *standard interface, not standard physics*) + `Notebooks/hail/m0_input_data/02_mrms_aws.ipynb` §1–§7 (the from-scratch data pattern).

## Repro / verify current state

```bash
source .venv/bin/activate    # python3.12, kernel "hazard_modeling"
# data artifacts (parquets) are gitignored; the cache too. To rebuild from scratch:
python scripts/scan_mrms_record.py 2020-10-15 2026-06-08         # re-pull MRMS (~10-20 min) → wide M0
# then re-run the chain: m1_catalog → m2_coupling → m3_damage → m4_loss_metrics (jupyter nbconvert --execute)
cat data/hail/hayhurst_hail_m4_metrics.json                       # the headline metrics
git remote -v                                                     # origin = git@github.com-work:D-ivyy/Hazard_Modeling.git
```

## Available vs needs-fetching

- **Available (in repo):** all notebooks (`.py`+executed `.ipynb`), the manifests/summaries/GeoJSON, the
  damage-curve spec, the `mrms_raw/_manifest.json` (index of pulled tiles), all docs.
- **Local-only / NOT in repo (gitignored):** `.env` (HYDRONOS_API_KEY), `.venv/`, `data/hail/mrms_raw/`
  (~905 MB of GRIB tiles), all `*.parquet`. A **fresh clone must re-run the scan** (re-downloads tiles) before
  re-executing M1+. On *this* machine the cache + parquets already exist.
- **Symlinks (gitignored, machine-local):** `model-gpr`, `hazard_analysis`, `infrasure-hazard-competitive-research`,
  `renewablesinfo_org`, `Learning`, `infrasure-damage-curves`.

---

## ▶ NEXT ACTION (primary focus)

### Phase A — Hazard #2: **Wildfire × Solar**, end-to-end in notebooks (M0→M4)

Mirror the hail structure (`Notebooks/hail/` → `Notebooks/wildfire/`), but **the physics differ** — this is
the test of "standard interface, not standard physics":

- **Coupling type changes:** wildfire is **site-conditioned** (loss set by a local fire intensity/proximity at
  the site), **not** areal hit-or-miss → the M2 Minkowski formula does **not** apply; build the site-intensity
  coupling instead (see `hazard_math/` + methodology §4 "site-conditioned").
- **Intensity metric + data differ:** fire perimeters / FRP (MODIS/VIIRS) / burn-probability / distance;
  NRI wildfire; Hydronos `fema_disaster`. Meet each source from-scratch (`learning_logs/03`).
- **Damage curve:** `infrasure-damage-curves/research/WILDFIRE_x_SOLAR.md` + the `wildfire/` curve folder
  (vendor + capex-weight like hail's M3).
- **Reusable as-is:** the **M4 compound-Poisson MC + metrics machinery**, the assumptions/decisions/learning_logs
  discipline, the per-layer README + % -of-TIV conventions. (Frequency may be Poisson/NegBin; EVT/financial deferred.)
- **Per-hazard `decisions.md`/`assumptions.md`:** start a wildfire set (or extend) — don't reuse hail's silently.

### Phase B — Hazard #3: Wind (or another) — same pattern (likely field-intensity or areal coupling).

### Phase C — *Then* design the production architecture (DB-connected dev code) — **deferred** until A+B done
(use the owner's `Learning/` project-structure reference *then*).

### Parallel / on-demand — Hail refinement backlog (all `deferred` rows in `assumptions.md`)

- **Damage-curve revamp** (the owner is doing this in `infrasure-damage-curves`): better subsystem weights,
  **conditional-DR distribution** (not scalar mean), **plant-specific at-risk value-allocation** (A15, A17,
  learning_logs/05). When ready, drop the new spec into `data/hail/damage_curves/` and re-run M3→M4.
- **NOAA-calibrated λ extension** (DD-3 Stage 2): bias-correct MESH (FAR) against NOAA over a longer record →
  lower, more credible frequency (this is the main lever to bring EAL down from ~5.7%).
- **EVT-GPD tail** (A23) for deep return periods; **financial terms** (deductibles/limits/BI — methodology §9).

### Gotchas the next session must know

- Notebooks are **jupytext `.py` (source) ↔ `.ipynb`**. Markdown-only edits: `jupytext --to notebook --update`
  to preserve executed outputs; code edits: re-run with `nbconvert --execute`.
- `01_noaa_hydronos` hits the **Hydronos API** (needs `.env` `HYDRONOS_API_KEY`) — don't re-run blindly; it
  re-fetches. M2–M4 are offline (read parquets).
- **Push** to D-ivyy uses SSH `github.com-work` (the gh HTTPS token lacks `workflow` scope) — see
  `docs/plans/remote_repo_push_plan.md` + the `github-push-setup` memory.
- The metrics are **real but record-limited** — don't quote them as final; the severity curve is temporary and
  the deep tail is truncated.
