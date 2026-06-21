# 02 · Metrics & tail honesty — what ships at v1  🔴 OPEN

A direct consequence of [`01`](01_emit_object.md). Under a **scalar-mean** curve, which risk metrics are
honest?

## The decision (Q2)

Scalar-mean has no spread, so the severity Monte Carlo can't vary loss at a fixed intensity → **VaR/PML/TVaR
are structurally understated**, while **EAL is preserved** (linearity of expectation).

```
   exceedance prob.
     |
     |*  <- both curves agree at the body / mean  (EAL preserved either way)
     | *
     |  *.            TRUE  (carries spread):  *   (fat tail)
     |   * .          SCALAR (mean only):      .   (thin tail)
     |    *  .
     |     *   . .                 <- SCALAR understates here ...
     |      *  *  *  *  *  *       <- ... while TRUE keeps probability in the tail
     +-------------------------------------> loss
       body        VaR99    PML        ( <-- the decisions live out here )
```

| Option | What we publish at v1 | Trade |
|---|---|---|
| **(a) EAL-only** | ship EAL; *withhold* VaR/PML/TVaR until the spread is carried | defensible & honest; narrower deliverable |
| **(b) Ship all, caveated** | ship tail metrics with a loud "tail-understated" flag | fuller deliverable; risk the caveat is ignored downstream |
| **(c) Block on `01`** | no tail metrics until the emit object climbs off scalar | cleanest correctness; slowest |

## Why this matters here specifically

The rebuild exists because the **old model broke the tail** ([`basics_spot_on.md`](../../../principles/basics_spot_on.md)) —
shipping a confident-but-understated VaR is the exact failure mode to avoid. "More simulation is not more
truth." This decision is the discipline that keeps us from re-paying that price. Always report metrics in **%
of TIV alongside dollars** (house display).

## Validation coupling

Known-answer checks (e.g. hail A22's capped-MC-mean vs uncapped-analytic EAL) are **valid only while the cap
rarely binds and no financial terms apply** — see [`06`](06_financial_terms_and_scope_edges.md). State which
metrics carry a known-answer check and which are extrapolations.

## To decide

1. (a) / (b) / (c)?
2. Exactly which metrics are "EAL-class" (honest under scalar) vs "tail-class" (need the spread)?
3. The caveat language + where it travels (the per-cell summary JSON, the report).

*Links:* [`01 emit object`](01_emit_object.md) · [risk-metrics reference](../../../google_drive_docs/README.md) ·
[`basics_spot_on`](../../../principles/basics_spot_on.md).
