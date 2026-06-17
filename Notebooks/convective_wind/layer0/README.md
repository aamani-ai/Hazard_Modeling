# layer-0 — Hazard Definition (the **authored** layer, above M0)

*The layer wind needed that hail and wildfire did not. For those perils the data product **defined the event**
(MESH = "hail ≥ 1 inch"; FSim = "fire + flame-length classes") — so layer-0 was empty, we inherited the
definition. **Wind has no such product:** SPC reports, NOAA episodes, ASCE design surface, IEC ratings, and the
EF damage→wind map are all fragmented, none of them "the event." So **we author the definition ourselves**,
quantitatively, anchored in published standards — and that authoring earns its own layer, above M0.*

**Where this sits:** **layer-0 (definition)** → [M0 (evidence)](../m0_input_data/README.md) → M1 → M2 → M3 → M4.
Plan-of-record: [`docs/plans/convective_wind/00_hazard_definition.md`](../../../docs/plans/convective_wind/00_hazard_definition.md).

| Notebook | What it authors | Status |
|---|---|---|
| [`01_hazard_definition`](01_hazard_definition.ipynb) | the wind hazard, defined quantitatively + the concepts it rests on | ✅ **built** |

## What `01_hazard_definition` fixes (the spec the pipeline consumes)

- **Magnitude observable** = the **3-second peak gust** (the cross-standard universal metric; gust ≠ sustained wind).
- **Event threshold μ** (what the catalog counts, for λ): strong wind **≥ 58 mph** (NWS severe) · tornado **≥ 65 mph**
  (EF0); the full **EF bin table** (damage-inferred, biased low in rural land).
- **Physical bound L** ≈ **113 m/s (~253 mph)** (EF5 ceiling) — with the 113-vs-145 m/s reconciliation logged.
- **The two thresholds, kept distinct** — event-count μ (58 mph) vs **asset damage-onset** (IEC 61400 survival
  Ve50 ≈ 52–70 m/s ≈ 117–157 mph). Far apart → the damage curve is **anchored** (`DR(μ) ≈ 0`).
- **Severity form, per sub-peril** — **tornado** = a **bounded GPD with ξ<0** on gust, anchored at μ, truncated at
  L (it reaches the EF5 ceiling); **strong wind** = **Gumbel/exponential (ξ≈0)**, log-linear, capped at L (the ASCE
  return-level curve is log-linear, R²≈0.999). ξ<0 is *not* a wind-wide rule — it is scoped to tornado. The
  bounded-GPD case uses the reusable analytic solve (`ξ=(μ_mean−μ)/(μ_mean−L)`, `σ=−ξ(L−μ)`), **verified against
  known answers** (mean==μ_mean, support==[μ,L]). μ_mean is **fit to observed gusts in M1**, *not* back-solved from
  an EAL (the old repo's rejected habit).
- **Strong-wind tail route** = the **ASCE 7-22 RP surface** as a pre-computed return-level curve (profile-assembly).
- A **coupling-taxonomy primer** — **convective wind = one peril, two sub-perils**: tornado [T] (areal) · strong /
  straight-line wind [W] (site-conditioned). The **separate, deferred hurricane / tropical-cyclone peril**
  (field-intensity) is shown for orientation only — it is *not* a convective-wind sub-peril; it relates to
  convective wind only through the shared **3-s-gust wind-damage curve**. One shared engine sits behind all of them.

> **This is a *definition* notebook, not an exploratory-*data* one** (no source to profile — that is M0). Its
> discipline is [*basics-spot-on*](../../../docs/principles/basics_spot_on.md) applied to the definition: every
> number is provenance-tagged (`[REF]` Hazard-Data-Reference · `[STD]` named standard · `[FRAME]` settled
> framing / old-repo, **not** the reference), and the one piece of real math passes its known-answer checks.

## Decisions & assumptions

Decisions [DD-WN-6/7/8/11](../../../docs/plans/convective_wind/decisions.md) (observable; two thresholds; bound L; anchored
curve). Assumptions **AWN-5/6/7/8/9/10** (observable, thresholds, EF bins, L, IEC onset, provenance honesty) +
**AWN-15/17/18** (ASCE pre-integrated; bounded-GPD form; μ_mean fit not back-solved). Register:
[`assumptions.md`](../../../docs/plans/convective_wind/assumptions.md).

**Next → [M0](../m0_input_data/README.md):** meet the real evidence against this definition (ASCE surface ✅ built).
