# 01 — Shifting the deep per-asset notebooks onto the shared engine (the second driver)

*A discussion doc — thinking through **when** we're ready to lift the deep-time per-asset run from notebooks
into the package (as the engine's second driver), and **what it takes to do it right**. Not a commitment to
build now. The grid driver proved the playbook; this maps the same move for use case 1.*

> **One-line state:** the engine is already shared, so the deep run *can* sit on it — but it isn't a
> copy-paste of the grid. The deep run differs in **collection geometry, frequency model, and footprint**,
> and it needs **real-asset data** and the **plausibility QC** it doesn't yet apply. Those are the nuances.

---

## 1. Where the deep run stands today

Two products, one engine ([DD-G11](../../../plans/hazard_conus_grid/architecture/README.md)):

```
                          shared/risk_engine  (M2 couple · M3 damage · M4 loss — already generic)
                                   ▲                                   ▲
                 ┌─────────────────┘                                   └─────────────────┐
        CONUS GRID DRIVER (built)                                          DEEP PER-ASSET (notebooks today)
        canonical asset @ every 0.25° cell                                 one real asset, its true site
        drivers/conus_grid/                                                Notebooks/hail/ → drivers/deep_per_asset/ ?
```

The deep run (e.g. Hayhurst TX Solar, 24.8 MW, EIA 66880) lives in `Notebooks/hail/` and already drove the
engine *before* we extracted it — the engine extraction was validated partly by reproducing the deep-run
metrics (the Hayhurst bridge: **EAL ≈ 5.7% · PML₁₀₀ 54% · λ_asset 0.26**). So the M2–M4 math is shared
already; what's *not* yet packaged is the deep run's **M0/M1 collection** and a real-asset **driver**.

## 2. When are we ready? (triggers, not a date)

Don't migrate because we can — the notebooks work for one-off deep runs. Migrate when **reuse, scale, or
QC-consistency** demand it. Concrete triggers / prerequisites:

| Signal | Why it gates the migration |
|---|---|
| **Phase C contracts done** (typed, versioned) | both drivers should bind to *one* stable hazard-distribution + risk-metrics contract before the second driver hardens — else they drift |
| **Engine supports `(family, params)` frequency** | the deep run is **NegBin** (over-dispersion detectable); the engine today samples Poisson only (§3) |
| **A real deep-per-asset demand** (a portfolio / repeated runs, not a one-off) | a notebook is fine for one asset; a driver earns its keep at *many* assets or *repeated* runs |
| **An asset data source** (registry / DB) | the deep driver needs real-asset inputs (location, capacity, footprint, TIV) — the architecture's deferred "new database" |
| **QC ready to adopt** ✓ (done) | `apply_plausibility_qc` exists; the deep run must use it (§3) |

**Likely order:** Phase C first (stable contract) → the `(family, params)` engine extension → then the deep
driver, when a real multi-asset need appears. Until then the notebooks are the right home.

## 3. The nuances — where the deep run is *not* the grid

The boundary holds (M0/M1 = peril, asset-free-by-*type*; M2–M4 = peril × asset), but three things differ in
substance, and they're the whole reason this needs a design pass, not a port:

| Dimension | Grid (driver 1, built) | Deep per-asset (driver 2) | Consequence for the migration |
|---|---|---|---|
| **Collection region** | the exact 0.25° cell | a 50-mi window (~20,342 km²) **centered on the asset** | the deep M0/M1 is asset-**location**-dependent; M0/M1 must take a *collection region* (cell \| window) |
| **Frequency model** | Poisson (V1 default) | **NegBin** (φ ≈ 3.37 detectable; λ_collection ≈ 29.6/yr) | the engine's count draw must dispatch on `(family, params)` — the contract already anticipates this slot |
| **Footprint F** | severe-pixel area in the cell (proxy) | reconstructed event-footprint polygon | different F *computation*; the **same** `couple_areal` consumes it |
| **Asset input** | canonical (config) | a real asset (location/capacity/footprint/TIV) | the deep driver needs a real-asset data source |
| **MC depth** | 250k | 300k | config only |
| **Validation** | the 5-cell smoke gate | the **Hayhurst reference bridge** | the migration gate = reproduce the deep-run numbers bit-for-bit |
| **Plausibility QC** | applied | **not yet** (predates the package) | adopt `apply_plausibility_qc` — same contract (the cross-driver point) |

Two of these deserve real thought:

**(a) Collection geometry — and a reuse worth chasing.** The grid's per-cell M0 evidence is a natural
*substrate* for the deep window: a 50-mi circle is just the set of cells near the asset, so the deep M1 could
**aggregate the in-window grid cells** instead of re-collecting from raw MESH. That would make M0 genuinely
shared (per-cell evidence) and M1 differ only in the *aggregation region* (cell vs window). The catch: a
circle doesn't tile to 0.25° cells, so cell-aggregation is quantized vs the notebook's exact-circle raw read
— a fidelity question to settle (probably fine, given window *size* cancels — [LL06](../../../learning_logs/06_collection_region_size_cancels.md)). Decide: **windowed-M0 param on the shared pipeline, vs a separate deep collector.**

**(b) Frequency `(family, params)`.** The engine's `run_cell_mc` draws `Poisson(λ)`. The deep run draws
`NegBin` over the window, then thins by `p_hit`. So the count step must become `draw(family, params)` —
Poisson for the grid, NegBin for the deep run — which is exactly the typed frequency object
[`contracts.md`](../../../plans/hazard_conus_grid/architecture/contracts.md) reserved (`family="poisson",
params={lambda}` → NegBin slots in with no schema break). This is a small, anticipated engine extension, and
it's the *only* engine change the deep driver needs — everything else it reuses.

## 4. What the plan should look like

Mirror the grid migration — **relocate behaviour-preserving, gated by reproduction** — but the oracle is the
**Hayhurst deep-run numbers**, not the grid smoke. Sketch:

```
  A. confirm reuse     deep run calls shared/risk_engine as-is        GATE: M4 metrics unchanged
  B. (family,params)   add NegBin to the engine count draw            GATE: grid Poisson path still 0-diff;
                                                                             deep NegBin reproduces λ_collection
  C. deep M0/M1        windowed collection (reuse grid cells? §3a)     GATE: window frequency + severity match
  D. adopt the QC      apply_plausibility_qc on the deep M1            GATE: an outlier-site deep run is capped/flagged
  E. deep_per_asset/   the driver + a real-asset input contract       GATE: Hayhurst reproduces EAL/PML/λ_asset bit-for-bit
```

Each phase ships working; nothing moves until it reproduces. The database/registry (real-asset inputs) is its
own track — likely the gating dependency, and worth its own discussion doc when we get there.

## 5. Cross-references to anchor on

- **The architecture + contracts** (the second-driver intent + the `(family,params)` slot): [`plans/hazard_conus_grid/architecture/`](../../../plans/hazard_conus_grid/architecture/) — README · contracts · migration_plan.
- **The migration playbook** (the grid's, as the model): [`guides/building_a_hazard_asset_grid.md`](../../../guides/building_a_hazard_asset_grid.md).
- **The deep-vs-grid differences** (source of truth): [`hazards/hail/README.md`](../../../hazards/hail/README.md) §3 + [`hazards/hail/solar.md`](../../../hazards/hail/solar.md) (the two-deployments table + the deep headline numbers).
- **Why window size cancels:** [`learning_logs/06_collection_region_size_cancels.md`](../../../learning_logs/06_collection_region_size_cancels.md).
- **The deep-run assumptions:** [`plans/hail/assumptions.md`](../../../plans/hail/assumptions.md) (A1–A24, incl. NegBin + the 50-mi window).
- **The QC to adopt:** [`discussion/conus_grid/hail/05_plausibility_qc_rule.md`](../conus_grid/hail/05_plausibility_qc_rule.md) ("applied identically in both deployments").
- **The engine + its extension point:** [`shared/`](../../../../shared/README.md) (`run_cell_mc`'s count draw) · **the source notebooks:** [`Notebooks/hail/`](../../../../Notebooks/hail/).

## 6. Open questions (for discussion)

1. **Windowed M0:** reuse the grid's per-cell evidence (cell-quantized window) or a separate exact-circle deep
   collector? (§3a — the fidelity vs reuse trade.)
2. **Where does NegBin live?** In the engine's count step directly, or a `shared/statistics/` fitting module
   the M1 calls?
3. **Real-asset data:** what's the minimal asset contract (location, capacity, footprint, TIV, valuation
   basis) and where does it come from? (This is probably the true gating dependency.)
4. **One driver or two?** Could `conus_grid` and `deep_per_asset` be one parameterized driver (exposure =
   canonical-grid vs real-asset), or are they cleaner separate? (Off-grid == on-grid suggests the former.)
