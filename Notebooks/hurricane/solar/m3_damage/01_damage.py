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
# # Hurricane · Solar — M3 damage: 3-second gust → capex-weighted solar damage ratio + conditional loss
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Cell:** × Solar PV · **Layer:** M3 (damage)
#
# **Magnitude metric:** the **3-second peak gust (mph)** — the damage curve's x-axis, on the exact basis of the
# library curves (no unit mismatch). *(Surge/rain = flood's `[C]`/`[F]`, cross-linked, not modeled here.)*
#
# **Data source:** the `infrasure-damage-curves` **HURRICANE × SOLAR** group (vendored from
# `the infrasure-damage-curves library`; empirically anchored to FPL Hurricane Ian data, Ceferino et al. 2023), the M2
# coupled events (`tc_m2_coupling.parquet`), and per-site TIV (`tc_m0_sites.json`).
#
# **What this notebook does:** maps each event's 3-s peak gust to a **capex-weighted asset damage ratio** and then a
# conditional dollar loss. It blends per-subsystem logistics `DR(x) = L/(1+exp(-k(x−x0)))`, each anchored so
# `DR(0)=0`, over capex weights (PV array 0.35 + mounting 0.15 + substation 0.08; the remaining 0.42 — inverters,
# cables, civil — is wind-low-vulnerability at DR≈0 but still counts in the denominator). It applies the curves to the
# M2 events, reports per-site gust/DR/loss, runs known-answer checks (DR anchored ~0 at low gust, monotonic, bounded
# at the wind-exposed capex share ~48%), and emits per-event loss (`tc_m3_damage.parquet`) plus the vendored curve and
# manifest.
#
# > **🟡 PROVISIONAL CURVES (ATC-14).** These library curves are **medium-confidence placeholders to be replaced by a
# > better set later** ([ATC-14](../../../../docs/plans/hurricane/assumptions.md)). The headline uses
# > **`pv_array_tracker_stow`** (x0 148 mph — assumes the single-axis tracker successfully stows in high wind, the
# > modern-FL-utility design + FPL-Ian-anchored case); the **stow-failure** case (`pv_array_tracker_midtilt`, x0 115)
# > is recorded as the sensitivity/worst band. The damage curve is the **dominant, irreducible uncertainty** of the
# > whole build.
# >
# > Plan: [`m3_damage.md`](../../../../docs/plans/hurricane/m3_damage.md) · prior: [M2](../m2_coupling/01_coupling.ipynb).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"
CURVE_DIR = DATA / "damage_curves"; CURVE_DIR.mkdir(parents=True, exist_ok=True)
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **Damage curves** — `infrasure-damage-curves` **HURRICANE × SOLAR** group, vendored from
#   `the infrasure-damage-curves library` → cached to `data/hurricane/damage_curves/hurricane_solar_asset_capex_weighted.json`.
#   **Basis:** 3-second peak gust, **mph** (matches M1/M2). Empirically anchored (FPL Hurricane Ian; Ceferino 2023).
#   **🟡 PROVISIONAL** — medium-confidence placeholders to be replaced (owner-directed).
# - **M2 coupled events** (`data/hurricane/tc_m2_coupling.parquet`) + **TIV** (`tc_m0_sites.json`). **Reproducibility:**
#   per-event loss persists to `data/hurricane/tc_m3_damage.parquet` (+ vendored curve + manifest).

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-14** damage = library **HURRICANE × SOLAR**, capex-weighted (PV 0.35 + mounting 0.15 + substation 0.08; rest
# ≈ wind-immune → DR **caps ~48%**), **PROVISIONAL** — headline `tracker_stow` (x0 148), stow-fail (x0 115) recorded
# as a sensitivity · **ATC-4** observable = **3-s gust** · **ATC-2** physical loss only (no business interruption).
# Full register: [`assumptions.md`](../../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · The curves (HURRICANE × SOLAR library) + capex weights
#
# Logistic params (`L, k, x0`) vendored from the library index. **Wind-damageable hardware** carries the curves;
# inverters / buried cables / civil are **wind-low-vulnerability** (enclosed/below-grade) → DR≈0 for wind, but their
# capex still counts in the denominator (so the asset DR isn't overstated). Weights are **approximate NREL-style**
# (an assumption — [ATC-14](../../../../docs/plans/hurricane/assumptions.md)); mounting/racking is a **primary wind
# subsystem** here (hurricanes break racking).

# %%
# HURRICANE × SOLAR logistic curves (3-s gust mph) — from the infrasure-damage-curves library (PROVISIONAL)
CURVES = {
    "pv_array_tracker_stow":    {"L": 0.85, "k": 0.055, "x0": 148, "src": "empirical FPL Ian + proxy"},
    "pv_array_tracker_midtilt": {"L": 0.95, "k": 0.065, "x0": 115, "src": "stow-FAILURE worst case (n=2)"},
    "pv_array_generic":         {"L": 0.85, "k": 0.050, "x0": 135, "src": "fleet-average composite"},
    "mounting_tracker_solar":   {"L": 0.80, "k": 0.055, "x0": 120, "src": "eng-standard + proxy"},
    "substation_solar":         {"L": 0.80, "k": 0.040, "x0": 120, "src": "HAZUS + NERC post-event"},
}
# capex weights (approximate; wind-damageable subsystems carry curves, rest ≈ wind-immune)
WEIGHTS = {"PV_ARRAY": 0.35, "MOUNTING": 0.15, "SUBSTATION": 0.08, "LOW_WIND_VULN_REMAINDER": 0.42}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

def anchored_logistic(c, x):
    raw = c["L"] / (1 + np.exp(-c["k"] * (x - c["x0"])))
    base = c["L"] / (1 + np.exp(-c["k"] * (0 - c["x0"])))     # DR(0), subtract so DR(0)=0
    return np.clip(raw - base, 0, None)

def asset_dr(gust_mph, pv_curve="pv_array_tracker_stow"):
    dr_pv = anchored_logistic(CURVES[pv_curve], gust_mph)
    dr_mt = anchored_logistic(CURVES["mounting_tracker_solar"], gust_mph)
    dr_sub = anchored_logistic(CURVES["substation_solar"], gust_mph)
    return WEIGHTS["PV_ARRAY"]*dr_pv + WEIGHTS["MOUNTING"]*dr_mt + WEIGHTS["SUBSTATION"]*dr_sub
    # + WEIGHTS["LOW_WIND_VULN_REMAINDER"] * 0  (wind-immune)

# spot-check the curve shape (gust → asset DR), headline vs stow-failure band
print(f"{'gust':>6} {'stow(148)':>10} {'midtilt(115)':>13}   (asset DR, capex-weighted)")
for g in [90, 110, 130, 150, 170, 190]:
    print(f"{g:>6} {asset_dr(g):>10.3f} {asset_dr(g,'pv_array_tracker_midtilt'):>13.3f}")

# %% [markdown]
# ## 2 · Apply to the M2 events → conditional loss per event

# %%
m2 = pd.read_parquet(DATA / "tc_m2_coupling.parquet")
sites = {s["name"]: s for s in json.load(open(DATA / "tc_m0_sites.json"))["sites"]}

m3 = m2.copy()
m3["conditional_DR"] = asset_dr(m3["gust_3s_mph"].values)                       # headline (stow)
m3["conditional_DR_stowfail"] = asset_dr(m3["gust_3s_mph"].values, "pv_array_tracker_midtilt")
m3["tiv_usd"] = m3["site"].map(lambda s: sites[s]["tiv_usd"])
m3["conditional_loss_usd"] = m3["conditional_DR"] * m3["value_exposed_fraction"] * m3["tiv_usd"]
print(f"events: {len(m3)}")
for site, grp in m3.groupby("site"):
    if grp.empty: continue
    print(f"\n{site}:")
    print(f"  gust 3-s: median {grp.gust_3s_mph.median():.0f}, max {grp.gust_3s_mph.max():.0f} mph")
    print(f"  conditional DR (stow): median {grp.conditional_DR.median():.3f}, max {grp.conditional_DR.max():.3f}")
    print(f"  conditional DR (stow-FAIL): median {grp.conditional_DR_stowfail.median():.3f}, max {grp.conditional_DR_stowfail.max():.3f}")
    print(f"  worst single-event loss: ${grp.conditional_loss_usd.max()/1e6:.1f}M of ${grp.tiv_usd.iloc[0]/1e6:.0f}M TIV "
          f"({100*grp.conditional_DR.max():.0f}% of TIV)")

# %% [markdown]
# ## 3 · Known-answer checks (basics-spot-on)

# %%
ev = m3[m3.site.str.startswith("Everglades", na=False)] if (m3.site.str.startswith("Everglades")).any() else \
     m3[m3.site_role.str.startswith("proving")]
checks = {
    "DR anchored ~0 at low gust (90 mph well below onset)": asset_dr(90) < 0.10,
    "DR monotonic in gust": bool(np.all(np.diff([asset_dr(g) for g in range(80, 200, 5)]) >= -1e-9)),
    "DR bounded < max subsystem L (≤0.85)": asset_dr(250) <= 0.85 + 1e-9,
    "stow-failure ≥ stow at every gust (worse case is worse)":
        all(asset_dr(g, "pv_array_tracker_midtilt") >= asset_dr(g) - 1e-9 for g in range(90, 200, 5)),
    "high site takes material loss at its max gust (>20% DR)": ev["conditional_DR"].max() > 0.20,
    "Cat-5 direct hit (~180 mph) is severe (>40% DR)": asset_dr(180) > 0.40,
    # documented limitation: asset DR caps ~48% — electrical/civil (0.42 of capex) treated wind-immune (library scope:
    # no solar inverter/electrical wind curve). So total-loss is NOT represented — a known provisional-curve limit.
    "asset DR caps near the wind-exposed capex share (~0.48), as designed": 0.44 <= asset_dr(300) <= 0.50,
    "baseline carries no events (true-zero)": (m3.site_role.str.startswith("baseline")).sum() == 0,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "an M3 check failed"
print("\nall M3/01 known-answer checks pass ✅")

# %% [markdown]
# ## 4 · Emit — per-event conditional loss + the vendored curves

# %%
out = DATA / "tc_m3_damage.parquet"
m3.to_parquet(out, index=False)

vendored = {
    "curve_id": "hurricane/solar__asset__capex_weighted",
    "STATUS": "PROVISIONAL — medium-confidence library placeholders, to be replaced by a better curve set later (owner-directed; ATC-14)",
    "hazard_type": "HURRICANE", "asset_type": "solar",
    "intensity_metric": "wind_speed_mph", "intensity_measure": "3-second peak gust", "intensity_unit": "mph",
    "logistic_form": "DR(x) = L/(1+exp(-k*(x-x0)))", "anchoring": "minus DR(0) so DR(0)=0",
    "source": "the infrasure-damage-curves library — HURRICANE_x_SOLAR group",
    "headline_pv_curve": "pv_array_tracker_stow (x0 148) — assumes tracker stows; FPL-Ian-anchored",
    "sensitivity_pv_curve": "pv_array_tracker_midtilt (x0 115) — stow FAILURE worst case",
    "capex_weights": WEIGHTS,
    "weights_note": "approximate NREL-style; MOUNTING restored as primary wind subsystem (flood had zeroed it); "
                    "inverter/electrical/civil ≈ wind-immune → in the 0.42 remainder at DR=0",
    "LIMITATION_dr_cap": "asset DR caps ~0.48 (wind-exposed capex share) — electrical/civil treated wind-immune "
                         "(library gives no solar inverter/electrical wind curve), so catastrophic TOTAL loss is NOT "
                         "represented. Revisit with the replacement curve set / a debris-driven remainder vulnerability.",
    "curves_used": {k: CURVES[k] for k in ["pv_array_tracker_stow", "pv_array_tracker_midtilt",
                                           "mounting_tracker_solar", "substation_solar"]},
}
(CURVE_DIR / "hurricane_solar_asset_capex_weighted.json").write_text(json.dumps(vendored, indent=2))
manifest = {
    "notebook": "hurricane/solar/m3_damage/01_damage",
    "curve_status": "PROVISIONAL (ATC-14) — library hurricane×solar, to be replaced",
    "headline": "pv_array_tracker_stow (x0 148)", "sensitivity_band": "pv_array_tracker_midtilt (x0 115)",
    "spot_DR": {f"{g}mph": round(float(asset_dr(g)), 3) for g in [110, 130, 150, 170, 190]},
    "n_events": int(len(m3)),
    "outputs": {"damage_parquet": str(out.relative_to(ROOT)),
                "vendored_curve": str((CURVE_DIR/'hurricane_solar_asset_capex_weighted.json').relative_to(ROOT))},
}
(DATA / "tc_m3_manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"wrote {out}\nwrote vendored curve + manifest")

# %% [markdown]
# ## Takeaways → next
#
# - **Damage mapped on the exact 3-s-gust basis** — library HURRICANE × SOLAR logistic, capex-weighted (modules +
#   mounting + substation are the wind-damageable hardware; inverters/cables/civil ≈ wind-immune).
# - **🟡 Curves are PROVISIONAL** (medium-confidence, owner-flagged for replacement) — the dominant uncertainty.
#   Headline = `tracker_stow` (x0 148, assumes stow works); **stow-failure band** (`midtilt`, x0 115) carried as the
#   sensitivity.
# - Per-event conditional loss emitted (DR × fraction × TIV); vendored curve saved for reproducibility.
# - **🟡 Documented limitation:** asset DR **caps ~48%** (electrical/civil treated wind-immune per library scope) →
#   catastrophic *total* loss isn't represented. Worst Cat-5 hit ≈ **41% of TIV**. Revisit with the replacement curve.
#
# **Next → M4 (loss & metrics):** sample the storm-resolved events through the shared MC engine → EAL / VaR / PML /
# TVaR (% of TIV + $), with the gust-factor / Holland-B / **stow-state** sensitivity dials and the ~1,000-yr
# catalog-depth limit carried in.
