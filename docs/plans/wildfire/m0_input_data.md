# M0 — Input Data (the active plan)

*The first layer: meet the raw wildfire hazard data and **understand** it, before any modeling. "What fire
hazard does the public record say exists at the asset, and what do we really know about it?" Method-neutral —
understanding, not the model. Mirrors hail's M0 ([`Notebooks/hail/m0_input_data/`](../../../Notebooks/hail/m0_input_data/README.md)).*

**Where this sits:** **M0 (evidence)** → M1 catalog → M2 coupling → M3 damage → M4 loss & metrics. No losses,
no events-as-objects yet — just the *evidence*, each candidate explored on its own terms, then compared.

---

## The two candidates — two views of the *same* FSim simulation

Unlike hail's two sources (NOAA vs MRMS — genuinely *different ways to detect* hail), wildfire's two candidates
are **two published products of the same underlying USFS FSim run** — they differ in *representation, vintage,
and resolution*, not in what hazard they describe. (Owner's framing: *"not that different in nature, but
versioning and sourcing differ — tackle them as 1 and 2."*)

| Notebook | Product | What it is | Strength | Weakness |
|---|---|---|---|---|
| [`01_wrc_geoplatform`] | **WRC 2.0** (`RDS-2020-0016-2`, geoplatform ImageServers) | BP + **collapsed** intensity: CFL, FLEP4, FLEP8 (+ WHP) | finer **30 m**; tested fetch plumbing; current intensity (end-2022) | intensity is **collapsed** (no 6-class histogram); BP-vs-intensity **vintage split**; BP upsampled (really 270 m) |
| [`02_fsim_rds`] | **FSim native** (`RDS-2016-0034-3`, USFS RDS archive) | BP + the **full FLP1-6 histogram** | **full 6-class histogram**, single clean vintage (BP+histogram same product), no reconstruction | coarser **270 m**; LANDFIRE-2020 vintage |

**Why both?** To *understand* the hazard surface from both angles and **compare them at matching cells** — the
same cross-product check we did by hand for legacy-vs-lab, now done properly. **Which one is primary is decided
for M1** ([DD-W4](decisions.md): **FSim FLP1-6 is the severity spine**; WRC is the 30 m context / cross-check —
exactly the role-split hail used for MRMS-vs-NOAA).

Because gridded fire-hazard rasters are the **complex** data case (like hail's MRMS GRIB2, not a tidy table),
**`01` — the reader's first contact with wildfire raster data — opens with a from-scratch "what is this
raster" walkthrough** (what it is, what one tile literally contains, grid/CRS/units/fill) *before* any
statistic; `02` then goes deeper on the 6-class histogram. The data dictionary
([discussion `02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md)) is the reference for every
field. See the full checklist in *Honoring the exploratory-data principle* below.

---

## Sourcing — direct public rasters, no Hydronos ([DD-W3](decisions.md))

| Candidate | Endpoint / product | Access |
|---|---|---|
| **01 WRC 2.0** | `imagery.geoplatform.gov/.../Fire_Aviation/USFS_EDW_RMRS_WRC_{BurnProbability, ConditionalFlameLength, FlameLengthExceedProb4ft, FlameLengthExceedProb8ft}/ImageServer` (`exportImage`) | no auth, CC BY 4.0 |
| **02 FSim** | USFS RDS archive `RDS-2016-0034-3` GeoTIFFs (`{CONUS}_FLP1..6.tif`, `{CONUS}_BP.tif`); or the `RDW_Wildfire/RMRS_ProbabilisticWildfireRisk_FLP{1..6}_CONUS/ImageServer` services | no auth, CC BY 4.0 |

**Re-verify endpoints live at build time** (the lab's WRC probes returned HTTP 200 on 2026-05-28; some `?f=json`
probes 403'd in our session — a fetch-header quirk, not an outage). Cache raw rasters to
`data/wildfire/<asset>_raw/` (**gitignored**; keep a small manifest).

### Setup prerequisite

The `.venv` has `pandas`/`pyarrow`/`numpy` but **not `rasterio`** (nor `rioxarray`/`geopandas`). M0 needs them
to read GeoTIFFs and do boundary-zonal stats → **add `rasterio`, `rioxarray`, `geopandas`, `shapely` to
`requirements.txt`** as the first M0 step. Notebooks are jupytext `.py`(percent) + `.ipynb`, kernel
`hazard_modeling`.

---

## Notebook `01_wrc_geoplatform` — explore WRC 2.0 (30 m collapsed)

1. **Fetch** BP, CFL, FLEP4, FLEP8 (and WHP) for the asset region (a small bbox around the asset boundary) via
   `exportImage`; cache GeoTIFFs. Reuse the lab's tile/scale conventions (BP `÷10000`, FLEP `÷1000`, CFL `×1`
   ft) — but **verify, don't trust** (next step).
2. **Field-dictionary every layer** (value + meaning + reference base + units): BP = annual P(burn); CFL = mean
   headfire flame length (ft); FLEP4/8 = conditional P(FL>4/8 ft). Cite [data dictionary `02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md).
3. **Verify the BP `÷10000` divisor** (AW-5) — the divisor is the lab's convention, *not* in service metadata.
   Cross-check the service value against the downloadable source GeoTIFF / `rasterFunctionInfos`.
4. **Conditional vs annual** (AW-4): demonstrate explicitly that BP is annual but CFL/FLEP are
   conditional-on-fire (so they get `×BP` to annualize) — pre-empts the frame error.
5. **🔴 Solar-site land-cover check** (AW-15): inspect the asset pixels — does WRC carry **BP but null
   CFL/FLEP** there (the "oozing" suppression on developed pixels)? Record what we find; this drives M2.
6. **Boundary-zonal sample** (DD-W5): mean + hotspot-max + pixel-count within `asset_boundary`
   (capacity-radius fallback). Compare boundary-zonal vs a single-centroid read (show the dilution).
7. **Emit** `data/wildfire/<asset>_wildfire_m0_wrc.parquet` + a small kept JSON manifest (provenance, exact
   DOI/edition, vintages, units, scale factors).

## Notebook `02_fsim_rds` — explore FSim native FLP1-6 (270 m histogram)

1. **From-scratch "what is this raster" walkthrough** — open one FLP tile, show it's a per-pixel probability;
   the six FLP layers; how 270 m looks vs the asset.
2. **Fetch** BP + FLP1..6 for the asset region (`RDS-2016-0034-3`); cache GeoTIFFs.
3. **Field-dictionary** the 6-class histogram + the verified **FIL class table** ({2,4,6,8,12} ft → kW/m).
   **Check `ΣFLP = 1`** per pixel (AW-6).
4. **Cross-validate the FLEP↔FLP identity** (the heart of this M0): compute `FLEP4 = ΣFLP₃₋₆` and
   `FLEP8 = ΣFLP₅₊₆` from candidate 02, and compare to candidate 01's WRC FLEP4/FLEP8 **at matching cells**.
   Expect *close but not exact* (270 m FSim vs 30 m WildEST, different vintage) — **document the divergence and
   attribute it** (grain / vintage / model), exactly as we did for legacy-vs-lab.
5. **Boundary-zonal sample** the BP + histogram (DD-W5).
6. **Emit** `data/wildfire/<asset>_wildfire_m0_fsim.parquet` + manifest (exact DOI, LANDFIRE-2020 vintage, 270 m).

## Cross-candidate comparison (the M0 payoff → feeds M1)

A short closing section (in `02` or a brief `03`): tabulate, at the asset and a few cells, **WRC BP vs FSim
BP**, **WRC FLEP4/8 vs FSim-derived FLEP4/8**, and the implied flame-length distributions. Conclude — per
[DD-W4](decisions.md) — that **FSim FLP1-6 is the M1 severity spine** (full histogram, single vintage) and
**WRC is the 30 m cross-check / context**. This is M0's deliverable: the hazard surface *understood and
reconciled*, ready for M1 to turn into a catalog.

---

## Asset & geometry — two assets: low-fire baseline + high-fire proving ✅

A deliberate **low-vs-high fire contrast** (owner-confirmed) — the strongest single validation that the model
behaves: *small numbers where fire is rare, material where common.*

| role | asset | where | screened exposure |
|---|---|---|---|
| **baseline** | **Hayhurst Texas Solar** (EIA 66880, 24.8 MW) | Culberson Co., **TX** — Chihuahuan desert grassland | BP ≈ 0.04%/yr — *same asset as hail* (cross-peril coherence) |
| **proving** | **Matrix Pleasant Valley** (EIA 67211, 200 MW) | Ada Co., **ID** — Snake River sagebrush steppe | **BP ≈ 4.7%/yr** (≈107×) — the standout of a 38-asset WRC screen |

Matrix was chosen by screening all 38 registry solar assets by WRC burn-probability × flame intensity (it
won by ~40× over the next candidate). Geometry: **real plant-boundary polygons** (OSM/EIA
`powerplants_enriched_v2`, ~8.8k EIA-matched) where available — Matrix uses a true **5.0 km² MultiPolygon**;
Hayhurst falls back to the **capacity→radius circle** (`r≈69√MW_DC`, not in the dataset). Distinguish *"no
CONUS coverage"* from *"genuinely zero risk"* (legacy null-BP→0 trap).

**Honest expectation (confirmed in `01`):** Hayhurst reads near-zero (desert; and its array pixel is *oozed* —
intensity suppressed, so on-site hazard comes from surrounding grass); Matrix shows a real BP field (≈4.7%/yr)
and moderate sagebrush intensity (FLEP4 ≈ 0.42, mostly < 8 ft) — a **~190× exogenous-exposure contrast**.
Utility solar skews low-fuel (kWh's "4% in high-fire geography"), so Matrix is the genuine high end. (Live
results + plots: the executed `01_wrc_geoplatform` notebook.)

## Outputs

```text
data/wildfire/<asset>_raw/                         raw GeoTIFF tiles        (gitignored)
data/wildfire/<asset>_wildfire_m0_wrc.parquet      WRC 2.0 boundary sample  (gitignored)
data/wildfire/<asset>_wildfire_m0_fsim.parquet     FSim FLP1-6 sample       (gitignored)
data/wildfire/<asset>_wildfire_m0_*_manifest.json  provenance + units       (kept)
```

## Assumptions surfaced (this layer)

AW-3 (public source, no Hydronos) · AW-4 (annual vs conditional) · **AW-5 (BP ÷10000 — to-verify)** · AW-6
(FIL breaks + FLEP=tail-sum, confirmed) · AW-7 (FSim FLP1-6 primary) · AW-8 (Byram coeff) · AW-9 (pin
DOI/edition) · AW-10 (CFL headfire vs FLEP integrated) · AW-11 (boundary-zonal) · **AW-15 (solar-site oozing —
to-verify, M2-critical)**. Full register: [`assumptions.md`](assumptions.md).

## Open questions to resolve in / before M0

- ✅ **Reference asset: Hayhurst Texas Solar** (owner chose cross-peril coherence over a CA fire-asset) — West
  Texas grassland, so expect a low-intensity but real signal (see *Asset & geometry*).
- **BP ÷10000** divisor — verify in `01`.
- **Solar-site oozing / land cover** — characterize in `01`; it decides the M2 coupling input.
- **270 m sufficiency** — confirm FSim 270 m resolves the chosen asset acceptably (very likely yes for utility
  solar); if not, reconsider the 30 m WRC path with a tested reconstruction.

## Honoring the exploratory-data-notebook principle (the binding checklist)

Both M0 notebooks **must** satisfy [`principles/notebook_work/exploratory_data_notebooks.md`](../../principles/notebook_work/exploratory_data_notebooks.md)
— *interpret every variable, don't just display it; the interpretation is the deliverable.* The 10-point
checklist, instantiated for wildfire:

1. **Intent & scope** — "M0, evidence only; no losses, no events-as-objects; method-neutral."
2. **Source & provenance** — pin the exact **DOI + edition** (AW-9), reliability window, and the **vintage
   split** (BP end-2020 vs intensity end-2022); **cache the raw GeoTIFF bytes** under `data/wildfire/<asset>_raw/`.
3. **Fetch** — a thin, readable client (`exportImage` / RDS download); no downstream entanglement.
4. **Windows & sampling, stated** — the asset-region bbox stated explicitly, with the full CONUS extent named;
   **no silent caps**.
5. **Quality audit** — pixel counts, NoData fraction, the **`ΣFLP = 1`** check (02), clamp of any
   `FLEP8 > FLEP4` noise (01).
6. **Field / grid dictionary — a *complete pass***: every layer with **value + meaning + units/base +
   what-it's-NOT + use-decision**; primary (BP, CFL, FLEP4/8, FLP1-6) **and** secondary (WHP, RPS, exposure);
   for gridded data also document **CRS, resolution (270 m vs 30 m), pixel type, scale factor, fill/NoData,
   lon convention** — flag any undocumented band with a visible ⚠.
7. **Distributions & coverage** — a map/histogram of each layer over the asset region, **each with a written
   takeaway**.
8. **Gotchas inline** — the "a number is meaningless without its base" traps (below), next to the data.
9. **Cross-references** — link every concept to the [data dictionary `02`](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md),
   `hazard_math`, and [coupling `gpt/03`](../../extra/discussion/gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md) — don't re-derive.
10. **Carried-forward artifact** — the clean per-asset M0 parquet + manifest + the open questions.

**The "number needs its base" traps — wildfire instances** (the principle's canonical `hail_hlrb`/TIV lesson,
applied — each is a latent bug if shown without its base):

| Layer | The trap | Its base / correct reading |
|---|---|---|
| **BP** | raw U16 service value isn't a probability | `÷10000` (AW-5, *verify*); it is **annual** (don't ×anything to annualize) |
| **FLEP4/8, FLP** | look like probabilities of an event | **conditional on a fire** — annualize via `×BP`; a FLEP is *not* annual |
| **CFL** | "flame length" | **mean *headfire*** FL (ft) — a different geometry population than FLEP; don't blend |
| **WHP** | an ordinal index | **not a probability, not a loss** — never multiply/annualize (the wildfire `hail_hlrb`) |
| **30 m WRC pixel** | looks precise | carries only **270 m** info (BP upsampled) — don't over-read |
| **null BP** | reads as "safe" | distinguish **"no coverage" vs "genuinely zero"** (legacy null→0 trap) |

## How M0 runs

Per the per-phase loop (Questions → Research → Decisions → Detailed Plan → Execute → Feedback → Document).
Research + decisions are largely done (the discussion docs). **Next concrete step once this plan is
greenlit + the reference asset is chosen:** create `Notebooks/wildfire/m0_input_data/` and build `01` first,
then `02`, then the comparison — one notebook at a time, no jumps.

**Next → M1 (catalog):** turn this reconciled evidence into one clean per-asset hazard catalog + frequency.
