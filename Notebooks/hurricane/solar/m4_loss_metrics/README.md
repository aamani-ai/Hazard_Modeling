# M4 — loss & metrics (hurricane × solar)

*Storm-resolved compound-Poisson MC → EAL / VaR / PML / TVaR (% of TIV + $). Plan:
[`docs/plans/hurricane/m4_loss_metrics.md`](../../../../docs/plans/hurricane/m4_loss_metrics.md).*

| Notebook | What it builds | Status |
|---|---|---|
| [`01_loss_metrics`](01_loss_metrics.ipynb) | shared event-based MC → risk metrics + EP curve | ✅ **built** |

## Headline — Everglades Solar (hurricane WIND only, % of TIV)

A **point estimate** on the chosen provisional curve (`tracker_stow`), consistent with the other cells — *not* a
stow↔stow-fail range (both curves are placeholders to be replaced; a range between throwaways would overstate precision).

| Metric | value (% of TIV) |
|---|---|
| **EAL** | **2.23%** (~1.85–2.60% incl. ±17% storm-rate uncertainty) |
| PML100 | 31.4% |
| PML250 | 37.4% |
| PML500 | 41.5% (annual AEP, bounded 100% TIV; deeper not resolvable) |
| TVaR99 | 37.3% |

*Recorded sensitivity (not headline):* a harsher provisional curve gives EAL 4.08% / PML500 66.2%. **Hayhurst = 0**
(true-zero control, λ=0). Dollar figures emitted too, but secondary (ride on the $/MW TIV estimate).

## Honest reading (what to trust)

- **Event-based MC, no RP bridge** (hurricane has real storm objects → feeds the shared engine directly, like hail).
- **The hazard side is independently validated** (ASCE: RP gusts within 5.5%; 90 kt == observed). **The loss side is
  the soft part** — driven by the **provisional curves** (esp. mounting onset x0 120 → EAL is high & curve-driven).
  The real number awaits the replacement fragility curve **+ a loss-side benchmark (Hazus/NRI)** — the loss analog of
  the ASCE hazard check.
- **PML is annual-aggregate (AEP)** bounded at 100% TIV — the stow-fail deep tail exceeds the ~48% single-storm cap
  because rare years see *two* hurricanes; occurrence-PML would cap lower. Reported to **500-yr** (~1,000-yr catalog limit).
- Outputs: `tc_m4_loss_metrics.parquet`, `tc_m4_ep_curve.png`, manifest.

**Dividends banked:** field-intensity coupling built; `event_family_id` stamped → coastal flood + pluvial-TC attach
later via the shared RAFT catalog. **Next:** swap the provisional curve + add a loss benchmark; then wind-farm V2.
