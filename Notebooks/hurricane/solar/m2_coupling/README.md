# M2 — Coupling (M1 → M2) *(field-intensity — thin, because M1 built the field)*

*Does the storm's wind reach **our** asset — and with what intensity across it? The layer that turns the catalog's
per-site gust into the **asset's own** exposure handoff. For a field-intensity peril this is **thin** — M1 already
synthesized the field (Holland → gust at the site) — so M2 mostly **declares the coupling, demonstrates why it's
degenerate on solar, and emits the contract**.*

**Where this sits:** [M0 evidence](../../m0_input_data/) → [M1 catalog](../../m1_catalog/) → **M2 (coupling)** →
[M3 damage](../m3_damage/) → M4 loss & metrics. Plan:
[`docs/plans/hurricane/m2_coupling.md`](../../../../docs/plans/hurricane/m2_coupling.md) · Decision:
[JD-TC-2](../../../../docs/plans/hurricane/decisions.md).

## The plain-English question

The M1 catalog has each storm's **3-second gust at the site**. M2 asks: across the *whole solar farm*, is that one
gust, or does it vary? Hurricane is **field-intensity** — *sample a continuous field at the asset* (the third
coupling type, vs hail's areal hit-or-miss and wildfire's site-conditioned). On a ~1.4 km solar polygon at storm
scale the field is essentially **uniform**, so the coupling collapses to **one value for the plant**.

## What we did

We **demonstrated** the uniformity rather than assuming it: for every storm we sampled the Holland gust at the
footprint **centroid vs its four edges** (±679 m) and measured the spread. It's **median 0.5%, p95 1.1%** across the
plant → the whole farm sees one effective gust → **`value_exposed_fraction = 1.0`**. M2 then passes the gust
through unchanged (it adds *exposure*, not magnitude) into the contract M3 reads.

## Why this way — and the honest tail

**1. Field-intensity, degenerate on solar — earned, not asserted.** The <2% spread is the *evidence* behind the
"degenerate" label ([JD-TC-2](../../../../docs/plans/hurricane/decisions.md)). Because the field is uniform, the
whole TIV is exposed to the one gust → `fraction = 1.0`. **No Minkowski (that's hail's areal coupling), no
susceptibility modifier (that's wildfire's site-conditioning)** — those belong to the other two coupling types.

**2. The rare near-eye tail (~8% max).** A small-eye storm passing *almost over* the plant drags its steep eyewall
gradient across the 1.4 km footprint → up to ~8% spread. Small enough for solar (we use the centroid ≈ the average),
but it **shows why the wind-farm cell (built) uses per-point field-intensity** (turbines span tens of km).

## Inputs → outputs

[M1 catalog](../../m1_catalog/) (per-event site `gust_3s_mph`) → `data/hurricane/tc_m2_coupling.parquet`
(each event + `gust_3s_mph` + `value_exposed_fraction = 1.0`, ready for M3) + `tc_m2_manifest.json` (coupling type,
fraction rule, the uniformity-check result).

## Deferred (stated, not hidden)

- **Per-point field-intensity** — sampling the field at each asset node, where it genuinely varies. Moot on a small
  solar polygon (uniform); **realized in the built wind-farm cell** (the full field-intensity proof).
- **Near-eye non-uniformity** — the ~8% tail is folded into the centroid value; a future per-point version would
  resolve it (only matters for the rare direct small-eye hit).

## Notebooks

| Notebook | What | Output |
|---|---|---|
| [`01_coupling`](01_coupling.ipynb) | footprint uniformity demonstration → `value_exposed_fraction = 1.0`; gust pass-through + known-answer checks | the coupled parquet + manifest |

## Key

Plan: [`m2_coupling.md`](../../../../docs/plans/hurricane/m2_coupling.md). Realizes the **field-intensity** coupling
type (A21 dispatch) — the repo's first primary build of it, in its honest spatially-degenerate-on-solar form.

## Assumptions (this layer)

[ATC-12](../../../../docs/plans/hurricane/assumptions.md) field-intensity, **spatially degenerate on solar**
(≈ centroid sample at storm scale — demonstrated <2% spread) · [ATC-13](../../../../docs/plans/hurricane/assumptions.md)
solar = dense areal polygon → `value_exposed_fraction = 1.0` (uniform exposure; no areal-miss, no susceptibility).

**Next → M3 (damage):** map each event's 3-s gust through the `infrasure-damage-curves` hurricane × solar curve →
conditional damage ratio + loss.
