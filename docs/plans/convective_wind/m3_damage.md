# M3 — Wind-Farm Damage (the active plan)

*Map the coupled **3-second peak gust (m/s)** → a **capex-weighted turbine damage ratio**, then
`conditional_loss = Asset_DR × exposure × TIV`. Like hail & wildfire: a **curated, approximate, anchored curve
now**, **accurate curves attached later**. Wind's curve is **net-new** — the old repo had **no turbine-specific
wind fragility** (it borrowed generic Real-Estate curves and hacked gust onto the tornado curve). This is the
InfraSure wedge: an **IEC-survival-anchored, operational-state-aware** turbine curve no incumbent ships.*

**Where this sits:** [M0](m0_input_data.md) → [M1](m1_catalog.md) → [M2](m2_coupling.md) → **M3 (wind-farm damage)**
→ [M4 loss](m4_loss_metrics.md). Built for both wind farms. Notebook: `Notebooks/convective_wind/wind_farm/m3_damage/01_damage`.

> **Built (2026-06-17) — one turbine, TWO sub-peril curves ([DD-WN-16](decisions.md)).** The realized M3 keeps **one**
> turbine object (shared subsystem/capex split + IEC anchor) but carries **two sub-peril fragility curves** that differ
> in **both reach *and* severity** — not reach alone, as this plan first framed it. A tornado at the *same* 3-s gust is
> **more damaging** than straight-line wind (rotation defeats feathering; vertical / pressure-drop / debris loads; the
> EF scale is damage-calibrated — [AWN-32](assumptions.md)), so the **tornado curve has a lower onset *and* steeper rise
> per subsystem**, plus full reach. Realized: onset (DR≥5%) ≈ **44 m/s tornado vs 54 m/s strong wind**;
> `DR_tornado(v) > DR_strongwind(v)` at every gust (DR by EF — tornado / strong wind: EF2 36% / 7%, EF3 77% / 50%,
> EF4 94% / 65%, EF5 ~100% / 65%); strong-wind `E[DR|event] ≈ 2e-4` → EAL ≈ 0.02% of TIV (the ≈0 known-answer check ✓).

---

## The two thresholds — why the curve is **anchored** (read this first)

Wind has **two distinct thresholds**, and keeping them separate is the heart of M3 ([00_hazard_definition](00_hazard_definition.md)):

| Threshold | Value | What it governs | Where it lives |
|---|---|---|---|
| **Meteorological event** μ | **58 mph ≈ 25.9 m/s (old repo: 25.92)** (NWS severe) / EF0 ≈ 29 m/s | what the **catalog counts** (for λ) | M1 |
| **Asset damage-onset** | **IEC 61400 survival speed** ≈ Ve50 ≈ 1.4·Vref ≈ **52–70 m/s** | where the **damage curve leaves zero** | **M3** (here) |

> **So the damage curve is *anchored*: `DR(μ) ≈ 0`.** Most "severe wind" — a gust just over 58 mph — **barely
> scratches a turbine** (turbines are engineered to feather and survive far beyond that). Damage onset is far
> higher, near the **IEC survival speed**, where the curve rises steeply. The reference is explicit: *"for wind
> turbines, account for operational state (feathered vs operating) and the survival wind speed in the curve, not
> just the design speed."* → [DD-WN-11](decisions.md).

This is the **continuous-severity** payoff: unlike wildfire's 6 discrete FLP classes, wind maps a **continuous
3-s gust** through the curve ([hazard_math/03](../../../Learning/ML-DL/InfraSure_related/hazard_math/03_severity_event_loss_distributions.md)).

> **Strong-wind damage ≈ 0 — a known-answer check, not a reason to skip it.** Because the anchored onset (IEC
> survival ~52–70 m/s) sits *above* the strong-wind gust range (even the 10⁶-yr gust ≈ 70–75 m/s — M1), running
> this M3 curve over the strong-wind catalog **must** yield a **≈ 0 EAL**. If it doesn't, the curve is
> **mis-anchored** (the old-repo two-threshold collapse). We still build strong wind **end-to-end** — the ≈ 0 is
> the honest output (the "correctly small number" proof, like wildfire's Hayhurst). M3 models **aerodynamic-overload**
> damage only; strong wind's *material* impact — operational disruption + fatigue/degradation — is the **disruption
> track, deferred** (Performance tier; see [discussion/convective_wind/01 §7a](../../extra/discussion/convective_wind/01_scope_and_sub_peril_taxonomy.md)
> + [AWN-31](assumptions.md)). So M3's curve rigor belongs in the **damaging regime (~52–113 m/s, where tornado
> lives)**, not the strong-wind regime.

**IEC anchor (honest provenance):** the **Vref wind classes** (I/II/III → 10-min mean Vref = 50 / 42.5 / 37.5 m/s)
and the extreme 3-s gust **Ve50 ≈ 1.4·Vref** come from **IEC 61400 / the settled framing**, **not** from
Hazard_Data_Reference (which supplies μ, the EF bins, and the "survival speed + operational state" instruction, but
not IEC numerically). Pin the turbine class for each site from the ASCE/site wind regime and record the chosen
Vref/Ve50 anchor ([AWN-?](assumptions.md)).

> **The 3-s-gust wind-damage-curve group (an OUTPUT / vulnerability grouping, not a peril family).** This single
> 3-s-gust turbine curve is what **tornado, strong wind, and — when it lands — the separate hurricane peril** all
> share: they differ as *perils/sub-perils* (different footprints, frequencies, data products, coupling buckets)
> but converge on the **same vulnerability function** once expressed in 3-s gust. That convergence is a grouping on
> the **damage/output side only** — it does **not** make hurricane a convective-wind sub-peril ([DD-WN-9](decisions.md)).

---

## The curve — IEC-anchored logistic per subsystem (decision → DD-WN-11)

**Anchored logistic curves on the 3-s gust**, per subsystem: `DRᵢ(v) = Lᵢ / (1 + exp(−kᵢ(v − x0ᵢ)))`, with the
**inflection `x0ᵢ` anchored near the IEC survival speed** (so `DRᵢ(μ) ≈ 0` and the rise is steep just past survival).
Mirrors hail's and wildfire's anchored-logistic form (the old repo's `LoadedDamageCurve` / "Anchored Logistic"
family — JRC/PNNL/HAZUS lineage).

- **Why not the old repo's curves:** Strong Wind and Hail mapped to generic **`Real Estate_*`** curves (identical
  to real-estate fragility, **not** turbine-specific), and gust events were **silently routed to the Tornado
  curve** (`interpolate_damage()`, conflating gust vs sustained by swapping curves). **Discard** — the new build
  maps the **3-s peak gust to a single, turbine-specific curve per subsystem**.
- **Why IEC-anchored:** a turbine's vulnerability is set by its **survival/design speed and operational state**
  (feathered vs operating), not by a generic building curve. The anchored form encodes the real physics: ≈0 damage
  through the everyday severe-wind band, steep rise approaching IEC survival, saturating in the violent tail.
- **Approximate / temporary (the honest label):** confidence **Low / Low-Medium**; the IEC anchor is class-level,
  not turbine-model-specific; **zero empirical RE-asset calibration**. Carry these caveats — the accurate-curve
  revamp is deferred (*approximate now, accurate later*, like hail & wildfire).

## The subsystems (from the old-repo `wind_config` / `wind_cost_matrix`)

Reuse the old repo's **subsystem cost-split** (the one genuinely reusable piece — fractions of the 7 active
subsystems sum to 1.00), with **per-subsystem anchors** reflecting which subsystems extreme wind actually reaches:

| subsystem | capex weight | wind reach (old-repo evidence) | V1 curve anchor (3-s gust) |
|---|---:|---|---|
| **rotor_blades** (hub, blades, pitch) | **0.26** | most exposed — both Strong Wind & Tornado curves applied | lowest x0 (first to fail; feathering reduces operating-state load) |
| **nacelle_drivetrain** (gearbox, generator, bearings) | **0.21** | exposed — both Strong Wind & Tornado | low-mid x0 |
| **tower** (steel sections, LPS) | **0.16** | **Tornado reaches it; strong wind does not** (old-repo distinction) | high x0 (fails only in the violent tail) |
| **foundation** (concrete, rebar, scour) | **0.12** | primarily hurricane / whole-structure — a violent (EF4–EF5) tornado may also load the foundation (deferred refinement, see assumptions) | highest x0 (near-rigid) |
| **substation** (transformers, HV switchgear) | **0.09** | — | mid x0 |
| **electrical** (cabling, grid connection) | **0.09** | hurricane | mid-high x0 |
| **civil_infrastructure** (roads, crane pads, O&M bldg) | **0.07** | — | building-like (lower x0) |
| *(monitoring, BESS — inactive)* | 0 | — | — |

The **subsystem distinction is meaningful**: strong wind reaches the **aero** subsystems (rotor/blades,
nacelle/drivetrain) but **not the tower**; a tornado reaches the **tower** too. So strong-wind and tornado damage
curves differ **in which subsystems they activate**, not just in magnitude — encode that. *(Source the weights from
the old-repo `wind_cost_matrix_default.csv` to avoid drift; record any midpoint substitution.)*

## Operational state — feathered vs operating (DD-WN-11, the reference mandate)

The reference requires it explicitly: damage depends on whether the turbine is **feathered** (blades pitched out of
the wind, the survival configuration above cut-out) or **operating** (full aerodynamic load). V1 treatment: assume
the turbine **feathers above cut-out** (the design behaviour) so the curve uses the **survival-state** anchor — but
**document** that a stuck/operating turbine (control or grid failure during the event) would shift the curve **left**
(damage onset at a lower gust). The operating-vs-feathered split is a named, deferred refinement ([AWN-?](assumptions.md)).

## The blend + the unmodeled-TIV note

`Asset_DR(v) = Σ wᵢ · DRᵢ(v)` over the active subsystems. Strong wind activates only the aero subsystems
(rotor_blades + nacelle_drivetrain, ~0.47 of capex); tornado activates those **plus the tower** (~0.63). So a
**strong-wind `Asset_DR` caps lower** (the non-activated subsystems contribute 0) than a tornado `Asset_DR` at the
same gust — the honest, conservative treatment (mirrors hail's ~34% cap and wildfire's ~61% cap). **V1 keeps weights
as-is** (un-activated subsystems contribute 0; **no renormalize-to-1.0**, which would over-count) — recorded as
[AWN-?](assumptions.md); revisit when accurate curves land.

## Mechanism

For each asset and each sub-peril, evaluate `Asset_DR` at the **sampled 3-s gust** (from M2's conditional severity —
**tornado's bounded GPD (ξ<0)** or **strong wind's Gumbel/exponential tail (ξ≈0)**, both capped at L) → a
**conditional damage ratio** → `conditional_loss = Asset_DR(v) × exposure × TIV`. For tornado,
`exposure` is the **swept fraction of turbines** (from M2); for strong wind, `exposure = 1.0` (whole farm). This is
the **conditional loss distribution given an event** — the M4 input.

> **LOTV (basics-spot-on):** M3 emits the **conditional** loss (full loss *given an event of magnitude v*); it does
> **not** multiply by occurrence probability/λ, and it does **not** average over the hit/miss draw. Keeping `p`
> (occurrence/strike) separate from severity is the rule the old repo broke; [M4](m4_loss_metrics.md)'s sampled
> compound engine reunites them — never an expected-loss collapse here.

## Verification

Known-answer: hand-compute `Asset_DR` at a fixed `v` (e.g. `v = μ` → `DR ≈ 0`; `v` near IEC survival → DR rising;
`v → L` → DR saturating) and confirm the blend; `DRᵢ, Asset_DR ∈ [0,1]`, monotone, saturating; **`DR(μ) ≈ 0`** (the
anchor check — the figure from M0 `01_asce_hazard`); strong-wind cap < tornado cap (tower activation);
provenance-as-deliverable (cite subsystem source + IEC anchor + confidence per subsystem); report the conditional
`E[DR | event]` per asset/sub-peril and sanity-check the contrast (Traverse ≫ Shepherds Flat; tornado tail ≫
strong-wind tail at the same site).

## Inputs → outputs

M2 coupled (conditional 3-s gust severity × exposure/swept-fraction) + the subsystem split + IEC anchors + TIV →
`data/convective_wind/<asset>_wind_m3_damage_strongwind.parquet` + `…_tornado.parquet` (conditional DR + loss vs gust) +
`…_m3_summary.json` (the `Asset_DR` curves per sub-peril, subsystem weights/anchors, cap, conditional `E[DR|event]`,
provenance), both assets.

## Assumptions / decisions

**DD-WN-11** (curve = IEC-survival-anchored logistic on 3-s gust, operational-state aware; old-repo Real-Estate /
gust-on-tornado-curve hacks discarded) · [AWN-?](assumptions.md) (turbine class → Vref/Ve50 anchor; IEC numbers from
the settled framing, not Hazard_Data_Ref) · [AWN-?](assumptions.md) (subsystem activation: strong wind = aero only,
tornado adds tower; a violent EF4–EF5 tornado may also load the **foundation** — that activation is a deferred
refinement, V1 leaves foundation tornado-inactive) · [AWN-?](assumptions.md) (operational state = feathered in V1; stuck/operating deferred) ·
[AWN-?](assumptions.md) (un-activated subsystem TIV contributes 0; no renormalize) · curve confidence Low/Low-Med
(carry) · **scalar DR per gust** (a *conditional-DR distribution* — uncertainty around the mean DR — deferred).

## Deferred (named)

Accurate / calibrated turbine curves (the damage-curve revamp — InfraSure wind × wind-farm library) ·
turbine-model-specific anchors (vs class-level Vref/Ve50) · operating-vs-feathered split (control/grid-failure
state) · conditional-DR **distribution** (not a scalar mean) · debris-impact and cascading inter-turbine effects —
all separate, deferred.

**Next → M4 (wind-farm loss & metrics):** the **shared compound-Poisson/NegBin Monte-Carlo**, reused — sample
events/yr per sub-peril, draw per-event conditional loss from M3, aggregate → EAL/VaR/PML/TVaR off the **sampled**
distribution, **% of TIV**; strong wind well-populated, tornado rare ([learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md)).
