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
# # Flood · Pluvial `[F]` — M1 catalog: the asset-independent rainfall-runoff field (all sites)
#
# **Magnitude metric:** pluvial **runoff depth `Q` (m, → ft above ground in M2)** indexed by annual return period
# (10/25/50/100/500-yr). The runoff volume here is the source term; the per-asset ponded inundation **depth** is
# derived in M2.
#
# **Data source:** **NOAA Atlas 14** point precipitation frequency (24-hr depth, partial-duration series) via the
# HDSC text service; runoff via the **SCS Curve-Number** method (CN = 80). Sites outside Atlas 14 (Pacific Northwest /
# Atlas 2) → pluvial 0.
#
# **What this notebook does:** builds the pluvial source field for **every flood site, both assets** (solar + wind
# farm) in one pass — one M1 per sub-peril, with the asset mattering only at M2 (per JD-FL-19). For each site it pulls
# the Atlas 14 24-hr rainfall at each return period and converts it to SCS-CN runoff `Q`. Pluvial uses **one method
# everywhere**, so a single field serves both assets; the per-asset ponding (lidar ponding-fraction `f` / depression
# depth-cap) is computed in each asset's M2 ([JD-FL-19](../../../docs/plans/flood/decisions.md)). Emits the
# asset-independent runoff field `Q(site, RP)` as a shared manifest; each asset's M2 filters to its own sites.

# %%
import json, hashlib
from pathlib import Path
import pandas as pd, requests

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "flood"
IN_M = 0.0254
_CACHE = OUT / "raw" / "http_cache"; _CACHE.mkdir(parents=True, exist_ok=True)
def cget_text(url, params=None, timeout=40):
    key = hashlib.md5(("T" + url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = _CACHE / (key + ".txt")
    if f.exists(): return f.read_text()
    t = requests.get(url, params=params, timeout=timeout).text; f.write_text(t); return t

def _slug(name): return name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "").replace(",", "")

# ALL flood sites, both assets — normalised to {asset, slug, name, role, lat, lon}
SITES = []
for s in json.loads((OUT / "flood_solar_m0_sites.json").read_text())["sites"]:
    SITES.append({"asset": "solar", "slug": _slug(s["name"]), "name": s["name"], "role": s["role"], "lat": s["lat"], "lon": s["lon"]})
for s in json.loads((OUT / "flood_wind_m0_sites.json").read_text())["sites"]:
    SITES.append({"asset": "wind_farm", "slug": s["slug"], "name": s["name"], "role": s["role"], "lat": s["lat"], "lon": s["lon"]})
print("all flood sites:", [(s["asset"], s["name"]) for s in SITES])

# %% [markdown]
# ## 1 · NOAA Atlas 14 — 24-hr rainfall → SCS-CN runoff `Q` per site (one method, every site)

# %%
A14 = "https://hdsc.nws.noaa.gov/cgi-bin/new/fe_text_mean.csv"
RP_COLS = {10: 3, 25: 4, 50: 5, 100: 6, 500: 8}; RPS = [10, 25, 50, 100, 500]
CN = 80.0; RETENTION = 0.5

def atlas14_24hr(lat, lon):
    txt = cget_text(A14, {"lat": lat, "lon": lon, "type": "pf", "data": "depth", "units": "english", "series": "pds"})
    for line in txt.splitlines():
        if line.lower().startswith("24-hr:"):
            return {rp: [float(v) for v in line.split(":", 1)[1].replace(" ", "").split(",") if v][i] for rp, i in RP_COLS.items()}
    return None   # outside Atlas 14 (PNW / Atlas 2) → pluvial 0

def scs_runoff_m(P_in, cn=CN):
    S = 1000.0 / cn - 10.0; Ia = 0.2 * S
    return (((P_in - Ia) ** 2 / (P_in + 0.8 * S)) if P_in > Ia else 0.0) * IN_M

field = []
for s in SITES:
    rain = atlas14_24hr(s["lat"], s["lon"]); cov = rain is not None
    tag = " ".join(f"{rp}yr={rain[rp]:.1f}" for rp in RPS) if cov else "NO Atlas 14 (PNW) → pluvial 0"
    print(f"  {s['asset']:9s} {s['name']:22s} 24-hr rain (in): {tag}")
    for rp in RPS:
        field.append({"asset": s["asset"], "slug": s["slug"], "name": s["name"], "role": s["role"],
                      "rp_years": rp, "aep": round(1/rp, 4),
                      "rain_in": round(rain[rp], 2) if cov else None,
                      "runoff_m": round(scs_runoff_m(rain[rp]), 4) if cov else 0.0, "atlas14_covered": cov})
fd = pd.DataFrame(field)
print()
print(fd[["asset", "name", "rp_years", "runoff_m", "atlas14_covered"]].to_string(index=False))

# %% [markdown]
# ## 2 · Emit the shared runoff-field manifest (each asset's M2 reads its own sites; per-node/areal ponding is M2's job)

# %%
manifest = {
    "peril": "flood", "sub_peril": "pluvial", "event_family_id": None, "layer": "M1",
    "kind": "shared asset-independent runoff field, ALL sites (Path 2 / JD-FL-19) — ponding deferred to each asset's M2",
    "depth_source": {"method": "NOAA Atlas 14 24-hr rainfall → SCS-CN runoff Q (one method, every site; JD-FL-9)",
                     "runoff": f"SCS Curve Number CN={CN}", "retention_r_for_M2": RETENTION,
                     "return_periods_yr": RPS, "units": "metres"},
    "caveats": ["No depth anchor (JD-FL-9). PNW (Shepherds Flat) outside Atlas 14 → pluvial 0 (coverage gap).",
                "Ponding fraction f + ponding now per-asset in M2: solar = areal lidar; wind = per-node lidar + pad-gate (JD-FL-19/W6)."],
    "field": json.loads(fd.to_json(orient="records")),
}
(OUT / "flood_pluvial_m1_catalog_manifest.json").write_text(json.dumps(manifest, indent=2))
print("\nwrote:", OUT / "flood_pluvial_m1_catalog_manifest.json", f"({len(fd)} rows, {len(SITES)} sites, both assets)")
