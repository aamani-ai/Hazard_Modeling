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
# # Flood · Coastal `[C]` — M1 catalog: the per-storm surge event catalog (all coastal sites, both assets)
#
# **Magnitude metric:** coastal surge **depth (ft above ground)** by **hurricane category (1–5), per storm**; the
# depth itself is sampled from SLOSH MOM in M2. M1 carries the event dimension — each qualifying storm's category and
# `event_family_id` — plus the annual frequency `λ`.
#
# **Data source:** the **RAFT** synthetic North Atlantic tropical-cyclone catalog (`RAFT.NA.v20231016.nc`) for the
# close-passage screen, and **HURDAT2** observed tracks + landfalls for the observed-anchored `λ`. SLOSH MOM
# (`US_SLOSH_MOM_Inundation_v2`, high-tide) is named here but sampled in M2.
#
# **What this notebook does:** builds the asset-independent coastal **event catalog** for **every coastal-exposed
# site, both assets** in one pass — one M1 per sub-peril, with the asset mattering only at M2 (per JD-FL-19). Each
# exposed site gets the same RAFT close-passage screen ([JD-FL-21](../../../docs/plans/flood/decisions.md): ≤50 km,
# ≥64 kt) → a per-storm catalog (category, `event_family_id`), and an observed-anchored frequency `λ` from HURDAT2
# close-passages within 50 km over the record. Coastal sites: solar **Discovery Solar Center** (FL, high-surge proving) + **LA3 West Baton Rouge** (LA, all-three) +
# **Hayhurst** (structural zero), and wind **Amazon Wind Farm US East** (NC, all-three). The manifest carries a
# per-site `sites` list (each asset's M2 reads its slug) plus `high_site`/`baseline_site` keys for the solar coastal
# M2. The catalog combines with hurricane wind in M4 via `event_family_id` (JD-FL-12).

# %%
import json
from pathlib import Path
import numpy as np, pandas as pd, h5py

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
FL = ROOT / "data" / "flood"; TC = ROOT / "data" / "hurricane"
R_SURGE_KM = 50.0; HUR_KT = 64.0      # JD-FL-21

def _slug(name): return name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "").replace(",", "")

# ALL coastal sites, both assets → {asset, slug, name, lat, lon, role, exposed, eia?, boundary_wkt?}
COAST = []
_sol = json.loads((FL / "flood_solar_coastal_m0_sites.json").read_text())["sites"]
for s in _sol:
    COAST.append({"asset": "solar", "slug": _slug(s["name"]), "name": s["name"], "lat": s["lat"], "lon": s["lon"],
                  "role": s["role"], "exposed": bool(s.get("surge_exposed", s["role"].startswith("proving"))),
                  "eia": s.get("eia"), "boundary_wkt": s.get("boundary_wkt")})
for s in json.loads((FL / "flood_wind_m0_sites.json").read_text())["sites"]:
    if s.get("m0_coastal", {}).get("exposed"):
        COAST.append({"asset": "wind_farm", "slug": s["slug"], "name": s["name"], "lat": s["lat"], "lon": s["lon"],
                      "role": s["role"], "exposed": True, "eia": None, "boundary_wkt": s.get("boundary_wkt")})
print("coastal sites:", [(c["asset"], c["name"], "exposed" if c["exposed"] else "zero") for c in COAST])

# %% [markdown]
# ## 1 · RAFT close-passage screen → per-site storm catalog (the asset-independent event catalog)

# %%
def haversine_km(la1, lo1, la2, lo2):
    R = 6371.0; p1, p2 = np.radians(la1), np.radians(la2)
    dp, dl = np.radians(la2 - la1), np.radians(lo2 - lo1)
    return 2 * R * np.arcsin(np.sqrt(np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2))

def cat_of(kt):
    return 0 if kt < HUR_KT else 1 + sum(kt >= t for t in [83, 96, 113, 137])

with h5py.File(TC / "raw" / "RAFT.NA.v20231016.nc", "r") as f:
    lat, lon, vmax = f["lat"][:], f["lon"][:], f["vmax"][:]
    storm_ID = f["storm_ID"][:]

def raft_catalog(site):
    d = haversine_km(site["lat"], site["lon"], lat, lon)
    inR = (d <= R_SURGE_KM) & (vmax >= HUR_KT)
    qual = np.where(inR.any(axis=1))[0]
    rows = []
    for s in qual:
        near_kt = float(np.nanmax(vmax[s][inR[s]]))
        rows.append({"site": site["name"], "site_role": site["role"], "asset": site["asset"],
                     "storm_ID": int(storm_ID[s]), "event_family_id": int(storm_ID[s]),   # cross-link (JD-FL-4/12)
                     "near_site_vmax_kt": round(near_kt, 1), "category": cat_of(near_kt),
                     "min_dist_km": round(float(np.nanmin(d[s])), 1)})
    return pd.DataFrame(rows)

# %% [markdown]
# ## 2 · Frequency — observed-anchored λ (HURDAT2 close-passages within 50 km / record years)

# %%
land = pd.read_parquet(TC / "tc_m0_hurdat2_landfalls.parquet")
trk  = pd.read_parquet(TC / "tc_m0_hurdat2_tracks_hu.parquet")
REC_YEARS = int(land["year"].max() - land["year"].min() + 1)
def lambda_of(site):
    dt = haversine_km(site["lat"], site["lon"], trk["lat"].values, trk["lon"].values)
    dl = haversine_km(site["lat"], site["lon"], land["lat"].values, land["lon"].values)
    obs_pass = int(trk.loc[dt <= R_SURGE_KM, "storm_id"].nunique())
    obs_land = int(land.loc[dl <= R_SURGE_KM, "storm_id"].nunique())
    return obs_pass / REC_YEARS, obs_pass, obs_land

# %% [markdown]
# ## 3 · Build per-site catalogs + emit the shared manifest (M2 samples SLOSH at the asset → per-storm depth)

# %%
site_entries = []
for c in COAST:
    if not c["exposed"]:
        entry = {"asset": c["asset"], "slug": c["slug"], "name": c["name"], "eia": c["eia"],
                 "lat": c["lat"], "lon": c["lon"], "role": c["role"], "exposed": False,
                 "lambda_per_yr": 0.0, "raft_qualifying_storms": 0,
                 "note": "structural zero — no coastline / no SLOSH basin (JD-FL-13)"}
        site_entries.append(entry)
        print(f"  {c['name']:24s} ({c['asset']}) structural zero")
        continue
    cat = raft_catalog(c)
    lam, obs_pass, obs_land = lambda_of(c)
    cat.to_parquet(FL / f"{c['slug']}_flood_coastal_m1_catalog.parquet", index=False)
    cdist = {int(k): int(v) for k, v in cat["category"].value_counts().sort_index().items()}
    entry = {"asset": c["asset"], "slug": c["slug"], "name": c["name"], "eia": c["eia"],
             "lat": c["lat"], "lon": c["lon"], "role": c["role"], "exposed": True,
             "boundary_wkt": c["boundary_wkt"], "raft_qualifying_storms": int(len(cat)),
             "category_dist": cdist, "lambda_per_yr": round(lam, 4),
             "obs_passages_50km": obs_pass, "obs_landfalls_50km": obs_land, "record_years": REC_YEARS,
             "catalog_parquet": f"{c['slug']}_flood_coastal_m1_catalog.parquet"}
    site_entries.append(entry)
    print(f"  {c['name']:24s} ({c['asset']}) {len(cat)} storms, cats {cdist}, λ={lam:.4f}/yr ({obs_pass} obs ≤50km / {REC_YEARS}yr)")

# back-compat keys for the (unchanged) solar coastal M2: high_site = solar proving, baseline_site = solar baseline
_sol_exp = next(e for e in site_entries if e["asset"] == "solar" and e["exposed"])
_sol_base = next((e for e in site_entries if e["asset"] == "solar" and not e["exposed"]), None)
manifest = {
    "peril": "flood", "sub_peril": "coastal", "layer": "M1",
    "kind": "shared asset-independent storm catalog, ALL coastal sites (Path 2 / JD-FL-19) — SLOSH sampling is each asset's M2",
    "event_model": "event-based (compound-Poisson) — combines with hurricane wind via event_family_id (JD-FL-12)",
    "decisions": ["JD-FL-14 (SLOSH-only)", "JD-FL-21 (≤50km ≥64kt, observed-anchored λ)", "JD-FL-19 (Path 2)", "JD-FL-17 (unify per all-three site)"],
    "slosh_source": "data/flood/raw/slosh/US_SLOSH_MOM_Inundation_v2 (M2 samples it at the asset)",
    "R_surge_km": R_SURGE_KM, "hur_kt": HUR_KT,
    "sites": site_entries,                                   # per-site, both assets (wind M2 reads its slug here)
    "high_site": _sol_exp,                                   # back-compat — solar coastal M2 reads this (unchanged)
    "baseline_site": _sol_base,
}
(FL / "flood_coastal_m1_catalog_manifest.json").write_text(json.dumps(manifest, indent=2))
print("\nwrote:", FL / "flood_coastal_m1_catalog_manifest.json",
      f"({sum(e['exposed'] for e in site_entries)} exposed + {sum(not e['exposed'] for e in site_entries)} zero, both assets)")
