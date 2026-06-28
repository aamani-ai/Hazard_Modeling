# docs/guides/ — reusable how-tos

**Forward-looking guides: "here's how to do the next one."** When a piece of work hardens into a repeatable
recipe — how to extend the system, how to add a peril, how to run a pipeline — it gets a guide here so the
next person (or the next session) doesn't re-derive it.

This is deliberately a different layer from the rest of `docs/`:

| Layer | Home | Answers |
|---|---|---|
| **Guide** *(here)* | `docs/guides/` | **how do I build / extend / run this?** (reusable, forward) |
| Decisions / plan | [`docs/plans/`](../plans/) | what did we decide, and how did we migrate? (record, backward) |
| Hazard anchor | [`docs/hazards/`](../hazards/) | what is this hazard and how reliable is it? (per-hazard snapshot) |
| Reasoning | [`docs/extra/discussion/`](../extra/discussion/) | why did we choose this? (the thinking) |
| Principles / lessons | [`docs/principles/`](../principles/) · [`docs/learning_logs/`](../learning_logs/) | what do we believe / what did building teach us? |

> A guide **synthesizes and links** — it points down into the plans, contracts, and code; it never becomes a
> second copy of them. If a guide and a register disagree on a number, the register wins.

## Guides

- [**Building a Hazard × Asset CONUS Grid**](building_a_hazard_asset_grid.md) — the as-built system (one
  engine, two drivers), the shared plausibility-QC contract, the five-blank recipe for a new (peril × asset),
  and the V1 constraints. Worked example: hail × solar.
