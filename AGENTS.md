# AGENTS.md — Hazard_modeling

> ⚠️ **Early scaffold.** This repo was just created. The structure below is real; the modeling
> content is still being assembled. Sections marked _(TBD)_ are placeholders, not commitments —
> they fill in as the work lands.

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
| `docs/extra/` | Staging area for reference materials being brought into the project _(contents TBD — owner-curated)_. |
| `docs/google_drive_docs/` | Local `.docx` copies of the team's shared Google Drive **"InfraSure Hazard"** reference set (Drive is the source of truth). Index + folder links: [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md). |
| `Notebooks/` | Exploratory & analysis notebooks. |
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

---

## Key references (start here)

The shared Drive reference set, mirrored under `docs/google_drive_docs/`:

- **hazard_modeling_terminology** — vocabulary / definitions for this domain.
- **Hazard_Data_Reference** — hazard datasets and their characteristics.
- **risk_metrics_reference** — the risk metrics we report.
- **hazard_asset_loss_distribution_methodology** — methodology for asset-level loss distributions.

Accurate per-doc summaries + Drive folder links: [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md).

---

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Notebooks live in `Notebooks/`; register the kernel from `.venv` if needed.

---

## Conventions _(emerging — TBD)_

- Single source of truth for agent guidance is **this file** (`AGENTS.md`); `CLAUDE.md` just imports it.
- Mirror the house style of the sibling `model-gpr` repo where it makes sense: `docs/` layout,
  gitignored local-only symlinks, plain `venv` + `requirements.txt`.
- _(Data layout, naming, output formats — to be defined once the modeling work starts.)_

---

## Status

**Foundation phase** — scaffolding only, no modeling code yet. Reference docs land first
(`docs/google_drive_docs/`), then the methodology and implementation follow.
