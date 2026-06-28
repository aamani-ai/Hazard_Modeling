# CONUS grid — assumptions register (draft)

The cross-cutting **assumptions** the gridded-risk product (use case 2) rests on — the analogue of the hail
[`assumptions.md`](../../../plans/hail/assumptions.md), but for the *grid* layer rather than a peril. An
assumption here is an input/parameter/simplification we **take as given** to make the CONUS grid tractable.
**Per-hazard** frequency/severity assumptions (the M1 hazard field) live in each peril's own register; this
file holds only what is **common to every cell**: the canonical asset, the area→cell translation, the engine
settings, the grid, and the reporting basis.

**Status:** 🟡 draft (discussion). Initial plan register now lives at
`docs/plans/hazard_conus_grid/assumptions.md`.
**Legend:** `measured` · `assumed` · `heuristic` (assumed, weakly grounded) · `decided` · `deferred`.

---

## Exposure — the canonical asset

| # | Assumption | Basis / why | Status | Confidence | Revisit when |
|---|---|---|---|---|---|
| **G1** | **Canonical asset = 100 MW solar + 100 MW wind**, placed at each cell **centre**; one full M0→M4 run per (cell × asset). | A standardized exposure → the map reflects *location/hazard* differences, not asset differences (the right basis for a comparable CONUS map). Same engine as the per-asset product (use case 1) with the asset held canonical. | decided | — | a second canonical size/config is wanted for sensitivity |
| **G2** | **Solar canonical asset = 100 MW dense areal footprint over `s_solar` = 1.5 km²**. Derived constant: **66.7 MW/km²**. | **Measured** from USPVDB polygon areas (`p_area`), median over 5,712 facilities — the most directly grounded number we have. `[REF]` org insight `capacity_area_scaling_solar_wind.md`. Supersedes the rougher 5 ac/MW used in single-site hail (A12); difference is immaterial for hail since `s ≪ F` and largely cancels (G4). Solar is treated as a compact damageable area; panel row spacing, inverter layout, tracker details, and exact sub-layout are real-asset inputs, not grid inputs. | **measured / decided (v1 default)** | high | USPVDB v4; or canonical defined as MW_AC (see note) |
| **G3** | **Wind canonical asset = 100 MW = 20 turbines × 5 MW**, spread over a **30 km² spacing envelope**. Derived constants: **0.667 turbines/km²** and **3.33 MW/km²**. | Fixed generic wind farm for the comparative grid. USWTDB gives turbine points, not a universal land-area footprint; the envelope is a planning-grade standard plant, not a measured project boundary. Keeping it fixed makes the map a location/hazard comparison. | **decided (v1 default)** | medium | measured wind-boundary source lands; or owner chooses a second canonical size |
| **G3a** | **Wind engineering defaults:** hub height **100 m**, turbine class **IEC Class II**, terrain/exposure **ASCE Exposure C / open terrain**; no topographic speed-up or terrain class variation in v1. | These are fixed baseline assumptions for the grid, not a claim about every real wind farm. Real-asset runs can use actual hub height, turbine model/class, and local terrain. Future grid improvements can add named scenarios; the baseline should not silently vary by cell. | **decided (v1 default)** | medium | topographic adjustment, class I/III sensitivity, or hub-height scenarios are explicitly requested |
| **G3-note** | **The wind 30 km² is a sparse-turbine envelope, not a contiguous damageable target.** | A hail/tornado swath clipping the 30 km² envelope does **not** damage all 100 MW. For narrow-path / areal-hit perils, use **fractional turbine-density exposure**: expected affected capacity fraction from overlap with the envelope, capped at 100%. The envelope can be used directly only for broad field/site-conditioned perils where the whole project samples local intensity. | **decided (caveat)** | — | a real-asset run supplies actual turbine lat/longs; or a grid known-answer check proves synthetic coordinates are needed |

> **AC/DC note (G2).** The solar density is per **MW_DC**. If the canonical "100 MW" is read as **MW_AC**, the
> array is larger by the DC/AC ratio (~1.2–1.3×) → `s_solar ≈ 1.8–2.0 km²`. Working number is **1.5 km²**
> (MW_DC basis); pin the AC-vs-DC reading of "100 MW" as a one-line sub-decision before build. Immaterial for
> hail (cancels), matters more for any future area-sensitive coupling.

## Exposure — the area → cell translation (the logic to document)

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G4** | **The canonical asset is a *sub-cell* exposure unit**: `s ≪ cell_area` (~600 km²) — solar ~0.25%, wind ~5% of a cell — and `s ≪ A` (the collection region). | Two consequences: **(i)** the asset samples essentially **one cell's** hazard value (no multi-cell spanning at this size); **(ii)** for hail the cancellation `λ_asset = ρ·E[(√F+√s)²]` holds — **cell size does not bias the rate, but `s` does** (it's in the numerator, doesn't cancel). So `s_solar`/`s_wind` are genuine model inputs, not cosmetic. `[OURS]` [learning-log 06](../../../learning_logs/06_collection_region_size_cancels.md). | assumed | wind grows to span multiple cells; or a peril whose footprint `F` is *smaller* than `s` (then `s` dominates) |

## Exposure — granularity (append per hazard × asset)

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G9** | **Exposure is defined at the *coarsest* tier the coupling needs — never finer.** Tiers: **area** (polygon/box) → **fractional point-cloud / density** (sparse turbines as expected affected capacity) → ~~sub-asset config~~ (**never**, for the grid). | A generic plant for a *comparable* map; sub-cell config is unknowable at 0.25° and would be false precision. Granularity is **appended per (hazard × asset)** only where the coupling makes the next tier load-bearing — the exposure-side analogue of the A21 coupling dispatch. Full framework + the reusable asset guide: [`03_exposure_granularity.md`](03_exposure_granularity.md). | decided (framework) | a coupling shows the current tier washes out / is insufficient |

**Per-pair sufficiency — the append register (extend as each pair is built):**

| Hazard × asset | Coupling | Tier used | Enough? | Append trigger |
|---|---|---|---|---|
| **Hail × solar** | areal hit-or-miss | area | ✅ — `s ≪ F`, region `A` cancels ([LL06](../../../learning_logs/06_collection_region_size_cancels.md)) | — |
| **Hail × wind** | areal, **sparse targets** | **fractional turbine-density** | ✅ v1 default | swath hits a *subset* of turbines — use G3/G3-note, not a solid 30 km² polygon |
| **Wildfire × solar** | site-conditioned | area | ✅ for hazard; **susceptibility held canonical** | per-cell susceptibility variance wanted |
| **Wildfire × wind** | site-conditioned + hub-height | box | ✅ (~immune) | — |

## Engine & Monte Carlo

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G5** | **MC depth = 250,000 yr/cell.** | Body (EAL, PML₁₀₀) stable at 100k; deep-tail readouts (`*_rp500`, `tvar_*_99`) need more samples and Stage 2 is embarrassingly parallel (compute is not the constraint). **Caveat:** deepest readouts inherit the **bootstrap-truncation** tail bias ([hail A23](../../../plans/hail/assumptions.md)) until severity is drawn from a *fitted distribution + EVT tail* — the same move as the storage decision (G-storage, under discussion). Flag `*_rp500`/`tvar_*_99` as provisional until then. | decided | EVT severity tail lands → re-baseline the deep tail |
| **G6** | **Loss engine (M2–M4) is identical across all hazards and cells;** only the M1 hazard field differs per hazard. | "Standard interface, not standard physics." Makes the grid one engineering investment and keeps grid ↔ point from drifting (the EAL-percentage bug was version drift). | decided | — |

## Grid & reporting

| # | Assumption | Basis / why | Status | Revisit when |
|---|---|---|---|---|
| **G7** | **Grid = the wildfire-index 0.25° benchmark grid** — serve **13,085** valued CONUS cells (of **17,543** full). | Reuse, not invent → consistency with Shruti's benchmark grid, Yuri's point↔cell validation, and the wildfire index. Native hazard data aggregated *up* to this grid (which also smooths noisy MRMS). | **locked** | — |
| **G8** | **All dollar metrics reported in both `$` and `% of TIV`;** TIV = canonical per-kW cost × 100 MW (solar ≈ \$1,483/kWp, wind ≈ \$1,666/kWp → ~\$148M / ~\$167M). | % of TIV is the house display and makes the MW choice wash out of the headline. **Caveat:** per-kWp basis is the platform's flat figure; valuation basis (TIV vs replacement vs insured) is not pinned — it scales every dollar metric linearly (cf. [hail A19](../../../plans/hail/assumptions.md)). | input (given) | confirm the valuation basis; per-cell cost variation |

## Deferred to the per-hazard registers (not assumed here)

- **The M1 hazard field** — per-cell frequency + magnitude/size distribution. This is the hazard-specific,
  data-availability-driven part (the "ready field vs build-from-raw" triage). Lives in each peril's register
  ([hail](../../../plans/hail/assumptions.md); wildfire/wind to come) and the sourcing-triage discussion
  (`03`, in progress).
- **Sparse-cell distribution fitting** — how a quiet cell with few events gets a stable frequency/severity
  fit (spatial pooling / shrinkage). Open design question surfaced under the storage discussion ([`01` §5](01_ideal_architecture_compute_and_grid.md)); will land as a `G`-row once decided.

---

*How to use this: when a layer or doc touches the grid product, check the relevant `G`-rows; when an
assumption changes, update the row (and the doc that surfaces it). The `heuristic`/`low-confidence` rows
(G3 wind area) are the ones most worth replacing with measured data.*
