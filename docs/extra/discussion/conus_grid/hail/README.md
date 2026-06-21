# conus_grid/hail/

**Hail-specific reasoning for the CONUS gridded product** — the part of the grid discussion that is *not*
generic. The cross-cutting design (architecture, output schema, exposure granularity, assumptions) lives one
level up in [`../`](../README.md); this subfolder holds only what is particular to **sourcing hail's M1 hazard
field**. (Adding wildfire/wind later = a sibling subfolder; this one is the template.)

## Read order

| # | Doc | What it is |
|---|---|---|
| 00 | [`00_m1_data_products_research.md`](00_m1_data_products_research.md) | **Factual research record** — what gridded hail-hazard data products exist (MRMS MESH, MYRORSS, GridRad-Severe, Murillo & Homeyer, Storm Events, FEMA NRI, Das & Allen, …): per-product tables, bucket classification, trade-offs, honesty flags, sources. **No recommendations.** |
| 01 | [`01_m1_sourcing_triage.md`](01_m1_sourcing_triage.md) | **The decision distilled from `00`** — finding: no FSim-equivalent for hail (no product gives both per-cell frequency *and* size distribution); the size distribution is the decisive gap → **self-build, anchored** (MRMS+MYRORSS · Murillo-&-Homeyer bias recipe · Storm-Events ground-truth). Open decisions **DEC-H1…H5**. |
| 02 | [`02_m1_build_flow.md`](02_m1_build_flow.md) | **The simple implementation-facing flow** — what to build first: selected-cell pilot → daily gridded evidence → frequency fit → size distribution → anchors/validation → durable per-cell M1 hazard layer. |
| 03 | [`03_mrms_tail_qa_and_m1_policy.md`](03_mrms_tail_qa_and_m1_policy.md) | **The M0/M1→M2-M4 pause point after the full MRMS run** — recaps the source inventory, Cloud Run M0, reconciliation, full-CONUS M1 numbers, tail diagnostics, what is usable now, what is deferred, and the readiness gate for solar M2-M4. |

## The headline (so you don't have to open both)

**Hail is "self-build, anchored"** — not a Bucket-1 ready field like wildfire/FSim, but not build-from-nothing
either: a validated bias-correction recipe (Murillo & Homeyer) + ground-truth (Storm Events) anchor a MESH
self-build. The size-distribution half *must* be self-built (no public product supplies it), which makes the
EVT severity tail load-bearing — the same move as the storage-boundary decision.

Implementation shorthand: **build a selected-cell MRMS pilot first**, write the same M1 artifact the full
CONUS run will write, validate it against Hayhurst / Storm Events / broad climatology, then add MYRORSS,
bias correction, EVT tail, and full-scale fan-out.

Current V1 update: the MRMS-only full-CONUS M0/M1 runs and the first selected-cell solar M2-M4 smoke run have
completed. Read [`03_mrms_tail_qa_and_m1_policy.md`](03_mrms_tail_qa_and_m1_policy.md) before full solar
M2-M4 scaleout, because it locks the frequency/severity split, the raw-MESH tail QA policy, and the
provisional-loss readiness gate.

## Feeds back into the generic docs

- Exposure for hail × wind (the point-cloud append): [`../03_exposure_granularity.md`](../03_exposure_granularity.md) §3.
- The per-cell M1 artifact (fitted distributions) ↔ storage boundary: [`../01_ideal_architecture_compute_and_grid.md`](../01_ideal_architecture_compute_and_grid.md).
- Hail rows in the grid assumptions register: [`../assumptions.md`](../assumptions.md).
