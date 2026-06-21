# 06 · Metrics & tail honesty — what ships, and what we refuse to ship  🟢 DECIDED (v1)

The direct consumer of [`05`](05_emit_object.md), and the last of the foundational decisions. Given
that v1 emits a **scalar** where the path is linear, *which risk metrics may we report, and how
honestly?* This is where the whole damage layer either keeps faith with `basics_spot_on` or quietly
re-commits the old model's exact sin. The decision: **ship what the emit object can honestly
produce, and treat what it can't as a structural absence — never a caveat-able shortfall.**

*Source key:* consumes [`05`](05_emit_object.md) (the emit object + the first-nonlinearity rule) and
its `cap-rarely-binds` condition; principles = `basics_spot_on` (this is the metric side of its
incident), `system_coherence_over_local_elegance`, `reference_is_input_not_authority`. `[OURS]`
derived; `[REF]` inherited.

---

## 1 · The question, framed by the nonlinearity rule

Doc [`05`](05_emit_object.md) established: a scalar mean survives only a **linear** path; the moment
a nonlinearity sits between the curve and the metric, `E[f(L)] ≠ f(E[L])` and the scalar is wrong.
The three nonlinearities are **N-cap** (saturation), **N-fin** (financial terms, parked), and
**N-quant** (the quantile operator — VaR/PML/TVaR *are* quantiles). So the metric you price decides
whether a scalar can honestly produce it.

This doc turns that into a *shipping policy*: for each metric, is it honestly producible from the v1
emit, and if not, what do we do about it?

---

## 2 · The metric partition — EAL-class vs tail-class `[OURS]`

```
   EAL-CLASS  (a MEAN of the loss — survives a scalar on a linear path)
        EAL / expected annual loss / average annual loss
        -> producible from a scalar  *iff*  the path is linear (cap rarely binds, no terms)

   TAIL-CLASS  (a QUANTILE or tail integral — needs the distribution's SHAPE)
        VaR (a quantile) · PML / OEP / AEP (tail quantiles) · TVaR (tail conditional expectation)
        · any "1-in-N year" number
        -> NOT producible from a scalar. a mean carries no quantiles. (N-quant, always on path.)
```

The partition is sharp because it's mechanical, not a matter of degree: a mean *is* the EAL-class
answer and *contains no* tail-class answer. So this isn't "scalar gives a rough tail" — it gives
**no** tail.

---

## 3 · The 2×2 — the real structure (not a 1-D choice) `[OURS]`

The existing framing offered three options (EAL-only / ship-all-caveated / block-everything). But
doc 05 §2 sharpened it: **EAL itself is only honest while the cap rarely binds.** So the honest
structure is a 2×2 over (metric class) × (cap behaviour):

```
                        cap RARELY binds              cap BINDS materially
                  ┌──────────────────────────┬──────────────────────────────┐
   EAL-class      │  SHIP (honest, checked    │  DON'T ship as-is — BIASED   │
                  │  by the known-answer test)│  (doc 05 §2). climb emit to   │
                  │                           │  rung 2 (spread) for EAL, or  │
                  │                           │  flag the cell. EAL is NOT    │
                  │                           │  automatically safe.          │
                  ├──────────────────────────┼──────────────────────────────┤
   tail-class     │  WITHHOLD                 │  WITHHOLD                     │
                  │  (N-quant: scalar has no  │  (doubly wrong: no quantiles  │
                  │  quantiles — STRUCTURAL   │  AND the cap nonlinearity).    │
                  │  absence, not a shortfall)│                               │
                  └──────────────────────────┴──────────────────────────────┘
```

The two insights the 2×2 forces that a 1-D choice hides: **(a)** tail metrics are withheld
*regardless* of the cap — they're structurally absent under a scalar; **(b)** even EAL is conditional
— a binding cap makes a cell's *EAL* biased, so a binding cap is the first thing that forces a cell
to climb the emit object, *for EAL itself*, before anyone even asks for the tail.

---

## 4 · The decision — withhold the tail, don't caveat it `[OURS]`

The load-bearing call, stated plainly and defended, because it's the one place the doc could go
wrong.

> **Decision.** Under a scalar emit, tail-class metrics are **withheld** — not shipped with a
> caveat. They are reported as *not yet available* (with the reason: the emit object doesn't carry
> the spread), never as a number-with-an-asterisk.

**Why withhold beats caveat — three reasons, in order of force:**

```
   1. CAVEAT IS THE OLD MODEL'S EXACT SIN.
      the old model's named failure was shipping a confident-but-understated VaR (~12x low).
      "ship the tail with an 'understated' flag" is RE-COMMITTING that, with a sticky note.
      basics_spot_on, verbatim: "a clamp that makes a bad number look reasonable is worse than
      the obviously-bad number, because it buys false confidence and ships."

   2. THE NUMBER TRAVELS; THE CAVEAT DOES NOT.
      a number in a cell/JSON gets priced against. a caveat in a doc/footnote gets dropped at the
      first hand-off downstream. you cannot bind a warning to a number across systems reliably.
      a withheld number creates no false anchor; a caveated number does.

   3. STRUCTURAL ABSENCE ≠ SHORTFALL.
      a scalar doesn't UNDERSTATE the tail — it has NO tail. shipping a "tail metric" from it means
      FABRICATING the quantile from an assumed shape we didn't source. that's not a caveat-worthy
      approximation; it's invention. withholding is the honest report of "not sourced yet."
```

**The honest counter-argument (documented, per P3, not buried):** a withheld tail can create a
*vacuum* — a risk team that needs a 1-in-100 number will substitute *their own* guess, possibly
worse than a loudly-caveated model number. This is a real concern from the consumer side. **Our
answer:** the vacuum is the *correct signal* — it says "this requires the spread, which isn't
sourced," which is true and actionable (it points at the work). A fabricated-but-caveated number
hides that signal under false precision. If a screening-grade tail placeholder is ever genuinely
needed, it must be a *separate, explicitly-labeled, never-externalized* artifact with its own
provenance — never the model's reported VaR. (This is the one place a reviewer might overrule us;
the call is recorded so it can be.)

---

## 5 · The known-answer check is the EAL boundary `[OURS]`

EAL is shippable *where it's checkable*, and the check defines the boundary:

```
   the known-answer check (hail A22):  capped-MC-mean  ≈  uncapped-analytic-EAL
        holds  ONLY WHILE:  the cap rarely binds  AND  no financial terms apply.

   => the check isn't just a test — it DRAWS THE LINE where EAL is honest.
      inside the line: EAL ships, with a passing known-answer check attached.
      outside it (cap binds / terms apply): EAL is an EXTRAPOLATION → climb or flag.
```

> **The labeling rule `[OURS]`.** Every shipped metric declares whether it carries a *passing
> known-answer check* or is an *extrapolation*. EAL-with-a-check and EAL-where-the-cap-might-bite are
> different epistemic objects and must not look identical in the output. (This is `basics_spot_on`'s
> "verify against known answers" applied to what we ship, not just what we compute.)

---

## 6 · House display rules `[REF + OURS]`

Two presentation disciplines that travel with every metric:

- **Report % of TIV alongside dollars** — always. A dollar loss without its fraction-of-value is hard
  to sanity-check across cells `[REF]`.
- **State the basis** (doc 03): % of *what* TIV — the **physical replaceable base**, not full capex.
  A %-of-TIV on full capex reads artificially low (doc 03 §2). The basis label travels *with* the
  percentage, or the percentage is ambiguous `[OURS]`.

---

## 7 · What ships at v1 — the summary table

```
   metric            v1 status (scalar emit, cap rarely binds, no financial terms)
   ─────────────────────────────────────────────────────────────────────────────
   EAL               SHIP — with passing known-answer check, % of TIV (physical basis), $ alongside
   EAL (cap binds)   DON'T ship as scalar — climb emit to rung 2, or flag cell as extrapolation
   VaR / PML / TVaR  WITHHOLD — structural absence under scalar; report "needs spread, not sourced"
   net-of-terms      OUT OF v1 SCOPE — N-fin parked (doc 06-financial / scope-edges)
   ─────────────────────────────────────────────────────────────────────────────
```

This is a *narrow, honest* v1 deliverable: EAL, checked and labeled, in dollars and physical-%-TIV —
and an explicit, non-fabricated "not yet" on the tail. It is exactly the deliverable that refuses to
re-pay the old model's price.

---

## 8 · What this commits us to

- Metrics split **EAL-class (mean) vs tail-class (quantile)**; the split is mechanical, not a degree.
- The decision is a **2×2**: EAL ships where the cap rarely binds (and is *checked*); a binding cap
  makes even EAL an extrapolation that forces an emit climb.
- **Tail-class metrics are withheld under a scalar — not caveated.** Withholding beats caveating
  (old-model sin; number-travels-caveat-doesn't; absence≠shortfall). The counter-argument (vacuum) is
  recorded and answerable.
- **Every shipped metric is labeled** check-backed vs extrapolation, and reported in **$ and
  physical-%-TIV** with the basis stated.

**Parked / downstream:** financial terms N-fin and net-of-terms metrics (scope-edges doc); the *climb*
mechanics (the spread form) when a binding cap or a tail request forces rung 2 ([`05`](05_emit_object.md)
§7 / [`04`](04_curation_derivation.md) §11 — the spread-sourcing seam).

---

## 9 · Open / revisit triggers

- **Does any built cell's cap bind materially?** (Carried from [`05`](05_emit_object.md) §7.) If
  hail/wildfire/wind saturation bites inside the spread, that cell's *EAL* is already biased and must
  climb — the highest-priority check, because it changes a number we'd otherwise ship today.
- **The withhold-vs-caveat call.** Decided as *withhold*; the consumer-vacuum counter-argument (§4) is
  the one a reviewer might reopen. If reopened, the resolution must still never let a fabricated tail
  become the *reported* VaR.
- **When financial terms arrive (N-fin).** They make the cap bind more often and break the
  known-answer check (doc 05 §2) — at which point the EAL boundary (§5) tightens and more cells need
  the climb. A scope-edge trigger to watch.

---

## 10 · Status

🟢 **Decided for v1.** Metrics partition into EAL-class and tail-class; the shipping policy is a 2×2
over metric-class × cap-behaviour; **EAL ships where checkable, the tail is withheld (not caveated)
under a scalar**, every metric labeled check-backed-vs-extrapolation and shown in $ and
physical-%-TIV. This keeps faith with `basics_spot_on` by refusing to ship the exact
confident-but-understated tail that broke the old model. The one reviewer-reopenable call is
withhold-vs-caveat (§4), recorded honestly. With this, the foundational damage-layer discussions
(01–06) are complete; what remains is parked extension work (portfolio, cascade, financial terms,
component depth) and the separate, run-the-guides build of the actual curve records
([`00`](../00_assembled_curve_record.md)).

*Links:* [`05 emit object`](05_emit_object.md) (the producer of the constraint) ·
[`04 curation`](04_curation_derivation.md) (the spread-sourcing seam) ·
[`03 valuation`](03_valuation_guide.md) (the %-TIV basis) · [`00 deliverable`](../00_assembled_curve_record.md)
(where metrics_shippable lands) · `basics_spot_on` (this is the metric side of its incident).
