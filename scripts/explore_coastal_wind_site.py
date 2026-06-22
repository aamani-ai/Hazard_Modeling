#!/usr/bin/env python
"""Survey coastal wind farms for an ALL-THREE flood site (coastal surge + riverine SFHA + pluvial).

Not production — a one-off scout to answer "does a wind farm with all three sub-perils exist?" and pick it.
Pluvial is ~automatic (Atlas 14 covers all CONUS but the PNW), so the binding test is **surge ∩ riverine-SFHA**:
a coast-front turbine cloud that ALSO straddles a river floodplain (Zone A / riverine AE), not just coastal V/VE.

Per candidate project: surge onset category (NOAA CFEM) + per-turbine NFHL zone mix (riverine A/AE vs coastal V/VE).
"""
import json, math, time, hashlib
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
RAW = ROOT / "data" / "flood" / "raw"; _C = RAW / "http_cache"; _C.mkdir(parents=True, exist_ok=True)
USWTDB = "https://energy.usgs.gov/api/uswtdb/v1/turbines"
NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query"
CFEM = ("https://www.coast.noaa.gov/arcgis/rest/services/FloodExposureMapper/"
        "CFEM_CoastalFloodHazardComposite/MapServer/identify")
RIVERINE_Z = {"A", "AE", "AH", "AO", "AR", "A99"}   # riverine-ish (A = approximate, almost always riverine)
COASTAL_Z = {"V", "VE"}                             # coastal surge zones
SESS = requests.Session()
SESS.mount("https://", HTTPAdapter(max_retries=Retry(total=4, backoff_factor=0.6, status_forcelist=[429,500,502,503,504])))
SESS.headers.update({"User-Agent": "infrasure-hazard-modeling/0.1 (coastal-wind scout)"})

def cget(url, params, timeout=40):
    k = hashlib.md5((url + json.dumps(params, sort_keys=True, default=str)).encode()).hexdigest()
    f = _C / (k + ".json")
    if f.exists(): return json.loads(f.read_text())
    j = SESS.get(url, params=params, timeout=timeout).json(); f.write_text(json.dumps(j)); return j

# US onshore coastal-wind regions (the only places with near-coast onshore utility wind). Bbox pulls, not county
# filter (USWTDB t_county carries a " County" suffix). South/Central TX is the main belt; NE-NC (Albemarle Sound)
# is the one notable Atlantic cluster; upper-TX/SW-LA catches Galveston→Cameron.
REGIONS = {
    "S/C Texas Gulf":  {"xlong": ["gte.-98.4", "lte.-95.5"], "ylat": ["gte.25.8", "lte.29.2"]},
    "Upper TX / SW LA":{"xlong": ["gte.-95.5", "lte.-92.5"], "ylat": ["gte.29.0", "lte.30.6"]},
    "NE North Carolina":{"xlong": ["gte.-77.1", "lte.-75.6"], "ylat": ["gte.35.6", "lte.36.8"]},
    "VA / mid-Atlantic":{"xlong": ["gte.-77.0", "lte.-75.2"], "ylat": ["gte.36.8", "lte.38.3"]},
}

def surge_onset(lat, lon):
    p = {"geometry": f"{lon},{lat}", "geometryType":"esriGeometryPoint","sr":4326,"tolerance":2,
         "mapExtent": f"{lon-.05},{lat-.05},{lon+.05},{lat+.05}","imageDisplay":"600,600,96",
         "layers":"all","returnGeometry":"false","f":"json"}
    try:
        for res in cget(CFEM, p).get("results", []):
            d = res.get("attributes", {}).get("Raster.DESCRPTN", "") or ""
            if "Hurricane Category" in d:
                cats = [int(x) for x in __import__("re").findall(r"\d", d.split("Hurricane Category")[1])]
                return min(cats) if cats else None
        return None
    except Exception:
        return None

def zone_at(lat, lon):
    p = {"geometry": f"{lon},{lat}","geometryType":"esriGeometryPoint","inSR":4326,
         "spatialRel":"esriSpatialRelIntersects","outFields":"FLD_ZONE","returnGeometry":"false","f":"json"}
    try:
        fs = cget(NFHL, p).get("features", [])
        return fs[0]["attributes"]["FLD_ZONE"] if fs else "X"
    except Exception:
        return "ERR"

# 1 · pull each coastal region's turbines (one bbox call per region), group into projects
frames = []
for rname, bbox in REGIONS.items():
    tb = pd.DataFrame(cget(USWTDB, {**bbox, "select": "p_name,t_state,t_county,xlong,ylat,t_cap"}, timeout=90))
    if len(tb):
        tb["region"] = rname; frames.append(tb)
    print(f"  {rname:20s}: {len(tb)} turbines, {tb['p_name'].nunique() if len(tb) else 0} projects")
turb = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
turb = turb.dropna(subset=["p_name"])
print(f"\nTOTAL coastal-strip turbines: {len(turb)} across {turb['p_name'].nunique()} projects\n")

# 2 · per project: surge onset (centroid) + per-turbine zone mix (sampled)
rows = []
for nm, g in turb.groupby("p_name"):
    clat, clon = float(g.ylat.mean()), float(g.xlong.mean())
    onset = surge_onset(clat, clon)
    samp = g.sample(min(20, len(g)), random_state=1)
    zones = Counter(zone_at(r.ylat, r.xlong) for r in samp.itertuples())
    n = sum(zones.values())
    riv = sum(v for z, v in zones.items() if z in RIVERINE_Z) / n
    coa = sum(v for z, v in zones.items() if z in COASTAL_Z) / n
    cty = str(g.t_county.iloc[0]) if pd.notna(g.t_county.iloc[0]) else "—"
    rows.append({"project": nm, "county": cty, "region": g.region.iloc[0], "n_turb": len(g), "mw": round(g.t_cap.sum()/1000,1),
                 "surge_onset_cat": onset, "frac_riverine": round(riv,2), "frac_coastal": round(coa,2),
                 "zone_mix": dict(zones), "lat": round(clat,4), "lon": round(clon,4)})
    print(f"  {nm[:26]:26s} {cty[:10]:10s} n={len(g):3d} surge={onset} "
          f"riv={riv:.2f} coa={coa:.2f} zones={dict(zones)}")
    time.sleep(0.1)

res = pd.DataFrame(rows)
# all-three candidate = surge-exposed AND has riverine-zone turbines
cand = res[(res.surge_onset_cat.notna()) & (res.frac_riverine > 0)].sort_values(
    ["frac_riverine","surge_onset_cat"], ascending=[False, True])
print("\n=== ALL-THREE candidates (surge + riverine SFHA; pluvial automatic) ===")
print(cand[["project","county","n_turb","mw","surge_onset_cat","frac_riverine","frac_coastal"]].to_string(index=False)
      if len(cand) else "  (none — fall back to surge+coastal-AE or two-site coastal build)")
(RAW / "coastal_wind_scout.json").write_text(res.to_json(orient="records"))
print("\nwrote:", RAW / "coastal_wind_scout.json")
