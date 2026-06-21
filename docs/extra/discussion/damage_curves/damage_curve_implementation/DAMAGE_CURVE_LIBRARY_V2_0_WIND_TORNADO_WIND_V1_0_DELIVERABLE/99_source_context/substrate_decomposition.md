# Engineering substrate — how each tech decomposes into subsystems → components

**Product:** workspace / demo (dev DB · `tenant_workspace_v2`). **Not** the public platform (the public site uses the JSONB engineering blob; the legacy flat `engineering_plant`/`engineering_generator` tables were dropped in 04m.12). This is the canonical answer to *"how do we break down a solar / wind / BESS / thermal asset?"*

> **Authoritative source of the vocabulary:** the DB code-lookups `subsystem_code_lookup` (18 subsystems) + `component_code_lookup` (30 components) on the dev branch. This doc is the readable consolidation (the **map**); the lookups are the runtime truth. For the **exhaustive per-field catalog** (every component's full typed spec schema — enums, units, ranges, hazard flags — the **territory**, generated from the lookups), see [`substrate_catalog.generated.md`](substrate_catalog.generated.md). For the per-component physical narrative (what each component is, why it matters, failure modes), see the [`engineering substrate learning guide`](../../../learn/engineering_substrate/00_index.md). See also the workspace [`governance`](../governance.md), the substrate DDs (DD-045–048, DD-053–057, DD-067), and [`dimension_design_principles`](../dimension_design_principles.md).

---

## The model

A generator (or plant) decomposes into **subsystems**, each of which decomposes into **components**:

```
plant / generator
  └─ SUBSYSTEM   (e.g. PV_ARRAY)      ── scope: plant | generator
        └─ COMPONENT (e.g. PV_MODULE) ── carries the leaf specs
```

Each row carries:

| Axis | Where | Meaning |
|---|---|---|
| `applicable_tech_classes` | subsystem lookup | which techs use this subsystem (solar / wind / bess / thermal) |
| `default_parent_scope` | subsystem lookup | **plant** (shared across the plant) vs **generator** (per unit) |
| `parent_subsystem_code` | component lookup | which subsystem a component hangs under |
| `specs_schema` | component lookup | the typed leaf fields (with enums/units/ranges) the component carries |
| `requirement` · `exclusive_group` · `is_default` | subsystem + component lookup | **the grammar of a valid asset (04x)** — `requirement` (`required`/`recommended`/`optional`); `exclusive_group` marks a mutually-exclusive *one-of* (e.g. `FIXED_MOUNT` ⊕ `TRACKER` in `MOUNTING_KIND`); `is_default` is the fallback member. This is the *menu's rules* — see [`04x`](../../../design/tenant_workspace_v2/04x_component_grammar_and_structural_variants.md). |
| `data_provenance` (per cell) | substrate row | per-field `{source, as_of, …}` — honest, field-level (DD-056 + **DD-067**: source labels must be field-level true, no composite defaults) |
| `typical_capex_weight_low/high`, `damage_behavior` | subsystem lookup | **declared but currently NULL** — capex/damage allocation belongs to a future `resiliency_subsystem` dim per `dimension_design_principles` (normalize to 1.0 per asset); not populated here today |

**Editability** rides the DD-058 six-class rubric (identity / knob / historical / lifecycle / derived / rollup) per FieldSpec; identity fields (e.g. `tracking_type`, `chemistry`, `prime_mover`) are Class-1-or-2 depending on whether a within-asset what-if is meaningful (DD-065).

---

## Shared / cross-cutting subsystems (every tech uses these)

These are **plant-scope** (one set per plant, shared across its generators) unless noted:

| Subsystem | Components | What it is |
|---|---|---|
| `SUBSTATION` | `TRANSFORMER_MAIN`, `SWITCHGEAR` (+ `TRANSFORMER_AUX`) | main step-up substation: transformer + HV switchgear + protection |
| `ELECTRICAL_COLLECTION` | `CABLE_AC` (+ `CABLE_DC` for solar/bess) | collection cabling + junctions from generators to the substation |
| `SCADA` | `MONITORING_SYSTEM`, `MET_STATION` | plant-wide monitoring + control + data acquisition + met masts |
| `CIVIL_INFRA` | — | roads, fencing, site grading, perimeter security (componentless rollup) |
| `FOUNDATION` | `FOUNDATION_BASE` | concrete/pile foundation — wind towers, thermal islands, **and solar piles (04x)** |
| `FIRE_PROTECTION` ⁰ | `FIRE_DETECTION`, `FIRE_SUPPRESSION` | fire detection (smoke/thermal/**off-gas** for BESS) + suppression (agent + **deflagration panels** per NFPA 68/69) |
| `GROUNDING_LIGHTNING` ⁰ | `GROUNDING_GRID`, `LIGHTNING_PROTECTION`, `SURGE_PROTECTION` | earthing grid + LPS air terminals + SPDs — lightning is a top damage/downtime cause for solar/wind |
| `AUXILIARY_POWER` ⁰ | `UPS_SYSTEM`, `BACKUP_GENSET` | survivability/backup power (UPS + emergency genset, optionally black-start) — keeps safety systems alive in a grid-down event. Distinct from `SUBSTATION`→`TRANSFORMER_AUX` (house-load) |
| `SITE_DRAINAGE` ⁰ | `DRAINAGE_SYSTEM`, `FLOOD_DEFENSE` | stormwater capacity + flood defenses (berm / pad elevation) — the real home for flood/drainage (CIVIL_INFRA is hollow) |

⁰ = **added in 04x** (the hazard/protection half — see the **04x update** section just below). The per-tech sections below cover only the **tech-specific** subsystems.

---

## 04x update — the grammar + protection subsystems

**Shipped on dev 2026-06-02** (migration `2026_06_02_01_04x`). Two things landed together, closing the "did we miss any major subsystem?" gap on the **hazard/protection** half:

- **Grammar (Gap 1):** every subsystem + component now carries `requirement` (`required`/`recommended`/`optional`), and components carry `exclusive_group` + `is_default`. This is the *grammar of a valid asset* — what's mandatory, what's a mutually-exclusive *one-of* (the canonical `FIXED_MOUNT` ⊕ `TRACKER` = `MOUNTING_KIND`, FIXED_MOUNT default), what's optional. Distinct from the per-*field* `required` inside `specs_schema`.
- **Protection subsystems (Gap 0):** 7 new subsystems + 14 new components for the hazard half that was systematically missing — cross-cutting `FIRE_PROTECTION` · `GROUNDING_LIGHTNING` · `AUXILIARY_POWER` · `SITE_DRAINAGE`; wind `PITCH_SYSTEM` · `BRAKE_SYSTEM` · `ICE_PROTECTION`; solar `DC_PROTECTION` + `RACKING_STRUCTURE`; plus tracker **stow** specs, `FOUNDATION_BASE` **pile** specs, and `FOUNDATION` extended to solar. All **skeletons** (typed, awaiting a source or workspace-user input per DD-047/DD-076).

This is the **inventory + the rules** (the *menu*). The act of **picking / swapping / adding** one of these on a specific asset (and in a resiliency variant) is **Gap 2 (structural variant)** — still pending the [04x](../../../design/tenant_workspace_v2/04x_component_grammar_and_structural_variants.md) Q1 decision. The exhaustive per-field detail lives in the generated [`substrate_catalog.generated.md`](substrate_catalog.generated.md).

---

## ☀️ Solar PV

A field of PV modules converting sunlight → DC, aggregated through combiners + inverters into grid AC, stepped up at the substation. No prime mover, no fuel; intermittent; DC side typically oversized vs the AC inverter rating (DC/AC ratio > 1).

```
solar generator
├─ PV_ARRAY          [gen]  └─ PV_MODULE
├─ MOUNTING          [gen]  └─ FIXED_MOUNT ⊕ TRACKER  (one-of: MOUNTING_KIND) · RACKING_STRUCTURE ⁰
└─ INVERTER_SYSTEM   [gen]  └─ INVERTER · COMBINER_BOX · DC_PROTECTION ⁰
   + shared: SUBSTATION · ELECTRICAL_COLLECTION · SCADA · CIVIL_INFRA · FOUNDATION(piles ⁰)
   + protection ⁰: FIRE_PROTECTION · GROUNDING_LIGHTNING · AUXILIARY_POWER · SITE_DRAINAGE
```
*(⁰ = added in 04x.)*

| Component | Key specs | Source | Populated? |
|---|---|---|---|
| `PV_MODULE` | `cell_type`, `panel_type`, `is_bifacial`, `peak_power_w`, `glass_thickness_mm`†, `tempered_glass`† | `cell_type`/`is_bifacial` ← USPVDB v3.0 (`p_cs_si`/`p_tf_cdte`/`p_bifacial`); EIA-860 3_3 has fleet-wide flags | ✅ cell_type, bifacial · ⛔ glass/peak_power (unsourced) |
| `FIXED_MOUNT` | `tilt_deg`, `azimuth_deg` | EIA-860 3_3 cols 29–30 / USPVDB `p_tilt`/`p_az` | ✅ |
| `TRACKER` | `tracking_type` (single/dual-axis), `axis_tilt_deg`, `axis_azimuth_deg`, `tracker_pitch_m` | tracking_type ← EIA-860 3_3 cols 19–20 (single/dual-axis flags) / USPVDB `p_axis` | ✅ tracking_type/axis · ⛔ pitch |
| `INVERTER` | `topology`, `rated_capacity_kw`, `efficiency_pct` | — EIA captures no inverter detail | ⛔ skeleton |
| `COMBINER_BOX` | `input_strings`, `current_rating_a` | — below public-source resolution | ⛔ skeleton |

† `glass_thickness_mm` + `tempered_glass` are **hazard-linked** (DD-046) — the hail-fragility driver.
**Tech note — DC/AC ratio:** PV is the one tech where both AC nameplate (3_3 col 13) and DC nameplate (3_3 col 31, 99.7% filled) exist; `dc_ac_ratio` is pipeline-derivable and lives on `INVERTER_SYSTEM` as a Class-2 spec (utility PV ≈ 1.2–1.4). **Tracking vs fixed** is the biggest yield + capex driver and is the FIXED_MOUNT-vs-TRACKER fork.

---

## 💨 Wind

An EIA-860 wind "generator" is a **wind farm** aggregating 50–300+ turbines. Each turbine = rotor (blades+hub) → nacelle (drivetrain) atop a tower; specs are per-turbine, aggregated to the generator.

```
wind generator
├─ ROTOR_ASSEMBLY    [gen]  └─ BLADE · HUB
├─ NACELLE           [gen]  └─ GEARBOX · GENERATOR_INTERNAL · YAW_SYSTEM
├─ TOWER             [gen]  └─ TOWER_SECTION
├─ POWER_ELECTRONICS [gen]  └─ POWER_CONVERTER
├─ PITCH_SYSTEM ⁰    [gen]  └─ PITCH_DRIVE         (primary aero brake + storm feathering)
├─ BRAKE_SYSTEM ⁰    [gen]  └─ MECHANICAL_BRAKE    (parking + emergency overspeed)
└─ ICE_PROTECTION ⁰  [gen]  └─ ICE_MITIGATION      (cold-climate de-icing)
   + shared: FOUNDATION · SUBSTATION · ELECTRICAL_COLLECTION · SCADA · CIVIL_INFRA
   + protection ⁰: FIRE_PROTECTION · GROUNDING_LIGHTNING · AUXILIARY_POWER · SITE_DRAINAGE
```
*(⁰ = added in 04x.)*

| Component | Key specs | Source | Populated? |
|---|---|---|---|
| `BLADE` | `length_m` | USWTDB v8.1 `t_rd` (rotor diameter → blade length), per-turbine → aggregated | ✅ length (derived) |
| `HUB` | `diameter_m` | USWTDB (geometry context) | ⛔ skeleton |
| `GEARBOX` | `ratio`, `configuration` — *omitted for direct-drive turbines* | inferable from USWTDB `t_manu`/`t_model`; no specs captured | ⛔ skeleton |
| `GENERATOR_INTERNAL` | `generator_type` (induction/synchronous/PM/dfig), `rated_power_kw` | rated_power ← USWTDB `t_cap` (per-turbine kW → avg) | ✅ rated_power · ⛔ generator_type |
| `YAW_SYSTEM` | `motor_count` | — not captured | ⛔ skeleton |
| `TOWER_SECTION` | `material`, `section_count`, `total_height_m` | total_height ← USWTDB `t_hh` (hub height); EIA-860 3_2 has Hub Height (Feet) | ✅ height |
| `POWER_CONVERTER` | `rated_power_kw` | derivable from `t_cap`; no converter spec captured | ⛔ skeleton |

**Tech note — drivetrain:** direct-drive vs gearbox is the central wind nuance (`GEARBOX` is "omitted for direct-drive"; `GENERATOR_INTERNAL.generator_type` distinguishes geared DFIG/induction from direct-drive PM). Today inferable only from USWTDB manufacturer/model — a gap. **Hub height** (`t_hh`) is the best-populated wind fact.

---

## 🔋 BESS (battery storage)

Stores energy electrochemically; charges/discharges on demand (no net generation). Often co-located with solar (AC- or DC-coupled).

```
bess generator
├─ BESS_PACKS  [gen]  └─ BATTERY_MODULE
├─ BESS_PCS    [gen]  └─ PCS_UNIT
├─ BESS_BMS    [gen]  └─ BMS_CONTROLLER
   + shared: INVERTER_SYSTEM · SUBSTATION · ELECTRICAL_COLLECTION · SCADA · CIVIL_INFRA
```
*(The `BESS_` prefix disambiguates PCS/BMS — short acronyms with cross-domain conflicts — as battery-specific.)*

| Component | Key specs | Source | Populated? |
|---|---|---|---|
| `BATTERY_MODULE` | `chemistry` (lfp/nmc/nca/… / lithium_ion / flow_vanadium / sodium_ion / lead_acid) | EIA-860 3_4 col 21 Storage Technology 1 (`eia860_3_4_storage`, DD-067) — LIB→lithium_ion (~97%); **LFP-vs-NMC subtype NOT distinguished by EIA** | ✅ coarse chemistry |
| `PCS_UNIT` | `rated_power_kw`, `efficiency_pct` | — (EIA 3_4 has unit-level Max Charge/Discharge MW, not PCS detail) | ⛔ skeleton |
| `BMS_CONTROLLER` | `cell_count`, `sampling_rate` | — EIA reports no BMS attributes | ⛔ skeleton |

**Tech note — chemistry / energy / duration triad:** `chemistry` (on BATTERY_MODULE) + `duration_hours`, `energy_capacity_mwh`, `co_located_renewable`, `coupling` (on BESS_PACKS) are the populated BESS facts (from EIA-860 3_4). PCS + BMS are pure skeletons.

---

## 🔥 Thermal (gas / coal / oil / biomass / MSW)

Burns fuel → working fluid → prime mover → electricity. The richest decomposition (most EIA-860 aux schedules apply).

```
thermal generator
├─ THERMAL_GENERATION [gen]  └─ BOILER · GAS_TURBINE · STEAM_TURBINE
├─ COMBINED_CYCLE     [PLANT] └─ HRSG · DUCT_BURNERS        (shared across the CCGT block)
└─ COOLING_SYSTEM     [gen]  └─ COOLING_TOWER · COOLING_INTAKE
   + shared: SUBSTATION · ELECTRICAL_COLLECTION · SCADA · CIVIL_INFRA · FOUNDATION
```

| Component | Key specs | Source | Populated? |
|---|---|---|---|
| `BOILER` | `boiler_type` (pc/cfb/stoker/…), `firing_type`, `max_steam_flow`, efficiency points | EIA-860 6_2 Boiler Info & Design (`eia860_6_2_boiler`) | ✅ (6_2) |
| `GAS_TURBINE` | `rated_power_mw`, `configuration` (aero/frame/…), `heat_rate` | seed gated by EIA-860 3_1 `prime_mover_code`; specs declared, not yet populated | ◐ gated · specs ⛔ |
| `STEAM_TURBINE` | `rated_power_mw`, `inlet_temp_f`, `inlet_pressure_psi` | seed gated by 3_1 prime_mover; specs not yet populated | ◐ gated · specs ⛔ |
| `HRSG` | `pressure_levels`, `max_steam_flow` | `has_hrsg` ← EIA-860 6_2 HRSG=Y (`eia860_6_2_boiler`) | ✅ presence |
| `DUCT_BURNERS` | `rated_input_mmbtu_per_hr` | `has_duct_burners` ← EIA-860 3_1 / 6_2 Firing Type 'DB' | ✅ presence |
| `COOLING_TOWER` | `tower_type`, `water_consumption_gpm` | EIA-860 6_2 Cooling sheet (`cooling_type`) | ✅ (6_2) |
| `COOLING_INTAKE` | `water_source`, `intake_gpm` | EIA-860 6_2 Cooling (`cooling_water_source`) | ✅ (6_2) |

**Tech note — CCGT topology:** a combined-cycle "block" is multiple EIA generators in one thermodynamic train (combustion turbine(s) → HRSG → steam turbine). EIA encodes it across grains: gen-grain identity (`combined_cycle_role` CT/ST, `combined_cycle_unit_id` linking the train) is Class-1 immutable on `THERMAL_GENERATION`; `COMBINED_CYCLE` is **plant-scope** because the HRSG/steam side is shared across the block's gas-turbine generators.

---

## Coverage honesty (what's real vs skeleton today)

The substrate is **structurally complete** (every subsystem/component exists with a typed `specs_schema`) but **selectively populated** — by design, per DD-047 ("backend completeness + frontend curation"). What's actually sourced today:

- **Solar:** ✅ cell_type, bifacial, tilt/azimuth, tracking_type. ⛔ inverter + combiner detail (no EIA source).
- **Wind:** ✅ hub height, rotor/blade length, rated power. ⛔ drivetrain, generator_type, converter (skeletons).
- **BESS:** ✅ coarse chemistry, duration, energy, coupling. ⛔ PCS + BMS (skeletons); LFP/NMC subtype (EIA limit).
- **Thermal:** ✅ boiler, cooling, HRSG/duct-burner presence, CCGT identity. ◐ turbine specs gated-but-unpopulated.
- **All techs:** ⛔ `capex_weight` + `damage_behavior` are NULL — deferred to a future `resiliency_subsystem` dim (`dimension_design_principles`).

The skeleton components are intentional: the structure is in place so a future source (or a workspace user, per the DD-076 augmentation carve-out) can populate them without a schema change.

---

## Sources map (upstream → substrate)

| Tech | Primary upstream | Schedules / datasets |
|---|---|---|
| Solar | USPVDB v3.0 + EIA-860 | Schedule 3_3 (Solar) |
| Wind | USWTDB v8.1 + EIA-860 | Schedule 3_2 (Wind) |
| BESS | EIA-860 | Schedule 3_4 (Energy Storage) |
| Thermal | EIA-860 | Schedules 3_1 (Generator), 3_5 (Multifuel), 6_1/6_2 (Boiler + Cooling) |

Per-field source labels are **field-level honest** (DD-067) — e.g. an array-area field is labelled `uspvdb_v3.0`, not a composite `uspvdb+eia860` default. The raw-source schemas are archived under [`docs/data/raw_sources/`](../../../data/raw_sources/).

---

## See also
- [`subsystem_code_lookup` / `component_code_lookup`] — the runtime vocabulary (dev DB)
- [workspace `governance`](../governance.md) · [`schema`](../schema.md) · [`architecture`](../architecture.md) · [`decisions`](../decisions.md) (DD log)
- [`dimension_design_principles`](../dimension_design_principles.md) · [`engineering_data_sources_map`](engineering_data_sources_map.md) · [`substrate_field_decomposition`](substrate_field_decomposition.md) *(the workspace canon — governance/architecture/schema/decisions + these references — relocates into `reference/workspace/` as a tracked follow-up; see [`design/docs_folder_cleanup.md`](../../../design/docs_folder_cleanup.md))*
- [`docs/data/raw_sources/`](../../../data/raw_sources/) — the upstream schema archive
