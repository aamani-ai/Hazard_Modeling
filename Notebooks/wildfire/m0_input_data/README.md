# M0 — Input Data (raw wildfire hazard evidence)

*The first layer: meet the raw wildfire hazard data and **understand** it, before any modeling. "What fire
hazard does the public record say exists at the asset, and what do we really know about it?" Method-neutral —
understanding, not the model.*

**Where this sits:** **M0 (evidence)** → M1 catalog → M2 coupling → M3 damage → M4 loss & metrics. No losses,
no events-as-objects yet — just the *evidence*, each candidate explored on its own terms, then **compared**.
Plan: [`docs/plans/wildfire/m0_input_data.md`](../../../docs/plans/wildfire/m0_input_data.md) ·
Principles: [`docs/principles/notebook_work/`](../../../docs/principles/notebook_work/README.md).

## The two candidates — two views of the *same* FSim simulation

Unlike hail's two *sources* (NOAA vs MRMS — different ways to *detect* hail), wildfire's two candidates are
**two published products of the same USFS FSim run** — they differ in representation, vintage, and
resolution, not in the hazard they describe.

| Notebook | Product | What it is | Strength | Weakness |
|---|---|---|---|---|
| [`01_wrc_geoplatform`](01_wrc_geoplatform.ipynb) | **WRC 2.0** (`RDS-2020-0016-2`, geoplatform ImageServers) | BP + **collapsed** intensity (CFL, FLEP4, FLEP8) | **30 m**; tested fetch; current intensity (end-2022) | intensity **collapsed** (no 6-class histogram); BP/intensity **vintage split**; BP really 270 m |
| [`02_fsim_rds`](02_fsim_rds.ipynb) | **FSim native** (`RDS-2016-0034-3`, USFS RDS archive) | BP + the **full FLP1-6 histogram** | **full histogram**, single clean vintage, no reconstruction | **270 m**; LANDFIRE-2020 vintage |

**Why both?** To understand the hazard from both angles and **compare them at matching cells**. Which is
primary is decided in M1 ([DD-W4](../../../docs/plans/wildfire/decisions.md): **FSim FLP1-6 is the severity
spine**; WRC is the 30 m cross-check — the role-split hail used for MRMS-vs-NOAA). Gridded fire-hazard rasters
are the **complex** data case, so `01` opens with a **from-scratch "what is this raster" walkthrough** before
any statistic (per the [exploratory-notebook principle](../../../docs/principles/notebook_work/exploratory_data_notebooks.md)).

## Reference asset

**Hayhurst Texas Solar** (EIA 66880; Culberson County, TX; `31.816°N, −104.085°W`; 24.8 MW; ~$36.8M) — the
**same asset as hail**, for cross-peril coherence toward the Total-Loss tier. West-Texas grassland → expect
**non-trivial burn probability but low intensity** (a small-but-real, thin-tailed exogenous-wildfire signal).

## Sourcing — direct public rasters, **no Hydronos** ([DD-W3](../../../docs/plans/wildfire/decisions.md))

`01` → WRC ImageServers (`imagery.geoplatform.gov/.../USFS_EDW_RMRS_WRC_*`, `exportImage`) · `02` → USFS RDS
archive `RDS-2016-0034-3` GeoTIFFs. No auth, CC BY 4.0. Raw rasters cached under
`data/wildfire/hayhurst_raw/` (gitignored); a small manifest is kept.

## Inputs → outputs

Public WRC / FSim rasters → `data/wildfire/hayhurst_wildfire_m0_wrc.parquet`,
`…_m0_fsim.parquet` (+ `…_manifest.json` kept). Raw GeoTIFF tiles cached under `data/wildfire/hayhurst_raw/`.

## Key decisions & assumptions (this layer)

[DD-W3](../../../docs/plans/wildfire/decisions.md) (public source, no Hydronos) · [DD-W4](../../../docs/plans/wildfire/decisions.md)
(FSim FLP1-6 primary) · [DD-W5](../../../docs/plans/wildfire/decisions.md) (boundary-zonal). Assumptions
**AW-3…AW-10, AW-15** — esp. **AW-4** (BP annual; CFL/FLEP conditional), **AW-5** (BP ÷10000 — *to-verify*),
**AW-6** (FIL breaks + FLEP = tail-sum, confirmed), **AW-15** (solar-site "oozing" — *to-verify, M2-critical*).
Full register: [`assumptions.md`](../../../docs/plans/wildfire/assumptions.md).

**Next → M1 (catalog):** turn this reconciled evidence into one clean per-asset hazard catalog + frequency.
