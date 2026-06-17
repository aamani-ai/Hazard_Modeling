# Decisions — wind route-zero session

The **canonical** wind design decisions live in [`docs/plans/convective_wind/decisions.md`](../../../plans/convective_wind/decisions.md)
(`DD-WN-1..13`, ADR-style with revisit triggers). This file indexes them and records the **session-level
meta-decisions** (how we worked, not what the model is).

## Canonical wind decisions (index → `plans/convective_wind/decisions.md`)

| ID | One-line | Realizes in |
|---|---|---|
| DD-WN-1 | Wind is a **sub-peril family** — split on the dual test (footprint AND data metric) | framing |
| DD-WN-2 | Route = **inland-convective** (strong wind → tornado); hurricane deferred; hazard-vs-performance scope boundary | framing |
| DD-WN-3 | Strong-wind M1 = **profile-assembly from the ASCE RP surface** (pre-integrated, no λ-fit) — the FSim analogue | M1 |
| DD-WN-4 | Strong-wind coupling = **site-conditioned** (bucket 3) — reuse wildfire's thin M2 | M2 |
| DD-WN-5 | Tornado coupling = **areal hit-or-miss** (bucket 1) — reuse hail's Minkowski, path-aware thin rectangle | M2 |
| DD-WN-6 | Hazard observable = **3-second peak gust** (the universal metric) | layer-0 |
| DD-WN-7 | **Two thresholds** distinct — meteorological event (NWS/EF) vs asset damage-onset (IEC survival) | layer-0 |
| DD-WN-8 | Severity = **bounded GPD** on 3-s gust, truncated at L≈113 m/s; ASCE RP surface = the pre-fit EVT curve | layer-0/M1 |
| DD-WN-9 | Hurricane / **field-intensity (bucket 2) deferred** — the unbuilt coupling type | — |
| DD-WN-10 | **Two sites** — Traverse OK (high) vs Shepherds Flat OR (low) | M0 |
| DD-WN-11 | Turbine damage = **anchored subsystem logistic** on 3-s gust; IEC-survival onset; operational-state aware; approximate | M3 |
| DD-WN-12 | Metrics off **one shared compound-Poisson/NegBin MC**; % of TIV alongside $ | M4 |
| DD-WN-13 | **Never the expected-loss shortcut (Method 0)** — every metric off one sampled distribution | M4 |

## Session-level meta-decisions

### 1. Hazard 3 = wind, paired with wind farms (not "another solar peril")
**Decision.** Pick the hazard that is *most material* to a new asset class — wind farms — over a hazard with
little wind-farm effect. **Rationale.** Materiality-first (the Matrix lesson); wind is wind turbines' dominant
catastrophic peril; and it forces the **sub-peril decomposition** muscle we hadn't exercised (hail/wildfire were
each single-phenomenon). It's also the roadmap's hazard 3.

### 2. Read the reference *before* drafting — and accept the coupling correction it forced
**Decision.** Follow the owner's process: extract `Hazard_Data_Reference` first, then draft. **Rationale.** It
materially corrected the coupling story (strong wind is **site-conditioned**, not areal hit-or-miss as I'd first
said) — proof that grounding-before-asserting pays. Honest correction surfaced to the owner, not silently changed.

### 3. Notebook structure — fork only at M2; M3 shared; M4 combines sub-perils
**Decision.** Coupling differs only at M2 → fork there (`strong_wind/` + `tornado/`); the turbine curve (M3) is
one object → shared; M4 **combines** both sub-perils into one annual-loss distribution + per-sub-peril split.
**Rationale.** You report *total* wind risk per site, not two incomparable PMLs; fork where physics differs,
share where it doesn't. Reconciled all docs to this after review flagged the inconsistency.

### 4. Build + adversarially review + fix via workflows (Ultracode was on)
**Decision.** Author the doc set with a build workflow (research → draft → review) and a fix-up workflow
(fix → verify). **Rationale.** Exhaustiveness + an independent adversarial pass — which earned its keep by
catching the stale DD-WN cross-ref defect a newcomer would have tripped on. (Ultracode is now off; future routine
work reverts to direct edits.)

### 5. Statistical known-answer tolerance (the MC-error sub-task)
**Decision.** A Monte-Carlo known-answer check uses `max(rel_floor, k·SE)`, not a fixed relative band.
**Rationale.** A rare-peril EAL is itself MC-noisy (effective sample = λM, not M); demand only the precision the
run actually has. Captured as `learning_logs/10` + KB note `hazard_math/06`.

### 6. Scope discipline — left `conus_grid/` and the personal-KB note uncommitted
**Decision.** Commit only the wind route-zero I built; do **not** commit `conus_grid/` (a separate session's
work) or the personal-KB note 06 (a separate repo) without the owner's say-so. **Rationale.** Don't commit work
I didn't create / wasn't asked to — especially to a public repo.
