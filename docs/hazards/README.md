# docs/hazards/ — the hazard anchors

**The front door to each hazard.** One shareable, high-level snapshot per hazard that you read *first*
(and return to when you're deep in the weeds) to keep the whole picture in mind: what the hazard is, how
we model it, what's reliable, what isn't, and what's V1 vs. deferred.

Before opening any hazard's M0 notebooks, read the cross-hazard prerequisite guide:
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). It defines the "before M0" mental model:
understand the physics, understand the data-source reality, then translate both into the M0-M4 pipeline.

For the shared mechanics of how M1 becomes annual financial metrics, read
[`m0_m4_event_loss_contract.md`](m0_m4_event_loss_contract.md). It documents the universal event/loss contract:
raw event catalogs, pre-integrated products, return-period profiles, and stochastic catalogs can all feed the same
M4 engine if they produce a count process, a conditional severity process, coupling, and an M3 damage function. It
also defines the M0/M1 input-mode taxonomy: event-first, return-period/surface-first, and hybrid.

Each hazard README should explain the M0-M4 flow directly. For the deeper choice/rationale ledger, read the
hazard's `modeling_choices.md` file. The convention is documented in
[`modeling_choices.md`](modeling_choices.md): these files carry the event-model choices, distribution choices,
M2 coupling choices, M3 damage assumptions, M4 sampling choices, and confidence/revisit triggers.

Between the Drive references and the notebooks, read the source-selection layer:
[`source_selection.md`](source_selection.md) plus the hazard-specific `source_selection.md` file. That is where
we record which candidate dataset becomes the V1 spine, which sources are validation-only, and which are
rejected or deferred.

## Physics Reader Guides

Each hazard folder has a `fundamentals_before_m0.md` file. These are the "explain the physics before the
notebook" guides; they should be read before source selection or M0 output interpretation.

| Hazard | Reader guide focus | Key confusion it prevents |
|---|---|---|
| [Hail](hail/fundamentals_before_m0.md) | Hailstone impact, MESH as radar-estimated hail size, areal hit/miss coupling. | Treating NOAA point reports as the catalog or reading MESH as perfect ground truth. |
| [Wildfire](wildfire/fundamentals_before_m0.md) | Fire reaching the asset, burn probability, conditional flame length, FSim vs WRC. | Confusing pre-integrated burn probability with a raw event catalog. |
| [Convective wind](convective_wind/fundamentals_before_m0.md) | 3-second peak gust, tornado vs strong-wind split, two thresholds, two coupling paths. | Collapsing severe-wind event threshold into turbine damage onset. |
| [Flood](flood/fundamentals_before_m0.md) | Inundation depth, riverine / pluvial / coastal physics, site-conditioned depth vs equipment elevation. | Treating flood as one data shape or adding overlapping inland water sources blindly. |
| [Hurricane](hurricane/fundamentals_before_m0.md) | Tropical-cyclone wind field, RAFT tracks, Holland wind, event identity for flood joins. | Modeling hurricane as a return-period gust only and losing wind-surge storm identity. |

## The goal: one loss object, many metrics

The goal of hazard modeling is not to produce a separate "hail number," "flood number," or one-off metric per
hazard. The goal is:

```text
For each hazard x asset pair,
build a coherent annual loss distribution
so EAL, VaR, PML, TVaR, and OEP/AEP metrics are readings off one consistent object.
```

Every hazard can reach that object by a different path, but every path has to supply the same three model
ingredients:

```text
1. event frequency / count process
   how many damaging or potentially damaging events occur per year?

2. event intensity / coupling process
   how big are those events, and what intensity reaches the asset?

3. conditional damage / loss process
   given the asset experiences that intensity, how much value is damaged?
```

M4 turns those ingredients into two annual loss vectors:

```text
A_y = sum of all event losses in year y       -> aggregate annual loss / AEP frame
O_y = max single-event loss in year y         -> occurrence annual loss / OEP frame

EAL      = mean(A_y)
VaR/PML  = quantile(A_y) or quantile(O_y), depending on the stated frame
TVaR     = tail mean beyond the chosen quantile
```

That is why the docs separate **source selection**, **hazard physics**, **coupling**, **damage**, and **loss
aggregation**. Different hazards take different routes to the three ingredients, but the final object is
standardized.

### The M1 Event Model Contract

The most important nuance: **M1 does not always mean a raw historical event catalog**. M1 means the hazard has
been translated into an event model that M2-M4 can consume.

For some hazards, that event model is literal event objects:

```text
hail:     MRMS fields -> hail-day footprints and severity summaries
tornado:  SPC tracks -> path events, EF mix, path geometry, regional frequency
```

For other hazards, it is a statistical profile derived from a source that has already integrated the event set:

```text
wildfire:      FSim burn probability + flame-length histogram
strong wind:   ASCE return period -> 3-s gust curve
flood:         return-period depth profile or modeled depth curve
```

That is still valid if the M1 object answers the same two questions:

```text
how many events occur per year?
given an event, how severe is it?
```

This distinction matters most for return-period surfaces. A **100-year ASCE gust** or **100-year flood depth** is
a hazard intensity statement, not a 100-year loss. M1 converts that source into a count/severity model; M2 couples
it to the asset; M3 translates intensity into damage; only then does M4 produce loss return periods like PML100.

M3 is conceptually separate from M4, even when a prototype notebook implements them close together:

```text
M3 = local intensity -> damage ratio / event loss rule
M4 = repeatedly apply that rule to sampled events and aggregate annual losses
```

So M4 can compute AEP and OEP even when there is no raw historical event table, because it generates synthetic
per-event losses from the M1 event model and the M3 damage function. What is deferred without raw event identity
is portfolio/event-family work: same storm across multiple assets, outbreak correlation, named-event validation,
and cross-hazard joins. The full version of this doctrine is in
[`m0_m4_event_loss_contract.md`](m0_m4_event_loss_contract.md).

This layer sits **above** the working detail and **points down into it** — it does not duplicate it:

```
                  ┌────────────────────────────────────────┐
                  │  docs/hazards/<hazard>/   ← THE ANCHOR   │   read first
                  │  what · source · how · reliable? · V1     │
                  └───────────────────┬────────────────────┘
                                      │  synthesizes, then links down ↓
        ┌────────────────┬────────────┼─────────────────────────────┐
        ▼                ▼            ▼                             ▼
 source_selection.md discussion/  plans/                       Notebooks/
 source roles        the          decisions · schema ·          the worked
 and tradeoffs       reasoning    assumption registers          pipelines (code)
```

| Layer | Home | Role |
|---|---|---|
| **Anchor** *(here)* | `docs/hazards/<hazard>/` | the synthesized snapshot — the map |
| **Source selection** *(here)* | `docs/hazards/<hazard>/source_selection.md` | the bridge from Drive candidates to the V1 source spine |
| **Modeling choices** *(here)* | `docs/hazards/<hazard>/modeling_choices.md` | M0-M4 modeling-choice rationale: distributions, coupling, M3/M4 mechanics, assumptions |
| Reasoning | [`docs/extra/discussion/`](../extra/discussion/) | where we think things out before building |
| Decisions / contract | [`docs/plans/`](../plans/) | what we decided, the schema, the assumption registers |
| Code | [`Notebooks/`](../../Notebooks/README.md) | the worked pipelines |

> **The one rule that keeps this clean:** the anchor **synthesizes and links** — it never becomes a second
> copy of a register, a schema, or a run log. If a number or decision has an authoritative home, the anchor
> summarizes it and links there.

## The structure mirrors the model (and the notebooks)

Each hazard folder follows the **peril → (peril × asset)** seam. The model itself is a **five-stage pipeline,
`M0 → M4`** — the same five stages every hazard anchor, per-asset page, and notebook refers to, so it's worth
drawing once here (the anchors lean on this rather than re-explaining it):

```
                  PERIL — asset-free                         PERIL × ASSET — specialized to the asset
         (identical for whatever asset sits there)                  (the asset enters at M2)
        ◄──────────────────────────────►                 ◄────────────────────────────────────────────►

        ┌─────────┐     ┌─────────┐                       ┌─────────┐     ┌─────────┐     ┌─────────┐
        │   M0    │ ──► │   M1    │ ───── asset ─────────► │   M2    │ ──► │   M3    │ ──► │   M4    │
        │  input  │     │ catalog │       enters          │coupling │     │ damage  │     │ loss &  │
        │  data   │     │ + freq  │       here            │         │     │         │     │ metrics │
        └─────────┘     └─────────┘                       └─────────┘     └─────────┘     └─────────┘
          raw hazard      events as                         does the        if it hits,     compound-MC
          evidence —      OBJECTS:                          hazard REACH     how BAD?        over years →
          meet &          how OFTEN (λ)                     the asset?       intensity →     annual loss →
          understand      + how BIG                         (coupling        damage ratio    EAL·VaR·PML·
          it (no model)   (severity dist)                   type)            (DR, capped)    TVaR ($,%TIV)
```

`M0/M1` are the **asset-free *peril*** — a hail catalog over a region is the same whether a solar or a wind
farm sits under it. `M2–M4` are the **(peril × asset) *cell*** — they specialize to the asset's geometry,
fragility, and value, which is why **the asset never enters before M2**. The folder layout mirrors exactly
this split (`M0/M1` at the hazard root; `M2–M4` under each asset):

```
docs/hazards/
  README.md            ← this index (the hazard × asset matrix)
  source_selection.md  ← cross-hazard convention for source-selection records
  modeling_choices.md  ← cross-hazard convention for per-hazard modeling_choices.md files
  m0_m4_event_loss_contract.md
                       ← cross-hazard event model, M3/M4 boundary, AEP/OEP doctrine
  hail/
    README.md          ← the HAZARD anchor — asset-free (definition, magnitude, data, M0/M1, limits)
    source_selection.md← why MRMS is the V1 spine; NOAA/MYRORSS roles
    modeling_choices.md← modeling-choice rationale: distributions, coupling, damage, aggregation
    solar.md           ← a (peril × asset) pair — coupling, damage, loss, the two deployments
    wind.md            ← (later, same shape)
  wildfire/  …         ← same template
```

So `hail/README.md` ↔ `Notebooks/hail/` (the catalog); `hail/solar.md` ↔ `Notebooks/hail/solar/` (the cell).

## The matrix — what exists

Rows = perils, columns = assets. Each filled cell links to its `<hazard>/<asset>.md`. **Maturity** is the
honest state, not the aspiration.

| Peril ↓ \ Asset → | Solar PV | Onshore wind | Notes |
|---|---|---|---|
| **Hail** | [solar](hail/solar.md) — *asset run: built; grid: provisional* | *(next)* | [anchor](hail/README.md) · [choices](hail/modeling_choices.md) · [sources](hail/source_selection.md) · [fundamentals](hail/fundamentals_before_m0.md) |
| **Wildfire** | [solar](wildfire/solar.md) — *asset run: built; grid: planned* | — | [anchor](wildfire/README.md) · [choices](wildfire/modeling_choices.md) · [sources](wildfire/source_selection.md) · [fundamentals](wildfire/fundamentals_before_m0.md) |
| **Convective wind** | — | [wind](convective_wind/wind.md) — *asset run: built; grid: planned* | [anchor](convective_wind/README.md) · [choices](convective_wind/modeling_choices.md) · [sources](convective_wind/source_selection.md) · [fundamentals](convective_wind/fundamentals_before_m0.md) — two sub-perils (tornado + strong wind) |
| **Flood** ⎇ | *notebooks imported — built* | *notebooks imported — built* | [anchor](flood/README.md) · [choices](flood/modeling_choices.md) · [sources](flood/source_selection.md) · [fundamentals](flood/fundamentals_before_m0.md) — **docs/plans under review**; 3 sub-perils (riverine · pluvial · coastal) |
| **Hurricane** ⎇ | *notebooks imported — built* | *notebooks imported — built* | [anchor](hurricane/README.md) · [choices](hurricane/modeling_choices.md) · [sources](hurricane/source_selection.md) · [fundamentals](hurricane/fundamentals_before_m0.md) — **docs/plans under review**; field-intensity wind (surge/rain → flood) |

> **⎇ review rows.** Flood and hurricane notebook folders and plan/register docs are now imported to main for
> review. Their anchors and `modeling_choices.md` files are main-branch review guides so the whole picture is
> visible before final product blessing.

## The anchor template (every hazard, same seven sections)

Hazard anchors (`<hazard>/README.md`) are **asset-free** and always carry these sections, so every hazard
reads the same way and a new one is fill-in-the-blanks:

1. **What it is & the magnitude** — the hazard, the intensity variable we model, units, threshold.
2. **Data source(s) & curation** — what we ingest and how raw data becomes a credible magnitude; summarize
   the rationale and link to `source_selection.md` for the candidate comparison.
3. **How we model it — two deployments** — per-asset deep run vs. CONUS screening grid: the *asset-free*
   (hazard-layer) differences and why.
4. **Assumptions** — the load-bearing ones (linking to the registers for the full line-items).
5. **Challenges & limitations** — honestly, with candidate solutions where the answer is still open.
6. **Maturity — V1 vs. deferred** — what's reportable, what's provisional, what's future.
7. **Go deeper** — links to reasoning, decisions, and code.

Per-asset pages (`<hazard>/<asset>.md`) carry the **peril × asset** half: coupling, damage, loss/metrics,
and the headline numbers for each deployment.

Hazard modeling choices (`<hazard>/modeling_choices.md`) carry the rationale behind the M0-M4 mechanics:
event-model choices, distribution choices, coupling choices, damage choices, M4 sampling/aggregation choices,
assumptions, confidence, and revisit triggers. The README should still carry the readable M0-M4 story.

## Fast Recap: What Each Layer Asks

Use this when reviewing a hazard notebook or anchor doc.

```text
M0 asks:
  what raw public/private evidence exists?
  what does each source variable mean?
  what units, grain, bias, and no-data traps matter?

M1 asks:
  what hazard event model or return-period/profile object is emitted?
  what frequency basis is used?
  what severity distribution or source curve is carried forward?

M2 asks:
  how does this hazard reach this asset?
  is coupling areal hit/miss, site-conditioned, field-intensity, or per-node?
  what exposure, p_hit, or local intensity goes forward?

M3 asks:
  if the hazard reaches the asset, how bad is damage?
  what component curves and capex weights map intensity to damage ratio?
  what full conditional loss is emitted?

M4 asks:
  across simulated years, what annual losses are realized?
  what are AEP and OEP?
  what are EAL, VaR/PML, and TVaR?
  what is read from the sampled distribution instead of an expected-loss shortcut?
```

There is no generic M5 in this repo today. If added later, it should be the platform-integration layer that feeds
portfolio aggregation, pricing/reporting, and decisions.
