# M1 — Catalog (the plan)

*Phase 2 of the flood build. The deliverable is the **flood event catalog**: the **asset-independent depth-at-return-
period field** per sub-peril (one notebook each — riverine / pluvial / coastal — over both assets), plus the
engine-contract manifest. The **field→asset reduction is done in M2** (the coupling), not here (JD-FL-19).* Per the per-phase loop
([feature_workflow](../../workflows/feature_workflow.md)): Questions → Research → Detailed Plan → Execute → Feedback →
Document.

> **Method = FEMA BLE, with StreamStats+HAND as the national fallback ([JD-FL-6](decisions.md)).** A scaling review +
> deep research `jdocs/flood_research_result.md` superseded the single-gauge route. The national
> production spine is **USGS StreamStats (discharge-at-RP) → NOAA OWP HAND (→ depth)**, but **FEMA BLE is preferred
> where it exists — and it exists for the high site (Elizabeth Solar, Allen Parish LA)** ("Data Available"). So V1
> builds the profile by **sampling the BLE depth grids** (1% / 100-yr + 0.2% / 500-yr, layers 12/16) over the real
> footprint polygon, plus the **10-yr (10%) extent** (layer 7). Single-gauge Bulletin 17C is retained as **local
> validation only**. BLE service: `txgeo.usgs.gov/arcgis/rest/services/FEMA_EBFE/EBFE/MapServer`.
>
> **Lower-RP densification ([JD-FL-8](decisions.md)) — built.** BLE gives only the 100/500-yr tail, so the proving
> site's **10/25/50-yr** depths now come from a **regression flow-frequency curve** (USGS NLDI drainage area → NSS
> LA Coastal Plain SIR 2024-5031 → Q(T)) fed into a **power-law rating `depth = d₁₀₀·(Q/Q₁₀₀)^p`** whose exponent is
> pinned by **both real BLE depths**. Result: a 5-point depth-at-RP curve, monotone, with the 10-yr depth ≈ 0.97 ft
> (vs the old assumed 0.5 ft) — and **near-invariant to channel slope** (the exponent absorbs it). The baseline
> (Hayhurst) keeps the tail-only curve (its 10-yr BLE extent is 0 — a true dry control). Live HAND-SRC remains the
> swap-in if the delineation service returns.
>
> **⚠️ The "Questions / Detailed plan" sections below describe the *superseded* single-gauge extraction route** (the
> pre-BLE plan). Kept only as the **no-BLE / ungauged fallback** reference; the built M1 uses BLE per the banner above.

---

## Questions (what M1 must resolve)

1. **Which gauge controls the plant's flood?** *(Historical — Bayou Galion was the early screen pick, since superseded
   by **Elizabeth Solar, Allen Parish LA** as the built riverine high site; the gauge-route below was not used.)* Bayou
   Galion sits in Morehouse Parish LA, FEMA Zone A. Candidates from
   the M0 probe: **Bayou Bartholomew** (runs through Morehouse — likely the local source) vs the **Ouachita River**
   (larger, regional). Pick the stream whose floodplain the plant occupies; confirm by drainage path + DEM.
2. **Record length & quality** — how many annual peaks at the chosen gauge? Bulletin 17C wants ≳ 10, ideally 30+.
   Gaps, mixed populations (rain vs. backwater)?
3. **Regulation / stationarity** — upstream dams or diversions? Bulletin 17C assumes a stationary, ~unregulated
   record; if regulated, note it (and prefer a pre-regulation or regulated-frequency approach).
4. **Datum reconciliation** — USGS gauge datum (often **NGVD29**) vs the DEM's **NAVD88**. Convert before differencing
   (`depth = stage − ground_elev`); the offset in N. Louisiana is ~−0.1 to −0.3 m but must be applied, not assumed.
5. **Gauge→plant offset** — the gauge is up/down-stream of the plant. V1 proxy = use the gauge water-surface directly
   ([AFL-12](assumptions.md)); flag the water-surface-slope error, decide whether a simple slope correction is needed.
6. **Rating-curve availability** — does the gauge publish a stage-discharge rating (NWIS RatingDepot)? If not, fit
   peak **stage** frequency directly (USGS peaks carry gage height alongside discharge) as the fallback.
7. **The event-model bridge (SETTLED, [JD-FL-7](decisions.md)).** *(Originally the open call.)* The RP depth curve
   feeds the shared MC as an **annual-maximum MC** — sample the annual-max loss-exceedance curve directly (not a
   compound-Poisson stream, which mis-fits flood). Coastal instead uses a compound-Poisson surge×wind track (JD-FL-12).

## Data sources

| Source | What it gives | Endpoint |
|--------|---------------|----------|
| **USGS NWIS — peak-flow** | annual peak streamflow (+ peak gage height) per gauge | `nwis/peak` (RDB) |
| **USGS NWIS — site** | gauge metadata, datum, drainage area | `nwis/site` |
| **USGS RatingDepot** | stage-discharge rating (Q→stage) | `waterdata.usgs.gov` rating tables |
| **3DEP DEM** (from `02`) | ground elevation at the footprint (NAVD88) | already pulled |
| **NOAA Atlas 14** *(later, pluvial)* | precip-frequency, if pluvial sub-peril is added | — |

## Detailed plan — `m1_catalog/01_catalog`

1. **Select the controlling gauge** — trace the plant's drainage (DEM + NHD stream network) to Bayou Bartholomew vs
   Ouachita; pick the gauge on that stream nearest the plant. Record drainage area, datum, regulation status.
2. **Pull the peak-flow record** (NWIS `peak`) — annual peak discharge (+ gage height); QA the record (length, gaps,
   qualification codes).
3. **Fit Log-Pearson Type III** (Bulletin 17C) on log-discharge — skew (station + regional weighting), return
   discharge `Q_T` at RP = {2, 5, 10, 25, 50, 100, 200, 500}.
4. **Convert Q_T → stage (WSE)** via the gauge rating; **reconcile datum to NAVD88**.
5. **Depth at the asset** — `depth_T = WSE_T − ground_elev` (DEM); for the flat site, ~uniform across the footprint.
   Hayhurst (no floodplain) → depth ≈ 0 at all RP (the low-baseline control).
6. **Assemble the catalog object** — the depth-at-RP table + the fitted frequency model + provenance, as a
   **sub-peril-keyed manifest** with a reserved `event_family_id` ([JD-FL-4](decisions.md)).
7. **Frame the event-model bridge** (Q7) — document the chosen RP-curve → compound-Poisson-MC mapping for M4.

## Catalog / manifest schema (engine contract — JD-FL-4 hooks)

```
{ peril: "flood", sub_peril: "riverine", event_family_id: null,        # family hooks
  site: {eia, name, lat, lon, ground_elev_navd88_m},
  frequency: { method: "logpearson3_b17c", gauge_id, record_years, skew, regulated: bool },
  depth_rp: [ {rp_years, aep, discharge_cfs, stage_navd88_m, depth_m}, ... ],   # the profile
  datum: {gauge_datum, dem_datum: "NAVD88", offset_applied_m},
  event_model: "<RP→compound-Poisson mapping — TBD>",                   # the open bridge
  provenance: {sources, fit_diagnostics, caveats: [offset, regulation]} }
```

## Verification checklist (basics-spot-on)

- [ ] Controlling gauge justified (drainage path, not just nearest point).
- [ ] Record length adequate for LP3 (≳10 yr) or limitation stated; regulation/stationarity checked.
- [ ] Datum reconciled (gauge → NAVD88), offset applied and recorded.
- [ ] `Q_100` sanity-checked against any published FEMA/USGS discharge for the reach.
- [ ] Depth rises **monotonically** with return period; **Hayhurst depth ≈ 0** at all RP (low-baseline control).
- [ ] Depth magnitudes physically plausible for a flat alluvial floodplain (not tens of metres).
- [ ] Event-model bridge documented before M4.

## Deferred / swap-in

- **Pre-integrated depth grid** (Fathom / FEMA Risk MAP) → swap in as the spine if sourced ([JD-FL-5](decisions.md)
  revisit), demoting extraction to cross-check.
- **2-D hydraulics** (HEC-RAS / gauge-offset slope) → V1 uses the `stage − DEM` proxy on a flat site; refine later.
- **Pluvial sub-peril** → **built** as its own M1 notebook (Atlas 14 → SCS-CN runoff) over both assets; **coastal**
  (SLOSH surge) is **built** too (JD-FL-12). The JD-FL-4 family hook held — adding them was a one-notebook-each change.

## On greenlight

Create [`../../../Notebooks/flood/m1_catalog/`](../../../Notebooks/flood) and build `01_catalog` — gauge selection →
peak-flow → LP3 → stage → depth-at-RP → the manifest. Document outcomes here + fold caveats into
[`assumptions.md`](assumptions.md).
