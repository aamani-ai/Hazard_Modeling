# Decisions — Flood Path 2 (indexes `docs/plans/flood/decisions.md`)

## JD-FL-19 · Path 2 — asset-independent M1 (field) + coupling in M2; M0/M1 shared at top, per-asset M2–M4
**Status: ✅ executed (2026-06-21).** Canonical entry + full execution note: [`docs/plans/flood/decisions.md`](../../../plans/flood/decisions.md).
- M1 emits the **field**, not a footprint-reduced depth. Coupling (areal for solar, per-node for wind) lives in M2.
- M1 **genuinely unified** per sub-peril over both assets (one notebook, all sites) — the "follow the convention"
  choice (Option 1ii), explicitly *not* co-located per-asset notebooks (1i, cosmetic).
- M3/M4 insulated (consume M2's reduced depth, same schema). Numbers preserved.

## JD-FL-6 (realised) · Riverine method-per-site by data availability
Riverine picks its method from the **site's data**, not the asset:
- `ble_image` — FEMA BLE depth raster exists (read at native resolution, JD-FL-18) + NLDI→NSS `Q(T)` (JD-FL-8).
- `sfha_bathtub` — only Zone-A mapped → 1% flood-area + boundary WSE contour off 3DEP (JD-FL-W4) + gauge Log-Pearson
  `Q(T)` (JD-FL-W5).
- `dry` — not in SFHA.
The manifest is method-tagged; M2 dispatches on the tag. Pluvial needs no dispatch — one method (Atlas-14→SCS-CN)
everywhere.

## OPEN — the `sfha_bathtub` branch only works for ONE hardcoded site (revisit at coastal × wind)
**Reviewed 2026-06-21** ([`jdocs/flood_path2_review.md`](../../../../jdocs/flood_path2_review.md)). The original handoff
framed this as a single dispatch issue; the review correctly widened it: **the roster assumption is wired in THREE
places**, and fixing the dispatch alone is insufficient. Canonical write-up is the JD-FL-19 "MUST-FIX-FIRST" block in
[`docs/plans/flood/decisions.md`](../../../plans/flood/decisions.md). In short:
1. **Gauge hardcoded** — `riverine/01_catalog.py` `GAUGE="05447000"` + `gauge_block` computed once → every bathtub site
   inherits Green River's `Q(T)`.
2. **M2 structural** — wind M2 reads the single `rman["gauge"]` (TypeError if no bathtub site); solar M2 assumes a
   populated `flow_frequency` (empty → silent sparse RP grid).
3. **Per-asset dispatch loop** — cross-branches (wind-with-BLE) unreachable/untested.

- **Risk:** a coast-front wind site that *also* sits in a riverine SFHA → routed to bathtub → **silently wrong
  hydrology, no error**.
- **Fix (all three):** asset-blind `select_method(site)` probing BLE per site + **per-site nearest-NWIS-gauge** +
  M2 keyed per site (not one global `gauge` block).
- **Decision:** **first task of the coastal × wind build**, before the new site's riverine field is generated. Not a
  bug today; current 4-site numbers unaffected.

## OPEN — manifest bloat (pre-commit, not a build blocker)
`flood_m1_catalog_manifest.json` is **1.8 MB** — Green River's `flood_area_wkt` inlined into a *tracked* manifest
(`ble_image` correctly stores rasters as `raw/` paths). De-inline the bathtub polygon to gitignored `raw/` with a path
before the flood-branch commit, else it's permanent in git history. (Review finding #5.)

## DONE in review follow-up (2026-06-21)
Orphaned `flood_m1_catalog_pluvial_manifest.json` `git rm`'d (#4); stale M2 manifest descriptions corrected (#8 — wind
"pluvial pending" → computed; solar `sub_peril` → `["riverine","pluvial"]`); both M2 `.ipynb` regenerated.

## Unchanged (in scope but deliberately not touched)
- **JD-FL-17** — coastal stays solar-only and `01`+`02` split (event-based hurricane-surge vs RP-indexed
  riverine/pluvial). Folds to one notebook only when a single site has all three sub-perils.
- **JD-FL-18** — full-resolution BLE *image* sampling kept (the only component shift; loss headline robust).
