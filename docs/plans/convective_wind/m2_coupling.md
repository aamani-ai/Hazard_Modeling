# M2 — Wind-Farm Coupling (the active plan) · *two buckets, one interface*

*Turn M1's per-sub-peril hazard profile into the **coupled handoff** M3/M4 consume — and this is where wind's
"sub-perils matter" payoff cashes in: **tornado is areal hit-or-miss** (reuse hail's Minkowski, path-aware) while
**strong wind is site-conditioned** (reuse wildfire's thin coupling, p_hit ≈ 1). One layer, two coupling buckets,
contrasted against the third (field-intensity, deferred). The value here is **clear coupling math + why each
sub-peril sits where it does** — exactly what the M0–M4 common structure is for.*

**Where this sits:** [M0](m0_input_data.md) → [M1](m1_catalog.md) → **M2 (coupling)** → [M3 damage](m3_damage.md) →
[M4 loss](m4_loss_metrics.md). Built for both wind farms (Traverse proving + Shepherds Flat baseline).
**How it works (the exploration):** [discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md).
Notebooks (M2 forks — two coupling buckets): `Notebooks/convective_wind/wind_farm/m2_coupling/strong_wind/01_coupling` (site-conditioned)
and `Notebooks/convective_wind/wind_farm/m2_coupling/tornado/01_coupling` (areal).

---

## The three coupling buckets — a newcomer primer (read this first)

Every peril on this platform is dispatched to **one of three coupling types**, each with its own math, behind one
standard interface ([principles/hazard_asset_specificity](../../principles/hazard_asset_specificity.md);
[discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)). The teaching question is *"how
does the hazard **reach** the asset, and what does the asset **read**?"* The reference's footprint taxonomy
("point / narrow path / broad swath / regional field") is the literal root:

| Bucket | Physics (footprint) | What the asset reads | Math | Built reference peril | Mapped peril / sub-peril |
|---|---|---|---|---|---|
| **1. Areal hit-or-miss** | finite footprint **covers you or misses you** (binary) — *narrow path* | full conditional loss on a hit, **$0** on a miss | Bernoulli hit × **Minkowski** `p = (√F+√s)²/A`; `λ_asset = λ_collection · p` | **hail** ✅ | **tornado** (convective-wind sub-peril) |
| **2. Field-intensity** | one event = a **continuous intensity field** over space — *regional field* | the field value **at your location**, varying event-to-event | sample-and-weight the field per event | hurricane (unbuilt) | **hurricane — a SEPARATE, deferred peril** (not a convective-wind sub-peril) |
| **3. Site-conditioned** | a **pre-integrated per-site profile** (frequency + intensity already aggregated) — *broad swath* | **your own local profile** — no hit-or-miss | read the profile; **no spatial factor** | **wildfire** ✅ | **strong / straight-line wind** (convective-wind sub-peril) |

> One sentence each: **Areal** = "the footprint covers you or it doesn't" (Bernoulli × Minkowski). **Field-intensity**
> = "you're always in the field; you read your local value, and it differs each event" (sample the field).
> **Site-conditioned** = "a simulator already pre-baked your site's frequency + intensity; you just look it up."
>
> **Convective wind's payoff:** its **two sub-perils** span **two already-built buckets** — tornado reuses hail's
> areal coupling, strong wind reuses wildfire's site-conditioned coupling. The remaining field-intensity bucket
> belongs to the **separate, deferred hurricane / tropical-cyclone peril** (related to convective wind only through
> the shared 3-s-gust wind-damage curve, [DD-WN-9](decisions.md)) — *not* to a third convective-wind sub-peril.
> Inland-convective wind tours the two buckets we have built; it builds **no new coupling physics**, only new
> *implementations* behind the same interface (*standard interface, not standard physics*). → [DD-WN-1](decisions.md).

---

## Tornado = areal hit-or-miss — the **path-aware** Minkowski variant ([DD-WN-5](decisions.md))

Tornado is hail's coupling **reused**, with one geometric twist. Hail events are roughly **compact** footprints
(the disk approximation `p = (√F + √s)²/A`). A **tornado path is a thin rectangle** — extreme aspect ratio,
length `L` ≫ width `w`. So the Minkowski sum of the path with the asset extent is **dominated by length × asset
extent**, not by the path's tiny area:

> **`p_hit ≈ (L + a)(w + a) / A`** — for a thin path (`w` small, `a` the asset's linear extent), this is
> **dominated by `L · a`** (and `L · w`, the bare path area). A point estimate (`F/A`, ignoring the asset's own
> size) **badly under-counts a spread-out asset** — and a wind farm is *the* spread-out asset.

This is the reference's explicit mandate (Hazard_Data_Ref): *"Risk ≈ annual strike probability (path-area density)
× conditional damage at the EF level. A point estimate understates large-footprint assets — a long transmission
line has many times the strike exposure of a single substation."*

**The wind-farm geometry — two views (this is why the path-aware variant earns its keep):**

1. **Areal footprint = the lease polygon.** A utility wind farm spans **tens of km²** (Traverse ~999 MW, Shepherds
   Flat ~845 MW — both large polygons). For the strike probability, `a` is the **polygon's effective extent**, and
   a long tornado path crossing the lease has a *much* higher strike probability than a point lookup would give.
2. **Per-turbine point cloud (USWTDB) = the refined exposure.** A narrow tornado path **clips a handful of turbines
   and misses the rest** — unlike a compact hail footprint that tends to cover the whole site. So the per-turbine
   view matters: the conditional loss given a strike is **not whole-farm** but **the swept fraction of turbines**.
   V1 can model this as `(strike → fraction of turbines inside the path swath) × per-turbine conditional loss`, with
   the swept fraction from the path width vs the turbine spacing. Document the V1 treatment (full-farm vs swept
   fraction) explicitly and defer the refined per-turbine path-intersection if V1 uses a coarser swept fraction
   ([AWN-?](assumptions.md)).

**Frequency thinning.** `λ_asset = λ_collection · E[p_hit]`, Poisson-thinned per EF class (each class has its own
mean path area from M1). This is exactly hail's thinning — *engine unchanged*. **Rare per site → sparse Monte
Carlo** → this is the sub-peril that exercises [learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md)
(effective sample size) in M4.

**EF-class mean areas (km², reusable from M1):** EF0≈0.5 · EF1≈1.5 · EF2≈3.0 · EF3≈6.0 · EF4≈12.0 · EF5≈20.0.

## Strong / straight-line wind = site-conditioned — **p_hit ≈ 1** (reuse wildfire's thin M2) ([DD-WN-4](decisions.md))

Strong wind is **broad-area** (thunderstorm outflow, derecho, downburst, synoptic high wind) — the reference:
*"broad-area, so most/all of a portfolio is exposed simultaneously."* The asset is **not missed**; it reads its
**local gust**. So M2 here is **thin, and that's correct** — exactly wildfire's M2:

- **No Minkowski overlap, no spatial factor.** The ASCE RP surface already gave the per-site gust profile in M1
  (profile-assembly, [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) → **M1 already
  produced `(λ, gust severity)` at the asset**. M2's remaining work is small.
- **p_hit ≈ 1** — when a severe-wind event occurs in the region, the whole spread-out farm is inside the swath.
  (Contrast tornado, where `p_hit` is small and the conditional loss is a swept *fraction*.)
- **Portfolio correlation surfaces here** (the reference's two-footprints note): strong wind is *correlated* across
  a portfolio (one event hits every turbine and every nearby asset together), whereas tornado is *near-independent*
  point-to-point. V1 is single-site, so we **document the correlation** rather than model it — the portfolio
  correlation term is deferred to the field-intensity / multi-asset build ([AWN-?](assumptions.md)).
- **We *document* the thinness rather than manufacture coupling that isn't there** — the wildfire discipline.

## The third bucket — field-intensity (hurricane), explicitly **deferred** (the contrast)

To make the taxonomy crystal-clear, M2 names the **separate, deferred peril** convective wind is **not** building
yet — and is **not a sub-peril of**. **Hurricane / tropical cyclone is its own peril**, related to convective wind
only through the shared 3-s-gust wind-damage curve ([DD-WN-9](decisions.md)); its coupling is bucket 2,
**field-intensity**: a single storm produces a **continuous wind field** (Holland parametric model along a track →
swath grid); every asset is **always inside the field** and reads its local value, which **varies event-to-event**.
There is no hit-or-miss to thin (you're never "missed" by a hurricane that's over you) — so neither the areal
Minkowski (bucket 1) nor the pre-integrated site profile (bucket 3) applies; you **sample the field**. This is the
**genuinely unbuilt bucket**, where **portfolio correlation and EVT become load-bearing** (one event correlates
many assets; the field tail must be extrapolated). The old repo's own note confirms the distinction: *"a hurricane
is always inside the wind field … the question isn't 'did it hit' but 'what wind speed did the site experience.'"*
Named, fence visible — the future field-intensity build, with its migration path (Holland → swath → hurricane-wind
curve, `x₀ ≈ 160 mph`). → [00_intent](00_intent.md) deferrals, [discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md).

> **Forward-compatibility — the hurricane double-count trap (flag for when hurricane lands).** Unlike tornado vs
> strong wind (disjoint by data product — *no shared physical event*), hurricane is **not** automatically disjoint
> from convective wind: **hurricanes spawn tornadoes and produce straight-line wind**, so a TC-spawned tornado could
> appear in **both** the tornado stream **and** a hurricane catalog. When hurricane is added, either treat the V1
> tornado catalog as **inland-convective only** (excluding TC-associated tornadoes) **or** bind hurricane's
> sub-perils with a shared event identifier and sample them jointly. → [DD-WN-9](decisions.md); [AWN-30](assumptions.md).

---

## The contract M2 emits (per sub-peril, per asset)

**Tornado (areal):** `{ lambda_collection_per_yr, p_hit_distribution (Minkowski, per EF class),
conditional_severity (3-s gust | strike), swept_fraction (turbines inside path | strike), tiv, footprint }` →
the engine thins `λ_asset = λ_collection · p_hit` and applies the swept fraction.

**Strong wind (site-conditioned):** `{ lambda_per_yr (from M1), severity_distribution (3-s gust, Gumbel/exponential
ξ ≈ 0, capped at L), exposure_fraction = 1.0, p_hit = 1.0, portfolio_correlation = "documented, deferred", tiv,
footprint }` → occurrence × conditional gust × whole-farm exposure, **no spatial factor**.

Both land on the same schema M3 (3-s gust → damage ratio) and M4 (compound engine) consume.

## Verification

- **Tornado:** the path-aware `p_hit` **exceeds** a naive point ratio for a spread-out asset (show the under-count
  the point estimate would make); `p_hit ∈ [0,1]`; `λ_asset = λ_collection · E[p_hit]` per EF class; swept
  fraction ∈ [0,1].
- **Strong wind:** no-spatial-factor confirmed (λ unchanged from M1; no `λ_collection · p`); `exposure = 1.0`;
  contract keys present; severity integrates to 1.
- **Both:** the coupling bucket is named in the manifest; the engine reads each handoff without a KeyError.

## Assumptions / decisions

[DD-WN-1](decisions.md) (wind spans two built buckets, no new coupling physics) · [DD-WN-5](decisions.md) (tornado
= path-aware Minkowski, thin-rectangle) · [DD-WN-4](decisions.md) (strong wind = site-conditioned, p_hit ≈ 1) ·
[AWN-?](assumptions.md) (V1 swept-fraction vs refined per-turbine path intersection) · [AWN-?](assumptions.md)
(strong-wind portfolio correlation documented, deferred) · [learning-06](../../learning_logs/06_collection_region_size_cancels.md)
(collection-region size cancels in the tornado thinning) · [learning-09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)
(strong wind is profile-assembly, no fit).

## Deferred (named, fence visible)

Refined per-turbine path-intersection (vs the V1 swept fraction) · strong-wind **portfolio correlation** (the
multi-asset / field-intensity build) · **field-intensity coupling for the separate, deferred hurricane peril
(bucket 2)** — Holland wind field → swath grid, the genuinely unbuilt bucket (with the TC-tornado double-count flag
above) · explicit terrain-exposure adjustment of the ASCE surface (B/D vs C). All in [`assumptions.md`](assumptions.md)
and [discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md).

**Next → M3 (wind-farm damage):** map the coupled **3-s gust** → a **subsystem-weighted, IEC-anchored** turbine
damage ratio (curves from the old-repo subsystem split, anchored at survival speed; operational-state aware).
