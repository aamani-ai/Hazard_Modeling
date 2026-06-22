# Handoff — Flood Path 2: unified M1 + M0/M1-shared restructure (2026-06-21)

> **Read me first.** This session **executed JD-FL-19 (Path 2)**: flood's M1 was doing M2's job (footprint
> reduction inside M1), and the two assets had asymmetric folders. We fixed both. **Nothing is committed** — the user
> holds the flood branch until *all* of flood is finished (coastal × wind still pending). The next chat is a **review
> of this work** before continuing.

## 60-second summary

- **What was wrong:** flood violated the standard layer split — M1 emitted depth *already reduced over the asset
  footprint*, leaving M2 thin. And solar's M0/M1 sat at the flood top level while wind nested its own `m0/m1` under
  `wind_farm/` (asymmetric, and the *reason* wind couldn't reuse solar's M1).
- **What we did (Path 2):** moved the footprint/per-node **coupling into M2**; M1 now emits the **asset-independent
  field**. Then **genuinely unified** each sub-peril's M1 into ONE notebook over **all sites, both assets** (the
  "follow the convention" option, not co-located per-asset notebooks). Moved M0+M1 to the **top**; `solar/` and
  `wind_farm/` now hold only **M2–M4**.
- **Riverine is method-per-site** (JD-FL-6 realised): `ble_image` (FEMA BLE depth raster) for sites with a depth map,
  `sfha_bathtub` (flood-area + WSE contour off 3DEP + gauge Q(T)) for Zone-A-only sites, `dry` otherwise. The manifest
  is method-tagged; M2 dispatches on the tag.
- **Numbers preserved.** Full chain re-run green: solar Elizabeth **EAL 0.163%**, wind Green River **EAL 1.27%** of
  TIV, all M3/M4 known-answer checks pass. (Only the JD-FL-18 full-res sampling shift in solar riverine M2 — headline
  robust.)

## Repro (verify the chain — uses the `hazard` conda env on this laptop)

```bash
PY=/Users/limjunga/opt/anaconda3/envs/hazard/bin/python   # laptop-specific env; others use their own
cd Notebooks/flood
# M1 (shared, both assets)
$PY m1_catalog/pluvial/01_catalog.py     # 4 sites, runoff Q; Green River 100yr 0.1134, Shepherds Flat 0
$PY m1_catalog/riverine/01_catalog.py    # 2 ble + 1 bathtub + 1 dry; NSS Q100=854, gauge Q100=7055
# M2 (per asset, read shared field, filter to own sites)
$PY solar/m2_coupling/01_coupling.py     # Elizabeth 100yr frac 0.177 / depth 0.433
$PY wind_farm/m2_coupling/01_coupling.py # Green River 100yr 22 turb wet / sub 0.885 m
# M3/M4 (unchanged logic; read M2)
$PY solar/m3_damage/01_damage.py && $PY solar/m4_loss_metrics/01_loss_metrics.py        # EAL 0.163%
$PY wind_farm/m3_damage/01_damage.py && $PY wind_farm/m4_loss_metrics/01_loss_metrics.py # EAL 1.27%
```

Regenerate executed `.ipynb` (jupytext not installed): `REGEN_KERNEL=hazard $PY scripts/regen_ipynb.py <file.py …>`.

## What to scrutinise in the review

1. **Riverine method dispatch is still branched per-asset loop** (`m1_catalog/riverine/01_catalog.py` §0): solar
   sites can only become `ble_image`/`dry`, wind sites only `sfha_bathtub`/`dry`. Correct for today's 4 sites by luck
   of the roster; the cross-branches (wind-with-BLE, solar-needing-bathtub) are **untested**. Fix = an asset-blind
   `select_method(site)` that probes BLE coverage for any site. **Deferred to the coastal × wind build** (you screen
   wind sites for coverage there anyway) — not a bug today. See [decisions.md](decisions.md).
2. **Manifest schema** — one method-tagged `field` list + both `flow_frequency` (ble sites) and `gauge` (bathtub
   sites) blocks in `flood_m1_catalog_manifest.json`. Confirm each M2 filters correctly to its asset.
3. **Wind M3 was decoupled from M1** — it now derives RPs from the M2 depth-table columns (Path-2 correct: M3 reads
   M2, not M1). The two orphaned wind M1 *data* manifests were deleted.
4. **Coastal untouched** — still solar-only, still `01`+`02` split (event-based vs RP-indexed; JD-FL-17).

## NEXT ACTION roadmap

1. **Review this Path 2 work** (this chat's purpose). Optionally lock it in (still no commit) before building more.
2. **Build coastal × wind** (the user's pre-stated next step) — mirrors coastal × solar but per-turbine: M0 coastal
   wind screen → extend shared coastal M1 → wind M2/M3/M4 `02_coastal_*` → compound surge+wind join on
   `event_family_id`. **Fold the §1 method-dispatch fix in here.**
3. When flood × wind has all three sub-perils → **all of flood done → commit the flood branch.**
