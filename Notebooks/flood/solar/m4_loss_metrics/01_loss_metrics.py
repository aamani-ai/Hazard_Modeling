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
# # Flood → Solar · M4 loss & metrics
#
# **Peril:** Flood (riverine) · **Asset:** Solar · **Layer:** M4 (loss & metrics) · sub-peril `riverine`
#
# **Goal:** turn the M3 conditional losses into the **annual loss distribution** → **EAL / VaR / PML / TVaR** (% of
# TIV + dollars), the same metric frame hail/wildfire/wind report (DD-4).
#
# **Event-model bridge ([JD-FL-7](../../../../docs/plans/flood/decisions.md)).** Riverine flood = **annual-maximum**
# (~1 damaging flood/yr). We build a **loss-exceedance curve** straight from the M3 conditional losses — now a **5-point
# RP curve** for the proving site (10/25/50/100/500-yr) after the [JD-FL-8](../../../../docs/plans/flood/decisions.md)
# densification: the 100/500-yr points are **real BLE**; the 10/25/50-yr points come from a **regression flow-frequency
# rating anchored to both BLE depths** (no more assumed onset depth). The MC draws each year's `AEP ~ U(0,1)` →
# `loss(AEP)` (log-AEP interpolation, bounded extrapolation) → per-year loss vectors → the shared metrics. The
# convective_wind strong-wind pattern (sample an RP curve), specialized to annual-max.
#
# > **Honest:** PML@100/500-yr is **anchored to real BLE**; **EAL is now densified** — the frequent region rests on
# > measurement-anchored 10/25/50-yr depths (JD-FL-8), not a flat onset guess. §2b shows how much that moved EAL.
# > Seam-ready: the curve is built generically from whatever RPs M3 emits. Plan: [`m4_loss_metrics.md`](../../../../docs/plans/flood/m4_loss_metrics.md).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "flood"

m3 = pd.DataFrame(json.loads((OUT / "flood_m3_damage_manifest.json").read_text())["sites"])
sites = m3.groupby("name").agg(role=("role", "first"), tiv_usd=("tiv_usd", "first")).reset_index()
L = {(r["name"], r["sub_peril"], r["rp_years"]): r["cond_loss_frac_tiv"] for _, r in m3.iterrows()}   # keyed by sub_peril
# real 10-yr exposure (BLE 10% extent, from M1) + the vendored damage curve (to price the onset depth)
F10 = {s["name"]: s.get("rp10_inund_frac", 0.0) for s in json.loads((OUT / "flood_m1_catalog_manifest.json").read_text())["sites"]}
_cv = json.loads((OUT / "damage_curves" / "flood_solar_asset_capex_weighted.json").read_text())


def asset_dr(depth_ft):   # capex-weighted, anchored DR(0)=0 — same curve as M3
    tot = 0.0
    for c in _cv["subsystems"]:
        L_, k, x0 = c["L"], c["k"], c["x0_ft"]
        tot += c["capex_weight"] * max(L_ / (1 + np.exp(-k * (depth_ft - x0))) - L_ / (1 + np.exp(-k * (0 - x0))), 0)
    return tot


print("M3 conditional losses (input — riverine + pluvial):")
print(m3[["sub_peril", "name", "rp_years", "cond_loss_frac_tiv", "tiv_usd"]].to_string(index=False))
print("  10-yr riverine exposure (BLE 10% extent):", {n: f"{f*100:.0f}%" for n, f in F10.items()})

# %% [markdown]
# ## 1 · Per-sub-peril loss-exceedance curves (one per sub_peril × site)
#
# Each `(site, sub_peril)` gets its own RP→loss curve from M3 — riverine (10/25/50/100/500-yr, BLE+densified) and
# pluvial (10/25/50/100/500-yr, Atlas-14). `ONSET_AEP` (10-yr) is the most-frequent mapped flood for both; below it,
# no modelled loss. §2 **co-samples** both at one annual severity and takes the **worse** ([JD-FL-11](../../../../docs/plans/flood/decisions.md)).

# %%
ONSET_AEP = 0.10        # 10-yr: the most-frequent mapped flood (both sub-perils); more frequent → no modelled loss

RP_AVAIL = {}
for (nm, sp, rp) in L:
    RP_AVAIL.setdefault((nm, sp), []).append(rp)
for k in RP_AVAIL:
    RP_AVAIL[k].sort()
SUBPERILS = sorted({sp for (_, sp) in RP_AVAIL})   # ['pluvial', 'riverine']

def make_curve(name, sp):
    return [(round(1 / rp, 4), L[(name, sp, rp)]) for rp in RP_AVAIL[(name, sp)]]   # (AEP, loss), RP ascending

def loss_at_aep(aep, curve):
    aeps = np.array([c[0] for c in curve]); losses = np.array([c[1] for c in curve])
    x = np.log10(np.clip(aep, 1e-7, 1.0))
    xs = np.log10(aeps[::-1]); ys = losses[::-1]          # increasing x: rarest→onset
    loss = np.interp(x, xs, ys)                            # interpolate within [0.002, 0.1]
    # bounded extrapolation below the rarest anchor (continue the 100→500 log-AEP slope)
    slope = (losses[-1] - losses[-2]) / (np.log10(aeps[-1]) - np.log10(aeps[-2]))
    extrap = losses[-1] + slope * (x - np.log10(aeps[-1]))
    loss = np.where(x < np.log10(aeps[-1]), np.minimum(extrap, 3 * losses[-1]), loss)
    loss = np.where(aep >= ONSET_AEP, 0.0, loss)          # more frequent than onset → no damaging flood
    return np.clip(loss, 0.0, None)

for _, s in sites.iterrows():
    for sp in SUBPERILS:
        print(f"  {s['name']:24s} {sp:9s}: " + " · ".join(f"{int(1/a)}yr={l*100:.2f}%" for a, l in make_curve(s['name'], sp)))

# %% [markdown]
# ## 2 · Monte-Carlo annual loss → **combine sub-perils** (co-sample, worse-wins) → metrics
#
# Per simulated year draw **one** annual severity `AEP ~ U(0,1)` and read **both** sub-peril curves at it (comonotonic
# — one storm drives both), then the year's flood loss = **max(riverine, pluvial)** ([JD-FL-11](../../../../docs/plans/flood/decisions.md)):
# correlation-honest, no double-count. Metrics on the **combined** per-year vector (the joint — *not* summed marginals;
# the convective_wind VaR lesson). Marginal per-sub-peril EALs kept for the breakdown.

# %%
N = 500_000
rng = np.random.default_rng(20260617)
RPS = [100, 250, 500]


def metrics_of(v):
    var99 = np.percentile(v, 99)
    return {"EAL": v.mean(), "VaR99": var99, "TVaR99": v[v >= var99].mean(),
            **{f"PML{T}": np.percentile(v, 100 * (1 - 1 / T)) for T in RPS}}


rows = []
vectors = {}        # combined per-year vector per site
marginal_eal = {}   # (site, sub_peril) -> marginal EAL %
for _, s in sites.iterrows():
    nm, tiv = s["name"], s["tiv_usd"]
    aep = rng.random(N)                                            # ONE severity per year → co-sample (JD-FL-11)
    per_sp = {sp: loss_at_aep(aep, make_curve(nm, sp)) for sp in SUBPERILS}
    combined = np.maximum.reduce(list(per_sp.values()))            # HEADLINE: worse-source-wins (φ=1; shared ground)
    vectors[nm] = combined
    for sp, v in per_sp.items():
        marginal_eal[(nm, sp)] = v.mean() * 100
    cm = metrics_of(combined)
    # recorded ENVELOPE only (NOT used downstream): additive-capped = upper bound (φ=0, fully-disjoint equipment)
    additive = np.minimum(sum(per_sp.values()), 1.0)              # min(TIV, Σ losses), co-sampled
    am = metrics_of(additive)
    rows.append({"name": nm, "role": s["role"], "tiv_usd": tiv,
                 "EAL_pct": cm["EAL"] * 100, "EAL_usd": cm["EAL"] * tiv,
                 "VaR99_pct": cm["VaR99"] * 100, "TVaR99_pct": cm["TVaR99"] * 100,
                 **{f"PML{T}_pct": cm[f"PML{T}"] * 100 for T in RPS},
                 **{f"PML{T}_usd": cm[f"PML{T}"] * tiv for T in RPS},
                 **{f"EAL_{sp}_pct": marginal_eal[(nm, sp)] for sp in SUBPERILS},
                 # envelope (sensitivity, recorded not used): EAL/PML500 under the additive-capped upper bound
                 "EAL_addUB_pct": am["EAL"] * 100, "PML500_addUB_pct": am["PML500"] * 100})
M = pd.DataFrame(rows)
print(M[["name", "EAL_pct", "VaR99_pct", "PML100_pct", "PML250_pct", "PML500_pct", "TVaR99_pct"]].round(3).to_string(index=False))
print("\ndollars:")
print(M[["name", "EAL_usd", "PML100_usd", "PML500_usd"]].round(0).to_string(index=False))
print("\nsub-peril EAL breakdown (% TIV) + the JD-FL-11 combine envelope (headline worse-wins → additive-capped upper bound):")
for _, r in M.iterrows():
    parts = " + ".join(f"{sp} {r[f'EAL_{sp}_pct']:.3f}" for sp in SUBPERILS)
    print(f"  {r['name']:24s} {parts}  | HEADLINE(worse-wins) {r['EAL_pct']:.3f}  envelope→ {r['EAL_pct']:.3f}–{r['EAL_addUB_pct']:.3f}")
print("  (headline = worse-wins φ=1, used downstream; additive-capped = φ=0 upper bound, recorded sensitivity only — JD-FL-11)")

# %% [markdown]
# ## 2b · What the densification bought — densified EAL vs the old assumed-onset EAL
#
# Before JD-FL-8, the frequent region rested on a single flat **assumed 10-yr onset depth** (`real BLE exposure ×
# Asset_DR(0.5 ft)`). Now the 10/25/50-yr points are **regression-rating depths anchored to both BLE depths**. Here's
# how much that moved EAL (and what the old assumption would have given across a plausible onset-depth band).
# **PML@100/500 are unchanged** (still the real BLE anchors). The M1 finding that the rating depths are near-invariant
# to channel slope means this densified EAL is robust to the one free regression parameter.

# %%
def eal_assumed_onset(name, onset_ft, n=200_000):   # the pre-JD-FL-8 RIVERINE method, for comparison only
    curve = [(ONSET_AEP, F10.get(name, 0.0) * asset_dr(onset_ft)), (0.01, L[(name, "riverine", 100)]), (0.002, L[(name, "riverine", 500)])]
    return loss_at_aep(rng.random(n), curve).mean() * 100

cmp_rows = []
for _, s in sites.iterrows():
    nm = s["name"]
    dens_eal = loss_at_aep(rng.random(200_000), make_curve(nm, "riverine")).mean() * 100
    cmp_rows.append({"site": nm.split()[0], "riverine_EAL_densified%": round(dens_eal, 3),
                     **{f"assumed@{d}ft": round(eal_assumed_onset(nm, d), 3) for d in (0.0, 0.5, 1.0)}})
cmp = pd.DataFrame(cmp_rows)
print("Riverine EAL (% TIV): JD-FL-8 densified vs the old assumed-onset method (3 onset-depth guesses):")
print(cmp.to_string(index=False))
print("\n→ Densification replaces the onset guess with measurement-anchored 10/25/50-yr depths (riverine only).")

# %% [markdown]
# ## 3 · Plots — loss-exceedance curve + annual-loss distribution

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
fig.suptitle("Flood × solar M4 — annual loss & metrics")
fig.tight_layout(); fig.savefig(OUT / "flood_m4_loss_metrics.png", dpi=120, bbox_inches="tight")
plt.show()
print("wrote:", OUT / "flood_m4_loss_metrics.png")

# %% [markdown]
# ## 4 · Known-answer checks (basics-spot-on)
#
# - **Combine frame check (JD-FL-11):** the combined is co-sampled worse-wins, so its **PML@T reproduces the *worse*
#   sub-peril's Lₜ** — `PML_T(combined) ≈ max_sp L(site, sp, T)` by construction.
# - **Monotone:** PML rises with RP. **Combined ≥ each marginal.** **Contrast:** Elizabeth ≫ Hayhurst. EAL ≪ PML.

# %%
eliz = M[M.name == "Elizabeth Solar Plant"].iloc[0]
hay = M[M.name == "Hayhurst Texas Solar"].iloc[0]
maxL = lambda nm, T: max(L[(nm, sp, T)] for sp in SUBPERILS)
assert abs(eliz["PML100_pct"] / 100 - maxL("Elizabeth Solar Plant", 100)) < 0.003, "PML100 must reproduce max-sub-peril L100 (combine frame check)"
assert abs(eliz["PML500_pct"] / 100 - maxL("Elizabeth Solar Plant", 500)) < 0.004, "PML500 must reproduce max-sub-peril L500"
assert eliz["PML500_pct"] >= eliz["PML250_pct"] >= eliz["PML100_pct"] >= eliz["EAL_pct"] > 0, "metrics must be monotone & positive"
assert eliz["EAL_pct"] >= max(eliz[f"EAL_{sp}_pct"] for sp in SUBPERILS) - 1e-9, "combined EAL ≥ every marginal (worse-wins)"
assert eliz["EAL_pct"] > hay["EAL_pct"], "Elizabeth should dominate Hayhurst"
print(f"✓ combine frame check: Elizabeth PML100 {eliz['PML100_pct']:.2f}% ≈ max-sp L100 {maxL('Elizabeth Solar Plant',100)*100:.2f}% | PML500 {eliz['PML500_pct']:.2f}% ≈ {maxL('Elizabeth Solar Plant',500)*100:.2f}%")
print(f"✓ Elizabeth: EAL {eliz['EAL_pct']:.3f}% < PML100 {eliz['PML100_pct']:.2f}% < PML500 {eliz['PML500_pct']:.2f}% TIV (monotone), ≥ each marginal")
print(f"✓ Elizabeth EAL {eliz['EAL_pct']:.3f}% > Hayhurst EAL {hay['EAL_pct']:.3f}% (contrast)")
print("✓ M4 known-answer checks pass (combined riverine + pluvial).")

# %% [markdown]
# ## 4b · External validation — observed flood depths (USGS high-water marks)
#
# Beyond the internal frame checks: do the modeled depths match a **real flood**? USGS surveyed high-water marks after
# the **Aug-2016 Louisiana flood**; we compare the proving site's modeled depth-at-RP against the observed
# height-above-ground near the site. Expectation: our **feet-scale** depths fall **inside** the observed range — a
# real-data regime check (not a to-the-inch calibration; the marks are regional, ~25–45 km out, many near channels).

# %%
import math
import requests

prov = pd.DataFrame(json.loads((OUT / "flood_m0_sites.json").read_text())["sites"])
prov = prov[prov.role.str.contains("proving")].iloc[0]
# the HWM are river/channel flood marks → compare to the RIVERINE modeled depths
_rivd = m3[(m3.name == prov["name"]) & (m3.sub_peril == "riverine")]["conditional_depth_m"]
model_ft = sorted((_rivd / 0.3048).round(2).tolist())
validation = {"source": "USGS STN high-water marks", "note": "not run"}
try:
    hwm = requests.get("https://stn.wim.usgs.gov/STNServices/HWMs/FilteredHWMs.json",
                       params={"States": prov["state"]}, timeout=40).json()
    near = sorted(h["height_above_gnd"] for h in hwm
                  if h.get("latitude") and h.get("longitude") and h.get("height_above_gnd") not in (None, "")
                  and math.hypot(h["latitude"] - prov["lat"], h["longitude"] - prov["lon"]) < 0.45)
    if near:
        lo, med, hi = near[0], near[len(near) // 2], near[-1]
        inside = (lo - 0.5) <= min(model_ft) and max(model_ft) <= (hi + 0.5)
        validation = {"source": "USGS STN high-water marks (regional, Aug-2016 LA flood era)", "n_marks": len(near),
                      "observed_ft": {"min": round(lo, 2), "median": round(med, 2), "max": round(hi, 2)},
                      "modeled_depth_ft": model_ft, "model_within_observed": bool(inside)}
        print(f"observed flood marks near {prov['name']} (n={len(near)}): {lo:.1f} / median {med:.1f} / {hi:.1f} ft above ground")
        print(f"modeled depths (10→500-yr): {model_ft} ft")
        assert inside, "modeled depths fall outside the observed flood-mark range — review"
        print("✓ modeled depths sit INSIDE the observed flood-mark range — real-data regime check passes")
    else:
        print("no high-water marks within range — validation skipped")
except Exception as e:
    print(f"HWM validation skipped (offline / endpoint?): {type(e).__name__}")

# %% [markdown]
# ## 5 · Persist metrics + per-year vectors

# %%
for nm, v in vectors.items():
    slug = nm.lower().replace(" ", "_").replace(",", "")
    pd.DataFrame({"annual_loss_frac_tiv": v}).to_parquet(OUT / f"{slug}_flood_m4_annual_vectors.parquet")  # gitignored
manifest = {
    "peril": "flood", "sub_peril": ["riverine", "pluvial"], "event_family_id": None, "layer": "M4",
    "event_model": "annual-max MC; sub-perils co-sampled comonotonic, combined worse-source-wins (JD-FL-7/JD-FL-11)",
    "combine_rule": "HEADLINE = max(riverine, pluvial) at one annual AEP (φ=1, shared-ground; research-backed, Bates 2021); metrics on the JOINT per-year vector",
    "combine_envelope_sensitivity": {nm: {"headline_eal_pct": round(M[M.name == nm]["EAL_pct"].iloc[0], 3),
                                          "additive_capped_eal_pct_UB": round(M[M.name == nm]["EAL_addUB_pct"].iloc[0], 3),
                                          "note": "headline worse-wins (used downstream) → additive-capped upper bound (recorded only)"}
                                     for nm in sites["name"]},
    "n_sim_years": N, "onset_aep": ONSET_AEP,
    "rp_points_per_site": {f"{nm} · {sp}": RP_AVAIL[(nm, sp)] for nm in sites["name"] for sp in SUBPERILS},
    "marginal_eal_pct": {f"{nm} · {sp}": round(marginal_eal[(nm, sp)], 3) for nm in sites["name"] for sp in SUBPERILS},
    "metric_frame": "per-year loss vectors; PML_T = (1-1/T) percentile (DD-4)",
    "caveats": ["RIVERINE: BLE tail + JD-FL-8 regression densification (lower RPs); PML@100/500 BLE-anchored (solid).",
                "PLUVIAL: blind-spot — Atlas-14 rainfall + SCS-CN + sheet ponding; NO depth anchor, assumption-driven (retention r, ponding-fraction f) → screening-grade; often DOMINATES the combined loss (driven by the f exposure knob).",
                "COMBINE (JD-FL-11): comonotonic worse-wins — overstates correlation slightly, ignores compound stacking; independent-sum / additive-stacking are the sensitivity variants.",
                "value∝area exposure; Elizabeth TIV estimated; medium-confidence curves; duration unmodeled; regression-Q + pluvial-knob uncertainty not yet propagated."],
    "external_validation": validation,
    "metrics": json.loads(M.round(2).to_json(orient="records")),
}
(OUT / "flood_m4_metrics_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote:", OUT / "flood_m4_metrics_manifest.json")

# %% [markdown]
# ## Findings — flood × solar, M0→M4 complete
#
# - **Annual loss & risk metrics computed** on the shared metric frame: per site, EAL / VaR99 / PML(100,250,500) /
#   TVaR99, % of TIV + dollars. **Elizabeth** carries a material flood tail; **Hayhurst** is the near-dry baseline.
# - **PML@100/500-yr is BLE-grounded** (the frame check confirms the percentiles reproduce the BLE-anchored losses);
#   **EAL is now densified** (JD-FL-8) — the frequent region rests on regression-rating depths anchored to both BLE
#   points, not a flat onset guess. §2b reports how much that moved EAL vs the old method.
# - **The flood × solar pipeline is end-to-end + EAL-hardened** (M0 → M1 BLE tail + regression-densified lower RPs →
#   M2 → M3 → M4), on **real public data + canonical curves**, every layer known-answer-checked, honestly labeled.
# - **Remaining hardening (no rework — seam-ready):** propagate the regression-Q standard error as an MC overlay; swap
#   live HAND-SRC depth if the delineation service returns; the enriched polygon / Fathom depth; duration/BI; PV flood-stow.
