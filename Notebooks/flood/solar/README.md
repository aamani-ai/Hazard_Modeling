# Flood × Solar — the asset cell (M2 → M3 → M4)

The **(peril × asset)** cell for the flood peril on a **solar farm** — built end-to-end, and the flood analogue of
[`wildfire/solar/`](../../wildfire/solar/m4_loss_metrics/README.md) (same site-conditioned coupling). See the
[**flood peril overview**](../README.md) for the sub-peril framing + the shared catalog. It **inherits the shared
flood catalog** (peril-level, asset-independent): [`../layer0/`](../layer0/) (definition) +
[`../m0_input_data/`](../m0_input_data/) (M0: NFHL screen + BLE depth + 3DEP DEM + NOAA CFEM coastal) +
[`../m1_catalog/`](../m1_catalog/) (M1: per-sub-peril field — riverine depth, pluvial runoff, coastal surge catalog).
*This* folder is where **coupling, damage, and loss specialize to a solar farm** — one unified notebook per layer,
covering all three sub-perils.

> **Why an asset cell?** The catalog (what the flood does at a site) is asset-independent; the **coupling, fragility,
> and loss** are asset-specific. A solar farm and a wind farm under the *same* flood catalog couple and break
> differently (solar = dense areal polygon → areal inundated fraction; wind = sparse point-cloud → per-node depth). So
> M2–M4 live under the asset — `solar/` here, [`wind_farm/`](../wind_farm/README.md) as the sibling — without touching
> the shared catalog (P1 — *hazard × asset specificity*).

**Assets (four solar farms, all three sub-perils):**
- **Hayhurst Texas Solar, TX** — Chihuahuan desert · **dry baseline** (riverine + pluvial both ≈ 0; cross-peril control).
- **Elizabeth Solar Plant, LA** (~143 MW) — Lower-Mississippi plain · **riverine + pluvial** (inland-only).
- **Discovery Solar Center, FL** (~75 MW) — Cape Canaveral coast · **coastal** (surge + hurricane-wind compound).
- **LA3 West Baton Rouge, LA** — West Baton Rouge Parish · **all three sub-perils**, the site where
  `max(riverine,pluvial) + coastal` actually combines into one total-flood EAL.

## The fork — where, and why
Flood is **one peril, a sub-peril family** ([JD-FL-1](../../../docs/plans/flood/decisions.md)). It forks the **catalog**
at M1 (the data differs); the asset cell is then **unified across sub-perils** — one M2, one M3, one M4 notebook each:

| Layer | Forked? | Why |
|---|---|---|
| **M1 catalog** (peril) | **folder-fork** → [`riverine/`](../m1_catalog/riverine/) · [`pluvial/`](../m1_catalog/pluvial/) · [`coastal/`](../m1_catalog/coastal/) | the sub-perils differ at the **data + magnitude basis** (BLE depth vs Atlas-14 runoff vs SLOSH-MOM surge) |
| M2 coupling | **unified** (one notebook, three sub-perils) | site-conditioned for every sub-peril — sample the depth field at the footprint |
| M3 damage | **unified curve** | one source-agnostic depth-damage curve on the shared depth driver, applied to all three |
| **M4 loss** | **two event-frames, then summed** | riverine + pluvial co-sampled annual-max (worse-source-wins, JD-FL-11); coastal compound-Poisson surge+wind per storm (JD-FL-12); **total flood = inland + coastal** |

## The layers
- **M2 — coupling** · [📖 folder README](m2_coupling/README.md) — **site-conditioned (bucket 3)**, samples each
  sub-peril field at the solar footprint: **riverine** areal inundated fraction × conditional depth off the full-res
  BLE field (lower RPs densified from M1 `Q(T)`, JD-FL-8); **pluvial** runoff poured over the footprint's 1 m-lidar
  closed depressions (ponding `f` + depth cap); **coastal** areal SLOSH-MOM surge per hurricane category per storm
  (footprint-mean depth + inundated fraction), `event_family_id`-stamped.
- **M3 — damage** · [📖 folder README](m3_damage/README.md) — one **source-agnostic** capex-weighted **flood × solar**
  depth-damage curve from `infrasure-damage-curves` (RIVERINE_FLOOD × solar, anchored `DR(0)=0`), applied to all three
  sub-perils — inundation is inundation, the source has no memory. Per-subsystem logistic `DR`; `x0` bakes in component
  elevation (inverter drowns @ 0.75 ft; mounting/SCADA flood-immune). `conditional_loss = exposure × Asset_DR(depth) ×
  TIV`.
- **M4 — loss & metrics** · [📖 folder README](m4_loss_metrics/README.md) — **inland**: annual-maximum MC, riverine +
  pluvial co-sampled comonotonic + worse-source-wins (JD-FL-11). **Coastal**: compound-Poisson event stream at
  λ_surge, surge + hurricane-wind combined **per subsystem** (`max(wind_DR, surge_DR)` on shared subsystems, joined on
  `event_family_id`). **Total flood = inland + coastal** (independent streams summed). Every metric off the **sampled**
  distribution, **% of TIV alongside $**.

## Headline numbers (real, record-limited; total flood = inland + coastal)
| | Sub-perils | Inland EAL | Coastal EAL | **Total EAL** | PML100 | PML500 |
|---|---|---|---|---|---|---|
| **LA3 West Baton Rouge** (all-three) | R + F + C | 0.653% | 0.107% | **0.761%** | 7.00% | 12.24% |
| **Discovery Solar Center** (coastal) | C | 0.000% | 0.338% | **0.338%** | 9.35% | 38.72% |
| **Elizabeth Solar Plant** (inland) | R + F | 0.163% | 0.000% | **0.163%** | 2.60% | 4.26% |
| **Hayhurst Texas Solar** (dry) | R + F | 0.030% | 0.000% | **0.030%** | 0.28% | 0.61% |

- **Inland marginals** (% TIV EAL): the **riverine** leg dominates — LA3 riverine 0.653 vs pluvial 0.026; Elizabeth
  riverine 0.163 vs pluvial 0.003; Hayhurst riverine 0.030 vs pluvial 0.004. Pluvial is small once ponding is grounded
  in 1 m lidar (closed-depression `f`, JD-FL-15) rather than a flat guess.
- **Coastal compound marginals** (% TIV EAL, per-subsystem max): LA3 wind-only 0.093 + surge-only 0.020 → compound
  0.107; Discovery wind-only 0.251 + surge-only 0.140 → compound 0.338. The combine is **material on both legs**
  (compound > wind-only *and* > surge-only).
- **LA3 is the headline all-three site** — `max(riverine,pluvial)` annual-max (0.653) + coastal surge×wind compound
  (0.107) sum to total **0.761%** of TIV. The single-peril sites (Elizabeth inland-only, Discovery coastal-only) remain
  as references; their absent sub-perils enter the M4 engine as 0.
- **Validation:** the Elizabeth riverine RP depths (10–500-yr, ~1.0–1.75 ft) fall **inside** the USGS STN high-water
  marks from the Aug-2016 LA flood (21 marks, 0.0–7.9 ft, median 2.1 ft). **Screening-grade caveats** persist on the
  pluvial blind spot (no depth anchor, AFL-P2) and the coastal SLOSH-MOM worst-case envelope.

## Deferred (asset-specific)
Calibrated / claims-calibrated curves from `infrasure-damage-curves` · the **PV flood-stow** mitigation lever (x0 7 ft)
· **duration / business-interruption** (Gen-2, physical loss only today) · regression-Q standard error as an MC overlay
· live **StreamStats + HAND** depth where BLE is absent. Plan-of-record:
[`docs/plans/flood/`](../../../docs/plans/flood/README.md).

## Asset-Cell Method In Plain English

This folder starts where the shared flood catalog ends. M0/M1 say what flood field exists at each site; the solar asset
cell says how a solar plant experiences that field.

```text
shared flood catalog
  R: return period -> riverine depth field
  F: return period -> pluvial runoff source
  C: storm -> coastal surge field
        |
        v
solar M2
  polygon mask -> exposure_fraction + conditional_depth
        |
        v
solar M3
  depth -> capex-weighted solar damage ratio
        |
        v
solar M4
  annual sampling -> EAL / PML / VaR / TVaR
```

The solar-specific assumption is that the plant is a dense areal footprint. So M2 treats the footprint as an area whose
value is spread over the polygon:

```text
solar plant polygon

+----------------------------------+
| dry cells                         |
|        +-------------+           |
|        | wet cells   |           |
|        | depth > 0   |           |
|        +-------------+           |
|                                  |
+----------------------------------+

exposure_fraction = wet cells inside polygon / all cells inside polygon
conditional_depth = average depth of wet cells only
```

The key V1 assumption is the **representative value mix** assumption:

```text
wet area fraction ~= wet value fraction

If 17.7% of the footprint is wet, M3 treats that as:
  17.7% of inverter-system value exposed
  17.7% of substation/electrical value exposed
  17.7% of PV-array/civil value exposed
```

This does not mean we know exactly where every inverter, transformer, substation, cable, and module row sits. It means
the wet part of the footprint is assumed to carry the same component/value mix as the whole plant. This is the solar
contrast to wind, where turbines and the collector substation are explicit nodes.

That split is important. The model does not average water depth over the whole plant and then damage the whole plant.
It damages the exposed share using the depth conditional on being wet:

```text
conditional_loss = exposure_fraction * Asset_DR(conditional_depth) * TIV
```

Bias direction:

```text
if inverters/substation are concentrated in the wet low area:
  V1 may understate loss

if inverters/substation are on raised or dry pads:
  V1 may overstate loss
```

This is also why flood x solar and flood x wind cannot share M2. The same river depth field can hit a solar polygon as
a partial area and a wind farm as a sparse set of turbine/substation nodes.

## What The Solar Asset Cell Asks

```text
solar M2 asks:
  inside the plant polygon:
    which pixels are wet?
    how many are wet?
    what is the average depth of the wet pixels?
    what is the max depth?

solar M3 asks:
  for the wet share:
    what solar components does that depth reach?
    what capex-weighted damage ratio applies?
    what conditional loss does that imply?

solar M4 asks:
  across simulated years:
    what is the inland annual-max loss?
    what coastal storm losses occur?
    what total annual loss distribution results?
```
