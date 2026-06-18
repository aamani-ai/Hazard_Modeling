# Notes — flood × solar M0→M4 + EAL hardening (implementation detail)

## Environment

- **A Python env with the full deps** (NOT the empty repo `.venv`) — numpy 2.x, pandas, shapely, **pyproj**,
  requests, matplotlib, openpyxl, jupytext, nbconvert. `pyproj` (used by the densification for EPSG:5070 equal-area
  drainage-area km²) comes transitively via `geopandas` in `requirements.txt`, so no extra install is needed.
- **Notebook run:** `jupytext --to ipynb X.py && jupyter nbconvert --to notebook --execute --inplace
  --ExecutePreprocessor.kernel_name=python3 X.ipynb`.

## The densification pipeline (M1 §1b)

```
NLDI comid/position  → snap (lat,lon) to NHDPlus reach   → comid 15078158
NLDI comid/{id}/basin→ upstream basin polygon            → 1.91 mi² (Albers EPSG:5070 area)
NSS scenarios (GET)  → LA Coastal Plain SIR 2024-5031 eqn structure (params: DRNAREA, CSL10_85)
NSS estimate (POST)  → fill DRNAREA + slope → Q(2,5,10,25,50,100) cfs
extrapolate Q500     → log-log tail slope (50→100yr)
rating               → p = ln(d500/d100)/ln(Q500/Q100);  depth(rp) = d100·(Q(rp)/Q100)^p
frac (lower RPs)     → log-RP interp between real BLE extents {10:f10, 100:f100}
```

- **Endpoints:** NLDI `https://api.water.usgs.gov/nldi/linked-data`; NSS `https://streamstatsservices`… **404
  (down)**, but **`https://streamstats.usgs.gov/nssservices`** works. Watershed-delineation service was down all
  session → no live HAND.
- **NSS estimate POST gotcha:** the body must be the **exact GET scenario JSON** with `parameters[].value` filled
  in-place (a hand-built minimal payload → HTTP 500). JSON body (`requests.post(..., json=...)`), not form-encoded.
- **Caching:** `cget` (form/GET, existing) + new **`cpost_json`** (JSON POST) — md5(url+payload) → file in
  `data/flood/raw/http_cache/` (~456 files, gitignored). Re-runs deterministic + robust to flaky USGS endpoints.

## Verification / metrics

- **Slope-invariance (the key robustness check):** 10-yr depth = **0.97 ft** at slope 3, 8, AND 20 ft/mi (< 1% move)
  — the rating exponent `p` re-solves to absorb the slope. Result rests on BLE anchors + flow *shape*, not basin params.
- **Densified depth-at-RP (Elizabeth, m):** 10yr 0.298 · 25yr 0.365 · 50yr 0.414 · 100yr 0.464 (BLE) · 500yr 0.604
  (BLE). Monotone; lower RPs ≤ the 100-yr BLE anchor (M1 known-answer check).
- **M3 conditional loss (% TIV):** 10yr 0.76 · 25yr 1.35 · 50yr 1.93 · 100yr 2.61 · 500yr 4.44.
- **M4 metrics (% TIV):** Elizabeth EAL **0.155**, VaR99 2.62, PML100 2.62, PML250 3.65, PML500 4.46, TVaR99 3.76.
  Hayhurst EAL 0.02 (baseline). **Frame check:** PML100≈L100 (2.62≈2.61), PML500≈L500 (4.46≈4.44).
- **§2b comparison:** densified EAL 0.155 vs old assumed-onset 0.115 (@0ft) / 0.131 (@0.5ft) / 0.159 (@1.0ft) →
  densification lands on the @1ft cross-check.
- **External validation (M4 §4b, real-data assertion):** USGS STN high-water marks near the proving site (21 marks,
  Aug-2016 LA flood) read 0 / median 2.1 / 7.9 ft above ground; modeled depths 1.0–2.0 ft (10→500-yr) fall **inside**
  that range → asserted + persisted (`external_validation` in the M4 manifest). Endpoint:
  `stn.wim.usgs.gov/STNServices/HWMs/FilteredHWMs.json?States=<ST>`. **NRI** county-EAL benchmark **not done** — FEMA
  reorganized NRI's public access (old API/download → RAPT tool redirect); GIS server exposes only report GPServers.

## Key insight (→ learning log 13)

**To fill the frequent end of a sparse RP curve, anchor a regional *shape* to your real points — don't import a
heavier *absolute* model.** Anchoring at two real points cancels the shape-source's poorly-known absolute inputs (the
slope here), so the answer is robust. And the "gold-standard" universal method (HAND) was the *least* accurate at this
particular flat, BLE-covered site — "gold standard for coverage" ≠ "most accurate here". HAND becomes essential only
at **no-BLE** sites (nothing to anchor to).

## Gotchas for next time

- Densification is **proving-site-only** (Elizabeth, LA). A national rollout needs **per-site regional equations**
  (Hayhurst is TX, different NSS region) — and the M4 curve already builds from whatever RPs each site has, so the
  asymmetry (Elizabeth 5 pts, Hayhurst 2 pts) flows through cleanly.
- `data/*/raw/` is gitignored → the http_cache is **local-only**; a fresh clone re-fetches live (expected).
