# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Hazard (hazard 3.11)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Hurricane — M1 catalog: the per-(storm, site) 3-second-gust field (asset-independent)
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Layer:** M1 (the catalog — the peril, asset-independent)
#
# **Magnitude metric:** the **3-second peak gust (mph)** at the site, synthesized from the **Holland (1980)** wind
# field evaluated along RAFT tracks (RAFT `vmax` knots → sustained field → ×gust-factor → 3-s gust → ×1.150779 → mph).
# Carried in the manifest as `magnitude_metric` (+ `units`). *(Storm **surge** and **TC rainfall** are hurricane's
# secondary perils — sourced as flood's coastal `[C]` / pluvial `[F]` and cross-linked via `event_family_id`, not
# modeled in this hurricane cell; see [M0/01 · Source & provenance](../m0_input_data/01_raft_catalog.ipynb).)*
#
# **Data source:** RAFT North-Atlantic synthetic tracks (`RAFT.NA.v20231016.nc`, from
# [M0/01](../m0_input_data/01_raft_catalog.ipynb)) for the storm physics; NOAA **HURDAT2** hurricane track points +
# landfalls (from [M0/02](../m0_input_data/02_landfall_record.ipynb)) for the observed rate anchor and severity
# validation; the locked sites (`tc_m0_sites.json`, from [M0/03](../m0_input_data/03_site_geometry.ipynb)).
#
# **What this notebook does:** turns M0's raw RAFT tracks into **events as objects** — a storm-resolved per-site
# catalog of the 3-s peak gust, each event carrying identity (`event_family_id`). This is the **field-intensity**
# build (the footprint synthesis — track → Holland (1980) wind field → sample at the asset,
# [JD-TC-7](../../../docs/plans/hurricane/decisions.md)). For each site it finds RAFT storms whose center passes within
# 100 km at hurricane intensity (the *event*), takes each such storm's peak 3-s gust at the site (the *severity*, from
# RAFT physics), and sets the annual **rate** λ from the **observed** count of distinct HURDAT2 hurricanes passing
# within 100 km — the [JD-TC-8](../../../docs/plans/hurricane/decisions.md) split of **observed frequency × RAFT-physics
# severity** that corrects RAFT's ~71× genesis oversample. It validates RAFT severity against observed HURDAT2
# intensities near the high site and emits the catalog (`tc_m1_catalog.parquet`) + per-site summary + manifest. The
# **gust factor** (sustained → 3-s) and **Holland B** are explicit sensitivity levers
# ([ATC-6/7](../../../docs/plans/hurricane/assumptions.md)).
#
# > **What M1 emits (the contract M2 reads):** per-(storm, site) rows — `event_family_id`, `peak_gust_3s_mph`,
# > closest-approach, peak intensity — plus the calibrated annual rate `λ` per site. Event-based → feeds the shared
# > MC **directly** (no RP bridge; contrast flood). Plan: [`m1_catalog.md`](../../../docs/plans/hurricane/m1_catalog.md).

# %%
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"

# --- the levers (sensitivity-tested; ATC-6/7) ---
HOLLAND_B = 1.3        # Holland radial-decay shape (ATC-6)
GUST_FACTOR = 1.2      # 1-min sustained → 3-s gust (Durst ~1.23; ATC-7)
R_ANCHOR_KM = 100.0    # "a hurricane affects the site" = center within 100 km (matches M0 screen + observed anchor)
HUR_KT = 64.0          # hurricane intensity (Saffir-Simpson, sustained knots)
KT_TO_MPH = 1.150779
NMI_TO_KM = 1.852
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# M1 is a **build** layer — its "sources" are the M0 products + the field method:
# - **RAFT tracks** (`data/hurricane/raw/RAFT.NA.v20231016.nc`, from [M0/01](../m0_input_data/01_raft_catalog.ipynb))
#   — the storm objects (vmax/rmax/track). **Units:** vmax **knots**, rmax **nmi**.
# - **HURDAT2 hurricane track points + landfalls** (from [M0/02](../m0_input_data/02_landfall_record.ipynb)) — the
#   observed **rate anchor** (close-passage frequency) + the **severity validation** target.
# - **Locked sites** (`data/hurricane/tc_m0_sites.json`, from [M0/03](../m0_input_data/03_site_geometry.ipynb)).
# - **Method:** the **Holland (1980)** parametric radial wind profile (standard, open — e.g. CLIMADA), anchored to
#   RAFT `vmax`. **Reproducibility:** the catalog + per-site λ persist to `data/hurricane/tc_m1_*` (+ manifest).

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-6** footprint = **Holland (1980)** field, B parameterized (sensitivity lever) · **ATC-7** sustained → 3-s
# gust via a **gust factor ≈1.2** (lever) · **ATC-8** wind **knots → mph ×1.150779**; rmax **nmi → km** ·
# **ATC-9 / JD-TC-8** frequency = **observed-anchored rate × RAFT-physics severity** (the oversample fix) ·
# **ATC-10** validated vs IBTrACS/HURDAT2 landfall winds · **ATC-11** `event_family_id` active (= RAFT storm;
# cross-link to flood surge/rain). Full register: [`assumptions.md`](../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · The Holland (1980) wind field — the footprint synthesis
#
# A track is not yet a hazard at the asset. The **Holland radial profile** turns each track point into a wind field;
# we anchor it to RAFT's given **`vmax`** (the peak sustained wind, which occurs at the **radius of max wind** `Rmw`):
#
# $$ V(r) = V_{max}\,\sqrt{\;\left(\tfrac{R_{mw}}{r}\right)^{B}\exp\!\Big(1-\left(\tfrac{R_{mw}}{r}\right)^{B}\Big)} $$
#
# At `r = Rmw` it equals `vmax` (the eyewall peak); it decays outward and vanishes in the eye — the **known-answer**
# below. `B` sets the decay rate (the sensitivity lever). We evaluate `V` at the **site's distance** to every track
# point, take the **max over the storm's life** = the peak sustained wind the site felt, then **×gust-factor → 3-s
# gust** and **×1.150779 → mph** (RAFT is knots — the M0/01 unit trap).

# %%
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1); dl = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def holland_sustained(vmax_kt, rmw_km, r_km, B=HOLLAND_B):
    r = np.maximum(r_km, 1e-3)
    x = (rmw_km / r) ** B
    return vmax_kt * np.sqrt(np.clip(x * np.exp(1 - x), 0, None))

# known-answer: peak at Rmw == vmax; far field → 0; eye → 0
ka = {
    "V(Rmw) == Vmax": abs(float(holland_sustained(120, 40, 40)) - 120) < 1e-6,
    "V(far) → small": float(holland_sustained(120, 40, 600)) < 60,
    "V(eye r→0) → 0": float(holland_sustained(120, 40, 0.001)) < 1.0,
}
print("Holland known-answers:", {k: ("✅" if v else "❌") for k, v in ka.items()})
assert all(ka.values())

# %% [markdown]
# ## 2 · Load the inputs — RAFT tracks, the locked sites, the observed landfalls

# %%
ds = xr.open_dataset(DATA / "raw" / "RAFT.NA.v20231016.nc", engine="h5netcdf")
lat, lon = ds["lat"].values, ds["lon"].values            # (storms, steps)
vmax_kt = ds["vmax"].values
rmw_km = ds["rmax"].values * NMI_TO_KM
storm_id = ds["storm_ID"].values
n_storms = ds.sizes["storms"]

sites = json.load(open(DATA / "tc_m0_sites.json"))["sites"]
# observed HURDAT2 hurricane-intensity TRACK POINTS (close-passage rulebook — matches RAFT's "center within 100 km",
# not just landfalls; fixes the different-rulebooks gap). Each storm counted once if it passes within 100 km.
obs_tracks = pd.read_parquet(DATA / "tc_m0_hurdat2_tracks_hu.parquet")
land_hu = pd.read_parquet(DATA / "tc_m0_hurdat2_landfalls.parquet")    # landfalls kept for the severity cross-check
land_hu = land_hu[land_hu["max_wind_kt"] >= HUR_KT].reset_index(drop=True)
RECORD_YEARS = 2023 - 1851 + 1
print(f"RAFT: {n_storms:,} storms · sites: {[s['name'] for s in sites]}")
print(f"HURDAT2: {len(obs_tracks):,} hurricane-intensity track points ({obs_tracks['storm_id'].nunique()} storms) "
      f"over {RECORD_YEARS} yr · {len(land_hu)} hurricane landfalls")

# %% [markdown]
# ## 3 · Sample the field at each site + 🔴 calibrate frequency to the observed record (JD-TC-8)
#
# For each site: (a) find RAFT storms whose **center passes within 100 km at hurricane intensity** (the *event*);
# (b) build the Holland field and take each such storm's **peak 3-s gust at the site** (the *severity*, from RAFT
# physics); (c) set the annual **rate** from the **observed** count of distinct HURDAT2 hurricanes **passing within
# 100 km** (same rulebook as severity — offshore brushes count; not landfalls-only, not RAFT's oversampled count).
# This is the [JD-TC-8](../../../docs/plans/hurricane/decisions.md) split:
# **observed frequency × RAFT-physics severity** — the only honest way to use an oversampled synthetic catalog.

# %%
catalog_rows = []
site_summ = []
for s in sites:
    d = haversine_km(s["lat"], s["lon"], lat, lon)                 # (storms, steps) km to site
    near_hur = (d <= R_ANCHOR_KM) & (vmax_kt >= HUR_KT)           # hurricane-intensity center within 100 km
    is_anchor = near_hur.any(axis=1)
    # severity: peak 3-s gust at the site over each anchor storm's track
    gust = holland_sustained(vmax_kt, rmw_km, d) * GUST_FACTOR * KT_TO_MPH
    gust = np.where(np.isnan(gust), 0.0, gust)
    peak_gust = np.where(is_anchor, gust.max(axis=1), 0.0)
    # closest approach + peak intensity for the catalog
    d_safe = np.where(np.isnan(d), 1e9, d)
    min_d = d_safe.min(axis=1)
    peak_vmax = np.nanmax(np.where(np.isnan(vmax_kt), -1, vmax_kt), axis=1)

    # observed rate anchor (JD-TC-8): COUNT DISTINCT observed hurricanes passing within 100 km / record years
    # — close-passage rulebook (matches RAFT's "center within 100 km"); a storm brushing offshore counts.
    od = haversine_km(s["lat"], s["lon"], obs_tracks["lat"].values, obs_tracks["lon"].values)
    obs_n = int(obs_tracks.loc[od <= R_ANCHOR_KM, "storm_id"].nunique())
    lam = obs_n / RECORD_YEARS

    idx = np.where(is_anchor)[0]
    for i in idx:
        catalog_rows.append({
            "site": s["name"], "site_role": s["role"],
            "storm_ID": int(storm_id[i]),
            "event_family_id": int(storm_id[i]),       # JD-TC-4 cross-link key (= RAFT storm)
            "peak_gust_3s_mph": float(peak_gust[i]),
            "min_dist_km": float(min_d[i]),
            "peak_vmax_kt": float(peak_vmax[i]),
        })
    site_summ.append({
        "site": s["name"], "role": s["role"], "lat": s["lat"], "lon": s["lon"],
        "tiv_usd": s["tiv_usd"],
        "obs_passages_100km": obs_n, "lambda_per_yr": round(lam, 4),
        "raft_anchor_storms": int(is_anchor.sum()),
        "sev_median_gust_mph": round(float(np.median(peak_gust[is_anchor])), 1) if is_anchor.any() else 0.0,
        "sev_max_gust_mph": round(float(peak_gust.max()), 1),
    })

cat = pd.DataFrame(catalog_rows)
summ = pd.DataFrame(site_summ)
print(summ.to_string(index=False))
print(f"\ncatalog rows (per storm × site): {len(cat):,}")

# %% [markdown]
# ## 4 · Validation — does RAFT severity match the observed record at the site?
#
# Frequency is observed-anchored by construction; **severity** comes from RAFT, so we check it: compare the
# **intensity** of RAFT's anchor storms (peak `vmax` of storms within 100 km of the high site) against the
# **observed** HURDAT2 hurricane-landfall intensities near it. Rough agreement ⇒ RAFT's severity is trustworthy at
# this site. *(The STORM RP-grid cross-check — a 1.1 GB download — is the remaining external validation, deferred to
# a follow-on; this internal HURDAT2 check is the load-bearing one.)*

# %%
hi = next(s for s in sites if s["role"].startswith("proving"))
d_hi = haversine_km(hi["lat"], hi["lon"], lat, lon)
# like-for-like: storm intensity *near the site* (within 100 km), hurricane-intensity storms only
# — compared to observed landfall intensity within 100 km (both = "how strong storms are when near the site")
vmax_near = np.nanmax(np.where((d_hi <= R_ANCHOR_KM) & ~np.isnan(vmax_kt), vmax_kt, np.nan), axis=1)
raft_anchor_vmax = vmax_near[np.nan_to_num(vmax_near) >= HUR_KT]   # the anchor storms' near-site peak intensity
obs_near = land_hu[haversine_km(hi["lat"], hi["lon"], land_hu["lat"].values, land_hu["lon"].values) <= R_ANCHOR_KM]
print(f"high site = {hi['name']}")
print(f"  RAFT anchor storms  : n={len(raft_anchor_vmax)}  peak vmax median {np.median(raft_anchor_vmax):.0f} kt, "
      f"p90 {np.percentile(raft_anchor_vmax,90):.0f} kt, max {raft_anchor_vmax.max():.0f} kt")
print(f"  HURDAT2 observed     : n={len(obs_near)}  landfall vmax median {obs_near['max_wind_kt'].median():.0f} kt, "
      f"p90 {obs_near['max_wind_kt'].quantile(.9):.0f} kt, max {obs_near['max_wind_kt'].max():.0f} kt")
print("  → overlapping intensity ranges ⇒ RAFT severity is consistent with observed at this site")

# %% [markdown]
# ## 5 · Known-answer checks (basics-spot-on)

# %%
ever = summ[summ.role.str.startswith("proving")].iloc[0]
hay = summ[summ.role.str.startswith("baseline")].iloc[0]
checks = {
    "Holland peaks at Vmax (field known-answer)": all(ka.values()),
    "baseline Hayhurst: λ == 0 (true-zero control, no observed landfalls)": hay["lambda_per_yr"] == 0.0,
    "baseline Hayhurst: no anchor storms / catalog rows": (hay["raft_anchor_storms"] == 0) and (cat[cat.site == hay["site"]].empty),
    "high site λ ≈ observed ~0.19/yr close-passage rate (anchored, not RAFT-oversampled)": 0.10 <= ever["lambda_per_yr"] <= 0.30,
    "high site severity reaches major-hurricane gusts (>150 mph max)": ever["sev_max_gust_mph"] > 150,
    "high site median gust is a real hurricane (>74 mph)": ever["sev_median_gust_mph"] > 74,
    "RAFT vs observed intensity overlap at high site": abs(np.median(raft_anchor_vmax) - obs_near["max_wind_kt"].median()) < 30,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "a known-answer check failed"
print("\nall M1/01 known-answer checks pass ✅")

# %% [markdown]
# ## 6 · Emit — the per-site storm-resolved gust catalog (the M2 contract)

# %%
cat_path = DATA / "tc_m1_catalog.parquet"
cat.to_parquet(cat_path, index=False)
summ_path = DATA / "tc_m1_site_summary.parquet"
summ.to_parquet(summ_path, index=False)

manifest = {
    "notebook": "hurricane/m1_catalog/01_event_catalog",
    "method": "RAFT tracks → Holland (1980) field → per-site peak 3-s gust; frequency observed-anchored (JD-TC-8)",
    "magnitude_metric": "3-s peak gust (mph) at the site — Holland (1980) wind field on RAFT tracks",
    "levers": {"holland_B": HOLLAND_B, "gust_factor_1min_to_3s": GUST_FACTOR,
               "anchor_radius_km": R_ANCHOR_KM, "hurricane_kt": HUR_KT},
    "frequency_calibration": {
        "decision": "JD-TC-8: lambda from OBSERVED distinct HURDAT2 hurricanes passing within 100 km (close-passage "
                    "rulebook, matches RAFT severity); severity from RAFT Holland field",
        "record_years": RECORD_YEARS,
        "per_site": {r["site"]: {"lambda_per_yr": r["lambda_per_yr"],
                                 "obs_passages_100km": r["obs_passages_100km"],
                                 "raft_anchor_storms": r["raft_anchor_storms"]} for r in site_summ},
    },
    "event_family_id": "= RAFT storm_ID (active cross-link, consumed by flood coastal/pluvial-TC)",
    "validation": "RAFT anchor-storm intensity vs observed HURDAT2 near high site (overlap confirmed); STORM RP grid cross-check deferred",
    "units": "peak_gust_3s_mph = MPH (RAFT knots × gust_factor × 1.150779)",
    "outputs": {"catalog": str(cat_path.relative_to(ROOT)), "site_summary": str(summ_path.relative_to(ROOT))},
    "honest_caveats": [
        "gust_factor (ATC-7) and Holland B (ATC-6) are sensitivity levers — V1 single values",
        "symmetric Holland (no forward-motion asymmetry) — V1 simplification",
        "Hayhurst lambda=0 → zero loss (true-zero control); a regional floor not applied",
    ],
}
(DATA / "tc_m1_manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"wrote {cat_path}  ({len(cat):,} rows)\nwrote {summ_path}\nwrote {DATA/'tc_m1_manifest.json'}")
ds.close()

# %% [markdown]
# ## Takeaways → next
#
# - **Field-intensity built** — RAFT tracks → Holland field → per-site 3-s-gust catalog. The Holland field passes
#   its known-answer (peak == Vmax).
# - **Frequency calibrated honestly (JD-TC-8)** — λ from the **observed** rate (Everglades ≈ 0.18/yr; Hayhurst 0),
#   severity from RAFT physics — resolving the M0 oversample flag.
# - **RAFT severity validated** against observed intensities near the high site (overlapping ranges).
# - **`event_family_id` stamped** (= RAFT storm) — the active cross-link consumed by flood's coastal surge (built).
# - **Honest levers flagged** — gust factor, Holland B, symmetric field — for sensitivity in M4.
# - Emitted `tc_m1_catalog.parquet` + site summary + manifest.
#
# **Next → M2 (coupling):** the field-intensity coupling — read the per-event site gust into the exposure contract
# M3 needs (solar = degenerate, `value_exposed_fraction = 1.0`).
