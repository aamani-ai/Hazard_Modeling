# docs/hazards/ — the hazard anchors

**The front door to each hazard.** One shareable, high-level snapshot per hazard that you read *first*
(and return to when you're deep in the weeds) to keep the whole picture in mind: what the hazard is, how
we model it, what's reliable, what isn't, and what's V1 vs. deferred.

Before opening any hazard's M0 notebooks, read the cross-hazard prerequisite guide:
[`fundamentals_before_m0.md`](fundamentals_before_m0.md). It defines the "before M0" mental model:
understand the physics, understand the data-source reality, then translate both into the M0-M4 pipeline.

Between the Drive references and the notebooks, read the source-selection layer:
[`source_selection.md`](source_selection.md) plus the hazard-specific `source_selection.md` file. That is where
we record which candidate dataset becomes the V1 spine, which sources are validation-only, and which are
rejected or deferred.

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
  hail/
    README.md          ← the HAZARD anchor — asset-free (definition, magnitude, data, M0/M1, limits)
    source_selection.md← why MRMS is the V1 spine; NOAA/MYRORSS roles
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
| **Hail** | [solar](hail/solar.md) — *asset run: built; grid: provisional* | *(next)* | [hail anchor](hail/README.md) · [sources](hail/source_selection.md) · [fundamentals](hail/fundamentals_before_m0.md) |
| **Wildfire** | [solar](wildfire/solar.md) — *asset run: built; grid: planned* | — | [wildfire anchor](wildfire/README.md) · [sources](wildfire/source_selection.md) · [fundamentals](wildfire/fundamentals_before_m0.md) |
| **Convective wind** | — | [wind](convective_wind/wind.md) — *asset run: built; grid: planned* | [conv-wind anchor](convective_wind/README.md) · [sources](convective_wind/source_selection.md) · [fundamentals](convective_wind/fundamentals_before_m0.md) — two sub-perils (tornado + strong wind) |
| **Flood** ⎇ | *on `flood` branch — built* | *on `flood` branch — built* | [flood anchor](flood/README.md) · [sources](flood/source_selection.md) · [fundamentals](flood/fundamentals_before_m0.md) — **preview**; 3 sub-perils (riverine · pluvial · coastal) |
| **Hurricane** ⎇ | *on `hurricane` branch — built* | *on `hurricane` branch — built* | [hurricane anchor](hurricane/README.md) · [sources](hurricane/source_selection.md) · [fundamentals](hurricane/fundamentals_before_m0.md) — **preview**; field-intensity wind (surge/rain → flood) |

> **⎇ preview rows.** Flood and hurricane are built on their own branches by another team, under cross-review
> (as is everything on main — we cross-review each other). Their anchors are **high-level syntheses** so the
> whole picture is visible from main; the code/plans land on main when review completes. The other rows' work
> lives on main already. Merging the branches is handled separately.

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
