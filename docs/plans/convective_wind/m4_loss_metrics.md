# M4 — Wind-Farm Loss & Metrics (the active plan) · *the finale, on the shared engine*

*Assemble M1's frequency + M3's conditional severity into **annual loss vectors** via the **shared compound-Poisson/
NegBin Monte-Carlo** (reused from hail & wildfire), then read **EAL / VaR / PML / TVaR** off the **sampled**
distribution, as **% of TIV**. This is the exact layer the old repo broke — its **own worked example proves it was
~12× wrong for strong wind**. Done right, and verified, on an unchanged engine.*

**Where this sits:** [M0](m0_input_data.md) → [M1](m1_catalog.md) → [M2](m2_coupling.md) → [M3](m3_damage.md) →
**M4 (loss & metrics)**. Both wind farms (Traverse proving + Shepherds Flat baseline), both sub-perils.
Notebook: `Notebooks/convective_wind/wind_farm/m4_loss_metrics/01_loss_metrics`.

## Reuse the engine (modular-from-day-one)

The hail/wildfire M4 compound-MC **aggregation / metrics / Method-0 contrast / %-of-TIV** machinery ports
**verbatim** — *the shared engine does not change for wind* (**one shared MC, % of TIV**, [DD-WN-12](decisions.md)).
Only the **per-year sampling** changes per sub-peril, and both forms already exist (tornado = hail's areal form;
strong wind = wildfire's site-conditioned form):

| | **Strong wind** (site-conditioned) | **Tornado** (areal hit-or-miss) |
|---|---|---|
| count/year | **`N ~ Poisson(λ)`** (λ from M1's ASCE surface; `fano=1`) | **`N ~ Poisson/NegBin(λ_collection)`** then **`Bernoulli(p_hit)`** per event (path-aware Minkowski, M2) |
| thinning | **none** — the occurrence *is* the gust at the site (no spatial factor) | **`Bernoulli(p_hit)`** per EF class (M2) |
| severity | **draw a 3-s gust ~ Gumbel/exponential (ξ≈0), capped at L** → M3 conditional loss (whole-farm) | **draw EF/gust ~ posterior / bounded GPD (ξ<0)** → M3 conditional loss × **swept fraction** of turbines |
| frequency regime | **high — well-populated tail** | **rare — sparse, exercises [learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md)** |

So: each simulated year, per sub-peril, draw `N` events; for each, **sample a 3-s gust** from M1/M2's severity
(tornado bounded GPD ξ<0; strong wind Gumbel/exponential ξ≈0) and add its **full conditional loss** from M3
(tornado: × swept fraction on a strike); `AEP_year` = annual total (capped at TIV), `OEP_year` = largest single
event. **Run in % of TIV** (TIV-free); dollars via TIV (estimated where not in the registry — [AWN-?](assumptions.md)).

**How the two sub-perils combine (the no-double-count rule — [DD-WN-12](decisions.md); [AWN-29](assumptions.md)).** Two separate
per-sub-peril `{λ, severity}` profiles go **IN**; they are combined **ONLY by co-sampling both event streams into
ONE annual-loss distribution per simulated year**, and **ALL tail metrics (VaR / PML / TVaR) are read off that ONE
combined distribution — never by summing per-sub-peril profiles or quantiles.** M4 reports **total convective-wind
risk with a strong-wind/tornado attribution split** — not two incomparable pipelines (per the settled notebook
structure).

- **EAL IS additive** across the sub-perils ([AWN-29](assumptions.md); linearity of expectation): `EAL_combined = EAL_tornado + EAL_strongwind`,
  and a per-sub-peril EAL split is meaningful. **But VaR / PML / TVaR are NOT additive** — summing per-sub-peril
  tail metrics overstates the joint tail (it assumes the worst tornado year and the worst strong-wind year
  coincide). **Caveat:** EAL additivity is exact for **gross / uncapped** loss; once `AEP` is **capped at TIV**,
  even EAL must be read off the combined sample.
- **Disjointness (explicit assumption — [AWN-28](assumptions.md)).** Tornado and strong wind are treated as
  **DISJOINT, independent** event streams — **disjoint by data product** (the ASCE basic-wind surface is
  **non-tornadic by construction**; tornado = the SPC Tornado record). This is what makes **adding their EALs valid**
  (no shared physical event). In V1 it is also safe because strong-wind damage is ≈0 (gusts stay below the IEC
  survival onset). It is a **classification/data-product assumption, not a physical law** — flag it.

## LOTV (basics-spot-on — the whole point of M4)

**Sample** occurrence (Poisson/NegBin) and **sample** severity (per-sub-peril gust draw → M3 curve — tornado
bounded GPD ξ<0, strong wind Gumbel/exponential ξ≈0) — **never** `× λ`
or `× p_hit` or `× E[loss]`. Keeping stochastic stochastic past every nonlinearity is the rule; the expected-loss
collapse (Method 0) is the rule the old repo broke and the one we never take ([DD-WN-13](decisions.md);
[principles/basics_spot_on](../../principles/basics_spot_on.md)).

## The Method-0 cardinal error — wind is the old repo's *own* counter-example

The old repo's worked example (`strong-wind-var-worked-example.md`) is its **self-audit proving the error — for
strong wind specifically**. Re-demonstrate it as the contrast every wind M4 metric refuses:

- **Method 0 (wrong):** store each event's loss as `damage% × value × spatial_factor` — the **expected loss
  averaged over the Bernoulli hit/miss draw**, summed deterministically per year, then fit a distribution to the
  annual sums. By the Law of Total Variance this preserves the **mean** but discards the **dominant (bimodal)
  variance**.
- **Method 3 (correct, compound-Poisson):** `N ~ Poisson(λ)`, each draws full conditional severity, annual loss =
  sum, read empirical quantiles. **One coherent distribution → all five metrics coherent.**

**The proof (verbatim from the old repo's example, $150M / 100 MW / Strong Wind, λ_asset = 0.25):**

| Metric | Method 0 (fitted) | **Method 3 (truth)** |
|---|---|---|
| EAL | $4.98M | $4.83M |
| VaR_99 ≡ PML_100 | **$8.99M** | **$108.94M** (~**12×** higher) |
| TVaR_99 | n/a | $141.19M |

EAL agrees (linearity of expectation); only the **tail** diverges (`Var[Bernoulli(p)·L] ≈ pL²` ≫ `Var[p·L] = 0`).
The repo also produced an **impossible 175×** VaR_99-vs-PML_500 ratio for Strong Wind — the signature of fitting
PML and VaR as **two incoherent objects**. Our fix: **one severity model + one λ → all metrics**, the way the old
repo's *correct* tornado F-scale model (commit `52db8e3`) did — *"one model → five coherent readings."*

## The frequency-regime split — well-populated vs sparse (learning-10)

The Method-0 error **bites at high frequency** and is "wrong but harmless" at low frequency — so the two wind
sub-perils sit on opposite ends, and we treat their Monte-Carlo precision differently:

- **Strong wind = high-frequency → well-populated tail** (the *Matrix* analogue from wildfire). Method 0 is **12×
  wrong** here, so the sampled engine is non-negotiable. Effective sample is large; metrics are tight.
- **Tornado = rare → sparse Monte-Carlo** (the *Hayhurst* analogue). The near tail empties: a metric is only as
  precise as its **effective** sample — `λ·M` events for the mean, `M·(1−α)` years for a quantile
  ([learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md);
  [hazard_math/06](../../../Learning/ML-DL/InfraSure_related/hazard_math/06_monte_carlo_error_effective_sample_size.md)).
  So for tornado we **(a) quote a standard error / seed-stability**, **(b)** set the known-answer tolerance from
  that error (`max(rel_floor·analytic, k·SE)`, never a fixed band), and **(c)** note the squeeze: a rare peril can
  give **VaR = $0 (Poisson floor)** at feasible M out to large return periods. **→ TVaR is mandatory for tornado**:
  when VaR floors to 0, `TVaR → E[severity | strike] = Σ_F P_F·L_F`, always `> EAL` by ~`1/λ_asset` — the only
  coherent read of the catastrophic-but-rare tail.

## Known-answer checks (before trusting any metric)

- `EAL ≈ λ · E[loss | event]` (mean preserved across Method 0 and Method 3 — the linearity check). ✓
- `zero-loss-year fraction ≈ exp(−λ_effective)` per sub-peril (strong wind: λ; tornado: `λ_collection · E[p_hit]`). ✓
- `AEP ≥ OEP` every year. ✓
- **Tornado VaR/TVaR floor:** confirm VaR floors to 0 where `λ_asset · RP ≤ 1`, and that **TVaR stays > EAL** there
  (the sparse-hazard remedy). ✓
- **Method-0 contrast run:** reproduce the ~12× strong-wind gap on our own numbers (EAL matches, VaR diverges). ✓

## Expected (the low-vs-high payoff)

| | Shepherds Flat (OR baseline) | Traverse (OK proving) |
|---|---|---|
| **strong wind** | low λ, modest tail | **material** — frequent severe straight-line wind / derecho corridor |
| **tornado** | ≈ 0 (Gorge — near-zero tornado) — **VaR floors, report TVaR** | **rare but catastrophic** — sparse tail, TVaR load-bearing |

The model behaving: **near-zero tornado for the Gorge baseline; a material strong-wind EAL + a rare catastrophic
tornado tail for the tornado-alley proving asset.** (Exact numbers are produced at build — *do not quote until the
notebook runs*; the curve, the bias-correction, and the ASCE RP convention are the binding uncertainties below.)

## Inputs → outputs

M1 manifests (`λ`, per-sub-peril severity — tornado bounded GPD ξ<0, strong wind Gumbel/exponential ξ≈0, `fano`) +
M2 coupling (tornado `p_hit`/swept fraction; strong-wind `exposure=1`) + M3 conditional loss (DR vs gust) + TIV →
`data/convective_wind/<asset>_wind_m4_annual_vectors.parquet` (AEP/OEP per sim-year, per sub-peril + combined) +
`…_m4_metrics.json` (EAL/VaR/PML/TVaR in **$ and % of TIV**, with SE), both assets. **Tail metrics are read off
the combined per-year distribution, never summed from per-sub-peril metrics; only EAL is reported as an additive
split** (see the combine rule above).

## Assumptions / decisions

Reuse engine (modular — **one shared MC**, [DD-WN-12](decisions.md)) · strong wind `frequency = Poisson(λ)`, fano=1
(profile-assembly [DD-WN-3](decisions.md); site-conditioned [DD-WN-4](decisions.md)) · tornado `λ_collection · p_hit`,
NegBin-capable (areal Minkowski thinning [DD-WN-5](decisions.md)) · **two sub-perils combined by co-sampling into ONE
distribution; tail metrics off the combined sample, EAL additive only** ([DD-WN-12](decisions.md); [AWN-29](assumptions.md)) ·
**tornado ⊥ strong wind — disjoint, independent event streams** (disjoint by data product; the ASCE basic-wind surface
is non-tornadic by construction — [AWN-28](assumptions.md)) · **Method-3 only, never Method 0**
([DD-WN-13](decisions.md); [principles/basics_spot_on](../../principles/basics_spot_on.md)) · **TVaR mandatory for
tornado** (sparse, [learning-10](../../learning_logs/10_monte_carlo_effective_sample_size.md)) · gross physical only
(no deductibles/limits/BI — deferred) · MC sized from the effective-sample law (tornado needs more years than strong
wind for the same precision) · **% of TIV alongside $** ([DD-WN-12](decisions.md); [AWN-?](assumptions.md); TIV
estimated where not in registry).

## Caveats (honest)

- **The binding uncertainties are upstream of M4:** the **anchored, approximate turbine curve** ([DD-WN-11](decisions.md)),
  the **SPC bias-correction** (tornado frequency), the **ASCE RP convention** (EVD vs empirical — drives the
  strong-wind tail), the **rural-low EF bias** (tornado severity likely understated), and **single-site** (no
  portfolio correlation — strong wind's broad-swath correlation is documented, deferred).
- **Tornado metrics are sparse-MC-limited** — quote with SE; VaR may floor to 0; **TVaR is the honest tail read**.
- Metrics are **real but approximate** (curve- and bias-correction-limited) — don't quote as final.

## Next

**M0→M4 convective wind × wind-farm (one peril, two sub-perils: strong wind + tornado) complete** → the cross-peril
close-out, and the **separate, deferred hurricane / tropical-cyclone peril** (related to convective wind only through
the shared 3-s-gust wind-damage curve) — Holland wind field → swath grid → hurricane-wind curve (`x₀ ≈ 160 mph`),
where portfolio correlation + EVT become load-bearing ([discussion/convective_wind/02](../../extra/discussion/convective_wind/02_coupling_buckets_and_wind.md)).
**Forward-compat double-count flag:** unlike tornado vs strong wind (disjoint by data product), **hurricanes spawn
tornadoes and produce straight-line wind**, so a TC-spawned tornado could appear in **both** the V1 tornado stream
**and** a hurricane catalog — when hurricane lands, treat the V1 tornado catalog as **inland-convective only** or
bind hurricane's sub-perils with a shared event identifier and sample jointly ([DD-WN-9](decisions.md); [AWN-30](assumptions.md)).
Then the production folder architecture (Hazard 3 of 3 done — *not before*).
