# M1 — Catalog (the active plan) · *the peril, shared & asset-independent*

*The modeling layer that turns M0's raw RAFT tracks into **events as objects** — a storm-resolved, per-site
**3-second-gust catalog**, with each event carrying identity (`event_family_id`). This is **the peril**: it is
asset-independent, so the same catalog feeds hurricane × solar (V1), hurricane × wind farm (V2), and — via the
cross-link — flood's coastal `[C]` and pluvial-TC `[F]`. The one genuinely new build here is the **footprint
synthesis** (track → Holland field → asset sample) authored in [layer-0](00_hazard_definition.md).*

**Where this sits:** layer-0 → [M0](m0_input_data.md) → **M1 (catalog)** → [M2](m2_coupling.md) →
[M3](m3_damage.md) → [M4](m4_loss_metrics.md).

---

## What M1 produces (the contract M2 reads)

A **storm-resolved event catalog at each site**: one row per (storm, site) for storms whose field reaches the site,
with the **3-s peak gust** at the site, the storm's metadata, and identity:

```
event_id · event_family_id · site_id · year(synthetic) · peak_gust_3s_mph
         · max_sustained_ms · central_pressure_hpa · rmw_km · closest_approach_km
```

- **`event_family_id`** is stamped here ([ATC-11](assumptions.md), [JD-TC-4](decisions.md)) — **now active**:
  flood coastal (built) consumes it so a coastal/pluvial-TC event points back to its parent storm (no double-count).
  It is the *one* thing expensive to retrofit.
- **No `rainfall_mm`** — the RAFT tracks file carries no rainfall variable (confirmed at build; rainfall is the
  deferred 16 GB slice, flood's pluvial-TC — [JD-TC-6](decisions.md)).
- The frequency is **observed-anchored** ([JD-TC-8](decisions.md)) — count of distinct HURDAT2 hurricanes ≥64 kt
  passing within 100 km ÷ record years; RAFT's raw genesis rate is a ~71× oversample, so it supplies the severity
  (gust) shape only, not the rate.

This is **event-based** (discrete storms), so it feeds the shared event MC **directly** — no RP-curve bridge
(contrast flood, which had to build one in [JD-FL-7](../flood/decisions.md)). A clean fit, like hail.

---

## The build steps

### 1. Track → continuous wind field — Holland (1980) ([JD-TC-7](decisions.md), [ATC-6](assumptions.md))
For each RAFT track, build a **Holland radial wind profile** at each track step from central-pressure deficit +
RMW, sweep it along the track with **asymmetry** (forward-motion vector + inflow angle), and take the **peak**
gust experienced at the site over the storm's passage. Use an open implementation (CLIMADA's Holland, or a thin
local one verified against it).
- **Parameters authored (sensitivity-tested, [ATC-6](assumptions.md)):** Holland **B** (from pressure/latitude or a
  fitted form), **RMW** (RAFT-provided where available), **environmental pressure**, asymmetry strength.
- **Gust factor ([ATC-7](assumptions.md)):** RAFT wind is **1-min sustained** → multiply by a **gust factor
  (≈1.1–1.3)** to the **3-s gust** the damage curve expects. Apply **once, here.**
- **Units ([ATC-8](assumptions.md)):** RAFT `vmax` is **knots → mph ×1.150779** (ATC-8 corrected at build; only STORM is m/s ×2.237).

### 2. Sample at the site — the field at the asset
V1 samples the field at the **site centroid** (one value per storm) — the **spatially-degenerate** field-intensity
read for solar ([JD-TC-2](decisions.md)). (The wind-farm cell — **built** — samples per turbine; the field-build above is identical —
only the sampling points change. *Modular-from-day-one*: the field is the peril; sampling is the cell.)

### 3. Frequency — observed-anchored ([JD-TC-8](decisions.md))
Storms/year near the site = **count of distinct HURDAT2 hurricanes ≥64 kt passing within 100 km ÷ record years**
(the RAFT raw genesis rate is a ~71× oversample, so it is *not* used for λ — RAFT supplies the severity/gust shape
only). Carry per-storm, not just an aggregate λ, so M4 samples actual events.

### 4. Stamp identity & emit
Assign `event_id` per (storm, site) and `event_family_id` per storm (shared across perils). Emit the catalog +
manifest.

---

## Validation — the M1 known-answer checks (basics-spot-on)

1. **Holland field vs observed landfalls** — replay the **IBTrACS/HURDAT2** historical tracks near each site through
   the *same* Holland code; modeled landfall gust must reproduce observed (within a stated tolerance). This is the
   load-bearing check — it validates the authored field method, not just the data.
2. **Catalog RP vs an independent tail benchmark** — ✅ **done in [02_tail_validation](../../../Notebooks/hurricane/m1_catalog/02_tail_validation.ipynb)**
   using **ASCE 7-22** (an independent engineering hurricane model — chosen over STORM, which is a RAFT *cousin* with
   the same blind spot): our RP gusts match ASCE within **5.5%** over 100–700 yr, no low bias. The **STORM RP-grid**
   cross-check (Zenodo `10931452`, ~1.1 GB; m/s ×2.237) is now an **optional peer-method implementation cross-check
   only** — *not* needed for accuracy (ASCE settled it) and *not* a coverage gap (US-only → ASCE covers our sites).
3. **Frequency sanity** — storms/year near each site vs the observed IBTrACS/HURDAT2 landfall rate (right order).
4. **Unit/threshold checks** — gust > sustained by the gust factor; gusts in mph; baseline (Hayhurst) ≈ near-zero.

---

## Outputs

```text
data/hurricane/<asset>_tc_m1_catalog.parquet     per-(storm,site) 3-s-gust events + event_family_id + metadata   (gitignored)
data/hurricane/<asset>_tc_m1_field_<storm>.tif    (optional) example Holland field rasters for QA/plots           (gitignored)
data/hurricane/<asset>_tc_m1_manifest.json        Holland params, gust factor, units, synthetic years, validation  (kept)
```

## Assumptions surfaced (this layer)

[ATC-5](assumptions.md) (RAFT) · [ATC-6](assumptions.md) (Holland field) · [ATC-7](assumptions.md) (gust factor) ·
[ATC-8](assumptions.md) (units) · [ATC-9](assumptions.md) (frequency from RAFT) · [ATC-10](assumptions.md)
(validation + STORM low tail) · [ATC-11](assumptions.md) (`event_family_id` reserved) · [ATC-18](assumptions.md)
(climate non-stationarity = overlay, not embedded).

## Open questions to resolve in / before M1 *(resolved in the build — kept for context)*

- **Holland B form** — which parameterization (Holland 2008 pressure-based vs a fitted local form)? Decide + sensitivity-test.
- **Gust factor value** — pin ≈1.1–1.3 with a source; sensitivity-test.
- **RMW source** — use RAFT's RMW directly or a wind-radii model where missing.
- **Asymmetry model** — forward-motion + inflow form for V1.
- **Field resolution** — sample at the centroid only (V1) vs a small grid over the footprint (cheap robustness check).

*(Resolved at build — the Holland field is built, severity validated (90 kt == observed) and the tail matches ASCE 7-22 within 5.5% over 100–700 yr; see [`02_tail_validation`](../../../Notebooks/hurricane/m1_catalog/02_tail_validation.ipynb).)*

**Next → [M2 (coupling)](m2_coupling.md):** the **field-intensity** coupling — sample the site field against the
solar footprint (degenerate: one centroid value), emitting the per-event exposure the damage curve reads.
