# Densifying a Sparse Return-Period Curve — Anchor a Regional *Shape*, Don't Import an Absolute Model (the Anchors Cancel the Weak Inputs)

*Flood BLE gave only the 100- and 500-yr depths; the frequent floods that drive EAL were a flat guess. We filled
them by anchoring a **regression flow-frequency shape** to the two real depths — and the result came out
**near-invariant to the regression's own poorly-known inputs**, because the anchors absorb them. The "gold-standard"
absolute method (HAND) would have been **worse** at this site, not better.*

**Status:** v1.0 · written 2026-06-17 · **Sourced from:** flood × solar, M1 (`01_catalog`) + M4 / [JD-FL-8](../plans/flood/decisions.md) · **Applies to:** any peril holding a *sparse* return-period intensity curve (a couple of tail points) that needs the frequent end filled for a trustworthy EAL.

---

## Where this came from

Flood M1 from FEMA BLE gives depth at exactly **two** return periods — 100-yr and 500-yr (plus a 10-yr *extent*,
no depth). M4's EAL is driven by the **frequent** floods (below 100-yr), so the whole average rested on a single
**assumed onset depth** (`ONSET_DEPTH_FT = 0.5 ft`). The promised hardening ([JD-FL-6/7](../plans/flood/decisions.md))
was "densify the lower RPs with StreamStats+HAND."

On building it, the literal HAND path was both **unavailable** (the USGS watershed-delineation service was 404ing;
HAND rasters are large S3 files) **and** — per the depth research itself — **least accurate exactly here** (small,
flat, low-relief Louisiana alluvial plain). What *was* reachable: the USGS **NSS** regression (flow-at-return-period)
and the two real **BLE** depths. So instead of importing an absolute depth model, we anchored a *shape*:
get `Q(T)` for T = 2…100-yr, fit a power-law rating `depth = d₁₀₀·(Q/Q₁₀₀)^p` whose exponent `p` is pinned by **both
BLE depths**, and read depth at the missing RPs (10/25/50-yr).

## Why it looked fine — the trap

The reflexive move is **"reach for the gold-standard method."** The research ranked HAND-SRC as the national
production spine, so the obvious next step reads as: get HAND running, sample real depths, done. Two things make that
plausible-but-wrong here:

1. **"Gold standard" was conflated with "most accurate *here*."** HAND-SRC is gold for **coverage** (it works at
   *every* CONUS point, including ungauged creeks). It is **not** the most accurate where a **HEC-RAS-grade BLE grid
   already exists on a flat stream** — there it's a *step down*. Reaching for the heavier method would have *lowered*
   depth quality at this site while costing far more.
2. **The cheap method's weak input looked disqualifying.** The regression needs a channel **slope** we can't measure
   well (the delineation service that computes it was down). It's tempting to conclude "garbage slope in → garbage
   depths out, so the regression route is unusable." That intuition is **wrong here** — see the lesson.

## The lesson

> **The lesson.** To fill the frequent end of a sparse RP curve, **borrow a regional *shape* and anchor it to the real
> points you already have — don't import a heavier *absolute* model.** Anchoring at two real points fixes the curve's
> *level and steepness*, so the shape-source's poorly-known *absolute* inputs **cancel** — the answer depends on the
> anchors + the relative shape, not on the weak parameter. And check *site-appropriateness* before reaching for the
> "gold standard": the most universal method is not the most accurate at every site.

The cancellation, with worked numbers. The rating exponent is solved *from the anchors*:
`p = ln(d₅₀₀/d₁₀₀) / ln(Q₅₀₀/Q₁₀₀)`. When you push the unknown slope around, every `Q(T)` scales, but `p` re-solves to
compensate — so the **depths barely move**:

| channel slope (guessed) | Q(100-yr) cfs | exponent `p` | **10-yr depth** |
|---|---|---|---|
| 3 ft/mi | 672 | 0.896 | **0.97 ft** |
| 8 ft/mi | 1060 | 0.766 | **0.97 ft** |
| 20 ft/mi | 1630 | 0.69 | **0.97 ft** |

The slope — the one input we *couldn't* pin — moves the 10-yr depth by **< 1%**. The result rests on the two BLE
anchors and the *relative* growth of `Q` with rarity (which regional regressions capture robustly), not on the basin
parameters. `[OURS]` — the references rank the *methods*; that the **anchoring cancels the regression's weak input**
is the build-time discovery.

The payoff was real and validated: the 10-yr depth went from the assumed **0.5 ft → 0.97 ft** (measurement-anchored),
EAL rose **0.13% → 0.155% TIV** (+18%), and the densified EAL landed on the independent *"assumed @1.0 ft"* cross-check
— while **PML@100/500 stayed exactly on the BLE anchors** (the tail is untouched; only the frequent end was filled).

## How to recognize it next time

- **The tell:** you hold a **2–3-point** intensity-vs-RP curve and the EAL-driving frequent end is missing or guessed.
  Before importing a whole absolute model, ask: *"is there a regional **shape** I can borrow and **anchor** to my real
  points?"* A shape + 2 anchors often beats an unanchored absolute model.
- **The site-fit check:** before reaching for the "gold-standard / most-universal" method, ask *"is it the most
  accurate **at this site**, or just the most **broadly applicable**?"* If a higher-tier local product already exists
  (BLE here), anchor to it; save the universal method for where nothing local exists.
- **The cancellation check:** if your shape-source has a weak input, **don't assume it dooms the result** — test it.
  Sweep the weak parameter; if anchoring makes the output near-invariant (as here), the input was never load-bearing.
  (Same shape as [`06`](06_collection_region_size_cancels.md): a parameter you feared was load-bearing **cancels**.)

## Caveats and limits

- **Anchoring fixes level + steepness, not curvature.** Two anchors pin a 2-parameter rating; its *shape between
  them* (we chose power-law) is still a modeling choice — sensitivity-test it, don't treat the densified points as
  measured.
- **The shape's *relative* error still rides along.** Cancellation kills the *absolute* (slope/area) error, **not**
  the regression's return-period-to-return-period uncertainty. The published ±40–60% standard error of prediction is
  **not yet** propagated — EAL is still a point estimate; the honest next step is an MC overlay → a *distributional*
  EAL (the JD-FL-8 revisit).
- **Only where anchors exist.** This works because BLE gave two real depths. At **no-BLE / ungauged** sites there is
  nothing to anchor to — *there* the universal absolute method (HAND-SRC) becomes essential, not optional. The door is
  left open in code for exactly that case.
- **Regional means region-specific.** The regression equation is **per state/region** (we used LA Coastal Plain SIR
  2024-5031); a national rollout calls a *different* equation per site. We densified the proving site (LA) only; the
  desert baseline (TX, different region, 0% frequent inundation) kept its tail-only curve.

## Cross-references

- **Decision it generalizes:** [JD-FL-8](../plans/flood/decisions.md) (regression flow-frequency + BLE-anchored
  rating, not live HAND) · builds on [JD-FL-6](../plans/flood/decisions.md) (BLE-preferred, HAND national fallback) ·
  [JD-FL-7](../plans/flood/decisions.md) (the RP-curve → annual-max MC seam this drops into).
- **Sibling learnings:** [`06`](06_collection_region_size_cancels.md) (a feared parameter **cancels** — same shape) ·
  [`09`](09_pre_integrated_vs_extracted_catalog.md) (classify the hazard layer before choosing M1 machinery) ·
  [`05`](05_damage_curve_three_coupled_choices.md) (anchoring/level choices downstream).
- **Where it shows in code:** `Notebooks/flood/m1_catalog/01_catalog.ipynb` §1b (NLDI→NSS→rating) ·
  `Notebooks/flood/solar/m4_loss_metrics/01_loss_metrics.ipynb` §2b (densified-vs-assumed EAL).
