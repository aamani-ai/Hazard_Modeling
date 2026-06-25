# 05 — Plausibility QC: the V1 rule (decision)

*The decision distilled from the [`04` MESH-nature research](04_mesh_nature_and_qc_research.md) and the
canonical hail×solar damage curve. **Plausibility QC** = detecting and handling the cases where the
radar-derived evidence claims something physically implausible — an impossible **magnitude** (a 1,437 mm
"hailstone") or an impossible **rate** (a cell with ~45 severe days/yr). Both are the same kind of failure;
this doc sets how V1 handles them.*

> **Why "plausibility QC," not "data cleaning":** the impossible hail size and the impossible severe-day rate
> are both *plausibility failures* in the MESH-derived signal. Grouping them names the real problem and keeps
> the magnitude rule and the frequency rule in one place. It sits inside the broader *curation* (raw MESH →
> credible hazard layer); the meteorology field calls the detection half *quality control (QC)*.

---

## The problem (recap)

Raw MRMS MESH is a radar *estimate*, skillful at hail **occurrence** but unreliable for hail **size**
([`04`](04_mesh_nature_and_qc_research.md)). Two failure modes reach our hazard layer:

```
  MAGNITUDE artifact                         FREQUENCY artifact
  "impossible hail size"                     "impossible severe-day rate"
  ─────────────────────                      ──────────────────────────
  max MESH = 1,437 mm                        λ_cell up to ~45 days/yr
  585 CONUS cells ≥ 300 mm                   (e.g. a NY cell, 255 severe days)
  → corrupts SEVERITY                        → corrupts FREQUENCY
       │                                          │
       └──────────────── same family: a plausibility failure in the MESH signal
```

**The split that makes this tractable** (validated by `04`): MESH is occurrence-skillful and size-unreliable,
so **frequency is robust to the magnitude artifact** (a severe day is severe whether MESH says 30 mm or
1,400 mm) — only *severity* and *spurious rates* need treatment.

## The rule (V1)

Applied **identically in both deployments** (deep per-asset and the grid), because it's a property of the
MESH signal, not the asset.

| Layer | Rule | Why / grounding |
|---|---|---|
| **M0/M1** — hazard, asset-free | **Physical-plausibility cap + flag at ~200 mm.** Anything above the US record (Vivian, SD 2010, ≈ 203 mm) has no physical precedent → cap the severity *summary* at the ceiling, keep the raw value beside it, flag it. **≥ 300 mm = hard artifact.** The **severe-day count (frequency) is untouched.** Never delete. | `04`: ~200 mm physical ceiling (NCEI/NWS); runaway-magnitude mechanism (residual bright-band, beam geometry, reflectivity miscalibration inflating SHI). Asset-agnostic, so it lives in the hazard layer. |
| **M3** — solar damage | **The damage curve clamps at 100 mm.** The canonical hail×solar curve declares `valid_range: [0,100] mm` (`clamp_or_warn`) and is **≥ 99% saturated by 100 mm** (logistic, D50 = 41–64 mm by archetype). So solar loss is **insensitive to MESH above 100 mm.** The grid's `cap_100mm` policy *is* this. | the canonical curve artifact (`hail_solar__model_v1_0`). Asset-specific (the saturation point is the asset's), so it lives in M3. |
| **Frequency spikes** | **Flag** suspicious high-λ cells (e.g. λ ≳ a percentile threshold / repeat-signal cells); **hold them out of reportable loss**; spatial pooling/shrinkage deferred. | `04` gap: **no published temporal-frequency-artifact QC procedure** — this is our own defensible rule, owned explicitly. |

### Terminology — cap vs. clamp vs. flag

Mechanically, **cap** and **clamp** are the *same* operation (limit a value to a bound); they differ only in
*what they act on and why*. The **flag** is a different kind of thing — a label, not a value change.

| Term | Acts on | What it says |
|---|---|---|
| **physical cap** (~200 mm, M0/M1) | the stored *severity value* | "this isn't a physically real hail size" — data **validity** |
| **curve clamp** (100 mm, M3) | the *input fed to the damage curve* | "don't use the curve outside its validated range [0, 100 mm]" — model **domain** |
| **frequency flag** (M1 / reporting) | the *cell* (its λ) | "this rate is suspect — hold it out of reportable loss" — a label + hold-out, no number changed |

## The elegant consequence for hail × solar

```
  raw MESH (may be 1,437 mm)
        │  M0/M1: cap at ~200 mm  ── keeps the HAZARD LAYER honest (severity summaries,
        │                            and future assets that saturate above 100 mm)
        ▼
   severity into M3
        │  M3: curve clamps at 100 mm  ── for SOLAR, the loss is already insensitive
        ▼                                 to anything above 100 mm
   solar loss  ──►  the magnitude tail is moot; only the body (≤100 mm) drives loss
```

For hail × solar specifically, **the M3 100 mm clamp alone fully neutralizes the magnitude tail for loss.**
The M0/M1 ~200 mm cap is not redundant — it does a *different* job: keeping the asset-free hazard layer
physically honest, and protecting future assets whose damage saturates above 100 mm.

## What's V1 vs. deferred (per [`good_enough_for_v1`](../../../../principles/good_enough_for_v1.md))

| Honesty-load-bearing — **V1, now** | Accuracy-load-bearing — **deferred V1.5/V2** |
|---|---|
| physical cap + flag (magnitude) | MESH de-biasing (Murillo & Homeyer MESH75/MESH95) |
| frequency-spike flag + hold-out | frequency pooling / spatial shrinkage |
| rely on M3 saturation for solar | EVT severity tail; conditional-DR distribution |
| keep raw + severe-day intact | legacy `~34%` blend → canonical curve reconciliation |

This is the honest, runnable V1: nothing physically impossible enters a loss number, every weakness is
flagged, and the accuracy work is on the record as deferred.

## Owned / open

- The **frequency-spike rule is ours** — no literature standard. We flag-and-hold for V1; the principled
  upgrade is pooling (same family as Murillo & Homeyer smoothing / Das & Allen GP), deferred.
- The **legacy→canonical damage-curve reconciliation** (the `~34%` asset blend vs. the failure-unit curve
  with value-share aggregation) is a damage-modeling item, **not** part of this QC rule — deferred.

## Cross-references

- Evidence base: [`04_mesh_nature_and_qc_research.md`](04_mesh_nature_and_qc_research.md).
- The pause point this resolves: [`03_mrms_tail_qa_and_m1_policy.md`](03_mrms_tail_qa_and_m1_policy.md).
- Folds into the hazard anchor's limitations: [`../../../../hazards/hail/README.md`](../../../../hazards/hail/README.md) §5.
- Canonical curve: `damage_modeling/.../01_cells/hail_solar/current/hail_solar__model_v1_0__docs_r5__curve_artifact.json` (`valid_range [0,100] mm`, logistic, `max_DR = 1.0` at failure-unit grain).
