# discussion/wildfire/

**Where we think out loud about wildfire — *before* we build it.** This folder is the deliberate
"discuss in detail, don't rush into M0" step the owner asked for. Nothing here is code or a plan-of-record;
it is the reasoning that *produces* the plan. Once a decision settles here, it graduates to
`docs/plans/wildfire/` (decisions `DD-*`, assumptions `A-*`) and then to the notebooks.

Wildfire is **hazard 2 of 3** (hail ✅ · **wildfire** · wind), built **solar-first, then wind**, mirroring
the hail pipeline (shared `M0`/`M1` peril catalog, then a `solar/` cell for `M2–M4`).

## Read order

| # | Doc | What it decides |
|---|---|---|
| 01 | [`01_v1_scope_and_framing.md`](01_v1_scope_and_framing.md) | **What V1 actually models** — the exogenous-vs-endogenous fire fork, the honest label, the data source, how far we go on site-conditioning, and the open decisions for the owner. |
| 02 | [`02_fsim_wrc_data_dictionary.md`](02_fsim_wrc_data_dictionary.md) | **What the source data *is*** — a verified, cited data dictionary for the FSim / WRC layers (BP, CFL, FLEP4/8, FLP1-6, WHP): definitions, units, vintages, the FIL↔FLEP relationship, and the native-FLP1-6 source. Understand-before-M0. |
| 03 | [`03_m2_site_conditioned_coupling.md`](03_m2_site_conditioned_coupling.md) | **How M2 (coupling) works** — the physics chain + x-axis ladder; why M2 is *thin* for a pre-integrated site-conditioned peril; the stale-output/currency + site-feature/distance points; the V1 contract + open decisions. Understand-before-M2. |

## Related (don't duplicate — link)

- The three coupling buckets, in depth: [`../gpt/03_coupling_types_…`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md) — wildfire is **bucket 3, site-conditioned**.
- The full M0→M4 journey: [`../gpt/05_m0_to_m4_full_modeling_journey.md`](../gpt/05_m0_to_m4_full_modeling_journey.md).
- The principles that govern every choice here: [`../../principles/`](../../principles/README.md).
- The scope-and-story anchor: [`../00_scope_and_story.md`](../00_scope_and_story.md).

## Status

🟡 **Open for discussion.** `01` is seeded from a grounded sweep of the three prior wildfire artifacts
(the legacy `_legacy_wildfire` model, the public-data `wildfire_analysis_lab`, and the kWh 2026 Solar Risk
Assessment) + the competitive-research A-series. Awaiting the owner's calls on the open decisions before
`docs/plans/wildfire/` M0/M1 planning begins.
