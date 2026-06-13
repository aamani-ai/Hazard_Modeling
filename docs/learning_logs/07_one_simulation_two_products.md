# One Simulation, Two Products — Not Interchangeable, and Validate the Paid Wrapper Before You Pay

*USFS WRC and FSim are built from the **same** fire simulation, yet their intensity layers **disagree** (and
the disagreement flips sign by fire regime); meanwhile a paid API that "adds value" turned out to be a thin
wrapper over the **same free public data**. Two traps, one M0.*

**Status:** v1.0 · written 2026-06-13 · **Sourced from:** wildfire × solar, M0 (`01_wrc_geoplatform`,
`02_fsim_rds`, `02b_fsim_via_hydronos`) — the cross-candidate comparison / [DD-W3](../plans/wildfire/decisions.md) ·
[DD-W4](../plans/wildfire/decisions.md) · **Applies to:** any peril with ≥2 products of one model, or a paid
hazard API offered over public data.

---

## Where this came from

Wildfire M0 had two public candidates for the *same* hazard: **WRC 2.0** (collapsed `CFL/FLEP4/FLEP8`, 30 m,
WildEST/FlamMap intensity) and **native FSim** (the full `FLP1-6` histogram, 270 m). Both descend from the
same FSim burn simulation. We compared them at the asset footprint (`02_fsim_rds` §9), then cross-checked
*both* against the legacy paid **Hydronos "Wildfire Risk API"** (`02b`).

## Why it looked fine — the two traps

1. **"Same family ⇒ interchangeable."** Both are "FSim products," so it's tempting to mix them — e.g. read the
   convenient 30 m WRC `FLEP4` *and* the 270 m FSim `FLP` histogram and treat them as one consistent severity
   source (or reconstruct the missing one from the other).
2. **"The paid API must add something."** The legacy paid for Hydronos; the natural assumption is that a
   commercial endpoint gives data you can't get free. Both assumptions are plausible — and both are wrong.

## The lesson

> **The lesson.** Products derived from one simulation can still **disagree** where it matters (different
> *edition / fire-behaviour model / vintage / resolution*) — so pick **one** for a given quantity and **never
> splice editions**. And before paying for a hosted hazard API, **probe whether it is just a wrapper over
> public rasters** — it very often is.

**The divergence, worked.** Footprint-mean `FLEP4 = P(flame > 4 ft | fire)`, FSim (270 m) vs WRC (30 m):

```
                 FSim FLP→FLEP4    WRC FLEP4
 Hayhurst (TX)        0.10            0.21      ← FSim LOWER  (desert grass)
 Matrix   (ID)        0.66            0.38      ← FSim HIGHER (sagebrush)
```

`[OURS]` The gap **flips sign by regime** — FSim reads *less* intense than WRC in low-fire desert and *more*
in high-fire sagebrush. That's not noise: WRC 2.0 replaced FSim's flame-length results with **WildEST**
(circa-2023 fuels) while the FSim histogram is the 3rd-Edition (2020) product — a different fire-behaviour
model *and* vintage. **BP, by contrast, agreed** (0.0004 vs 0.0005; 0.043 vs 0.045) — because BP is the
shared frequency layer; only the *derived intensity* product diverges. So the splice is unsafe **exactly on
the severity axis that drives M3**.

`[REF]` The data dictionary already flagged "WRC v2 switched intensity to WildEST — not mixable with FSim
FLPs." `[OURS]` What building added: the divergence is **regime-dependent (sign-flipping)**, it is confined
to the intensity layer (BP is fine), and it is **material** (≈2× at the footprint) — enough to pick the
native histogram (DD-W4) and forbid splicing, not just note it.

**The wrapper, validated.** `02b` queried Hydronos for both assets and it **reproduced both public products**
to ~2–3 dp (Matrix 270 m `FLEP4` 0.654 vs our 0.662; 30 m 0.387 vs 0.382). `[OURS]` So the paid API is the
*same public USFS data aggregated server-side* — it buys query-convenience, not unique data. Going public
(DD-W3) lost nothing and gained auditability, no secret, no cost.

## How to recognize it next time

- **≥2 products of one model?** Compare them at **matched cells/footprints before trusting either** — and
  check *which layer* diverges. A shared upstream (here BP) does **not** guarantee the *derived* layers agree.
- **The splice tell:** you're about to combine a number from product A with a number from product B "because
  they're both FSim." Stop — confirm same edition/model/vintage/resolution, or pick one.
- **The paid-API tell:** before paying, send one geometry to the API *and* sample the public raster at the
  same place. If they match, you're paying for a wrapper.

## Caveats and limits

- **The frequency layer agreed** — this lesson is about *derived/secondary* products (intensity), not every
  layer. Don't over-generalize to "all products of one model disagree."
- **"Not interchangeable" ≠ "one is wrong."** Both WRC and FSim are defensible; they answer with different
  models/vintages. The rule is *consistency* (don't mix), not *correctness*.
- Deltas vs Hydronos also include footprint/grid-aggregation (it clips to its own cells); that's why "≈ to
  2–3 dp," not bit-identical.

## Cross-references

- **Decisions it validates:** [`DD-W4`](../plans/wildfire/decisions.md) (FSim FLP1-6 = severity spine, no
  reconstruction) · [`DD-W3`](../plans/wildfire/decisions.md) (public rasters, no Hydronos — now empirically
  validated).
- **Reference it builds on:** [`discussion/wildfire/02`](../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)
  (the two product lines; the WildEST switch).
- **Where it shows in code:** `Notebooks/wildfire/m0_input_data/02_fsim_rds.ipynb` §9 · `02b_fsim_via_hydronos.ipynb`.
- **Sibling:** [`learning_logs/04`](04_two_datasets_one_peril_decompose.md) (two datasets, one peril) — there
  the two sources were *complementary*; here they're two *renderings of one model* that must not be spliced.
