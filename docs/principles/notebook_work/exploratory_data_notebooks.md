# Exploratory Data Notebooks — Interpret Every Variable, Not Just Display It

*Why we meet a new data source in a notebook, and what that notebook owes the reader: not a dump of values,
but an understanding — every variable shown **with its meaning, its units, and its reference base** before a
single number is used downstream.*

A **working principle** (how we operate in a mode), built on the three foundational ones — it's
*basics-spot-on* and *hazard × asset specificity* applied to the very first contact with data.

---

## Why this document exists

A notebook's real advantage isn't that it runs code — it's that it has **room for nuance**. It's the one
place where a value and the paragraph explaining what that value *means* can sit in the same frame. Waste
that, and a notebook is just a slow script.

The trigger was concrete. The NRI endpoint returns 363 fields (20 for hail). Showing `hail_hlrb = 6.24e-5`
on its own is *worse than useless* — it invites the reader to multiply it by our asset value and quote a
loss. It is actually a loss ratio against **county building exposure (~$1.19 B of Hazus building value)**,
for **generic community buildings**, not a solar plant — so it must *never* touch our loss path. The number
without its interpretation is a latent bug. **The interpretation is the deliverable.**

---

## The principle: every variable gets value + meaning + base + a use-decision

> **The principle.** In an exploratory data notebook, each variable you surface is shown with: its **value**,
> **what it is**, its **units / reference base** (the denominator!), what it is **not**, and **whether we use
> it and why**. Understanding precedes use.

A loss ratio without its exposure base, a magnitude without its unit, a frequency without its area
normalization — each is a number that *looks* usable and isn't. The notebook's job at M0 is to make every
such trap explicit, on the page.

---

## Sub-principles

### Understand before you use
Profile, quality-audit, and **interpret** a source before any modeling step reads from it. The first
notebook for a peril is about the *evidence*, not the model — and is method-neutral (the data understanding
is identical regardless of the loss math that comes later).

### Match the onboarding to the data's complexity
> **The rule.** Simple **API** data (a tidy table of events, e.g. NOAA) → load and profile. Complex **raw /
> open-source** data (gridded, binary, bucket-delivered, e.g. MRMS GRIB2) → first do a *from-scratch* pass:
> what it **is** (a mental model vs data you know), what one **file/record** literally looks like (decode it;
> show the raw numbers), the **folder/file layout + how you fetch it**, and the **grid / units / fill / CRS**
> conventions — *before any statistic*. Don't gold-plate the simple case; don't under-serve the complex one.
> See [`learning_logs/03`](../../learning_logs/03_meet_complex_raw_data_from_scratch.md) (worked example:
> `02_mrms_aws` §1–§7).

### A number is meaningless without its base
> **The rule.** Always state the denominator: units (inches vs mph), reference base (our asset value vs
> community building exposure), normalization (per-county vs per-radius). The `hail_hlrb` / TIV case is the
> canonical example; the radius-scaling of NOAA counts (25/50/100 mi → 40/373/1762) is another — raw counts
> are not the asset's hit rate.

### Show what you use AND what you ignore (and why)
> **The rule.** A field dictionary lists the consumed fields *and* the deliberately-ignored ones with the
> reason — e.g. we ignore NOAA's own `DAMAGE_PROPERTY`, because using its dollar estimate would import a
> non-PV, inconsistent loss basis. "Fetched but not consumed" is information, not noise.

### Cover every field — a complete pass (primary + secondary)
> **The rule.** When a source has many fields, do a **complete pass**, not a cherry-pick: a **primary**
> table (the fields we use or must understand) and a **secondary** table (everything else). Build both from
> the *actual* columns and **flag any field with no description**, so "I never explained `EPISODE_ID`" shows
> up as a visible ⚠ instead of a gap the reader trips over later.
>
> The test: a reader should never be able to point at a returned column and ask "what is this?" and find it
> missing from the notebook. (This rule exists because exactly that happened — `EPISODE_ID` vs `EVENT_ID`
> went unexplained in the first hail notebook.)
>
> _For **gridded / array** data the same completeness covers **coordinates and attributes**: document the
> grid — CRS, resolution, longitude convention, units, and the **fill / NoData** value (e.g. MRMS MESH: 1 km,
> lon 0–360, mm, `-1` = no-hail) — not just tabular columns._

### Pin the source, cache the raw bytes
> **The rule.** For remote / external data, record **what you pulled and from where** (source, product,
> version, access window, URL pattern) **and cache the raw fetched bytes** locally (under `data/`). A live
> API/bucket can change or rate-limit between runs; caching makes the notebook **reproducible**, makes
> re-runs cheap, and pins the exact data a finding rests on.

### No silent windows or sampling
> **The rule.** If you bound a date range, subset a region, sample, cap, or skip-on-error for volume or
> speed, **say so, say why, and report what's excluded** — in the cell, not in your head. A notebook that
> quietly looks at two months of a five-year record reads as "this is the whole picture" when it isn't.
> State the window, flag the full extent, and name the widening path.

### Cross-reference the foundations
> **The rule.** When a notebook touches a concept that's *defined* in the math / discussion / architecture
> docs, **link to it** — don't re-derive it or leave it floating. (The radius question links to
> `hazard_math/01` and `discussion/gpt/03`; a loss-ratio's base links to the risk-metrics reference.) The
> notebook is connective tissue, not an island.

### Surface the gotchas inline
Reliability windows (NOAA magnitude data trustworthy from ~1996), known biases (report density tracks
population, not hazard), and scaling traps belong **next to the data**, not in someone's head.

### Every output earns a takeaway
> **The anti-pattern.** A plot or table with no written interpretation. If a cell produces a figure, the
> next line says what it tells us — and what it doesn't.

### The notebook is the durable record
The interpreted notebook is where a future data dictionary and the `02_architecture.md` come *from*. The
understanding is paid for once and reused every phase — it compounds.

---

## What every exploratory data notebook should have

The practical checklist (the *how*, sitting next to the *why* — see the README note on guides):

1. **Intent & scope** — which layer this is (e.g. M0) and what it deliberately does *not* do.
2. **Source & provenance** — where the data comes from, its reliability window, known biases; for remote
   data, **pin it and cache the raw bytes** under `data/`.
3. **Fetch** — a thin, readable client, with no downstream entanglement.
4. **Windows & sampling, stated** — any date bound / region subset / sample / skip, with *why* and *what's
   excluded* (no silent caps).
5. **Quality audit** — counts, missing values, dedup, the filters applied.
6. **Field dictionary / interpretation — a *complete pass*** — primary + secondary, value + meaning +
   units/base + use-decision, built from the live columns, undocumented flagged. (Gridded: cover
   coords/attrs + grid/units/fill too.)
7. **Distributions & coverage** — with a written takeaway per figure.
8. **Gotchas & cautions** — the traps that would mislead a reader.
9. **Cross-references** — link concepts to their definition in the math / discussion / architecture docs.
10. **The carried-forward artifact** — the clean record passed to the next phase + the open questions.

---

## Caveats

1. **Don't gold-plate every field.** Interpret where it *matters* or could *mislead* — not all 363 NRI
   fields deserve a paragraph. Depth follows consequence.
2. **Interpretation must be accurate, not invented.** Verify field meanings against the source's own docs;
   mark anything uncertain as uncertain. A confident wrong interpretation is worse than none.
3. **This is understanding, not modeling.** Keep the method out of M0 — the data exploration is shared
   regardless of the loss math downstream.

---

## How this relates to the other principles

| Principle | Connection |
|-----------|------------|
| [Basics spot-on](../basics_spot_on.md) | Understanding the input *is* part of getting the basics right — the wrong reference base is a basics failure (the `hail_hlrb` / TIV trap). |
| [Standard interface, not standard physics](../hazard_asset_specificity.md) | A community-buildings loss ratio ≠ a solar-PV one — interpreting the exposure base is specificity applied to data. |
| [Modular from day one](../modularity_and_scaling.md) | The carried-forward M0 record is the clean, named object the next phase consumes. |

---

## Summary

A value is data; a value *with its meaning and its base* is understanding. Exploratory notebooks exist to
produce the second, before any number is used. Interpret every variable that matters, name its reference
base, say what you ignore and why, give every output a takeaway — and the understanding compounds across
every phase that follows.
