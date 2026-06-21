# M1 — catalog (hurricane) · *the peril, shared & asset-independent*

*Turn M0's raw RAFT tracks into **events as objects** — a storm-resolved per-site 3-s-gust catalog with identity.
Plan: [`docs/plans/hurricane/m1_catalog.md`](../../../docs/plans/hurricane/m1_catalog.md).*

**Magnitude metric: the 3-second peak gust (mph)** at the site, synthesized from the Holland (1980) wind field along
RAFT tracks (RAFT `vmax` knots → sustained field → ×gust-factor → 3-s gust → ×1.150779 → mph). **Surge** and **TC
rainfall** are flood's coastal `[C]` / pluvial `[F]` sub-perils, cross-linked via `event_family_id` — not catalogued
here. **M0/M1 are shared** across both assets; the catalog covers the proving pair (Everglades, Hayhurst) and the
appended flood cross-link / all-three riders (Discovery, LA3).

| Notebook | What it builds | Status |
|---|---|---|
| [`01_event_catalog`](01_event_catalog.ipynb) | RAFT tracks → **Holland (1980) wind field** → per-site peak 3-s gust; **frequency calibration** (JD-TC-8); `event_family_id` | ✅ **built** |
| [`02_tail_validation`](02_tail_validation.ipynb) | independent **tail** check vs **ASCE 7-22** + the observed record | ✅ **built** |

## What `01_event_catalog` established

- **Field-intensity built (the new step)** — the Holland radial profile turns each RAFT track into a wind field,
  sampled at each site; passes its known-answer (peak == `Vmax` at the radius of max wind).
- **🔴 Frequency calibrated honestly ([JD-TC-8](../../../docs/plans/hurricane/decisions.md))** — the M0 oversample
  fix: **λ from the observed HURDAT2 close-passage rate** (any hurricane within 100 km, same rulebook as severity —
  Everglades **0.19/yr**, Hayhurst **0**; cross-link riders Discovery **0.10/yr**, LA3 **0.08/yr**), **severity from
  RAFT physics**.
- **RAFT severity validated** at the high site — near-site intensity **median 90 kt == observed 90 kt**.
- **`event_family_id` stamped** (= RAFT storm) — the cross-link to flood's surge / TC-rain sub-perils.
- **Sensitivity levers flagged** — gust factor (1.2), Holland B (1.3), symmetric field — for M4.
- Outputs: `tc_m1_catalog.parquet` (storm×site events across the proving pair + flood riders) +
  `tc_m1_site_summary.parquet` + manifest.

## What `02_tail_validation` established (the tail flag, resolved)

- **The tail is validated, independently** — our catalog's return-period gusts match **ASCE 7-22** (a *separate*
  engineering hurricane model) within **5.5%** over 100–700 yr, with **no systematic low bias** (100-yr we're +5.5%).
  This resolves the "tail might be silently low" concern at the level that drives PML — and **corroborates the gust
  factor (1.2)** (if it were wrong, the RP gusts wouldn't land on ASCE).
- **Observed record agrees** on central intensity (RAFT median 90 kt == observed 90 kt); the deep extreme rests on a
  small observed sample (33), consistent within noise.
- **Honest remaining limit:** the 260-storm catalog resolves only to **~1,300 yr** → PML trustworthy to ~700–1,000 yr;
  deeper return periods need extrapolation or a larger RAFT subset (carried to M4).
- ASCE chosen over **STORM** for the check because STORM is a RAFT *cousin* (shared tail blind spot → false comfort).

**STORM RP-grid cross-check — status: optional follow-on, not a gap.** The independent tail check (ASCE) is done and
passed, so STORM is no longer needed for *accuracy*. Its only remaining value is a **peer-method implementation
cross-check** (does our synthetic-catalog→Holland pipeline land where the synthetic-catalog literature does). Run it
*only* if we want that implementation confidence. (The other trigger — a non-US/Caribbean site where ASCE doesn't
reach — **does not apply: this build is US-only.**)
