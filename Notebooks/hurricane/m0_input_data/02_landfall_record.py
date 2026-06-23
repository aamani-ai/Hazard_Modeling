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
# # Hurricane — M0 input data: the observed landfall record (HURDAT2) — frequency anchor + severity targets
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Layer:** M0 (raw evidence) · method-neutral
#
# **Magnitude metric:** the hurricane wind peril's damage observable is the **3-second peak gust (mph)**, built in M1
# from the Holland (1980) wind field on storm tracks. HURDAT2 here carries **observed max *sustained* wind (knots)**,
# used two ways: the **rate anchor** (landfall frequency) and the **validation targets** (observed landfall
# intensities the Holland field must reproduce). *(Surge/rain are flood's `[C]`/`[F]`, cross-linked, not modeled here.)*
#
# **Data source:** **HURDAT2** — NOAA/NHC **Atlantic hurricane best-track record** (1851–2023), public-domain fixed-format text.
#
# **What this notebook does:** parses the observed Atlantic best-track record — the truth that **brackets** the
# synthetic RAFT catalog from [01](01_raft_catalog.ipynb) — and produces the two things the synthetic catalog can't
# supply for itself:
#
# 1. **The rate anchor.** RAFT's raw ~1000 storms/env-year is a **~71× genesis oversample**, so the physical
#    frequency comes from the **observed landfall rate**. The notebook reproduces the **published US
#    hurricane-landfall climatology (~1.7/yr)** as a known-answer, restricting landfalls to a CONUS coastal box at
#    hurricane intensity.
# 2. **The severity validation targets.** The per-storm observed **landfall intensities** are what M1's Holland wind
#    field must reproduce on historical tracks ([JD-TC-7](../../../docs/plans/hurricane/decisions.md)).
#
# It emits the US landfall catalog (`tc_m0_hurdat2_landfalls.parquet`) and the hurricane-intensity track points
# (`tc_m0_hurdat2_tracks_hu.parquet`, all ≥64 kt obs for M1's close-passage counting) plus manifest. The STORM RP-grid
# cross-check (a 1.1 GB, site-dependent download) is performed in M1; M0/02 is the **site-independent** observed record.
#
# > Plan: [`m0_input_data.md`](../../../docs/plans/hurricane/m0_input_data.md) · Decisions:
# > [`decisions.md`](../../../docs/plans/hurricane/decisions.md) (JD-TC-3/7) · prior: [01](01_raft_catalog.ipynb).

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **HURDAT2** — NOAA/NHC **Atlantic hurricane best-track record** (1851–2023): the *observed* truth that brackets
#   the synthetic RAFT catalog. **Role:** the two jobs RAFT can't do for itself — the **rate anchor** (reproduce the
#   published US hurricane-landfall climatology, ~1.7/yr) and the **validation targets** (observed landfall
#   intensities M1's Holland field must reproduce). **Access:** public NHC fixed-format text
#   (`nhc.noaa.gov/data/hurdat/`), **public domain**; cached at `data/hurricane/raw/hurdat2_atlantic.txt` → offline,
#   idempotent. **Magnitude basis:** `max_wind_kt` = **max sustained wind, knots (1-min)** (× 1.150779 = mph; not a gust).
#
# ⚠️ **Caveats (carried):** best-track intensities are operational estimates with evolving methods across ~170 yr;
# landfalls are flagged by `record_id == 'L'`. **Reproducibility:** the observed catalog (rate anchor + M1 targets)
# is persisted to `data/hurricane/tc_m0_hurdat2_landfalls.parquet` / `…_tracks_hu.parquet`
# (+ `tc_m0_hurdat2_manifest.json`).

# %%
import json, re
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
RAW = ROOT / "data" / "hurricane" / "raw"
OUT = ROOT / "data" / "hurricane"
RAW.mkdir(parents=True, exist_ok=True)
KT_TO_MPH = 1.150779
print("repo root:", ROOT)

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-9** the observed HURDAT2 rate is the **frequency anchor** (calibrates RAFT's oversample in M1) · **ATC-8**
# wind in **knots → mph ×1.150779** (sustained, not a gust) · **ATC-10** the observed landfall intensities are the
# **validation targets** for M1's Holland replay · **ATC-17** self-serve public data. Full register:
# [`assumptions.md`](../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · Fetch HURDAT2 (Atlantic best tracks, 1851–2023)
#
# Source: **NHC HURDAT2** — the canonical US Atlantic best-track record (public domain). One text file, a peculiar
# fixed format: a **header line** per storm (`AL<num><year>, NAME, <n_track_lines>`) followed by `n` **data lines**
# (date, time, record-id, status, lat, lon, max-wind, pressure, wind-radii). Winds are **knots** (as RAFT — §2/01).

# %%
HURDAT_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
HURDAT_TXT = RAW / "hurdat2_atlantic.txt"
if not HURDAT_TXT.exists():
    print("downloading HURDAT2 …")
    r = requests.get(HURDAT_URL, timeout=120); r.raise_for_status()
    HURDAT_TXT.write_text(r.text)
lines = HURDAT_TXT.read_text().splitlines()
print(f"HURDAT2: {len(lines):,} lines  ({HURDAT_TXT.stat().st_size/1e6:.1f} MB)")
print("sample header + first track line:")
print(" ", lines[0]); print(" ", lines[1])

# %% [markdown]
# ## 2 · Parse the fixed format → a tidy per-observation table
#
# Header rows start with the storm id `AL\d{6}`; everything else is a 6-hourly observation of the *current* storm.
# We parse lat/lon (`28.0N`/`94.8W` → signed degrees), max wind (knots), status, and the **record identifier**
# (`L` = **landfall**, the field we most need). `-999` = missing.

# %%
def parse_latlon(tok):
    v = float(tok[:-1]); h = tok[-1]
    return -v if h in ("S", "W") else v

rows = []
cur_id = cur_name = None; cur_year = None
hdr = re.compile(r"^(AL|EP|CP)\d{6}$")
for ln in lines:
    p = [x.strip() for x in ln.split(",")]
    if hdr.match(p[0]):
        cur_id, cur_name, cur_year = p[0], p[1], int(p[0][4:8])
    elif len(p) >= 7 and p[0]:
        wind = int(p[6])
        rows.append({
            "storm_id": cur_id, "name": cur_name, "year": cur_year,
            "date": p[0], "time": p[1], "record_id": p[2], "status": p[3],
            "lat": parse_latlon(p[4]), "lon": parse_latlon(p[5]),
            "max_wind_kt": np.nan if wind == -999 else wind,
        })
obs = pd.DataFrame(rows)
n_storms = obs["storm_id"].nunique()
print(f"parsed {len(obs):,} observations · {n_storms:,} storms · years {obs['year'].min()}–{obs['year'].max()}")
print("\nstatus codes present:", sorted(obs["status"].unique()))
print("record-id values:", sorted(obs["record_id"].replace("", "·").unique()))

# %% [markdown]
# ## 3 · Field dictionary (the discipline)
#
# | Field | Meaning | Units / base | ⚠ what it's NOT |
# |---|---|---|---|
# | `status` | system type at the obs | `HU` hurricane · `TS` trop. storm · `TD` dep. · `EX` extratrop. · etc. | not an intensity number |
# | `record_id` | special marker | **`L` = landfall** · `C/G/I/...` other | blank = ordinary 6-hr obs |
# | `max_wind_kt` | max sustained wind | **knots** (1-min) | NOT mph (×1.150779), NOT a gust |
# | `lat`/`lon` | center | signed degrees | — |
#
# Saffir-Simpson (sustained, knots): hurricane = **≥ 64 kt** (`HU`); major = **≥ 96 kt** (Cat3+).

# %%
land = obs[obs["record_id"] == "L"].copy()
print(f"landfall records (record_id == 'L'): {len(land):,}  across {land['storm_id'].nunique():,} storms")
print(f"  of which at hurricane intensity (≥64 kt): {(land['max_wind_kt'] >= 64).sum():,}")
print("landfall intensity (kt): " +
      f"median {land['max_wind_kt'].median():.0f} · max {land['max_wind_kt'].max():.0f} "
      f"({land['max_wind_kt'].max()*KT_TO_MPH:.0f} mph)")

# %% [markdown]
# ## 4 · 🔑 The rate anchor — reproduce the published US hurricane-landfall climatology
#
# This is the number that calibrates RAFT's oversample. We restrict landfalls to a **CONUS coastal box**
# (`lon −98…−67, lat 24…47`) at **hurricane intensity** and count **storms making US landfall per year**. The
# published NOAA/Klotzbach climatology is **~1.7 CONUS hurricane landfalls/yr** (~0.46 major/yr) — our known-answer.
#
# *(The box is a coarse CONUS proxy — it can nick NE Mexico / the Bahamas — so we expect the right order, ~1.5–2.0/yr,
# not a decimal match. The precise per-site close-passage rate is M1's job, with this as the regional anchor.)*

# %%
YEARS = obs["year"].max() - obs["year"].min() + 1
in_conus = land["lon"].between(-98, -67) & land["lat"].between(24, 47)
us_hu = land[in_conus & (land["max_wind_kt"] >= 64)]
us_major = land[in_conus & (land["max_wind_kt"] >= 96)]
# count distinct storms per year that made a US hurricane landfall, then annual rate
hu_storms_per_yr = us_hu.groupby("year")["storm_id"].nunique()
major_storms_per_yr = us_major.groupby("year")["storm_id"].nunique()
rate_hu = hu_storms_per_yr.sum() / YEARS
rate_major = major_storms_per_yr.sum() / YEARS
print(f"record span: {YEARS} years")
print(f"US hurricane landfalls: {rate_hu:.2f} storms/yr   (published ~1.7/yr)")
print(f"US major (≥Cat3) landfalls: {rate_major:.2f} storms/yr   (published ~0.46/yr)")
print(f"\nmost-recent decades (storms with a US hurricane landfall):")
print(hu_storms_per_yr[hu_storms_per_yr.index >= 2014].to_string())

# %% [markdown]
# ## 5 · Known-answer checks (basics-spot-on)

# %%
checks = {
    "parsed a plausible storm count (>1500 since 1851)": n_storms > 1500,
    "years span 1851–2023": (obs["year"].min() == 1851 and obs["year"].max() == 2023),
    "HU status present and landfalls exist": ("HU" in obs["status"].values and len(land) > 0),
    "landfall winds in knots range (max 130–175 kt)": 130 <= land["max_wind_kt"].max() <= 175,
    "US hurricane-landfall rate ~published 1.7/yr (order: 1.4–2.2)": 1.4 <= rate_hu <= 2.2,
    "US major-landfall rate ~published 0.46/yr (order: 0.3–0.7)": 0.3 <= rate_major <= 0.7,
    "major rate < hurricane rate (majors are a subset)": rate_major < rate_hu,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "a known-answer check failed"
print("\nall M0/02 known-answer checks pass ✅  — parse validated, rate anchor reproduces published climatology")

# %% [markdown]
# ## 6 · Emit — the observed catalog (rate anchor + M1 validation targets)
#
# **Two products, so M1 can use the *same rulebook* for frequency as for severity:**
# 1. **Landfall catalog** (`record_id == 'L'`) — the strict landfall record (validation targets for the Holland
#    replay; a conservative cross-check rate).
# 2. **🔑 Hurricane-intensity *track points*** (every 6-hourly obs at ≥ 64 kt, not just landfalls) — so M1 can count
#    **close passages within 100 km of a site** (a storm brushing offshore still brings wind). This matches RAFT's
#    "center within 100 km" severity definition exactly — fixing the *different-rulebooks* gap (one definition on
#    both sides of frequency × severity).

# %%
land_us = land[in_conus].copy()
land_us["max_wind_mph"] = land_us["max_wind_kt"] * KT_TO_MPH
keep = ["storm_id", "name", "year", "date", "time", "status", "lat", "lon", "max_wind_kt", "max_wind_mph"]
out_path = OUT / "tc_m0_hurdat2_landfalls.parquet"
land_us[keep].to_parquet(out_path, index=False)
print(f"wrote {out_path}  ({len(land_us):,} US landfall records)")

# hurricane-intensity track points (≥64 kt) — ANY obs, for site close-passage counting in M1
tracks_hu = obs[obs["max_wind_kt"] >= 64][["storm_id", "name", "year", "date", "time", "lat", "lon", "max_wind_kt"]].copy()
tracks_path = OUT / "tc_m0_hurdat2_tracks_hu.parquet"
tracks_hu.to_parquet(tracks_path, index=False)
print(f"wrote {tracks_path}  ({len(tracks_hu):,} hurricane-intensity track points, "
      f"{tracks_hu['storm_id'].nunique():,} storms — for M1 close-passage rate)")

manifest = {
    "notebook": "hurricane/m0_input_data/02_landfall_record",
    "source": "NOAA NHC HURDAT2 Atlantic best-track",
    "url": HURDAT_URL,
    "license": "public domain (NOAA)",
    "record_years": [int(obs["year"].min()), int(obs["year"].max())],
    "n_storms_total": int(n_storms),
    "n_landfall_records": int(len(land)),
    "units": {"max_wind": "knots (1-min sustained)"},
    "us_landfall_climatology": {
        "conus_box": {"lon": [-98, -67], "lat": [24, 47]},
        "hurricane_per_yr": round(float(rate_hu), 3),
        "major_per_yr": round(float(rate_major), 3),
        "published_reference": {"hurricane_per_yr": 1.7, "major_per_yr": 0.46},
    },
    "role": [
        "rate anchor: calibrates RAFT's ~71x oversample to physical landfall frequency (ATC-9, applied in M1)",
        "validation targets: observed landfall intensities for Holland field replay (JD-TC-7, M1)",
    ],
    "deferred": "STORM RP-grid cross-check → M1 (needs locked site + 1.1 GB download; validates our catalog RP)",
    "outputs": {"landfalls_parquet": str(out_path.relative_to(ROOT)),
                "tracks_hu_parquet": str(tracks_path.relative_to(ROOT))},
    "tracks_hu_note": "all ≥64 kt obs (not just landfalls) → M1 counts close passages within 100 km, matching RAFT's severity rulebook",
}
man_path = OUT / "tc_m0_hurdat2_manifest.json"
man_path.write_text(json.dumps(manifest, indent=2))
print("wrote", man_path)

# %% [markdown]
# ## Takeaways → next
#
# - **HURDAT2 parsed & validated** — the observed Atlantic record reproduces the **published US hurricane-landfall
#   climatology (~1.7/yr)**, so it is a trustworthy **rate anchor** for the RAFT oversample ([01](01_raft_catalog.ipynb)).
# - **Landfall intensities captured** as the **validation targets** for M1's Holland field replay.
# - **Winds are knots again** (×1.150779 → mph) — consistent with RAFT.
# - **STORM RP-grid cross-check deferred to M1** (site-dependent + 1.1 GB).
# - Emitted `tc_m0_hurdat2_landfalls.parquet` + manifest.
#
# **Next → [03_site_geometry](03_site_geometry.py):** lock the four solar sites (Hayhurst baseline, screened Everglades high,
# and the Discovery/LA3 cross-link riders) and their geometry/TIV — after which M1 filters both RAFT (01) and these landfalls (02) to
# each site, calibrates the rate, and builds the Holland field.
