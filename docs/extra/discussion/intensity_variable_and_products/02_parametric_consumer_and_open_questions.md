# 02 · The parametric trigger as a new consumer — and the open decisions  🟡 OPEN

*The catalog and the damage curve are consumers of the hazard we already model. The **parametric trigger** is
a third — and it is a different species: a **risk-transfer / product** surface, not a hazard or damage one.
This doc places it and lists what's still the owner's call.*

Builds on [`01`](01_one_chain_many_products.md). Provenance tags as there:
`[GROUNDED]` / `[ILLUSTRATIVE]` / `[OURS]`.

---

## 1 · Why the parametric trigger is genuinely *new*

The platform's three tiers (Performance · Hazard · Overall) and the `damage_modeling` substrate all answer
**"what happens physically, and what does it cost?"** A parametric trigger answers a different question:

> **"Did an event severe enough to create financial stress occur — and how much fast, objective liquidity
> should we release?"** `[ILLUSTRATIVE: Descartes solar-SCS reference]`

That is a **product / risk-transfer** question, not a hazard-frequency or damage-physics one. It is the reason
the trigger pins `X` at the **cheaply-sensed, legally-verifiable, contract-bindable** node ([`01`](01_one_chain_many_products.md) §2) — objectivity and speed, *not* damage fidelity, are its optimands. It
**buys** dispute-proofness and payout speed by **selling** basis risk.

This is why it does **not** belong in `damage_modeling`: that repo's scope explicitly excludes financial
terms, EAL/PML, and portfolio accumulation (*"the purpose of this library is not to own EAL, PML, or
portfolio metrics"*). `[GROUNDED: damage_modeling SCOPE_AND_STORY §4]` A trigger/payout structure is squarely
on the financial side of that line.

---

## 2 · Hedge, not replacement — and why that falls out of the frame

The Descartes worked example (the **only** grounded dollar case; all other parametric legs are
`[ILLUSTRATIVE]`):

```
   TIV                                  $150M
   traditional wind/hail deductible     5% × TIV   = $7.5M   (owner absorbs first)
   parametric limit                     $50M
   triggered payout (16% band)          16% × $50M = $8.0M   (fast, objective)
   ───────────────────────────────────────────────────────────────────────────
   effect: the $8.0M parametric cash roughly FUNDS the $7.5M deductible the owner must absorb
```
`[ILLUSTRATIVE: Descartes solar-SCS straight-line-wind reference]`

The product is **not** "replace the property policy." It is *"when a severe-enough event occurs, release fast
cash that can fund the deductible, the BI gap, PPA penalties, and repair liquidity."* That is a **hedge /
gap-fill / top-up** role. And [`01`](01_one_chain_many_products.md) §3 explains *why* structurally:

> **The parametric trigger is a hedge precisely because its node sits upstream of the damage node.** The
> node-gap *is* the basis risk; a non-zero gap is what distinguishes a hedge from indemnity. Drive the trigger
> node all the way to the damage node and you have indemnity (and lose the speed/objectivity that justified
> going parametric in the first place). `[OURS]`

A useful three-role taxonomy for any future parametric work `[OURS]`: **replacement** (narrow layer where
indemnity is slow/unavailable) · **hedge / gap-fill** (deductible, BI waiting period, PPA penalty, sublimit
gap) · **top-up / excess** (limit above the traditional policy). The solar-SCS reference is mostly
**hedge/gap-fill**.

---

## 3 · Where it would sit in the platform (a sketch, not a decision)

```
   PERFORMANCE          HAZARD (this repo)              OVERALL
   (model-gpr)          catalog → coupling → damage     performance + hazard
                        → loss → EAL/PML/VaR            → Total Loss
                              │
                              │  same catalog, NEW consumer
                              ▼
                        ┌─────────────────────────────┐
                        │  PARAMETRIC / RISK-TRANSFER  │   ← trigger design (which node, banded how)
                        │  trigger → payout %          │      is hazard-adjacent; payout/contract
                        │  (hedge / gap-fill / top-up) │      logic is financial-product
                        └─────────────────────────────┘
```

The **trigger-design** half (which node, what bands, basis-risk budget) is deeply hazard-adjacent — it reads
the same catalog the damage curve does. The **payout / contract** half is a financial-product concern. So a
parametric surface is a *consumer of the hazard catalog that lives partly in Hazard and partly in a product
layer.* This is a candidate sibling to the **CONUS-grid** product (use-case 2) — another non-loss consumer of
the same engine.

---

## 4 · Open decisions (the owner's call)

1. **Does the parametric trigger become a tracked scope item at all?** It is, today, a *lens* that sharpened
   the intensity-variable question — that value is already banked in [`01`](01_one_chain_many_products.md) and
   [`learning_logs/13`](../../../learning_logs/13_one_chain_many_products.md). Promoting it to a built product
   is a separate, larger decision.
2. **If yes — Drive-first.** Per house discipline, a new product concept is *discussed → reflected in the
   Drive taxonomy/methodology → then built*, not introduced bottom-up in the repo. A "parametric / risk-
   transfer" surface would need a home in the Drive reference set (likely alongside the risk-metrics and
   methodology docs) before any M-layer work.
3. **Grounding the parametric legs.** Every parametric example here and in [`01`](01_one_chain_many_products.md)
   is `[ILLUSTRATIVE]` (the Descartes reference is external; the PDF itself is a *product/commercial*
   reference, **not** a modeling-methodology source — it has no frequency, calibration, or backtesting). If
   this graduates, the trigger-design work needs its own grounded references, ingested the disciplined way.
4. **The basis-risk budget as a first-class output.** Since basis risk = the node-gap
   ([`01`](01_one_chain_many_products.md) §3), a parametric product would want the node-gap *quantified* — the
   same machinery (e.g. the wind 10 m→hub terrain bridge, `AWN-15`) that the damage pipeline needs anyway.
   Worth noting the overlap: closing in-pipeline node-gaps serves *both* damage fidelity and trigger basis-risk
   estimation.

---

## 5 · Status

🟡 **Open.** The frame (`01`) is settled and grounded; the parametric product is **flagged, not adopted.**
Recommendation: keep it as a lens for now, bank the learning, and revisit promotion-to-scope via the
Drive-first path only if/when a parametric product becomes a real direction. No M-layer work proposed.
