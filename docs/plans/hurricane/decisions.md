# Hurricane pipeline — decisions log

Running record of the non-obvious design decisions for the hurricane / tropical-cyclone build, ADR-style
(context → options → decision → why → revisit trigger). Prefix `JD-TC-*` (matches flood's `JD-FL-*` lineage,
distinct from hail `DD-*`, wildfire `DD-W*`, wind `DD-WN-*`). The V1 **seed set** `JD-TC-1..7` is listed in
dependency order; later decisions (`JD-TC-8+`) added newest-first below.

---

## JD-TC-8 · Frequency calibration — **observed-anchored λ × RAFT-physics severity** (resolves the oversample)

**Date:** 2026-06-20 · **Status:** decided · **built in M1/01** · resolves [ATC-9](assumptions.md); realizes [JD-TC-3](#jd-tc-3).

**Context.** M0/01 found RAFT's raw rate is a **~71× genesis oversample** (~1000 seeds/env-year vs the real ~14/yr),
so the catalog's storm *count* near a site is not a physical frequency. But RAFT's storm *physics* (intensity,
geometry → the Holland field) is trustworthy. M1 must produce a per-site annual rate `λ` + a severity distribution.

**Options.** (a) Use RAFT's raw count / its env-years → **wrong** (oversampled, and the effective-years
normalization is ambiguous). (b) Rescale RAFT by a global oversample factor → still leans on RAFT's absolute rate.
(c) **Anchor `λ` to the OBSERVED HURDAT2 rate, take only the severity *shape* from RAFT.**

**Decision — (c).** Define the event as *"a hurricane-intensity (≥64 kt) storm center passes within 100 km of the
site"* — and **use that *same* definition on both sides** (the rulebook-consistency fix). **`λ` = observed count of
distinct HURDAT2 hurricanes *passing within 100 km* ÷ record years** — **close passages, not landfalls-only**, so a
storm brushing offshore (common at a peninsula tip like Miami) still counts (Everglades 33/173 ≈ **0.19/yr**;
Hayhurst **0**). **Severity** (the conditional distribution of peak 3-s gust at the site) = the **RAFT Holland
field** over the storms meeting that *same* definition. The MC (M4) draws `λ` events/yr, each gust sampled from the
RAFT severity.

> **Rulebook-consistency note.** An earlier cut anchored `λ` on *landfalls within 100 km* while severity used
> *center-passages within 100 km* — two different storm populations (landfalls under-count offshore brushes). Fixed
> by anchoring both on close passages (M0/02 emits the ≥64 kt track points for this). At Everglades the effect was
> small (31→33 storms) because South Florida takes so many direct hits; it matters more for sites that mostly see
> offshore passers.

**Why.** It is the only honest use of an oversampled synthetic catalog: observed data is authoritative on *how
often*, RAFT is authoritative on *how strong / where* — and the two are kept in their lanes. It sidesteps the
ambiguous "RAFT effective years" entirely. The event definition is **identical** for the observed rate and the RAFT
severity (center within 100 km at hurricane intensity), so frequency and severity compose consistently.

**Validation (M1/01).** RAFT anchor-storms' near-site intensity **median 90 kt == observed 90 kt** (p90 116 vs
123 kt) — RAFT severity matches reality at the high site. λ reproduces the observed rate by construction.

**Tail validation (M1/02).** The decision-relevant *tail* was checked against **two independent opinions** (not
STORM — a RAFT cousin with the same blind spot): our return-period gusts match **ASCE 7-22** (a separate engineering
hurricane model) within **5.5%** over 100–700 yr with **no systematic low bias**, and the observed record agrees on
central intensity. This **resolves the "tail might be silently low" flag** and **corroborates the gust factor (1.2)**.
*Remaining honest limit:* the 260-storm catalog resolves only to **~1,300 yr** → PML trustworthy to ~700–1,000 yr;
deeper RPs need extrapolation or a larger RAFT subset (carried to M4).

**Honest caveats.** (1) Observed per-site counts are **small samples** (31 at Everglades; **0 at Hayhurst** → λ=0 →
the true-zero control gets exactly zero loss, no regional floor applied — defensible for a desert site, flagged).
(2) The 100 km anchor radius is a choice (matches the M0 screen). (3) Gust factor + Holland B remain severity
levers ([ATC-6/7](assumptions.md)).

**Revisit trigger.** A site with too few observed landfalls to anchor → a regional regression rate (à la flood's
NSS); the STORM RP-grid cross-check (deferred) disagreeing with the catalog RP → revisit B / the anchor.

---

> **Status: scope, asset/order, catalog method, and the cross-link hooks decided (seed).** V1 = **hurricane wind →
> solar**, on a **shared storm-resolved RAFT TC catalog** (Holland field, validated vs IBTrACS/HURDAT2), with the
> `event_family_id` hook reserved for the deferred flood coastal `[C]` + pluvial TC slice. The genuinely load-bearing
> call was the **catalog method** ([JD-TC-3](#jd-tc-3)) — driven by the goal of *founding* coastal flood, not just a
> fast wind number.

---

## JD-TC-1 · Asset & order — **solar V1, wind farm V2** (order, not exclusion; the catalog is shared either way)

**Date:** 2026-06-19 · **Status:** decided (seed) · Mirrors flood's solar-V1→wind-V2 order.

**Context.** Both solar and wind farm are eventual hurricane cells (peril × asset matrix). Which first? The asset
choice affects only **M2–M4**; **M0/M1 (the catalog) is the peril — asset-independent and shared**.

**Options.** (a) Solar first (coherence + fast number; degenerate field coupling). (b) Wind farm first (proves
field-intensity immediately; defers coherence). (c) Both at once (scope blow-up).

**Decision — (a) solar first, wind farm V2.** Build M0/M1 (the RAFT field catalog) once; apply it to **solar** in V1
(spatially degenerate M2 — see [JD-TC-2](#jd-tc-2)); the **wind-farm V2** cell then exercises the full per-turbine
field-intensity, reusing the same M1 field **plus** convective wind's 3-s-gust turbine curve
([DD-WN-16](../convective_wind/decisions.md)) and turbine geometry (Traverse / Shepherds Flat).

**Why.** The field machinery lives in M1 (shared) — solar-first wastes none of it; it only defers *stressing* the
spatial coupling to V2, where the expensive groundwork is already paid for. Solar buys **cross-peril coherence**
(hail + wildfire + flood + hurricane on the *same* asset) and the fastest real number; it matches flood's order so
the build stays coherent across perils. The owner's stated lean is solar; the field-intensity "weaker proof"
concern is dissolved because both cells get built.

**Revisit trigger.** If the wind-farm cell is needed sooner (e.g. an offshore-wind ask), reorder — M0/M1 is unaffected.

---

## JD-TC-2 · Coupling honesty — **field-intensity, spatially degenerate on solar V1**; full proof deferred to wind-farm V2

**Date:** 2026-06-19 · **Status:** decided (seed) · The honest label behind [JD-TC-1](#jd-tc-1).

**Context.** Hurricane is the repo's first **field-intensity** primary (the third coupling bucket). Field-intensity =
*sample a continuous field at the asset.* On a wind-farm point cloud the field varies per turbine; on a ~1 km solar
polygon, at storm scale, it is ~uniform.

**Decision.** Build the field-intensity coupling in M2, but **label V1's solar coupling as spatially degenerate** —
the field is sampled at ≈ the centroid (one value), operationally like the site-conditioned perils already built.
**V1 does NOT claim to have proven field-intensity**; the per-point proof is the wind-farm V2 cell.

**Why.** *basics-spot-on* applied to a coupling claim: a correct loss number on a mislabeled coupling is a
credibility failure (the rebuild exists to escape exactly that). The field itself (M1) is fully built and
validated; only the spatial *sampling* is degenerate on solar — say so, don't oversell.

**Revisit trigger.** Wind-farm V2 built → field-intensity exercised per turbine → the claim upgrades there.

---

## JD-TC-3 · Catalog method — **storm-resolved RAFT tracks → Holland field** (NOT the pre-integrated STORM RP grid)

**Date:** 2026-06-19 · **Status:** decided (seed) · **The load-bearing call.** Generalizes
[learning_logs/09 (pre-integrated vs extracted)](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md).

**Context.** M1 needs a TC frequency/severity basis. Two routes: **(a) pre-integrated** — sample the STORM 10 km
**wind-RP GeoTIFFs** (a wind *surface*; fast; the FSim/ASCE/BLE house pattern); **(b) storm-resolved** — **RAFT
tracks → Holland wind field** (storm *objects*; heavier). The house precedent favors pre-integrated. **But** the
*reason hurricane is built before coastal flood* is to **found coastal flood**, and that reframes the choice.

**Decision — (b), and specifically RAFT.** Build M1 as a **storm-resolved RAFT track catalog → Holland field**.
STORM RP grids + IBTrACS/HURDAT2 become **validation cross-checks**, not the spine.

**Why.** A pre-integrated RP grid has **no storm objects** — it cannot feed coastal flood's `event_family_id` link
or a landfall-by-intensity frequency (what category-SLOSH surge needs). Only a storm-resolved catalog transfers.
And **RAFT specifically** (North Atlantic; tracks + along-track intensity + **rainfall** in one product, CC-BY)
means a **single catalog serves hurricane wind, coastal surge, AND the pluvial TC-rain slice** with shared storm
identity — built once, reused across perils ([JD-TC-6](#jd-tc-6)). STORM's only edge was the RP grid, the exact
part that doesn't transfer. The cost — building/validating the Holland field instead of reading a grid — is accepted
in exchange for the foundation.

**Honest caveats.** (1) Slower to a V1 wind number than reading a grid. (2) Holland parameterization (B, RMW,
asymmetry, gust factor) is authored — assumptions, validated vs landfall winds. (3) RAFT is synthetic
(R²≈0.73 landfall winds vs obs) — validate, don't assume. (4) RAFT = North Atlantic only (fine: V1 sites are US
Atlantic/Gulf). (5) RAFT DOI must be re-confirmed at build (repository versioning — Hazard Data Reference §8).

**Revisit trigger.** A free per-event probabilistic *surge* product (FFRD/ADCIRC opens) → revisit whether RAFT or
that product anchors the shared event set; a global (non-Atlantic) site → STORM tracks for that basin.

---

## JD-TC-4 · Scope — **wind only**; surge = flood `[C]`, rain = flood `[F]`, cross-linked via reserved `event_family_id`

**Date:** 2026-06-19 · **Status:** decided (seed) · Reference-aligned (Hazard Data Reference §1, §8); mirrors
[flood JD-FL-1](../flood/decisions.md).

**Context.** A hurricane drives wind + surge + rain. Surge and rain are the **same physics** as flood's coastal
`[C]` (SLOSH/ADCIRC) and pluvial `[F]` (Atlas 14). Do we model them here, or reference them?

**Decision.** **Wind only** in hurricane (the primary peril it owns). Surge and rain are **flood's** sub-perils,
**not** hurricane's — not catalogued or modeled in V1. M1 **reserves `event_family_id`** (unused in V1) so a future
flood coastal/pluvial event can point back to its parent storm. Also out of scope: the wind *resource*
([DD-WN-2](../convective_wind/decisions.md)), business interruption, climate non-stationarity (flagged).

**Why.** Tagging surge/rain as hurricane sub-perils would create **two surge models** (hurricane's + flood's
coastal) → duplication, drift, and the **double-count** the old model demonstrates (separate `Hurricane` +
`Coastal Flood` rows, summed). One owner (flood), one model, one storm identity shared by reference is the honest,
*modular-from-day-one* architecture. Per-event surge needs ADCIRC (outside the free stack) anyway, so building
surge "now" would also force the category-only SLOSH compromise prematurely.

**Revisit trigger.** Flood's coastal `[C]` is built → switch the `event_family_id` link on (no hurricane refactor).

---

## JD-TC-5 · Sites — **a screened Gulf/Atlantic-coast solar high site + Hayhurst (reused) baseline**

**Date:** 2026-06-19 · **Status:** proposed (seed) · Mirrors [flood JD-FL-3](../flood/decisions.md) on the solar asset.

**Context.** The low-vs-high contrast every cell uses. The high site must have **material TC wind** *and* (for the
future surge cross-link) be **coastal**, where surge can reach.

**Decision.** **Low/baseline = reuse Hayhurst Texas Solar** (Culberson Co. TX, desert — near-zero TC, the same
asset hail/wildfire/flood used → cross-peril coherence). **High/proving = screen for a Gulf/Atlantic-coast solar
farm** (real footprint + reachable geometry + high landfall exposure) — confirmed in M0. TIV from $/MW (Hayhurst
basis), coastal site estimated by capacity; % of TIV alongside $.

**Why.** Reusing Hayhurst preserves coherence and is a legitimate near-zero control. A coastal high site is the
natural proving ground for the field *and* the eventual surge link.

**Revisit trigger.** Top screened coastal asset lacks geometry/exposure → next candidate; an offshore-wind ask →
the high site may move to the wind-farm V2 cell.

---

## JD-TC-6 · Cross-peril consequence — **flood's pluvial becomes an Atlas-14 + RAFT hybrid** (RAFT enters the system once)

**Date:** 2026-06-19 · **Status:** recorded (not built in V1) · Consequence of [JD-TC-3](#jd-tc-3); concerns the
flood pipeline.

**Context.** Flood's pluvial `[F]` is **RP-based** (NOAA Atlas 14 → SCS-CN → ponding; [JD-FL-9](../flood/decisions.md))
— **not storm-resolved**, so a hurricane's rain cannot be linked to it. Compound TC flooding (one storm's wind +
surge + rain, no double-count) needs a storm-resolved TC-rain source.

**Decision (recorded for the future build).** When compound flooding is built, flood's pluvial becomes a **hybrid**:
**Atlas 14 (all-cause / non-TC baseline) + RAFT (the storm-resolved TC-rain slice)**, reconciled so TC rain isn't
double-counted between the two. Critically, that RAFT slice draws the **same RAFT catalog** hurricane M1 builds —
so RAFT enters the system **once**, owned by the TC catalog layer, consumed by hurricane wind, coastal surge, and
pluvial-TC.

**Why.** If hurricane used STORM and pluvial later added RAFT independently, there would be **two disconnected storm
universes** → `event_family_id` would have nothing to match → the no-double-count goal fails. One shared RAFT
catalog is the only architecture where the cross-link works. RAFT covers only TCs (North Atlantic), so it
*augments* Atlas 14 (which covers all-cause, all-CONUS rain), it does **not** replace it.

**Revisit trigger.** Compound flooding scheduled → spec the Atlas-14↔RAFT reconciliation; record as a `JD-FL-*`
decision on the flood side at that time.

---

## JD-TC-7 · Footprint method — **Holland (1980) field from tracks, validated vs IBTrACS/HURDAT2; STORM RP grid cross-check**

**Date:** 2026-06-19 · **Status:** decided (seed) · Realizes [JD-TC-3](#jd-tc-3)'s field-build; Hazard Data Reference §5/§6/§7.

**Context.** A RAFT track is not yet a hazard at the asset — it must become a continuous wind field. The reference's
practical stack: *track → Holland parametric wind field → rasterize peak wind → validate vs observed landfall winds.*

**Decision.** Use the **Holland (1980) radial wind profile** (open implementations, e.g. CLIMADA) to turn each
track into a continuous gust field, swept along-track with **asymmetry** (forward motion + inflow) and a **gust
factor** (sustained → 3-s). **Validate** by replaying historical landfalls (IBTrACS/HURDAT2 best tracks) and
checking modeled vs observed landfall gusts; **cross-check** catalog RP winds vs the STORM 10 km RP GeoTIFF.

**Why.** It is the standard, open, public method, and the only one that produces a *per-event* continuous field
(what field-intensity and the future surge correlation need). Validation against observed winds keeps it
hazard-first.

**Honest caveats.** Holland **B**, **RMW**, asymmetry, and the gust factor are parameterized (assumptions,
sensitivity-tested). STORM's empirical-Weibull RP **runs low past ~100-yr** vs EVD (§7) — document the convention
when cross-checking. RAFT is **knots** → mph **×1.150779** on ingest (ATC-8; not m/s ×2.237).

**Revisit trigger.** A higher-fidelity open wind-field model (or RAFT shipping a ready gust field) → swap the field
step, keep the catalog.

---

## JD-TC-9 · Unified catalog & wind screen — **wind = 100 km, surge = 50 km; the wind-farm reads its own 100 km catalog** (un-fork)

**Date:** 2026-06-24 · **Status:** decided · **built** (M0/M1 + wind M2/M4 + solar M2/M4 + flood-coastal × wind M4) · corrects [JD-FL-19](../flood/decisions.md); the screen radius realizes [JD-TC-8](#jd-tc-8).

**Problem.** The wind-farm cell was forked off flood-coastal's M1 catalog ([JD-FL-19](../flood/decisions.md)) so the
wind & surge legs would share one event frame. But that catalog is screened at the **50 km surge radius**, so the
wind hazard was being counted with the surge ruler: only 2 observed passages → λ = 0.0116/yr, and a 24-storm severity
pool. Solar, by contrast, built its own catalog at 100 km and was already correct. The radius is a property of the
**hazard, not the asset** — wind reaches ~100 km; surge attenuates by ~50 km.

**Decision.**
1. **One unified hurricane M1 catalog with all sites**, every site screened at the **100 km wind radius**. Amazon
   (the wind farm) is added to `tc_m0_sites.json` with `asset: "wind_farm"`; M1 carries `asset` (+ `category`,
   `near_site_vmax_kt`) so the asset forks at M2 (the M0/M1-shared principle).
2. **Wind farm reads its own 100 km catalog** (`tc_m1_catalog.parquet`, `asset==wind_farm`) instead of borrowing
   flood-coastal's 50 km file. Result: λ **0.0116 → 0.0751/yr** (13 obs, ±28% vs the old ±71%), severity pool
   **24 → 95 storms** (Cat-3 count 1 → 5), wind **EAL 0.012% → 0.067%**, **PML500 1.43% → 5.70%** of TIV.
3. **Solar M2/M4 gain an `asset=="solar"` filter** so the wind-farm site can't leak into the solar pipeline
   (verified: solar outputs byte-identical).
4. **Surge stays at 50 km.** The flood-coastal surge leg keeps its ≤50 km rate ([JD-FL-21](../flood/decisions.md)).
   The two legs join on `event_family_id` (= RAFT storm_ID); the 50 km surge storms are a strict **subset** of the
   100 km wind storms, so the join is still clean. The flood-coastal × wind **coastal compound restricts its wind
   leg to the 50 km surge event set** (so the surge-driven compound is unchanged — still 24 storms — and the
   50–100 km wind-only storms are carried by the standalone wind product, not the surge compound).

**Tier-3 caveat (forward-looking, no code yet).** The standalone hurricane-wind product (100 km, all 95 storms) and
the flood coastal compound (which already contains the 24 close storms' wind via `max(wind, surge)`) **overlap on
those 24 storms' wind**. Nothing in this repo combines the two, so there is **no double-count today**. But when the
**Overall Risk Modeling** tier merges them into Total Loss, it must combine **worse-wins (max), not sum**, for the
overlapping storms — otherwise their wind is counted twice. Record kept so that combiner is built correctly.

**Why.** Same structure for both assets, driven by the hazard. Removing the fork makes each pipeline independent and
correct (wind at its own radius), while the shared `event_family_id` preserves the compound join — the fork was a
convenience, never a requirement.

**Revisit trigger.** A native standalone-wind site screen that differs from 100 km, or a hurricane-specific turbine
curve (would also lift the 0.65 DR cap).
