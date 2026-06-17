# 00 — Intent

*The seed for the wind pipeline. Captured after the scope discussion, before layer-0 / M0 planning.*

## The goal

Take the **third peril — convective wind — and build the whole end-to-end workflow in notebooks**, step by step,
exactly as hail and wildfire were built. Convective wind is the **payoff** for *"standard interface, not standard
physics"*: it is **one peril with two sub-perils** ([T] tornado + [W] strong / straight-line wind) that land in
**different coupling buckets**, so building it tours coupling types the platform already owns — **tornado reuses
hail's areal hit-or-miss**, **strong wind reuses wildfire's site-conditioned** machinery — leaving only
**field-intensity (the separate, deferred hurricane / tropical-cyclone peril)** genuinely unbuilt. Each step
legible, every basic verified, the **shared loss engine untouched**.

## Why wind (third)

Three reasons it earns the slot. (1) **It exercises the interface hardest** — one peril, two already-built coupling
types, on one engine; if the M0→M4 contract holds for wind it is not hail-shaped or wildfire-shaped, it is
*general*. (2) **It is the first peril we must *define* ourselves.** For hail the event came pre-defined by the data
product (MESH = "severe hail ≥ 1 in"); for wildfire likewise (FSim = "fire occurrence + flame-length classes"). We
inherited the definition. **No single wind product does that** — so we author the hazard definition, anchored in
engineering / meteorological standards (NWS, the EF scale, ASCE 7-22, IEC 61400). That authored definition is a new
**layer-0** above M0 ([00_hazard_definition](00_hazard_definition.md)). (3) It **cashes in two deferred threads** —
*continuous* magnitude severity (unlike wildfire's 6 discrete FLP classes) via a fitted continuous gust tail
(tornado = a bounded GPD; strong wind = Gumbel/exponential off the ASCE RP surface), and the sparse-MC
effective-sample-size discipline (tornado is rare).

## What V1 is — and is NOT (the honest label, settled)

> **Wind V1 models *inland-convective, exogenous, structural-damage* convective wind on utility-scale wind farms** —
> **one peril, two sub-perils**: **[W] strong / straight-line convective wind** (broad-swath thunderstorm outflow,
> derecho, downburst, thunderstorm gust, synoptic high wind) and **[T] tornado** (narrow rotating path). It is the
> wind that *physically damages the turbine* — not the wind *resource* that drives generation (that is the
> Performance tier, `model-gpr`; see the scope boundary below). **Tropical-cyclone / hurricane wind is a separate,
> deferred *peril* — NOT a convective-wind sub-peril** (the field-intensity bucket — [DD-WN-9](decisions.md));
> wind is hurricane's primary peril and its surge/rainfall cross-link to the flood peril, and it relates to
> convective wind only through the shared 3-s-gust wind-damage curve. **Hail-on-turbine, lightning, ice/rime
> accretion, and winter / synoptic non-convective storm are adjacent turbine perils — separate perils, NOT
> convective-wind sub-perils** (they fail the dual test as wind). **V1 does not claim to cover total wind risk** to a
> wind farm. ([DD-WN-1/2](decisions.md))

This honesty is *basics-spot-on* applied to scope: a correct tail on a mislabeled or over-claimed peril is still a
credibility failure — the exact thing the rebuild exists to escape.

## The two sub-perils (and where they sit)

**Convective wind = one peril, two sub-perils.** The hurricane / tropical-cyclone peril is **separate and deferred**
— listed below the rule only to show where that *separate peril* would slot in, not as a member of convective wind.

| Sub-peril (of convective wind) | Footprint | Coupling bucket | Reuses | Frequency regime |
|---|---|---|---|---|
| **[W] Strong / straight-line wind** | broad swath | **site-conditioned** (3) | wildfire M2; ASCE RP surface = pre-integrated profile | **high** — well-populated MC |
| **[T] Tornado** | narrow path | **areal hit-or-miss** (1) | hail Minkowski (path-aware thin rectangle) | **rare** — sparse MC; TVaR alongside VaR |
| *Hurricane — a **separate, deferred peril** (not a convective-wind sub-peril)* | regional field | *field-intensity (2) — unbuilt* | *Holland wind field → swath; EVT + portfolio correlation become load-bearing* | *broad — every asset always in the field* |

The two convective-wind sub-perils split on **footprint geometry**, not gust magnitude (the dual test — a stronger
vs weaker gust is *one* peril; a rotating vortex vs a straight-line field is *two*). The reference's own ruling:
*"two sub-perils, two footprints… don't apply one spatial logic to both — strong wind drives correlated portfolio
loss, tornado drives rare severe single-asset loss."*

## The two sites (low-vs-high contrast, mirroring hail's Hayhurst/Matrix)

- **HIGH / proving — Traverse Wind Energy Center, Oklahoma (~999 MW).** Tornado-alley + derecho corridor; the asset
  that should show a *material* tornado tail and a real strong-wind signal. Real boundary polygon from the
  renewablesinfo boundary DB (OSM/EIA); turbine points from USWTDB.
- **LOW / baseline — Shepherds Flat, Oregon (~845 MW).** Columbia River Gorge; minimal tornado / derecho exposure —
  the near-zero-signal control. ([DD-WN-10](decisions.md))

Two sites across a wide convective-wind exposure range validate the same model end-to-end: near-zero at Shepherds
Flat, material at Traverse.

## The scope boundary — hazard-tier wind vs performance-tier wind (CRITICAL — must be explicit)

For solar, the line was obvious: the *sun* (resource) is not *hail* (hazard) — two different media. **For wind the
hazard medium IS the resource medium** — both are "wind" — so the line blurs unless we draw it in words:

- **Hazard-tier wind (THIS repo).** *Extreme* wind that **structurally damages the turbine** → physical loss
  (repair / replacement). Rare/severe, off the upper tail of the wind distribution. Modeled here, M0→M4.
- **Performance-tier wind (sibling [`../../../model-gpr`](../../../model-gpr)).** The wind *resource* — the
  everyday wind speed that drives the power curve, generation, and revenue (including curtailment and routine
  variability). Normal operations, not catastrophe. **Out of scope here.**

The hard line: **structural damage from extreme wind here; energy/revenue from the wind resource there.** Stated as
[DD-WN-2](decisions.md) so it is never silently crossed.

## Domain principles for this pipeline

- **Standard interface, not standard physics** — convective wind's two sub-perils have genuinely different physics
  (areal vs site-conditioned), so they get sub-peril-specific coupling *behind the interface hail and wildfire
  already defined*; the loss engine never changes. Splitting convective wind into two sub-perils — rather than one
  "wind model" — is the dual test applied honestly (the same dual test also keeps hurricane and the adjacent turbine
  perils *out* as separate perils, not sub-perils).
- **Basics spot-on** — tail metrics off the *sampled* loss distribution (never the expected-loss shortcut / Method
  0, the old repo's cardinal error); two thresholds kept distinct (event-count μ vs damage-onset); for the rare
  tornado, report metrics with their effective-sample precision and TVaR alongside VaR.
- **Modular from day one** — layer-0 / M0 / M1 are shared; the fork is **only at M2** (coupling differs:
  `strong_wind/` site-conditioned vs `tornado/` areal); **M3 and M4 are shared** (one turbine curve; M4 takes the
  two per-sub-peril {λ, severity} profiles and combines them ONLY by co-sampling both event streams into one sampled
  annual-loss distribution per site — tail metrics read off that one combined distribution — with a
  strong-wind/tornado attribution split). Each sub-peril still ships value on its own (strong wind first — fastest
  path to a real number because the ASCE surface hands the hazard pre-integrated, exactly as FSim did for wildfire);
  the **separate hurricane / tropical-cyclone peril** is a documented wall with a migration path, not built past.

## What success looks like

A reviewable, step-by-step notebook series that takes authored convective-wind hazard definitions to a coherent
*sampled* annual loss distribution for a wind farm (EAL/VaR/PML/TVaR, **% of TIV**), honestly labeled as
inland-convective-exogenous-only — strong wind and tornado both built on coupling machinery the platform already
owns, every step legible, every basic verified, the structure ready for the **separate, deferred hurricane**
(field-intensity) peril build.

## Open questions (to resolve as we plan / in layer-0 & M0)

- ✅ **Reference assets (two — a low-vs-high contrast):** **Traverse Wind Energy Center** (OK, ~999 MW; tornado-alley
  + derecho; high/proving) **+ Shepherds Flat** (OR, ~845 MW; Columbia Gorge; low/baseline). ([DD-WN-10](decisions.md))
- ✅ **Build order:** **strong wind first** (site-conditioned, ASCE RP surface pre-integrated → fastest real number),
  **then tornado** (areal, path-strike + the rare catastrophic tail). ([DD-WN-2](decisions.md))
- **Strong-wind M1 path:** pre-integrated **ASCE RP surface** (the spine; severity is Gumbel/exponential, ξ ≈ 0 —
  the ASCE return-level curve is log-linear) vs the *extraction* alternative (Poisson + GPD fit to bias-corrected
  SPC) — confirm the ASCE surface as the V1 spine at M1, with the SPC fit as the documented cross-check
  ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)). (The bounded GPD with ξ < 0 is
  the **tornado** severity form, not strong wind's.)
- **Physical bound L (settled, with a revisit note):** the old repo used tornado L = 145 m/s (observed Doppler max);
  **V1 adopts L = 113 m/s (the EF5 damage-inferred ceiling)**, corroborated by the old-repo F5 midpoint 111.8 m/s,
  with a logged revisit trigger ([DD-WN-8](decisions.md)). Not "still open" — the choice is made; the revisit note
  is the only residual.
- **Bias correction:** SPC tornado/wind counts are population-biased and the detection of weak events changed over
  time; the rural-low EF bias understates severity at *both* rural sites — decide the bias-correction approach
  before any frequency fit ([AWN-1](assumptions.md)).
- **Turbine TIV basis** — estimate Traverse / Shepherds Flat TIV from $/kW (no registry TIV yet); report % of TIV
  alongside dollars ([AWN-14](assumptions.md)).
