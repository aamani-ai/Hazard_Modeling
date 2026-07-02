# M1 — Coastal `[C]` catalog (the per-storm surge event catalog)

*The **coastal branch** of the M1 fork — and the **deliberate exception**: it is **event-based**, not return-period
indexed. It builds a **per-storm surge catalog** (hurricane category + `event_family_id`) with an observed-anchored
annual frequency `λ`, for **every coastal-exposed site of both assets** in one pass. Its partner is the
**compound-Poisson hurricane engine**, not the flood annual-max — so at M4 it joins the hurricane **wind** leg on
the same storm and combines **per subsystem** ([JD-FL-12](../../../../docs/plans/flood/decisions.md)).*

**Where this sits:** [M0 evidence](../../m0_input_data/README.md) → **M1 (catalog — coastal fork)** → M2 coupling →
M3 damage → M4 loss (compound surge×wind). Parent: [`m1_catalog/`](../README.md). Sibling forks:
[`riverine/`](../riverine/README.md) · [`pluvial/`](../pluvial/README.md). Plan:
[`m1_catalog.md`](../../../../docs/plans/flood/m1_catalog.md). Notebook: [`01_catalog`](01_catalog.ipynb) (built).

## Method — RAFT screen + HURDAT2 frequency ([JD-FL-21](../../../../docs/plans/flood/decisions.md))
- **Event screen:** the **RAFT** synthetic North-Atlantic TC catalog (`RAFT.NA.v20231016.nc`) — each storm passing
  **≤ 50 km at ≥ 64 kt** → a per-storm row (`category`, `event_family_id`).
- **Frequency `λ`:** **observed-anchored** from **HURDAT2** close-passages within 50 km over the ~173-yr record.
- **Depth:** **NOAA SLOSH MOM** (`US_SLOSH_MOM_Inundation`, high-tide) by category — *named here, sampled in M2*.
- **`event_family_id` switched ON** (stamped per storm) so M4 joins surge ↔ hurricane wind on the **same storm**.

**Magnitude metric:** coastal surge **depth (ft above ground)** by **hurricane category (1–5), per storm**. M1 carries
the event dimension (category + `event_family_id`) + `λ`; the depth itself is sampled from SLOSH MOM in M2.

## What `01_catalog` found
Per-site event catalogs over the observed record, each storm `event_family_id`-stamped:

| site | asset | storms (by category) | λ /yr |
|---|---|---|---|
| **Discovery Solar Center** (FL) | solar | **117** {1:62, 2:33, 3:16, 4:5, 5:1} | ≈ **0.029** |
| **LA3 West Baton Rouge** (LA) | solar | **11** {1:9, 2:1, 3:1} (Gulf surge up the Mississippi) | ≈ **0.0173** |
| **Amazon Wind Farm US East** (NC) | wind | **24** {1:21, 2:2, 3:1} (Albemarle Sound funnel) | ≈ **0.0116** |
| Hayhurst / inland sites | both | — | **structural zero** (no coastline) |

- The **cross-link checks out** — qualifying storms also hit the hurricane-cell sites, confirming the global
  storm-identity joins (`event_family_id`).
- **Known-answer checks pass:** depth rises monotonically with surge category; dry/inland sites read ≈ 0.
- **Screening-grade caveat:** SLOSH MOM is a **per-category worst-case envelope**, not per-event (the ADCIRC gap,
  [JD-FL-14](../../../../docs/plans/flood/decisions.md)).

## Inputs → outputs
RAFT catalog + HURDAT2 tracks/landfalls (+ SLOSH MOM, sampled in M2) → `data/flood/flood_coastal_m1_catalog_manifest.json`
(per-site `sites` list + `high_site`/`baseline_site` keys) + per-site, per-storm parquets (each row
`event_family_id`-stamped). Unlike riverine/pluvial, `event_family_id` is **switched on** here.

## Decisions & assumptions
[JD-FL-12](../../../../docs/plans/flood/decisions.md) (compound surge×wind, per-subsystem max on `event_family_id`) ·
[JD-FL-14](../../../../docs/plans/flood/decisions.md) (SLOSH category spine, source-tagged) ·
[JD-FL-21](../../../../docs/plans/flood/decisions.md) (RAFT close-passage screen + observed λ) ·
[JD-FL-16/17](../../../../docs/plans/flood/decisions.md) (wind leg appended to hurricane; all-three sites) ·
[JD-FL-19](../../../../docs/plans/flood/decisions.md) (M1 = field/event catalog, M2 = coupling) ·
[JD-FL-4](../../../../docs/plans/flood/decisions.md) (`event_family_id` hook). Register:
[`assumptions.md`](../../../../docs/plans/flood/assumptions.md).

**Next → M2 (coupling):** sample SLOSH-MOM depth by category at each asset (areal for solar, per-node for wind) →
**M4** joins the hurricane wind leg on `event_family_id` and runs the per-subsystem `max(wind_DR, surge_DR)` combine.

## Method In Plain English: Storm Identity Matters

Coastal is different from riverine and pluvial because the same hurricane can create both wind loss and surge loss.
That means the model must keep storm identity instead of reducing everything to a return-period curve too early.

```text
RAFT synthetic/track screen
  which storms pass close enough and strong enough?

HURDAT2 observed record
  how often do comparable storms occur?

SLOSH MOM
  if a Cat-1/2/3/4/5 storm affects this coast, what surge depth envelope is plausible?

event_family_id
  the key that lets M4 join surge loss to hurricane wind loss for the same storm
```

The event row has this mental shape:

```text
event_family_id = storm_123
category        = 3
site            = Discovery Solar
surge source    = SLOSH MOM Cat-3 depth field
frequency       = coastal event rate lambda and category mix
```

Then M2 samples the surge field at the asset:

```text
storm_123 Cat-3 surge field
        |
        v
solar footprint or wind nodes
        |
        v
exposure/depth for that same storm_123
```

And M4 combines:

```text
same storm_123:
  hurricane wind loss
  coastal surge loss
        |
        v
  per-subsystem max on shared equipment
```

SLOSH MOM is a screening-grade envelope, not a per-storm hydrodynamic simulation. The model is therefore strongest as a
transparent event-identity bridge and weakest where precise per-storm surge depth would require ADCIRC-grade modeling.

## What Coastal M1 Asks

```text
coastal M1 asks, for each coastal site:
  which storms pass the distance and wind-speed screen?
  what hurricane category is assigned?
  what event_family_id identifies the storm?
  what observed-anchored annual rate lambda should drive storm counts?
  which SLOSH category layer should M2 sample?
```

It does not ask:

```text
  exactly how much of the solar polygon is wet?
  exactly which wind turbines are flooded?
  how much damage happens?
```

M1 carries storm identity and category. M2 samples the surge at the asset; M3 prices the depth; M4 joins surge to
hurricane wind.
