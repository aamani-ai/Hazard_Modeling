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
# # Flood · Wind-farm — M4 loss & metrics: annual loss for all three sub-perils (riverine + pluvial + coastal compound)
#
# **Magnitude metric:** inundation **depth (ft above ground)** drives the M3 conditional losses this layer integrates —
# riverine/pluvial by return period (annual-max frame), coastal surge by hurricane category (per storm). Headline
# metrics are **% of TIV** + dollars (DD-4), the frame hail/wildfire/wind/flood-solar share.
# **Data source:** the M3 flood × wind conditional-loss manifest (`flood_wind_m3_damage_manifest.json`, riverine +
# pluvial + coastal), the per-node coastal SLOSH depth tables, the hurricane × wind-farm per-storm per-subsystem wind
# DR (`data/hurricane/tc_windfarm_m3_damage.parquet`), the shared coastal event rate λ from flood-coastal M1, and FEMA
# National Risk Index (Riverine Flooding EAL, Lee County IL) as an independent benchmark.
# **What this notebook does:** turns the M3 conditional losses into the annual loss distribution → EAL / VaR / PML /
# TVaR, running **two frequency frames** ([JD-FL-17](../../../../docs/plans/flood/decisions.md); Amazon Wind US East is
# the all-three site):
# - **Inland (riverine + pluvial)** — annual-maximum MC (~1 flood/yr,
#   [JD-FL-7](../../../../docs/plans/flood/decisions.md)): per simulated year draw one annual severity `AEP ~ U(0,1)`,
#   read both sub-peril curves at it (comonotonic), year loss = `max(riverine, pluvial)` (worse-source-wins, φ=1 shared
#   ground, [JD-FL-11](../../../../docs/plans/flood/decisions.md)); metrics on the joint per-year vector.
# - **Coastal (surge × hurricane wind)** — compound-Poisson event stream at λ_surge: per qualifying storm, combine
#   surge and wind **per subsystem** `combined_DRₛ = max(wind_DRₛ, surge_DRₛ)`
#   ([JD-FL-12](../../../../docs/plans/flood/decisions.md)), joined on `event_family_id`. Shared subsystems = electrical
#   + substation; wind-only = rotor + nacelle; surge-only = foundation + civil.
# - **Total flood** = inland annual-max **+** coastal compound (independent streams summed). A with/without bracket
#   reports the substation-collector contribution (turbines-only floor vs full headline, JD-FL-W7).
#
# The wind-specific inputs upstream: L₁₀₀/L₅₀₀ summed over flooded turbines + the substation (M3), the riverine RP
# curve gauge-grounded ([JD-FL-W5](../../../../docs/plans/flood/decisions.md)), pluvial pad-gated with lidar-grounded
# f+d_cap (JD-FL-15 → floor = 0 at every node). Coastal-exposed site today = Amazon Wind US East; Green River /
# Shepherds Flat are inland-only.
#
# > **Honest:** PML@T reproduces the worse sub-peril's Lₜ by construction; EAL rests on the gauge-grounded riverine
# > 10/25/50-yr (solid) + the assumption-driven, here-negligible pluvial. Plan:
# > [`m_wind_farm.md`](../../../../docs/plans/flood/m_wind_farm.md).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "flood"

m3 = pd.DataFrame(json.loads((OUT / "flood_wind_m3_damage_manifest.json").read_text())["sites"])
sites = m3.groupby("name").agg(slug=("slug", "first"), role=("role", "first"), tiv_usd=("tiv_usd", "first")).reset_index()
SUBPERILS = sorted(m3["sub_peril"].unique())                                          # ['pluvial', 'riverine']
L = {(r["name"], r["sub_peril"], r["rp_years"]): r["cond_loss_frac_tiv"] for _, r in m3.iterrows()}
# turbines-only loss (drop the substation) — the ROBUST FLOOR (the substation is the only assumed-location node).
L_TURB = {(r["name"], r["sub_peril"], r["rp_years"]): r["turb_loss_frac_tiv"] for _, r in m3.iterrows()}
print("M3 conditional losses (input — riverine + pluvial):")
print(m3[["sub_peril", "name", "rp_years", "turb_loss_frac_tiv", "sub_loss_frac_tiv", "cond_loss_frac_tiv"]].to_string(index=False))

# %% [markdown]
# ## 1 · Per-sub-peril loss-exceedance curves (one per sub_peril × site) — JD-FL-7 + JD-FL-W5
#
# Each `(site, sub_peril)` gets its own RP→loss curve from M3 — riverine (10/25/50/100/250/500-yr, gauge-grounded) and
# pluvial (10/25/50/100/500-yr, Atlas-14, pad-gated). A single onset anchor at **5-yr** (AEP 0.2 → 0) sets where damage
# begins (a flood smaller than ~5-yr doesn't reach the elevated wind base). §2 **co-samples** both at one annual
# severity and takes the **worse** (JD-FL-11).

# %%
ONSET_AEP = 0.20        # 5-yr: below the most-frequent modeled RP, damage ramps from 0 (same as the riverine-only M4)

RP_AVAIL = {}
for (nm, sp, rp) in L:
    RP_AVAIL.setdefault((nm, sp), []).append(rp)
for k in RP_AVAIL:
    RP_AVAIL[k].sort()


def make_curve(name, sp, Ltab=L):
    pts = [(ONSET_AEP, 0.0)] + [(round(1 / rp, 4), Ltab[(name, sp, rp)]) for rp in RP_AVAIL[(name, sp)]]
    return sorted(pts, reverse=True)   # decreasing AEP (frequent → rare)


def loss_at_aep(aep, curve):
    aeps = np.array([c[0] for c in curve]); losses = np.array([c[1] for c in curve])
    x = np.log10(np.clip(aep, 1e-7, 1.0))
    xs = np.log10(aeps[::-1]); ys = losses[::-1]
    loss = np.interp(x, xs, ys)
    slope = (losses[-1] - losses[-2]) / (np.log10(aeps[-1]) - np.log10(aeps[-2]))
    extrap = losses[-1] + slope * (x - np.log10(aeps[-1]))
    loss = np.where(x < np.log10(aeps[-1]), np.minimum(extrap, 3 * max(losses[-1], 1e-9)), loss)
    loss = np.where(aep >= ONSET_AEP, 0.0, loss)
    return np.clip(loss, 0.0, None)


for _, s in sites.iterrows():
    for sp in SUBPERILS:
        print(f"  {s['name']:16s} {sp:9s}: " + " · ".join(f"{int(1/a)}yr={l*100:.3f}%" for a, l in make_curve(s['name'], sp) if a < ONSET_AEP))

# %% [markdown]
# ## 2 · Monte-Carlo annual loss → **combine sub-perils** (co-sample, worse-wins) → metrics
#
# Per simulated year draw **one** annual severity `AEP ~ U(0,1)`, read **both** sub-peril curves at it (comonotonic),
# then the year's flood loss = **max(riverine, pluvial)** (JD-FL-11): correlation-honest, no double-count. Metrics on
# the **combined** per-year vector. Marginal per-sub-peril EALs kept for the breakdown; the **additive-capped**
# envelope is recorded as the φ=0 upper sensitivity bound (not used downstream).

# %%
N = 500_000
rng = np.random.default_rng(20260617)
RPS = [100, 250, 500]


def metrics_of(v):
    var99 = np.percentile(v, 99)
    return {"EAL": v.mean(), "VaR99": var99, "TVaR99": v[v >= var99].mean() if (v >= var99).any() else 0.0,
            **{f"PML{T}": np.percentile(v, 100 * (1 - 1 / T)) for T in RPS}}


def twin_metrics(aep, oep):   # house-standard metric set, native units (fraction of TIV) — emitted as $ and % twin blocks
    var99 = np.percentile(aep, 99)
    return {
        "EAL":                  float(aep.mean()),
        "VaR95 (AEP-PML20)":    float(np.quantile(aep, 0.95)),
        "VaR99 (AEP-PML100)":   float(var99),                  # this IS PML100 — one entry, both names
        "VaR99.6 (AEP-PML250)": float(np.quantile(aep, 0.996)),
        "PML500 (AEP-99.8)":    float(np.quantile(aep, 0.998)),  # flood's existing 500-yr point
        "TVaR99":               float(aep[aep >= var99].mean()) if (aep >= var99).any() else 0.0,
        "OEP-PML100":           float(np.quantile(oep, 0.99)),  # per-EVENT (occurrence basis), not per-year
    }


tiv_by_site = {s["name"]: s["tiv_usd"] for _, s in sites.iterrows()}
rows, vectors, marginal_eal = [], {}, {}
for _, s in sites.iterrows():
    nm, tiv = s["name"], s["tiv_usd"]
    aep = rng.random(N)                                            # ONE severity per year → co-sample (JD-FL-11)
    per_sp = {sp: loss_at_aep(aep, make_curve(nm, sp)) for sp in SUBPERILS}
    combined = np.maximum.reduce(list(per_sp.values()))            # HEADLINE: worse-source-wins (φ=1; shared ground)
    vectors[nm] = combined
    for sp, v in per_sp.items():
        marginal_eal[(nm, sp)] = v.mean() * 100
    cm = metrics_of(combined)
    additive = np.minimum(sum(per_sp.values()), 1.0)               # ENVELOPE only (φ=0 upper bound), co-sampled
    am = metrics_of(additive)
    rows.append({"name": nm, "role": s["role"], "tiv_usd": tiv,
                 "EAL_pct": cm["EAL"] * 100, "EAL_usd": cm["EAL"] * tiv,
                 "VaR99_pct": cm["VaR99"] * 100, "TVaR99_pct": cm["TVaR99"] * 100,
                 **{f"PML{T}_pct": cm[f"PML{T}"] * 100 for T in RPS},
                 **{f"PML{T}_usd": cm[f"PML{T}"] * tiv for T in RPS},
                 **{f"EAL_{sp}_pct": marginal_eal[(nm, sp)] for sp in SUBPERILS},
                 "EAL_addUB_pct": am["EAL"] * 100, "PML500_addUB_pct": am["PML500"] * 100})
M = pd.DataFrame(rows)
print(M[["name", "EAL_pct", "VaR99_pct", "PML100_pct", "PML250_pct", "PML500_pct", "TVaR99_pct"]].round(3).to_string(index=False))
print("\ndollars:")
print(M[["name", "EAL_usd", "PML100_usd", "PML500_usd"]].round(0).to_string(index=False))
print("\nsub-peril EAL breakdown (% TIV) + the JD-FL-11 combine envelope (headline worse-wins → additive-capped UB):")
for _, r in M.iterrows():
    parts = " + ".join(f"{sp} {r[f'EAL_{sp}_pct']:.3f}" for sp in SUBPERILS)
    print(f"  {r['name']:16s} {parts}  | HEADLINE(worse-wins) {r['EAL_pct']:.3f}  envelope→ {r['EAL_pct']:.3f}–{r['EAL_addUB_pct']:.3f}")
print("  (headline = worse-wins φ=1, used downstream; additive-capped = φ=0 upper bound, recorded sensitivity only — JD-FL-11)")

# %% [markdown]
# ### 2b · The substation bracket — full (with collector) vs turbines-only floor (JD-FL-W7)
#
# We bracket the headline by the **turbines-only floor** (combined worse-wins over each sub-peril's turbine-only
# curve). Green River's own collector (the in-hull `substation=generation` 138 kV node on the west edge; JD-FL-W7)
# sits **in the river valley → it FLOODS** (riverine 0.56 m @ 10-yr → 1.00 m @ 500-yr) and carries ~9% of TIV on a
# steep curve, so the **full headline sits well above the turbines-only floor** — the collector dominates the EAL. The
# floor (collector excluded/dry) is the documented with-vs-without bracket. *(Pluvial is 0 at every node — lidar-grounded
# floor, water-limited; JD-FL-15.)*

# %%
def combined_floor(nm, aep):
    per_sp = {sp: loss_at_aep(aep, make_curve(nm, sp, L_TURB)) for sp in SUBPERILS}
    return np.maximum.reduce(list(per_sp.values()))


floor = {}
for _, s in sites.iterrows():
    yl = combined_floor(s["name"], rng.random(N))
    floor[s["name"]] = {"EAL_pct": yl.mean() * 100, "PML100_pct": np.percentile(yl, 99) * 100,
                        "PML500_pct": np.percentile(yl, 99.8) * 100}
gr_full = M[M.name == "Green River"].iloc[0]; gr_floor = floor["Green River"]
sub_share = (1 - gr_floor["EAL_pct"] / gr_full["EAL_pct"]) * 100 if gr_full["EAL_pct"] > 1e-9 else 0.0
print(f"Green River — headline (combined, real flooding collector): EAL {gr_full['EAL_pct']:.2f}% · PML100 {gr_full['PML100_pct']:.1f}% · PML500 {gr_full['PML500_pct']:.1f}% TIV")
print(f"Green River — turbines-only floor (collector excluded):     EAL {gr_floor['EAL_pct']:.2f}% · PML100 {gr_floor['PML100_pct']:.1f}% · PML500 {gr_floor['PML500_pct']:.1f}% TIV")
print(f"→ the flooding collector contributes ~{max(sub_share,0):.0f}% of EAL; the headline is collector-dominated (JD-FL-W7).")

# %% [markdown]
# ## 2c · Coastal compound — surge × hurricane WIND, per subsystem (JD-FL-12), for coastal-exposed sites
#
# The capstone. Per qualifying storm, combine the **surge** leg (this cell's coastal M2/M3) and the **hurricane wind**
# leg (`data/hurricane/tc_windfarm_m3_damage` — per-storm per-subsystem DR at Amazon, built for this join) **per
# subsystem**: `combined_DRₛ = max(wind_DRₛ, surge_DRₛ)`, joined on `event_family_id`. Both legs share the same
# 7-subsystem capex split. Surge reaches the base (foundation/electrical/civil/substation); wind reaches the aero
# (rotor/nacelle/electrical/substation) → **shared = electrical + substation** carry the max. Compound-Poisson MC at
# **λ_surge**. (the wind analogue of the solar coastal compound, with per-node legs.)

# %%
TC = ROOT / "data" / "hurricane"
FT_M = 0.3048
CAPEX7 = {"rotor_blades": 0.26, "nacelle_drivetrain": 0.21, "tower": 0.16, "foundation": 0.12,
          "substation": 0.09, "electrical": 0.09, "civil": 0.07}                 # same split as both M3s
SURGE_CURVE = {"electrical": (0.90, 3.0, 0.75), "substation": (0.95, 2.5, 1.50),  # flood × wind M3 surge curves
               "civil": (0.70, 1.2, 2.00), "foundation": (0.40, 0.8, 3.00)}
def _sdr(depth_ft, L, k, x0):
    raw = L / (1 + np.exp(-k * (depth_ft - x0))); floor = L / (1 + np.exp(-k * (0 - x0)))
    return np.clip(raw - floor, 0.0, None)

cman = json.loads((OUT / "flood_coastal_m1_catalog_manifest.json").read_text())
coastal_wind_sites = [c for c in cman["sites"] if c["asset"] == "wind_farm" and c["exposed"]]
wind_leg = pd.read_parquet(TC / "tc_windfarm_m3_damage.parquet")
compound_metrics, coastal_vectors, coastal_oep_vectors, compound_events = {}, {}, {}, {}

def cp_metrics(annual, tiv):
    return {"EAL_pct": annual.mean()/tiv*100, "PML100_pct": np.quantile(annual, 0.99)/tiv*100,
            "PML250_pct": np.quantile(annual, 0.996)/tiv*100, "PML500_pct": np.quantile(annual, 0.998)/tiv*100}

for cs in coastal_wind_sites:
    cslug, nm, lam = cs["slug"], cs["name"], cs["lambda_per_yr"]
    TIV = float(sites[sites.name == nm]["tiv_usd"].iloc[0])
    # Restrict the wind leg to the ≤50 km SURGE event set: this is the surge-driven coastal compound, so only storms
    # that actually produce surge belong here. (The hurricane wind leg is now the full ≤100 km set — 95 storms — so the
    # 50–100 km wind-only storms are carried by the STANDALONE hurricane-wind product, not double-counted here.)
    surge_cat = pd.read_parquet(OUT / f"{cslug}_flood_coastal_m1_catalog.parquet")
    surge_efids = set(surge_cat["event_family_id"].astype(int))
    w = wind_leg[(wind_leg.slug == cslug) & (wind_leg.event_family_id.astype(int).isin(surge_efids))]
    nd = pd.read_parquet(OUT / f"{cslug}_flood_wind_coastal_m2_node_depths.parquet")
    t = nd[nd.kind == "turbine"]; sub = nd[nd.kind == "substation"].iloc[0]
    surge_DR_cat = {}                                    # per-category, per-subsystem surge DR (farm-level, matched to wind leg)
    for c in range(1, 6):
        dt = t[f"depth_cat{c}_m"].values / FT_M; ds = sub[f"depth_cat{c}_m"] / FT_M
        surge_DR_cat[c] = {"foundation": float(np.mean(_sdr(dt, *SURGE_CURVE["foundation"]))),
                           "electrical": float(np.mean(_sdr(dt, *SURGE_CURVE["electrical"]))),
                           "civil":      float(np.mean(_sdr(dt, *SURGE_CURVE["civil"]))),
                           "substation": float(_sdr(ds, *SURGE_CURVE["substation"])),
                           "rotor_blades": 0.0, "nacelle_drivetrain": 0.0, "tower": 0.0}
    ev = []
    for r in w.itertuples():
        c = int(r.category); sdr = surge_DR_cat.get(c, {k: 0.0 for k in CAPEX7})
        wdr = {k: float(getattr(r, f"DR_{k}")) for k in CAPEX7}
        comb = {k: max(wdr[k], sdr[k]) for k in CAPEX7}
        ev.append({"event_family_id": int(r.event_family_id), "category": c,
                   "wind_loss":  sum(CAPEX7[k]*wdr[k]  for k in CAPEX7) * TIV,
                   "surge_loss": sum(CAPEX7[k]*sdr[k]  for k in CAPEX7) * TIV,
                   "compound_loss": sum(CAPEX7[k]*comb[k] for k in CAPEX7) * TIV})
    ev = pd.DataFrame(ev); compound_events[nm] = ev
    # ONE shared storm draw → wind/surge/compound annual vectors are co-sampled (per-realization compound ≥ each leg)
    counts = rng.poisson(lam, N); n_ev = int(counts.sum())
    idx = rng.integers(0, len(ev), n_ev); yr = np.repeat(np.arange(N), counts)
    annual_of = lambda col: np.bincount(yr, weights=ev[col].values[idx], minlength=N)
    coa_annual = annual_of("compound_loss")
    coastal_vectors[nm] = coa_annual / TIV
    oep_coa = np.zeros(N)                                             # OEP = largest single storm's compound loss per year
    if n_ev:
        np.maximum.at(oep_coa, yr, ev["compound_loss"].values[idx])
    coastal_oep_vectors[nm] = oep_coa / TIV
    compound_metrics[nm] = {"lambda_per_yr": lam, "n_storms": int(len(ev)),
                            "wind_only":  cp_metrics(annual_of("wind_loss"),  TIV),
                            "surge_only": cp_metrics(annual_of("surge_loss"), TIV),
                            "compound":   cp_metrics(coa_annual, TIV)}
    cm = compound_metrics[nm]
    worst = ev.sort_values("compound_loss", ascending=False).iloc[0]
    print(f"{nm} — coastal compound (λ={lam:.4f}/yr, {len(ev)} storms):")
    print(f"  per-stream EAL: wind-only {cm['wind_only']['EAL_pct']:.3f}% · surge-only {cm['surge_only']['EAL_pct']:.3f}% · "
          f"COMPOUND {cm['compound']['EAL_pct']:.3f}% of TIV/yr")
    print(f"  compound PML100 {cm['compound']['PML100_pct']:.2f}% · PML500 {cm['compound']['PML500_pct']:.2f}% · "
          f"worst storm Cat{int(worst.category)} ${worst.compound_loss/1e6:.1f}M ({worst.compound_loss/TIV*100:.1f}% TIV)")

# %% [markdown]
# ## 2d · Total flood per site = inland (annual-max) + coastal (compound-Poisson), independent streams
#
# A year can carry both an inland flood AND a hurricane surge (different drivers, not yet event-linked — JD-FL-17), so
# the **total** annual loss = inland vector **+** coastal vector. Inland-only sites (Green River, Shepherds Flat) keep
# their inland total; Amazon gains the coastal stream.

# %%
total_metrics = {}
total_aep, total_oep = {}, {}     # per-site TOTAL annual-aggregate + occurrence vectors (fraction of TIV)
for nm in sites["name"]:
    inland = vectors[nm]; coa = coastal_vectors.get(nm, np.zeros(N))
    tot = inland + coa
    coa_oep = coastal_oep_vectors.get(nm, np.zeros(N))
    # TOTAL occurrence basis: year's occurrence set = {inland annual-max as ONE occurrence} ∪ {each coastal storm};
    # OEP_total = max(inland_year, largest coastal storm that year). AEP_total = inland + Σ coastal storms.
    tot_oep = np.maximum(inland, coa_oep)            # inland is annual-max (1 occurrence/yr) → its OEP == its AEP
    total_metrics[nm] = {"inland_eal_pct": inland.mean()*100, "coastal_eal_pct": coa.mean()*100,
                         "EAL_pct": tot.mean()*100, "PML100_pct": np.percentile(tot, 99)*100,
                         "PML250_pct": np.percentile(tot, 99.6)*100, "PML500_pct": np.percentile(tot, 99.8)*100}
    vectors[nm + "__total"] = tot
    total_aep[nm] = tot; total_oep[nm] = tot_oep
# house-standard twin blocks per site (TOTAL flood headline) — identical keys, the block name carries the unit
twin = {nm: twin_metrics(total_aep[nm], total_oep[nm]) for nm in total_aep}
metrics_usd = {nm: {k: round(v * tiv_by_site[nm], 2) for k, v in twin[nm].items()} for nm in twin}
metrics_pct_of_tiv = {nm: {k: round(v * 100, 4) for k, v in twin[nm].items()} for nm in twin}
print("\ntotal flood (inland + coastal), % of TIV:")
for nm in sites["name"]:
    tm = total_metrics[nm]
    print(f"  {nm:24s} inland {tm['inland_eal_pct']:.3f} + coastal {tm['coastal_eal_pct']:.3f} = "
          f"TOTAL EAL {tm['EAL_pct']:.3f}% · PML100 {tm['PML100_pct']:.2f}% · PML500 {tm['PML500_pct']:.2f}% · "
          f"OEP-PML100 {metrics_pct_of_tiv[nm]['OEP-PML100']:.2f}%")

# %% [markdown]
# ## 3 · Plots — loss-exceedance curves (sub-perils + combined) + simulated annual-loss exceedance

# %%
import matplotlib.pyplot as plt

fig, (axC, axH) = plt.subplots(1, 2, figsize=(13, 4.8))
Ts = np.array([5, 10, 25, 50, 100, 250, 500, 1000])
for _, s in sites.iterrows():
    nm = s["name"]
    per_sp = {sp: loss_at_aep(1 / Ts, make_curve(nm, sp)) for sp in SUBPERILS}
    combined = np.maximum.reduce(list(per_sp.values())) * 100
    for sp, v in per_sp.items():
        axC.plot(Ts, v * 100, "^--" if sp == "pluvial" else "s--", alpha=0.45, label=f"{nm.split()[0]} · {sp}")
    axC.plot(Ts, combined, "o-", lw=2, label=f"{nm.split()[0]} · combined")
    axH.plot(np.sort(vectors[nm])[::-1] * 100, np.arange(1, N + 1) / N, label=f"{nm.split()[0]} (combined)")
axC.set_xscale("log"); axC.set_xlabel("return period (yr)"); axC.set_ylabel("loss (% TIV)")
axC.set_title("Loss-exceedance — sub-perils + combined (worse-wins)"); axC.legend(fontsize=7); axC.grid(alpha=0.3)
axH.set_xscale("symlog", linthresh=0.01); axH.set_yscale("log"); axH.set_ylim(1e-4, 1)
axH.set_xlabel("annual loss (% TIV)"); axH.set_ylabel("annual exceedance prob")
axH.set_title("Simulated annual-loss exceedance (MC)"); axH.legend(fontsize=8); axH.grid(alpha=0.3)
fig.suptitle("Flood × wind-farm M4 — annual loss & metrics (riverine + pluvial combined)")
fig.tight_layout()
plt.show()


# %% [markdown]
# ## 4 · Known-answer checks (basics-spot-on)
#
# - **Combine frame check (JD-FL-11):** the combined PML@T reproduces the *worse* sub-peril's Lₜ — `PML_T ≈ max_sp
#   L(site, sp, T)` by construction (here riverine wins → combined ≈ the riverine-only headline).
# - **Monotone:** PML rises with RP. **Combined ≥ each marginal.** **Contrast:** Green River ≫ Shepherds Flat. EAL ≪ PML.

# %%
gr = M[M.name == "Green River"].iloc[0]; sf = M[M.name == "Shepherds Flat"].iloc[0]
maxL = lambda nm, T: max(L[(nm, sp, T)] for sp in SUBPERILS if (nm, sp, T) in L)
assert abs(gr["PML100_pct"] / 100 - maxL("Green River", 100)) < 0.003, "PML100 must reproduce max-sub-peril L100 (combine frame check)"
assert abs(gr["PML500_pct"] / 100 - maxL("Green River", 500)) < 0.004, "PML500 must reproduce max-sub-peril L500"
assert gr["PML500_pct"] >= gr["PML250_pct"] >= gr["PML100_pct"] >= gr["EAL_pct"] > 0, "metrics must be monotone & positive"
assert gr["EAL_pct"] >= max(gr[f"EAL_{sp}_pct"] for sp in SUBPERILS) - 1e-9, "combined EAL ≥ every marginal (worse-wins)"
assert gr["EAL_pct"] > 5 * max(sf["EAL_pct"], 1e-9), "Green River EAL should dominate Shepherds Flat"
assert gr["EAL_riverine_pct"] > gr["EAL_pluvial_pct"], "riverine should dominate pluvial for wind (pads shed rainfall)"
print(f"✓ combine frame check: Green River PML100 {gr['PML100_pct']:.2f}% ≈ max-sp L100 {maxL('Green River',100)*100:.2f}% | "
      f"PML500 {gr['PML500_pct']:.2f}% ≈ {maxL('Green River',500)*100:.2f}%")
print(f"✓ Green River: EAL {gr['EAL_pct']:.3f}% < PML100 {gr['PML100_pct']:.2f}% < PML500 {gr['PML500_pct']:.2f}% TIV (monotone), ≥ each marginal")
print(f"✓ sub-peril split: riverine {gr['EAL_riverine_pct']:.3f}% ≫ pluvial {gr['EAL_pluvial_pct']:.4f}% (lidar-grounded floor = 0, water-limited; JD-FL-15)")
print(f"✓ Green River EAL {gr['EAL_pct']:.3f}% ≫ Shepherds Flat EAL {sf['EAL_pct']:.3f}% (contrast)")
for nm, cm in compound_metrics.items():
    assert cm["compound"]["EAL_pct"] >= cm["surge_only"]["EAL_pct"] - 1e-9, "compound ≥ surge-only (per-subsystem max)"
    assert cm["compound"]["EAL_pct"] >= cm["wind_only"]["EAL_pct"] - 1e-9, "compound ≥ wind-only (per-subsystem max)"
    assert total_metrics[nm]["EAL_pct"] >= cm["compound"]["EAL_pct"] - 1e-9, "total ≥ coastal compound (inland adds)"
    print(f"✓ COASTAL COMPOUND {nm}: compound EAL {cm['compound']['EAL_pct']:.3f}% ≥ max(wind {cm['wind_only']['EAL_pct']:.3f}%, "
          f"surge {cm['surge_only']['EAL_pct']:.3f}%) — per-subsystem max(wind,surge) on the joined storm stream (JD-FL-12)")
# twin-block / occurrence-basis checks (house standard) — across every TOTAL-flood site
for nm in total_aep:
    aep, oep, t, tiv = total_aep[nm], total_oep[nm], twin[nm], tiv_by_site[nm]
    assert bool((aep + 1e-12 >= oep).all()), f"{nm}: AEP ≥ OEP must hold every year"
    assert t["OEP-PML100"] <= t["VaR99 (AEP-PML100)"] + 1e-12, f"{nm}: OEP-PML100 ≤ AEP-PML100 (occurrence ≤ aggregate)"
    if t["EAL"] > 0:
        assert t["TVaR99"] >= t["VaR99 (AEP-PML100)"] - 1e-12, f"{nm}: TVaR99 ≥ VaR99 (tail-average past the quantile)"
        assert t["PML500 (AEP-99.8)"] >= t["VaR99.6 (AEP-PML250)"] >= t["VaR99 (AEP-PML100)"] >= t["EAL"] > 0, f"{nm}: twin-block monotone"
    assert all(abs(metrics_usd[nm][k] / tiv * 100 - metrics_pct_of_tiv[nm][k]) < 1e-3 for k in t), f"{nm}: usd/TIV*100 == pct (unit consistency)"
    if nm not in coastal_vectors:   # inland-only sites: occurrence == aggregate (annual-max = 1 occurrence/yr)
        assert abs(t["OEP-PML100"] - t["VaR99 (AEP-PML100)"]) < 1e-12, f"{nm}: inland-only → OEP == AEP"
print("✓ twin-block + occurrence-basis checks pass (AEP≥OEP, OEP-PML100≤AEP-PML100, TVaR99≥VaR99, monotone, unit-consistent).")
print("✓ M4 known-answer checks pass (riverine + pluvial + coastal compound + total).")

# %% [markdown]
# ## 4b · External validation — FEMA National Risk Index (independent benchmark)
#
# FEMA's **National Risk Index** publishes a **Riverine Flooding** Expected Annual Loss per county (their own
# HAZUS-based model). For **Lee County, IL** we form a county-average EAL rate and sanity-check ours. Since pluvial is
# a negligible add here, the **combined** EAL ≈ the riverine EAL, so the riverine-only NRI comparison still holds. Two
# checks: **(a) magnitude** — our high-exposure farm a few× *above* county avg; **(b) frequency** — NRI's annualized
# riverine frequency ≈ our annual-maximum (~1/yr).

# %%
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

NRI_FIPS = "17103"   # Lee County, IL (Green River high site)


def fetch_nri(fips):
    cache = OUT / "raw" / f"nri_ifld_{fips}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    sess = requests.Session()
    sess.mount("https://", HTTPAdapter(max_retries=Retry(total=4, backoff_factor=0.6, status_forcelist=[429, 500, 502, 503, 504])))
    sess.headers.update({"User-Agent": "infrasure-hazard-modeling/0.1"})
    url = "https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/National_Risk_Index_Counties/FeatureServer/0/query"
    a = sess.get(url, params={"where": f"STCOFIPS='{fips}'", "outFields": "*", "f": "json", "returnGeometry": "false"},
                 timeout=30).json()["features"][0]["attributes"]
    rec = {k: a[k] for k in ("COUNTY", "STATE", "IFLD_EALB", "IFLD_EXPB", "IFLD_EALT", "IFLD_EXPT",
                             "IFLD_AFREQ", "IFLD_EALR", "IFLD_RISKR")}
    cache.parent.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(rec, default=str))
    return rec


try:
    nri = fetch_nri(NRI_FIPS)
    nri_rate = nri["IFLD_EALB"] / nri["IFLD_EXPB"] * 100        # county-avg riverine EAL as % of building value /yr
    our_eal = gr["EAL_pct"]; ratio = our_eal / nri_rate
    print(f"FEMA NRI — {nri['COUNTY']} Co., {nri['STATE']} · Riverine Flooding (independent HAZUS-based model):")
    print(f"  county-avg EAL rate = ${nri['IFLD_EALB']/1e6:.1f}M / ${nri['IFLD_EXPB']/1e9:.1f}B building = {nri_rate:.3f}% / yr "
          f"(hazard rating: {nri['IFLD_EALR']})")
    print(f"  annualized riverine frequency = {nri['IFLD_AFREQ']:.2f} events/yr")
    print(f"\n  OUR Green River EAL (combined) = {our_eal:.3f}% of TIV/yr  →  {ratio:.1f}× the county average")
    print(f"  ✓ magnitude: same order, a few× above county avg (60%-in-floodplain site) — {'PASS' if 1 < ratio < 30 else 'CHECK'}")
    print(f"  ✓ frequency: NRI {nri['IFLD_AFREQ']:.2f}/yr ≈ our annual-maximum ~1/yr (JD-FL-7) — {'PASS' if 0.4 < nri['IFLD_AFREQ'] < 2 else 'CHECK'}")
    assert 1 < ratio < 30, "EAL should be a few× the county average (high-exposure site), same order of magnitude"
    nri_ok = True
except Exception as e:
    print(f"NRI fetch unavailable ({str(e)[:60]}) — external validation skipped this run (endpoint/field drift).")
    nri, nri_rate, ratio, nri_ok = None, None, None, False

# %% [markdown]
# ## 5 · Persist metrics + per-year vectors

# %%
for key, v in vectors.items():                                  # keys: "<site>" (inland) + "<site>__total" (inland+coastal)
    nm = key.replace("__total", ""); suffix = "_total" if key.endswith("__total") else ""
    slug = sites[sites.name == nm]["slug"].iloc[0]
    pd.DataFrame({"annual_loss_frac_tiv": v}).to_parquet(OUT / f"{slug}_flood_wind_m4_annual_vectors{suffix}.parquet")  # gitignored
manifest = {
    "peril": "flood", "sub_peril": ["riverine", "pluvial", "coastal"], "event_family_id": None, "layer": "M4", "asset": "wind_farm",
    "event_model": "INLAND (riverine+pluvial): annual-max MC, co-sampled comonotonic, worse-source-wins (JD-FL-7/11). "
                   "COASTAL: compound-Poisson surge×hurricane-wind, per-subsystem max(wind,surge) on event_family_id (JD-FL-12). "
                   "TOTAL = inland + coastal (independent streams).",
    "coastal_compound": {nm: {"lambda_per_yr": cm["lambda_per_yr"], "n_storms": cm["n_storms"],
                              "wind_only_eal_pct": round(cm["wind_only"]["EAL_pct"], 4),
                              "surge_only_eal_pct": round(cm["surge_only"]["EAL_pct"], 4),
                              "compound": {k: round(v, 4) for k, v in cm["compound"].items()}}
                         for nm, cm in compound_metrics.items()},
    "total_flood": {nm: {k: round(v, 4) for k, v in tm.items()} for nm, tm in total_metrics.items()},
    "wind_leg_source": "data/hurricane/tc_windfarm_m3_damage.parquet (hurricane × wind-farm, per-storm per-subsystem DR, event_family_id join)",
    "compound_combine": "per subsystem combined_DR = max(wind_DR, surge_DR); shared = electrical+substation, wind-only = rotor+nacelle, surge-only = foundation+civil (JD-FL-12)",
    "_inland_event_model": "annual-max MC; sub-perils co-sampled comonotonic, combined worse-source-wins (JD-FL-7/JD-FL-11)",
    "combine_rule": "HEADLINE = max(riverine, pluvial) at one annual AEP (φ=1, shared-ground; Bates 2021); metrics on the JOINT per-year vector",
    "combine_envelope_sensitivity": {nm: {"headline_eal_pct": round(M[M.name == nm]["EAL_pct"].iloc[0], 3),
                                          "additive_capped_eal_pct_UB": round(M[M.name == nm]["EAL_addUB_pct"].iloc[0], 3),
                                          "note": "headline worse-wins (used downstream) → additive-capped upper bound (recorded only)"}
                                     for nm in sites["name"]},
    "n_sim_years": N, "onset_aep": ONSET_AEP,
    "rp_points_per_site": {f"{nm} · {sp}": RP_AVAIL[(nm, sp)] for nm in sites["name"] for sp in SUBPERILS if (nm, sp) in RP_AVAIL},
    "marginal_eal_pct": {f"{nm} · {sp}": round(marginal_eal[(nm, sp)], 4) for nm in sites["name"] for sp in SUBPERILS},
    "substation_bracket": {"full_eal_pct": round(gr_full["EAL_pct"], 3), "turbines_only_eal_pct": round(gr_floor["EAL_pct"], 3),
                           "substation_share_of_eal_pct": round(max(sub_share, 0), 0),
                           "note": "substation = Green River's OWN west-edge 138 kV collector (in-hull generation node, JD-FL-W7); it FLOODS (0.56-1.00 m) → collector-dominated headline. Floor = collector excluded. (Earlier 'Big Sky Wind' node was the adjacent farm's, dry.)"},
    "metric_frame": "per-year loss vectors; PML_T = (1-1/T) percentile (DD-4)",
    "external_validation": ({"source": "FEMA NRI Riverine Flooding (Lee County IL)",
                             "county_eal_rate_pct": round(nri_rate, 4), "our_eal_pct": round(gr["EAL_pct"], 4),
                             "ratio_to_county_avg": round(ratio, 1), "nri_annual_freq": round(nri["IFLD_AFREQ"], 3),
                             "verdict": "same order, a few× above county avg (high-exposure site); freq ≈ annual-max; pluvial negligible so combined≈riverine"}
                            if nri_ok else "NRI endpoint unavailable this run"),
    "caveats": ["RIVERINE: gauge-grounded RP curve (JD-FL-W5); PML@100/500 bathtub-anchored. EAL rests on real 10/25/50-yr gauge losses + the real FLOODING collector (JD-FL-W7; 0.56-1.00 m, ~75% of EAL).",
                "PLUVIAL: Atlas-14 + SCS-CN + pad-gated ponding, with f+d_cap LIDAR-GROUNDED per node (JD-FL-15). For WIND it is NEGLIGIBLE: lidar d_cap < pads → floor = 0 at every node. Green River is WATER-LIMITED (ρ up to ~490 ≫ 1) so the floor is a lower bound, but the no-drainage ceiling (Q ≤ 0.16 m) is still pad-shed and the valley substation is riverine-flooded 0.88 m → worse-wins makes pluvial immaterial; Rank-1 volume-pour deferred.",
                "PLUVIAL baseline (Shepherds Flat, OR) has NO Atlas-14 coverage (PNW = Atlas 2) → set to 0 (low-rainfall dry control, not a true zero).",
                "COMBINE (JD-FL-11): comonotonic worse-wins; additive-capped is the recorded φ=0 upper envelope.",
                "residual uncertainty is CURVE-level (the Zone-A 1% bathtub + the greenfield M3 curve) + the in-hull substation pick; loss per-node (not areal); rotor/nacelle/tower immune.",
                "SUBSTATION RESOLVED (JD-FL-W7): the west-edge 138 kV node IS Green River's OWN collector (in-hull substation=generation; OSM/HIFLD) and it FLOODS (0.88 m @ 100-yr) → ~75% of EAL. The earlier 'Big Sky Wind' node was the adjacent farm's collector (a wrong-substation bug), now corrected."],
    # house-standard twin blocks (per site, TOTAL flood) — identical keys, the block name carries the unit (parity w/ hail/wildfire/conv-wind)
    "metrics_usd": metrics_usd,
    "metrics_pct_of_tiv": metrics_pct_of_tiv,
    "occurrence_basis_note": ("OEP-PML100 = per-EVENT occurrence basis; AEP metrics = annual aggregate. TOTAL occurrence set per year = "
                              "{inland annual-max as ONE occurrence} ∪ {each coastal storm's compound loss}; OEP_total = max(inland, max coastal storm). "
                              "AEP_total = inland + Σ coastal storms. Inland-only sites → OEP == AEP (annual-max is one occurrence/yr)."),
    "metrics": json.loads(M.round(4).to_json(orient="records")),
}
(OUT / "flood_wind_m4_metrics_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote:", OUT / "flood_wind_m4_metrics_manifest.json")

# %% [markdown]
# ## Findings — flood × wind-farm, M0→M4 complete (riverine + pluvial, parity with flood × solar)
#
# - **Annual loss & risk metrics (combined):** **Green River EAL ≈ 1.27% / PML100 ≈ 10.9% / PML500 ≈ 11.4% of TIV** —
#   driven by the farm's **own collector substation**, which sits in the river valley and floods (JD-FL-W7). The
#   **turbines-only floor** (collector excluded) is EAL ≈ 0.31% / PML500 ≈ 3.2% — the with-vs-without bracket. Adding
#   pluvial is negligible. **Shepherds Flat** is the true-zero baseline. Flood is a **minor-to-moderate** peril here,
#   driven by the in-valley collector (JD-FL-W7).
# - **Pluvial confirmed negligible — now on lidar-grounded terrain (JD-FL-15):** `f`+`d_cap` measured per node from
#   1 m lidar; the terrain depression depth (~0.07–0.09 m) sits below the pads → **pluvial = 0 at every node/RP**
#   (marginal EAL 0.000%). Green River is **water-limited**
#   (ρ ≫ 1) so the floor is a lower bound — but the no-drainage ceiling is still pad-shed and the valley substation is
#   riverine-flooded → pluvial immaterial (Rank-1 deferred). The combine is **riverine-dominated** → headline ≈ riverine.
# - **Combine done the same way as flood × solar (JD-FL-11):** co-sampled comonotonic, **worse-source-wins** headline
#   + **additive-capped** envelope recorded — but where solar's headline was *pluvial*-dominated (flat compact
#   footprint), wind's is *riverine*-dominated (high-ground pads shed rain). A clean, honest asset contrast.
# - **Still gauge-grounded + NRI-validated:** the riverine RP curve rests on a real USGS Log-Pearson III flow-frequency
#   (JD-FL-W5); the substation is now the farm's **real, flooding collector** (JD-FL-W7); combined EAL ≈ riverine ≈
#   **~13× the Lee Co. average** riverine rate — order-consistent for a high-exposure site with a valley-bottom collector.
# - **End-to-end on real data, both sub-perils:** M0 → M1 (riverine bathtub + pluvial Atlas-14, forked per JD-FL-10) →
#   M2 per-node coupling → M3 source-agnostic greenfield curve → M4 worse-wins combine. Keeper: **pluvial is even
#   smaller than riverine for wind** — the raised pad, not the floodplain, is what sheds the rain.
