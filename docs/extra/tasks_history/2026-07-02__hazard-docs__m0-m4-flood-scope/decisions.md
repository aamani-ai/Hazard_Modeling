# Decisions — hazard docs M0-M4 + flood scope handoff (2026-07-02)

## 1. Keep Source Selection Separate From Modeling Choices
**Decision:** Hazard folders should keep `source_selection.md` focused on data-source choice and provenance, while
`modeling_choices.md` carries modeling assumptions, distributions, coupling choices, combine rules, and open questions.

**Rationale:**
- Source selection answers "what evidence do we trust and why?"
- Modeling choices answer "how do we turn that evidence into M0-M4 numbers?"
- Keeping them separate makes pressure testing easier: a source can be right while the modeling bridge remains weak, or
  vice versa.

## 2. Document M0/M1 Input Modes Explicitly
**Decision:** The M0-M4 contract should name the three common M0/M1 modes: event-first, return-period/surface-first, and
hybrid.

**Rationale:**
- Event-first approaches are flexible and preserve per-event structure, but require heavier QC, deduplication, footprint
  treatment, and sometimes EVT or other add-ons.
- Return-period/surface-first approaches are often cleaner and more authoritative for a site metric, but require
  assumptions when converting a return-period curve into event frequency/severity or missing depth points.
- Hybrid approaches are common in practice, especially when official grids give strong anchors but not a full event set.

## 3. Use ASCII Diagrams And Layer Questions In README Files
**Decision:** Notebook and hazard README files should include compact "what this layer asks" blocks and ASCII diagrams
instead of acting only as cross-reference indexes.

**Rationale:**
- The user explicitly values short, high-signal explanations like:
  `inside the polygon: which pixels are wet? how many are wet? what is the average wet depth?`
- These explanations help future sessions restart without needing to open notebooks first.
- ASCII plots are sufficient for method intuition and work well in Markdown reviews.

## 4. Solar Flood V1 Uses A Representative Value-Mix Assumption
**Decision:** For solar flood V1, inundated area fraction can proxy inundated value fraction when exact sub-asset
locations are unavailable, but the assumption must be documented.

**Rationale:**
- Solar M2 emits exposed fraction and conditional depth from raster pixels inside the polygon.
- M3 then applies capex-weighted component curves as if the wet area contains the same value mix as the whole plant.
- This is a practical V1 assumption, but it can understate or overstate loss if low electrical equipment is spatially
  clustered, raised, or dry.

## 5. Flood Usually Maxes Over Inland Sub-Perils For Overlapping Equipment
**Decision:** For inland flood physical loss, riverine and pluvial should be combined with a worse-source-wins rule for
the same equipment, with additive-capped envelopes treated as sensitivity rather than the headline.

**Rationale:**
- Riverine and pluvial can be driven by the same storm and can drown the same components.
- Naive addition can double-count the same damaged equipment.
- This mirrors the larger principle: combine rules are peril/asset specific, not a universal sum.

## 6. Collector Substation Mapping Is Not Automatic Physical Wind-Farm Loss
**Decision:** A mapped collector/substation should be treated as exposure/dependency evidence by default. It should
enter wind-farm physical damage only when ownership and inclusion in the asset TIV / insured value schedule are
confirmed.

**Rationale:**
- USWTDB gives turbine points, not collector-substation coordinates.
- The hull + OSM/HIFLD method is valuable because it prevents grabbing a neighboring substation.
- The value-breakdown workbook does not support a clean standalone `substation = 9% of wind farm TIV` physical bucket.
  It has a combined `ELECTRICAL_COLLECTION + SUBSTATION` row and explicitly says the public source does not split
  collection from substation.
- Physical damage and disruption/outage are different products. Flooded grid dependencies should not be smuggled into
  M3 physical damage.

## 7. Defer The Flood x Wind-Farm Scope Correction To A Focused Next Chat
**Decision:** Do not rush code changes to the flood wind-farm M3/M4 notebooks in this close-out. Preserve the finding
and tackle it deliberately next session.

**Rationale:**
- This is a model-scope correction, not a small documentation edit.
- Changing it can materially change EAL and PML outputs.
- The right next step is to decide the product boundary: physical-only baseline, owned-collector sensitivity, or
  separate disruption/dependency model.
