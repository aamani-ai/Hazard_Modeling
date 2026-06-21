# 05 · The emit object — what M3 puts on the wire  🟢 DECIDED (v1)

The headline of the damage layer. What object does the damage stage emit, per event, per failure
unit? Everything downstream hangs on it — which risk metrics are honest, what the library must
produce, how much sourcing is needed. The earlier framing treated this as a *fidelity ladder*
("how high do we climb: scalar → spread → states → distribution?"). **That framing is wrong, and
the reason it's wrong is the founding incident of this whole project.** This doc reframes the
decision around a single forcing rule — **the first nonlinearity** — and shows scalar-vs-spread is a
*derivation*, not a matter of appetite.

*Source key:* depends on [`01`](01_granularity.md) (emit is **per failure unit, then summed**),
[`02`](02_x_axis_intensity_variable.md) (input is **univariate**), and
[`04`](04_curation_derivation.md) (curation **constrains** the emit form — the curve's functional
form sets what *can* be emitted); principles = `basics_spot_on` (this *is* its incident),
`system_coherence_over_local_elegance`, `hazard_asset_specificity`. `[OURS]` derived; `[REF]`
inherited.

---

## 0 · Why this is the basics-spot-on decision, not a fidelity dial

The old model stored each event's loss as `damage% × value × spatial_factor` — i.e. the **expected**
loss, the random variable collapsed to its mean. By the Law of Total Variance that preserves the mean
and **discards the dominant variance term**; VaR₉₉ came out **~12× understated** `[REF]`. EAL
survived (linearity of expectation); every shape-dependent metric broke.

The emit-object choice is *exactly* that decision, at *exactly* that spot. "Emit a scalar mean DR" is
the modern spelling of "store the expected loss." So this is not a question of how much fidelity we'd
*like* — it is the question of whether we re-commit the original sin. That reframes everything below.

> **`basics_spot_on` Axiom 3 `[REF]`.** *Stochastic must stay stochastic past every nonlinearity.*
> The moment you replace a random variable with its expectation **upstream of a nonlinearity**, you
> have silently broken the tail, because `E[f(L)] ≠ f(E[L])`.

---

## 1 · The forcing rule: find the first nonlinearity

The decision is not "which rung." It is: **where is the first nonlinearity downstream of the emit,
and does a scalar mean survive it?**

```
   emit  -->  [ ... downstream operations ... ]  -->  metric

   if everything from emit to the metric is LINEAR (only sums, scalar multiplies):
        E[ Σ Lᵢ ] = Σ E[Lᵢ]      <- scalar mean is EXACT. scalar is CORRECT, not merely cheap.

   the instant a NONLINEARITY sits between emit and metric:
        E[ f(L) ] ≠ f( E[L] )    <- scalar mean is WRONG, and wrong SILENTLY (looks fine, is biased).
```

So the emit object is **dictated by the metric and the terms**, not chosen by taste. The job is to
enumerate the nonlinearities on the path and emit the simplest object that survives all of them.

### 1.1 · The nonlinearities on our actual path

There are exactly three classes between a damage curve and a reported metric, and we already know
where each lives:

```
   N-cap    SATURATION / the per-unit cap Lᵢ        <- doc-08: each failure unit caps at Lᵢ.
            min(cap, DR·v) is nonlinear.               ALREADY PRESENT, even with no financial terms.

   N-fin    DEDUCTIBLE / LIMIT / per-occurrence      <- doc-06 (parked): max(0, L−d), min(L, limit).
            financial terms. nonlinear.                NOT in v1 (gross/occurrence), but coming.

   N-quant  THE QUANTILE OPERATOR ITSELF             <- VaR/PML/TVaR are quantiles of the loss
            VaR, PML, TVaR.                              DISTRIBUTION. a mean carries no quantiles.
                                                         this nonlinearity is the METRIC, unavoidable.
```

The metric you price decides which of these are on your path:

| Metric | Nonlinearities on path | Scalar mean survives? |
|---|---|---|
| **EAL** | N-cap only (if it binds) | **Yes — iff the cap rarely binds** (§2) |
| **VaR / PML / TVaR** | N-quant (always) + N-cap | **No** — quantiles need the distribution |
| **net-of-terms EAL or tail** | N-fin + N-cap (+N-quant for tail) | **No** — terms are nonlinear |

---

## 2 · The subtlety the old ladder missed: the cap is *already* a nonlinearity `[OURS]`

Even in v1, with **no** financial terms, we are not in the clean linear world — because
[`01`](01_granularity.md) caps each failure unit at `Lᵢ` (saturation), and saturation
is nonlinear:

```
   loss for unit i  =  min( capᵢ , DRᵢ(x) · valueᵢ )

   summing SCALAR means:    Σ min( capᵢ , E[DRᵢ]·vᵢ )
   the TRUE expected loss:  E[ Σ min( capᵢ , DRᵢ·vᵢ ) ]

   these are EQUAL only when the cap doesn't bite inside the spread.
   if the DR distribution has mass near/above the cap, Jensen's inequality kicks in
   and the scalar OVERSTATES (the cap clips the high tail the mean didn't know about).
```

So the honest statement is **not** "scalar mean gives correct EAL." It is:

> **Scalar mean gives correct EAL *only while the cap rarely binds.* `[OURS]`** This is precisely the
> condition the hail A22 known-answer check encodes (capped-MC-mean ≈ uncapped-analytic EAL holds
> *only* when the cap rarely binds and no financial terms apply). The emit object and the
> known-answer check are the same fact seen twice — which is why this doc and [`06`](06_metrics_and_tail_honesty.md)
> are tightly coupled.

This matters because it means "scalar for EAL" is not unconditionally safe — it carries a *checkable
condition*, and stating that condition is part of being basics-spot-on rather than plausibly-wrong.

---

## 3 · The decision

Three sub-decisions, cleanly separable.

### 3.1 · Q-a — the INTERFACE: make the seam distribution-ready (build once, up front)

```
   decision: the SEAM (the parquet schema, the M4 consumer contract) is DISTRIBUTION-CAPABLE.
             it can carry a scalar OR a spread OR a discretized distribution.
   why:      modularity (build the interface up front, fill implementations per cell). a
             distribution-ready interface with scalar v1 CONTENT is cheap insurance against
             re-plumbing M4 when the first tail metric or financial term arrives.
   cost:     ~nil. it's a schema decision, not a sourcing decision. you reserve the column;
             you don't have to fill it.
```

This is the `modularity_and_scaling` move exactly: the seam is the unit of growth, designed before
the content. We do **not** want to discover at the first VaR request that the schema can only hold a
mean.

### 3.2 · Q-b — the CONTENT: emit the simplest object that survives the path's nonlinearities

```
   v1 CONTENT rule (the forcing rule applied):

   IF deliverable = EAL  AND  cap rarely binds  AND  no financial terms:
        -> emit SCALAR MEAN DR.  (correct, not merely convenient — §1, §2)

   IF deliverable includes VaR/PML/TVaR  (N-quant)  OR  cap binds materially (N-cap)
   OR  financial terms apply (N-fin):
        -> emit a SPREAD (≥ rung 2: mean + a dispersion, or states, or a discretized dist).
           a scalar is structurally wrong here; no caveat rescues it.
```

So v1 fills **scalar where the path is effectively linear** and **a spread where any nonlinearity
bites**. This is the same earn-the-complexity discipline as docs 08 and 00x, but with a *precise*
trigger (a nonlinearity) rather than a judgment of appetite.

### 3.3 · Q-c — UNIFORM vs PER-PERIL: uniform interface, per-source content `[OURS]`

The old framing posed this as either/or ("one emit object repo-wide" vs "per-peril"). It dissolves:

```
   the INTERFACE is UNIFORM      -> always the same distribution-capable object (Q-a). built once.
   the CONTENT follows the SOURCE -> scalar where the curve is a published MDR (the source only
                                     gives a mean); a STATE VECTOR where it's fragility-derived
                                     (the source natively carries P(state)); a spread where
                                     elicited. (Methodology §6's own logic.)

   => NOT "one object" vs "many objects". ONE interface, source-driven fill.
      a fragility-derived cell emits states into the same seam a published-MDR cell emits a scalar into.
```

This also respects `hazard_asset_specificity`: standardize the interface, specialize the content to
what each peril's evidence actually supports.

---

## 4 · The four rungs, re-read as "what survives which nonlinearity"

The ladder isn't a fidelity preference; it's a map of *which nonlinearities each object can pass
through intact.*

| Rung | Object | Passes N-cap? | Passes N-fin? | Passes N-quant? | When it's the right fill |
|---|---|---|---|---|---|
| **1** | scalar mean DR | only if cap rarely binds | no | **no** (no quantiles) | EAL, linear path, no terms |
| **2** | mean + dispersion | yes (carries spread) | yes | yes (approx tail) | tail metrics, cheap upgrade; must assume a spread form |
| **3** | damage-state vector P(state) | yes | yes | yes | **fragility-derived** sources; needs state→cost map |
| **4** | discretized distribution | yes | yes | yes (best) | strongest tail (OASIS-style); most sourcing |

The honest cost of climbing (why scalar is the v1 default where it's *correct*): moving off scalar
costs (i) **choosing the spread's form** per hazard (beta on [0,1]? lognormal? elicited min/mode/max?),
(ii) **re-parameterizing** the library curves that today emit only a mean, and (iii) **finding
validation data to calibrate the spread** — scarcer than data for the mean. So we climb **only where a
nonlinearity forces it**, not everywhere.

---

## 5 · What the emit object physically is (per [`01`](01_granularity.md) + [`02`](02_x_axis_intensity_variable.md))

Pinning the shape so it's unambiguous:

```
   PER failure unit i, at a univariate intensity x (doc-00x):

   emit_i(x) = a distribution-capable object over the damage ratio DRᵢ ∈ [0, capᵢ]
               v1 content: a scalar E[DRᵢ](x)   (where the path is linear)
                           OR a spread/states   (where a nonlinearity bites)

   loss_i = ( emit_i applied to value_i )  [capped at capᵢ]
   asset loss = Σ_i loss_i                  (doc-08 summation; NO grouping object)

   KEY: keep emit_i STOCHASTIC (a distribution, even if degenerate-scalar in v1) all the way
   to wherever the FIRST nonlinearity sits, and only then collapse. never collapse upstream of N-cap,
   N-fin, or N-quant. (Axiom 3.)
```

The phrase "even if degenerate-scalar in v1" is the bridge: the *interface* always speaks
distribution; v1 *content* may be a point mass; the discipline is never to collapse the point mass
*before* a nonlinearity that would have seen its spread.

---

## 6 · What this commits us to

- **The emit object is decided by the first nonlinearity, not by fidelity appetite.** Enumerate
  N-cap / N-fin / N-quant on the metric's path; emit the simplest object that survives all of them.
- **Interface is distribution-ready, built up front** (Q-a) — cheap insurance, a schema decision.
- **v1 content is scalar where the path is linear** (EAL, cap rarely binds, no terms) **and a spread
  where any nonlinearity bites** (Q-b).
- **Uniform interface, per-source content** (Q-c) — scalar for published-MDR sources, state-vector for
  fragility-derived, into the same seam.
- **Scalar's EAL-safety is conditional** ("cap rarely binds") and that condition is the A22
  known-answer check — the hinge to [`06`](06_metrics_and_tail_honesty.md).
- **Never collapse the random variable upstream of a nonlinearity** (Axiom 3) — the whole point.

**Parked / downstream:** which metrics ship under scalar + the caveat language ([`06`](06_metrics_and_tail_honesty.md));
the spread *form* per hazard (the climb, when N forces it); financial terms N-fin
([financial-terms (parked)](06_financial_terms_and_scope_edges.md)).

---

## 7 · Open / revisit triggers

- **Does the cap bind materially in any built cell?** If hail/wildfire/wind caps bite inside the
  spread, scalar EAL is already biased there (§2) and that cell must climb to rung 2 *for EAL itself*,
  not just for the tail. Needs a per-cell check against the curve's saturation behavior. **The most
  decision-relevant open item.**
- **The spread form, when we climb.** Beta-on-[0,1] is the natural default for a bounded DR, but
  per-hazard validation data may favor lognormal or elicited three-point. Deferred until a nonlinearity
  forces the climb (don't choose a form we're not yet using).
- **Fragility-derived cells and the state→cost map.** Rung 3 needs a state→cost-ratio map (doc-00 §2's
  worked example). Confirm which cells are fragility-native and would emit states rather than a scalar.
- **Interface schema specifics.** The exact distribution-capable representation (parametric tag +
  params? discretized bins? both?) is an implementation choice for the seam — flagged, not fixed here.

---

## 8 · Status

🟢 **Decided for v1.** The emit object is reframed off the fidelity ladder and onto the **first-
nonlinearity** forcing rule — the basics-spot-on decision at the spot the old model broke. v1: a
**distribution-ready interface built up front**, filled with **scalar content where the path is
linear** (EAL, cap rarely binds, no financial terms) and a **spread where any nonlinearity (cap,
terms, or the quantile operator) bites**; **uniform interface, per-source content**. Scalar's
EAL-safety is conditional on the cap rarely binding — the explicit hinge to
[`06`](06_metrics_and_tail_honesty.md), the natural next doc. The one open item that could change a
*built* cell today is whether its cap binds materially (§7).

*Links:* [`01` grain](01_granularity.md) (emit is per-unit, summed) ·
[`00x x-axis`](02_x_axis_intensity_variable.md) (univariate input) ·
[`06` metrics](06_metrics_and_tail_honesty.md) (the consumer — which metrics are honest) ·
[financial-terms (parked)](06_financial_terms_and_scope_edges.md) (N-fin) · `basics_spot_on` (this is its
incident; Axiom 3) · `system_coherence_over_local_elegance` · `hazard_asset_specificity`.
