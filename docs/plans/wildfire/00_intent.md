# 00 — Intent

*The seed for the wildfire → solar pipeline. Captured after the scope discussion, before M0 planning.*

## The goal

Take the **second peril — wildfire — and build the whole end-to-end workflow in notebooks**, step by step,
solar-first then wind, exactly as hail was built. This is the test of **"standard interface, not standard
physics"**: wildfire's physics differ from hail's (site-conditioned, not areal hit-or-miss), but it must
plug into the *same* downstream loss engine. Each step legible, every basic verified.

## Why wildfire (second)

It exercises a **different coupling type** (bucket 3, site-conditioned) than hail (bucket 1, areal) — so it
proves the M1→M4 interface generalizes rather than being hail-shaped. It's hazard 2 of 3 in the plan
(hail → wildfire → wind), and we have rich prior material (a legacy model, a public-data lab, and industry
loss evidence) to mine and improve on.

## What V1 is — and is NOT (the honest label, settled)

> **Wildfire × Solar V1 models *exogenous geographic (wildland) wildfire only*** — the asset as a **receptor**
> of a landscape fire that reaches it. Per the kWh 2026 evidence, ~84% of PV fire *loss events* are instead
> **equipment-driven on-site brushfires** (a different ignition process where the plant is the *source*), and
> only ~4% of fire loss falls in high-wildfire-risk geography. **Equipment-driven brushfire — plus BESS
> thermal runaway, smoke-soiling, and PSPS — are distinct, deferred perils**, each able to plug into the same
> engine later. **V1 does not claim to cover total PV fire risk.** ([DD-W1](decisions.md))

This honesty is *basics-spot-on* applied to scope: a correct tail on a mislabeled peril is still a
credibility failure — the exact thing the rebuild exists to escape.

## The two sides

1. **Input data (M0).** Understand the raw wildfire hazard data — **two public USFS products** that are two
   views of the *same* FSim simulation: **WRC 2.0** (collapsed CFL/FLEP, 30 m) and **native FSim** (full
   FLP1-6 histogram, 270 m). Sourced **directly from public rasters — no Hydronos, no secret** ([DD-W3](decisions.md)).
   Mine the legacy model + the `wildfire_analysis_lab` for *data plumbing and domain info only* — rebuild all
   math.
2. **The model (M1 → M4).** Boundary-zonal catalog → **site-conditioned** coupling → **BoS-weighted** damage
   → loss distribution & metrics on the **shared compound-NegBin MC** — grounded in the
   [data dictionary](../../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md), the A-series, and
   `hazard_math`.

## Domain principles for this pipeline

- **Basics spot-on** — tail metrics off the *sampled* loss distribution (never expected loss); BP is the only
  *annualized* layer (CFL/FLEP/FLP are conditional-on-fire — annualize via ×BP); verify the BP scale divisor
  and the FLEP↔FLP identity against source before trusting numbers.
- **Standard interface, not standard physics** — wildfire is *site-conditioned*; build its coupling/damage as
  wildfire-specific physics behind the interfaces hail already defined; the loss engine never changes.
- **Modular from day one** — each layer emits a clean named object; the wind cell reuses the shared M0/M1.

## What success looks like

A reviewable, step-by-step notebook series that takes the public wildfire hazard surface to a coherent
*sampled* annual loss distribution for a solar asset (EAL/VaR/PML/TVaR, % of TIV), honestly labeled as
exogenous-wildfire-only — every step legible, every basic verified, the structure reusable for wind.

## Open questions (to resolve as we plan / in M0)

- ✅ **Reference assets (two — a low-vs-high contrast):** **Hayhurst Texas Solar** (TX desert; baseline; same
  asset as hail, for cross-peril coherence) **+ Matrix Pleasant Valley** (ID sagebrush; BP ≈ 4.7%/yr; the
  high-fire *proving* asset, picked by a 38-asset WRC screen). Validates the model across a ~190× exposure
  range — a near-zero signal at Hayhurst, a material one at Matrix.
- Native **FLP1-6 (270 m)** as primary severity vs WRC 30 m intensity — confirm 270 m is sufficient for the
  reference asset's scale (it very likely is for utility solar).
- The **solar-site "oozing"** question (WRC suppresses intensity on developed pixels) — resolve the land-cover
  treatment of PV sites *before* M2 (it decides whether on-site hazard comes from surrounding fuel).
- One notebook per candidate in M0 (01 WRC, 02 FSim) — confirmed; same granularity as hail.
