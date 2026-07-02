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
# # Hurricane · Solar — M0 input data: lock the solar sites + footprint geometry + TIV
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Layer:** M0 (raw evidence) · method-neutral
#
# **Magnitude metric (screening):** **HURDAT2 hurricane-intensity (≥64 kt) landfalls within 100 km** of each candidate
# plant — a frequency proxy that ranks coastal exposure. The damage magnitude itself (the **3-second peak gust, mph**)
# is sampled at these locked sites in M1; this notebook carries no gust, only the *where* (geometry + TIV).
# *(Surge/rain = flood's `[C]`/`[F]`, cross-linked, not modeled here.)*
#
# **Data source:** **EIA-860** (2024 operating solar fleet — the screen population, reused from the flood cell's
# cache) and the **HURDAT2** landfall record from [02](02_landfall_record.ipynb) (the screen metric).
#
# **What this notebook does:** locks the solar sites as a deliberate **low-vs-high** hurricane-wind contrast (the
# strongest validation a hazard model can have: ~zero loss where the peril is absent, material where it's common). It
# **reuses Hayhurst** (TX desert) as the near-zero-TC baseline (same asset as hail/wildfire/flood → cross-peril
# coherence) and **screens the national solar fleet** for a **Gulf/SE-Atlantic-coast high site**, ranking utility-scale
# coastal plants by observed hurricane-landfall density within 100 km. The screened high site here is **Everglades**
# (FL). It assigns geometry via the **capacity→radius circle** + centroid and TIV via $/MW, runs known-answer checks
# (Hayhurst reads ~0 landfalls; high site materially exposed), and emits the locked pair (`tc_m0_sites.json`) plus the
# screen audit (`tc_m0_site_screen.csv`). *(Downstream M1/M4 also append cross-link rider sites — Discovery and LA3
# West Baton Rouge — to supply the wind leg for flood-coastal × solar; they are not hurricane proving sites and are
# excluded from the hurricane headline.)*
#
# | role | asset | where | screen metric |
# |---|---|---|---|
# | **baseline (low-TC)** | **Hayhurst Texas Solar** (EIA 66880) | Culberson Co., **TX** — Chihuahuan desert | expect **~0** hurricane landfalls nearby (true zero) |
# | **proving (high-TC)** | *chosen below* | **Gulf / SE-Atlantic coast** | most **HURDAT2 hurricane landfalls within 100 km** |
#
# > **Coastal on purpose.** The high site is coastal not just for wind — it's the future **surge** cross-link ground
# > ([JD-TC-4/5](../../../docs/plans/hurricane/decisions.md)); landfall-density screening inherently favors the coast.
# > Geometry uses the **capacity→radius circle** (the hail/wildfire/flood fallback) — fine here because solar's
# > field-intensity coupling is **spatially degenerate** (one centroid sample), so a real polygon adds little in V1.
# >
# > Plan: [`m0_input_data.md`](../../../docs/plans/hurricane/m0_input_data.md) · Decisions:
# > [`decisions.md`](../../../docs/plans/hurricane/decisions.md) (JD-TC-5) · prior: [01](01_raft_catalog.ipynb), [02](02_landfall_record.ipynb).

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# Site selection reuses two sources already met — named here so the screen's provenance is up-front:
#
# - **EIA-860** (2024 operating solar fleet) — the screen **population** (every utility-scale solar plant: name,
#   EIA id, lat/lon, capacity). **Access:** Form EIA-860 bulk ZIP, **reused from the flood cell's cache**
#   (`data/flood/raw/eia860_2024.zip`); no re-download. **Units:** capacity in MW.
# - **HURDAT2 landfalls** (from [02](02_landfall_record.ipynb)) — the screen **metric**: observed
#   **hurricane-landfall density within 100 km** of each candidate. **Access:** the cached observed catalog from M0/02.
#
# ⚠️ **Caveats (carried):** geometry = **capacity→radius circle** (solar's field-intensity coupling is spatially
# degenerate — one centroid sample — so a real polygon adds little in V1); the coastal high site doubles as the
# future **surge** cross-link ground (JD-TC-4/5). **Reproducibility:** the locked pair + screen audit are persisted
# to `data/hurricane/tc_m0_sites.json` + `tc_m0_site_screen.csv`.

# %% [markdown]
# ## Field dictionary — the screen sources
#
# | field | what it is | units / base | source | how we use it |
# |---|---|---|---|---|
# | `plant_name`, `eia_id` | plant identity | string / id | EIA-860 | label the fleet |
# | `latitude`, `longitude` | plant location | degrees, EPSG:4326 | EIA-860 | distance to landfalls; lock the site |
# | `nameplate_mw` | generator capacity | MW | EIA-860 | utility-scale filter; capacity→radius geometry; TIV basis |
# | `landfalls_100km` | observed hurricane landfalls within 100 km | count | HURDAT2 (02) | the high-TC **screen metric** |
# | `role` | baseline (low) vs proving (high) | categorical | derived | the low-vs-high contrast |

# %%
import json, math, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "hurricane"
# reuse the EIA-860 fleet cached by the flood cell (same national solar population)
EIA_ZIP = ROOT / "data" / "flood" / "raw" / "eia860_2024.zip"
TIV_PER_MW = 1.483e6        # $/MW — Hayhurst hail basis (flood AFL-16); coastal site estimated by capacity
print("repo root:", ROOT, "| EIA zip exists:", EIA_ZIP.exists())

def cap_radius_m(mw):
    return 69.0 * math.sqrt(mw * 1.3)   # capacity→radius proxy (DC≈AC·1.3), the hail/wildfire/flood fallback

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1); dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dlmb/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-16** sites = screened Gulf/Atlantic-coast solar (high) + **Hayhurst reused** (low); **TIV from $/MW**,
# coastal site estimated by capacity · **ATC-13** solar = dense areal polygon (capacity→radius circle here; field is
# degenerate so a real polygon adds little) · **ATC-17** self-serve public data (EIA-860 reused; HURDAT2 from 02).
# Full register: [`assumptions.md`](../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · The national solar fleet (EIA-860, reused) + the observed landfall record (02)

# %%
with zipfile.ZipFile(EIA_ZIP) as z:
    with z.open("2___Plant_Y2024.xlsx") as f:
        plant = pd.read_excel(f, skiprows=1)
    with z.open("3_3_Solar_Y2024.xlsx") as f:
        solar = pd.read_excel(f, skiprows=1)
solar["Nameplate Capacity (MW)"] = pd.to_numeric(solar["Nameplate Capacity (MW)"], errors="coerce")
cap = solar[solar["Status"] == "OP"].groupby("Plant Code")["Nameplate Capacity (MW)"].sum().rename("solar_mw")
fleet = (plant.set_index("Plant Code").join(cap, how="inner").reset_index()
              .dropna(subset=["Latitude", "Longitude"]))
fleet = fleet[["Plant Code", "Plant Name", "State", "County", "solar_mw", "Latitude", "Longitude"]]
print(f"operating solar plants nationwide: {len(fleet):,}  |  total {fleet['solar_mw'].sum():,.0f} MW")

# HURDAT2 US hurricane-intensity landfalls (≥64 kt) from notebook 02
land = pd.read_parquet(OUT / "tc_m0_hurdat2_landfalls.parquet")
land_hu = land[land["max_wind_kt"] >= 64].reset_index(drop=True)
print(f"HURDAT2 US hurricane-intensity landfalls (≥64 kt): {len(land_hu):,}")

# %% [markdown]
# ## 2 · Screen — coastal, utility-scale, ranked by observed hurricane-landfall density
#
# Restrict to the **Gulf / SE-Atlantic hurricane belt** (TX, LA, MS, AL, FL, GA, SC, NC, VA), utility-scale
# (≥ 20 MW), and score each plant by the **number of HURDAT2 hurricane landfalls within 100 km** over the 1851–2023
# record. Highest = the proving site.

# %%
COAST_STATES = ["TX", "LA", "MS", "AL", "FL", "GA", "SC", "NC", "VA"]
RADIUS_KM = 100.0
cand = fleet[fleet["State"].isin(COAST_STATES) & (fleet["solar_mw"] >= 20.0)].copy().reset_index(drop=True)

ll_lat = land_hu["lat"].values; ll_lon = land_hu["lon"].values
def landfalls_within(lat, lon, r=RADIUS_KM):
    return int((haversine_km(lat, lon, ll_lat, ll_lon) <= r).sum())
cand["landfalls_100km"] = [landfalls_within(r.Latitude, r.Longitude) for r in cand.itertuples()]
ranked = cand.sort_values(["landfalls_100km", "solar_mw"], ascending=False).reset_index(drop=True)
print(f"coastal utility-scale candidates: {len(cand)}  (states {COAST_STATES}, ≥20 MW)")
print("\ntop 10 by observed hurricane-landfall density (within 100 km):")
print(ranked.head(10)[["Plant Name", "State", "County", "solar_mw", "Latitude", "Longitude", "landfalls_100km"]].to_string(index=False))

# %% [markdown]
# ## 3 · Lock the pair — screened high site + Hayhurst baseline
#
# The top-ranked plant is the **proving** site. **Hayhurst** is the fixed baseline; we score it on the *same* metric
# to prove the contrast (it should read **~0** landfalls — West-Texas desert, ~700 km inland).

# %%
high = ranked.iloc[0]
hay = {"name": "Hayhurst Texas Solar", "eia": 66880, "state": "TX", "county": "Culberson",
       "lat": 31.815992, "lon": -104.085297, "solar_mw": 24.8}
hay_landfalls = landfalls_within(hay["lat"], hay["lon"])

sites = pd.DataFrame([
    {"role": "baseline (low-TC)", "name": hay["name"], "eia": hay["eia"], "state": hay["state"],
     "county": hay["county"], "lat": hay["lat"], "lon": hay["lon"], "solar_mw": hay["solar_mw"],
     "landfalls_100km": hay_landfalls},
    {"role": "proving (high-TC)", "name": high["Plant Name"], "eia": int(high["Plant Code"]),
     "state": high["State"], "county": high["County"], "lat": float(high["Latitude"]),
     "lon": float(high["Longitude"]), "solar_mw": float(high["solar_mw"]),
     "landfalls_100km": int(high["landfalls_100km"])},
])
sites["footprint_r_m"] = sites["solar_mw"].map(lambda mw: round(cap_radius_m(mw)))
sites["tiv_usd"] = (sites["solar_mw"] * TIV_PER_MW).round(0)
print(sites.to_string(index=False))

# %% [markdown]
# ## 4 · Known-answer checks (basics-spot-on)

# %%
checks = {
    "Hayhurst baseline reads ~0 hurricane landfalls nearby (true-zero control)": hay_landfalls == 0,
    "high site is materially exposed (≥3 landfalls within 100 km)": high["landfalls_100km"] >= 3,
    "high site is in a Gulf/SE-Atlantic state": high["State"] in COAST_STATES,
    "clear contrast (high site ≫ baseline)": high["landfalls_100km"] > hay_landfalls + 2,
    "both sites utility-scale (≥20 MW)": bool((sites["solar_mw"] >= 20).all()),
    "TIV positive both sites": bool((sites["tiv_usd"] > 0).all()),
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "a known-answer check failed"
print(f"\nall M0/03 known-answer checks pass ✅  — high site: {high['Plant Name']} ({high['State']}), "
      f"{high['landfalls_100km']} landfalls/100km vs Hayhurst {hay_landfalls}")

# %% [markdown]
# ## 5 · Emit — the locked site pair + screen audit
#
# House convention: manifest/summary → JSON (kept); the screen audit → CSV (small, diffable). Both feed M1, which
# filters RAFT ([01](01_raft_catalog.ipynb)) and the landfalls ([02](02_landfall_record.ipynb)) to **these
# coordinates**, calibrates the per-site rate, and builds the Holland field.

# %%
ranked.to_csv(OUT / "tc_m0_site_screen.csv", index=False)
sites_path = OUT / "tc_m0_sites.json"
manifest = {
    "peril": "hurricane", "sub_peril": "wind", "event_family_id": None, "layer": "M0",
    "screen": {
        "population": "EIA-860 2024 operating solar fleet (reused from flood)",
        "region": f"Gulf/SE-Atlantic ({', '.join(COAST_STATES)})",
        "metric": f"HURDAT2 hurricane-intensity (≥64 kt) landfalls within {RADIUS_KM:.0f} km (1851–2023)",
        "n_candidates": int(len(cand)), "min_mw": 20.0,
    },
    "geometry_basis": "capacity→radius circle (centroid = the degenerate field-sample point, JD-TC-2)",
    "tiv_basis": f"${TIV_PER_MW:,.0f}/MW (Hayhurst hail basis; coastal site estimated by capacity, ATC-16)",
    "sites": sites.to_dict(orient="records"),
}
sites_path.write_text(json.dumps(manifest, indent=2))
print("wrote", sites_path, "and", OUT / "tc_m0_site_screen.csv")

# %% [markdown]
# ## Takeaways → next
#
# - **Two solar sites locked** — a clean low-vs-high hurricane-wind contrast: **Hayhurst** (TX, ~0 landfalls, the
#   true-zero control) vs the **screened Gulf/SE-Atlantic coastal high site** (the proving ground, also the future
#   surge cross-link location).
# - Screen metric = **observed HURDAT2 hurricane-landfall density** (ties the site choice to real data from [02](02_landfall_record.ipynb)).
# - Geometry = capacity→radius circle + centroid (enough for solar's degenerate field-intensity, JD-TC-2); TIV = $/MW.
# - Emitted `tc_m0_sites.json` (the locked pair) + `tc_m0_site_screen.csv` (audit).
#
# **This completes M0.** **Next → M1 (catalog):** filter RAFT (01) + the landfalls (02) to these coordinates,
# **calibrate the per-site rate to the observed landfall rate** (the ATC-9 fix for the oversample), build the
# **Holland wind field**, validate vs landfall winds + the STORM RP grid, and stamp `event_family_id`.
