# M0 — Input Data (the active plan)

*The first modeling layer (it sits **under** the new [layer-0 hazard-definition](00_hazard_definition.md), which
authored the event *before* any data): meet the raw wind hazard data and **understand** it. "What extreme-wind
hazard does the public record say exists at the two sites, and what do we really know about it?" Method-neutral
— understanding, not the model. Mirrors hail's M0 (record-fit) and wildfire's M0 (pre-integrated rasters);
wind needs **both** flavours at once.*

**Where this sits:** layer-0 (definition) → **M0 (evidence)** → [M1 catalog](m1_catalog.md) → [M2 coupling](m2_coupling.md)
→ [M3 damage](m3_damage.md) → [M4 loss & metrics](m4_loss_metrics.md). No losses, no events-as-objects yet —
just the *evidence*, each source explored on its own terms, then compared. **How the event was defined first:**
[00_hazard_definition](00_hazard_definition.md). **Why these sources:** [discussion/convective_wind/03](../../extra/discussion/convective_wind/03_hazard_definition_and_thresholds.md).

---

## The structural twist — wind M0 meets **two data shapes at once** (read this first)

Hail M0 met one shape: a **record** (radar/report series) to *extract events* and *fit* a rate. Wildfire M0 met
the other: a **pre-integrated surface** (FSim BP+FLP) to *read a profile* — no fit ([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
**Convective wind is the first peril that needs both** — *one peril with two sub-perils*: **[T] tornado** and
**[W] strong / straight-line wind** (derecho, downburst, thunderstorm gust, synoptic high wind), which land in
different coupling buckets ([discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)).
*(Hurricane / tropical cyclone is a **separate, deferred peril**, not a convective-wind sub-peril — related only
through the shared 3-s-gust wind-damage curve; see [DD-WN-9](decisions.md).)*

| Sub-peril | Coupling bucket | The data shape M0 must meet | Primary source |
|---|---|---|---|
| **Strong / straight-line wind** | site-conditioned (bucket 3) | a **pre-integrated return-period gust surface** (the *wildfire-analog* — like FSim, the probabilistic tail is already baked in) | **ASCE 7-22 design-wind map** (3-s gust by MRI) — read via the ASCE Hazard Tool |
| **Tornado** | areal hit-or-miss (bucket 1) | a **path/strike record** to fit `λ` + EF severity (the *hail-analog*) | **SPC SVRGIS** tornado tracks (path geometry, 1950+) |

> **So M0 here is not one walkthrough — it's two**: read the **ASCE RP surface** at each site (strong wind,
> profile-assembly) *and* extract the **SPC tornado/wind record** around each site (tornado, event-fit). Both
> are public; both feed the same [M1 catalog](m1_catalog.md), which forks per sub-peril. The two-shape contrast
> is itself a [learning-log](../../learning_logs/README.md) candidate once built.

---

## Sourcing — direct public products, no Hydronos ([DD-WN-3](decisions.md))

| Notebook | Source | What it is | Access |
|---|---|---|---|
| [`01_asce_hazard`] | **ASCE 7-22 design-wind maps** (Hazard Tool API, point lookup) | 3-s gust at 33 ft, Exposure C, by **MRI** (RC I 300-yr / II 700-yr / III 1,700-yr / IV 3,000-yr); **Appendix F** to ~10⁴–10⁶-yr | free API, point query |
| [`01_asce_hazard`] | **ASCE 7-22 Ch 32 tornado maps** (NIST/ARA) | design tornado 3-s gust by **MRI × effective plan area** (RC III 1,700-yr / IV 3,000-yr); **covers ~EF2 and below** | free API |
| [`02_spc_storm_record`] | **SPC SVRGIS** | tornado tracks 1950+ (~70k, **path length × width**, EF rating, touchdown/liftoff); severe **wind reports** 1955+ (gust kt or damage-inferred) | no auth, public |
| [`02_spc_storm_record`] | **NOAA Storm Events DB** | Thunderstorm Wind / High Wind / Strong Wind / Tornado, 1950+; gust in kt or damage-inferred; episode/event structure | no auth, public |
| [`03_asset_geometry`] | **USWTDB** (turbine points) + **boundary polygons** (OSM/EIA `powerplants_enriched_v2`, renewablesinfo DB) | per-turbine lat/lon + the lease/areal footprint MultiPolygon | no auth, public |
| (screening) | **FEMA NRI** (Tornado + Strong Wind = 2 of 18 hazards) | loss-side screening; frequency from SPC reports | no auth, public |

**No public stochastic catalog exists** for tornado/convective wind (operational catalogs are proprietary —
Verisk, Moody's RMS). The reference's authorization (Hazard_Data_Reference §4): *"the ASCE 7-22 wind and tornado
hazard maps already embed a probabilistic return-period analysis (NIST tornado simulation, ASCE wind statistics),
so the RP surface exists even though a downloadable event set does not. For custom frequency, fit Poisson
occurrence + EF/gust severity to the SPC record, bias-corrected for population."* → this single sentence
authorizes **both** the ASCE-surface path (strong wind, [DD-WN-3](decisions.md)) **and** the SPC-fit path (tornado, [DD-WN-5](decisions.md)).

**Re-verify endpoints live at build time.** Cache raw pulls (ASCE JSON responses, SPC/Storm-Events extracts,
USWTDB rows, boundary polygons) to `data/convective_wind/<asset>_raw/` (**gitignored**; keep a small manifest).

### Setup prerequisite

The `.venv` has `pandas`/`pyarrow`/`numpy`/`rasterio`/`geopandas`/`shapely` (added at wildfire M0). Wind adds
**no new heavy deps** — ASCE is a JSON point API, SPC/Storm-Events are tabular, USWTDB is points, boundaries are
the same `geopandas` MultiPolygons wildfire used. Confirm `requests` is present for the ASCE Hazard Tool client.
Notebooks are jupytext `.py`(percent) + `.ipynb`, kernel `hazard_modeling`.

---

## Notebook `01_asce_hazard` — the strong-wind & tornado **return-period surfaces** (pre-integrated)

1. **From-scratch "what is this surface" walkthrough** — the ASCE Hazard Tool returns, at a lat/lon, a **3-s gust
   (mph) per risk-category MRI**. Explain plainly: this is *not* a forecast and *not* a single observation — it is
   a **pre-integrated return-period surface**, the wind-hazard analog of FSim's BP+FLP ([learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
   ASCE/NIST already did the probabilistic tail extrapolation; we *read* it, we don't *fit* it.
2. **Fetch** the basic-wind-speed values at **both site centroids** (Traverse, Shepherds Flat) for RC I/II/III/IV;
   if reachable, the **Appendix F** very-long-MRI values (10⁴–10⁶-yr) for the deep tail. Cache the JSON.
3. **Field-dictionary every value** (value + meaning + reference base + units): basic wind speed = **3-s peak gust
   at 33 ft, Exposure C**; **MRI = mean recurrence interval = return period** (so RC II = the 700-yr gust); the
   risk-category→MRI map (AWN-15, surface vintage = ASCE 7-22). Cite [data dictionary 03](../../extra/discussion/convective_wind/03_hazard_definition_and_thresholds.md).
4. **Fetch the Ch 32 tornado design speed** at both sites for RC III/IV — note it is a function of **effective
   plan area Aₑ**, not a single map value, and that it **covers ~EF2 and below** (not full EF5). Record what the
   tool returns vs the "not designed for the violent tail" caveat.
5. **Exposure-terrain note (AWN-15):** the surface is Exposure C (open terrain); both sites are open
   (cropland / Columbia Gorge) so C is apt — but record that terrain B/C/D would adjust, and that ASCE governs
   **building-like** assets (PV racking, enclosures) while **turbine fragility anchors come from IEC 61400 / NESC,
   not ASCE design loads** (matrix line 1792). The ASCE surface is the *meteorological hazard*, not the turbine curve.
6. **The two-threshold trap, made concrete** ([00_hazard_definition](00_hazard_definition.md)): plot the site's
   RP→gust curve against (a) the **meteorological event threshold** μ = **58 mph** (NWS severe) and (b) the **asset
   damage-onset threshold** (IEC survival ≈ 52–70 m/s) — show that *most* of the catalog (gusts just over 58 mph)
   sits far **below** the damage onset. This is the figure that teaches why the damage curve is anchored at ≈0.
7. **Emit** `data/convective_wind/<asset>_wind_m0_asce.parquet` (RP→gust table per site, per sub-peril) + a kept JSON manifest
   (exact ASCE edition, MRIs, exposure, vintage, units; Appendix-F availability).

## Notebook `02_spc_storm_record` — the **tornado & convective-wind record** (event-fit)

1. **From-scratch "what is this record" walkthrough** — SVRGIS tornado rows carry **path geometry** (length × width,
   touchdown/liftoff, EF rating), *unique to tornado* (unlike hail/wind points). Storm Events rows carry gust (kt
   or damage-inferred) and an episode/event structure. Explain the row → event mapping before any statistic.
2. **Fetch** tornado tracks (SVRGIS) and Thunderstorm/High/Strong-Wind reports (Storm Events) within a stated
   collection radius around each site (the radius is a homogeneity/data-consistency choice — its *size* cancels in
   `λ_asset = λ_collection · p_hit`, [learning-06](../../learning_logs/06_collection_region_size_cancels.md); choose
   it, don't tune magnitude with it). Cache the extracts.
3. **Field-dictionary** the columns: `EVENT_TYPE, MAGNITUDE, MAGNITUDE_TYPE, EF rating, path length × width,
   BEGIN/END_LAT/LON, EPISODE_ID, DAMAGE_PROPERTY`. Pin the **EF bin table** (EF0 65–85 / EF1 86–110 / EF2 111–135 /
   EF3 136–165 / EF4 166–200 / EF5 >200 mph, 3-s gust, damage-inferred via **28 DIs × 8 DODs**), and the **severe
   wind = ≥58 mph** definition. State that EF is **damage-inferred, not measured**.
4. **Episode de-duplication** (one episode = one event): group by `(EPISODE_ID, EVENT_TYPE)`, MAGNITUDE = max within
   episode, dates = earliest/latest, coords = mean (the old repo's `process_noaa_data` logic — reuse the structure,
   not its lack of bias-correction).
5. **🔴 Report / population-bias audit (AWN-1, frequency-critical)** — the single most important caveat for wind
   frequency. SPC counts are **population-biased**, detection of weak events has **increased over time**, the
   **F→EF switch in 2007** is a discontinuity, wind reports **mix measured gusts with damage-only** entries, and EF
   ratings are **biased low in rural/open land** (capped by the strongest damage indicator present — *both our sites
   are rural*, so historical EF severity is likely understated). **Demonstrate** the pre/post-1996 and pre/post-2007
   count steps; conclude that frequency must be **bias-corrected before fitting** (M1). Do **not** silently filter to
   1996+ and call it done (the old repo's omission).
6. **Per-site tornado path statistics** for M2: empirical distribution of path length, width, and EF rating near
   each site; the EF-class mean areas (km²) for the path-aware Minkowski input. Tabulate the count, window length,
   and the implied raw `λ_collection` per EF class (un-bias-corrected — flag it).
7. **Emit** `data/convective_wind/<asset>_wind_m0_spc.parquet` (de-duplicated tornado + convective-wind events, path stats) +
   manifest (window, radius, F→EF break, bias-correction TODO flag).

## Notebook `03_asset_geometry` — the two sites, two exposure views

1. **The two sites** (settled framing, owner-confirmed) — a **low-vs-high** convective-wind contrast mirroring
   hail/wildfire's baseline-vs-proving pattern:

| role | asset | where | screened exposure |
|---|---|---|---|
| **proving** | **Traverse Wind Energy Center** (~999 MW) | **Oklahoma** — tornado-alley + derecho corridor | the high end: real tornado-path density + frequent severe straight-line wind |
| **baseline** | **Shepherds Flat** (~845 MW) | **Oregon** — Columbia River Gorge | minimal tornado/derecho; the near-zero-tornado baseline |

2. **Two exposure geometries** — wind farms are **spread out**, so M0 captures *both*:
   - the **boundary polygon** (OSM/EIA `powerplants_enriched_v2`, renewablesinfo DB) = the **areal footprint** for
     tornado path/swath intersection (the lease polygon, ~tens of km²);
   - the **USWTDB turbine points** = the refined **per-turbine point cloud** (each turbine is a separate small target;
     a tornado may clip a handful while missing the rest — the per-turbine view is where the path-aware areal
     coupling earns its keep, M2).
   Record both; M2 uses the polygon for the areal extent and the point cloud for the refined per-turbine view.
3. **TIV** — per-turbine value × turbine count (or $/kW × MW); subsystem cost-split deferred to [M3](m3_damage.md).
   Mark Traverse/Shepherds Flat TIV as **estimated** where not in the registry (AWN-14), so every metric can be shown
   as **% of TIV alongside $**.
4. **Emit** `data/convective_wind/<asset>_wind_m0_geometry.parquet` (turbine points + boundary polygon + TIV) + manifest.

## Cross-source comparison (the M0 payoff → feeds M1)

A short closing section: for each site, put the **ASCE RP→gust curve** beside the **SPC-extracted convective-wind
gusts** (do the design-surface and the raw record roughly agree on the broad-area gust level?), and the **SPC
tornado-path density** beside the **Ch 32 design-tornado speed** (does the historical strike record corroborate
the NIST-integrated map, given it caps at ~EF2?). Conclude — per [DD-WN-3](decisions.md) (strong wind) +
[DD-WN-5](decisions.md) (tornado) — the M1 split:
**strong wind = the ASCE pre-integrated surface** (site-conditioned, profile-assembly), **tornado = the SPC fit**
(bias-corrected `λ` + EF severity). This is M0's deliverable: the hazard *understood and reconciled across both
data shapes*, ready for M1.

---

## Outputs

```text
data/convective_wind/<asset>_raw/                          raw ASCE JSON, SPC/Storm-Events, USWTDB, polygon   (gitignored)
data/convective_wind/<asset>_wind_m0_asce.parquet          ASCE RP→gust table (strong wind + Ch 32 tornado)   (gitignored)
data/convective_wind/<asset>_wind_m0_spc.parquet           de-duplicated SPC tornado + convective-wind events (gitignored)
data/convective_wind/<asset>_wind_m0_geometry.parquet      USWTDB points + boundary polygon + TIV             (gitignored)
data/convective_wind/<asset>_wind_m0_*_manifest.json       provenance + units + bias-correction TODO          (kept)
```

## Assumptions surfaced (this layer)

AWN-11 (public source, no Hydronos — [DD-WN-3](decisions.md)) · AWN-15 (ASCE surface = pre-integrated, Exposure C
reference) · AWN-9 (ASCE governs building-like; turbine fragility anchors = IEC/NESC) · **AWN-1 (SPC report /
population bias — frequency-critical, to-bias-correct)** · AWN-7 (EF damage-inferred, rural-low bias) · AWN-6
(two thresholds: NWS 58 mph event vs IEC survival damage-onset) · AWN-? (collection-region size cancels —
[learning-06](../../learning_logs/06_collection_region_size_cancels.md)) · AWN-14 (TIV estimated where not in
registry — %-of-TIV display). Full register: [`assumptions.md`](assumptions.md).

## Open questions to resolve in / before M0

- ✅ **The two sites** — Traverse (OK, proving) + Shepherds Flat (OR, baseline), owner-confirmed (cross-peril
  low-vs-high pattern).
- **ASCE Hazard Tool reachability** — confirm the API returns RC I–IV + (if possible) Appendix F at both sites;
  fall back to the published map values if the API gates.
- **Bias-correction method** — *which* population/detection-bias correction to apply to SPC counts (decide the
  approach in M0's audit, apply in M1). The old repo applied **none** — we must.
- **Per-turbine vs polygon for tornado** — confirm the M2 input convention (polygon for areal extent, USWTDB points
  for the refined per-turbine strike view).
- **F→EF reconciliation window** — decide the fit window given the 2007 F→EF break and pre-1996 damage-value gap.

## Honoring the exploratory-data-notebook principle (the binding checklist)

All three M0 notebooks **must** satisfy [`principles/notebook_work/exploratory_data_notebooks.md`](../../principles/notebook_work/exploratory_data_notebooks.md)
— *interpret every variable, don't just display it; the interpretation is the deliverable.* The 10-point checklist,
instantiated for wind:

1. **Intent & scope** — "M0, evidence only; no losses, no events-as-objects; method-neutral; the event was already
   *defined* in layer-0."
2. **Source & provenance** — pin the exact **ASCE edition (7-22)**, the **SVRGIS / Storm-Events windows + radius**,
   the **USWTDB vintage**; cache the raw bytes under `data/convective_wind/<asset>_raw/`.
3. **Fetch** — thin, readable clients (ASCE Hazard Tool point query; SPC/Storm-Events tabular pull; USWTDB rows);
   no downstream entanglement.
4. **Windows & sampling, stated** — the collection radius and the record window stated explicitly (and that the
   radius *size* cancels, [learning-06](../../learning_logs/06_collection_region_size_cancels.md)); **no silent caps**
   (do **not** quietly drop to 1996+).
5. **Quality audit** — event counts by decade (the population-bias steps), F→EF discontinuity, measured-vs-damage-only
   split, NoData fraction, EF-rural-low caveat.
6. **Field / surface dictionary — a *complete pass*** — every value with **value + meaning + units/base +
   what-it's-NOT + use-decision**: ASCE (3-s gust, MRI=RP, Exposure C, Ch 32 plan-area dependence), SPC (EF bins,
   ≥58 mph severe, path length × width, damage-inferred), USWTDB (turbine point, hub height), the boundary polygon
   (areal footprint). Flag any undocumented field with a visible ⚠.
7. **Distributions & coverage** — the RP→gust curve, the EF-class histogram, the path-length/width distribution,
   the turbine point map over the polygon — **each with a written takeaway**.
8. **Gotchas inline** — the "a number is meaningless without its base" traps (below), next to the data.
9. **Cross-references** — link every concept to [00_hazard_definition](00_hazard_definition.md),
   [discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md),
   [discussion/convective_wind/03](../../extra/discussion/convective_wind/03_hazard_definition_and_thresholds.md), the
   [hazard_math notes](../../../Learning/ML-DL/InfraSure_related/hazard_math/README.md), and
   [coupling gpt/03](../../extra/discussion/gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md)
   — don't re-derive.
10. **Carried-forward artifact** — the clean per-asset M0 parquets + manifests + the open questions.

**The "number needs its base" traps — wind instances** (each a latent bug if shown without its base):

| Source / field | The trap | Its base / correct reading |
|---|---|---|
| **ASCE basic wind speed** | looks like "the wind here" | it is the **3-s gust at a specific MRI** (RC II = 700-yr), at **33 ft, Exposure C** — name the return period and the reference height/terrain |
| **ASCE MRI** | reads like a forecast horizon | **MRI = return period**; reading several MRIs = sampling the EVT return-level curve at fixed exceedance probabilities |
| **Ch 32 tornado speed** | looks like one map value | it is a function of **effective plan area Aₑ** *and* MRI — and **caps at ~EF2** (not the violent tail) |
| **SPC severe wind ≥58 mph** | the *meteorological* threshold | it is the **catalog μ for λ**, **not** the asset damage onset (IEC survival is far higher) — keep the two distinct |
| **EF rating** | reads as measured wind | **damage-inferred** (28 DIs × 8 DODs); **biased low in rural/open land** — *both sites are rural* |
| **SPC count over time** | reads as a trend | **population-biased + detection-increasing + F→EF-2007 break**; bias-correct before fitting frequency |
| **single turbine point** | one target | a wind farm is **spread out** — a narrow tornado path clips *some* turbines; use the point cloud, not one centroid |

## How M0 runs

Per the per-phase loop (Questions → Research → Decisions → Detailed Plan → Execute → Feedback → Document). Research
+ decisions are largely done (the discussion docs + layer-0). **Next concrete step once this plan is greenlit:**
create `Notebooks/convective_wind/m0_input_data/` and build `01_asce_hazard` first (the pre-integrated surface — fastest path
to a real number, exactly as FSim was for wildfire), then `02_spc_storm_record` (the bias-aware record), then
`03_asset_geometry`, then the cross-source comparison — one notebook at a time, no jumps.

**Next → M1 (catalog):** fork the reconciled evidence per sub-peril — strong wind from the ASCE surface
(profile-assembly; severity is **Gumbel/exponential, ξ ≈ 0**, capped at L — the ASCE return-level curve is
log-linear), tornado from the bias-corrected SPC fit (`λ` + **bounded-GPD severity, ξ < 0** — it reaches the EF5
ceiling L). The two sub-peril event streams are treated as **disjoint and independent** (the ASCE basic-wind surface
is non-tornadic by construction; tornado = the SPC Tornado record) — a classification/data-product assumption,
not a physical law.
