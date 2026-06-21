# Hurricane pipeline — assumptions register

Every input, method, and simplification the hurricane build rests on, by layer — so each is visible, challengeable,
and revisable. Prefix `ATC-*`. Grows as we plan and build. (Mirrors [flood AFL-*](../flood/assumptions.md) /
[wind AWN-*](../convective_wind/assumptions.md).)

> **Status: route-zero seed (planning).** Rows below are *proposed* — to be confirmed/realized as M0→M4 are built.

| ID | Layer | Assumption | Source / decision | Status | Revisit trigger |
|---|---|---|---|---|---|
| ATC-1 | scope | V1 = **hurricane wind only**; surge & rain are **flood's** `[C]`/`[F]`, not modeled here | [JD-TC-4](decisions.md); Hazard Data Ref §1/§8 | proposed | flood coastal built → switch link on |
| ATC-2 | scope | **Physical structural loss only** — business interruption excluded | [JD-TC-4](decisions.md); team hazard-tier scope | proposed | BI tier opens |
| ATC-3 | scope | **Wind *resource* (generation/revenue) out of scope** — Performance tier (`model-gpr`) | [DD-WN-2](../convective_wind/decisions.md) | proposed | n/a (hard boundary) |
| ATC-4 | layer-0 | **Magnitude observable = 3-s peak gust at 33 ft, Exposure C** (shared 3-s-gust curve with convective wind) | [00_hazard_definition](00_hazard_definition.md); [DD-WN-9](../convective_wind/decisions.md) | proposed | a hub-height/terrain-resolved curve is sourced |
| ATC-5 | M1 | **Catalog = storm-resolved RAFT tracks** (N. Atlantic; tracks+intensity+rainfall), CC-BY-4.0, **Zenodo `10.5281/zenodo.10392723`** (`RAFT.NA.v20231016.nc`, 154 MB) — ✅ probed live 2026-06-19 | [JD-TC-3](decisions.md); Hazard Data Ref §4 | **reachable** | per-event surge product / non-Atlantic site |
| ATC-6 | M1 | **Footprint = Holland (1980) field** swept along-track with asymmetry; **Holland B, RMW** parameterized | [JD-TC-7](decisions.md); Hazard Data Ref §5/§6 | proposed | higher-fidelity open field model / RAFT ships a gust field |
| ATC-7 | M1 | **Sustained → 3-s gust** via a **gust factor (≈1.1–1.3)** — value to fix & sensitivity-test | [00_hazard_definition](00_hazard_definition.md) | proposed | site/terrain-specific gust factor sourced |
| ATC-8 | M0/M1 | **Wind-unit guard.** ⚠️ **Corrected at build (M0/01):** RAFT `vmax` is **knots → mph ×1.150779** (NOT m/s ×2.237 — the Hazard-Data-Ref's generic STORM note); STORM RP grid *is* m/s ×2.237. RAFT `rmax` = nmi → km ×1.852 | Hazard Data Ref §7; M0/01 build | **built** | n/a (guard) |
| ATC-9 | M1 | **Frequency = RAFT synthetic landfalling-storm rate** near the site; validated vs IBTrACS/HURDAT2 | [JD-TC-3](decisions.md)/[JD-TC-7](decisions.md) | proposed | longer/observed record reweighting |
| ATC-10 | M1 | **Validation = IBTrACS/HURDAT2 landfall winds** (Holland replay) + **STORM RP grid cross-check** (empirical-Weibull runs low past ~100-yr) | [JD-TC-7](decisions.md); Hazard Data Ref §7 | proposed | EVD-fit convention adopted for the tail |
| ATC-11 | M1 | **`event_family_id` reserved** in the catalog schema (unused in V1) — the surge/rain cross-link hook | [JD-TC-4](decisions.md); [JD-FL-4](../flood/decisions.md) | proposed | flood coastal/pluvial-TC added → confirm field sufficient |
| ATC-12 | M2 | **Field-intensity coupling, spatially degenerate on solar** (≈ centroid sample at storm scale) — labeled as such | [JD-TC-2](decisions.md) | proposed | wind-farm V2 cell → per-point field-intensity |
| ATC-13 | M2 | **Asset = solar PV, dense areal polygon** (V1); wind farm (point cloud) = V2 | [JD-TC-1](decisions.md) | proposed | V2 build |
| ATC-14 | M3 | **Damage = `infrasure-damage-curves` HURRICANE × SOLAR** (3-s-gust mph; from `jdocs/master_curve_index.json`), capex-weighted (modules 0.35 + mounting 0.15 + substation 0.08; inverter/electrical/civil 0.42 ≈ wind-immune). **🟡 PROVISIONAL — owner-flagged for replacement.** Headline PV curve = **`tracker_stow` (x0 148, assumes tracker stows)**; **stow-failure `midtilt` (x0 115) = sensitivity band**. **Limitation:** asset DR **caps ~48%** (no solar electrical wind curve → total-loss not represented) | infrasure-damage-curves; M3 build | **built (provisional)** | replacement curve set; debris-driven remainder vulnerability; per-site tracker-state + claims calibration |
| ATC-15 | M4 | **Event model = storm-resolved MC** sampling the RAFT catalog → EAL/VaR/PML/TVaR, **% of TIV + $**, shared engine | [JD-TC-3](decisions.md); shared M4 frame | proposed | settled at M4 build |
| ATC-16 | M0 | **Sites = screened Gulf/Atlantic-coast solar (high) + Hayhurst (low, reused)**; TIV from $/MW, coastal estimated by capacity | [JD-TC-5](decisions.md) | proposed | screen top asset lacks geometry/exposure |
| ATC-17 | M0 | **Input data self-serve public** (RAFT NetCDF, IBTrACS, HURDAT2, STORM GeoTIFF, SLOSH) — no private feed | [00_intent](00_intent.md); Hazard Data Ref | proposed | a needed product turns out gated |
| ATC-18 | M1 | **Climate non-stationarity** carried as an explicit overlay (STORM CC set / CMIP6 factor), **not embedded** in V1 | Hazard Data Ref §7 | proposed | a forward-looking (2040+) horizon drives a decision |
| ATC-19 | cross-peril | **Pluvial becomes Atlas-14 + RAFT hybrid** (recorded, built flood-side later) — RAFT enters the system once | [JD-TC-6](decisions.md) | recorded | compound flooding scheduled |
