# Task context — Flood Path 2 (unified M1 + restructure)

## Objective
Execute **JD-FL-19 (Path 2)**: restore the standard M1=field / M2=couple layer split that flood violated, and unify
flood's structure now that it's the first **two-asset** hazard (solar + wind_farm). Make flood structurally identical
to the other four hazards (M0/M1 shared at the peril top; M2–M4 per asset).

## Background
- Flood is the first hazard with two assets. Solar's M0/M1 sat at the flood top level; wind nested its own `m0/m1`
  under `wind_farm/`. Investigating that asymmetry surfaced the root cause: flood's **M1 did the footprint reduction**
  (it emitted depth already averaged over the solar footprint), so M2 was "deliberately thin." That early coupling is
  why wind couldn't reuse solar's M1 and forked its own.
- The other four hazards (hail/wildfire/convective_wind/hurricane): **M1 = asset-independent field; M2 = coupling.**
- User decision path: chose **Option 1(ii) — genuinely unify** each sub-peril's M1 into ONE notebook over all sites
  (not 1(i) co-located per-asset notebooks, which is cosmetic). "okay follow the convention then."

## Problems hit & fixed
- **Two site schemas differ** — solar `flood_m0_sites.json` has no `slug` (derive from name); wind
  `flood_wind_m0_sites.json` has `slug`. Normalised both to `{asset, slug, name, role, lat, lon}` in each M1.
- **Riverine genuinely uses different methods per site** — BLE depth-grid image (solar TX/LA) vs SFHA-bathtub off
  3DEP (wind Zone-A). Solved with method-per-site dispatch + a method-tagged manifest; M2 dispatches on the tag.
- **Wind M3 read a now-removed M1 manifest** (only to get the RP list). Repointed: it now derives RPs from the M2
  depth-table columns — Path-2 correct (M3 reads M2, not M1).
- **Orphaned data manifests** (`flood_wind_m1_catalog*.json`) deleted; **stale provenance `source` strings** in the
  moved wind M0 notebooks corrected.

## What we built / changed
- **Unified M1 (both assets):** `m1_catalog/pluvial/01_catalog` (Atlas-14→SCS-CN, all sites) and
  `m1_catalog/riverine/01_catalog` (method-per-site: `ble_image`/`sfha_bathtub`/`dry`).
- **M2 updated:** solar + wind M2 read the shared field manifests and filter to their own asset's sites.
- **Folders:** wind M0 moved up to `m0_input_data/04`,`05`; `wind_farm/m0_input_data` + `wind_farm/m1_catalog`
  removed. `solar/` + `wind_farm/` now M2–M4 only.
- **Docs:** flood/m0/m1/wind_farm READMEs + `docs/plans/flood/{decisions.md,m_wind_farm.md}` updated; JD-FL-19 → ✅
  executed.
- **Tooling:** added `scripts/regen_ipynb.py` (percent-`.py` → executed `.ipynb`; kernel via `REGEN_KERNEL`,
  defaults to portable `python3` — personal env name not hard-coded).

## Files touched
```
Notebooks/flood/m1_catalog/pluvial/01_catalog.{py,ipynb}      REWRITTEN — unified field, all sites
Notebooks/flood/m1_catalog/riverine/01_catalog.{py,ipynb}     REWRITTEN — unified field, method-per-site
Notebooks/flood/solar/m2_coupling/01_coupling.{py,ipynb}      EDIT — read shared M1, filter asset=solar
Notebooks/flood/wind_farm/m2_coupling/01_coupling.{py,ipynb}  EDIT — read shared M1, filter asset=wind_farm
Notebooks/flood/wind_farm/m3_damage/01_damage.{py,ipynb}      EDIT — RPs from M2 cols, drop M1 dep
Notebooks/flood/m0_input_data/04_wind_screening_sweep.*       MOVED (from wind_farm/m0_input_data/00_*)
Notebooks/flood/m0_input_data/05_wind_site_screen_and_geometry.*  MOVED (from wind_farm/m0_input_data/01_*)
Notebooks/flood/{README, m0_input_data/README, m1_catalog/README, wind_farm/README}.md   UPDATED
docs/plans/flood/{decisions.md, m_wind_farm.md}              UPDATED (JD-FL-19 executed)
scripts/regen_ipynb.py                                       NEW
data/flood/flood_wind_m1_catalog{,_pluvial}_manifest.json   DELETED (orphaned)
data/flood/flood_pluvial_m1_field_manifest.json             NEW (unified pluvial field)
```

## Status
✅ **Executed and validated end-to-end; numbers preserved. Not committed** (user holds flood branch until coastal ×
wind is done too).

## Next steps
1. **Review** (this is the next chat's purpose).
2. **Coastal × wind** build — fold in the method-dispatch fix (see decisions.md / handoff §1).
3. All-three for wind → flood complete → commit branch.
