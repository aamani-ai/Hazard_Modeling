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
# # Hurricane — M1 catalog: tail validation of the 3-second-gust catalog (the second opinion)
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Layer:** M1 (catalog validation)
#
# **Magnitude metric:** the **3-second peak gust (mph)** — this notebook validates the *tail* of that magnitude (the
# rare, severe gusts that drive PML/VaR). *(Surge/rain = flood's `[C]`/`[F]`, not modeled here.)*
#
# **Data source:** the frozen M1 catalog (`tc_m1_catalog.parquet`) under test; **ASCE 7-22** design-wind speeds (3-s
# gust @ 33 ft Exposure C, mph) from the public ASCE Hazard Tool ImageServer; NOAA **HURDAT2** hurricane track points
# and the RAFT `.nc` for the near-site observed-vs-synthetic intensity check.
#
# **What this notebook does:** independently checks the part of the catalog that matters most and is hardest to trust —
# the **extreme tail**. It builds the catalog's return-period gust curve `T(g) = 1 / (λ·P(gust > g | event))` and
# compares it against **two independent opinions**, neither of which shares RAFT's method:
#
# 1. **ASCE 7-22 design-wind speeds** — the US building-code wind standard, which along the coast derive from a
#    separate, peer-reviewed, code-adopted engineering hurricane model built to nail the rare tail. Independent of
#    RAFT; reported as the **3-s gust @ 33 ft, Exposure C** — our exact basis.
# 2. **The observed record** — real HURDAT2 storm intensities near the site (no model at all).
#
# It reports the max deviation over the resolvable return-period range, runs acceptance checks, and persists the
# verdict (`tc_m1_tail_validation_manifest.json`). STORM is deliberately not used as the cross-check: it is a cousin
# of RAFT (synthetic resampling + empirical return periods) and likely shares the same tail blind spot, so agreement
# could be false comfort ([JD-TC-8](../../../docs/plans/hurricane/decisions.md)). This step validates the *frozen* M1
# catalog **before** M2–M4 read it, so a low tail can't silently propagate to the headline PML.

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import xarray as xr

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"
RAW = DATA / "raw"
KT_TO_MPH = 1.150779
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **Our M1 catalog** (`data/hurricane/tc_m1_catalog.parquet`) — the thing under test (per-site 3-s gusts).
# - **ASCE 7-22 design-wind speeds** — independent engineering hurricane model; public ASCE Hazard Tool ImageServer
#   (`gis.asce.org/.../w2022_mri{MRI}`), 3-s gust @ 33 ft Exposure C, **mph**; responses **cached** to `raw/asce_*.json`.
# - **HURDAT2 hurricane track points** (from [M0/02](../m0_input_data/02_landfall_record.ipynb)) + the **RAFT `.nc`**
#   (for near-site observed-vs-synthetic intensity). **Reproducibility:** the verdict persists to
#   `data/hurricane/tc_m1_tail_validation_manifest.json`.

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-10** validate the catalog tail against **independent** sources — **ASCE** (chosen over STORM, a RAFT cousin
# with the same blind spot) + the observed record · **ATC-6/7** the gust factor / Holland B are corroborated *by* this
# check (RP gusts land on ASCE) · catalog resolves to **~1,300-yr** only (PML trustworthy to ~700–1,000 yr; deeper not validated). Full register:
# [`assumptions.md`](../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · Our catalog's return-period gust curve
#
# The return period of a gust `g` at the site is `T(g) = 1 / (λ · P(gust > g | event))`, where `λ` is the calibrated
# annual event rate (JD-TC-8) and `P` comes from the empirical severity distribution (the per-storm peak gusts). We
# can only resolve `T` up to the rarest single storm in the catalog — beyond that is extrapolation, flagged.

# %%
cat = pd.read_parquet(DATA / "tc_m1_catalog.parquet")
summ = pd.read_parquet(DATA / "tc_m1_site_summary.parquet")
hi = summ[summ.role.str.startswith("proving")].iloc[0]
SITE = hi["site"]; LAM = float(hi["lambda_per_yr"])
g = np.sort(cat[cat.site == SITE]["peak_gust_3s_mph"].values)
n = len(g)
T_MAX_RESOLVABLE = 1.0 / (LAM * (1.0 / n))
print(f"site: {SITE} · λ={LAM:.3f}/yr · {n} severity samples · "
      f"catalog resolves return periods up to ~{T_MAX_RESOLVABLE:.0f} yr")

def our_rp_gust(T):
    P = 1.0 / (LAM * T)                       # exceedance prob per event
    if P < 1.0 / n:                           # beyond the rarest storm → cannot resolve
        return np.nan
    return float(np.quantile(g, 1.0 - P))

# %% [markdown]
# ## 2 · Second opinion A — ASCE 7-22 (independent engineering hurricane model)
#
# Public ASCE Hazard Tool ImageServer backend (`w2022_mri{MRI}`) — basic wind speed (3-s gust, Exposure C, mph) at
# the site, by mean recurrence interval (= return period). No auth. Cached to `raw/`.

# %%
ARC = "https://gis.asce.org/arcgis/rest/services/ASCE722"
UA = {"User-Agent": "Mozilla/5.0 (hazard_modeling tail-validation)"}
MRIS = [100, 300, 700, 1700, 3000]

def asce_gust(lon, lat, mri):
    cache = RAW / f"asce_w2022_mri{mri}_{lat:.4f}_{lon:.4f}.json"
    if cache.exists():
        j = json.loads(cache.read_text())
    else:
        p = {"geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
             "geometryType": "esriGeometryPoint", "returnGeometry": "false", "f": "json"}
        j = requests.get(f"{ARC}/w2022_mri{mri}/ImageServer/identify", params=p, headers=UA, timeout=40).json()
        RAW.mkdir(parents=True, exist_ok=True); cache.write_text(json.dumps(j))
    v = j.get("value")
    return None if v in (None, "", "NoData") else round(float(v), 1)

asce = {T: asce_gust(hi["lon"], hi["lat"], T) for T in MRIS}
print(f"ASCE 3-s gust (Exposure C, mph) at {SITE}:")
for T, v in asce.items():
    print(f"  {T:>5}-yr : {v}")

# %% [markdown]
# ## 3 · The comparison — does our tail match the independent authority?

# %%
rows = []
for T in MRIS:
    ours = our_rp_gust(T); a = asce[T]
    diff = (ours - a) if (ours == ours and a is not None) else np.nan
    pct = (100 * diff / a) if (diff == diff and a) else np.nan
    rows.append({"RP_yr": T, "our_gust_mph": round(ours, 0) if ours == ours else np.nan,
                 "asce_gust_mph": a, "diff_mph": round(diff, 0) if diff == diff else np.nan,
                 "diff_pct": round(pct, 1) if pct == pct else np.nan})
comp = pd.DataFrame(rows)
print(comp.to_string(index=False))
resolvable = comp.dropna(subset=["our_gust_mph"])
max_abs_pct = resolvable["diff_pct"].abs().max()
print(f"\nover the resolvable range (≤ ~{T_MAX_RESOLVABLE:.0f} yr): max |difference| = {max_abs_pct:.1f}%")
print("→ our catalog tail agrees with ASCE (independent) — NOT silently low" if max_abs_pct <= 12
      else "→ ⚠ our tail diverges from ASCE — investigate")

# %% [markdown]
# ## 4 · Second opinion B — the observed record (real storms, no model)
#
# RAFT's near-site intensity distribution vs the **observed** HURDAT2 intensities near the site (storms passing
# within 100 km, peak `vmax`). Real data is the ultimate check; its only weakness is the small sample.

# %%
ds = xr.open_dataset(RAW / "RAFT.NA.v20231016.nc", engine="h5netcdf")
def hav(la, lo, LA, LO):
    R = 6371.0; p1 = np.radians(la); p2 = np.radians(LA)
    a = np.sin(np.radians(LA-la)/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(np.radians(LO-lo)/2)**2
    return 2*R*np.arcsin(np.sqrt(a))
d = hav(hi["lat"], hi["lon"], ds["lat"].values, ds["lon"].values)
vm = ds["vmax"].values
raft_near = np.nanmax(np.where((d <= 100) & ~np.isnan(vm), vm, np.nan), axis=1)
raft_near = raft_near[np.nan_to_num(raft_near) >= 64]
ot = pd.read_parquet(DATA / "tc_m0_hurdat2_tracks_hu.parquet")
od = hav(hi["lat"], hi["lon"], ot["lat"].values, ot["lon"].values)
obs_near = ot.loc[od <= 100].groupby("storm_id")["max_wind_kt"].max().values
print(f"near-site peak intensity (kt) — RAFT n={len(raft_near)} vs observed n={len(obs_near)}:")
for q in [50, 75, 90]:
    print(f"  p{q}: RAFT {np.percentile(raft_near,q):3.0f} kt   observed {np.percentile(obs_near,q):3.0f} kt")
print(f"  max: RAFT {raft_near.max():3.0f} kt   observed {obs_near.max():3.0f} kt "
      f"(single-storm extremes; small obs sample n={len(obs_near)})")
ds.close()

# %% [markdown]
# ## 5 · Known-answer / acceptance checks

# %%
checks = {
    "ASCE responded at the site (independent source live)": all(v is not None for v in asce.values()),
    "our tail agrees with ASCE within 12% over the resolvable range": max_abs_pct <= 12,
    "no systematic LOW bias (we're not consistently under ASCE)": (resolvable["diff_mph"] >= -10).all(),
    "RAFT median intensity ≈ observed (within 10 kt)": abs(np.median(raft_near) - np.median(obs_near)) <= 10,
    "catalog resolves to ≥ 500-yr (PML reportable to here)": T_MAX_RESOLVABLE >= 500,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "a tail-validation check failed"
print("\nall M1/02 tail-validation checks pass ✅")

# %% [markdown]
# ## 6 · Emit — the validation record

# %%
manifest = {
    "notebook": "hurricane/m1_catalog/02_tail_validation",
    "site": SITE, "lambda_per_yr": LAM, "n_severity_samples": int(n),
    "catalog_resolvable_rp_yr": round(float(T_MAX_RESOLVABLE), 0),
    "comparison_vs_asce": comp.to_dict(orient="records"),
    "max_abs_pct_diff_resolvable": round(float(max_abs_pct), 1),
    "observed_vs_raft_intensity_kt": {
        "raft": {f"p{q}": round(float(np.percentile(raft_near, q)), 0) for q in [50, 75, 90]} | {"max": float(raft_near.max())},
        "observed": {f"p{q}": round(float(np.percentile(obs_near, q)), 0) for q in [50, 75, 90]} | {"max": float(obs_near.max())},
    },
    "verdict": [
        f"tail VALIDATED vs ASCE (independent engineering hurricane model) within {max_abs_pct:.0f}% over 100–{T_MAX_RESOLVABLE:.0f} yr",
        "no systematic low bias — earlier 'tail runs low' concern resolved at the decision-relevant RP-gust level",
        "gust factor (1.2) independently corroborated (RP gusts land on ASCE)",
        f"LIMIT: catalog resolves only to ~{T_MAX_RESOLVABLE:.0f} yr; deeper PML (1700/3000-yr) needs extrapolation or a larger catalog",
    ],
}
(DATA / "tc_m1_tail_validation_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote", DATA / "tc_m1_tail_validation_manifest.json")

# %% [markdown]
# ## Takeaways → next
#
# - **The tail is validated, independently and in the good direction.** Our catalog's return-period gusts match
#   **ASCE** (a separate engineering hurricane model) within ~5.5% over 100–700 yr, with **no systematic low bias** —
#   resolving the M1 tail flag at the level that actually drives PML.
# - **The gust factor (1.2) is corroborated** — it lands our RP gusts on ASCE.
# - **Observed record agrees** on central intensity (RAFT median ≈ observed); the deep extreme rests on a small
#   observed sample, consistent within noise.
# - **Honest remaining limit:** the 260-storm catalog resolves only to **~1,300 yr** — so **PML is trustworthy to
#   ~700–1,000 yr; deeper return periods need extrapolation or a larger RAFT subset** (recorded for M4).
#
# **Next → M2 (coupling):** read the validated per-event site gust into the field-intensity exposure contract M3 needs.
