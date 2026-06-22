# Handoff — Coastal × wind: COMPLETE M0→M4, all three sub-perils (2026-06-21)

> **Read me first.** Built **coastal flood × wind-farm** end-to-end **M0→M4** at the all-three site **Amazon Wind US
> East (NC)**, with wind's **M2/M3/M4 unified into one notebook each** (M1 unified/asset-aware). **M4 was briefly
> paused** thinking the surge×wind compound combine needed an unbuilt hurricane × wind-farm wind leg — but **that leg
> already existed and was purpose-built for this join** (`data/hurricane/tc_windfarm_m3_damage.parquet`: same site /
> λ=0.0116 / **24 storms with 0 event_family_id mismatch** / same 7-subsystem capex split). So M4 ran the compound
> combine. **Coastal × wind is done.** Nothing committed (flood branch held until all of flood is finished).
>
> **M4 result:** Amazon coastal compound EAL **0.013%** (worst Cat-3 storm 14.3% TIV, PML500 1.43%); total flood Amazon
> **0.069%** (inland 0.056 + coastal 0.013). Green River unchanged (inland-only, EAL 1.276%, NRI-validated).

## 60-second summary

- **The site (found by a national scout, `scripts/explore_coastal_wind_site.py`):** Amazon Wind US East, Perquimans
  Co NC — 104 turbines / 208 MW / $291M TIV. The Albemarle Sound funnels surge inland → **76% of turbines
  surge-exposed (Cat-3 onset), 11% in riverine Zone A, pluvial everywhere**, and the farm's own **230 kV collector is
  itself surge-exposed**. Nationally only two onshore wind farms have all three (Amazon NC, Peyton Creek TX); Amazon
  is the stronger example.
- **M0** (`m0_input_data/06_coastal_wind_site_screen`) — surge (CFEM) + SFHA + turbine cloud + hull + collector;
  **idempotently added to the shared wind roster** `flood_wind_m0_sites.json` (now 3 sites).
- **M1** — all three sub-perils unified/asset-aware. Riverine gives Amazon its **own NC gauge** (Pasquotank
  0204382800; Green River unchanged). Coastal unified (Amazon 24 storms, λ=0.0116; **Discovery 117 preserved**, solar
  M2 back-compat kept).
- **M2** — **ONE file** (`wind_farm/m2_coupling/01_coupling`): riverine + pluvial + coastal. SLOSH LZW read via
  **GDAL-decompress → DEFLATE (cached)** so it runs in the **hazard env** (no `imagecodecs`). The split `02_coastal`
  was merged in and deleted.
- **M3** — **ONE file**; the source-agnostic curve over all three. **Coastal is Amazon's material sub-peril:**
  Cat-3 → 5.98% of TIV, → 23% at Cat-5. Green River stays riverine-dominated (11.4%). Clean asset contrast.
- **M4** — **UNIFIED, all three.** Inland (riverine+pluvial) annual-max **+** coastal **compound combine** (surge ×
  hurricane wind, per-subsystem `max(wind_DR, surge_DR)` on `event_family_id`, JD-FL-12) **+** total flood (inland +
  coastal). Green River EAL 1.276% (inland-only, NRI-validated); Amazon coastal compound 0.013%, total 0.069%.

## The compound combine (how M4 §2c works)

- **Wind leg:** `data/hurricane/tc_windfarm_m3_damage.parquet` — hurricane × wind-farm, per-storm per-subsystem wind DR
  at Amazon (it already existed; its M3 header literally says it's built to be this join's input).
- **Surge leg:** this cell's coastal node depths → per-category, per-subsystem surge DR (flood × wind M3 curves).
- **Combine:** join on `event_family_id` (24 storms, exact match); per subsystem `combined_DR = max(wind_DR, surge_DR)`.
  Shared = electrical + substation; wind-only = rotor + nacelle; surge-only = foundation + civil. Compound-Poisson MC
  at λ=0.0116. **Total flood** = inland annual-max vector + coastal compound vector (independent streams).
- **Still deferred (JD-FL-17):** the full per-storm three-way Level-1 `max(surge,riverine,pluvial)` needs inland flood
  event-ified (rainfall per hurricane → event_family_id). Today inland and coastal are summed as independent streams.

## Repro (all in the hazard env now — SLOSH works there via GDAL-decompress)

```bash
PY=/Users/limjunga/opt/anaconda3/envs/hazard/bin/python
cd Notebooks/flood
$PY m1_catalog/riverine/01_catalog.py     # Amazon bathtub + NC gauge (Pasquotank); Green River unchanged
$PY m1_catalog/coastal/01_catalog.py      # Discovery 117 preserved + Amazon 24 storms
$PY wind_farm/m2_coupling/01_coupling.py  # UNIFIED riverine+pluvial+coastal, one file, hazard env
$PY wind_farm/m3_damage/01_damage.py      # UNIFIED — coastal Cat-3 5.98% -> Cat-5 23% of TIV
$PY wind_farm/m4_loss_metrics/01_loss_metrics.py   # UNIFIED — inland + coastal compound + total flood
```
Regen .ipynb: `REGEN_KERNEL=hazard $PY scripts/regen_ipynb.py <file.py ...>`.

## Don't-trip-on-these

- **Solar's coastal M2** (`solar/m2_coupling/02_coastal_coupling`) still uses tifffile on SLOSH → needs **base
  anaconda** (`/Users/limjunga/opt/anaconda3/bin/python`, has imagecodecs). Only **wind's** M2 was switched to the
  GDAL-decompress path. Both verified.
- The compound MC (M4 §2c) shares ONE storm draw across wind/surge/compound streams so per-realization
  `compound ≥ each leg` holds (independent draws gave MC noise that broke the assertion — fixed).
- `vectors` dict has `<site>` (inland) + `<site>__total` (inland+coastal) keys — the persist loop strips `__total`.
- Nothing committed. Solar coastal stays `01`/`02` split until LA3 West Baton Rouge (its all-three site) — wind led.
