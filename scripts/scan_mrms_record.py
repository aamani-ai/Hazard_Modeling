#!/usr/bin/env python3
"""
Stage-1 frequency widening (DD-3): scan the FULL MRMS-on-AWS record over the Hayhurst 50-mi region.

Mirrors the 02_mrms_aws notebook's scan logic exactly (same asset, region mask, threshold, daily grain),
but over the full ~2020-10 → present record — too long for a notebook cell. Concurrent + cache-first +
resumable: downloads each day's last (≈24-h-max) MESH tile, caches the raw bytes under data/hail/mrms_raw/,
and computes the region-max / footprint per day. Writes a WIDE M0 parquet the catalog (M1) then consumes.

Run (background):  python scripts/scan_mrms_record.py 2020-10-15 2026-06-08
Re-runnable: cached tiles are skipped, so a re-run resumes.
"""
from __future__ import annotations
import os, gzip, json, math, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
import numpy as np
import pandas as pd
import xarray as xr

# --- asset + region config (identical to 02_mrms_aws) ---
ASSET = {"name": "Hayhurst Texas Solar", "lat": 31.815992, "lon": -104.0853}
RADIUS_MI, THRESHOLD_MM = 50, 25.4
PRODUCT = "CONUS/MESH_Max_1440min_00.50"
RES_DEG = 0.01
PX_KM2 = (RES_DEG * 111.32) * (RES_DEG * 111.32 * math.cos(math.radians(ASSET["lat"])))
N_WORKERS = 8

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "hail" / "mrms_raw"
CACHE.mkdir(parents=True, exist_ok=True)
MPATH = CACHE / "_manifest.json"
BUCKET = "https://noaa-mrms-pds.s3.amazonaws.com"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"

_manifest = json.loads(MPATH.read_text()) if MPATH.exists() else {}
_lock = threading.Lock()

def box_from_radius(lat, lon, r_mi):
    dlat = r_mi / 69.0; dlon = r_mi / (69.0 * math.cos(math.radians(lat)))
    return {"lat_lo": lat - dlat, "lat_hi": lat + dlat, "lon_lo": lon - dlon, "lon_hi": lon + dlon}
BOX = box_from_radius(ASSET["lat"], ASSET["lon"], RADIUS_MI)

def region_mask(sub, lat0, lon0, r_mi):
    LO, LA = np.meshgrid(sub.longitude.values, sub.latitude.values)
    lon180 = np.where(LO > 180, LO - 360, LO)
    R = 3958.8
    dphi = np.radians(LA - lat0); dl = np.radians(lon180 - lon0)
    a = np.sin(dphi / 2) ** 2 + np.cos(np.radians(lat0)) * np.cos(np.radians(LA)) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a)) <= r_mi

def _session():
    s = requests.Session()
    s.mount("https://", requests.adapters.HTTPAdapter(pool_connections=N_WORKERS, pool_maxsize=N_WORKERS, max_retries=2))
    return s
_SESS = _session()

def get_day(ymd):
    """Local path to the day's last (≈24-h-max) tile; download+cache if needed. None if no tile."""
    fn = _manifest.get(ymd)
    if fn and (CACHE / fn).exists():
        return CACHE / fn
    r = _SESS.get(BUCKET + "/", params={"list-type": "2", "prefix": f"{PRODUCT}/{ymd}/", "max-keys": "1000"}, timeout=40)
    r.raise_for_status()
    keys = sorted(e.find(NS + "Key").text for e in ET.fromstring(r.text).findall(NS + "Contents"))
    if not keys:
        return None
    key = keys[-1]; fn = key.split("/")[-1]; local = CACHE / fn
    if not local.exists():
        rr = _SESS.get(f"{BUCKET}/{key}", timeout=120); rr.raise_for_status()
        local.write_bytes(rr.content)
    with _lock:
        _manifest[ymd] = fn
    return local

def region_stats(ymd):
    """Download+read one day, mask to the 50-mi circle, return region-max / footprint stats. None on no-tile/error."""
    try:
        gz = get_day(ymd)
        if gz is None:
            return {"date": ymd, "status": "no_tile"}
        raw = gzip.decompress(Path(gz).read_bytes())
        with tempfile.NamedTemporaryFile(suffix=".grib2", delete=False) as tf:
            tf.write(raw); tmp = tf.name
        try:
            ds = xr.open_dataset(tmp, engine="cfgrib", backend_kwargs={"indexpath": ""}); ds.load()
            da = ds[list(ds.data_vars)[0]]
        finally:
            os.unlink(tmp)
        la, lo = da.latitude.values, da.longitude.values
        li = np.where((la >= BOX["lat_lo"]) & (la <= BOX["lat_hi"]))[0]
        oi = np.where((lo >= BOX["lon_lo"] % 360) & (lo <= BOX["lon_hi"] % 360))[0]
        sub = da.isel(latitude=li, longitude=oi)
        arr = np.where(sub.values.astype("float64") < 0, np.nan, sub.values.astype("float64"))
        arr = np.where(region_mask(sub, ASSET["lat"], ASSET["lon"], RADIUS_MI), arr, np.nan)
        if not np.isfinite(arr).any():
            return {"date": ymd, "status": "ok", "region_max_mm": np.nan, "n_above_px": 0, "footprint_km2": 0.0}
        above = arr >= THRESHOLD_MM
        return {"date": ymd, "status": "ok", "region_max_mm": float(np.nanmax(arr)),
                "n_above_px": int(np.nansum(above)), "footprint_km2": round(float(np.nansum(above)) * PX_KM2, 1)}
    except Exception as e:
        return {"date": ymd, "status": f"error:{str(e)[:60]}"}

def main(start, end):
    dates = [d.strftime("%Y%m%d") for d in pd.date_range(start, end, freq="D")]
    print(f"[scan] {len(dates)} days  {start} → {end}  | region {RADIUS_MI}mi | threshold {THRESHOLD_MM}mm | workers {N_WORKERS}",
          flush=True)
    rows, done = [], 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(region_stats, d): d for d in dates}
        for fut in as_completed(futs):
            rows.append(fut.result()); done += 1
            if done % 100 == 0:
                MPATH.write_text(json.dumps(_manifest))   # periodic flush (resumability)
                print(f"[scan] {done}/{len(dates)} days …", flush=True)
    MPATH.write_text(json.dumps(_manifest))
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    ok = df[df.status == "ok"].copy(); ok["date"] = pd.to_datetime(ok["date"])
    n_notile = int((df.status == "no_tile").sum()); n_err = int(df.status.str.startswith("error").sum())
    out = ROOT / "data" / "hail" / f"hayhurst_hail_m0_mrms_{start[:7].replace('-','')}_{end[:7].replace('-','')}.parquet"
    ok[["date", "region_max_mm", "n_above_px", "footprint_km2"]].to_parquet(out, index=False)
    yrs = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    hail_days = int((ok.n_above_px > 0).sum())
    print(f"[scan] DONE. read {len(ok)} days | no_tile {n_notile} | errors {n_err}", flush=True)
    print(f"[scan] hail-days (≥{THRESHOLD_MM}mm in region): {hail_days} over {yrs:.2f} yr "
          f"→ λ_collection ≈ {hail_days/yrs:.1f}/yr (raw count; M1 fits + tests dispersion)", flush=True)
    print(f"[scan] wide M0 → {out}", flush=True)

if __name__ == "__main__":
    s = sys.argv[1] if len(sys.argv) > 1 else "2020-10-15"
    e = sys.argv[2] if len(sys.argv) > 2 else "2026-06-08"
    main(s, e)
