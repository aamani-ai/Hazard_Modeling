# 01 · The emit object — what M3 puts on the wire  🔴 OPEN

**The headline decision.** Everything downstream — which metrics are honest, what the library must produce,
how much sourcing is needed — hangs on this. Deeper prior treatment:
[`../gpt/04_damage_representation_scalar_vector_distribution.md`](../gpt/04_damage_representation_scalar_vector_distribution.md).
The Methodology explicitly **refuses to decide** it ("would over-constrain the build before the per-peril
evidence is in") — so it's ours to close.

## The decision (Q1)

What object does the M3 damage stage emit per event?

| Rung | Crosses the seam | FOR | AGAINST |
|---|---|---|---|
| **Scalar mean DR** ← *all 3 cells today* | one number | simplest; **sufficient for EAL** (linearity); a published-MDR curve *is* this | drops secondary uncertainty → **understates VaR/PML/TVaR** |
| **Mean + uncertainty** | mean + a dispersion | better tail; cheap upgrade | must assume a form for the spread |
| **Damage-state vector** | P(state) | natural for **fragility-derived** curves; carries uncertainty natively | discrete; needs a state→cost map |
| **Discretized distribution** | full distribution over bins | strongest for VaR/PML/TVaR (OASIS-style) | most fidelity, most sourcing |

**The sharp version** ([`../gpt/04`](../gpt/04_damage_representation_scalar_vector_distribution.md)): *"Scalar
preserves the center. Distribution preserves the tail. And VaR/PML/TVaR live in the tail."* Same 60 mm hail
event: scalar → $30M every time; distribution → $8M / $28M / $54M / $110M sampled.

```
   the ladder (rising tail-fidelity AND sourcing cost):

   tail
   fidelity ^
            |                                      [4] discretized DISTRIBUTION
            |                                          (OASIS-style; best tail)
            |                          [3] damage-STATE vector
            |                              (fragility-native)
            |            [2] mean + UNCERTAINTY (a spread)
            | [1] scalar MEAN DR   <-- all 3 cells today (EAL-ok, tail-weak)
            +-------------------------------------------------> richness / cost
```

```
   what M3 emits at one fixed 60 mm hail event:

   SCALAR (mean only)              DISTRIBUTION (mean + spread)
      loss                            loss
       |                               |          .:|||:.
       |   | $30M                      |       .:|||||||||:.
       |   |                           |     .:|||||||||||||:.
       +---+------>                    +----+----+----+----+----> $
          one value                       $8M  $30M       $110M
   fine for EAL, blind to tail        carries what VaR/PML/TVaR need
```

## The two halves to separate

- **Interface vs content.** Decide first whether the *seam* can carry a distribution (the parquet schema, M4's
  consumer), separately from whether v1 *fills* it. A distribution-ready interface with scalar v1 content is
  cheap insurance against re-plumbing later.
- **Uniform vs per-peril (Q5-linked).** One emit object repo-wide, or let it follow the source — scalar where
  the curve is a published MDR, state vector where it's fragility-derived (Methodology §6's own logic)?

## The blocker to climbing the ladder (why it's deferred, not done)

Moving off scalar costs three things: (i) **choose the form** of secondary uncertainty per hazard (beta on
[0,1]? lognormal? elicited min/mode/max?); (ii) **re-parameterize** the ~27 non-mean-only library curves;
(iii) **find validation data** to calibrate the spread — scarcer than data for the mean. This is **Q5**, and
it belongs with this decision.

## Current stance & status

Scalar mean, v1, **explicitly temporary** (hail A22, wildfire DD-W8 revisit, wind DD-WN-11). The library can't
emit fragility/state today (Gen-2 plan). 🔴 **Open — the decision that unblocks the rest.**

## To decide

1. The target rung — and is it the *interface* target or the *content* target?
2. Uniform or per-peril.
3. If we climb: the uncertainty form + the re-parameterization plan (which curves first — the
   research-priority score?).

*Links:* [`00`](00_context_and_scope.md) · [`02 metrics`](02_metrics_and_tail_honesty.md) ·
[`../gpt/04`](../gpt/04_damage_representation_scalar_vector_distribution.md).
