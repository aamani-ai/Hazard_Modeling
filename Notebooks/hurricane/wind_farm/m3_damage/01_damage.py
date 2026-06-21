# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Hazard (hazard 3.11)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Hurricane · Wind-farm — M3 damage: 3-s gust → per-storm, per-subsystem turbine wind loss
#
# **Magnitude metric:** the **3-second peak gust (mph)** per node (from M2), the damage curve's x-axis. Site: Amazon
# Wind US East (NC).
# **Data source:** the M2 per-node coupling (`data/hurricane/tc_windfarm_m2_coupling.parquet`, per-(storm, node) 3-s
# gust), the M0 TIV record (`flood_wind_m0_sites.json`, Amazon $291M / 104 × 2 MW + collector), and the
# convective_wind × wind_farm turbine fragility (`data/convective_wind/wind_m3_damage_manifest.json`) — the 7-subsystem
# capex split + the strong-wind logistic fragility map reused as the straight-line analogue of hurricane sustained
# wind; vendored to `data/hurricane/damage_curves/`.
# **What this notebook does:** maps each node's 3-s gust → a per-subsystem damage ratio, then aggregates over the farm
# to a **per-storm, per-subsystem** wind DR + asset-level conditional loss, each row stamped `event_family_id`. This
# per-storm × per-subsystem shape is exactly what the flood-coastal × wind M4 compound combine joins to the surge leg,
# taking `max(wind_DRᵢ, surge_DRᵢ)` per subsystem ([JD-FL-12](../../../../docs/plans/flood/decisions.md)); it is
# subsystem-resolved because a wind farm's surge and wind hit different subsystems. M3 is source-agnostic — a gust
# reaches it as just a number, and the curve is the turbine's, not the peril's. Hurricane sustained wind is a
# feathered-survival overload (the turbine pitches edge-on and survives to its IEC speed), so it reaches only the
# **aero** subsystems (rotor / nacelle / electrical / substation), onset at IEC survival (~60 m/s); tower / foundation
# / civil are not defeated by straight-line loading (only tornado rotation does that), so the asset DR **caps at the
# aero capex share (~0.65)** — no tower-collapse total-loss mode (AWN-26, low confidence: the dominant uncertainty).
#
# > Prior: [M2 coupling](../m2_coupling/01_coupling.ipynb) · curve source: [convective_wind × wind_farm
# > M3](../../../convective_wind/wind_farm/m3_damage/01_damage.ipynb). Next: [M4](../m4_loss_metrics/01_loss_metrics.ipynb).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"
FLOOD = ROOT / "data" / "flood"
CURVE_DIR = DATA / "damage_curves"; CURVE_DIR.mkdir(parents=True, exist_ok=True)
MS = 0.44704                                          # mph → m/s (the convective curve's units)
AMAZON_SLUG = "amazon_wind_us_east"
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **M2 per-node coupling** (`data/hurricane/tc_windfarm_m2_coupling.parquet`) — per-(storm, node) 3-s gust (mph).
# - **TIV** (`data/flood/flood_wind_m0_sites.json`, Amazon entry — $291M, 104 × 2 MW + collector; AFL-W3 estimate).
# - **Turbine fragility** — reused verbatim from convective_wind × wind_farm M3
#   (`data/convective_wind/wind_m3_damage_manifest.json`): capex split + the **strong-wind** fragility map (the
#   straight-line analogue of hurricane sustained wind). **Reproducibility:** per-storm loss →
#   `data/hurricane/tc_windfarm_m3_damage.parquet` (+ vendored curve + manifest).

# %% [markdown]
# ## Assumptions (this layer)
#
# **AWN-24 (reused)** turbine = capex-weighted subsystem logistic on 3-s gust · **AWN-9** onset anchored at IEC
# survival (~60 m/s, class II Ve50≈59.5) · **AWN-32 (strong-wind branch)** hurricane sustained wind = feathered-
# survival overload → **aero reach only** (rotor/nacelle/electrical/substation; DR caps ≈ aero capex 0.65); tower/
# foundation/civil not reached by straight-line loading · **AWN-26** Low confidence (approximate; the dominant
# uncertainty) · **ATC-2** physical loss only. Register: [hurricane assumptions](../../../../docs/plans/hurricane/assumptions.md)
# · [convective_wind DD-WN-16](../../../../docs/plans/convective_wind/decisions.md).

# %% [markdown]
# ## 1 · The turbine wind curve — reused from convective_wind (capex split + strong-wind fragility)
#
# One turbine, the **strong-wind** (straight-line) fragility map — *"M3 is source-agnostic; the curve is the
# turbine's, not the peril's."* The collector **substation** is its own node (0.09 of farm value), sampled at its own
# gust; the per-turbine aero subsystems (rotor/nacelle/electrical) are averaged over the 104 turbines. Tower (0.16),
# foundation (0.12) and civil (0.07) are **not reached** by straight-line/hurricane wind → DR 0 (only tornado defeats
# them) → the asset DR caps at the **aero capex share (0.65)**.

# %%
# capex split (old-repo wind_config / convective_wind) — the 7-subsystem turbine object
CAPEX = {"rotor_blades": 0.26, "nacelle_drivetrain": 0.21, "tower": 0.16, "foundation": 0.12,
         "substation": 0.09, "electrical": 0.09, "civil": 0.07}
assert abs(sum(CAPEX.values()) - 1.0) < 1e-9
# strong-wind fragility {subsystem: (x0 [m/s], k)} — REUSED from convective_wind M3 (the straight-line analogue).
# Hurricane wind reaches only these AERO subsystems (feathered-survival overload, onset at IEC survival).
FRAG = {"rotor_blades": (60, 0.30), "nacelle_drivetrain": (66, 0.28),
        "substation": (62, 0.28), "electrical": (64, 0.28)}
AERO = list(FRAG)                                              # reachable by straight-line / hurricane wind
PER_TURBINE_AERO = ["rotor_blades", "nacelle_drivetrain", "electrical"]   # averaged over turbines
NOT_REACHED = ["tower", "foundation", "civil"]                 # not defeated by straight-line loading → DR 0
SUBSYSTEMS = list(CAPEX)


def frag_dr(gust_mph, subsystem):
    """Per-subsystem DR at 3-s gust (mph) — convective_wind strong-wind logistic (DR(0)≈0 naturally)."""
    x0, k = FRAG[subsystem]
    return 1.0 / (1.0 + np.exp(-k * (np.asarray(gust_mph, float) * MS - x0)))


print(f"aero reach (straight-line/hurricane): {AERO}  →  capex cap = {sum(CAPEX[s] for s in AERO):.2f}")
print(f"not reached (tower/foundation/civil): {NOT_REACHED}  →  DR 0 (only tornado defeats them)")
print(f"{'gust_mph':>9} " + " ".join(f"{s.split('_')[0]:>8}" for s in AERO) + f"{'assetDR':>9}")
for mph in [90, 110, 130, 150, 175, 200, 250]:
    drs = {s: float(frag_dr(mph, s)) for s in AERO}
    asset = sum(CAPEX[s] * drs[s] for s in AERO)
    print(f"{mph:>9} " + " ".join(f"{drs[s]:>8.3f}" for s in AERO) + f"{asset:>9.3f}")

# %% [markdown]
# ## 2 · Apply per node → aggregate to per-storm, per-subsystem farm DR
#
# Per storm: the **aero per-turbine** subsystems take the **mean over the 104 turbines** of their per-node DR (convex
# curve → average of DRs, not DR of the average gust); the **substation** takes its own node's DR; **tower/foundation/
# civil = 0**. `asset_DR = Σₛ capexₛ · DRₛ`. Each row is stamped `event_family_id` (the join key).

# %%
m2 = pd.read_parquet(DATA / "tc_windfarm_m2_coupling.parquet")
site = next(s for s in json.loads((FLOOD / "flood_wind_m0_sites.json").read_text())["sites"]
            if s["slug"] == AMAZON_SLUG)
TIV = site["tiv"]

turb = m2[m2.node_type == "turbine"]
subn = m2[m2.node_type == "substation"].set_index("storm_ID")
meta = m2[["storm_ID", "event_family_id", "category", "site", "slug"]].drop_duplicates("storm_ID").set_index("storm_ID")

rows = []
for sid, g in turb.groupby("storm_ID"):
    dr = {s: float(np.mean(frag_dr(g.gust_3s_mph.values, s))) for s in PER_TURBINE_AERO}   # mean over turbines
    dr["substation"] = float(frag_dr(subn.loc[sid, "gust_3s_mph"], "substation"))
    for s in NOT_REACHED:
        dr[s] = 0.0
    asset_dr = sum(CAPEX[s] * dr[s] for s in SUBSYSTEMS)
    m = meta.loc[sid]
    rows.append({"site": m.site, "slug": m.slug, "storm_ID": int(sid),
                 "event_family_id": int(m.event_family_id), "category": int(m.category),
                 "n_turbines": int(len(g)), "max_gust_3s_mph": float(g.gust_3s_mph.max()),
                 **{f"DR_{s}": round(dr[s], 6) for s in SUBSYSTEMS},
                 "conditional_DR": round(asset_dr, 6), "tiv_usd": TIV,
                 "conditional_loss_usd": round(asset_dr * TIV)})
m3 = pd.DataFrame(rows).sort_values("conditional_DR", ascending=False).reset_index(drop=True)
print(f"per-storm rows: {len(m3)} (one per shared storm, event_family_id-stamped)")
print(m3[["storm_ID", "event_family_id", "category", "max_gust_3s_mph", "DR_rotor_blades",
          "DR_substation", "conditional_DR", "conditional_loss_usd"]].head(6).to_string(index=False))
print(f"\nworst storm: Cat{int(m3.category.iloc[0])}, asset DR {m3.conditional_DR.iloc[0]*100:.2f}% of TIV "
      f"(${m3.conditional_loss_usd.iloc[0]/1e6:.2f}M); median DR {m3.conditional_DR.median()*100:.3f}%")
print("→ Bimodal: the BULK is tiny (median ~0.3%) — Amazon's frequent storms gust well below IEC turbine survival")
print("  (~133 mph) so turbines ride them out — but the rare Cat-3 close passage (~132 mph) hits the STEEP onset of")
print("  the aero curve → ~11% of TIV (the substation + rotor take it). A real but rare tail; no total loss (cap 0.65).")

# %% [markdown]
# ## 3 · Known-answer checks (basics-spot-on)

# %%
g_grid = np.arange(60, 260, 5)
asset_grid = np.array([sum(CAPEX[s] * float(frag_dr(g, s)) for s in AERO) for g in g_grid])
checks = {
    "one row per shared storm, all event_family_id preserved":
        len(m3) == m2.storm_ID.nunique() and set(m3.event_family_id) == set(m2.event_family_id),
    "per-subsystem DR columns present for all 7 subsystems": all(f"DR_{s}" in m3 for s in SUBSYSTEMS),
    "tower/foundation/civil DR == 0 (not reached by straight-line wind)":
        bool((m3[[f"DR_{s}" for s in NOT_REACHED]].abs().to_numpy() < 1e-12).all()),
    "asset DR == capex-weighted subsystem sum (identity)":
        bool(np.allclose(m3.conditional_DR, sum(CAPEX[s] * m3[f"DR_{s}"] for s in SUBSYSTEMS), atol=1e-6)),
    "asset DR monotonic in gust": bool(np.all(np.diff(asset_grid) >= -1e-9)),
    "asset DR caps at the aero capex share (~0.65) — no tower/foundation collapse mode":
        0.60 <= sum(CAPEX[s] * float(frag_dr(400, s)) for s in AERO) <= 0.66,
    "bulk DR tiny (median < 1% — frequent storms below IEC survival), tail bounded (worst < 20% of TIV)":
        (m3.conditional_DR.median() < 0.01) and (m3.conditional_DR.max() < 0.20),
    "all DR ∈ [0,1]": bool(((m3[[f"DR_{s}" for s in SUBSYSTEMS]] >= 0).all().all()) and (m3.conditional_DR.max() <= 1.0)),
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "an M3 check failed"
print("\nall M3/01 known-answer checks pass ✅")

# %% [markdown]
# ## 4 · Emit — per-storm per-subsystem loss (the compound-combine input) + the vendored curve

# %%
out = DATA / "tc_windfarm_m3_damage.parquet"
m3.to_parquet(out, index=False)
vendored = {
    "curve_id": "hurricane/wind_farm__turbine__capex_weighted",
    "STATUS": "REUSED from convective_wind × wind_farm M3 (turbine wind curve) — Low confidence, greenfield (AWN-26)",
    "hazard_type": "HURRICANE", "asset_type": "wind_farm",
    "intensity_metric": "wind_speed_mph", "intensity_measure": "3-second peak gust", "intensity_unit": "mph",
    "logistic_form": "DR_s(v) = 1/(1+exp(-k_s*(v_ms - x0_s)))  per subsystem; asset DR = Σ_s capex_s·DR_s",
    "branch": "strong-wind (straight-line) fragility — hurricane sustained wind ≈ feathered-survival overload (AWN-32)",
    "capex_weights": CAPEX,
    "aero_reach": AERO, "aero_capex_cap": round(sum(CAPEX[s] for s in AERO), 3),
    "not_reached": NOT_REACHED,
    "fragility_strong_wind_ms": {s: {"x0_ms": x0, "k": k} for s, (x0, k) in FRAG.items()},
    "LIMITATION_dr_cap": ("asset DR caps ~0.65 (aero capex share) — tower/foundation/civil treated not-reached by "
                          "straight-line loading, so catastrophic TOWER-COLLAPSE total loss is NOT represented "
                          "(the wind-farm analogue of hurricane×solar's DR cap). Revisit with a hurricane-specific "
                          "turbine curve (tower failure at Cat-4/5) from infrasure-damage-curves."),
    "source": "data/convective_wind/wind_m3_damage_manifest.json (strong_wind fragility + capex)",
}
(CURVE_DIR / "hurricane_windfarm_asset_capex_weighted.json").write_text(json.dumps(vendored, indent=2))
manifest = {
    "notebook": "hurricane/wind_farm/m3_damage/01_damage",
    "site": "Amazon Wind US East (NC)", "slug": AMAZON_SLUG, "asset": "wind_farm",
    "curve_status": "REUSED convective_wind turbine wind curve (strong-wind branch); Low confidence (AWN-26)",
    "deliverable": ("per-storm, per-subsystem wind DR stamped event_family_id — the EXACT input flood-coastal × wind "
                    "M4 joins to the surge leg (JD-FL-12, max(wind_DRᵢ, surge_DRᵢ) per subsystem)"),
    "subsystems": SUBSYSTEMS, "aero_reach": AERO, "not_reached": NOT_REACHED,
    "n_storms": int(len(m3)), "tiv_usd": TIV,
    "worst_storm": {"storm_ID": int(m3.storm_ID.iloc[0]), "category": int(m3.category.iloc[0]),
                    "conditional_DR": float(m3.conditional_DR.iloc[0]),
                    "max_gust_3s_mph": float(m3.max_gust_3s_mph.iloc[0])},
    "finding": ("bimodal — bulk DR tiny (median ~0.3%, storms below IEC survival), but the rare Cat-3 close passage "
                "(~132 mph) hits the steep aero onset → ~11% of TIV. A real-but-rare wind tail; no total loss (cap 0.65)."),
    "outputs": {"damage_parquet": str(out.relative_to(ROOT)),
                "vendored_curve": str((CURVE_DIR / "hurricane_windfarm_asset_capex_weighted.json").relative_to(ROOT))},
}
(DATA / "tc_windfarm_m3_manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"wrote {out}\nwrote vendored curve + manifest")

# %% [markdown]
# ## Takeaways → next
#
# - **Deliverable met** — per-storm, **per-subsystem** wind DR at Amazon Wind US East, stamped `event_family_id`: the
#   exact shape the flood-coastal × wind M4 compound combine joins to the surge leg (`max(wind_DRᵢ, surge_DRᵢ)` per
#   subsystem, JD-FL-12). Shared subsystems with surge = electrical + substation; wind-only = rotor + nacelle.
# - **Curve reused, source-agnostic** — convective_wind's turbine wind curve (strong-wind branch); hurricane sustained
#   wind ≈ straight-line overload → aero reach, asset DR caps ~0.65 (no tower-collapse mode — the honest limitation).
# - **Bimodal DR** — the bulk is tiny (median ~0.3%; Amazon's frequent storms gust below IEC turbine survival, so
#   turbines ride them out, cf. convective strong-wind≈0), but the rare **Cat-3 close passage (~132 mph) hits the
#   steep aero onset → ~11% of TIV**. A real-but-rare wind tail (no total loss — cap 0.65). The compound combine still
#   leans surge-heavy at the low-end, with wind contributing the rare Cat-3 spike.
#
# **Next → M4 (loss & metrics):** compound-Poisson MC at the shared λ → **wind-only** EAL / PML / VaR (% of TIV); then
# (separately) flood-coastal × wind M4 reads this per-storm per-subsystem table to run the surge × wind combine.
