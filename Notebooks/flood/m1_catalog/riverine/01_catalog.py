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
# # Flood · Riverine `[R]` — M1 catalog: the asset-independent flood-depth field (all sites)
#
# **Magnitude metric:** riverine flood **depth (ft above ground)** indexed by annual return period (10–500-yr) — the
# inundation depth the M3 damage curve consumes.
#
# **Data source:** FEMA **Base Level Engineering (BLE)** depth grids where a study exists (`ble_image`); FEMA **NFHL**
# Special Flood Hazard Area + USGS **3DEP** elevation where only the flood zone is mapped (`sfha_bathtub`); USGS
# **NLDI→NSS** regression and **NWIS** peak-flow gauges for the flow-frequency `Q(T)` that anchors the lower RPs.
#
# **What this notebook does:** builds the riverine **hazard field** for every flood site (solar + wind farm) in one
# pass, picking the method per site from its data availability ([JD-FL-6](../../../docs/plans/flood/decisions.md)):
#
# | method | when | field emitted | `Q(T)` source |
# |---|---|---|---|
# | **`ble_image`** | a FEMA BLE depth grid covers the site | native-resolution depth raster ([JD-FL-18](../../../docs/plans/flood/decisions.md)) | USGS NLDI→NSS regression ([JD-FL-8](../../../docs/plans/flood/decisions.md)) |
# | **`sfha_bathtub`** | only SFHA Zone A is mapped (no BLE grid) | 1% flood-area polygon + boundary water-surface contour off 3DEP ([JD-FL-W4](../../../docs/plans/flood/decisions.md)) | per-site USGS gauge Log-Pearson III ([JD-FL-W5](../../../docs/plans/flood/decisions.md)) |
# | **`dry`** | site outside the SFHA | — | — |
#
# The field is **asset-independent** — sampling it at the solar footprint (areal) or each wind turbine (per-node) is
# M2's job. Emits one method-tagged field manifest; large flood-area polygons are written to gitignored `raw/` and
# referenced by path.

# %%
import csv, json, math, hashlib, re
from pathlib import Path
from io import BytesIO
import numpy as np, pandas as pd, requests
import matplotlib.image as mpimg
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from scipy.stats import norm
from shapely import wkt
from shapely.geometry import shape
from shapely.ops import transform, unary_union
import pyproj

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "flood"
RAW = OUT / "raw"; (RAW / "ble_field").mkdir(parents=True, exist_ok=True)
_CACHE = OUT / "raw" / "http_cache"; _CACHE.mkdir(parents=True, exist_ok=True)
FT_M = 0.3048
SESS = requests.Session()
SESS.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.8, status_forcelist=[429, 500, 502, 503, 504])))
SESS.headers.update({"User-Agent": "infrasure-hazard-modeling/0.1 (flood riverine M1 field)"})

def cget(url, params=None, timeout=60):
    key = hashlib.md5(("G" + url + json.dumps(params, sort_keys=True, default=str)).encode()).hexdigest()
    f = _CACHE / (key + ".json")
    if f.exists(): return json.loads(f.read_text())
    j = requests.get(url, params=params, timeout=timeout).json(); f.write_text(json.dumps(j)); return j
def cpost_json(url, payload, timeout=90):
    key = hashlib.md5(("J" + url + json.dumps(payload, sort_keys=True)).encode()).hexdigest()
    f = _CACHE / (key + ".json")
    if f.exists(): return json.loads(f.read_text())
    j = requests.post(url, json=payload, timeout=timeout).json(); f.write_text(json.dumps(j)); return j

def _slug(name): return name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "").replace(",", "")

# %% [markdown]
# ## 0 · Normalise ALL flood sites and select each site's method from its data availability
#
# BLE-eligible = the site carries a footprint polygon (`boundary_wkt` in the solar M0 DEM context) over BLE-covered
# terrain. SFHA-bathtub = a wind site mapped in Zone A (`m0_sfha.frac_sfha ≥ 2%`). Else dry. (The split is by site
# evidence, not asset — it just happens that today's BLE sites are solar and the Zone-A sites are wind.)

# %%
SITES = []
_solar = json.loads((OUT / "flood_solar_m0_sites.json").read_text())["sites"]
_geo = {s["eia"]: s for s in json.loads((OUT / "flood_solar_m0_dem_context.json").read_text())["sites"]}
for s in _solar:
    bwkt = _geo.get(s["eia"], {}).get("boundary_wkt")
    SITES.append({"asset": "solar", "slug": _slug(s["name"]), "name": s["name"], "role": s["role"],
                  "lat": s["lat"], "lon": s["lon"], "eia": int(s["eia"]),
                  "method": "ble_image" if isinstance(bwkt, str) else "dry", "boundary_wkt": bwkt})
for s in json.loads((OUT / "flood_wind_m0_sites.json").read_text())["sites"]:
    frac = s["m0_sfha"]["frac_sfha"]
    SITES.append({"asset": "wind_farm", "slug": s["slug"], "name": s["name"], "role": s["role"],
                  "lat": s["lat"], "lon": s["lon"], "sub_lat": s["sub_lat"], "sub_lon": s["sub_lon"],
                  "method": "sfha_bathtub" if frac >= 0.02 else "dry", "frac_sfha": frac})
for s in SITES:
    print(f"  {s['asset']:9s} {s['name']:22s} → {s['method']}")

# %% [markdown]
# ## 1 · `ble_image` field — full-resolution BLE depth raster per site/RP (JD-FL-18)
#
# The BLE service has no value-raster endpoint, so we `export` the depth layer over the footprint bbox at native
# resolution and decode the 6 legend colour-bands → a depth-ft grid. **This grid IS the field** (saved to
# `raw/ble_field/`, gitignored); M2 masks it to the asset.

# %%
BLE = "https://txgeo.usgs.gov/arcgis/rest/services/FEMA_EBFE/EBFE/MapServer"
DEPTH_LAYER = {100: 12, 500: 16}; EXTENT_10PCT_LAYER = 7
BAND_RGB = np.array([[0.745,0.91,1.0],[0.451,0.698,1.0],[0.298,0.902,0.0],[1.0,1.0,0.0],[1.0,0.667,0.0],[0.902,0.0,0.0]])
BAND_MID_FT = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])

def fetch_depth_field(eia, geom, layer, W=700):
    """Export the BLE depth layer over the footprint bbox at native resolution → (depth-ft grid, extent_4326).
    NoData/dry → 0. This IS the asset-independent field; M2 masks it to the asset (JD-FL-19)."""
    out = RAW / "ble_field" / f"{eia}_L{layer}.npz"
    if out.exists():
        d = np.load(out); return d["depth_ft"], d["extent"]
    mnx, mny, mxx, mxy = geom.bounds
    asp = (mxy - mny) / (mxx - mnx); H = int(W * asp)
    p = {"bbox": f"{mnx},{mny},{mxx},{mxy}", "bboxSR": 4326, "imageSR": 4326, "layers": f"show:{layer}",
         "size": f"{W},{H}", "format": "png", "transparent": "true", "f": "json"}
    j = requests.get(BLE + "/export", params=p, timeout=60).json(); ext = j["extent"]
    img = mpimg.imread(BytesIO(requests.get(j["href"], timeout=60).content))
    rgb, alpha = img[..., :3], img[..., 3]
    wet = alpha > 0.5
    depth_ft = np.zeros(rgb.shape[:2], dtype="float32")
    if wet.any():
        dist = np.linalg.norm(rgb[wet][:, None, :] - BAND_RGB[None, :, :], axis=2)
        depth_ft[wet] = BAND_MID_FT[dist.argmin(1)]
    extent = np.array([ext["xmin"], ext["ymin"], ext["xmax"], ext["ymax"]], dtype="float64")
    np.savez_compressed(out, depth_ft=depth_ft, extent=extent)
    return depth_ft, extent

def fetch_extent_field(eia, geom, layer, W=700):
    """Export the 10% (10-yr) flood-EXTENT layer over the footprint bbox → a 0/1 wet mask (no depth grid exists)."""
    out = RAW / "ble_field" / f"{eia}_L{layer}_ext.npz"
    if out.exists():
        d = np.load(out); return d["extent"]
    mnx, mny, mxx, mxy = geom.bounds; asp = (mxy - mny) / (mxx - mnx); H = int(W * asp)
    p = {"bbox": f"{mnx},{mny},{mxx},{mxy}", "bboxSR": 4326, "imageSR": 4326, "layers": f"show:{layer}",
         "size": f"{W},{H}", "format": "png", "transparent": "true", "f": "json"}
    j = requests.get(BLE + "/export", params=p, timeout=60).json(); ext = j["extent"]
    img = mpimg.imread(BytesIO(requests.get(j["href"], timeout=60).content))
    mask = (img[..., 3] > 0.5).astype("uint8")
    extent = np.array([ext["xmin"], ext["ymin"], ext["xmax"], ext["ymax"]], dtype="float64")
    np.savez_compressed(out, mask=mask, extent=extent); return extent

# %% [markdown]
# ## 2 · `sfha_bathtub` field — 1% flood-area polygon + boundary WSE contour off 3DEP (JD-FL-W4)

# %%
NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query"
EPQS = "https://epqs.nationalmap.gov/v1/json"
SFHA_WHERE = "FLD_ZONE IN ('A','AE','AH','AO','AR','A99','V','VE')"

def epqs(lat, lon):
    try:
        return float(SESS.get(EPQS, params={"x": lon, "y": lat, "units": "Meters", "wkid": 4326}, timeout=20).json()["value"])
    except Exception:
        return None

def flood_area(minx, miny, maxx, maxy, where, pad=0.012):
    env = f"{minx-pad},{miny-pad},{maxx+pad},{maxy+pad}"
    p = {"geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 4326, "outSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "where": where, "outFields": "FLD_ZONE",
         "returnGeometry": "true", "f": "geojson"}
    fs = SESS.get(NFHL, params=p, timeout=90).json().get("features", [])
    geoms = [shape(f["geometry"]) for f in fs if f.get("geometry")]
    return unary_union(geoms) if geoms else None

def boundary_samples(area, n=80, cache=None):
    """Elevations along the flood-area boundary (the local 1% water-surface contour). Cached."""
    if cache and cache.exists():
        d = json.loads(cache.read_text()); return np.array(d["xy"]), np.array(d["z"])
    bnd = area.boundary
    pts = [bnd.interpolate(t, normalized=True) for t in np.linspace(0, 1, n, endpoint=False)]
    xy = np.array([(p.x, p.y) for p in pts]); z = np.array([epqs(p.y, p.x) for p in pts], dtype=float)
    ok = np.isfinite(z); xy, z = xy[ok], z[ok]
    if cache: cache.write_text(json.dumps({"xy": xy.tolist(), "z": z.tolist()}))
    return xy, z

# %% [markdown]
# ## 3 · Build the field per site (dispatch on method) + the matching `Q(T)` hydrology
#
# `ble_image` → BLE rasters + NLDI→NSS flow-frequency (JD-FL-8); `sfha_bathtub` → flood-area + WSE contour + gauge
# Log-Pearson III (JD-FL-W5). Both `Q(T)` are asset-independent (M2 turns them into densified RPs / ΔWSE).

# %%
# -- ble_image hydrology: USGS NLDI → NSS regression (drives the proving solar site's lower-RP densification) --
NLDI = "https://api.water.usgs.gov/nldi/linked-data"; NSS = "https://streamstats.usgs.gov/nssservices"
AEP2RP = {50: 2, 20: 5, 10: 10, 4: 25, 2: 50, 1: 100}; SLOPE_FT_MI = 5.0
def reach_drainage_area_mi2(lat, lon):
    comid = cget(f"{NLDI}/comid/position", {"coords": f"POINT({lon} {lat})", "f": "json"})["features"][0]["properties"]["comid"]
    basin = cget(f"{NLDI}/comid/{comid}/basin", {"f": "json"})["features"][0]["geometry"]
    proj = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True).transform
    return comid, transform(proj, shape(basin)).area / 1e6 * 0.386102
def nss_q_curve(da_mi2, slope_ft_mi, region="GC1889"):
    sc = cget(f"{NSS}/scenarios", {"regions": "LA", "statisticgroup": 2, "regressionregions": region})
    for p in sc[0]["regressionRegions"][0]["parameters"]:
        p["value"] = da_mi2 if p["code"] == "DRNAREA" else slope_ft_mi
    res = cpost_json(f"{NSS}/scenarios/estimate", sc)[0]["regressionRegions"][0]["results"]
    Q = {}
    for x in res:
        m = re.search(r"PK([\d.]+)AEP", x.get("code", "") or "")
        if m and float(m.group(1)) in AEP2RP: Q[AEP2RP[float(m.group(1))]] = x["value"]
    return Q

# -- sfha_bathtub hydrology: USGS gauge peak-flow Log-Pearson III, PER SITE --
# Each bathtub site uses its OWN nearest peak-flow gauge (hand-picked here, notebook-level; production auto-discovery
# deferred — see decisions.md). NOT a single hardcoded gauge: a 2nd bathtub site must not inherit the 1st's hydrology.
RPS_GAUGE = [10, 25, 50, 100, 250, 500]
GAUGE_BY_SITE = {
    "green_river_il":       "05447000",     # USGS Green River at Amboy, IL
    "amazon_wind_us_east":  "0204382800",   # USGS Pasquotank River near South Mills, NC (Albemarle tributary, ~14 km)
}
def gauge_QT(site, rps):
    cache = RAW / f"gauge_QT_{site}.json"
    if cache.exists():
        d = json.loads(cache.read_text()); return {int(k): v for k, v in d["Q"].items()}, d["n"], d["skew"]
    txt = SESS.get("https://nwis.waterdata.usgs.gov/nwis/peak",
                   params={"site_no": site, "agency_cd": "USGS", "format": "rdb"}, timeout=60).text
    lines = [l for l in txt.splitlines() if l and not l.startswith("#")]
    rows = list(csv.reader([lines[0]] + lines[2:], delimiter="\t"))
    df = pd.DataFrame([dict(zip(rows[0], r)) for r in rows[1:]])
    pk = pd.to_numeric(df["peak_va"], errors="coerce").dropna().values
    x = np.log10(pk[pk > 0]); m, sd = x.mean(), x.std(ddof=1); n = len(x)
    g = (n / ((n - 1) * (n - 2))) * np.sum(((x - m) / sd) ** 3)
    def Kwh(p):
        z = norm.ppf(1 - p)
        return z if g == 0 else (2 / g) * (((z - g / 6) * (g / 6) + 1) ** 3 - 1)
    Q = {int(t): float(10 ** (m + Kwh(1 / t) * sd)) for t in rps}
    cache.write_text(json.dumps({"Q": Q, "n": int(n), "skew": float(g)})); return Q, int(n), float(g)

field, flow_frequency, gauges = [], {}, {}
for s in SITES:
    rec = {"asset": s["asset"], "slug": s["slug"], "name": s["name"], "role": s["role"], "method": s["method"]}
    if s["method"] == "ble_image":
        geom = wkt.loads(s["boundary_wkt"]); rec["eia"] = s["eia"]; rec["rasters"] = {}
        for rp, layer in DEPTH_LAYER.items():
            depth_ft, extent = fetch_depth_field(s["eia"], geom, layer)
            rec["rasters"][str(rp)] = {"path": str((RAW / "ble_field" / f"{s['eia']}_L{layer}.npz").relative_to(ROOT)),
                                       "extent_4326": extent.tolist(), "shape": list(depth_ft.shape),
                                       "px_m": round((extent[2]-extent[0]) * 111000 / depth_ft.shape[1], 1)}
        ext10 = fetch_extent_field(s["eia"], geom, EXTENT_10PCT_LAYER)
        rec["rasters"]["10ext"] = {"path": str((RAW / "ble_field" / f"{s['eia']}_L{EXTENT_10PCT_LAYER}_ext.npz").relative_to(ROOT)),
                                   "extent_4326": ext10.tolist(), "kind": "10pct flood-extent mask (no depth)"}
        print(f"  {s['name']:22s} ble_image field @ ~{rec['rasters']['100']['px_m']:.0f} m/px (+10yr extent)")
        if "proving" in s["role"] or "all-three" in s["role"]:   # proving + all-three BLE sites get NSS densification (JD-FL-8)
            comid, da_mi2 = reach_drainage_area_mi2(s["lat"], s["lon"])
            Q = nss_q_curve(da_mi2, SLOPE_FT_MI)
            b_tail = (math.log(Q[100]) - math.log(Q[50])) / (math.log(100) - math.log(50))
            Q500 = math.exp(math.log(Q[100]) + b_tail * (math.log(500) - math.log(100)))
            flow_frequency[s["name"]] = {"comid": int(comid), "drainage_area_mi2": round(da_mi2, 2), "slope_ft_mi": SLOPE_FT_MI,
                                         "regression": "USGS NSS — LA Coastal Plain SIR 2024-5031 (GC1889)",
                                         "Q_cfs": {int(k): round(v) for k, v in Q.items()}, "Q500_cfs_extrap": round(Q500)}
            print(f"     flow-frequency: comid {comid}, DA {da_mi2:.1f} mi^2 | Q100={round(Q[100])} Q500~{round(Q500)} cfs")
    elif s["method"] == "sfha_bathtub":
        tb = pd.read_parquet(OUT / f"{s['slug']}_flood_wind_m0_geometry.parquet")
        minx, miny = tb["lon"].min(), tb["lat"].min(); maxx, maxy = tb["lon"].max(), tb["lat"].max()
        area = flood_area(min(minx, s["sub_lon"]), min(miny, s["sub_lat"]), max(maxx, s["sub_lon"]), max(maxy, s["sub_lat"]), SFHA_WHERE)
        bxy, bz = boundary_samples(area, cache=RAW / f"bnd_{s['slug']}_rp100.json")
        rec["frac_sfha"] = s["frac_sfha"]
        # de-inline the (large) SFHA polygon → gitignored raw/, store a PATH (mirrors the ble_image raster pattern;
        # keeps the tracked manifest lightweight — NC Zone A alone is ~10 MB of WKT). M2 loads it from the path.
        fa_dir = RAW / "flood_area"; fa_dir.mkdir(parents=True, exist_ok=True)
        fa_path = fa_dir / f"{s['slug']}.wkt"; fa_path.write_text(area.wkt)
        rec["flood_area_path"] = str(fa_path.relative_to(ROOT))
        rec["wse_contour"] = {"xy": bxy.tolist(), "z": bz.tolist()}
        gsite = GAUGE_BY_SITE.get(s["slug"])                 # this site's OWN gauge (per-site, JD-FL-19 fix)
        if gsite is None:
            raise KeyError(f"no gauge mapped for bathtub site {s['slug']} — add it to GAUGE_BY_SITE")
        QT, GN, GSKEW = gauge_QT(gsite, RPS_GAUGE)
        gblock = {"site": gsite, "n_peaks": GN, "log_skew": round(GSKEW, 3),
                  "Q_cfs": {int(k): round(v) for k, v in QT.items()}, "rating_exp_b": 0.6}
        gauges[s["slug"]] = gblock; rec["gauge"] = gblock    # per-site — M2 reads rec["gauge"], not one global block
        print(f"  {s['name']:22s} sfha_bathtub field ({s['frac_sfha']*100:.0f}% SFHA) | gauge {gsite}: {GN}-yr peaks, "
              f"log-skew {GSKEW:.2f}, Q100={int(QT[100])} Q500={int(QT[500])} cfs")
    else:                                                    # dry baseline
        rec["frac_sfha"] = s.get("frac_sfha", 0.0); rec["flood_area_path"] = None; rec["wse_contour"] = None
        print(f"  {s['name']:22s} DRY baseline")
    field.append(rec)

# %% [markdown]
# ## 4 · Emit the shared field manifest (one `field` list, method-tagged; both `Q(T)` provenances)

# %%
manifest = {
    "peril": "flood", "sub_peril": "riverine", "event_family_id": None, "layer": "M1",
    "kind": "shared asset-independent field, ALL sites, method-per-site (Path 2 / JD-FL-19) — footprint/per-node coupling is M2's job",
    "methods": {"ble_image": "FEMA BLE depth grids as full-resolution image (JD-FL-18); Q(T) from NLDI→NSS (JD-FL-8)",
                "sfha_bathtub": "1% flood area + boundary WSE contour off 3DEP (JD-FL-W4); Q(T) from gauge Log-Pearson III (JD-FL-W5)",
                "dry": "site not in SFHA → no riverine field"},
    "ble": {"service": "txgeo.usgs.gov/.../FEMA_EBFE/EBFE/MapServer (layers 12,16,7)",
            "depth_bands_ft": BAND_MID_FT.tolist(), "return_periods_tail_yr": [100, 500]},
    "flow_frequency": flow_frequency,                       # ble_image sites — solar M2 reads this
    "gauges": gauges,                                        # sfha_bathtub sites — PER SITE (slug → gauge); each field row also carries rec["gauge"]
    "field": field,
    "caveats": ["Method is by site data availability, not asset (JD-FL-6). No footprint/per-node reduction here (M2's job, JD-FL-19).",
                "ble_image: depth is BANDED (6 classes, JD-FL-18); BLE tail only (100/500-yr), lower RPs densified in M2 (JD-FL-8).",
                "sfha_bathtub: Zone A has no engineered depth; ΔWSE(T) from gauge applied in M2 (JD-FL-W5)."],
}
(OUT / "flood_riverine_m1_catalog_manifest.json").write_text(json.dumps(manifest, indent=2))
print("\nwrote:", OUT / "flood_riverine_m1_catalog_manifest.json",
      f"({len(field)} site fields — {sum(f['method']=='ble_image' for f in field)} ble, "
      f"{sum(f['method']=='sfha_bathtub' for f in field)} bathtub, {sum(f['method']=='dry' for f in field)} dry)")
