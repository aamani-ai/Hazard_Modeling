# Plan: Wind Pipeline

> **Status: ✅ BUILT — convective wind × wind-farm M0→M4 complete** (2026-06-17; both sites, both sub-perils,
> reference-aligned; numbers real-but-small + approximate). Wind is **Hazard 3 of 3** and the first peril
> where **no single data product pre-defines the event** — so the build opens with a new **layer-0
> (hazard-definition)** above M0, then M0→M4. The peril V1 builds is **convective wind = one peril with two
> sub-perils**: **[W] strong / straight-line wind** and **[T] tornado** (matching the Drive reference). V1 =
> **inland-convective, exogenous** convective wind on utility-scale wind farms — **strong / straight-line wind
> first** (broad-swath, *site-conditioned*, bucket 3; the **ASCE 7-22 RP gust surface is the pre-integrated
> profile**, like FSim was for wildfire — DD-WN-3/4), then **tornado** (narrow-path, *areal hit-or-miss*, bucket 1;
> reuses hail's Minkowski in a path-aware thin-rectangle form — DD-WN-5). Hazard observable = **3-second peak gust**
> (DD-WN-6); two thresholds kept distinct — the **meteorological event threshold** (NWS severe **≥ 58 mph**; EF
> scale; DD-WN-7) that the catalog *counts* for λ, vs the **asset damage-onset threshold** (IEC 61400 survival
> speed; DD-WN-11) where the damage curve *leaves zero*. Severity differs by sub-peril: **tornado = a bounded GPD on
> gust, truncated at the EF5 ceiling L ≈ 113 m/s** (ξ < 0, reaches the ceiling); **strong wind = Gumbel/exponential
> (ξ ≈ 0), capped at L** — read straight off the log-linear ASCE return-period surface (DD-WN-8). Two sites mirror
> hail's low-vs-high: **Traverse (OK, ~999 MW)** high/proving vs **Shepherds Flat (OR, ~845 MW)** low/baseline
> (DD-WN-10). Metrics off the **one shared compound-Poisson/NegBin MC** (DD-WN-12) — never the expected-loss
> shortcut (DD-WN-13), always **% of TIV** alongside dollars. **The separate, deferred hurricane / tropical-cyclone
> peril (field-intensity, bucket 2) is the genuinely unbuilt bucket — deferred** (DD-WN-9); it relates to convective
> wind only through the shared 3-s-gust wind-damage curve. Next: open **layer-0** (the hazard-definition notebook).
> Scope/coupling reasoning settled in [`../../extra/discussion/convective_wind/`](../../extra/discussion/convective_wind/README.md).

Hazard **3 of 3** (hail ✅ · wildfire ✅ · **wind**). Same approach as hail and wildfire: take **one peril** and
build the whole pipeline **end-to-end in notebooks**, step by step, each cell legible (description → code →
output → plots → tables), every basic verified against a known answer. The notebooks will live in
[`../../../Notebooks/convective_wind/`](../../../Notebooks/convective_wind) (a shared `layer-0`/`m0`/`m1`, a per-sub-peril fork **only at
M2** (`strong_wind/` + `tornado/` — coupling differs), then a **shared** `m3_damage` and `m4_loss_metrics` (one
turbine curve; M4 combines both sub-perils into one annual-loss distribution)).

## The two sides (owner's framing, mirrored from hail & wildfire)

1. **Input data (M0).** Meet and *understand* the raw wind hazard evidence — the **ASCE 7-22 design-wind RP
   surface**, the **SPC SVRGIS** tornado-path + severe-wind record, **NOAA Storm Events**, the **EF scale**, and
   **USWTDB** turbine points — before any modeling. But wind adds a step *above* M0: because no product hands us
   "the event" pre-defined (MESH = "hail ≥ 1 in"; FSim = "fire + flame-length classes" — both inherited), **we must
   author the hazard definition ourselves**, anchored in engineering / meteorological standards. That is
   **layer-0** ([DD-WN-6/7](decisions.md)).
2. **The model (layer-0 → M1 → M4).** Hazard definition → per-sub-peril catalog → coupling (site-conditioned for
   strong wind; areal hit-or-miss for tornado) → anchored turbine-subsystem damage → loss distribution & metrics —
   on the **shared compound-Poisson/NegBin Monte-Carlo engine** (reused unchanged from hail & wildfire).

## Planned phase breakdown

| Phase | M-step | What we build | Notebook(s) | Status |
|------:|--------|---------------|-------------|--------|
| **0. Hazard definition** | layer-0 (authored, above M0) | The peril defined **quantitatively** — 3-s gust observable; the **two thresholds** (NWS ≥ 58 mph / EF event-count μ vs IEC survival damage-onset); physical bound **L ≈ 113 m/s (EF5)**; per-sub-peril severity form (tornado = bounded GPD ξ < 0; strong wind = Gumbel/exponential ξ ≈ 0 off the log-linear ASCE RP surface); + a newcomer coupling-taxonomy primer (areal vs field vs site-conditioned). The first peril where the event is *authored, not inherited* ([DD-WN-6/7/8/11](decisions.md)). | `layer0/01_hazard_definition` | planned ([layer-0 plan](00_hazard_definition.md)) |
| 1. Input data | layer-0 → M0 | Meet the raw evidence: **ASCE 7-22** RP gust surface (the pre-integrated EVT product), **SPC SVRGIS** (~70k tornado tracks 1950+, severe-wind reports 1955+), **NOAA Storm Events**, **EF bins**, **USWTDB** turbine points; the **two sites** (Traverse / Shepherds Flat) with real boundary polygons. **Report/population bias** flagged for correction before any frequency fit ([AWN-1](assumptions.md)). | `m0_input_data/01_…` | planned ([m0 plan](m0_input_data.md)) |
| 2. Catalog | M0 → M1 | **Per-sub-peril** event definition + λ + severity. **Strong wind** = profile-assembly from the **ASCE RP surface** (pre-integrated → no λ-fit; the wildfire/FSim analogue — DD-WN-3, [learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)); severity is Gumbel/exponential (ξ ≈ 0) — the ASCE return-level curve is log-linear; the *extraction* alternative = Poisson + GPD fit to SPC, bias-corrected. **Tornado** = Poisson λ + EF/path stats from SPC; severity = bounded GPD (ξ < 0, truncated at L). | `m1_catalog/01_catalog` | planned ([m1 plan](m1_catalog.md)) |
| 3a. Strong-wind coupling | M1 → M2 | **Site-conditioned** (bucket 3) — *reuses wildfire's M2*. Broad swath → no areal "miss"; the asset reads its **local RP gust**. A **deliberately thin** layer (M1 already coupled). High-frequency → well-populated MC ([DD-WN-4](decisions.md)). | `m2_coupling/strong_wind/01_coupling` | planned ([m2 plan](m2_coupling.md)) |
| 3b. Tornado coupling | M1 → M2 | **Areal hit-or-miss** (bucket 1) — *reuses hail's Minkowski* in a **path-aware thin-rectangle** form `(L+a)(w+a)`. Rare per site → sparse MC → invokes effective-sample-size ([learning_logs/10](../../learning_logs/10_monte_carlo_effective_sample_size.md), [DD-WN-5](decisions.md)). Per-turbine point-cloud (USWTDB) vs areal-footprint distinction noted. | `m2_coupling/tornado/01_coupling` | planned ([m2 plan](m2_coupling.md)) |
| 4. Turbine damage | M2 → M3 | **Shared** — one **subsystem-decomposed, anchored** logistic on 3-s gust (rotor/blades, nacelle/drivetrain, tower, foundation, electrical, civil — old-repo cost split); sub-peril-specific subsystem *activation*, but **one curve object**. `DR(μ) ≈ 0`, rises steeply near the **IEC 61400 survival speed**; **operational-state** (feathered vs operating) note. Approximate now, accurate later ([DD-WN-11](decisions.md)). | `m3_damage/01_damage` | planned ([m3 plan](m3_damage.md)) |
| 5. Loss & metrics | M3 → M4 | **Shared and combined** — the **shared compound-Poisson/NegBin MC**, engine untouched. Two separate per-sub-peril {λ, severity} profiles go IN; they are combined ONLY by co-sampling both event streams into ONE annual-loss distribution per site; ALL tail metrics (VaR / PML / TVaR) are read off that ONE combined distribution — never by summing per-sub-peril profiles or quantiles. **EAL IS additive** across the sub-perils (linearity of expectation): EAL_combined = EAL_tornado + EAL_strongwind, so a per-sub-peril EAL split is meaningful; **VaR / PML / TVaR are NOT additive** (summing per-sub-peril tails assumes the worst tornado year and worst strong-wind year coincide). (Caveat: EAL additivity is exact for gross/uncapped loss; once AEP is capped at TIV, even EAL must be read off the combined sample.) Tornado ⊥ strong wind are treated as **disjoint, independent streams** — disjoint by data product (the ASCE basic-wind surface is non-tornadic; tornado = the SPC Tornado record) — which is what makes adding their EALs valid. EAL/VaR/PML/TVaR off the *sampled* distribution, **% of TIV**. **Strong wind well-populated** vs **tornado rare** (TVaR alongside VaR for the sparse tail). **Method-0** named as the refused cardinal error (~12× tail miss; DD-WN-13). | `m4_loss_metrics/01_loss_metrics` | planned ([m4 plan](m4_loss_metrics.md)) |

## Settled framing (from the discussion → see [`decisions.md`](decisions.md))

- **DD-WN-1** **Convective wind = one peril, two sub-perils** ([T] tornado + [W] strong wind); split per the dual test (distinct footprint **and** distinct data metric). **Hurricane is a separate, deferred peril**, not a convective-wind sub-peril (related only via the shared 3-s-gust damage curve). Adjacent turbine perils (lightning, ice/icing, hail-on-turbine, winter/synoptic non-convective) are also **separate perils, not convective-wind sub-perils** — they fail the dual test as wind.
- **DD-WN-2** Route = **inland-convective**: strong wind, then tornado; **the separate hurricane / tropical-cyclone peril deferred**.
- **DD-WN-3** Strong wind M1 = **profile-assembly from the ASCE RP surface** (pre-integrated; no λ-fit) — the wildfire analogue.
- **DD-WN-4** Strong-wind coupling = **site-conditioned** (bucket 3); reuses wildfire's thin M2.
- **DD-WN-5** Tornado coupling = **areal hit-or-miss** (bucket 1); reuses hail's Minkowski, path-aware.
- **DD-WN-6** Hazard observable = **3-second peak gust** (the universal metric).
- **DD-WN-7** **Two thresholds**, kept distinct: meteorological event μ (NWS ≥ 58 mph / EF) vs asset damage-onset (IEC).
- **DD-WN-8** Severity is **per-sub-peril**: **tornado = a bounded GPD on gust** (ξ < 0, truncated at **L ≈ 113 m/s (EF5)**, reaches the ceiling); **strong wind = Gumbel/exponential (ξ ≈ 0), capped at L** — read off the log-linear ASCE RP return-level curve (R² ≈ 0.999). ξ < 0 is **not** a wind-wide rule.
- **DD-WN-9** **Hurricane / field-intensity (bucket 2) — a separate, deferred peril** — the genuinely unbuilt bucket. *Forward double-count flag:* hurricanes spawn tornadoes and straight-line wind, so a TC-spawned tornado could appear in both the tornado stream and a hurricane catalog (NOT automatically disjoint, unlike tornado-vs-strong-wind); treat the V1 tornado catalog as inland-convective only, or bind hurricane's sub-perils with a shared event identifier and sample them jointly.
- **DD-WN-10** Two sites: **Traverse (OK)** high/proving vs **Shepherds Flat (OR)** low/baseline.
- **DD-WN-11** Damage = **anchored turbine-subsystem** logistic; IEC-survival onset; operational-state aware.
- **DD-WN-12** Metrics off the **one shared compound-Poisson/NegBin MC**; two per-sub-peril {λ, severity} profiles combined ONLY by co-sampling into ONE annual-loss distribution; tail metrics read off that ONE distribution (EAL additive across sub-perils, VaR/PML/TVaR not); **% of TIV** alongside dollars.
- **DD-WN-13** **Never the expected-loss shortcut** (Method 0 — the old repo's cardinal error, ~12× tail miss).

## Files

- [`00_intent.md`](00_intent.md) — the seed: goal, the two sides, the honest V1 label, the scope boundary, open questions.
- [`00_hazard_definition.md`](00_hazard_definition.md) — **the layer-0 centerpiece**: the peril defined quantitatively + the newcomer coupling-taxonomy primer.
- [`decisions.md`](decisions.md) — ADR-style decision log (`DD-WN-*`).
- [`assumptions.md`](assumptions.md) — the assumptions register (`AWN-*`), by layer.
- [`m0_input_data.md`](m0_input_data.md) — the M0 plan (data sources, the two sites, raw evidence to meet).
- [`m1_catalog.md`](m1_catalog.md) · [`m2_coupling.md`](m2_coupling.md) · [`m3_damage.md`](m3_damage.md) · [`m4_loss_metrics.md`](m4_loss_metrics.md) — the per-layer plans.
- Source-of-truth reasoning lives in the discussion docs: [scope/taxonomy `01`](../../extra/discussion/convective_wind/01_scope_and_sub_peril_taxonomy.md) · [coupling buckets `02`](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md) · [hazard definition `03`](../../extra/discussion/convective_wind/03_hazard_definition_and_thresholds.md).
