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
# # Hurricane · Wind-farm — M2 coupling: per-turbine 3-s gust across the lease (non-degenerate field)
#
# **Magnitude metric:** the **3-second peak gust (mph)**, sampled per turbine and at the collector substation from the
# Holland (1980) wind field along the storm track. *(Surge is flood's coastal leg, cross-linked via `event_family_id`
# and combined in flood-coastal × wind M4.)*
# **Data source:** the shared Amazon storm catalog from flood-coastal M1
# (`data/flood/amazon_wind_us_east_flood_coastal_m1_catalog.parquet` — RAFT storms reaching Amazon Wind US East with
# `storm_ID`/`event_family_id`/`category`), RAFT.NA tropical-cyclone tracks (`RAFT.NA.v20231016.nc`, vmax/rmax/track),
# and USWTDB turbine geometry (104 Gamesa G114-2.0 turbines + collector substation;
# `flood_wind_m0_geometry.parquet` / `flood_wind_m0_sites.json`).
# **What this notebook does:** turns the shared storm catalog into the per-node exposure contract M3 reads. M0/M1 are
# the shared peril catalog; this cell forks the asset at M2 ([JD-FL-19](../../../../docs/plans/flood/decisions.md)) so
# the per-storm wind loss joins the surge leg on `event_family_id`
# ([JD-FL-12](../../../../docs/plans/flood/decisions.md), [JD-FL-17](../../../../docs/plans/flood/decisions.md)). For
# every catalog storm it builds the Holland field on the RAFT track and takes each node's peak 3-s gust over the
# storm's life — the same field math (Holland B, gust factor) M1 used at the centroid, now evaluated at 105 points.
# Because a ~98 km² lease (not a sub-km solar polygon) sees a genuinely varying field, it runs the spread diagnostic
# (the inverse of the solar degeneracy check) to confirm the field is non-degenerate across the farm, so per-node
# sampling is required rather than a single centroid sample.
#
# > Shared catalog: flood-coastal M1 · turbine fragility source: [convective_wind × wind_farm
# > M3](../../../convective_wind/wind_farm/m3_damage/01_damage.ipynb). Next: [M3 damage](../m3_damage/01_damage.ipynb).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
DATA = ROOT / "data" / "hurricane"
FLOOD = ROOT / "data" / "flood"          # the shared Amazon storm catalog + geometry live here (flood-coastal M1)
DATA.mkdir(parents=True, exist_ok=True)

# same field math + levers as hurricane M1/M2 (a coupling MUST use the identical field)
HOLLAND_B = 1.3; GUST_FACTOR = 1.2; R_ANCHOR_KM = 100.0; HUR_KT = 64.0
KT_TO_MPH = 1.150779; NMI_TO_KM = 1.852
AMAZON_SLUG = "amazon_wind_us_east"
print("repo root:", ROOT)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0; p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin(np.radians(lat2-lat1)/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(np.radians(lon2-lon1)/2)**2
    return 2*R*np.arcsin(np.sqrt(a))


def holland_sustained(vmax_kt, rmw_km, r_km, B=HOLLAND_B):
    r = np.maximum(r_km, 1e-3); x = (rmw_km/r)**B
    return vmax_kt*np.sqrt(np.clip(x*np.exp(1-x), 0, None))


# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **Shared Amazon storm catalog** (`data/flood/amazon_wind_us_east_flood_coastal_m1_catalog.parquet`, flood-coastal
#   M1 / JD-FL-19) — the RAFT storms that reach Amazon, each with `storm_ID`, `event_family_id`, `category`,
#   `near_site_vmax_kt`, `min_dist_km`. **This is the join key set** the flood-coastal × wind compound combine needs.
# - **Turbine geometry** (`data/flood/amazon_wind_us_east_flood_wind_m0_geometry.parquet`) — 104 turbine lon/lat
#   (Gamesa G114-2.0, 2 MW) + the collector substation (`sub_lat`/`sub_lon` in `flood_wind_m0_sites.json`).
# - **RAFT tracks** (`data/hurricane/raw/RAFT.NA.v20231016.nc`) — vmax (kt) / rmax (nmi) / track, indexed by
#   `storm_ID`; the field source (re-read here, exactly as hurricane M1 used it).
# - **Reproducibility:** the per-node coupling contract persists to `data/hurricane/tc_windfarm_m2_coupling.parquet`.

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-12 (wind-farm form)** coupling = **field-intensity, FULL per-node** (the asset is ~10 km across → the field is
# NOT degenerate; demonstrated below) · **ATC-13 (wind)** each node is fully exposed (`value_exposed_fraction = 1.0`
# per node — a turbine is a point structure, no areal Minkowski); exposure is carried by the **per-node gust**, not a
# fraction · field math (Holland B, gust factor) **identical to M1/M2** — a coupling re-samples the same field. Full
# register: [`assumptions.md`](../../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · Load the shared Amazon storm catalog + the per-node geometry
#
# The storm catalog (the *which storms, with which identity*) is shared — built once in flood-coastal M1. We add the
# **collector substation** as a 105th node (it carries 0.09 of farm value and is wind-exposed just like the turbines).

# %%
cat = pd.read_parquet(FLOOD / f"{AMAZON_SLUG}_flood_coastal_m1_catalog.parquet")
geo = pd.read_parquet(FLOOD / f"{AMAZON_SLUG}_flood_wind_m0_geometry.parquet")
site = next(s for s in json.loads((FLOOD / "flood_wind_m0_sites.json").read_text())["sites"]
            if s["slug"] == AMAZON_SLUG)

nodes = geo[["lon", "lat"]].copy()
nodes["node_id"] = [f"T{i:03d}" for i in range(len(nodes))]
nodes["node_type"] = "turbine"
nodes = pd.concat([nodes, pd.DataFrame([{"lon": site["sub_lon"], "lat": site["sub_lat"],
                                         "node_id": "SUB", "node_type": "substation"}])], ignore_index=True)
print(f"Amazon Wind US East: TIV ${site['tiv']/1e6:.0f}M · {(nodes.node_type=='turbine').sum()} turbines + "
      f"1 substation = {len(nodes)} nodes")
print(f"shared storm catalog: {len(cat)} storms · λ (flood-coastal M1) reused at M4 · "
      f"category dist {cat['category'].value_counts().sort_index().to_dict()}")
print(f"farm extent: {haversine_km(nodes.lat.min(), nodes.lon.min(), nodes.lat.max(), nodes.lon.max()):.1f} km corner-to-corner")

# %% [markdown]
# ## 2 · Sample the Holland field at EVERY node, for every shared storm
#
# For each catalog storm we pull its RAFT track (by `storm_ID`), build the Holland (1980) field, and take each node's
# **peak 3-s gust over the storm's life** — `holland_sustained × gust_factor × kt→mph`, the identical pipeline M1 used
# at the site centroid, now evaluated at 105 points.

# %%
ds = xr.open_dataset(DATA / "raw" / "RAFT.NA.v20231016.nc", engine="h5netcdf")
lat_t, lon_t = ds["lat"].values, ds["lon"].values          # (storms, steps)
vmax_kt = ds["vmax"].values; rmw_km = ds["rmax"].values * NMI_TO_KM
storm_id = ds["storm_ID"].values
row_of = {int(sid): i for i, sid in enumerate(storm_id)}    # storm_ID → RAFT row

nlat = nodes["lat"].values[:, None]; nlon = nodes["lon"].values[:, None]   # (nodes, 1)
rows = []
for r in cat.itertuples():
    i = row_of[int(r.storm_ID)]
    d = haversine_km(nlat, nlon, lat_t[i][None, :], lon_t[i][None, :])      # (nodes, steps)
    g = holland_sustained(vmax_kt[i][None, :], rmw_km[i][None, :], d) * GUST_FACTOR * KT_TO_MPH
    g = np.where(np.isnan(g), 0.0, g)
    peak = g.max(axis=1)                                                    # (nodes,) peak 3-s gust per node
    for nid, ntype, gust in zip(nodes.node_id, nodes.node_type, peak):
        rows.append({"site": "Amazon Wind US East", "slug": AMAZON_SLUG,
                     "site_role": str(r.site_role), "storm_ID": int(r.storm_ID),
                     "event_family_id": int(r.event_family_id), "category": int(r.category),
                     "node_id": nid, "node_type": ntype,
                     "gust_3s_mph": float(gust), "value_exposed_fraction": 1.0})
m2 = pd.DataFrame(rows)
ds.close()
print(f"per-node coupling: {len(m2)} rows = {cat.shape[0]} storms × {len(nodes)} nodes")
print(m2.groupby("category")["gust_3s_mph"].agg(["count", "median", "max"]).round(1).to_string())

# %% [markdown]
# ## 3 · Earn the **non-degenerate** label — the field VARIES across the farm (inverse of the solar check)
#
# Hurricane × solar *demonstrated* the field was uniform across a sub-km polygon (median spread <1%, p95 <2%) → one
# centroid sample sufficed. Here the asset is **~10 km across**, so we run the **same diagnostic** and expect the
# opposite: a per-storm gust spread (max−min)/mean across the 104 turbines that is **materially non-zero** — which is
# exactly why we sample per turbine, not once. (The closest passages, near-eye, spread the most.)

# %%
turb = m2[m2.node_type == "turbine"]
spread = turb.groupby("storm_ID")["gust_3s_mph"].agg(lambda s: 100 * (s.max() - s.min()) / max(s.mean(), 1e-9))
worst = spread.idxmax(); wcat = int(cat.set_index("storm_ID").loc[worst, "category"])
wdist = float(cat.set_index("storm_ID").loc[worst, "min_dist_km"])
print("per-storm 3-s gust spread across the 104 turbines (max−min)/mean:")
print(f"  median {spread.median():.2f}%   p95 {spread.quantile(.95):.2f}%   max {spread.max():.2f}%")
print(f"  → NOT degenerate (solar was median <1%, p95 <2%). The widest-spread storm (#{int(worst)}, "
      f"min_dist {wdist:.1f} km, Cat{wcat}) varies {spread.max():.1f}% across the ~18 km lease — a steep gradient one")
print("  centroid sample would erase → per-node sampling is required, not a convenience (the V2 payoff).")

# %% [markdown]
# ## 4 · Known-answer checks (basics-spot-on)

# %%
checks = {
    "every shared storm × node represented once (no drop/dup)": len(m2) == len(cat) * len(nodes),
    "all 24 join keys (event_family_id) preserved from the shared catalog":
        set(m2.event_family_id.unique()) == set(cat.event_family_id.astype(int)),
    "value_exposed_fraction == 1.0 at every node (point structures)": bool((m2.value_exposed_fraction == 1.0).all()),
    "gusts non-negative & finite": bool(np.isfinite(m2.gust_3s_mph).all() and (m2.gust_3s_mph >= 0).all()),
    "field is NON-degenerate across the farm (median spread > 2% — unlike solar)": spread.median() > 2.0,
    "median gust rises with category (sanity: stronger storms → stronger gusts)":
        m2.groupby("category")["gust_3s_mph"].median().is_monotonic_increasing,
    "gusts in a sane hurricane range (max ≤ 250 mph; finite)": float(m2.gust_3s_mph.max()) <= 250.0,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "an M2 check failed"
print("\nall M2/01 known-answer checks pass ✅")

# %% [markdown]
# ## 5 · Emit — the per-node coupling contract M3 reads

# %%
out = DATA / "tc_windfarm_m2_coupling.parquet"
m2.to_parquet(out, index=False)
manifest = {
    "notebook": "hurricane/wind_farm/m2_coupling/01_coupling",
    "site": "Amazon Wind US East (NC)", "slug": AMAZON_SLUG, "asset": "wind_farm",
    "coupling_type": "field-intensity (3rd bucket) — FULL per-node (NON-degenerate; the wind-farm V2 the solar cell foreshadowed)",
    "shared_catalog": "data/flood/amazon_wind_us_east_flood_coastal_m1_catalog.parquet (flood-coastal M1, JD-FL-19) — M0/M1 shared, asset forked at M2",
    "field_levers": {"holland_B": HOLLAND_B, "gust_factor_1min_to_3s": GUST_FACTOR},  # identical to hurricane M1/M2
    "n_nodes": int(len(nodes)), "n_turbines": int((nodes.node_type == "turbine").sum()), "n_storms": int(len(cat)),
    "fraction_rule": "value_exposed_fraction = 1.0 PER NODE (turbines/substation are point structures); exposure carried by per-node gust",
    "field_variation_across_farm_pct": {"median": round(float(spread.median()), 2),
                                        "p95": round(float(spread.quantile(.95)), 2), "max": round(float(spread.max()), 2)},
    "contract_fields": ["site", "slug", "storm_ID", "event_family_id", "category", "node_id", "node_type",
                        "gust_3s_mph", "value_exposed_fraction"],
    "n_rows": int(len(m2)),
    "outputs": {"coupling_parquet": str(out.relative_to(ROOT))},
}
(DATA / "tc_windfarm_m2_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote", out, "and", DATA / "tc_windfarm_m2_manifest.json")

# %% [markdown]
# ## Takeaways → next
#
# - **Field-intensity coupling, in its full per-node form** — the wind-farm V2 the solar cell promised. We sampled the
#   Holland 3-s gust at **all 105 nodes** (104 turbines + collector) for the **shared** Amazon storm catalog, and
#   **demonstrated the field is genuinely non-degenerate** across the ~10 km lease (the inverse of the solar check) →
#   per-node sampling is *required*, not a convenience.
# - **M0/M1 shared, asset forked at M2** — we reused the flood-coastal storm catalog (with `event_family_id`), not a
#   rebuilt one, so the per-storm wind loss will **join the surge leg on the same key** (JD-FL-12).
# - **Contract emitted** — per-(storm, node) `gust_3s_mph × value_exposed_fraction` for M3.
#
# **Next → M3 (damage):** map each node's 3-s gust through the **turbine wind-damage curve** (reused from convective
# wind — hurricane wind on a turbine ≈ straight-line wind on a turbine) → **per-storm, per-subsystem** damage ratio,
# stamped `event_family_id` (the exact shape flood-coastal × wind M4 joins to the surge leg).
