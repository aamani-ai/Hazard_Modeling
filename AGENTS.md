# AGENTS.md — Hazard_modeling

> **Status — building, notebooks-first.** All **three** hazards' first **(peril × asset)** cells are
> **built end-to-end in notebooks**, M0→M4 (raw data → catalog → coupling → damage → annual loss & risk
> metrics), with real (record-limited) numbers: **hail × solar ✅ · wildfire × solar ✅ · convective-wind ×
> wind-farm ✅** (Hazard **3 of 3** — convective wind = two sub-perils, tornado + strong wind, combined).
> **Next:** a production folder architecture. Start at [`Notebooks/README.md`](Notebooks/README.md) — the
> peril × asset map.

**Hazard_modeling** is the **Hazard Risk Modeling** engine of InfraSure's risk platform — the tier
that models **catastrophic natural-hazard events and the resulting asset damage / losses** (e.g.
hurricane, hail, wildfire, flood). It turns hazard exposure + asset characteristics into
**asset-level loss distributions** that feed the platform's overall risk picture.

It is **one of three tiers** of the platform:

1. **Performance Modeling** — normal operations & weather variability → probabilistic
   generation/revenue forecasts (P50/P90/P99). *Sibling repo:* [`model-gpr`](model-gpr) (symlinked).
2. **Hazard Risk Modeling** ← *this repo* — catastrophic events + damage → asset loss distributions.
3. **Overall Risk Modeling** — combines all loss sources (performance shortfall + hazard losses)
   into **Total Loss**.

**Scope:** low-frequency / high-severity hazard events and their damage-to-loss translation.
**Not in scope:** normal weather variability and routine generation forecasting — that's the
Performance tier (`model-gpr`).

---

## Repo map

| Path | What |
|---|---|
| `docs/` | Project documentation. Index: [`docs/README.md`](docs/README.md). |
| `docs/extra/` | Scope-and-story anchor + per-session [`tasks_history/`](docs/extra/tasks_history/) handoffs (session→session context). |
| `docs/google_drive_docs/` | Local `.docx` copies of the team's shared Google Drive **"InfraSure Hazard"** reference set (Drive is the source of truth). Index + folder links: [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md). |
| `docs/plans/` | Planning docs / plan-of-record (mirrors `model-gpr`'s `docs/plans/`). |
| `docs/principles/` | **The foundational beliefs** — why we build this way ([index](docs/principles/README.md)). |
| `docs/learning_logs/` | **What building taught us** — derived knowledge not in the references ([index](docs/learning_logs/README.md)). |
| `Notebooks/` | The worked pipelines, organized **`peril → asset`** (e.g. `hail/` = shared catalog M0/M1; `hail/solar/` = M2–M4). Index: [`Notebooks/README.md`](Notebooks/README.md). |
| `data/` | Pipeline outputs per peril (`data/<peril>/`); large parquets + raw cache gitignored, manifests/summaries kept. |
| `scripts/` | One-off / utility scripts (e.g. the resumable MRMS record scan) — explicitly not production code ([README](scripts/README.md)). |
| `.venv/` | Local Python environment (gitignored). |
| `.github/workflows/` | CI (GitHub Actions) — starter `ci.yml`, also runnable locally with `act`. |

### Cross-project reference symlinks (gitignored, local-only)

These point at machine-specific absolute paths and **must not be committed**:

| Link | → Points at | Why it's here |
|---|---|---|
| [`model-gpr`](model-gpr) | sibling Performance Modeling repo | how this team structures a modeling repo; the Performance tier this one sits beside |
| [`hazard_analysis`](hazard_analysis) | sibling repo | hazard-domain reference _(role TBD — owner to detail)_ |
| [`infrasure-hazard-competitive-research`](infrasure-hazard-competitive-research) | sibling repo | competitive / market research on hazard modeling _(role TBD)_ |
| [`Learning`](Learning) | `~/Desktop/Learning` knowledge base | domain notes (risk, insurance, modeling, electricity markets) |
| [`infrasure-damage-curves`](infrasure-damage-curves) | sibling repo (`Divi-patel/infrasure-damage-curves`) | the **damage-curve library** — peril × asset/subsystem/component fragility curves; the source for **M3 severity** (replaces the literature-curated curve) |

---

## Key references (start here)

The shared Drive reference set, mirrored under `docs/google_drive_docs/`:

- **hazard_modeling_terminology** — vocabulary / definitions for this domain.
- **Hazard_Data_Reference** — hazard datasets and their characteristics.
- **risk_metrics_reference** — the risk metrics we report.
- **hazard_asset_loss_distribution_methodology** — methodology for asset-level loss distributions.

Accurate per-doc summaries + Drive folder links: [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md).

**Method provenance** — where each method comes from (external citations + the research-repo A-series),
mapped per pipeline layer: [`docs/references/`](docs/references/README.md).

---

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Notebooks live in `Notebooks/`; register the kernel from `.venv` if needed.

---

## Conventions

- Single source of truth for agent guidance is **this file** (`AGENTS.md`); `CLAUDE.md` just imports it.
- Mirror the house style of the sibling `model-gpr` repo where it makes sense: `docs/` layout,
  gitignored local-only symlinks, plain `venv` + `requirements.txt`.
- **The three principles** ([`docs/principles/`](docs/principles/README.md)) govern design decisions: *standard interface, not standard physics* · *modular from day one* · *basics spot-on*.
- **Layout:** notebooks organized `peril → asset` (M0/M1 = shared peril catalog · M2–M4 = per-asset);
  outputs under `data/<peril>/`; a README per layer/folder.
- **Tracking:** assumptions in [`docs/plans/hail/assumptions.md`](docs/plans/hail/assumptions.md),
  decisions in [`decisions.md`](docs/plans/hail/decisions.md) (DD-*), derived lessons in
  [`docs/learning_logs/`](docs/learning_logs/README.md). Risk metrics shown as **% of TIV** alongside dollars.

---

## Status

**Hazard 3 of 3 — all three first cells built end-to-end** in notebooks (M0→M4: catalog → coupling →
damage → loss & metrics; real but record-limited numbers, math-validated): **hail × solar**, **wildfire ×
solar**, and **convective-wind × wind-farm** (two sub-perils — tornado + strong wind — co-sampled into one
loss distribution; M2 folder-forked, M3 one turbine / two curves, M4 combined). **Next:** a production
folder architecture (not before). Latest session context: the newest handoff in
[`docs/extra/tasks_history/`](docs/extra/tasks_history/).
