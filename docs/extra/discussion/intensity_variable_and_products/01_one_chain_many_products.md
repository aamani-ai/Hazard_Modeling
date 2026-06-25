# 01 · One chain, many products — the hazard intensity variable is product-dependent  🟡 OPEN

*The hazard intensity variable `X` is not chosen once per hazard. It is chosen once per **consumer** — and
every consumer reads off the **same causal chain**, pinning `X` at the node its own binding constraint forces.*

**Provenance tags used throughout:** `[GROUNDED: file:line]` = verified against a repo/dossier source ·
`[ILLUSTRATIVE]` = general/market practice, no repo source · `[OURS]` = our interpretive frame on top of the
grounded facts. The damage-side x-axis method is **canonical in `damage_modeling`** (foundations `02`,
standard `04`); this doc is the *cross-consumer* synthesis the damage repo's scope deliberately stops short of.

---

## 1 · The question

Across the versions, one peril seemed to wear three different intensity variables — one in the **event
catalog** (M0/M1), one in the **damage curve** (M3 / a `damage_modeling` cell), one in a **parametric
insurance product** (the Descartes solar-SCS reference). So: is `X` picked **once per hazard** (agnostic), or
**once per product** (product-dependent)?

> **The answer `[OURS]`: product-dependent, but principled.** All three consumers read off **one shared
> causal chain**. Each pins `X` at the node where *its own* binding constraint lives. They differ because the
> constraints differ — and they reconcile through **bridges** between nodes.

"Product," not "use case" — and the three products are *layers*, not customers: the catalog, the damage
curve, the parametric trigger. (A fourth, classic **indemnity**, anchors the far end — it pays on realized
loss, no proxy at all.)

---

## 2 · The shared causal chain, and who pins where

Every hazard has a chain from event to dollars. The chain-position vocabulary is grounded in
`damage_modeling` standard `04` §3 (*Hazard source → Local hazard intensity → Contact intensity → Damage
state*) and the per-hazard chains in foundations `02` §5b; the "each consumer pins a node" overlay is `[OURS]`.

```
   THE CHAIN (convective wind shown; every hazard has one)
   ─────────────────────────────────────────────────────────────────────────────────────
   hazard source   →   local intensity   →   contact intensity   →   load   →  DAMAGE  →  $ loss
   (EF / category)     (gust @ 10m, mph)     (gust @ the member)    (½ρV²)     (DR)       (loss)
        ▲                    ▲                                         ▲          ▲          ▲
        │                    │                                         │          │          │
   ┌────┴────┐        ┌──────┴───────┐                          ┌──────┴────┐  (curve    ┌───┴────────┐
   │ CATALOG │        │  PARAMETRIC  │                          │  DAMAGE   │   absorbs   │ INDEMNITY  │
   │  (M1)   │        │   TRIGGER    │                          │ CURVE(M3) │   load→DR)  │ (classic   │
   └─────────┘        └──────────────┘                          └───────────┘             │ insurance) │
   node = what        node = cheaply                            node = most-              └────────────┘
   the SOURCE         SENSED + legally                          downstream node           node = the
   DATA emits         VERIFIABLE +                              the DATA can               realized loss
                      contract-bindable                         DELIVER                    itself
```

| Consumer | Reads off `X` | Picks its node by… | Optimizes for |
|---|---|---|---|
| **Catalog (M0/M1)** | event magnitude | what the **source data natively emits** | faithful event representation |
| **Damage curve (M3)** | damage ratio | **physics ∩ data** — the chain-position rule (most-downstream node the data delivers); physics bridge behind it | mechanistic honesty (what breaks the part) |
| **Parametric trigger** | payout % | **sensability + legal verifiability + contract-bindability** (accepts basis risk) | objective, fast, dispute-proof payout |
| **Indemnity** | dollars | none — it *measures* the loss | exactness (accepts slowness) |

The damage curve's rule is the load-bearing one and it is already canonical: *"put the x-axis at the
most-downstream node on the causal chain your hazard layer can actually deliver as data"* — and a damage
curve carries an **operational axis** (what the data speaks) with a **physics bridge** behind it (what the
mechanism responds to). `[GROUNDED: damage_modeling foundations 02 §5b; standard 04 §2]`

---

## 3 · Two coordinates: which quantity (Q-x2a) vs which node (Q-x2b)

The single most useful distinction — it dissolves most of the confusion. Foundations `02` splits the x-axis
choice into **Q-x2a (which quantity)** and **Q-x2b (where on the chain)**. The realization that unlocked this:

> **Same *quantity* ≠ same *node*. `[OURS]`** Two consumers can read the *identical physical quantity* (e.g.
> a 3-s gust) and still sit at *different nodes* (anemometer height vs hub height vs the member). The quantity
> can collapse while the node does not.

And the consequence that ties it to insurance:

> **Basis risk = the node-gap. `[OURS]`** The distance along the chain between a product's node and the
> *damage* node **is** its basis risk. Indemnity sits *at* the damage node → zero proxy gap → no basis risk,
> but slow. A parametric trigger sits *upstream* → the gap is the basis risk → which is exactly **why a
> parametric product is a hedge, not a replacement.** If its node *were* the damage node, it would be
> indemnity.

Matching the *quantity* is necessary but **not sufficient** to kill basis risk — the gap is a *node* (spatial
/ reference-frame) gap, not a quantity gap.

---

## 4 · The contrast panel — six perils, two coordinates

The cleanest way to see "product-dependent but principled" is to ask, per peril: does the **quantity**
collapse across consumers (Q-x2a)? does the **node** (Q-x2b)? Verified across the four built perils + two
forward ones.

| Peril | Q-x2a quantity collapses? | Q-x2b node collapses? | Shape it teaches |
|---|:--:|:--:|---|
| **Hail × solar** | **yes** — MESH mm everywhere | **yes** — all at the gridded-MESH node | **degenerate** (both collapse); residual grid→panel gap is where basis risk hides |
| **Convective wind × wind farm** | **yes** — 3-s gust everywhere | **no** — anemometer / hub-`r` / member | **HERO** — quantity collapses, node diverges |
| **Wildfire × solar** | catalog↔damage **yes** (kW/m); parametric **no** | catalog↔damage **yes** (zero gap); parametric **no** | **chain-position** — axis = what data delivers |
| **Flood × solar** | **no** — depth vs velocity vs gauge | **no** | **split (E2)** — different quantities by mechanism |
| **Winter ice/snow** *(fwd)* | **no** — composite load vs sensed depth | **no** | **composite (E1)** — inputs fuse to one scalar |
| **Hurricane** *(fwd)* | **no** — category / sustained / gust | **no** | **split + averaging-time bridge** |

Read across: there is exactly **one** clean "quantity-collapses-but-node-diverges" case (wind, the hero);
hail is the **degenerate** both-collapse case; everything else is a genuine **split** or **composite**. So
"can one variable serve all products?" → only when the constraints happen to land on the same node. They
nearly do for wind (everyone gravitates to gust); they don't for the rest.

---

## 5 · The worked examples

### 5.1 · Convective wind — the hero (quantity collapses, node diverges)

All three consumers speak **3-second gust** — the cross-standard observable ASCE 7, the EF scale, NWS, and
IEC 61400-1 all reconcile to. `[GROUNDED: m1_catalog/01_catalog.py:321 `magnitude_metric='3s_gust_ms'`;
dossier `r = V_3s_hub/Ve50_class` :99,106-107]` But the **node** differs:

```
   QUANTITY (Q-x2a): 3-s gust   ── collapses across all three ✅
   NODE     (Q-x2b):
     catalog      →  ASCE surface @ 10 m, Exposure C  (the data ASCE/SPC can speak)
     damage curve →  HUB height, design-normalized r = V_3s_hub / Ve50_class
     parametric   →  site ANEMOMETER @ sensor height (cheap, verifiable, bindable)   [ILLUSTRATIVE: Descartes]
   ── node does NOT collapse ❌  → basis risk lives in the node-gaps
```

The bridges that connect the nodes (all on the *same* gust quantity):
- **EF → gust** (tornado catalog): EF rating → bin-midpoint gust `{EF0:75 … EF5:226 mph}`, then a bounded GPD
  (`μ=EF0`, `L=113 m/s` EF5 truncation, `ξ<0`). `[GROUNDED: convective_wind m1_catalog]`
- **Vref (10-min mean) → Ve50 (3-s gust)**: gust factor ≈ 1.4 — the **averaging-time** bridge that lets IEC
  survival speeds line up with the 3-s-gust language. `[GROUNDED: dossier]`
- **10 m Exposure-C gust → hub-height gust**: the terrain/height adjustment — **this is the central
  catalog→damage node-gap, and it is declared but NOT built.** `[GROUNDED: layer0 + AWN-15 assign it to M2;
  the built M2 passes the gust through unconverted]` → **basis risk *inside the pipeline*, not only in the
  insurance product.** That's the sharpest finding here: a node-gap you can leave unmodeled by accident.

And the reason the two sub-perils (tornado + strong wind) share one curve: *"the gust has no memory of where
it came from"* — once a gust reaches M3 it is just a number; the source-specific work happened upstream.
`[GROUNDED: commit f6788d7]` The two sub-peril curves differ by loading **mechanism**, not by **axis**.

### 5.2 · Hail — the degenerate case (both collapse) + the physics bridge

All three speak **MESH-equivalent diameter (mm)**: catalog peak MESH `[GROUNDED:
Notebooks/hail/m1_catalog/01_event_catalog.py:144,179-180]`, the damage curve (`intensity_metric =
'hail_diameter_mm'`), and the Descartes hail-size bands `[ILLUSTRATIVE]`. Node collapses too — all at the
gridded-MESH node, fed straight into M3 with no coupling transform.

Two things this example teaches:
- **The physics bridge behind the operational axis (E1 composite).** Physics hands a combiner —
  `KE = ½·m(D)·v(D)²` with DOE/FEMP power-laws `m(D)=0.000529·D^2.974 g`, `v(D)=4.812·D^0.487 m/s`. But the
  axis is **diameter**, not KE: *"catalogs provide hail size, not kinetic energy."* KE is retained as a
  derived bridge, **never the input axis**. `[GROUNDED: dossier:135-141,462-495]` *(Note a source-internal
  looseness: foundations `02` §7 writes hail's axis as "kinetic energy / MESH," which reads as KE-on-axis; the
  dossier is the precise one — diameter axis, KE bridge.)* **The built M3 notebook does not even compute the
  KE bridge.** `[GROUNDED: no kinetic/energy term in the .py]`
- **The residual node-gap where basis risk hides.** Even with quantity *and* node collapsed, a real gap
  remains: **gridded-MESH (estimated aloft) → the impact an individual panel actually receives.** The
  parametric product **monetizes** this gap (accepts it for cheap, verifiable sensing); the damage curve
  **absorbs** it into the curve + conditioners (stow, archetype). Same gap, different owner.

> **A caution this peril forces into the open `[GROUNDED]`:** hail has **two non-agreeing damage curves**.
> (a) The **built & consumed** M3 capex-weighted *subsystem blend* (asset DR cap ≈ 0.344,
> `data/hail/damage_curves/hail_solar_asset_capex_weighted.json`). (b) The more-developed `damage_modeling`
> dossier v1.3 *failure-unit* `P_break` logistic (archetypes D50 ≈ 41/53/64 mm), **not yet wired into the
> notebook.** Both pin `X` on MESH mm (so the Q-x2a/Q-x2b claims hold), but "the hail damage axis" has **two
> instantiations that disagree on grain and numbers** — do not quote one as settled.

### 5.3 · Wildfire — the chain-position rule, vivid

FSim emits **fireline intensity (Byram, kW/m)** — via `FL_m = 0.0775·I^0.46` from its FLP flame-length
classes — and the damage curve reads kW/m **directly**. `[GROUNDED:
Notebooks/wildfire/m1_catalog/01_catalog.py:64,98-102; solar/m3_damage/01_damage.py]` So catalog and damage
sit at the **same node — zero node-gap, zero basis risk between them.** This is the chain-position rule at its
most legible: *component temperature would be more honest, but it is downstream of a coupling model we
haven't built, so the axis sits where the data speaks — fireline intensity — and the
intensity→heat-flux→temperature physics lives inside the curve.* `[GROUNDED: foundations 02 §5b, verbatim]`

It also carries the **one deferred 2-D axis** in the whole platform: **residence time** (burn-through — a slow
front delivers more heat than a fast flash at equal intensity). It is the *single* genuine irreducible 2-D
case, deliberately excluded from v1 and documented as a wall. `[GROUNDED: foundations 02 §5a]` *(It is a
singleton by design — not "one of several" deferrals.)* The parametric leg (burned-area / proximity / fire-
weather-index) sits far upstream of every damage node. `[ILLUSTRATIVE]`

### 5.4 · Flood — the split (E2)

One hazard, **two univariate axes by mechanism**: **depth** above each component's datum shorts the
electricals; **velocity / scour** attacks the foundation — two curves, **summed**, not one 2-D surface.
`[GROUNDED: flood_solar dossier:156-184; foundations 02 §3 ESCAPE 2, §4]` The apparent asset-level
multivariate-ness *dissolves at the failure-unit grain*. Quantity does **not** collapse (depth vs velocity vs
a gauge reading), node does not either.

One precision the review forced: the depth bridge `h_i = max(0, WSE − z_i_crit)` is a **horizontal datum
re-reference** — the *same* quantity (a depth in metres), moved from the site frame to the component frame.
The dossier calls it *"Exposure geometry / horizontal shift."* It is a **Q-x2b reference-frame shift, not a
Q-x2a quantity change** — don't overstate it as "one node downstream." `[GROUNDED: dossier:283]`

### 5.5 · Winter ice/snow *(forward)* — the composite (E1)

The cleanest non-hail **composite-collapse**: ice thickness + snow depth + density fuse via a physics combiner
(`Σ depth_i·density_i·g`) into **one areal-load scalar (kPa)**, keeping the curve univariate. `[ILLUSTRATIVE:
foundations 02 §7:271]` Its parametric foil is instructive: a **snow-depth** trigger is **density-blind** —
same depth, very different kPa for wet snow vs powder vs glaze ice — so the dominant basis risk is *inside the
composite*, upstream of any node-gap.

### 5.6 · Hurricane *(forward)* — split + the averaging-time bridge

Hurricane is the canonical **E2 split** (wind→structure on gust, summed with surge/rain→flood pathway), and it
is where the **"unqualified gust = 3-s" convention breaks**: NHC reports **1-minute sustained** wind, so a
**gust-factor (~1.4) averaging-time bridge** is needed to reach the 3-s-gust damage axis. `[GROUNDED-by-
composition: dossier flags the hurricane blade curve as 1-min sustained, x0=118, and the set as a different
x-axis convention]` Catalog candidates chain *upward* too — Saffir-Simpson **category** is a coarse
hazard-source node above 1-min sustained. The wind, tornado, and hurricane perils **converge on one 3-s-gust
turbine curve** (the curve collapses) while staying **distinct perils** with different footprints and
frequencies (the catalog does not collapse). `[GROUNDED: shared-curve note]` *(Averaging-time bridges are
**wind-family-only** — there is no clean non-wind second instance; pair with `AWN-27`: "do not mix gust and
sustained.")*

---

## 6 · What this commits us to (and what stays open)

- **`X` is product-dependent, principled.** One chain; each consumer pins its node by its own constraint;
  bridges reconcile; the **node-gaps are the basis risk.** `[OURS]`
- **`X` is an *index*, not a forecast target** — we read damage/payout/magnitude *off* it; that's *why* the
  product (not the physics) selects the node.
- **Same quantity ≠ same node**, and **matching the quantity does not remove basis risk** — the gap is a node
  gap. `[OURS]`
- **A node-gap can be left unmodeled by accident** (the wind 10 m→hub terrain bridge, declared not built) —
  basis risk is not only an insurance-product phenomenon; it can hide *inside the pipeline*. `[GROUNDED]`
- **Honesty rails for the authored learning:** all parametric legs are `[ILLUSTRATIVE]`; hail has two
  non-agreeing damage curves; the deferred-2D case is a singleton; node-vocabulary is `[OURS]` over
  standard-04's chain.

**Open → [`02`](02_parametric_consumer_and_open_questions.md):** the parametric trigger is a *new kind of
consumer* (risk-transfer, not hazard or damage). Does it become a tracked scope item, and where does it live?
