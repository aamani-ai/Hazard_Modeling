# Building a Hazard × Asset CONUS Grid

**A reusable how-to for standing up a new (hazard × asset) gridded risk layer on the shared engine** —
what the system *is* as built, the plausibility-QC contract both drivers share, the five things a new
peril × asset has to fill in, and the V1 constraints to be honest about. The worked example throughout is
**hail × solar**, the first cell built end-to-end.

> **What this is, and isn't.** This is a **guide** — forward-looking, "here's how to do the next one." It is
> not the decision record (that's [`docs/plans/hazard_conus_grid/`](../plans/hazard_conus_grid/)), and it is
> not a per-hazard snapshot (that's [`docs/hazards/`](../hazards/)). It *links down* into those; it never
> copies them. When a number here and a number there disagree, the plan/registers win — fix this.

---

## 1. What the grid is — one engine, two drivers

The CONUS grid is a **per-cell catastrophe-risk layer**: take the 0.25° benchmark grid over the Lower 48,
place a **canonical asset at every served cell**, and score each cell end-to-end (M0→M4) into the standard
risk-metric family (EAL, VaR, PML, TVaR; $ and % of TIV). It is **use-case 2** — a comparable screening map,
not a single trustworthy number.

The single most important design fact: **there is one engine, driven two ways.**

```
                       M0 ───► M1 ───►[ BOUNDARY ]───► M2 ───► M3 ───► M4
                      (raw)  (hazard layer)         (couple) (damage) (loss)
                       └────── peril · ASSET-FREE ──────┘└──── peril × asset ────┘
                                        │  the typed per-cell hazard-distribution object
              ┌──────────────────────────┴──────────────────────────┐
              ▼                                                       ▼
      CONUS GRID DRIVER                                      DEEP-PER-ASSET DRIVER
      canonical 100 MW at every 0.25° cell                  one real asset, its true site
      ▶ 13,085-cell comparable map (this guide)             ▶ one trustworthy number (future driver)
              └─────────────── same engine · same QC · same contracts ───────────────┘
```

**The boundary is the rule that makes this work.** Everything left of it (M0 raw evidence, M1 frequency +
severity) is the **peril** — asset-free. Everything right of it (M2 coupling, M3 damage, M4 loss) is the
**(peril × asset)** cell. The asset never enters until M2. So the hazard layer, the catalog, the frequency,
the severity — and **the plausibility QC** (§3) — are identical no matter what asset sits in the cell, and
identical no matter which driver consumes them. *Off-grid == on-grid.* (DD-G11/G12.)

---

## 2. The as-built system

Three installable packages, plus the notebooks and the deferred deep-per-asset driver:

```
shared/                          ← the risk ENGINE — imports NO peril (the "engine")
  src/risk_engine/
    engine/        monte_carlo · metrics · quantile · validate   (M4: run_cell_mc, exceedance_metrics)
    exposure.py    M2 coupling-type dispatch: couple_areal(F, s, A) → p_hit   (areal | field | site)
    vulnerability.py  M3 framework: capex_weighted_damage_ratio(size, subsystems)
    orchestration.py  run_cell_risk(...) — M2→M4 for one cell × policy, generic
    config.py      the canonical RP / VaR / PML / TVaR ladders, pinned once
    io_base/       gcs helpers (is_gcs_uri, up/download, prefix_exists)

pipelines/hail/                  ← the PERIL (M0/M1) — imports risk_engine, never the reverse
  src/hail/
    config.py            THRESHOLD_MM · PRODUCT · the 0.25° grid · coverage enum · the M0 contract
    mrms_m0.py           the SourceAdapter: build_daily_panel (raw MESH tile → per-cell-day evidence)
    m1_hazard_layer.py   build_m1_hazard_layer (reconciled M0 → one hazard row per cell)
    plausibility_qc.py   apply_plausibility_qc (the asset-free QC — §3)
    coupling.py          hail_event_p_hit (areal field-mapping → risk_engine.couple_areal)
    damage.py            load_curve + hail_damage_ratio (the hail×solar curve → risk_engine.vulnerability)

drivers/conus_grid/              ← the canonical-asset-at-every-cell DRIVER
  src/conus_grid/
    canonical_assets.py  CANONICAL_SOLAR (100 MW / 1.5 km² / $148.3M) · SEVERITY_POLICIES · SEED · MC_YEARS
    grid_driver.py       load_severe_events + run_grid (fan M0 events × M1 × asset over all cells)
    entrypoint.py        run the full grid → the per-cell risk layer + summary + metadata
```

| Layer | Where the *generic* part lives | Where the *peril/asset* part lives |
|---|---|---|
| **M0** raw → cell-day evidence | — | `pipelines/<peril>` SourceAdapter |
| **M1** frequency + severity (the boundary object) | — | `pipelines/<peril>` M1 fit **+ plausibility QC** |
| **M2** coupling | `shared/exposure` (areal/field/site dispatch) | `pipelines/<peril>` field-mapping |
| **M3** damage | `shared/vulnerability` (curve framework) | `pipelines/<peril>` curve artifact |
| **M4** loss + metrics | `shared/engine` + `shared/orchestration` | — (it only sees `p_hit` + `conditional_loss`) |
| driver | `drivers/conus_grid` | `canonical_assets.py` (the asset) |

The engine is **leak-clean**: no `*_solar`, no `CANONICAL_*`, no `mesh_*`, no hardcoded ladders inside
`shared/`. It knows only the two typed objects — the hazard-distribution it consumes and the risk-metrics it
emits ([`contracts.md`](../plans/hazard_conus_grid/architecture/contracts.md)).

---

## 3. The plausibility QC — the contract **both** drivers share

This is the piece that makes the whole architecture pay off, so read it carefully.

Raw MRMS MESH is a radar *estimate*: skillful at hail **occurrence**, unreliable for hail **size**. It emits
physically-impossible magnitudes (our record max is **1,437 mm** — there is no 1.4 m hailstone; **585** CONUS
cells have a day ≥ 300 mm) and spurious **rates** (a cell at ~45 severe days/yr). The plausibility QC detects
and handles both — **without ever touching the frequency count**. The decided rule lives in
[`05_plausibility_qc_rule.md`](../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md); the code is
`pipelines/hail/plausibility_qc.py::apply_plausibility_qc`. The rule is **derived, not assumed** — the
data-product + MESH-nature research pass (§4, Step 0) is what surfaced the impossible values and the physical
ceiling; a new peril writes its QC only after that pass.

| Failure | Rule (V1) | In the hail × solar grid |
|---|---|---|
| **Impossible magnitude** | Cap the severity *summary* at the physical ceiling (US record, Vivian SD 2010 = **203.2 mm**); keep the raw beside it; **≥ 300 mm = hard artifact**; never delete. | 1,437 → 203.2 mm; **749** cells capped (164 in 203–300, **585** hard artifacts) |
| **Impossible rate** | **Flag** suspicious high-λ cells (ours: a percentile cut) and **hold them out of reportable loss**; the rate itself is unchanged. Pooling deferred. | **61** spikes (λ > 8.9/yr) held out; 13,024 eligible |
| **Curve domain (M3, asset-specific)** | Clamp the damage-curve input at its validated range. | solar curve clamps at 100 mm (the `cap_100mm` policy) |

**Why this is asset-free, and therefore cross-driver.** The magnitude and rate failures are properties of
the *MESH signal*, not the asset — so the QC lives at M0/M1, *above* the boundary. By construction it is
consumed by **both** drivers. The grid uses it today. **The deep-per-asset driver must use it too** — and
this is not hypothetical:

> Today the deep runs sit at one or two **safe** sites, so the QC hasn't bitten. But the moment a deep-time
> site lands in the **Ohio Valley** (where the literature documents MESH over-reads — and where our ≥ 300 mm
> hard-artifacts visibly cluster) or a **sparse Western cell** (radar under-detection), it hits the *same*
> plausibility failure and needs the *same* treatment. **Building the shared QC so both drivers inherit it is
> the entire reason the architecture is shaped this way.** The deep-per-asset notebooks predate the package
> and don't apply it yet — closing that is the next architectural to-do (§7).

**What the QC changes, and what it doesn't (be precise).** It makes the *hazard layer* physically honest
(capped severity, flags). For **solar loss specifically it is ~invariant** — capping severity moves grid EAL
by at most 0.55 %TIV-points (≤ 7.8% on material cells), because the solar damage curve is ~99% saturated by
100 mm. That is the decided result, not a gap: for solar the magnitude tail is a *minor* driver. The cap's
real job is hazard-layer honesty and **future assets that fail above 100 mm** (where it will move loss).

**Handled in V1 vs. documented-but-deferred** (the honest split):

| Handled now (honesty-load-bearing) | Deferred (accuracy-load-bearing) |
|---|---|
| physical cap + flags; ≥300 mm hard-artifact | MESH de-biasing (Murillo & Homeyer refit) |
| frequency-spike flag + hold-out | frequency **pooling / spatial shrinkage** (replaces flag-and-hold) |
| rely on M3 saturation for solar | EVT severity tail; conditional-DR distribution |
| raw severity + severe-day counts kept intact | record extension (MYRORSS back-fill) |

---

## 4. How to add a new hazard × asset — the five blanks

A new (peril × asset) cell is **five blanks to fill**; everything else is reused unchanged (DD-G13). If
adding one turns out to be more than this, the abstraction is wrong — fix the engine, don't fork it.

### Step 0 — the research pass (the prerequisite, and the highest-leverage step)

**Before any blank, do a per-hazard data-product + QC research pass — and keep the factual findings separate
from the decision they feed.** This is what tells you *which* source, *how* to define frequency, and — above
all — **what the plausibility QC rule even is.** You cannot write blank #2's QC by guessing; you derive it
from how the data actually fails. For hail this was, consistently, the most useful work we did:

```
  FACTUAL research  ([REF] vs [OURS], no recommendations)      →   DECISION
  ───────────────────────────────────────────────────              ──────────────────────────────
  00_m1_data_products_research  what products exist, coverage  →   01_m1_sourcing_triage   source + why
  04_mesh_nature_and_qc_research how MESH is built, why it      →   05_plausibility_qc_rule the V1 QC rule
                                emits impossible values, its             (cap 203 mm · ≥300 hard
                                bidirectional event-dependent bias        artifact · freq-spike hold-out)
        └──────────────── evidence ────────────────┘            └──── the rule, grounded in the evidence ────┘
```

Two habits made this pay off: **factual findings stay separate from the decision** (the research doc records
what's true, with sources, *no* recommendations; the decision doc chooses), and every claim is tagged
**`[REF]`** (literature) vs **`[OURS]`** (our own observation). It shows directly in the hail QC — the 203 mm
cap is the US hailstone record `[REF]`; the ≥300 mm hard-artifact line and the frequency-spike rule are
`[OURS]`, *because the research found no published standard for them*. A new peril (wildfire/FSim, convective
wind) gets the same pass first — its failure modes differ, so its QC differs, and only the research tells you
what it is. Research home: [`discussion/conus_grid/<peril>/`](../extra/discussion/conus_grid/).

| # | Blank | What it is | Hail × solar (worked example) | Home |
|---|---|---|---|---|
| 1 | **SourceAdapter** | raw source → per-cell-day evidence (+ a QC hook) | MRMS MESH tile → `build_daily_panel` | `pipelines/<peril>/<src>_m0.py` |
| 2 | **M1 fit** | frequency + severity → the hazard-distribution object **+ plausibility QC** | `build_m1_hazard_layer` + `apply_plausibility_qc` | `pipelines/<peril>/m1_*.py`, `plausibility_qc.py` |
| 3 | **Coupling type** | areal \| field-intensity \| site (dispatched by `shared/exposure`) | **areal** (Minkowski `(√F+√s)²/A`) | `pipelines/<peril>/coupling.py` |
| 4 | **Damage curve** | the M3 contract — a curve artifact | capex-weighted logistic, caps ~34% | `pipelines/<peril>/damage.py` + curve JSON |
| 5 | **Config** | peril id · source URIs · thresholds · canonical asset(s) | `THRESHOLD_MM`, `CANONICAL_SOLAR` | `pipelines/<peril>/config.py`, `drivers/conus_grid/canonical_assets.py` |

> **Reused unchanged:** `shared/engine` · `shared/exposure`/`vulnerability`/`orchestration` · both drivers ·
> `io_base` · the two contracts · the %-of-TIV reporting. A new *asset* on an existing peril is even less —
> usually just blanks 3–5.

**The recipe (each step gated before the next):**

```
0. research pass        data-product + QC nature   → fixes the source, the frequency def, AND the QC rule
1. SourceAdapter        raw → cell-day evidence    GATE: reproduce a sample of reconciled days, 0 diff
2. M1 fit + QC          → the hazard layer         GATE: reproduce the per-cell layer; QC flags validate
3. coupling + 4. curve  p_hit + conditional_loss   GATE: a selected-cell smoke reproduces by hand
5. config + driver      run the grid               GATE: driver on the smoke cells == the smoke, bit-for-bit
   → full-CONUS run      the risk layer            then: map it, sanity-check the geography
```

Honor the **A/B/C source-qualification boundary + the promotion gate** (coverage denominator · target
reference base · source-era comparability · bias treatment · frequency definition · tail treatment ·
provenance) before a new source enters M1 —
[`gridded_radar_source_qualification.md`](../plans/hazard_conus_grid/common/gridded_radar_source_qualification.md).

---

## 5. Constraints — what the V1 grid honestly can't do

State these on every layer the grid feeds; the deep-per-asset driver shares them at a sparse site.

**Sparse cells / short record / no smoothing.** 974 cells (7.4%) have **zero** severe hail in the 5.7-year
record → EAL = 0. The West is genuinely sparser (23% of cells west of −110° are zero-hail; median 2 severe
days vs. 13 in the East). **This is not missing data** — coverage is complete (`observed_day_fraction ≈ 1.00`
everywhere; MRMS is a gap-filled CONUS field). Those cells *have* data; it shows little hail because severe
hail genuinely *is* rare there (e.g. CAISO: lots of solar, little hail → ~zero risk, which is broadly
correct). The honest limitation:

> The grid **cannot distinguish "genuinely no hail" from "rare hail not yet observed,"** and it does **not
> smooth or extrapolate** into sparse cells. A true 1-in-20-yr cell can read a hard zero on a 5.7-yr record.

Three remedies, all deferred, each fixing a different part:

| Symptom | Remedy (deferred) |
|---|---|
| rare-hail cell reads hard zero on a short record | **record extension** (MYRORSS back-fill, 5.7 → ~20+ yr) |
| isolated zero cells, no neighbor borrowing | **spatial pooling / shrinkage** |
| Western "zeros" may be radar *under-detection*, not absence | **MESH de-biasing** |

**Severity is provisional.** Raw/provisional MESH; the magnitude tail is capped + flagged, not de-biased. No
grid loss number is reportable — it's a screening layer, labeled `MRMS_ONLY`, `V1`, `provisional`.

**Daily event grain.** One event = one hail-day (the MRMS product is a 24-h max). Fine for hail; sub-daily is
a future refinement.

---

## 6. Reproduction gates — the discipline that lets us trust it

Every extraction was proven **bit-identical** against the worked outputs before it moved — no expensive
re-runs, no "trust me." Run them with `pytest shared/tests pipelines/hail/tests drivers/conus_grid/tests`.

| Gate | Proves | Result |
|---|---|---|
| `shared/tests` engine smoke | M4 engine == the worked notebook | max rel diff **2.1e-16** |
| `pipelines/hail` M0 adapter | `build_daily_panel` == reconciled M0 (sample dates) | **0.0** diff |
| `pipelines/hail` M1 | `build_m1_hazard_layer` == the 13,085-cell M1 | **0.0** diff, all 52 cols |
| `pipelines/hail` plausibility QC | cap/flags correct; **frequency untouched** | validated on the real M1 |
| `drivers/conus_grid` smoke | the driver == the 5-cell smoke, both policies | max rel diff **2.06e-16** |

Status: hail × solar is built end-to-end — M0 → M1 (QC'd) → M2/M3 → M4 → the 13,085-cell risk layer + maps.
The map geography is credible (loss tracks the central-Plains/Upper-Midwest corridor); the QC's hard-artifacts
cluster over the Ohio Valley exactly where the MESH literature says they should.

---

## 7. Open to-dos — so nothing is left implicit

1. **Deep-per-asset adopts the QC** *(the cross-driver gap, §3).* The deep-per-asset notebooks predate the
   package and don't apply `apply_plausibility_qc` yet. Safe at today's sites; **required** before a deep run
   in an outlier (Ohio Valley) or sparse (West) region. Close it by having the deep-per-asset M1 consume the
   QC'd hazard layer — the same contract the grid uses. The full migration (when we're ready, the nuances,
   the plan) is worked through in
   [`discussion/deep_per_asset/01_notebooks_to_second_driver.md`](../extra/discussion/deep_per_asset/01_notebooks_to_second_driver.md).
2. **Typed, versioned contracts** (Phase C): `shared/schemas` for the hazard-distribution + risk-metrics
   objects, `schema_version` from day one — [`contracts.md`](../plans/hazard_conus_grid/architecture/contracts.md).
3. **Second peril — wildfire** (Phase D): the real test of §4. If it isn't mostly "fill the five blanks," the
   abstraction is wrong.
4. **Deferred accuracy work**: pooling/shrinkage, record extension, MESH de-biasing, EVT tail (§3, §5).
5. **Notebook hygiene**: the two earliest solar smokes (`01`, `02`) predate the package (inline engine code);
   kept as dev record, marked superseded — not re-pointed (that would rewrite history).

---

## 8. Go deeper

- **Decisions / migration:** [`architecture/`](../plans/hazard_conus_grid/architecture/) (README · contracts · migration_plan) · [`decisions.md`](../plans/hazard_conus_grid/decisions.md).
- **The research pass (Step 0, the model):** sourcing [`00_m1_data_products_research`](../extra/discussion/conus_grid/hail/00_m1_data_products_research.md) → [`01_m1_sourcing_triage`](../extra/discussion/conus_grid/hail/01_m1_sourcing_triage.md) · QC [`04_mesh_nature_and_qc_research`](../extra/discussion/conus_grid/hail/04_mesh_nature_and_qc_research.md) → [`05_plausibility_qc_rule`](../extra/discussion/conus_grid/hail/05_plausibility_qc_rule.md).
- **The hazard snapshot:** [`docs/hazards/hail/`](../hazards/hail/README.md) (asset-free) · [hail × solar](../hazards/hail/solar.md).
- **The code:** [`shared/`](../../shared/README.md) · [`pipelines/hail/`](../../pipelines/hail/README.md) · [`drivers/conus_grid/`](../../drivers/conus_grid/).
- **The worked notebooks:** [`Notebooks/hazard_conus_grid/`](../../Notebooks/hazard_conus_grid/README.md) (M0 → M1 → M2–M4 → the grid maps).
