# Hazard_modeling

**Hazard Risk Modeling** for InfraSure's risk platform — modeling catastrophic natural-hazard
events (hurricane, hail, wildfire, flood, …) and the resulting **asset damage and losses**.
Produces asset-level **loss distributions** that feed the platform's overall **Total Loss** picture.

> **Tier 2 of 3** — Performance Modeling (normal ops · [`model-gpr`](model-gpr)) ·
> **Hazard Risk Modeling** _(this repo)_ · Overall Risk Modeling (Total Loss).

> 🚧 **Early scaffold** — structure is in place; modeling content is being assembled.

## Layout

```
docs/
  README.md
  extra/                 # reference materials being brought in (TBD)
  google_drive_docs/     # local copies of the team's shared Drive reference set (+ links)
Notebooks/               # analysis / exploration
.github/workflows/       # CI (GitHub Actions)
requirements.txt
AGENTS.md / CLAUDE.md    # contributor + agent guidance
```

Plus local-only, **gitignored** cross-project symlinks: `model-gpr/`, `hazard_analysis/`,
`infrasure-hazard-competitive-research/`, `Learning/`.

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab            # notebooks live in Notebooks/
```

## References

- **Shared Google Drive — "InfraSure Hazard":** file index + folder links in
  [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md).
- **Contributor / agent guidance:** [`AGENTS.md`](AGENTS.md).

## Status

Foundation phase: reference docs first, then methodology + implementation.
