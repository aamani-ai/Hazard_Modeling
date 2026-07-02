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
# # Hurricane · Wind-farm — M4 loss & metrics: compound-Poisson MC → wind-only EAL / VaR / PML / TVaR
#
# **Magnitude metric:** the **3-second peak gust (mph)** drives the M3 per-storm conditional losses this layer
# integrates. Headline metric is **% of TIV** + dollars. Site: Amazon Wind US East (NC).
# **Data source:** the M3 per-storm conditional losses (`data/hurricane/tc_windfarm_m3_damage.parquet`), the shared
# coastal event rate λ from flood-coastal M1 (`flood_coastal_m1_catalog_manifest.json`, Amazon entry, λ≈0.0116/yr,
# JD-FL-21), and the M0 TIV record (`flood_wind_m0_sites.json`).
# **What this notebook does:** turns M3's per-storm conditional losses into a sampled annual-loss distribution on the
# shared compound-Poisson Monte-Carlo engine (each year draws `N ~ Poisson(λ)` storms, each storm's loss resampled
# from the empirical per-storm severity, summed within the year and bounded at 100% TIV) and reads EAL / VaR / PML /
# TVaR off it. This is the **wind-only** headline for the cell; the surge × wind compound combine is the separate
# flood-coastal × wind M4 step, which reads M3's per-storm per-subsystem table and joins on `event_family_id`
# ([JD-FL-12](../../../../docs/plans/flood/decisions.md)). Outputs metrics + the annual vector + EP curve.
#
# **Reported honestly (the caveats carried in):**
# - **% of TIV is the headline** ($/MW TIV is an estimate — AFL-W3).
# - **λ is the SHARED coastal-event rate** (≤50 km close-passage rate from flood-coastal M1, JD-FL-21) — used so the
#   wind leg and surge leg sit on the identical event frame (required for the compound join). It is anchored on only
#   2 observed passages / 173 yr → a wide ±~71% frequency band; a standalone wind screen (≤100 km, JD-TC-8) would admit
#   more distant-but-windy storms and raise λ.
# - **Curve is Low-confidence** (reused convective_wind turbine curve; the dominant uncertainty), DR caps ~0.65 (no
#   tower-collapse total-loss mode).
# - **PML to 500-yr** (inside the ~1,000-yr catalog limit).
#
# > Prior: [M3 damage](../m3_damage/01_damage.ipynb) · the compound combine that consumes M3: flood-coastal × wind M4
# > ([JD-FL-12](../../../../docs/plans/flood/decisions.md)).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"
FLOOD = ROOT / "data" / "flood"
RPS = [100, 250, 500]
N_YEARS = 1_000_000
AMAZON_SLUG = "amazon_wind_us_east"
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **M3 per-storm conditional losses** (`data/hurricane/tc_windfarm_m3_damage.parquet`) — the severity samples.
# - **Wind λ** (`data/hurricane/tc_m1_site_summary.parquet`, Amazon row) — the ≤100 km WIND-screen event rate
#   (unified hurricane M1, JD-TC-8). The surge leg keeps its own ≤50 km rate (JD-FL-21); join on `event_family_id`.
# - **TIV** (`data/flood/flood_wind_m0_sites.json`). **Engine:** shared compound-Poisson MC (event-based, no RP bridge).
#   **Reproducibility:** metrics + annual vector + EP curve → `data/hurricane/tc_windfarm_m4_*`.

# %% [markdown]
# ## 1 · Inputs — per-storm loss fractions + the shared rate λ

# %%
m3 = pd.read_parquet(DATA / "tc_windfarm_m3_damage.parquet")
# WIND-leg λ now from the unified hurricane M1 site summary (Amazon, 100 km WIND screen) — NOT the flood-coastal
# 50 km surge rate. Wind reaches ~100 km, so screening wind at the 50 km surge radius undercounted the rate
# (2 obs → 0.0116/yr); the 100 km wind screen gives 13 obs → ~0.0751/yr. The surge leg keeps the 50 km rate; the
# two join on event_family_id (= RAFT storm_ID), and the 50 km surge storms remain a subset of these wind storms.
summ = pd.read_parquet(DATA / "tc_m1_site_summary.parquet")
amz = summ[summ["asset"] == "wind_farm"].iloc[0]
LAM = float(amz["lambda_per_yr"])
OBS_N = int(amz["obs_passages_100km"]); REC_YR = 2023 - 1851 + 1
FREQ_REL_UNC = OBS_N ** -0.5                                    # √n/n
TIV = float(m3["tiv_usd"].iloc[0])
loss_fracs = m3["conditional_DR"].values
print(f"wind λ = {LAM:.4f}/yr (100 km WIND screen, unified M1; anchored on {OBS_N} obs passages / {REC_YR} yr → ±{FREQ_REL_UNC*100:.0f}% freq band)")
print(f"{len(loss_fracs)} per-storm DR samples · mean {loss_fracs.mean()*100:.3f}% · max {loss_fracs.max()*100:.2f}% of TIV · TIV ${TIV/1e6:.0f}M")

# %% [markdown]
# ## 2 · The shared compound-Poisson MC + metrics
#
# Each simulated year draws `N ~ Poisson(λ)` storms; each storm's loss is resampled from the empirical per-storm
# severity (M3's conditional losses); losses **sum within the year** (bounded at 100% TIV). Metrics read off the
# sampled annual-loss vector — never the expected-loss shortcut.

# %%
rng = np.random.default_rng(20260621)


def simulate(fr, lam, n_years=N_YEARS):
    if lam <= 0 or len(fr) == 0:
        return np.zeros(n_years), np.zeros(n_years)
    n_per_year = rng.poisson(lam, n_years)
    total = int(n_per_year.sum())
    draws = rng.choice(fr, size=total, replace=True)
    year_id = np.repeat(np.arange(n_years), n_per_year)
    annual = np.zeros(n_years)
    np.add.at(annual, year_id, draws)                          # AEP = annual aggregate (sum of a year's storms)
    oep = np.zeros(n_years)
    if total:
        np.maximum.at(oep, year_id, draws)                     # OEP = the year's single largest storm (occurrence basis)
    return np.minimum(annual, 1.0), np.minimum(oep, 1.0)


def metrics_of(v):
    var99 = np.percentile(v, 99)
    return {"EAL": v.mean(), "VaR99": var99, "TVaR99": v[v >= var99].mean() if (v >= var99).any() else 0.0,
            **{f"PML{T}": np.percentile(v, 100 * (1 - 1 / T)) for T in RPS}}


def twin_metrics(aep, oep):                                    # house-standard metric set, native units (fraction of TIV)
    var99 = np.percentile(aep, 99)
    return {
        "EAL":                  float(aep.mean()),
        "VaR95 (AEP-PML20)":    float(np.quantile(aep, 0.95)),
        "VaR99 (AEP-PML100)":   float(var99),                  # this IS PML100 — one entry, both names
        "VaR99.6 (AEP-PML250)": float(np.quantile(aep, 0.996)),
        "PML500 (AEP-99.8)":    float(np.quantile(aep, 0.998)),
        "TVaR99":               float(aep[aep >= var99].mean()) if (aep >= var99).any() else 0.0,
        "OEP-PML100":           float(np.quantile(oep, 0.99)),  # per-EVENT (largest single storm/yr), not per-year
    }


annual, oep = simulate(loss_fracs, LAM)
m = metrics_of(annual)
tw = twin_metrics(annual, oep)
metrics_usd = {k: round(v * TIV, 2) for k, v in tw.items()}
metrics_pct_of_tiv = {k: round(v * 100, 4) for k, v in tw.items()}
eal_lo, eal_hi = m["EAL"] * (1 - FREQ_REL_UNC), m["EAL"] * (1 + FREQ_REL_UNC)
print(f"zero-loss years: {(annual == 0).mean()*100:.2f}%  (λ small → most years see no qualifying storm)")

# %% [markdown]
# ## 3 · The headline (wind-only, % of TIV)

# %%
print(f"HEADLINE — Amazon Wind US East (hurricane WIND only, % of TIV, reused turbine curve [Low confidence]):")
print(f"  EAL:     {m['EAL']*100:.3f}%   (~{eal_lo*100:.3f}–{eal_hi*100:.3f}% incl. ±{FREQ_REL_UNC*100:.0f}% storm-rate uncertainty)")
print(f"  EAL ($): ${m['EAL']*TIV/1e6:.2f}M")
for T in RPS:
    print(f"  PML{T}:  {m[f'PML{T}']*100:5.2f}%  (${m[f'PML{T}']*TIV/1e6:.1f}M)")
print(f"  VaR99:   {m['VaR99']*100:.2f}%")
print(f"  TVaR99:  {m['TVaR99']*100:.2f}%")
print("\n⚠ wind is SMALL at Amazon — most storms gust below IEC turbine survival; the tail is the rare Cat-3 close")
print("  passage. The cell's MATERIAL hazard is SURGE (flood-coastal × wind M4); this wind leg is the join partner.")

# %% [markdown]
# ## 4 · Known-answer checks

# %%
checks = {
    "EAL ≈ λ·mean(per-storm DR) (compound-Poisson identity)":
        abs(m["EAL"] - LAM * loss_fracs.mean()) < 5e-4,
    "PML monotonic in return period":
        (m["PML500"] >= m["PML250"] - 1e-12) and (m["PML250"] >= m["PML100"] - 1e-12),
    "TVaR99 ≥ VaR99 (tail-average past the quantile)": m["TVaR99"] >= m["VaR99"] - 1e-12,
    "all annual metrics ≤ 100% of TIV (aggregate bound)":
        max(m["VaR99"], m["TVaR99"], *[m[f"PML{T}"] for T in RPS]) <= 1.0 + 1e-9,
    "EAL > 0 (material peril, however small)": m["EAL"] > 0,
    "single-event PML ≤ DR cap (~0.65); no total loss": m["PML500"] <= 0.66,
    "most years loss-free; zero-year frac ≈ Poisson exp(-λ) (MC known-answer)":
        ((annual == 0).mean() > 0.5) and (abs((annual == 0).mean() - np.exp(-LAM)) < 0.01),
    "AEP ≥ OEP every year (annual total ≥ its largest single storm)": bool((annual + 1e-12 >= oep).all()),
    "OEP-PML100 ≤ AEP-PML100 (occurrence ≤ aggregate)": tw["OEP-PML100"] <= tw["VaR99 (AEP-PML100)"] + 1e-12,
    "twin-block unit consistency: usd/TIV*100 == pct_of_tiv (to rounding)":
        all(abs(metrics_usd[k] / TIV * 100 - metrics_pct_of_tiv[k]) < 1e-3 for k in tw),
    "PML500 ≥ PML250 ≥ PML100 ≥ EAL > 0 (twin-block monotone)":
        tw["PML500 (AEP-99.8)"] >= tw["VaR99.6 (AEP-PML250)"] >= tw["VaR99 (AEP-PML100)"] >= tw["EAL"] > 0,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "an M4 check failed"
print("\nall M4/01 known-answer checks pass ✅")

# %% [markdown]
# ## 5 · Plot — annual-loss exceedance (EP) curve

# %%
fig, ax = plt.subplots(figsize=(7, 4.5))
v = np.sort(annual)[::-1]; ep = np.arange(1, len(v) + 1) / len(v); nz = v > 0
ax.plot(v[nz] * 100, ep[nz], color="tab:purple", lw=1.7, label="hurricane wind (Amazon Wind US East)")
for T in RPS:
    ax.axhline(1 / T, color="grey", ls=":", lw=0.7); ax.text(0.05, 1 / T * 1.1, f"1-in-{T}", fontsize=7, color="grey")
ax.set_yscale("log"); ax.set_xlabel("annual loss (% of TIV)"); ax.set_ylabel("annual exceedance probability")
ax.set_title("Hurricane wind × wind-farm — annual loss EP curve\nAmazon Wind US East (reused turbine curve)")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(DATA / "tc_windfarm_m4_ep_curve.png", dpi=110)
print("wrote", DATA / "tc_windfarm_m4_ep_curve.png")

# %% [markdown]
# ## 6 · Emit — metrics + annual vector + manifest

# %%
pd.DataFrame({"annual_loss_frac_tiv": annual}).to_parquet(DATA / "tc_windfarm_m4_annual_vectors.parquet", index=False)
M = pd.DataFrame([{"site": "Amazon Wind US East", "slug": AMAZON_SLUG, "lambda": LAM, "tiv_usd": TIV,
                   "EAL_pct": m["EAL"] * 100, "EAL_usd": m["EAL"] * TIV,
                   "VaR99_pct": m["VaR99"] * 100, "TVaR99_pct": m["TVaR99"] * 100,
                   **{f"PML{T}_pct": m[f"PML{T}"] * 100 for T in RPS},
                   **{f"PML{T}_usd": m[f"PML{T}"] * TIV for T in RPS}}])
M.to_parquet(DATA / "tc_windfarm_m4_loss_metrics.parquet", index=False)
manifest = {
    "notebook": "hurricane/wind_farm/m4_loss_metrics/01_loss_metrics",
    "site": "Amazon Wind US East (NC)", "slug": AMAZON_SLUG, "asset": "wind_farm",
    "engine": f"shared compound-Poisson MC (event-based, no RP bridge); N_years={N_YEARS}",
    "headline_metric": "% of TIV (dollars secondary — $/MW estimate)",
    "lambda_per_yr": LAM,
    "lambda_note": ("WIND-screen rate (≤100 km, unified hurricane M1) — wind reaches ~100 km, so the rate is anchored "
                    "on %d obs hurricane passages / %d yr → ±%d%% band. Was previously the ≤50 km surge rate "
                    "(2 obs → 0.0116/yr), which screened wind at the surge radius and undercounted it ~6.5×. The surge "
                    "leg keeps the ≤50 km rate; the two join on event_family_id (= RAFT storm_ID, surge ⊆ wind)."
                    % (OBS_N, REC_YR, round(FREQ_REL_UNC * 100))),
    "headline_pct_of_TIV": {"EAL": round(m["EAL"] * 100, 3),
                            "EAL_with_freq_unc": [round(eal_lo * 100, 3), round(eal_hi * 100, 3)],
                            **{f"PML{T}": round(m[f"PML{T}"] * 100, 2) for T in RPS},
                            "VaR99": round(m["VaR99"] * 100, 2), "TVaR99": round(m["TVaR99"] * 100, 2)},
    # house-standard twin blocks — identical keys, the block name carries the unit (parity with hail/wildfire/conv-wind)
    "metrics_usd": metrics_usd,
    "metrics_pct_of_tiv": metrics_pct_of_tiv,
    "occurrence_basis_note": "OEP-PML100 = per-EVENT (largest single storm/yr); AEP metrics = annual aggregate (sum of a year's storms). λ≪1 → OEP≈AEP (rarely >1 storm/yr).",
    "zero_loss_year_fraction": round(float((annual == 0).mean()), 4),
    "caveats": [
        "wind is SMALL at Amazon — frequent storms below IEC turbine survival; tail = rare Cat-3 close passage",
        "the cell's MATERIAL hazard is SURGE (flood-coastal × wind M4); this wind leg is the compound join partner",
        "curve Low-confidence (reused convective_wind turbine curve); DR caps ~0.65 (no tower-collapse total loss)",
        "λ from ≤100 km wind screen (±%d%%, %d-obs anchor); surge leg keeps ≤50 km, join on event_family_id (surge ⊆ wind)" % (round(FREQ_REL_UNC * 100), OBS_N),
    ],
    "outputs": {"metrics_parquet": "data/hurricane/tc_windfarm_m4_loss_metrics.parquet",
                "annual_vectors": "data/hurricane/tc_windfarm_m4_annual_vectors.parquet",
                "ep_curve_png": "data/hurricane/tc_windfarm_m4_ep_curve.png"},
}
(DATA / "tc_windfarm_m4_metrics_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote", DATA / "tc_windfarm_m4_loss_metrics.parquet", "+ vectors + manifest")

# %% [markdown]
# ## Takeaways — hurricane × wind-farm M2→M4 COMPLETE
#
# - **Hurricane × wind-farm runs end-to-end** at Amazon Wind US East (M0/M1 shared from flood-coastal → M2 per-node
#   field-intensity → M3 per-storm per-subsystem damage → M4 compound-Poisson MC).
# - **Wind-only headline is small** (EAL ≈ a few ×0.01% of TIV; the tail is the rare Cat-3 close passage) — the honest
#   "turbines are built to survive sound-weakened storms" result; the cell's material hazard is **surge**.
# - **The deliverable for coastal × wind is in hand** — `tc_windfarm_m3_damage.parquet`: per-storm, **per-subsystem**
#   wind DR stamped `event_family_id`. **Next (separate): finish flood-coastal × wind M4** — read this table, join the
#   surge leg on `event_family_id`, and run the JD-FL-12 `max(wind_DRᵢ, surge_DRᵢ)`-per-subsystem compound combine.
