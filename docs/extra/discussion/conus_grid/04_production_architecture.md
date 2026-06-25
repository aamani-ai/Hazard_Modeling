# 04 — Grid Production Architecture (discussion)

*How the CONUS grid moves off notebooks/scripts into a proper, reusable **package** — the shared skeleton
every peril inherits. A discussion doc: it commits the architecture's shape and the genuine choices, modelled
on the **layered-pipeline** project-structure variant (`Learning/coding/project_structure/variants/layered-pipeline.md`),
adapted to this repo. Once reviewed, it graduates to a plan-of-record under
`docs/plans/hazard_conus_grid/architecture/`.*

> **Scope:** the **CONUS grid** (use case 2). The deep per-asset product stays in notebooks for now — but it
> is **not a separate engine**: it's a future *second driver* of the same shared engine (see "one engine, two
> drivers"). Settled *inputs* (not open here): the 0.25° grid + `cell_id`, GCP/Cloud Run (DD-G6/G7/G9), the
> per-cell output schema, the [plausibility-QC rule](hail/05_plausibility_qc_rule.md), and the damage-curve contract.

---

## Why now, and what's wrong today

The grid works and has run at full CONUS scale — but its logic lives in the wrong place for reuse: the M4
engine is **re-typed inline** in a notebook, the GCS helpers are **byte-duplicated** across scripts, each
peril's M0 is a **fresh ~800-line script**, and the "common source job with adapter config" is
[specced but unbuilt](../../../plans/hazard_conus_grid/common/gridded_radar_source_qualification.md). So
"add wildfire/tornado" today = copy hail and rebuild. The fix is
[*modular-from-day-one*](../../../principles/modularity_and_scaling.md) as real code.

## The boundary — the single most important decision

In a layered pipeline, the one architectural feature that matters most is **where peril-specific logic ends
and the shared generic engine begins**, and **what typed object crosses it**. For us that boundary is the
**per-cell hazard-distribution object** that M1 emits — and it's exactly the asset-free M0/M1-vs-M2–M4 seam
we've enforced all along, now made a versioned contract:

| Our layer | Reference layer(s) | Side |
|---|---|---|
| **M0** raw | L1 Evidence + L2 Reconstruction | peril-specific |
| **M1** catalog · frequency · severity | L3 Event Catalog + L4 Stochastic + L5 Hazard Distribution | peril-specific → **emits the boundary object** |
| — | **▶ boundary: per-cell hazard-distribution object (typed, `schema_version`) ◀** | — |
| **M2** coupling | Exposure (event × asset intersection) | shared *framework* + per-(peril×asset) coupling type |
| **M3** damage | Vulnerability (framework shared; **curves peril-specific**) | shared framework + peril curves |
| **M4** loss · metrics | Loss + Aggregation + Metrics + Outputs | shared engine |

The contract is enforced in code (`schemas/`, versioned from day one), so the boundary can't silently drift —
the failure mode the rebuild exists to kill. **Nothing bypasses it:** a peril never calls engine internals;
the engine never imports a peril.

## One engine, two drivers

The shared engine consumes a hazard distribution **+ an exposure input**. That exposure input is the only
thing that differs between our two products:

```
                         ONE shared risk engine  (M2 → M3 → M4)
                                       ▲ consumes (hazard distribution + exposure)
                ┌──────────────────────┴───────────────────────┐
        grid driver  (V1, now)                         deep-per-asset driver  (future)
        canonical asset at every served cell           one real asset, true geometry/TIV
        → the CONUS map                                → a single deal's risk
```

So we build the engine **exposure-agnostic now, with the grid as its first driver**; the deep per-asset later
is a *second driver*, not a second engine. This is the [off-grid==on-grid](01_ideal_architecture_compute_and_grid.md)
principle as code — and the reason the two products can never disagree.

## The structure — monorepo with extractable subpackages

Each pipeline and the engine is its own installable package, so if a peril (or the engine) ever earns its own
repo, extraction is **mechanical, not a refactor** — the safe form of "in-repo now" (your damage-curve repo
met the split bar; the grid is the common spine and does not).

```
Hazard_modeling/
├── src/                                  ← NEW home for grid production code (notebooks stop holding logic)
│   ├── shared/                           ← the risk ENGINE — a peer of pipelines; consumes ANY peril
│   │   ├── schemas/                      ← ★ THE CONTRACTS, versioned
│   │   │   ├── hazard_distribution.py    ←   the boundary object (M1 emits, engine consumes)
│   │   │   ├── exposure.py · risk_metrics.py …
│   │   ├── exposure/                     ← M2: coupling dispatch (areal | field-intensity | site-conditioned)
│   │   ├── vulnerability/                ← M3: curve framework  apply(size, asset) → DR  (curves live w/ peril)
│   │   ├── loss/ · aggregation/ · metrics/   ← M4: loss → AEP/OEP → EAL/VaR/PML/TVaR (USD + %TIV)
│   │   ├── statistics/ · io_base/
│   │   └── orchestration/engine.py       ←   run M2–M4 given (hazard dist + exposure + curves)
│   ├── pipelines/
│   │   └── hail/                         ← peril-specific (M0/M1), installable
│   │       ├── layers/  (l1_evidence … l5_hazard_distribution)
│   │       ├── plausibility_qc/          ←   ~200 mm cap + frequency flag (asset-free)
│   │       ├── vulnerability_curves/     ←   consumes the canonical hail×solar curve artifact
│   │       ├── io/ · validation/ · orchestration/ · config/
│   └── drivers/                          ← the CONSUMERS (one-engine-two-drivers)
│       ├── conus_grid/                   ←   canonical asset at every cell (V1) — fans out per cell
│       └── (deep_per_asset/  ← future)
├── orchestration/                        ← Cloud Run jobs · batch specs (config-driven; reuse DD-G9 fanout)
├── docs/                                 ← OUR existing system (hazards/ anchors · discussion/ · plans/ · principles/)
├── Notebooks/                            ← THIN: explore · validate · the Hayhurst bridge — all import src/
└── data/                                 ← gitignored cache
```

- **`shared/` is a peer of pipelines, not a child** — explicit dependency direction: pipelines + drivers
  import `shared`; `shared` imports no peril.
- **`io/` isolates cloud/DB** so layers are pure and unit-testable without mocking GCS.
- **`orchestration/` is separate from layers** — layers say *what*, orchestration says *how it runs*.

## The reusability move — the adapter pattern

The shared engine, drivers, orchestration, and contracts are written **once**. A new peril fills five blanks:

```
  ADD A NEW PERIL (e.g. tornado × wind):
    1. SourceAdapter      raw source → per-cell-day evidence        (M0; + a plausibility-QC hook)
    2. M1 fit             frequency + severity → hazard distribution (M1; emits the boundary object)
    3. coupling type      areal | field-intensity | site-conditioned (M2; selected, dispatched by engine)
    4. damage curve       point at a canonical curve artifact         (M3 contract)
    5. config             peril id · source URIs · thresholds · canonical asset(s)
    ──────────────────────────────────────────────────────────────────────────────
    REUSED unchanged: the M4 engine · both drivers · the Cloud Run orchestration ·
                      the contracts · GCS I/O · %-TIV reporting.
```

This is [*standard interface, not standard physics*](../../../principles/hazard_asset_specificity.md) as code:
the interface (the five blanks) is fixed; the physics (what the adapter and curve contain) is per-peril.

## Absorbing divergence — per-peril depth, and the deep per-asset

The structure's real job is to let the *variable* parts diverge while the *shared* parts stay clean. Two
kinds of divergence, both designed for:

**Per-peril process depth.** Each pipeline is a self-contained micro-project, so a peril's M0/M1 can be as
heavy or light as its science demands — and they still emit the *same* boundary object:

| Peril | M0/M1 process | Depth |
|---|---|---|
| **Hail** | raw MRMS → curation → plausibility QC (~200 mm cap + freq flag) → empirical freq + severity | **heavy** (layers earn folder promotion) |
| **Wildfire** | ingest a pre-integrated FSim field → aggregate to `cell_id` | **light** |

This is exactly the "divergence in the process" hail surfaced — it needs real curation; wildfire doesn't. It
lives *inside* the hail pipeline, behind the contract; it never leaks into the engine or another peril. That
divergence being absorbable is the structure doing its job, not a strain on it.

**The deep per-asset (future).** Same engine, a second driver — its growth lands in isolated places, never a
second engine:

| Deep-per-asset addition | Lands in | Shared with grid? |
|---|---|---|
| new DB + real-asset registry, real geometry | the per-asset **driver** | no — isolated |
| financial terms (deductibles / limits / BI), richer severity | the **shared engine** | yes — the grid gains it too |
| the M2–M4 risk math | the **shared engine** | yes — identical |

So the per-asset's *data* complexity is isolated in its driver; its *capability* additions enrich the engine
for everyone. Its physical home — same monorepo vs. its own repo — is a **deferred, reversible packaging
call** (extractable subpackages), made when we build it and know its real shape, by concrete signals
(diverging deps, release cadence, DB isolation, CI cost). **The one non-negotiable: the engine is never
duplicated.**

## Migration — phased, never breaking the working hail pipeline

Today's hail outputs + the Hayhurst bridge are the **regression oracle**: each phase must reproduce them.

```
  Phase A  Extract the ENGINE (M4 MC + metrics + coupling dispatch + GCS helpers) into shared/;
           re-wire existing hail notebooks/scripts to IMPORT it.
           ✓ gate: identical hail M2–M4 outputs + Hayhurst bridge unchanged.
  Phase B  Wrap hail M0 ingest as the first SourceAdapter (MRMS); fold in plausibility QC.
           ✓ gate: identical reconciled M0/M1 (27.1M rows, 13,085 cells).
  Phase C  Code-enforce the per-cell contracts (schemas + versioning); thin the notebooks.
  Phase D  Prove the seam: add the SECOND peril (wildfire FSim adapter) as fill-in-the-blanks.
  (Every phase ships working; the live hail pipeline never breaks.)
```

Phase D is the real test of the skeleton — if wildfire isn't mostly "fill the five blanks," the abstraction
isn't right yet.

## Decisions

| # | Choice | Decision |
|---|---|---|
| 1 | **Package location** | **In-repo** monorepo with extractable subpackages (decided — spine is common; extraction stays mechanical if ever needed). |
| 2 | **Repo split** | **No** — reserved for "a whole different process" (the damage curve); the grid is the shared spine. |
| 3 | **Adapter config** | Light registry: per-peril config (id, source URIs, thresholds, asset refs) + a code adapter. Declarative without YAML over-engineering. |
| 4 | **Contract enforcement** | **Code** (dataclass/pydantic + `schema_version`) at the seams — a break surfaces *at the layer* ([*basics spot-on*](../../../principles/basics_spot_on.md)). |
| 5 | **Tests** | Known-answer unit tests on the engine + regression vs current hail outputs + Hayhurst bridge as the cross-product oracle. |
| 6 | **Packaging / deploy** | `pyproject` packages installed into the Cloud Run image; the existing job/workflow re-points to a package entrypoint. |

## Adapted from the reference (it's a reference, not gospel)

- **Docs:** keep *our* system (the `hazards/` anchors + `discussion/`/`plans/`/`principles/`) — not the
  reference's D3 framework wholesale. We borrow its **code** conventions, not its doc taxonomy.
- **V1 layer depth:** build the L1–L5 *seams*, fill at today's depth — L4 "stochastic catalog" is light for V1
  (empirical frequency, observed severity). EVT tail / climate adjustment / record extension are deferred
  V1.5/V2 work that slots into the L4/L5 seams ([*good_enough_for_v1*](../../../principles/good_enough_for_v1.md)).

## Out of scope (so it doesn't creep)

- The deep per-asset *driver* + new database — explicitly later (but it reuses *this* engine).
- The V1.5/V2 accuracy work — leave clean seams, don't build it now.

---

## Cross-references

- The reference blueprint: `Learning/coding/project_structure/variants/layered-pipeline.md` (local vault).
- The conceptual architecture this makes real: [`01_ideal_architecture_compute_and_grid.md`](01_ideal_architecture_compute_and_grid.md).
- The adapter spec this builds out: [`gridded_radar_source_qualification.md`](../../../plans/hazard_conus_grid/common/gridded_radar_source_qualification.md).
- The output contract: [`02_per_cell_output_schema.md`](02_per_cell_output_schema.md) · [`output_schema.md`](../../../plans/hazard_conus_grid/output_schema.md).
- QC + damage plug-ins: [`hail/05_plausibility_qc_rule.md`](hail/05_plausibility_qc_rule.md).
- Reader-facing hazard view: [`../../../hazards/hail/README.md`](../../../hazards/hail/README.md).
- Code being migrated: [`../../../../scripts/`](../../../../scripts/README.md) · [`../../../../Notebooks/hazard_conus_grid/`](../../../../Notebooks/hazard_conus_grid/README.md).
