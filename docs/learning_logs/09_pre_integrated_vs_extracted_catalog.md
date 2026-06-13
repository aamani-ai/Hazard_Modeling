# When the Simulator Pre-Integrates the Event Set, M1 Becomes Profile-Assembly — Not Event-Extraction

*Hail's M1 extracts discrete events from raw radar and fits a rate; wildfire's M1 does neither — FSim already
Monte-Carlo'd the seasons into a per-site burn probability + conditional-severity histogram. **Which kind of
hazard data you hold decides the entire M1 — and where λ comes from.***

**Status:** v1.0 · written 2026-06-13 · **Sourced from:** wildfire × solar, M1 (`01_catalog`) /
[DD-W7](../plans/wildfire/decisions.md) · **Applies to:** every peril at M1 — classify *pre-integrated* vs
*raw evidence* before reaching for catalog/frequency machinery.

---

## Where this came from

Building wildfire M1, we reached for hail's M1 shape — *extract events, fit `λ_collection` (NegBin,
dispersion), thin by a spatial factor* — and none of it fit. FSim hands you **BP** (annual burn probability)
and the **FLP histogram** (conditional flame-length) per pixel: it has *already run ≥20,000 fire seasons*. So
M1 had **nothing to extract and no rate to fit**.

## Why it looked fine — the trap

We'd just built hail M1, so the mental template was loaded and recently rewarded: *"M1 = turn raw evidence
into an event catalog + fit a frequency."* Applied to wildfire it would have us (a) **invent** a discrete
"fire event" set from a probability grid (there isn't one), (b) **"fit" a λ** from a record (there's no count
series — BP is a single number), and (c) reach for **`λ_collection × spatial_factor`** (the areal-thinning
frame). All three are category errors for a pre-integrated, site-conditioned hazard — and each *looks* right
because it's exactly what worked one peril ago.

## The lesson

> **The lesson.** Classify the hazard by **how its data arrives** before choosing M1's machinery. If an
> upstream simulator has **pre-integrated** the stochastic event set into an *annualized probability +
> conditional-severity field* (FSim BP+FLP; flood depth-return grids), **M1 is profile-assembly** — read the
> per-site rate **directly**, declare the process, done: no extraction, no rate-fit, no spatial factor. If you
> hold **raw evidence** (radar swaths, point reports), **M1 is event-extraction + a fitted λ** (hail's path).
> The frequency comes from a *different place* in each.

`[REF]` The methodology says it for the site-conditioned family: the rate comes *"from the site intensity
process directly,"* no spatial factor; and the Hazard Data Reference says wildfire *"outputs the footprint
statistics directly — no track→swath step."* `[OURS]` The operational consequence is the value-add: this
**flips M1 from extraction to assembly**, **kills the short-record λ-fit and the dispersion test** (the
dispersion is *inside* the simulator's BP — you can't even test it, so `fano` is **structural, not
measured**), and **forbids the areal `λ_collection·p` frame**.

**Worked.** Hail fit `λ_collection ≈ 29.6/yr` from a 5.65-yr MRMS record (NegBin `φ ≈ 3.4`) — a genuine
estimation problem. Wildfire: `λ = −ln(1−BP)`, BP read straight from FSim (Matrix 0.044/yr, Hayhurst
0.0004/yr) — **no record, no fit, no dispersion to estimate.**

## How to recognize it next time

The tell: **you're about to "fit a frequency from a record" — pause and ask what the hazard layer actually
*is*.** If it's an **annualized probability** (BP) or an **annual-max / return-period intensity** field, a
simulator already pre-integrated the seasons → re-fitting is double-counting (or inventing a catalog that
doesn't exist). If it's **raw counts/observations** (reports, radar passes) → you *do* build + fit. The
one-question test: *"does my source give me a probability / return-period, or a count / observation series?"*

## Caveats and limits

- **Pre-integration is a borrow, not a free lunch.** You inherit the simulator's assumptions, **vintage**,
  **resolution**, and **dispersion** — and you *can't test them* (the M0 270 m / end-2020-fuel caveats; `fano`
  structural). Spot-on basics here = being honest the uncertainty moved upstream, not that it vanished.
- **Keep frequency × severity *coupled*.** When the source gives BP and FLP jointly per cell, never average
  them separately (the legacy covariance error) — pre-integration is *per cell*, so aggregate the **joint**,
  not the marginals.
- **The line isn't exactly "site-conditioned vs areal."** It's **"pre-integrated stochastic set vs raw
  evidence."** They often align (FSim = site-conditioned + pre-integrated; hail = areal + raw), but a
  site-conditioned peril where *you* build the depth grid is still extraction-ish. **Classify by the data, not
  the coupling.**
- **Portfolio breaks the single-site simplicity:** correlated BP across nearby assets reintroduces a
  dispersion/correlation term ([DD-W7](../plans/wildfire/decisions.md) revisit).

## Cross-references

- **Decision it generalizes:** [DD-W7](../plans/wildfire/decisions.md) (Poisson `λ=−ln(1−BP)`, `fano=1`, no
  fit) · [DD-W2](../plans/wildfire/decisions.md) (site-conditioned coupling).
- **Reference it builds on:** methodology §4–5/§9 (site-conditioned rate, no spatial factor); Hazard-Data-Ref
  wildfire (*"no track→swath step"*).
- **Siblings:** [`02`](02_count_distribution_and_dispersion_prior.md) (count dispersion — the *hail* path this
  contrasts with) · [`04`](04_two_datasets_one_peril_decompose.md) (two datasets, one peril) ·
  [`07`](07_one_simulation_two_products.md) (one simulation, two products).
- **Where it shows in code:** `Notebooks/wildfire/m1_catalog/01_catalog.ipynb` §1.
