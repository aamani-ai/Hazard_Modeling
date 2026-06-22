# M1 — Catalog (per-sub-peril flood FIELD, all sites)

*M0 met the flood hazard as raw evidence; **M1 turns it into the asset-independent hazard FIELD the rest of the
pipeline consumes** — per sub-peril, **over every site of both assets in one notebook**, with a manifest declaring the
catalog's choices. Inland flood has no events-as-objects — the return period **is** the frequency basis (annual-maximum,
JD-FL-7); coastal is the event-based exception (compound-Poisson).*

> **M1 emits the field (JD-FL-19)**, not a footprint-reduced depth — the BLE depth raster / flood-area + WSE contour /
> runoff `Q` / per-storm surge catalog. The **coupling** (sampling that field at the asset — areal for solar, per-node
> for wind) lives in **M2**. Each M1 notebook is **shared over both assets**; the asset only matters at M2–M4, which
> filter the shared field to their own sites. Riverine picks its method **per site by data availability** (JD-FL-6),
> not by asset.

**Where this sits:** [M0](../m0_input_data/README.md) → **M1 (catalog — forks here)** → M2 coupling → M3 damage →
M4 loss. Plan: [`docs/plans/flood/m1_catalog.md`](../../../docs/plans/flood/m1_catalog.md). Notebooks:
[`riverine/01_catalog`](riverine/01_catalog.ipynb) + [`pluvial/01_catalog`](pluvial/01_catalog.ipynb) +
[`coastal/01_catalog`](coastal/01_catalog.ipynb) (built).

## The fork — by sub-peril (data + footprint), not coupling

Flood forks the **catalog**, because its sub-perils differ at the **data** — different products, different magnitude
bases, different footprints — even though they re-converge on one depth driver (JD-FL-10). *(Contrast: convective-wind
shares one catalog and forks at **M2** — same atmosphere, two couplings. Flood diverges earlier and re-converges later
at depth→damage.)* All three share the damage driver **inundation depth (ft above ground)**.

| | **Riverine [R]** (`riverine/`) | **Pluvial / flash [F]** (`pluvial/`) | **Coastal / surge [C]** (`coastal/`) |
|---|---|---|---|
| magnitude basis | depth at return period (annual-max, AEP) | depth at return period (annual-max, AEP) | surge depth per storm, by hurricane category (event-based) |
| field emitted | **method-per-site** (by data, JD-FL-6): `ble_image` = FEMA BLE depth raster at native resolution (JD-FL-18); `sfha_bathtub` = NFHL 1% flood-area polygon + boundary WSE contour off 3DEP + per-site USGS gauge (JD-FL-W4); `dry` | NOAA Atlas 14 24-hr rainfall-frequency → SCS Curve-Number **runoff `Q`** per site (one method, every site) | **read** SLOSH MOM depth-by-category (US national raster); frequency = observed-anchored **λ × RAFT category mix** |
| lower RPs / hydrology | `Q(T)` for M2's densification: NLDI→NSS regression (`ble_image`, JD-FL-8) or USGS-NWIS gauge Log-Pearson III (`sfha_bathtub`, JD-FL-W5) | same Atlas-14 RPs (no densification needed; rainfall frequency is continuous) | **n/a — event-based**, not RP-indexed (compound-Poisson via λ; combines with hurricane wind, not the flood annual-max) |
| reduction (→ M2) | footprint/per-node sampling of the field is **M2's job** (JD-FL-19) — areal fraction × conditional depth (solar) / per-node bathtub (wind) | ponding `f`/depth from per-asset 1 m lidar terrain is **M2's job** (JD-FL-19/15) | per-storm footprint/per-node surge depth in M2 |
| confidence | **best-supported** — BLE is HEC-RAS quality; only the rating *between* anchors is modeled | the **blind spot** — no free pluvial *depth* grid → softer/wider, no depth anchor (AFL-P1/P2) | screening-grade — MOM is a **per-category worst-case envelope**, not per-event (ADCIRC gap, JD-FL-14) |

Riverine + pluvial each emit a **field manifest** tagged `sub_peril` (rows tagged `asset`, and `method` per riverine
site); M2 reduces the field to the asset's `{rp_years, aep, exposure_fraction, conditional_depth}` and the two
sub-perils combine worse-source-wins at M4 (JD-FL-11). **Coastal is the deliberate exception** (JD-FL-12/15): its
partner is the **compound-Poisson hurricane engine**, not the flood annual-max — so it emits an **event-based catalog**
(one row per qualifying storm: `{event_family_id, category, surge_depth_ft, min_dist_km}`) with the
**`event_family_id` cross-link switched on**, so M4 joins surge ↔ wind on the *same storm* (per-subsystem
`max(wind_DR, surge_DR)`). M3 still runs one depth→damage path over whatever rows arrive.

## What the catalogs found

- **Riverine (`riverine/01_catalog`)** — method-per-site over both assets:
  - `ble_image` (FEMA BLE depth raster + NSS flow-frequency) for the solar sites: **Elizabeth** (Q₁₀₀≈854 cfs) and
    **LA3 West Baton Rouge** (Q₁₀₀≈2610 cfs); Hayhurst reads the dry control. BLE carries 100/500-yr banded depth; the
    **JD-FL-8 densification** rating supplies the lower RPs (the rating exponent is near-invariant to channel slope).
  - `sfha_bathtub` (NFHL 1% flood-area + 3DEP boundary WSE + USGS-NWIS gauge Log-Pearson III, JD-FL-W4/W5) for the wind
    sites: **Green River** (gauge 05447000, Q₁₀₀≈7055 cfs) and **Amazon Wind US East** (gauge 0204382800, Q₁₀₀≈2946
    cfs). **Shepherds Flat** = `dry`.
- **Pluvial (`pluvial/01_catalog`)** — Atlas 14 24-hr rainfall → SCS-CN runoff `Q` (CN≈80), one method every site
  (10/25/50/100/500-yr): Elizabeth 100-yr `Q`≈0.284 m, LA3 ≈0.247 m, Green River ≈0.113 m, Amazon ≈0.180 m. **Shepherds
  Flat** is outside Atlas 14 coverage (PNW = Atlas 2) → pluvial 0 (a low-rainfall control, AFL-W11). Screening-grade —
  flagged, no depth anchor (AFL-P2); ponding `f`/depth is per-asset terrain, deferred to M2.
- **Coastal (`coastal/01_catalog`)** — per-site event catalogs from SLOSH MOM + RAFT (≤50 km, ≥64 kt) + HURDAT2 over a
  173-yr observed record, each storm stamped with `event_family_id`:
  - **Discovery Solar** (FL): **117 storms** {Cat1:62, 2:33, 3:16, 4:5, 5:1}, λ≈**0.029/yr**; footprint-mean depth Cat-1
    0.08 ft → Cat-5 12.4 ft (clean monotonic gradient).
  - **LA3 West Baton Rouge** (LA): **11 storms** {1:9, 2:1, 3:1}, λ≈**0.0173/yr** (Gulf surge up the Mississippi).
  - **Amazon Wind US East** (NC): **24 storms** {1:21, 2:2, 3:1}, λ≈**0.0116/yr** (Albemarle Sound funnel).
  - Hayhurst / inland sites = **structural zero** (no coastline). The cross-link checks out — qualifying storms also hit
    hurricane-cell sites, confirming the global storm-identity joins.
- **Known-answer checks pass** — depth rises **monotonically** with return period (and with surge category); **dry
  sites read ≈ 0** at all RPs / sub-perils (low-baseline control); RP labels map to AEP (100-yr = 1%).

## Inputs → outputs

M0 BLE depth + 3DEP DEM + USGS NSS/NWIS gauge + NOAA Atlas 14 + NOAA SLOSH MOM + RAFT + HURDAT2 → one **shared** field
manifest per sub-peril over both assets: `data/flood/flood_riverine_m1_catalog_manifest.json` (riverine — `field` rows tagged
`asset`/`method`, plus `flow_frequency` for `ble_image` sites and `gauge` for `sfha_bathtub` sites) +
`flood_pluvial_m1_catalog_manifest.json` (pluvial — per-site runoff `Q`, tagged `asset`) +
`flood_coastal_m1_catalog_manifest.json` with per-site, per-storm parquets (`event_family_id`-stamped). The manifests
are the typed M2 input (sub-peril-keyed; `event_family_id` **reserved** for riverine/pluvial, **switched on** for
coastal).

## Key decisions & assumptions

[JD-FL-6](../../../docs/plans/flood/decisions.md) (BLE depth, national-pipeline fallback) ·
[JD-FL-8](../../../docs/plans/flood/decisions.md) (regression densification of lower RPs) ·
[JD-FL-9](../../../docs/plans/flood/decisions.md) (Atlas 14 → SCS-CN pluvial) ·
[JD-FL-10](../../../docs/plans/flood/decisions.md) (fork at M1) ·
[JD-FL-12/14/15](../../../docs/plans/flood/decisions.md) (coastal event-based + SLOSH/RAFT + cross-link) ·
[JD-FL-4](../../../docs/plans/flood/decisions.md) (`event_family_id` hook). Assumptions **AFL-6/12/13** (riverine
source, lower-RP densify, datum), **AFL-P1/P2** (pluvial source + the `r`/`f` knobs, no anchor), **AFL-W5** (gauge
flow-frequency), **AFL-11** (sub-peril family schema).

**Next → M2 (coupling):** turn the per-sub-peril field into the asset's exposure × conditional depth (site-conditioned,
bucket 3) — solar areal fraction, wind per-node; coastal per-storm.
