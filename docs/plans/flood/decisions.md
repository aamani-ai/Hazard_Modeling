# Flood pipeline — decisions log

Running record of the non-obvious design decisions for the flood → solar build (then wind in V2), ADR-style
(context → options → decision → why → revisit trigger). Newest on top. Prefix `JD-FL-*`.

> **Status: scope, frequency, sites, and the modularity hooks decided (proposed); one call still open.** The
> competitive-research architecture (`…/learnings/architecture/`) **pre-defines** flood's taxonomy (A12), catalog
> method (A20), coupling (A21), and damage form (A22). Settled below: scope/defer-coastal (JD-FL-1), frequency path
> (JD-FL-2), the two sites + national screen (JD-FL-3), the add-coastal-later hooks (JD-FL-4). **The one genuinely-open
> call is the event-model bridge** to our shared MC engine (bottom). **Update (2026-06-17):** depth-source research +
> a FEMA-BLE probe **supersede** the single-gauge route — the spine is now the **national StreamStats+HAND pipeline,
> FEMA-BLE-preferred where it exists** ([JD-FL-6](#jd-fl-6)); BLE *does* exist for Bayou Galion. **The event-model
> bridge is now settled** ([JD-FL-7](#jd-fl-7)) — annual-maximum MC sampling the loss-exceedance curve.
> **Update (2026-06-20):** **coastal `[C]` route-zero scoped** — JD-FL-12 (the wind+surge compound combine, the
> genuinely new step), JD-FL-13 (coastal site pair), JD-FL-14 (SLOSH category-based spine + standalone→compound
> sequencing). Coastal realizes the [JD-FL-1](#jd-fl-1)/[JD-FL-4](#jd-fl-4) deferral hooks; not yet built.
> **Update (2026-06-20):** M0 coastal built (`01_solar_sites` — Discovery Solar Center FL, the surge high
> site); the surge **event/frequency definition** for M1 is settled in JD-FL-15.
> **Update (2026-06-20):** the **compound combine's wind leg** is settled in JD-FL-16 — Discovery appended to the
> hurricane pipeline (not recomputed in flood, not reusing Everglades).
> **Update (2026-06-20) — coastal × solar BUILT end-to-end (M0→M4).** Discovery Solar Center FL: surge leg
> (M0 screen → M1 SLOSH-MOM catalog → M2/M3 depth-damage) + wind leg (hurricane M1→M3, Discovery appended) joined on
> `event_family_id` and combined **per subsystem** (JD-FL-12, exact — both curves subsystem-resolved). Compound
> **EAL 1.15% / PML500 62.9% TIV** (band 1.28% / 66.7%), materially above wind-only (0.86% / 26.7%) — both legs
> contribute. Hurricane headline kept Discovery-free (cross-link guard added to TC M4).
> **V2 plan (JD-FL-17):** the **three-way flood combine** — one unified event-based M4 ("deepest water → wind by
> subsystem", absent hazards zeroed; `02_*` notebooks collapse to helpers) at a co-located all-three site
> (**LA3 West Baton Rouge**, verified Zone A + surge to 16.5 ft + pluvial); blocked on event-ifying inland (RAFT
> rainfall slice). The disjoint-site `01`/`02` split is a V1 artifact, correct until then.
> **Update (2026-06-21):** flood **structure + sampling** investigated and **executed** — JD-FL-18 (BLE sampling
> under-resolved but loss robust; full-resolution image method adopted) and JD-FL-19 (Path 2: asset-independent M1 +
> coupling in M2; M1 **unified per sub-peril over both assets**, M0/M1 shared at top, per-asset M2–M4 — flood now
> structurally matches the other four hazards; numbers preserved).

---

## JD-FL-19 · Flood structure — **Path 2: asset-independent M1 (field) + coupling in M2; M0/M1 shared at top, per-asset M2–M4** — aligns flood with the other four hazards

**Date:** 2026-06-21 · **Status:** ✅ **executed** (2026-06-21) · Fixes the M1/M2 layer-definition violation; sets the multi-asset template · *standard-interface / modular*

**Context.** Flood is the **first two-asset hazard** (solar + wind). Its **solar** M0/M1 sit at the peril top level while
**wind** nested its own `m0/m1` under `wind_farm/` — an asymmetry. Investigating it surfaced the root cause: **flood
violates the standard M1/M2 definitions.** Across the other four hazards (hail/wildfire/convective_wind/hurricane), **M1 =
the asset-independent hazard field**, and **M2 = coupling** (sample the field at the asset). Flood instead does the
**footprint-sampling inside M1** (it emits depth *already reduced over the solar footprint*), leaving M2 "deliberately
thin" — its own M2 doc admits *"the field→asset step is done [in M1]."* That early coupling is **why** wind couldn't reuse
solar's M1 and forked its own.

**Decision (proposed) — Path 2.** Move the footprint-sampling **from M1 to M2**, restoring the definitions:
- **M1** emits the **asset-independent field**: the BLE depth raster (riverine, sampled via JD-FL-18's image method) /
  runoff `Q` (pluvial) / SLOSH-by-category + storm catalog (coastal) — *no footprint reduction*.
- **M2** does the **coupling**: sample the field at the asset (areal mean for solar; per-node for wind).
- **M3/M4 unchanged** (insulated — they consume M2's reduced depth, same schema).
- **Folders:** M0/M1 move to the **top** (shared), per-asset **M2–M4** — **identical to hail/hurricane**, and the template
  for when they get a second asset.

**Why.** It makes flood *honor* the layer definitions instead of carrying a private interpretation, and makes **all five
hazards structurally consistent**. The genuinely-shared thing (raw data) already lives in `data/*/raw/`; per-asset **site
screening** (M0) remains per-asset (different fleets) — but that is true for *every* hazard once it has two assets, not a
flood quirk.

**Validation.** A PoC confirmed the M1→M2 relocation is **clean and number-safe** (riverine: M2-reduce reproduces M1's
output bit-for-bit when sampling is held fixed). The sampling *upgrade* (JD-FL-18) shifts the components but **not the loss
headline** (robust, −0.5%/−4% at 100/500-yr).

**Honest caveats.** (1) ~7 notebooks rewritten (5 M1 + 2–3 M2) + full re-run + re-validate; coastal (event-based) the
fiddliest. (2) **M3/M4 stay `01`+`02`** — the event-frame merge to one notebook is the *separate* [JD-FL-17](#jd-fl-17).
(3) The truly-shared M1 also needs the **depth-source choice unified per site** (BLE-preferred / bathtub-fallback,
[JD-FL-6](#jd-fl-6)) since solar (BLE) and wind (Zone-A bathtub) sites differ.

**Executed (2026-06-21).** Path 2 built and number-validated end-to-end:
- **M1 genuinely unified per sub-peril over both assets** (the "follow the convention" option — *one* notebook all
  sites, not co-located per-asset notebooks). `m1_catalog/pluvial/01_catalog` runs Atlas 14 → SCS-CN for **all 4 sites**
  (one method); `m1_catalog/riverine/01_catalog` dispatches **method-per-site by data availability** (JD-FL-6 realised):
  `ble_image` for BLE-covered sites (Hayhurst, Elizabeth) + NLDI→NSS `Q(T)`; `sfha_bathtub` for Zone-A-only sites
  (Green River) + gauge Log-Pearson `Q(T)`; `dry` otherwise (Shepherds Flat). One method-tagged field manifest each
  (`flood_riverine_m1_catalog_manifest.json`, `flood_pluvial_m1_catalog_manifest.json`), rows tagged `asset`.
- **M2 per asset reads the shared field and filters to its sites** — solar M2 (areal footprint reduce) + wind M2
  (per-node bathtub); both reproduce the prior coupling numbers.
- **Folders:** M0 (01–03 solar, 04–05 wind) + M1 now shared at the **top**; `solar/` and `wind_farm/` hold only M2–M4.
  The nested `wind_farm/m0_input_data` + `wind_farm/m1_catalog` are removed.
- **Numbers preserved:** full chain re-run green — solar Elizabeth EAL **0.163%**, wind Green River EAL **1.27%** of TIV,
  all M3/M4 known-answer checks pass (only the JD-FL-18 full-res sampling shift in solar riverine M2, headline-robust).
- **Coastal stays solar-only** (coastal × wind is a later build); its `01`/`02` event-frame is untouched (JD-FL-17).

**Post-Path-2 review (2026-06-21, [`jdocs/flood_path2_review.md`](../../../jdocs/flood_path2_review.md)).** Code/manifest
audit — restructure confirmed sound, numbers re-verified against committed manifests. Cleanups applied immediately:
orphaned `flood_m1_catalog_pluvial_manifest.json` `git rm`'d; stale M2 manifest descriptions fixed (wind "pluvial
pending" → computed; solar `sub_peril` "riverine" → `["riverine","pluvial"]`). Two items carried forward (below).

**⚠️ Coastal × wind — MUST-FIX-FIRST (before the new site generates any riverine field).** The `sfha_bathtub` branch
currently works for **exactly one hardcoded site**. The roster assumption is wired in **three** places, not one — fixing
the dispatch alone is insufficient:
1. **Gauge hardcoded** — `riverine/01_catalog.py` `GAUGE="05447000"` + `gauge_block` computed once (`if gauge_block is
   None`). Every bathtub site inherits **Green River's** flow-frequency curve. (This is the "single gauge doesn't scale"
   failure JD-FL-5 was superseded for, reintroduced.)
2. **Wind M2 structural** — reads the single `rman["gauge"]["Q_cfs"]` at module top and applies it to every node; also
   **throws `TypeError`** if no wind site resolves to `sfha_bathtub` (gauge left `None`). Solar M2 symmetrically assumes a
   populated `flow_frequency` (empty → silent sparse 100/500-only RP grid).
3. **Per-asset dispatch loop** — solar sites can only resolve `ble_image`/`dry`, wind only `sfha_bathtub`/`dry`; the
   cross-branches (wind-with-BLE) are untested.
   **Fix (all three together):** an asset-blind `select_method(site)` that probes BLE coverage per site + a **per-site
   nearest-NWIS-gauge** lookup in the `sfha_bathtub` branch + M2 keyed per site (not one global `gauge` block).
   **Why first:** a coast-front wind site can also sit in a riverine SFHA → routed to bathtub → **silently wrong
   hydrology, no error**. Do this before wiring the new site's riverine layer.

**✅ DONE (2026-06-21) — manifest de-inline (review finding #5).** `flood_riverine_m1_catalog_manifest.json` had grown to
**11.57 MB** (Green River 1.8 MB + Amazon Wind's NC Zone-A polygon **9.7 MB**, inlined into a *tracked* manifest).
Fixed: each `sfha_bathtub` polygon is now written to gitignored `raw/flood_area/<slug>.wkt` and the manifest stores a
`flood_area_path` (mirroring the `ble_image` raster-path convention); wind M2 loads it via the path. Manifest now
**23 KB**, numbers unchanged. (Reproducible: M1 re-writes the polygon from FEMA NFHL on a fresh run, same as the BLE
rasters.)

**Revisit trigger.** Hail/hurricane adopt the same layout the day they gain a second asset; coastal × wind extends the
riverine method-dispatch pattern when built (do the MUST-FIX-FIRST cluster as its first task).

---

## JD-FL-18 · Flood depth sampling — **full-resolution BLE *image* read, not the 68-point grid**; the grid under-samples the flooded fraction, but the loss is robust (offsetting biases)

**Date:** 2026-06-21 · **Status:** decided · the sampling method for [JD-FL-19](#jd-fl-19)'s M1 field · *basics-spot-on*

**Context.** M1 sampled BLE depth on an **11×11 grid clipped to the footprint** (`n=5` → ~68 points at Elizabeth) — an
**unvalidated default**. A convergence test (68 → 188 → 297 points) showed it **does not converge**: the flooded
*fraction* keeps climbing with resolution → **68 points under-sample**.

**The finding (measured against the full-resolution flood map — 637k pixels at native ~3 m).** The committed grid
**under-counts the flooded fraction** (Elizabeth 100-yr 0.162→**0.177**, 500-yr 0.191→**0.218**; ~+10–14%) and
**over-states depth** (0.464→0.433 m, 0.604→0.532 m; ~−7–12%). **But the two biases offset in the loss** (bigger area ×
shallower depth) → conditional loss moves only **−0.5 % (100-yr) / −4.2 % (500-yr)**. **The committed headline is robust.**

**Decision.** Adopt **full-resolution image sampling** as the correct method: MapServer `export` the depth layer for the
footprint bbox → **flooded fraction** from non-transparent pixels at native resolution (one request), **depth** from the
6 legend bands (color → band-midpoint). Replaces the point grid. **Folded into [JD-FL-19](#jd-fl-19)'s M1 rewrite** (no
urgent standalone re-run — the headline barely moves).

**Honest caveats.** (1) The image is **symbolized → banded depth** (6 classes; ≤1 ft floored at 0.5 ft) — it over-states
the near-zero **Hayhurst** baseline (immaterial, baseline ≈ 0) but **matches the dense point-identify at Elizabeth**
(0.433/0.532 ≈ 0.433/0.540), so it's sound on the headline driver. (2) **BLE-riverine specific** — pluvial (Atlas-14) and
coastal (SLOSH, already raster-sampled) sample differently. (3) A raw-value BLE raster (no ImageServer exists today) would
give *continuous* full-resolution depth — the future upgrade.

**Revisit trigger.** A value-raster BLE endpoint → continuous full-res depth; the same convergence check on pluvial/other
sites.

---

## JD-FL-17 · The three-way flood combine — **one unified event-based M4: "deepest water, then wind by subsystem", absent hazards zeroed** (V2; needs inland event-ified) — supersedes the V1 per-site `01`/`02` split

**Date:** 2026-06-20 · **Status:** proposed (V2 — not built) · Completes the [JD-FL-10](#jd-fl-10)/[JD-FL-11](#jd-fl-11)/[JD-FL-12](#jd-fl-12) combine framework; the open question flagged when coastal landed · *modular / basics-spot-on*

**Context.** V1 ships the flood sub-perils on **disjoint sites + disjoint event frames**: riverine + pluvial at **Elizabeth**
(annual-max RP, worse-source-wins, [JD-FL-11](#jd-fl-11)) and coastal at **Discovery** (event-based surge + wind compound,
[JD-FL-12](#jd-fl-12)/[JD-FL-16](#jd-fl-16)). So they never actually combine — and the M4 layer is **two notebooks**
(`01_loss_metrics` inland + `02_coastal_compound`). The open question: **how do all three combine on ONE asset?** The reference
doc ([Flood-Data-Ref](../../../jdocs/Hazard_Data_Reference-Flood.md) §5/§7/§8) says *"handle each separately, then combine on the
**shared depth metric**… avoid double-counting… the compound case (one storm → surge + rain + river) — treat manually; no public
product models it"* — i.e. it gives the **principle, not the formula**. (Contrast the **old model**: sums Riverine/Flash/Coastal as
**independent perils** → double-counts the shared storm — the anti-pattern, [JD-FL-11](#jd-fl-11)/[JD-FL-1](#jd-fl-1).)

**Decision (proposed) — one unified, event-based M4: a single per-storm loop with a two-level combine.**
```
for each event (compound-Poisson stream):
    # LEVEL 1 — water (all inundation, same equipment → a part drowns once)
    flood_depth = max(surge_depth, riverine_depth, pluvial_depth)        # worse-source-wins, JD-FL-11 extended
    # LEVEL 2 — water + wind (different subsystems → additive; max on the shared two)
    combined_DRᵢ = max(wind_DRᵢ, flood_DRᵢ)   per subsystem               # JD-FL-12, already built
    event_loss   = Σᵢ TIVᵢ · combined_DRᵢ      (capped at TIV)
aggregate event losses → annual → EAL / PML / VaR
```
**Generality (the load-bearing property):** absent hazards enter as **0** → they drop out of the `max` and the sum automatically.
So the **same loop** serves every site — 1, 2, or 3 sub-perils, with or without wind — with no branching:
- coastal-only (Discovery) = the loop with `riverine = pluvial = 0`
- riverine+pluvial (Elizabeth) = the loop with `surge = wind = 0`
- all-three (LA3 W. Baton Rouge) = all inputs present.

**Notebook collapse.** Because it's one loop, V2 **merges the layer notebooks**: M3 → one `01_damage` (one depth-damage curve over
whatever rows arrive); M4 → one `01_loss_metrics` (Level 2 = a **helper inside the loop**, not a separate notebook). The V1
`02_coastal_*` notebooks **dissolve into helpers**. The split was never about coastal being special — it was a V1 artifact of **two
event frames at two sites**; unify the frame and it's one notebook.

**All-three V2 site — confirmed.** **LA3 West Baton Rouge Solar (EIA 61646, LA, 50 MW)** is a genuine all-three asset (verified
live): **Zone A** (true 1% riverine, Mississippi floodplain) **+** SLOSH surge **Cat-2 3.5 ft → Cat-3 10.5 → Cat-5 16.5 ft**
(deeper than Discovery — Gulf surge propagates up-river) **+** flat delta (pluvial). The compound-flood proving site.

**Execution rule (2026-06-21) — unify M3/M4 per-asset *once that asset has a co-located all-three site*; until then `01`/`02`
split is correct.** This makes the split principled (a function of site coverage), not asset-specific drift:
- **Wind leads now** — **Amazon Wind US East (NC)** is the wind all-three site (76% surge / 11% riverine Zone A / pluvial;
  M0 `06`), so wind builds **unified single M3/M4** here. (User-requested + this rule.)
- **Solar followed (✅ 2026-06-21)** — **LA3 West Baton Rouge** (above) was built as the all-three solar site, so solar
  **unified its M2/M3/M4 into one file each** (collapsing `01`+`02_coastal`), same as wind. Both assets are now on the
  unified form, each triggered by its own all-three site — neither retrofitted prematurely. (See the "Solar all-three"
  execution note below.)
- **⚠️ Honesty caveat — *file*-collapse now, full *per-storm* Level-1 combine still blocked.** Unified M3/M4 here means
  ONE notebook each (the notebook collapse), with the *computable* combine: riverine+pluvial in the annual-max RP frame
  (worse-source-wins, JD-FL-11) + coastal event-based (compound surge×wind via `event_family_id`, JD-FL-12), combined at
  the headline. The **full per-storm three-way Level-1 `max(surge,riverine,pluvial)`** still needs inland flood
  **event-ified** (rainfall per hurricane → `event_family_id`) — the blocker below — and stays deferred for **wind too**,
  not just solar. So wind's unified M4 is two aggregations under one roof, not yet one per-storm loop.

**Coastal x wind — COMPLETE, M0->M4 (2026-06-21).** All three sub-perils, unified, at Amazon Wind US East (NC):
- **M0** (`02_wind_sites` -> Amazon Wind US East; added to the shared wind roster), **M1** coastal
  (unified/asset-aware: Amazon 24 storms, lambda=0.0116; Discovery 117 preserved), **M2** (UNIFIED one file —
  riverine+pluvial+coastal; SLOSH via GDAL-decompress so it runs in the hazard env), **M3** (UNIFIED — coastal is
  Amazon's material sub-peril: Cat-3 -> 5.98% TIV, -> 23% at Cat-5). Per-site gauge fix shipped (Pasquotank NC gauge).
- **M4 (UNIFIED) — the surge x wind compound combine RAN.** The "missing hurricane x wind-farm wind leg" the build was
  paused on **already existed and was purpose-built for this join**: `data/hurricane/tc_windfarm_m3_damage.parquet` —
  per-storm, per-subsystem wind DR at Amazon, same 7-subsystem capex split, same lambda=0.0116, **same 24 storms (0
  event_family_id mismatch).** M4 combines per subsystem `combined_DR = max(wind_DR, surge_DR)` (shared =
  electrical+substation; wind-only = rotor+nacelle; surge-only = foundation+civil; JD-FL-12), compound-Poisson MC at
  lambda, + **total flood = inland annual-max + coastal compound** (independent streams).
- **Numbers:** Amazon coastal compound EAL **0.013%** (worst Cat-3 storm $41.8M = 14.3% TIV; PML500 1.43%); total flood
  Amazon **0.069%** (inland 0.056 + coastal 0.013). Green River unchanged (inland-only, EAL 1.276%, NRI-validated).
- **Still deferred (JD-FL-17 blocker):** the full per-storm three-way Level-1 `max(surge,riverine,pluvial)` needs inland
  flood **event-ified** (rainfall per hurricane -> event_family_id). Today inland (annual-max) + coastal (Poisson) are
  summed as independent streams — honest, not yet one per-storm loop.
- **✅ RESOLVED (2026-06-21) — hurricane x wind-farm BUILT (M2→M4); the wind leg now exists.** New cell
  `Notebooks/hurricane/wind_farm/` (M0/M1 shared from flood-coastal M1; asset forked at M2): M2 = per-turbine
  field-intensity at Amazon (the non-degenerate V2 the solar cell foreshadowed — gust spread median 4.4% across the
  ~18 km lease); M3 = convective_wind's turbine curve reused (hurricane wind ≈ straight-line → aero reach, asset DR
  cap ~0.65) → **per-storm, per-subsystem wind DR stamped `event_family_id`**; M4 = wind-only EAL 0.012% / PML500
  1.43% of TIV (small — Amazon's storms peak ~132 mph, right at IEC turbine survival; the rare Cat-3 close passage is
  the tail). **The resume input for coastal x wind M4 is `data/hurricane/tc_windfarm_m3_damage.parquet`** (per-storm
  per-subsystem wind DR + `event_family_id`) — join it to the surge leg (`coastal_event_rows`) on `event_family_id`
  and run the JD-FL-12 `max(wind_DRᵢ, surge_DRᵢ)`-per-subsystem combine. **Next step: finish coastal x wind M4.**

**Solar all-three — COMPLETE, M0->M4 unified (2026-06-21).** Built **LA3 West Baton Rouge Solar (EIA 61646, LA)** as the
solar analogue of Amazon — a genuine all-three site (riverine **Zone A / FEMA BLE "Lower Grand"** -> `ble_image` + NSS
densification · coastal **Cat-3** SLOSH, 11 RAFT storms λ=0.0173 · pluvial Atlas-14). Steps: M0 `01_solar_sites`
registers LA3 in the inland roster + dem_context + coastal roster; **hurricane x solar extended to LA3** (added to
`tc_m0_sites.json`, re-ran hurricane M1/M2/M3 -> LA3 51-storm gust to 140 mph in `tc_m3_damage`, Discovery/Everglades
preserved); flood M1 auto-picks-up LA3 across all three; **solar M2/M3/M4 UNIFIED into one file each** (collapsed
`01`+`02_coastal`; SLOSH via GDAL-decompress so it runs in the hazard env). M4 = inland annual-max + coastal compound
(per-subsystem `max(wind_DR,surge_DR)`, shared = PV_ARRAY+SUBSTATION) + total. **Numbers:** LA3 total flood **0.761%**
(inland 0.653 + coastal compound 0.107); Discovery 0.338% (coastal-only); **Elizabeth 0.163% preserved** (inland-only);
Hayhurst 0.030%. Both assets are now unified on their own all-three site; the disjoint-site Elizabeth/Discovery examples
remain as single-peril references. (Full per-storm three-way Level-1 still deferred — same JD-FL-17 inland-event-ify blocker.)

**Why.** It is the **physically correct** model — a hurricane is **one event** driving surge + rainfall + wind together, so
combining per-event captures compound flooding and double-counts nothing (the reference's §7 case). One engine, one annual
aggregation, general across sites — the opposite of the old model's independent-sum.

**The blocker (what V2 must build first).** Level 1 needs **all three water depths *per storm***. Surge we have (SLOSH); the missing
piece is **the rainfall each hurricane drops → riverine/pluvial depth, stamped with the storm's `event_family_id`** — i.e.
**event-ify the inland sub-perils**. That needs RAFT's **deferred rainfall slice** (the ~16 GB variable not loaded in M0). And
**non-hurricane** inland flooding (frontal/snowmelt — the bulk) has no storm catalog → it remains a **second event stream**
synthesized from the RP curve, feeding the *same* M4 (one engine, two event sources — still not a separate pipeline).

**Honest caveats.** (1) Until the rainfall slice is event-ified, full unification is blocked → **V1 keeps the disjoint sites +
`01`/`02` split** (correct, not a bug). (2) The RP→event bridge for inland is real modeling work (riverine has no event identity
today, [JD-FL-7](#jd-fl-7)). (3) Compound-flood **correlation** (how tightly surge/rain co-occur within a storm) is a published
knowledge gap (Guan 2023, [JD-FL-11](#jd-fl-11)) — the per-event co-sampling handles *occurrence*, but the joint *severity*
dependence stays judgment. (4) Same TIV/curve provisionality as V1.

**Revisit trigger.** Build the LA3 W. Baton Rouge all-three cell (loads the RAFT rainfall slice + event-ifies inland) → realize this
M4 and collapse the notebooks; a free compound-flood dataset appears → replace the manual overlap.

---

## JD-FL-16 · Compound combine's wind leg — **compute it in the hurricane pipeline (Discovery appended as a `cross-link` site), not recomputed in flood; not reused from Everglades** — joined by `event_family_id`

**Date:** 2026-06-20 · **Status:** decided · route-zero scope (pre-build) · The M4 prerequisite for [JD-FL-12](#jd-fl-12); operationalizes the [JD-FL-4](#jd-fl-4) cross-link · *modular / single-source-of-truth*

**Context.** The wind+surge combine ([JD-FL-12](#jd-fl-12)) needs **both** legs at the **same** site. Coastal M1 built the
surge leg at **Discovery Solar Center** (FL) and stamped `event_family_id`, but the hurricane solar cell computed wind at
**Everglades**, not Discovery. So the join partner — per-storm **wind loss at Discovery** — does not yet exist. Three ways to
get it: (a) recompute wind inside the flood pipeline; (b) reuse Everglades (its wind is already built); (c) compute Discovery's
wind in the hurricane pipeline.

**Options weighed.**
- **(a) Recompute wind in flood** — rejected: forks the Holland-field + wind-curve logic into two pipelines (drift, duplication);
  violates "hurricane owns wind" ([JD-TC-4](../hurricane/decisions.md)).
- **(b) Reuse Everglades** (one site for both perils — wind already built, zero hurricane-side work) — rejected as the *proving*
  site: a SLOSH probe shows **Everglades surge is tail-only** — dry at Cat 1-3 (the common storms), flooding only at **Cat 4
  (7.5 ft) / Cat 5 (11.5 ft)**. With the near-site storm mix dominated by Cat 1-3, surge EAL ≈ 0 and surge appears only in the
  deep PML tail → the compound combine would be **wind-dominated across ~99% of the loss curve**, under-exercising the very step
  JD-FL-12 exists to prove. (Kept as an honest *finding*: at an inland-ish (~40 km) coastal site, surge is a Cat-4/5 tail risk.)
- **(c) Compute Discovery's wind in the hurricane pipeline** — **chosen.**

**Decision — (c), by *appending* Discovery to the hurricane end-to-end notebooks as a `cross-link` site.** The hurricane
notebooks already loop over a site list (Hayhurst + Everglades); Discovery is added as a **third row, `site_role =
"cross-link (flood-coastal)"`**, processed by the existing M1→M3 machinery (Holland gust → wind loss), `event_family_id`-stamped.
Flood-coastal M4 reads the per-storm wind loss from `data/hurricane/` and **joins surge ↔ wind on `event_family_id`** (the
JD-FL-12 additive-by-subsystem combine). Two guardrails keep the hurricane narrative intact: Discovery enters by **append, not by
the hurricane screen** (the [JD-TC](../hurricane/decisions.md) site-selection rationale is untouched), and it is **excluded from
the hurricane headline** (EAL/PML story + "end-to-end example" stay **Everglades** + Hayhurst). The genuine new work is hurricane
**M1 + M3** at one site (M0 = a trivial append; M2 solar is spatially degenerate, [JD-TC-2](../hurricane/decisions.md); M4
optional).

**Why.** Keeps wind single-sourced (hurricane-owned), which is exactly what `event_family_id` is for — each peril computes its loss
in its own lane, the shared storm key joins them. Appending-as-a-site is far less code than a sidecar import and reuses the
already-multi-site machinery; the role tag + headline-exclusion carry the honesty. Discovery (real surge from Cat 2 up) makes the
combine *material on both legs*, which Everglades cannot.

**Honest caveats.** (1) The hurricane end-to-end outputs/plots now show **3 sites** (slightly dilutes the pure-Everglades example) —
mitigated by the role tag. (2) Discovery is a **flood-chosen** site sitting in the hurricane pipeline — transparent via
`role="cross-link"`, but it did not pass hurricane's screen. (3) The compound M4 itself lives **flood-side** (it is a flood decision,
JD-FL-12) reading a hurricane input — a deliberate cross-pipeline dependency. (4) Discovery's wind λ is modest (fewer hurricanes than
Miami) — the wind leg is real but smaller than Everglades'.

**Revisit trigger.** A second coastal cell → generalize the append into a hurricane "cross-link sites" list; if the 3-site hurricane
example becomes cluttered → split Discovery into a sidecar notebook (the rejected option B, revivable cheaply).

---

## JD-FL-15 · Surge event definition — **hurricane center within 50 km (tighter than wind's 100 km); λ observed-anchored; SLOSH-MOM worst-case = the single depth conservatism** (don't stack wide-radius over-counting on worst-case depth)

**Date:** 2026-06-20 · **Status:** decided · built in M1 coastal `01_catalog` · the surge analogue of [JD-TC-8](../hurricane/decisions.md) (wind frequency); realizes the [JD-FL-4](#jd-fl-4) `event_family_id` stamp · *basics-spot-on*

**Context.** M1 coastal must turn the hurricane catalog into a surge event stream. Wind ([JD-TC-8](../hurricane/decisions.md))
defines an event as *"center within 100 km at ≥64 kt"* and anchors λ to the observed close-passage rate. **Surge is not
wind:** it is **coastal-local** (a storm passing 100 km offshore pushes little water onto *this* shore), and our depth
source is **SLOSH MOM — a per-category worst-case envelope** ([JD-FL-14](#jd-fl-14)). Reusing the wind definition verbatim
would **over-count** offshore passers *and* — stacked on the worst-case MOM depth — apply **two** conservatisms at once.

**Options.** (a) Reuse wind's 100 km close-passage → over-counts surge events; doubled conservatism vs MOM. (b) Per-track
surge de-rating by landfall proximity → physically ideal, but needs the per-event track→surge model we don't have (the
ADCIRC gap). (c) **Tighten the radius so the *frequency* is honestly surge-relevant, and let SLOSH MOM carry the *one*
intentional depth conservatism.**

**Decision — (c).** Define a surge event as a **hurricane-intensity (≥64 kt) storm whose center passes within `R_surge = 50 km`
of the site** — half the wind radius, because surge attenuates fast offshore (~50 km ≈ the surge-influence reach of a typical
storm). **Same rule on both sides** (the JD-TC-8 rulebook-consistency lesson): RAFT supplies the **severity shape** (category
distribution of qualifying storms → SLOSH MOM depth-by-category over the footprint); **observed HURDAT2 supplies λ** (distinct
hurricanes within 50 km ÷ record years). Each qualifying RAFT storm is stamped with its **`event_family_id`** (the cross-link
M4 joins on, [JD-FL-12](#jd-fl-12)).

**The numbers (Discovery Solar Center, Cape Canaveral FL).** RAFT within 50 km: **117 storms**, cat dist {1:62, 2:33, 3:16,
4:5, 5:1}. Observed (HURDAT2, 173 yr): **5 close-passages → λ ≈ 0.029/yr**; landfalls within 50 km = 4 (λ ≈ 0.023/yr) — the
two nearly agree at tight radius, confirming that at 50 km the *passage-vs-landfall* distinction collapses (so the
rulebook-consistent close-passage anchor is also surge-appropriate here). Discovery's λ is **~6× below Everglades' 0.19/yr** —
central-FL Atlantic takes far fewer direct hits than Miami; correct, not a bug.

**Why.** Tight radius keeps the **frequency** honest (only genuinely surge-relevant storms count) while SLOSH MOM provides the
**single, intentional** depth conservatism — avoiding the doubled-conservatism trap of wide-radius × worst-case depth. It reuses
the JD-TC-8 machinery (same haversine close-passage screen, same observed-anchored λ), so frequency and severity compose
consistently, and it switches on the `event_family_id` stamp exactly as JD-FL-4 reserved.

**Honest caveats.** (1) **Small observed sample** — 4–5 storms anchor λ (Cape Canaveral gets few direct hits); the rate is
coarse (sensitivity-test `R_surge` ∈ {40, 75} km — 3→7 landfalls). (2) `R_surge = 50 km` is a **screening choice**, not a
derived surge-reach (which depends on storm size/coast geometry — the ADCIRC gap again). (3) **Every qualifying storm of
category C gets the *same* worst-case MOM depth** regardless of its exact track — the JD-FL-14 envelope caveat, carried. (4)
Category is taken at **closest approach to the site** (the surge-relevant intensity), not lifetime peak. (5) **High-tide MOM
scenario** (surge on high tide — conservative).

**Revisit trigger.** ADCIRC per-event surge → drop the MOM worst-case and the radius proxy together (re-validate λ and depth);
a site with too few observed storms to anchor → a regional landfall-rate regression (à la flood's NSS); `R_surge` sensitivity
moving the headline materially → report the band.

---

## JD-FL-15 · Pluvial ponding — **ground `f` per site from 1 m lidar (drop the 0.40 guess); the headline flips to riverine-dominated**

**Date:** 2026-06-20 · **Status:** decided/built (the floor) · **Backed by** [`pluvial_depth_method_recommendation.md`](../../../jdocs/pluvial_depth_method_recommendation.md) (Barnes 2021; Wu 2019; Fathom/First Street rain-on-grid survey) · Grounds [JD-FL-9](#jd-fl-9)/[AFL-P2](assumptions.md).

**Context.** Pluvial's exposure `f` (the ponding fraction) was a **flat guess (0.40)** — the headline's softest input, and it made the combined flood loss **pluvial-dominated** (EAL 0.27%). We grounded it with real data.

**Decision (built).** Compute `f` **per site** from **USGS 3DEP 1 m lidar**: snap the footprint, fetch the tile
(`/vsicurl`, windowed), run a **closed-depression (sink-fill) analysis** → `f` = depression fraction, `d_cap` = the
depression depth, and **cap** the wet depth at `d_cap` (water can't pond deeper than the sink — fixes the `r·Q/f`
explosion at small `f`). Per-site, cached, with a documented fallback where lidar is absent. Wired into
`m1_catalog/pluvial`; M2/M3/M4 flow through.

**Result — the dominance flips.** Elizabeth `f`: **0.40 guess → 0.016 measured**; pluvial EAL **0.27% → 0.003%**
(~90× drop); **combined headline EAL 0.27% → 0.15%, now RIVERINE-dominated** (PML back to the BLE-anchored 2.62/4.46%;
the wide combine envelope collapses to 0.15–0.16 — it was also an `f` artifact). The well-anchored, HWM-validated
riverine layer now drives the headline. *"Pluvial dominates" was an artifact of the 0.40 guess.*

**What the research settles (the backbone).** The leading models (Fathom, First Street) all use **rain-on-grid with
soil-based infiltration and NO retention fraction, NO curve number** for pluvial; **no free calibrated pluvial-depth
product exists** → the screening estimate must be **modeled + bounded, not borrowed**. So:
- **`r` (retention) is a lumped artifact → drop it** (replace with a mass-conserving terrain pour). *Still present in
  the code's water-limited branch; dormant at Elizabeth (terrain-capped); to be removed by the Rank-1 upgrade.*
- **`CN` is real + groundable** (USDA SSURGO soil + NLCD → NRCS TR-55). Dormant at Elizabeth (capped); matters at
  **water-limited** sites. Currently still assumed (CN=80).
- **Our method = the Rank-2 *floor*** — a defensible *settled, on-site* lower bound (the terrain-limited special case).

**The agreed upgrade path (not yet built).**
1. **Rank-1 — terrain volume-pour:** ground `CN` (SSURGO+NLCD) → pour runoff volume `Q` into the lidar depression
   hierarchy (fill-spill-merge) → `(depth, f)` emerge, **`r` gone**; **+ one-bucket level-pool routing** over the
   short-duration hyetograph for the **storm-peak** depth (the loss-relevant one; the pour gives only *settled* depth);
   **+ DEM buffer** for **run-on**; report a **floor→ceiling range** + the regime ratio **ρ = V_runoff/S_dep**.
2. **Endpoint — SFINCS** rain-on-grid (open-source, minutes-scale) for high-TIV / water-limited sites.

**Honest caveats.** Closed-depression `f` is a **settled, lower-bound** depth (misses storm-peak surcharge + run-on) —
**fine at Elizabeth** (ρ≪1, sloped, drains fast → narrow band) but a floor at flat, poorly-drained sites (where pluvial
actually bites). Bare-earth lidar ≠ engineered grading. Damage curve still medium-confidence (shared with riverine).

**Revisit trigger.** Build the Rank-1 volume-pour (for water-limited sites / national rollout); ground `CN` (SSURGO);
a free pluvial depth grid (FFRD national) → sample it. Escalate to SFINCS when ρ≫1 or pluvial approaches riverine.

**Update (2026-06-20) — ported to flood × WIND.** The lidar `f`+`d_cap` machinery is now applied to the wind cell's
pluvial, **per node** (each turbine pad + the substation) rather than per compact footprint — a wind lease is a sparse
~88 km² cloud, so one lease-wide raster is neither tractable nor meaningful; each pad gets its own 1 m closed-depression
window (uplands `f≈0.005`, valley substation `f≈0.018`, `d_cap` ~0.07–0.09 m). **Result:** the grounded `d_cap` sits
**below the pads** → **floor pluvial = 0 at every node** (the flat `f=0.40` had given a 500-yr substation trace); marginal
pluvial EAL **0.0007% → 0.000%**, headline unchanged (riverine-dominated since [JD-FL-W7](#jd-fl-w7)). **Regime: Green
River is WATER-LIMITED** (ρ = Q/(f·d_cap) up to ~490 ≫ 1) — exactly the flat-river-valley case where the floor
under-states. **Decision: report the floor + the no-drainage ceiling bound + the ρ flag; DEFER the Rank-1 volume-pour
for wind** — because even the ceiling (Q ≤ 0.16 m) is pad-shed, and the one run-on-receiving node (the valley
substation) is **already riverine-flooded 0.88 m**, so worse-source-wins ([JD-FL-11](#jd-fl-11)) makes pluvial
immaterial to the headline regardless of regime (Rank-1's payoff is at *pluvial-driven* water-limited sites, not this
riverine-dominated one). Same outcome shape as solar (grounding `f` removes a soft guess and confirms riverine
dominance), reached by a different route (wind was already riverine-dominated via the collector).

---

## JD-FL-12 · Wind+surge compound combine — **additive-across-subsystems, max-within-shared** (= JD-FL-11's φ-formula read at φ≈0)

**Date:** 2026-06-20 · **Status:** decided · route-zero scope (pre-build) · The M4 cross-peril step for coastal `[C]`; the genuinely new work the [`event_family_id`](#jd-fl-4) link exists for · *standard-interface-not-standard-physics*

**Context.** Coastal surge is flood's `[C]` sub-peril ([JD-FL-1](#jd-fl-1)), but it rides the **same storms** as hurricane
wind. M4 must turn a storm's **wind loss** (hurricane solar cell) and its **surge loss** (this cell) into one annual loss
**without double-counting** — the Flood-Data-Ref's repeated instruction (§5/§7/§8: *"avoid double-counting when a hurricane
drives both… treat the cross-peril overlap manually for now"*). The question is whether this is flood's worse-wins **max**
([JD-FL-11](#jd-fl-11)) or something else.

**Options.** (a) **max** (mirror JD-FL-11) — under-counts: wind and surge destroy *different* equipment. (b) **pure additive**
— over-counts the few components both perils can kill, and can exceed TIV. (c) **additive-across-subsystems with max on the
shared slice** — the physically-resolved middle.

**Decision — (c), which is JD-FL-11's own envelope formula at low φ.**
1. **Occurrence = comonotonic, one storm.** One annual draw reads **both** losses for the **same** storm via `event_family_id`
   (identical to JD-FL-11 part 1 — the storm produces a gust field *and* a surge depth at the site simultaneously).
2. **Severity = subsystem-resolved.** Wind and surge are **different mechanisms on different subsystems** — wind = uplift/debris
   on the *above-ground structure* (modules, racking, trackers); surge = inundation of the *at-grade electrical* (inverters,
   combiner boxes, DC/AC cabling, pad transformers, foundation scour). So: wind-only subsystems take wind damage, surge-only
   take surge damage, **shared** subsystems take `max(wind, surge)`, **sum across subsystems, capped at TIV**.
3. **This is `L = max + (1−φ)·min`** (JD-FL-11's recorded envelope) with **φ = shared-subsystem fraction**. The two combines are
   the *same formula at opposite ends*: riverine+pluvial = same water/same equipment → **φ≈1 → worse-wins**; wind+surge =
   different mechanisms/different subsystems → **φ≈0 → additive**. **Pure-additive (φ=0) is the upper envelope, worse-wins
   (φ=1) the lower** — same spread discipline as JD-FL-11, mirror-imaged.

**Why.** It is not a new ad-hoc rule — it is the φ knob the repo already adopted, read at the other end, so it stays internally
consistent and Total-Loss-combinable. `max` would say a storm that rips off every module *and* drowns every inverter costs the
same as the worse alone (false); pure-add double-counts shared components and can exceed TIV (false). Subsystem-resolved is the
only reading that double-counts nothing and loses nothing. The one input — the wind-vs-surge subsystem TIV split (φ) — already
lives in the capex-weighting inside `flood_solar_asset_capex_weighted.json` + the hurricane M3 curve.

**Honest caveats.** (1) φ is a **subsystem-TIV judgment**, not a measured joint-damage observation — hence the additive↔max
envelope is reported, not a point. (2) Surge depth is **category-based** (SLOSH MOM, [JD-FL-14](#jd-fl-14)) → the surge leg is
screening-grade. (3) Wind and surge are **physically correlated within a storm** (a strong storm brings both); comonotonic
co-sampling captures the occurrence correlation but assumes the *conditional* severities are read at the same storm — defensible
given the shared `event_family_id`. (4) **Differs from convective_wind's additive on purpose and from flood's max on purpose** —
both are the same φ-formula at different overlap; intentional, documented.

**Revisit trigger.** A measured wind×surge joint-damage dataset → replace φ judgment; ADCIRC per-event surge ([JD-FL-14](#jd-fl-14))
→ the surge leg sheds its category-envelope caveat; sub-asset subsystem geometry → drop φ for true per-component max-then-sum.

**Update (2026-06-20) — built exact per-subsystem, NOT the asset-level φ-blend.** On building M4 it turned out **both** curves
are already subsystem-resolved (the hurricane×solar wind curve carries `PV_ARRAY/MOUNTING/SUBSTATION` weights; the flood×solar
surge curve carries `PV_ARRAY/INVERTER/SUBSTATION/ELECTRICAL/CIVIL`). So the combine is done **exactly**: `combined_DRᵢ =
max(wind_DRᵢ, surge_DRᵢ)` per subsystem, `asset_loss = Σᵢ TIVᵢ·combined_DRᵢ`. The `max` is automatic for single-peril
subsystems (the other DR is 0 → genuinely additive across them) and dedups only the **two shared** subsystems **PV_ARRAY +
SUBSTATION (~0.40 of a reconciled canonical TIV split)**. So the asset-wide φ **collapses to a max-vs-add band on just those two
subsystems** — `max` = headline, `min(1, wind+surge)` = upper band — far tighter and better-located than a whole-asset φ. The
asset-level φ-blend is **demoted to the fallback** for when one peril's curve is *not* subsystem-resolved. **Result (Discovery,
M4):** compound **EAL 1.15%** (band 1.28%), **PML500 62.9%** (band 66.7%) — materially above wind-only (EAL 0.86% / PML500 26.7%)
*and* surge-only, confirming both legs contribute (the JD-FL-16 site choice). The within-shared-subsystem overlap (same modules hit
by wind-uplift vs submersion?) is the only residual assumption — carried by the narrow band.

---

## JD-FL-13 · Coastal sites — **Hayhurst (low, reused, zero-surge) + a screened coast-front solar high site**

**Date:** 2026-06-20 · **Status:** decided · route-zero scope (pre-build) · Mirrors [JD-FL-3](#jd-fl-3) (solar) / [JD-FL-W1](#jd-fl-w1) (wind) on the coastal sub-peril

**Context.** Coastal needs a low/high pair like every other cell. Hurricane's high site (**Everglades**) is **~40 km inland** —
it takes wind but little surge — so it cannot serve as the coastal high site (the handoff's flag). A genuine **coast-front** solar
asset is required.

**Decision.** **Low / baseline = reuse Hayhurst Texas Solar** (Culberson Co. TX, Chihuahuan desert) — a *legitimate* zero-surge
control (inland desert, no coastline) and the same asset as hail / wildfire / flood-R+F (cross-peril coherence; owner preference).
**High / proving = a new M0 surge-exposure screen** over Gulf/Atlantic coastal solar (FL/TX/LA/NC), ranked on SLOSH surge depth /
coastline proximity, exact EIA asset confirmed in M0 — same screening method as JD-FL-3, metric swapped to **surge exposure**.

**Why.** Reusing Hayhurst preserves the asset coherence axis and is a true dry baseline (no surge can reach it → exactly-zero
coastal loss, like its λ=0 hurricane control). The national screen keeps the coast-front high site honest and reproducible.

**Honest caveats.** (1) Hayhurst's coastal loss is a **structural zero** (no coastline), not a modelled small number — flagged,
defensible. (2) The high site must also have a **hurricane-cell wind loss** to exercise the JD-FL-12 compound combine — so the
screen prefers a coast-front site already inside the hurricane catalog's footprint (a storm-exposed Gulf/Atlantic asset).

**Revisit trigger.** The screen's top coast-front asset lacks SLOSH/DEM coverage → next candidate; an owner-portfolio coastal
solar asset appears → prefer it for realism.

---

## JD-FL-14 · Coastal surge spine — **SLOSH-only for V1** (category-based, conservative, source-tagged); **CHS/ADCIRC is the recorded one-place upgrade**; build standalone first, then the compound combine

**Date:** 2026-06-20 · **Status:** decided · route-zero scope (pre-build) · Realizes the [JD-FL-4](#jd-fl-4) `event_family_id` hook; the coastal analogue of [JD-FL-6](#jd-fl-6) (riverine) / [JD-FL-9](#jd-fl-9) (pluvial) · Source: [Hazard-Data-Ref-Flood](../../../jdocs/Hazard_Data_Reference-Flood.md) §5/§7/§8

**Context.** Coastal `[C]` needs a free, self-serve surge **depth** source and an event model. The Flood-Data-Ref is explicit:
**SLOSH is the public coastal-surge layer, shared with hurricane** (§5: *"the same layer as the hurricane surge grid — reuse it,
don't rebuild"*), and **no public product jointly models the compound case** (§8: *"treat the cross-peril overlap manually for
now"*).

**Decision.**
1. **Spine = NOAA SLOSH MOM** (Maximum-of-MOMs), category-based surge depth at the site (`nhc.noaa.gov/nationalsurge`, free,
   public domain). Each storm in the hurricane catalog passing the coastal site is assigned its **category** (from RAFT
   `peak_vmax_kt`, `tc_m0_raft_summary.parquet`) → SLOSH MOM surge depth-at-category. M1/coastal emits the **same depth-at-RP
   schema** riverine/pluvial do ([JD-FL-10](#jd-fl-10)), tagged `sub_peril="coastal"` **and `event_family_id`** stamped (the
   cross-link). M2/M3 reuse flood depth→damage unchanged.
2. **Frequency = the [JD-TC-8](../hurricane/decisions.md) recipe, reused verbatim** — observed-anchored λ (HURDAT2 close-passage
   rate, by category) × catalog severity shape. **Independent validation anchor:** NOAA Tides & Currents exceedance-probability
   water levels (Flood-Data-Ref §3) — the coastal analogue of NRI (riverine) / ASCE 7-22 (hurricane).
3. **Sequencing = standalone first, then compound.** Build coastal surge M0→M4 **standalone** (a clean, validated surge-only
   loss number), **then** add the wind+surge compound combine ([JD-FL-12](#jd-fl-12)) as the **M4 capstone** — the Flood-Data-Ref's
   *"handle each separately, then combine on the shared metric"* (§5).
4. **V1 = SLOSH-only, with a source-tagged seam for the CHS upgrade.** A live probe (2026-06-20) confirmed an engineering-grade
   free alternative exists and is reachable — **USACE Coastal Hazards System (CHS)**, ADCIRC/STWAVE, 20,000+ save points,
   return-period (AEP) surge at 1–10,000 yr, HDF5/CSV download (`chs.erdc.dren.mil` → `200`; SACS open-data `200`), **covering all
   our candidate coasts** (TX/LA via the Gulf studies + Sabine-to-Galveston; FL/NC via SACS). **We deliberately ship SLOSH-only for
   V1 anyway** — one universal, consistent method everywhere it's relevant, no cross-site mixing bias, simplest honest first cut —
   and make the depth step **source-tagged** (`depth_source ∈ {SLOSH, CHS}`) so CHS slots in later as a **one-place change** (the
   StreamStats→BLE seam of [JD-FL-6](#jd-fl-6), coastal edition). M2/M3/M4 read "depth at the site" and never see the source.

**Why.** SLOSH is the only **free, reference-mandated, universally-available** coastal depth source (CHS is study-by-study; SLOSH
covers the whole hurricane-surge zone + HI/PR/USVI), and reusing it across both perils is what prevents the old-model double-count
(separate Hurricane + Coastal-Flood rows). SLOSH-only keeps V1 **simple and internally consistent** (one method → the "two values
across a mixed portfolio" problem never arises) and is in keeping with how the rest of the pipeline shipped — honest screening-grade
first, hardened through a pre-wired seam ([JD-FL-7](#jd-fl-7)). The standalone→compound order gives a defensible checkpoint before
the genuinely new combine, and keeps coastal Total-Loss-combinable like every other sub-peril.

**Honest caveats — the costs we are knowingly accepting.** (1) **Category worst-case → loss reads HIGH.** SLOSH MOM is a
**per-category worst-case envelope, NOT a per-event footprint** (Hazard-Data-Ref §5/§7) — every category-N storm gets the *same*
worst-case surge regardless of track/forward-speed/tide, so the surge leg is **conservative/over-stated** and **screening-grade**
(same posture as the Zone-A bathtub, [JD-FL-W4](#jd-fl-w4)). (2) **Coarse loss-curve shape → EAL soft** (one depth per category
blurs the frequent low-end that drives EAL; PML firmer than EAL, as [JD-FL-7](#jd-fl-7)). (3) **Weaker site-to-site discrimination**
(worst-case washes out real differences CHS would resolve) — matters when ranking a portfolio. (4) These are the *accepted* price of
SLOSH-only; CHS removes (1)–(3) where it exists and is the documented upgrade. (5) **Datum** (SLOSH MHHW vs DEM NAVD88) must be
reconciled or depths are meaningless (§7); **SLR** horizon excluded in V1 (static present-day).

**Revisit trigger — CHS is the named upgrade.** Adopt **CHS depth-at-RP (ADCIRC/STWAVE)** where a save point covers the asset →
swap the source-tagged depth step (one place), **keeping SLOSH as the universal fallback + running it at CHS sites once as an
overlap cross-check to size the SLOSH-vs-CHS bias** (tagged, one headline value per site — CHS where present, else SLOSH); re-validate,
loss will move (down — SLOSH runs high). Other triggers: a coastal asset with no SLOSH basin **and** no CHS → NOAA Coastal Flood
Exposure Mapper bathtub; per-storm wind↔surge correlation needed → run ADCIRC on the RAFT catalog itself (CHS's own synthetic storms
don't map 1:1 to ours); SLR-aware horizon → add the Tides & Currents + SLR overlay.

---

## JD-FL-W7 · Wind substation — **pick the farm's OWN collector (in-hull `substation=generation`), not the nearest mapped one**; the real Green River collector **floods** → headline EAL 0.31% → **1.27%**

**Date:** 2026-06-20 · **Status:** decided · **Corrects [JD-FL-W5](#jd-fl-w5)'s substation** (and supersedes the "AFL-W5 collapsed → dry → no load-bearing assumption" claim) · *basics-spot-on / portfolio-scalable*

**Context.** JD-FL-W5 reported the Green River substation as "real and **dry**" — the nearest mapped substation to the
turbine-cloud centroid (HIFLD-primary, OSM supplying the name "**Big Sky Wind LLC Substation**"), on high ground → ~0
loss → headline **EAL 0.31% / PML500 3.2%**, with the note that *one unnamed 138 kV west-edge substation does flood
(0.88 m) — role unconfirmed*. Confirming that flag is this decision.

**The finding (ownership, evidence-backed).** The flooding west-edge substation **IS Green River's own collector**, and
the node the model was using is the **adjacent Big Sky Wind farm's** collector — a wrong-substation bug:
- **Two different projects share this corridor.** USWTDB: **Green River** = 74 turbines, 2019, lon −89.648…−89.461;
  **Big Sky Wind** = 114 turbines, 2011, 240 MW, lon −89.520…−89.318 (a separate project — BlackRock→Vitol→Potentia).
  Their footprints **overlap only in the east**.
- The model's node ("Big Sky Wind LLC Substation", 41.5989, −89.4564) sits **inside Big Sky's footprint, just east of
  Green River's hull** (`in_hull = False`) — it is the *neighbour's* collector, dry on high ground (3DEP 242 m, outside SFHA).
- Green River's **own** collector is the OSM **`substation=generation`** 138 kV node at (41.6074, −89.6406), **inside
  Green River's hull** (`in_hull = True`, nearest GR turbine 0.30 km), with a co-located `substation=transmission`
  138 kV POI switchyard + gen-tie lines to a **ComEd** 138 kV line (one OSM changeset — the textbook wind-farm
  interconnection). It sits in the river valley (3DEP 197 m, **inside the SFHA**) → it **floods**: 0.56 m @ 10-yr →
  **0.88 m @ 100-yr** → 1.00 m @ 500-yr (the bathtub depth that exactly reproduces the flagged 0.88 m).

**Decision — two parts.**
1. **Use the real collector** as the substation node (riverine M0 geometry → M1→M4 re-run). Because the collector
   carries ~9% of TIV on a steep curve and floods from the 10-yr on, the headline rises **EAL 0.31% → 1.27% /
   PML100 2.8% → 10.9% / PML500 3.2% → 11.4%** (collector ≈ **75% of EAL**). Bracket kept: **turbines-only floor**
   (collector excluded) = the old 0.31% / 3.2% (with-vs-without). NRI multiple **~3× → ~13×** Lee Co. avg — still
   order-consistent for a 60%-in-floodplain site whose collector sits in the valley bottom.
2. **Fix the selection *method* (the production point).** Replace "nearest mapped substation to the cloud centroid"
   (HIFLD-primary — HIFLD has no substation *type* and no farm identity, so it can grab a neighbour's) with a
   **portfolio-scalable rule that identifies a farm's OWN collector**: prefer the OSM **`substation=generation` node
   INSIDE the turbine hull** (a plant's own collector, by definition; a neighbour's falls outside the hull), with
   fallbacks **gen-adjacent (<0.6 km of this farm's turbines) → any in-hull substation (generation-first) →
   HIFLD-in-hull (containment as the guard) → centroid**, plus a **name-mismatch guard** that flags a chosen
   substation named for a different plant. The two facts a collector always satisfies — **type = generation** and
   **inside the lease** — are exactly what containment + the OSM tag encode.

**Why.** The collector is the single highest-value low-lying node, so the *wrong* substation silently mis-states loss
by ~4× — and "nearest-to-centroid" is not safe wherever farms cluster (common in good wind regions). Containment +
the generation tag is general, automatable at any CONUS asset, and self-correcting (the name-mismatch guard surfaces
the exact failure that happened here).

**Honest caveats.** (1) The collector depth is still the **Zone-A bathtub** (medium-low confidence, JD-FL-W4) — only
now it's applied at the *right* node. (2) The transmission POI switchyard (dry here) is the grid owner's, not project
TIV — excluded by design (generation-preferred). (3) Where OSM lacks a `generation` tag, the method degrades to
HIFLD-in-hull (containment still rejects neighbours, but type can't be confirmed) — flagged. (4) The 138 kV
collector's `substation=generation` tag is OSM-sourced; HIFLD here carries no voltage/type (all 0/UNKNOWN), so OSM is
the discriminating layer.

**Revisit trigger.** A farm with no OSM-mapped generation substation (HIFLD-only) → confirm the in-hull pick by a
one-line/interconnection check; a detailed BFE / StreamStats+HAND raster at Green River → swap the collector's depth step.

---

## JD-FL-W6 · Wind pluvial — **per-node pad-gated Atlas-14 ponding** + JD-FL-11 combine; **confirmed negligible for wind** (riverine-dominated)

**Date:** 2026-06-19 · **Status:** decided · Brings the wind cell to **parity with flood × solar** — realizes [JD-FL-10](#jd-fl-10) (catalog fork) + [JD-FL-11](#jd-fl-11) (combine) on the wind asset, with [JD-FL-9](#jd-fl-9)'s pluvial method applied **per node**.

**Context.** The wind cell shipped riverine-only. Pluvial (intense-rainfall sheet ponding) is the second inland
sub-peril; solar already built it (JD-FL-9) and combines it with riverine (JD-FL-11). Wind needed the same — but
wind is a **sparse point cloud on high ground**, not solar's compact areal footprint, so the solar *areal* pluvial
doesn't transfer directly.

**Decision — three parts:**
1. **Fork M1** (`m1_catalog/{riverine,pluvial}/`, matching solar / JD-FL-10) — the existing riverine catalog moved
   into `riverine/`; the new **pluvial** catalog samples **per node** (each turbine pad + the substation), emitting
   the **same per-node depth schema** the riverine bathtub does, so M2/M3 run one code path over both and M4 combines.
2. **Per-node pad-gated ponding.** Reuse the solar pluvial machinery (Atlas 14 24-hr rainfall → SCS-CN runoff CN=80,
   `r=0.5`, `f=0.4` → conditional sheet depth `pond = r·Q/f`), but — unlike riverine's SFHA gate — pluvial is **not
   floodplain-gated** (rain falls everywhere); the **raised pad is the gate**: node depth = `max(pond − pad, 0)`
   (turbine pad 0.30 m, substation 0.15 m; AFL-W6). The 10 m DEM is again *not* used for micro-ponding (its σ is the
   site slope — same call as solar).
3. **Combine at M4 worse-source-wins** (JD-FL-11, unchanged) — co-sampled comonotonic, headline `max(riverine,
   pluvial)`, additive-capped envelope recorded.

**Why / the finding (tested, not assumed).** **Pluvial is even smaller than riverine for wind, and the combine is
riverine-dominated.** Green River 100-yr ponding `pond ≈ 0.14 m`, 500-yr `≈ 0.21 m` — **below the 0.30 m turbine
pad**, so **every turbine sheds it (pluvial turbine loss = 0 at every RP)**. Only the lower-pad (0.15 m) **substation**
catches a **trace** (0.055 m at 500-yr → ~0.1% of TIV). So the combined headline is **unchanged** from riverine-only
(pluvial marginal EAL **0.0007%**) — the pluvial-negligible finding stands. *(The absolute riverine-only headline
cited here at build time was EAL 0.31% / PML500 3.16%; that has since risen to **EAL 1.27% / PML500 11.4%** under
[JD-FL-W7](#jd-fl-w7) — the substation correction — but pluvial remains negligible regardless.)* This is the clean
asset contrast to solar, where the headline was *pluvial*-dominated (flat compact footprint ponds): for wind the
**raised pad, not the floodplain, sheds the rain**.

**Honest caveats.** (1) Pluvial has **no depth anchor** (JD-FL-9 blind spot) — screening-grade — but it's negligible
here, so it doesn't move the headline. (2) **Shepherds Flat (baseline) is outside NOAA Atlas 14 coverage** (the
Pacific NW is Atlas 2, not Atlas 14) → its pluvial is set to **0** (a low-rainfall dry control, *not* a true zero);
Atlas 2 / Atlas 15 is the upgrade. (3) Applying the *conditional* (concentrated) ponding to every node is the
conservative no-drainage reading.

**Revisit trigger.** Atlas 15 (climate-aware) / a free pluvial depth grid → re-source the rainfall; Atlas 2 pull →
give the PNW baseline real pluvial; a deeper-rainfall wind site where `pond > pad` → pluvial would start to bite.

---

## JD-FL-11 · Sub-peril combine — **co-sample (comonotonic) + worse-source-wins headline; additive-capped as the recorded upper envelope** (research-confirmed)

**Date:** 2026-06-17 · **Status:** decided · The M4 combine for JD-FL-10 · **Backed by [`flood_subperil_research_result.md`](../../../jdocs/flood_subperil_research_result.md)** (Bates 2021; FFRD/HEC-WAT; Guan 2023; Ward 2018; Oasis LMF).

**Context.** With riverine + pluvial both built, M4 must turn two per-sub-peril loss curves into one annual flood loss.
Both are **rain-driven** → positively correlated (one storm often causes both); and they act through the **same
depth-damage curve on the same equipment**. The **old model** treats Riverine/Flash/Coastal as **independent perils
and sums** them — which **double-counts** the shared storm and mis-states occurrence dependence.

**Decision.** Two parts, both research-endorsed:
1. **Occurrence = co-sample comonotonic.** Draw one annual AEP `u ~ U(0,1)` per year; read **both** sub-peril loss
   curves at `u` (one shared storm — matches FFRD shared-storm logic / RMS single-event identity).
2. **Severity = worse-source-wins (per-location max depth → one damage eval).** The year's flood loss =
   **max(loss_riverine(u), loss_pluvial(u))** — physically correct for **shared ground** (a component drowns once; this
   is exactly what the Bates 2021 / Fathom / First Street engine does: *"max depth at each pixel"*). This is the
   **headline number** (single-valued, like every other peril → combinable into Total Loss). Metrics on the
   **combined per-year vector** (never summed marginals — Oasis LMF; comonotonic-sum is the upper bound, not the answer).
3. **Recorded envelope (not used in the math):** the general rule is `L = max + (1−φ)·min(L_r, L_p)`, φ = shared-ground
   overlap. For a **compact, flat solar footprint where both sources pond on the same low ground (Elizabeth), φ skews
   high (0.6–0.8)** → worse-wins (φ=1) is the defensible **headline**; **additive-capped** (φ=0, `min(TIV, L_r+L_p)`)
   is the **upper sensitivity bound** reported beside it. Keep per-sub-peril marginals.

**Why.** Worse-wins is the research's recommended default *when overlap is high* (our case) and avoids double-counting
the same drowned equipment; co-sampling is correlation-honest; single-valued headline keeps flood consistent +
Total-Loss-combinable; the envelope carries the honest spread without false precision in φ.

**Honest caveats.** (1) **[Superseded by [JD-FL-15](#jd-fl-15)]** — the headline was *pluvial-dominated* only while `f`
was the 0.40 guess; with `f` lidar-grounded, **pluvial collapses and the headline is riverine-dominated** (EAL 0.15%),
and the combine **envelope tightens to ~nothing** (the wide envelope was an `f` artifact — the combine rule barely
bites when one sub-peril is negligible; it would re-widen at a flat, pluvial-heavy site). (2) **Differs from convective_wind on purpose** —
wind *adds* its sub-perils (tornado/strong-wind hit *different* subsystems); flood *maxes* (same water, same equipment).
Intentional, not a bug. (3) Inland riverine↔pluvial dependence is a **published knowledge gap** (Guan 2023) → φ is
judgment, hence the reported envelope.

**Revisit trigger.** Sub-asset spatial-exposure data → drop the φ heuristic for true per-location max-then-sum; a
measured riverine↔pluvial copula → replace comonotonic occurrence; pluvial depth anchor → narrow the envelope.

---

## JD-FL-10 · Sub-peril structure — **fork the catalog (M1) per sub-peril; share M2/M3; combine at M4**

**Date:** 2026-06-17 · **Status:** decided · Realizes the [JD-FL-4](#jd-fl-4) family hooks · Sets the pluvial/coastal layout.

**Context.** Riverine shipped as a single implicit cell. Adding **pluvial** (then coastal) needs a folder/data shape.
The convective_wind precedent forks sub-perils at **M2** (tornado vs strong-wind *couple* differently, share M0/M1).
Flood is different: its sub-perils differ in **data + footprint** (BLE/streamflow vs Atlas-14 rainfall vs SLOSH surge)
but share **one damage driver — inundation depth** (the reference: *"handle each separately, then combine on the
shared depth metric"*).

**Decision.** Fork **at the catalog (M1)**, not at M2 and not a top-level `flood/riverine/` tree:
```
flood/ m0_input_data/                    # shared site geometry + DEM
       m1_catalog/ riverine/ 01_catalog  # BLE + streamflow densification  (built)
                   pluvial/  01_catalog  # NOAA Atlas-14 rainfall → ponding depth
       solar/ m2_coupling/ m3_damage/    # SHARED — depth→damage is identical per sub-peril
              m4_loss_metrics/           # reads ALL sub-peril catalogs, COMBINES (per JD-FL-?, the combine rule)
```
Each catalog emits the **same depth-at-RP schema** tagged `sub_peril`; M2/M3 process whatever rows arrive; M4 combines.

**Why.** Matches flood's actual shape (diverge at the data, re-converge at depth→damage) and the JD-FL-4 hooks
(`sub_peril` key already in every manifest). Avoids duplicating the shared M2/M3/M4 framework. Coastal slots in the
same way later — with its catalog **shared from hurricane** + the `event_family_id` link switched on (its extra twists).

**Revisit trigger.** A sub-peril whose *coupling* (not just data) differs would justify an M2 fork too (none yet).

---

## JD-FL-9 · Pluvial depth source — **NOAA Atlas 14 rainfall → SCS-CN runoff → DEM-hypsometry ponding** (no free pluvial grid exists)

**Date:** 2026-06-17 · **Status:** decided · The pluvial analogue of [JD-FL-6](#jd-fl-6) (riverine BLE). Reference-aligned (Flood-Data-Ref §2/§5/§7).

**Context.** Pluvial = intense-rainfall surface flooding — *"the blind spot"* (Flood-Data-Ref §7): FEMA NFHL
**under-maps it ~3×** (Wing/Bates 41M vs FEMA 13M in the 1% floodplain), and — unlike riverine — there is **no free
pluvial *depth* product** to anchor to (FFRD pilot-only; First Street/Fathom commercial). So we have easy *frequency*
(rainfall) but must *model* depth with **nothing observed to calibrate against** (the inherent weakness, flagged).

**Options.** (a) Atlas-14 rainfall → a **rainfall-driven depth model** on our 3DEP DEM (runnable, approximate);
(b) full **HEC-RAS rain-on-grid** 2-D (gold standard, not runnable here — the HAND problem again); (c) **FFRD** (pilot,
not at site) / **commercial** (paid, excluded); (d) NWC-FIM flash (HAND — more flash-riverine than pure pluvial).

**Decision — option (a), the free reference-recommended method.**
1. **Frequency = NOAA Atlas 14** point precipitation-frequency (24-hr depth at 10/25/50/100/500-yr; PFDS CSV — probed,
   reachable: Elizabeth 100-yr 24-hr ≈ 13.8″). *The pluvial frequency backbone, as StreamStats is for riverine.*
2. **Rainfall → runoff = SCS Curve-Number** (CN≈80, graded solar open-space/soil-C): `Q = (P−0.2S)²/(P+0.8S)`,
   `S=1000/CN−10` — the net runoff depth (the flood water available to pond).
3. **Runoff → ponding depth = DEM-hypsometry bathtub:** pour `Q` over the footprint's 3DEP elevation distribution
   (≈ Normal(μ,σ) from M0's `elev_mean`/`elev_std`); solve the ponded water surface so footprint-average depth = `Q`
   (the **conservative no-drainage** limit) → `inund_frac = Φ((WSE−μ)/σ)`, `conditional_depth = Q/inund_frac`.
   Emits the **same depth-at-RP schema** riverine does (JD-FL-10), `sub_peril="pluvial"`.

**Why.** The only **free, self-serve, reference-endorsed** pluvial path (Flood-Data-Ref §5: *"drive a rainfall-based
model from Atlas 14… or use FFRD/commercial"*). Reuses the DEM M0 already pulled; keeps us hazard-first.

**Honest caveats.** (1) **No depth anchor** (vs riverine's BLE) → pluvial depths are inherently **softer/wider** — the
reference's blind-spot, not a shortcut. (2) **No-drainage** assumption (all runoff ponds in place) → an **upper bound**;
real grading/drainage reduces it (the pluvial analogue of riverine's onset-depth — sensitivity-test). (3) `CN` and the
24-hr duration are assumptions. (4) Atlas-14 LA Vol-9 is stationary + aging (§8).

**Revisit trigger.** **Atlas 15** (climate-aware, CONUS ~Sept 2026) for the rainfall input; **FFRD** national / a free
pluvial depth grid → swap in and demote the rainfall-runoff model; commercial budget → Fathom/First-Street pluvial.

---

## JD-FL-W5 · Ground the wind RP curve in a **USGS gauge flow-frequency** (replaces the flat 500-yr freeboard) + **FEMA NRI** external validation

**Date:** 2026-06-18 · **Status:** decided · Hardens [JD-FL-W4](#jd-fl-w4)'s RP rises · the wind analogue of [JD-FL-8](#jd-fl-8)

**Context.** JD-FL-W4 shipped the 1% surface from the bathtub but set the **500-yr by a flat +0.6 m freeboard guess**
(AFL-W7) and gave only 100/500-yr — exactly the soft spots an honest audit flags (fabricated tail, EAL resting on an
assumed onset). The solar JD-FL-8 hardening (regression Q(T) + a BLE-anchored rating) needed *two* measured depth
anchors; Green River (Zone A) has none — only the bathtub 1% surface.

**Decision.** Pull a **real USGS flood-frequency curve** `Q(T)` from the **Green River at Amboy gauge (05447000)** —
annual peaks → **Log-Pearson III (Bulletin 17C)** — and convert each RP's **discharge ratio** to a water-surface
rise relative to the 1% surface through a wide-channel rating: `ΔWSE(T) = d_char·[(Q(T)/Q₁₀₀)^b − 1]` (`b≈0.6`,
sensitivity-tested). This (a) **grounds the 500-yr** in measured flood-frequency and (b) **adds real 10/25/50-yr
points** → the EAL no longer rests on an assumed onset. Validate the result against **FEMA NRI** (independent
HAZUS-based Riverine-Flooding EAL for Lee County).

**Why.** It removes the two biggest soft assumptions with public, runnable data, and is the same spirit as JD-FL-8
(real flow-frequency + a rating), adapted to a one-anchor (no-BLE) site. The residual is only the rating exponent
`b`, which is **not load-bearing** (the discharge ratio dominates; sensitivity-tested).

**What it changed (honest).** The real `Q(500)/Q(100) ≈ 1.10` (strong negative log-skew −1.1 — this flat basin's
floods have a natural ceiling), so the old +0.6 m was a **~5–10× overestimate**: **PML500 13.3% → 11.5%** (corrected
down). And the substation floods even at the **10-yr**, so the **EAL hardened 0.45% → 1.5%** (real frequent loss the
assumed onset had hidden). **NRI cross-check:** our EAL ≈ **16×** the Lee County average riverine rate (0.096%/yr) —
right order for a 60%-in-floodplain site — and NRI's **0.93 floods/yr** confirms the annual-maximum model (JD-FL-7).

**Honest caveats.** Gauge is offset from the farm → we use RP **ratios** (robust to offset), not absolute stage.
Rating exponent `b` assumed (sensitivity-tested). NRI is building-stock, not wind — an order-of-magnitude anchor,
not a like-for-like.

**Update (2026-06-18) — the substation is now REAL, and AFL-W5 is collapsed.** The substation is the mapped collector
nearest the turbine cloud, sourced from **HIFLD Electric Substations** (the complete, government-maintained US
substation layer — **portfolio-scalable: works at any CONUS asset**) with **OpenStreetMap** supplying the project
name ("Big Sky Wind LLC Substation") and an independent cross-check (HIFLD + OSM agree on the coordinate to the
decimal). The cloud centroid is the last-resort fallback. It sits on **high ground (FEMA zone X, dry)** — like the
turbines — so it contributes ~0. The
headline **dropped EAL 1.5% → 0.31% / PML500 11.5% → 3.2%** (the earlier "substation-concentrated" result was an
artifact of the assumed centroid-in-floodplain location), and the **NRI multiple improved to ~3× county avg** (from
16×). The full result now ≈ the turbines-only floor; **no load-bearing site assumption remains** — residual
uncertainty is curve-level (the greenfield M3 + Zone-A bathtub). Caveat: one **unnamed 138 kV west-edge** substation
does flood (0.88 m) — role unconfirmed, flagged. M4 keeps a floodplain-substation **sensitivity scenario**.

> **⚠ CORRECTED by [JD-FL-W7](#jd-fl-w7) (2026-06-20).** This "real and **dry**" substation was the **wrong** node —
> the nearest-to-centroid pick grabbed the **adjacent Big Sky Wind farm's** collector (outside Green River's hull).
> Green River's **own** collector is the in-hull `substation=generation` 138 kV node on the west edge — the flagged
> "unnamed west-edge" substation — and it **floods** (0.88 m @ 100-yr). So the EAL **did not** drop to the
> turbines-only floor: with the real collector the headline is **EAL 1.27% / PML500 11.4%** (≈ the earlier
> floodplain-substation figure, now on real grounds, not an assumption). "No load-bearing site assumption remains"
> is **withdrawn** — the substation *location method* was load-bearing and is now fixed (in-hull generation pick).

**Revisit trigger.** A detailed FEMA study (BFE) or StreamStats+HAND raster → swap the depth step; confirm the
west-edge substation's role.

---

## JD-FL-W4 · Wind-cell depth — **extent-based bathtub off 3DEP** (Zone A has no BFE/BLE)

**Date:** 2026-06-17 · **Status:** decided · Specializes [JD-FL-6](#jd-fl-6) to the wind high site · *basics-spot-on*

**Context.** The solar high site (Elizabeth, LA) had a FEMA **BLE** depth grid. The wind high site (**Green River,
IL**, [JD-FL-W3](#jd-fl-w3)) does not: its floodplain is **Zone A** (approximate — `STATIC_BFE = -9999`, no BFE
lines) and **outside BLE coverage** — exactly the approximate/ungauged case JD-FL-6 reserved StreamStats+HAND for.

**Decision.** Sample depth **per node** (turbine + substation) via an **extent-based bathtub** off the **3DEP DEM**:
the 1% floodplain *boundary* is the 1% **water-surface contour**, so
`depth = WSE(median of nearest SFHA-edge 3DEP samples) − ground(3DEP) − pad_elevation` (clipped ≥0), a node flooding
iff inside the mapped SFHA. The **500-yr** surface = the 1% surface **raised by a freeboard** `ΔWSE ≈ 0.6 m` (≈2 ft;
**AFL-W7**) because no 0.2% band is mapped here — deepening floods *and* catching valley-edge turbines. Sampled **at
each turbine point** (a sparse cloud), not over an areal footprint.

**Why.** The only **public, self-contained** depth path for an approximate Zone A floodplain (no BFE, no BLE grid),
reusing the **3DEP DEM** the solar M0/02 established. It honours the asset's physics (most turbines above the
floodplain; valley-bottom ones flood; the substation is one low node).

**Honest caveats.** Medium-low confidence — a **flat-water** approximation of a sloping floodplain; the 500-yr
freeboard is an assumption (no mapped 0.2% band); two RPs only. **StreamStats+HAND** (JD-FL-6/JD-FL-8) or a
detailed-study BFE is the documented upgrade.

**Revisit trigger.** A detailed FEMA study (BFE) or a StreamStats+HAND run at Green River → swap in engineered depth.

---

## JD-FL-W3 · Wind high site = **Green River, IL** — the **most flood-exposed** wind farm (a TX site would serve equally)

**Date:** 2026-06-17 · **Status:** decided · refined alongside [JD-FL-W2](#jd-fl-w2)'s correction

**Context.** Site selection screened wind fleets by SFHA membership (`00_screening_sweep`). Exposed riverine wind
exists in **both** TX (Lane City, Colorado R., ~42%) and the Midwest (Green River IL ~60%; Barton IA ~16%).

**Decision.** High site = **Green River (Lee Co., IL)** — **~60% of its 74 turbines in the 1% SFHA**, the **most
exposed** of either region (the clean proving site). Baseline = **Shepherds Flat** reused.

**Why (corrected).** Green River is chosen because it is the **most exposed**, *not* because TX is immune (it isn't —
JD-FL-W2 correction). The depth method is the same either way: Green River **and** the exposed TX sites are
**approximate Zone A with no BLE depth**, so depth comes from the extent-based bathtub + gauge flow-frequency
(JD-FL-W4/W5) — there was never a BLE-reuse advantage to a TX wind high site.

**Honest caveats.** Depth via bathtub/gauge, not BLE (JD-FL-W4/W5). The substation location is unknown (centroid
proxy, AFL-W5) and is the load-bearing assumption.

**Revisit trigger.** A detailed BLE/Risk-MAP study covers an exposed wind farm → sample real depth there.

---

## JD-FL-W2 · Finding — wind **mostly avoids floodplains** (exposure is per-node, not areal); a minority don't. **(Corrected: TX is NOT flood-immune)**

**Date:** 2026-06-17 · **Corrected:** 2026-06-18 (the `00_screening_sweep` reproducibility artifact caught the error) · **Status:** decided

**Context.** The solar cell treats flood as **areal** (one footprint floods as a unit); the plan assumed the wind
cell would screen a TX wind farm the same way. A FEMA probe reframed it — but an early draft of *this* decision
**overstated** the result.

**The durable finding.** A wind farm is **not** an areal flood asset: turbines are deliberately sited on **high
ground**, so the **median** wind project has **~0% of turbines in the 1% SFHA** (confirmed across both the TX and
Midwest fleets). Flood exposure is **per-node** — a *fraction* of valley-bottom turbines + the **substation** — not
an areal fraction. This drives the M0 screen (SFHA *fraction*), the M2 coupling (per-node sum), and the M3 curve
(only the base floods). **Flood is a *minor* peril for wind vs ground-mounted solar.**

**The correction (important).** An earlier draft claimed "**TX wind is flood-immune — 0/2,976 turbines wet**." That
was **wrong** — a **false zero**. It used FEMA **BLE *depth*** (which reads 0 at the exposed TX turbines because they
sit in **approximate Zone A with no BLE coverage** — BLE-NoData ≠ dry), not SFHA *membership*. By membership, **TX
has genuinely flood-exposed riverine wind** — e.g. **Lane City Wind (Wharton Co., Colorado River) ~42% of turbines
in the SFHA**, plus several others. The exposed minority exists in **both** regions; **Green River, IL (~60%)** is
simply the **most** exposed. The `00_screening_sweep` notebook reproduces the durable finding *and* demonstrates the
false-zero trap (§3) so the record is self-correcting.

**Why it matters.** The per-node framing stands. But the site pivot to the Midwest was **not** because "TX is
immune" — it was because Green River is the most-exposed example; TX's Lane City would serve equally (both are Zone A
→ same bathtub/gauge depth method, JD-FL-W4/W5).

**Revisit trigger.** Turbine siting standards change; or a wind-specific flood-loss benchmark appears.

---

## JD-FL-W1 · Wind sites — **Shepherds Flat (reused, baseline) + a screened high-flood farm**; geometry = USWTDB cloud + hull

**Date:** 2026-06-17 · **Status:** decided · Mirrors [JD-FL-3](#jd-fl-3) (solar) on the wind asset

**Context.** The flood cell's V2 asset is the wind farm — it needs a low/high pair like solar's, and a geometry for
a **sparse turbine point cloud** (not solar's dense footprint).

**Decision.** **Baseline = reuse Shepherds Flat** (the convective_wind wind baseline — the *asset's* cross-peril
coherence axis, as Hayhurst is for solar); polygon WKT + turbine cloud cached in `data/convective_wind/`. **High =
screened** ([JD-FL-W3](#jd-fl-w3)). **Geometry = USWTDB turbine cloud + a convex-hull boundary** (the
`renewablesinfo_org` boundary-DB symlink is **absent** here, so the hull is the symlink-free honest extent for a
point cloud — **AFL-W4**). **TIV = $/kW** (AWN-14 basis). **Substation** = a centroid node (**AFL-W5**).

**Why.** Reusing Shepherds Flat preserves coherence and is a legitimate mapped-dry control (NFHL SFHA ≈ 0); the
USWTDB cloud is the per-turbine view flood needs; the hull is symlink-free.

**Revisit trigger.** The boundary-DB symlink returns / an OSM plant polygon is found → swap the hull for it.

---

## JD-FL-8 · Densify the lower return periods — **regression flow-frequency + a BLE-anchored rating curve** (not a live HAND raster)

**Date:** 2026-06-17 · **Status:** decided · Hardens [JD-FL-7](#jd-fl-7)'s EAL · Implements the JD-FL-6 seam, depth step swapped.

**Context.** JD-FL-7 shipped a 3-point loss curve where the **10-yr onset depth is an assumption** (`ONSET_DEPTH_FT`),
not a measurement — and EAL is driven by exactly that frequent region (PML@100/500 is BLE-solid, EAL is soft). The
hardening JD-FL-6/7 promised is "densify the lower RPs with StreamStats+HAND." On building it, two facts surfaced:
1. **The literal HAND path won't run here & is weakest here.** The USGS **watershed-delineation** service
   (`streamstatsservices/watershed`) is **down (404)**; the NOAA OWP HAND depth step needs multi-GB 3DEP/HAND rasters
   from an AWS S3 bucket. And the research doc itself flags **HAND as *least* accurate on low-order, low-relief
   streams** — exactly Elizabeth's flat Louisiana alluvial plain, where BLE already ran a HEC-RAS-quality study.
2. **The regression-equation service (NSS) *is* reachable** (HTTP 200) — so the **flow-frequency** half is live.

**Options.** (a) Full live StreamStats→HAND raster pipeline — most independent evidence, but not runnable here and
least reliable for this site. (b) **Regression flow-frequency Q(T) + a rating curve pinned to the two real BLE
depths** → read depth at the lower RPs. (c) JRC/GloFAS coarse depth grid — needs Google Earth Engine, ~1 km (too
coarse for this footprint). (d) Keep the flat onset assumption.

**Decision — option (b).** Get the **flow-frequency curve** `Q(T)` for T∈{2,5,10,25,50,100,500} at the site's reach
from real regression data, then build a **stage/depth–discharge rating curve anchored to the two genuinely-measured
BLE depths** (100-yr + 500-yr): with `(Q₁₀₀, d₁₀₀)` and `(Q₅₀₀, d₅₀₀)` as anchors, fit a monotone rating
`depth = f(Q)` (power-law / log form) and evaluate it at the lower-RP discharges → **measured-anchored depths at
2/5/10/25/50-yr**, replacing the flat `ONSET_DEPTH_FT`. Feed the now-denser depth→loss profile through the **same**
M4 seam (variable-length RP curve — no downstream change). **Also persist the raw `Q(T)`** so a future swap to full
HAND is just the depth step.

**Why.** It makes the lower-RP depths **rest on real data** (real flow-frequency shape + two real BLE depth anchors)
instead of a flat guess — the EAL-hardening goal — while staying runnable and honest. For a flat alluvial plain
where BLE exists, **anchoring to BLE beats raw HAND** (the research doc's own ranking: "prefer BLE; HAND weakest on
low-relief"). The single remaining assumption is the **shape of the rating between the two anchors** (vs. a flat
onset depth before) — strictly less assumption, and surfaced in an M4 sensitivity sweep.

**Honest caveats.** (1) Two BLE anchors fix the rating's *level*; its *curvature* is assumed (power-law) — sensitivity-
tested. (2) Flow-frequency is regional regression (tens-of-% standard error in the LA plains) — propagate later as an
MC overlay, not yet. (3) Still annual-maximum, physical-damage-only (JD-FL-1/7). (4) Elizabeth sits near a regression-
region boundary (Coastal Plain / Mississippi Alluvial Plain) — note which region's equation is used.

**Revisit trigger.** Watershed-delineation service back up **and** HAND rasters fetchable → swap the rating step for
live HAND-SRC depth and keep `Q(T)` as-is; or a hi-res national RP-depth grid appears → sample it directly (JD-FL-6
trigger). Either way re-validate EAL — it will move.

---

## JD-FL-7 · Event-model bridge — annual-maximum MC sampling the loss-exceedance curve (3-point, seam-ready)

**Date:** 2026-06-17 · **Status:** decided · Settles the long-open call. Mirrors convective_wind strong-wind (fit to an RP curve).

**Context.** M3 gives conditional loss at the BLE return periods (100-yr, 500-yr). The shared engine wants per-year
loss vectors (EAL/VaR/PML/TVaR off them — DD-4 frame). How does a sparse RP curve become that?

**Decision.** Model riverine flood as **annual-maximum** (~1 damaging flood/year — *not* compound-Poisson multi-event,
which mis-fits flood). Build a **loss-exceedance curve** from the real BLE points — `(AEP 0.01 → L₁₀₀, 0.002 → L₅₀₀)`
— plus a **10-yr onset anchor** `(AEP 0.1 → ~0)` where BLE's 10% *extent* shows inundation begins. The MC draws each
year's AEP ~ U(0,1) → `loss(AEP)` by **log-AEP interpolation** (bounded extrapolation below 0.002) → per-year loss
vectors → the **shared EAL/VaR/PML/TVaR** (% of TIV). This is the convective_wind strong-wind pattern (fit/sample an
RP curve) specialized to annual-max + 3 points.

**Why.** **PML at 100/500-yr is anchored to real BLE** (the percentiles reproduce L₁₀₀/L₅₀₀ by construction — a frame
known-answer). Keeps the **shared metric frame** → Total-Loss-combinable with hail/wildfire/wind. Avoids both the
old-model loss-first shortcut and a fabricated compound-Poisson fit from 2 points.

**Honest caveat.** **EAL is approximate** — it's driven by the frequent region (below 100-yr), which rests on the
onset anchor + interpolation, not measured depths. PML solid, EAL soft.

**Seam (easy upgrade).** M1 emits a **variable-length, source-tagged depth/loss-RP profile**; M4 fits/samples
generically. So adding lower-RP points (StreamStats+HAND, or JRC) is a **one-place change** — downstream untouched,
re-validate because EAL will move.

**Revisit trigger.** Lower-RP depths sourced (StreamStats+HAND primary, JRC coarse cross-check) → re-fit; EAL hardens.

---

## JD-FL-6 · Depth source (final) — **national pipeline: StreamStats + OWP-HAND, FEMA-BLE-preferred** (BLE used for the high site)

**Date:** 2026-06-17 · **Status:** decided · **Supersedes [JD-FL-5](#jd-fl-5)** · Source: [research](../../../jdocs/flood_research_result.md) + BLE probe.

**Context.** JD-FL-5 picked single-gauge extraction because no grid was available. A scaling review (we need *every*
CONUS asset, not one site) + a deep research pass reframed it: **single-gauge Bulletin 17C does NOT scale** — it
needs a hand-picked adequate gauge per site and fails at ungauged/short-record points (exactly Bayou Galion, whose
on-stream gauge has stage-only ~23 yr and whose discharge gauge drains too large an area). The only architecture
where **prototype == production at any CONUS point** is a national one.

**Decision.**
1. **Production spine (national, per-asset, automatable):** **USGS StreamStats** regional-regression discharge-at-RP
   → **NOAA OWP HAND + synthetic rating curve** → depth-above-ground (vs the 3DEP DEM). Works at any reach.
2. **Preferred where it exists:** sample a **FEMA BLE** depth grid (InFRM EstBFE / `txgeo.usgs.gov/.../FEMA_EBFE/EBFE`)
   — local-HEC-RAS quality, free, NAVD88, 1% + 0.2% depth/WSE.
3. **Coarse cross-check:** JRC/GloFAS global (~1 km).
4. **Single-gauge Bulletin 17C → demoted to local validation only**, never the engine.
5. **For Bayou Galion specifically (V1):** **BLE is available** (probe: Boeuf HUC8 `08050001`, "Data Available";
   0.2% depth ≈ 1.66 ft at the plant, WSE ≈ 88 ft matching our DEM) → **use BLE depth as the M1 source** for this
   site, with StreamStats+HAND as the scalable method for the no-BLE / ungauged general case.

**Why.** Nationwide queryability is the binding constraint; StreamStats+HAND is the only free method that satisfies
it, and BLE is the best free *depth* product where present. Accuracy (HAND ≈0.75 CSI / ~0.6 m) is acceptable for
portfolio EAL/VaR/PML (regression-Q error + the damage curve dominate), and BLE is better still. Keeps us hazard-first.

**Honest caveats.** BLE gives only **1% (100-yr) + 0.2% (500-yr)** depth (+10% extent) — the tail points, not the full
curve; lower RPs come from StreamStats+HAND or interpolation. HAND is weakest on low-order/low-relief streams (like
Bayou Galion) → prefer BLE there. Datum via NOAA VDatum; flag regulation/levees + climate non-stationarity as overlays.

**Revisit trigger.** A free hi-res national RP-*depth* grid appears (or BLE reaches full CONUS) → switch primary to
"sample the national depth grid per asset", demote StreamStats+HAND to gap-fill. Commercial budget → Fathom-US primary.

---

## JD-FL-5 · Depth source — USGS extraction (Log-Pearson III) — **SUPERSEDED by [JD-FL-6](#jd-fl-6)**

**Date:** 2026-06-17 · **Status:** ~~decided~~ **superseded** (single-gauge doesn't scale to all-US; see JD-FL-6).

**Context.** JD-FL-2 made pre-integrated RP depth grids the V1 spine, extraction the cross-check. The depth-source
probe + owner confirmation say no grid is available for **Bayou Galion**:
- **No depth product on hand** (owner confirmed — not Fathom, First Street, or otherwise).
- **FEMA** carries no depth here — Zone A is an *approximate* floodplain (`STATIC_BFE = -9999`, `DEPTH = -9999`); no
  detailed study → no Risk MAP depth grid.
- **JRC global** flood maps: old endpoint dead (moved to the JRC Data Catalogue) and coarse (~1 km) anyway.
- **But** 49 USGS peak-flow gauges sit within ~0.4° — incl. the **Ouachita River** and **Bayou Bartholomew**
  (through Morehouse Parish — the plant's likely flood source).

**Decision.** For V1, **flip the spine to extraction**: controlling-gauge peak-flow record → **Log-Pearson Type III**
(Bulletin 17C) → discharge-at-RP → **stage** (gauge rating) → **depth = stage − ground elevation** (3DEP DEM from
[`02`](../../../Notebooks/flood/m0_input_data/01_solar_sites.ipynb)). Pre-integrated grids (Fathom / FEMA Risk
MAP / First Street) become the **future swap-in**, not the V1 path.

**Why.** It is the only **public, hazard-first** depth path that covers this site; gauge density is high; and the
site is **flat** (3.2 m relief — `02`), so `stage − DEM` is a defensible V1 depth without 2-D hydraulics. Keeps us
off the old model's loss-first shortcut (*basics-spot-on*).

**Honest caveats (carried into M1).** (1) The gauge is offset from the plant along the stream — V1 uses the nearest
gauge's water-surface as a proxy (flag the slope offset). (2) **Datum** — USGS gauge datum (often NGVD29) must be
reconciled to the DEM's NAVD88. (3) Regulation — check for upstream dams that break stationarity (Bulletin 17C
assumes a stationary, unregulated record).

**Revisit trigger.** A depth-grid product (Fathom / FEMA Risk MAP / First Street) becomes available → swap it in as
the spine and demote extraction to the cross-check (reverting to JD-FL-2's original ordering).

---

## JD-FL-4 · M1 built as a sub-peril *family* + a reserved `event_family_id` — the two "easy-to-add-coastal-later" hooks

**Date:** TBD · **Status:** proposed · Enables [JD-FL-1](#jd-fl-1)'s deferral · *modular-from-day-one*

**Context.** JD-FL-1 defers coastal (and pluvial may lag riverine). Deferral is only low-regret if the M1 catalog is
built so the deferred sub-perils slot in **without a refactor**. Wind's family (strong wind + tornado: shared M0/M1,
fork at M2, shared M3/M4) is the precedent.

**Decision (proposed) — two cheap hooks, built now even though V1 ships riverine(+pluvial) only:**
1. **Sub-peril-keyed catalog/manifest** — model flood as a *family* (a `sub_peril` key: `riverine` now, with the
   schema able to hold `pluvial`/`coastal` rows), **not** hardcoded "flood = riverine." Adding a sub-peril later = a
   new row, not a rebuild.
2. **Reserve `event_family_id`** in the catalog schema — unused in V1, but present — so a future coastal-surge event
   can be linked to its parent hurricane event (the A12 cross-link) to prevent double-counting. The *one* piece of
   future-proofing that's expensive to retrofit.

**Why.** Both cost almost nothing at build time and are the difference between "add coastal in a day" and "refactor
M1." The old repo's flood code (single conflated flood type, no event identity) is exactly what these avoid.

**Revisit trigger.** When pluvial or coastal is actually added — confirm the keys/field were sufficient; extend if not.

---

## JD-FL-3 · Two solar sites — **Hayhurst (low, reused) + a national-EIA flood-screen high site** (Lower-Mississippi riverine)

**Date:** TBD · **Status:** decided · **High site = Elizabeth Solar Plant** (EIA 66111, Allen Parish LA, 143 MW).

The SFHA-centroid screen first surfaced **Bayou Galion** (EIA 67104, Zone A) — but it has **no OSM/enriched polygon**
(circle-only), and flood needs a real footprint more than other perils. A **geometry + BLE-depth refinement** over the
exposed candidates selected **Elizabeth Solar**: a real **~3.9 km² OSM polygon** *and* the deepest BLE flood of the
polygon-bearing candidates (100-yr 16% @ 0.46 m / 500-yr 19% @ 0.60 m, sampled over the real polygon). Its centroid is
zone X but the footprint straddles the SFHA (BLE-confirmed). Both sites now use **real OSM polygons** (Hayhurst 0.73 km²,
Elizabeth 3.91 km²) — no circle fallback. Enriched-registry/Fathom remain future swap-ins.

**Context.** The low-vs-high contrast mirrors hail (single asset = Hayhurst) → wildfire (added the pair: Hayhurst
baseline + Matrix proving, Matrix chosen by screening 38 registry assets on burn probability). Flood needs the same
shape, with the high site chosen on a *flood* metric.

**Decision (proposed).**
- **Low / baseline = reuse Hayhurst Texas Solar** (EIA 66880, Culberson Co. TX, Chihuahuan desert) — genuinely
  near-zero flood **and** the same asset as hail + wildfire (cross-peril coherence; the owner's stated preference).
- **High / proving = screen the *national* EIA registry** (`powerplants_enriched_v2`, ~8.8k EIA-matched — the set
  wildfire screened, **not** the 66-site in-repo AIG portfolio, which has no MS/LA and only 2 AR sites) by a flood
  metric (FEMA flood zone / Fathom RP depth), targeting the **Lower-Mississippi alluvial plain** (LA/MS/AR Delta) —
  best depth-grid coverage + cleanest riverine contrast. The exact EIA asset is confirmed by that screen in M0.

**Why.** Reusing Hayhurst preserves coherence and is a *legitimate* low baseline (desert). The national screen keeps
the Lower-Mississippi high site reachable (the in-repo portfolio is TX/CA/Midwest-weighted). Method = wildfire's,
metric swapped to flood.

**Revisit trigger.** If the national screen's top Lower-Mississippi asset lacks depth-grid/DEM coverage, fall to the
next candidate or pivot region (Central Valley CA / Illinois riverine — both present even in the in-repo portfolio).

---

## JD-FL-2 · M1 frequency path — **pre-integrated return-period depth grids** (not Log-Pearson III extraction)

**Date:** TBD · **Status:** proposed (A-series-backed) · Generalizes [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)

**Context.** M1 needs a flood frequency basis. Two routes: **(a) pre-integrated** return-period depth rasters
(hydrodynamic-reanalysis output — Fathom-US / HEC-RAS / FEMA Risk MAP — tagged 10/50/100/200/500-yr), or **(b)
extracted** — fit Log-Pearson Type III (Bulletin 17C) to USGS annual peak streamflow, then route to depth.

**Decision (proposed).** **Pre-integrated depth grids = the V1 spine** (per A20 §3.3, "the hydrodynamic reanalysis
*is* the backbone for fluvial"). USGS gauge / Log-Pearson III kept as the **validation cross-check**, not the
primary path.

**Why.** Same logic as wildfire (FSim pre-integrated) and wind (ASCE RP surface): the frequency is already baked
into the product by a hydraulic model we can't out-build; extraction-from-gauges is labor-heavy and ungauged-stream
regionalization is its own project. Pre-integrated is the honest, fast, defensible V1 ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)).

**Revisit trigger.** If the chosen grid product lacks the needed return periods or resolution at our sites, or if a
site is ungauged-and-ungridded → fall back to the extraction route. Confirm the actual public product (Fathom-US
2.0 vs FEMA Risk MAP depth grids vs licensed First Street) in M0.

---

## JD-FL-1 · Scope — flood as a **sub-peril family**; **riverine + pluvial** physical damage to solar first; coastal cross-linked to hurricane, deferred

**Date:** TBD · **Status:** proposed (A12-backed)

**Context.** "Flood" is not one peril. A12 splits it by the dual test (distinct footprint **and** distinct data)
into **Riverine `[R]`** (river-network-anchored), **Pluvial `[F]`** (grid-anchored local rainfall), and **Coastal
`[C]`** (coastline surge). Each is a separate catalog row; coastal surge is **cross-linked to hurricane** via a
shared `event_family_id` (A12 §3 / A20 §6.8), not double-listed as its own independent peril.

**Decision (proposed).** V1 = **riverine + pluvial inland inundation → physical equipment damage**, on a **solar
farm first** (wind farm V2, off the shared catalog). **Coastal `[C]` deferred** — it rides the deferred hurricane
field (surge frequency follows tropical-cyclone tracks). **Also out of scope:** foundation scour/erosion, corrosion,
water-quality, and **business-interruption loss** (physical loss only — A25's acute × damage cell; matches the
team's hazard-tier scope).

**Why — and the precise reason coastal is deferred (not "can't," but "shouldn't yet").** Coastal surge *depth* is
actually obtainable pre-integrated (Fathom-US coastal layer / NOAA SLOSH / FEMA coastal BFE), so the hazard is **not**
blocked by the deferred hurricane build. We defer coastal because: (1) **double-counting** — surge and hurricane wind
are the *same storm*; building coastal standalone now, then hurricane later, counts one event in two pipelines unless
the `event_family_id` cross-link exists — premature plumbing (the old repo's separate Hurricane + Coastal-Flood rows
are the live demo of this error); (2) **zero payoff for our V1 sites** — both are **inland** (Hayhurst desert;
Lower-Mississippi riverine), so surge never reaches them; (3) **scope/correlation cost** for no V1 benefit. R + F have
self-serve data + a committed pre-integrated method (JD-FL-2). Honest scope is *basics-spot-on* (mirrors DD-W1, DD-WN-1).

**Easy to add back — by design.** Coastal reuses the *same* site-conditioned coupling and pre-integrated-grid M1
pattern, so adding it later = a new M0 fetch (coastal grids) + a catalog row + a USACE coastal curve + a coastal site;
M2/M3-framework/M4 reused (wind's strong-wind+tornado family is the working precedent). The two cheap hooks that keep
it easy are recorded in **JD-FL-4**. Deferring does **not** make the one genuinely hurricane-gated part (surge↔wind
double-count reconciliation) any harder — that's hurricane-side work whenever hurricane lands.

**Revisit trigger.** When the hurricane / field-intensity bucket is built, coastal `[C]` attaches via the existing
cross-link without re-architecting. Decide R-only vs R+F for the *first* notebook in M0 (pluvial may lag riverine).

---

## Open — the genuinely undecided call

**JD-FL-? · Event model — RP-scenario + AAL vs the shared compound-Poisson MC (the bridge).** The flood reference
world (HAZUS / First Street) computes loss at each return period, then integrates the **exceedance curve → AAL**
(trapezoid). Our repo's shared M4 is a **compound-Poisson/NegBin Monte-Carlo** that samples events/year. These are
two different mathematical routes. **The decision:** convert the RP depth grids into an event stream the shared MC
can sample (the wildfire precedent — FSim's pre-integrated BP became a λ feeding the same MC), **or** run flood on
an RP+AAL track and reconcile the metrics. This must be settled before M4 — it is *the* load-bearing flood decision.
Frame it explicitly against [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md) and
the engine contract.

*Also to record as we plan:*
- *JD-FL-? — **depth-damage curve**: tabular USACE building-archetype + per-asset DEM elevation offset (A22 §2.4/§7.6);
  subsystem split; solar-specific curve deferred (A22 Q7 — none exists publicly).*
