# 04 · Portfolio extension — single-site → many assets  🔴 OPEN (out of the v1 box)

Everything else in this folder is single-asset. Extending to a portfolio is its own cluster, **unmodelled in
the built cells**. Surfaced as a block, not scattered.

```
   INDEPENDENT sum  (cheap, understates tail)   CORRELATED occurrence  (correct PML)

     event1 --> [A]                                         ,--> [A]
     event2 --> [B]   losses rarely land         one swath -+--> [B]   all hit the
     event3 --> [C]   in the SAME year                      '--> [C]   SAME year
                                                  => the portfolio tail gets FAT
```

## The decision (Q3)

| Option | What it does | Trade |
|---|---|---|
| **(a) Stay single-site** | label loudly, defer portfolio | honest; no book-level number |
| **(b) Independent-asset sum** | sum per-asset losses assuming independence | cheap; **understates the correlated tail** |
| **(c) Correlated occurrence** | one event (swath / fire / system) hits many assets together | correct portfolio PML; most work |

## The three sub-issues

- **Correlated occurrence** — a single hail swath / fire complex / convective system hits many nearby assets
  at once; independence understates portfolio PML (the dependence is exactly what fattens the tail). Named:
  wildfire DD-W6, wind AWN-22 / DD-WN-12.
- **Weight-aggregation grain** — do per-asset capex weights sum to a portfolio, or do we TIV-weight across
  assets? The single-asset cap `Σ wᵢ·Lᵢ` doesn't obviously compose.
- **Within-asset spatial homogeneity** — even one utility-scale plant doesn't feel uniform intensity across
  its footprint (library flag). A portfolio inherits this at two scales (within-asset and across-asset).

## Status

🔴 **Open, none built.** The highest-severity *gap* (vs decision) — fine to defer for v1, but it must be a
named workstream, not an afterthought.

*Links:* [`00 §1 scope`](00_context_and_scope.md) · [wildfire decisions](../../../plans/wildfire/decisions.md) ·
[convective-wind decisions](../../../plans/convective_wind/decisions.md).
