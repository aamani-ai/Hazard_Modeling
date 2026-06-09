# Meet Complex Raw Data From Scratch — Before You Use It

*Why simple API data you can just load and profile, but complex raw open-source data (gridded radar files,
binary formats, bucket-delivered) earns a deliberate ground-up pass first — what is it physically, what does
one file look like, how is the raw data laid out — before a single number is used downstream.*

**Status:** v1.0 · written 2026-06-09 · **Sourced from:** hail × solar, Phase 1 / M0 (NOAA vs MRMS) · **Applies to:** every new data source — and especially any *raw / gridded / binary / open-source* one.

---

## Where this came from

Two M0 hail sources, two completely different experiences:

- **NOAA Storm Events** (notebook 01) came over a simple **API** as a tidy table of events. Easy — you read
  it like a spreadsheet, profile it, write a field dictionary, done.
- **MRMS MESH** (notebook 02) is **raw open-source data**: gridded radar files (GRIB2) on a public AWS
  bucket. It was genuinely *hard to understand* — what is this format? is it events? where's the polygon?
  how do we even get it? — until we stopped and built a from-scratch *"what is this data"* pass (now §1–§7
  of [`02_mrms_aws`](../../Notebooks/hail/m0_input_data/02_mrms_aws.ipynb)).

The owner named the gap precisely: that ground-up pass is exactly what was missing, and it should be
**standard practice** whenever we tackle this kind of data — *"take the time and a good cell to first define
the dataset, its folder structure, and how the raw data sits."*

## Why it looked fine — the trap

With simple API data you can skip straight to profiling, because the format is self-evident (a table of
rows). The trap is treating **complex raw data the same way** — jumping into statistics on a gridded radar
field before establishing what it physically *is*, what one file/record looks like, the folder/file layout,
and the unit/fill/CRS conventions. Do that and the whole downstream analysis sits on a format you don't
actually understand — and the silent errors are exactly the kind that bite: a `0–360` longitude convention,
`< 0` fill sentinels, *"wait, is this events or a continuous field?"*, a 24-h-max accumulation window you
didn't realize was a max. None of these show up as crashes; they show up as wrong answers.

## The lesson

> **The lesson.** Match the onboarding to the data's complexity. **Simple API data** → load and profile.
> **Complex raw / open-source data** (gridded, binary, bucket-delivered) → first take the time to define,
> *from scratch*: (1) what it **is** (a mental model against data you already know), (2) what one
> **file/record** literally looks like (decode it; show the raw bytes / numbers), (3) the **folder/file
> structure and how you fetch it**, (4) the **grid / units / fill / CRS** conventions — **before any
> statistic.** The understanding pass *is* part of the work, not a preamble to skip.

`[REF]` This extends the exploratory-notebook principle ([`exploratory_data_notebooks.md`](../principles/notebook_work/exploratory_data_notebooks.md)
— *"understand before you use; interpret every variable; cover every field"*). `[OURS]` What this adds is the
explicit **two-mode distinction** and the **from-scratch protocol for the complex mode** — born from the NOAA
(easy) vs MRMS (hard) contrast.

### The two modes

| | **Simple data, by API** | **Complex raw data, from an open source** |
|---|---|---|
| Example | NOAA Storm Events (Hydronos JSON) | MRMS MESH (GRIB2 on `s3://noaa-mrms-pds`) |
| Format | tidy table — self-evident | gridded/binary — needs decoding |
| Native structure | already *events* (the unit we reason in) | a *field* — no events; we derive them |
| Onboarding | load → profile → field dictionary | **full from-scratch pass** (below) |

### The from-scratch pass (the shape that worked for MRMS — §1–§7 of `02`)

1. **Mental model** — what *kind* of data is this, vs something we already understand? (NOAA = a list of
   events; MRMS = a picture.)
2. **What it is physically** — the quantity, its units, how it's produced (e.g. MESH is a radar *estimate*,
   a 24-h max, in mm).
3. **What one file/record literally is** — decode the filename/format; show the raw bytes → the actual
   grid of numbers.
4. **The picture** — visualize it; overlay something familiar (NOAA points) to anchor intuition.
5. **How structure is derived** — if the data isn't natively in our unit, show the steps that get it there
   (field → threshold → polygon → "event").
6. **The fetch / folder layout** — where it lives, how it's organized, how we pull and cache it.
7. **Conventions & fills** — CRS, lon range, resolution, NoData sentinels, accumulation window — the traps.

## How to recognize it next time

You need the full pass when the data is delivered as **raw files** (not a tidy API), is
**gridded/array/binary**, carries its **own conventions** (CRS, fill values, lon ranges, accumulation
windows), or **isn't natively in the unit you reason in** (a field, not events). When in doubt, do the pass —
it is cheap relative to a silent format error, and it's paid once per source then reused every phase.

## Caveats and limits

- **Don't gold-plate simple data.** A tidy API table doesn't need an eight-part essay — *depth follows
  complexity* (the existing principle's caveat). The two-mode rule cuts both ways.
- **Keep it method-neutral.** The from-scratch pass is about *understanding the evidence*, not the model —
  same discipline as the rest of M0.
- **It compounds.** The pass is a one-time cost that becomes the durable reference (the §1–§7 of `02` is now
  where a future data dictionary / onboarding comes from).

## Cross-references

- **Principle it extends:** [`principles/notebook_work/exploratory_data_notebooks.md`](../principles/notebook_work/exploratory_data_notebooks.md).
- **Worked example:** [`Notebooks/hail/m0_input_data/02_mrms_aws.ipynb`](../../Notebooks/hail/m0_input_data/02_mrms_aws.ipynb) §1–§7 (the from-scratch pass) — contrast with `01_noaa_hydronos` (the simple API mode).
- **Downstream consequence:** [`learning_logs/01`](01_extending_a_short_hazard_record.md) (MRMS's short record), and the M1 [catalog](../../Notebooks/hail/m1_catalog/01_event_catalog.ipynb) (where the derived events live).
