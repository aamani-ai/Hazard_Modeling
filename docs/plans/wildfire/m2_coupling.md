# M2 — Solar Coupling (the active plan) · *a deliberately thin layer*

*Turn M1's per-asset hazard profile into the **coupled handoff** M3/M4 consume — for a site-conditioned peril
this is **thin** (M1 already did the coupling; the heavy physics is embedded or deferred). The value here is
**clear assumptions + a note on *why* it's thin + what improves later** — which is exactly what the M0–M4
common structure is for.*

**Where this sits:** M0 → M1 → **M2 (solar coupling)** → M3 damage → M4 loss. Built for both solar assets.
**How it works (the exploration):** [`discussion/wildfire/03`](../../extra/discussion/wildfire/03_m2_site_conditioned_coupling.md).
Notebook: `Notebooks/wildfire/solar/m2_coupling/01_coupling`.

## Why M2 is thin (and that's correct)

For a **pre-integrated, site-conditioned** peril: FSim pre-integrated the events ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md))
**and** there is no areal "miss" (methodology) → **M1 already produced `(λ, kW/m severity)` at the asset**.
There is no Minkowski overlap, no spatial factor. M2's remaining V1 work is small — and we *document* the
thinness rather than manufacture coupling that isn't there.

## Resolved decisions (from `03`)

| # | Decision | V1 |
|---|---|---|
| 1 | **Oozing / on-site source** | Use the **burnable footprint** (M1's FSim severity already excludes non-burnable pixels). At **270 m** a pixel spans the array *and* surrounding fuel → oozing is largely **moot** for the spine (it's acute only at WRC 30 m, our cross-check). **Surrounding-ring fallback** only if a footprint is *entirely* non-burnable (neither asset is) — [AW-15](assumptions.md). |
| 2 | **Exposure fraction** | **1.0 — whole-site on a fire** (V1). Partial-burn / contiguous-front correlation = fire-front sweep, **deferred** — [AW-28](assumptions.md). |
| 3 | **Susceptibility** | **Embed `d = 10 m`** (the M3 curve's reference distance); explicit per-site `d` (defensible space / fences / fire breaks → larger `d`) **deferred** — [AW-27](assumptions.md). Fix the `I/d²`→`I/d` doc bug — [AW-17](assumptions.md). |
| 4 | **Currency** | **Out of V1** — record the FSim vintage; the recency adjustment is **deferred** — [AW-25/26](assumptions.md). |
| 5 | **Own notebook?** | **Yes, a short one** — its value is *documenting* the thin coupling + the assumptions + what's deferred (exploratory-notebook principle: the interpretation is the deliverable). |

## The contract M2 emits (per asset)

`{ lambda_per_yr, severity_kwm_distribution (from M1), exposure_fraction = 1.0, susceptibility_d_m = 10,
oozing_status }` → the same schema M3 (kW/m → damage ratio) and M4 (compound engine) consume. No spatial
factor, no `p_hit` overlap — just occurrence × conditional intensity × whole-site exposure.

## Verification

No-spatial-factor confirmed (λ unchanged from M1; no `λ_collection·p`); `exposure ∈ [0,1]`; contract keys
present; severity probs sum to 1.

## Deferred (named, fence visible)

Fire-front sweep (partial burn, explicit `d`/`t`, real PML tail) · explicit site-feature susceptibility
(imagery/site data → per-site `d`) · currency adjustment (MTBS/WFIGS) · heat-flux/temperature curves. All in
[`assumptions.md`](assumptions.md) (AW-25–28) and [`03`](../../extra/discussion/wildfire/03_m2_site_conditioned_coupling.md).

**Next → M3 (solar damage):** map the coupled kW/m intensity → BoS-weighted damage ratio (curves from
`infrasure-damage-curves`).
