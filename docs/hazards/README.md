# docs/hazards/ — the hazard anchors

**The front door to each hazard.** One shareable, high-level snapshot per hazard that you read *first*
(and return to when you're deep in the weeds) to keep the whole picture in mind: what the hazard is, how
we model it, what's reliable, what isn't, and what's V1 vs. deferred.

This layer sits **above** the working detail and **points down into it** — it does not duplicate it:

```
                  ┌────────────────────────────────────────┐
                  │  docs/hazards/<hazard>/   ← THE ANCHOR   │   read first
                  │  what · how · reliable? · V1 vs later    │
                  └───────────────────┬────────────────────┘
                                      │  synthesizes, then links down ↓
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
   discussion/                    plans/                       Notebooks/
   the reasoning (why)            decisions · schema ·         the worked
                                  assumption registers         pipelines (code)
```

| Layer | Home | Role |
|---|---|---|
| **Anchor** *(here)* | `docs/hazards/<hazard>/` | the synthesized snapshot — the map |
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
  hail/
    README.md          ← the HAZARD anchor — asset-free (definition, magnitude, data, M0/M1, limits)
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
| **Hail** | [solar](hail/solar.md) — *asset run: built; grid: provisional* | *(next)* | [hail anchor](hail/README.md) |
| **Wildfire** | [solar](wildfire/solar.md) — *asset run: built; grid: planned* | — | [wildfire anchor](wildfire/README.md) |
| **Convective wind** | — | [wind](convective_wind/wind.md) — *asset run: built; grid: planned* | [conv-wind anchor](convective_wind/README.md) — two sub-perils (tornado + strong wind) |

## The anchor template (every hazard, same seven sections)

Hazard anchors (`<hazard>/README.md`) are **asset-free** and always carry these sections, so every hazard
reads the same way and a new one is fill-in-the-blanks:

1. **What it is & the magnitude** — the hazard, the intensity variable we model, units, threshold.
2. **Data source(s) & curation** — what we ingest and how raw data becomes a credible magnitude.
3. **How we model it — two deployments** — per-asset deep run vs. CONUS screening grid: the *asset-free*
   (hazard-layer) differences and why.
4. **Assumptions** — the load-bearing ones (linking to the registers for the full line-items).
5. **Challenges & limitations** — honestly, with candidate solutions where the answer is still open.
6. **Maturity — V1 vs. deferred** — what's reportable, what's provisional, what's future.
7. **Go deeper** — links to reasoning, decisions, and code.

Per-asset pages (`<hazard>/<asset>.md`) carry the **peril × asset** half: coupling, damage, loss/metrics,
and the headline numbers for each deployment.
