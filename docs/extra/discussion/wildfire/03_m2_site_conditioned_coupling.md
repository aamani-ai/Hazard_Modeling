# 03 — M2: Site-Conditioned Coupling (exploration, before implementation)

*Understanding **how** wildfire's M2 works before we plan or build it — because this is the genuinely
under-charted part (the legacy barely developed it). The surprise: for a **pre-integrated, site-conditioned**
peril, **M2 is thin** — most of the "coupling" happened upstream in FSim/M1, and the rest is **embedded** in
the M3 curve or **deferred**. This doc maps the physics, shows where V1 cuts, and frames the decisions.*

> Exploration, not a plan-of-record. Settles *how it works*; the M2 plan (`docs/plans/wildfire/m2_coupling.md`)
> and the build come after. Siblings: [`01` scope](01_v1_scope_and_framing.md) · [`02` data dictionary](02_fsim_wrc_data_dictionary.md).

---

## 1 · The physics chain — where you "cut" decides what you must model

The legacy's own Gen-2 discussion lays out the full chain from fire to damage:

```
  spatial model        which cells   fire front   distance    intensity    heat flux       temperature   damage
  (extent, direction)  burn          position     to asset d  at asset I    q = 0.35·I/d    T(d, t, I)    %
       └─ Gen3 ──────────────────────────────────────────────┘            └──── Gen3 ────────────┘
       └─ Gen2+ (fire-front sweep gives d, t "for free") ──────┘
  FSim pre-integrates ──────────────────────────┘  (BP + FLP per cell)
```

**Each x-axis you pick demands more upstream modeling:**

| Curve x-axis | You must model | needs `d`? | needs duration `t`? | curve embeds | tier |
|---|---|---|---|---|---|
| Flame length (ft) | FSim FIL → FL | no | no | everything (d, t, response) | Gen 1 (legacy) |
| **Intensity (kW/m)** | FSim FIL → Byram → I | **no — embed `d`** | no — embed `t` | `d`, `t`, material response | **Gen 2 — our V1** |
| Heat flux (kW/m²) | I, d → `q=0.35·I/d` | **yes** | no | t, response | Gen 2+ |
| Temperature (°C) | I, d, t → ΔT | **yes** | **yes** | threshold only | Gen 3 |

**V1 cuts at intensity (kW/m) with `d` embedded** — exactly where M1 already left us (the FLP→kW/m severity
distribution). The damage-curve library embeds **`d = 10 m`** and a representative duration; explicit `d`/`t`
need a **fire-front sweep**, which we defer ([AW-28](../../plans/wildfire/assumptions.md)).

---

## 2 · The surprise: for a pre-integrated site-conditioned peril, **M2 is thin**

Hail's M2 was heavy — a Minkowski overlap (`(√F+√s)²/A`) computing a per-event hit probability against the
asset polygon. **Wildfire has no such step**, for two compounding reasons:

1. **FSim pre-integrated the events** ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) — there's no event set to overlap; the hazard is a per-cell field.
2. **Site-conditioned → no spatial factor** (methodology: *"there is no 'miss'… the rate comes from the site
   intensity process directly"*). M1 already sampled BP + FLP **at the asset footprint** and produced
   `(λ, kW/m severity)`.

So **M1 did the coupling that M2 does for hail.** What's genuinely left for wildfire's M2 is small:

| M2's real V1 jobs | What it is |
|---|---|
| **(a) Oozing / surrounding-fuel** | Where the asset pixel is mapped *developed* (BP present, intensity suppressed — [AW-15](../../plans/wildfire/assumptions.md), confirmed at Hayhurst), source the on-site intensity from the **surrounding-fuel footprint/ring**, not the centroid. The Hydronos `buffer_ring` is the ready tool. |
| **(b) Exposure fraction** | Does a fire expose the **whole site** or a fraction? V1 = whole-site on a fire (the area-average); partial-burn correlation is the fire-front-sweep, deferred (AW-28). |
| **(c) Susceptibility** | The intensity→damage modifier. V1 **embeds** it in the M3 curve (`d=10 m`); explicit per-site susceptibility is deferred (§4). |
| **(d) The typed handoff** | Emit, per simulated fire, `(occurrence ~ Poisson(λ), conditional intensity ~ FLP→kW/m)` — the same schema the shared engine + M3 consume. |

> So M2's V1 deliverable is mostly **(a) + (d)**: the oozing correction + the clean handoff. **(b)** and **(c)**
> are *consciously embedded or deferred* — and saying so plainly is the point of this doc.

---

## 3 · Your point #1 — we use a **stale simulator OUTPUT**, not a live run (AW-25 / AW-26)

We consume **pre-computed FSim/WRC rasters** — a *snapshot* of a LANDFIRE fuel vintage (**BP ≈ end-2020,
intensity ≈ end-2022**). We do **not** run FSim on today's fuels. The Hazard Data Reference is blunt about it:
the hazard *"ages fast… USFS re-runs every 1–2 yr… don't treat a hazard map as stationary."*

- **What this means:** a site whose fuels changed *after* the vintage — a recent burn scar (now low fuel), a
  fuel treatment, or post-fire regrowth — is mis-stated by the stale raster.
- **The ideal, approximate fix (AW-26, deferred):** a **currency adjustment factor** — overlay recent burn
  history (**MTBS** scars + **WFIGS** perimeters) onto the stale BP/intensity to nudge it toward current
  conditions. The lab already sketched this path. It's *not* a full re-run (which needs the FSim simulator +
  current LANDFIRE) — it's a cheap, honest recency correction.
- **V1 decision:** record the **exact vintage** in the manifest and treat the hazard as a non-stationary
  snapshot; **defer** the currency factor. (This is a genuine limitation, now on the page, not hidden.)

---

## 4 · Your point #2 — site features (defensible space, fences) → the distance `d` (AW-27)

The damage-curve doc gives us the hook directly: *"Curves assume a reference distance of `d = 10 m` from the
fire front to the asset. **For assets with larger defensible space, intensity thresholds shift upward
proportionally.**"* So:

```
  more defensible space / fire breaks / fences / cleared land
        → larger effective distance d
        → q = 0.35·I/d  drops          (heat flux ∝ 1/d for a fire FRONT — line source)
        → curve thresholds shift UP    → less damage at the same fireline intensity
```

**This is the explicit site-feature susceptibility** — and it lives in the **distance `d`**. The catch: it is
**in no public dataset.** A 270 m FSim cell can't see a 30 m firebreak or a cleared buffer around the array.

- **V1 decision:** **embed `d = 10 m`** (the curve's reference) for everyone — a single, documented,
  slightly-conservative susceptibility. ([AW-27](../../plans/wildfire/assumptions.md); pairs with [AW-16](../../plans/wildfire/assumptions.md).)
- **Deferred (Gen 2+):** a **per-site `d`** derived from **site data or imagery** (defensible-space width,
  fire breaks, equipment setback) — the imagery idea from [`01` Decision 4](01_v1_scope_and_framing.md). This
  is where "do they have fences?" actually enters the model.
- ⚠️ **Pre-build fix:** the doc's causal chain writes `q ∝ I/d²` (point source) — **wrong** for a fire front
  (`∝ I/d`). Pin to `1/d` before any heat-flux work ([AW-17](../../plans/wildfire/assumptions.md)).

Both your points are the *same shape*: **the regional, stale raster doesn't reflect the actual, current
site** — once in *time* (vintage → currency factor), once in *space/detail* (site features → distance `d`).
V1 **embeds defensible defaults and defers explicit modeling** — honestly flagged, not silently dropped.

---

## 5 · What V1's M2 emits (the contract)

Per asset, per simulated fire year (feeding the shared compound engine + M3):

```
  occurrence  ~ Poisson(λ)                      # λ from M1 (= −ln(1−BP)); site-conditioned, no spatial factor
  if a fire:
     intensity ~ FLP→kW/m distribution (M1)     # oozing-corrected: surrounding fuel where the pixel is developed
     exposure  = whole site (V1)                # partial-burn deferred (AW-28)
     → M3 curve (kW/m, d=10 m embedded) → damage ratio → loss
```

No Minkowski, no `p_hit` overlap, no spatial factor — just occurrence × conditional intensity, with the
oozing correction. The interface out is identical to hail's, which is the whole point: *standard interface,
specialized physics.*

---

## 6 · Open decisions for the M2 plan (to settle before building)

1. **Oozing rule (the main V1 substance).** When the asset pixel is developed (intensity suppressed): use a
   **surrounding buffer ring** (which radius? — Hydronos `buffer_ring`, or our own zonal on a ring) vs the
   nearest burnable pixel vs the regional cell. *Recommend:* a small surrounding-fuel ring; decide the width.
2. **Exposure fraction.** Whole-site-on-fire (V1) vs a coarse partial-burn. *Recommend:* whole-site for V1
   (single small-ish sites; partial-burn is the fire-front-sweep, deferred).
3. **Susceptibility `d`.** Confirm embed `d = 10 m` (V1) and defer per-site `d`. Fix the `I/d²`→`I/d` doc bug.
4. **Currency.** Confirm the stale-vintage adjustment (AW-26) is **out of V1** (record vintage only).
5. **Do we even need a separate M2 notebook,** or does the thinness mean M2 folds into M1→M3? *Lean:* keep a
   short M2 notebook for the **oozing correction + the explicit handoff + the susceptibility declaration** —
   the documentation value (showing the coupling is thin *and why*) is worth its own cell, per the
   exploratory-notebook principle.

## 7 · Deferred (named, so the fence is visible)

- **Fire-front sweep** — partial burn, contiguous front, explicit `d` + residence time `t`, real PML/tail
  (Gen 2+).
- **Explicit site-feature susceptibility** — per-site `d` from imagery/site data (defensible space, fences,
  fire breaks) (Gen 2+ / Decision 4).
- **Currency adjustment** — MTBS/WFIGS recency overlay (AW-26).
- **Heat-flux / temperature curves** — need explicit `d`, `t` (Gen 3).

---

*Next: turn this into `docs/plans/wildfire/m2_coupling.md` (the plan-of-record — the oozing rule, the contract,
the embedded-`d` susceptibility, the verification), then build a short M2 notebook. The heavy lifting is
upstream (FSim/M1) or deferred — V1's M2 is the oozing correction + the honest handoff.*
