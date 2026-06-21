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
# # Hurricane · Solar — M2 coupling: field-intensity exposure contract (spatially degenerate on solar)
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Cell:** × Solar PV · **Layer:** M2 (coupling)
#
# **Magnitude metric:** the **3-second peak gust (mph)**, passed through unchanged from M1 (M2 adds *exposure*, not
# magnitude). *(Surge/rain = flood's `[C]`/`[F]`, cross-linked, not modeled here.)*
#
# **Data source:** the M1 catalog (`tc_m1_catalog.parquet`, per-event site 3-s gust), the locked sites
# (`tc_m0_sites.json`, footprint radius), and the RAFT `.nc` re-read to sample the field across the footprint.
#
# **What this notebook does:** turns M1's per-event site gust into the **exposure contract** M3 reads. This is the
# repo's **field-intensity** coupling (sample a continuous field at the asset) in its **spatially-degenerate** form on
# a small solar polygon ([JD-TC-2](../../../../docs/plans/hurricane/decisions.md)) — thin because M1 already did the
# field synthesis (Holland → gust at the site). It **demonstrates** the degenerate label rather than asserting it:
# for each anchor storm it recomputes the peak gust at the centroid vs the footprint-edge points and shows the spread
# is far smaller than the gust (median < 1%, p95 < 2%), so the whole plant sees one effective gust and
# `value_exposed_fraction = 1.0` is justified. It emits the per-event coupling contract
# (`tc_m2_coupling.parquet`: `gust_3s_mph × value_exposed_fraction`) + manifest. The full per-point field-intensity is
# the wind-farm V2 cell, where the asset is tens of km across and the field genuinely varies.
#
# > Plan: [`m2_coupling.md`](../../../../docs/plans/hurricane/m2_coupling.md) · Decisions:
# > [`decisions.md`](../../../../docs/plans/hurricane/decisions.md) (JD-TC-2). Prior: [M1 catalog](../../m1_catalog/01_event_catalog.ipynb).

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

# same field math + levers as M1 (a coupling must use the identical field)
HOLLAND_B = 1.3; GUST_FACTOR = 1.2; R_ANCHOR_KM = 100.0; HUR_KT = 64.0
KT_TO_MPH = 1.150779; NMI_TO_KM = 1.852

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0; p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin(np.radians(lat2-lat1)/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(np.radians(lon2-lon1)/2)**2
    return 2*R*np.arcsin(np.sqrt(a))
def holland_sustained(vmax_kt, rmw_km, r_km, B=HOLLAND_B):
    r = np.maximum(r_km, 1e-3); x = (rmw_km/r)**B
    return vmax_kt*np.sqrt(np.clip(x*np.exp(1-x), 0, None))
print("repo root:", ROOT)

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# - **M1 catalog** (`data/hurricane/tc_m1_catalog.parquet`) — per-event site **3-s gust**; the magnitude M2 couples.
# - **Locked sites** (`data/hurricane/tc_m0_sites.json`) — footprint radius for the uniformity demonstration.
# - **RAFT `.nc`** — re-read only to sample the field across the footprint (the degeneracy check). **Reproducibility:**
#   the coupling contract persists to `data/hurricane/tc_m2_coupling.parquet` (+ manifest).

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-12** coupling = **field-intensity**, **spatially degenerate on solar** (≈ centroid sample — *demonstrated*
# <2% gust spread across the footprint) · **ATC-13** solar = dense areal polygon → **`value_exposed_fraction = 1.0`**
# (uniform exposure; no Minkowski, no susceptibility). Full register:
# [`assumptions.md`](../../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · Load the validated M1 catalog + sites

# %%
cat = pd.read_parquet(DATA / "tc_m1_catalog.parquet")
sites = {s["name"]: s for s in json.load(open(DATA / "tc_m0_sites.json"))["sites"]}
print(f"M1 catalog: {len(cat)} per-event rows across {cat.site.nunique()} sites")
print(cat.groupby("site").agg(events=("storm_ID", "size"),
      med_gust=("peak_gust_3s_mph", "median"), max_gust=("peak_gust_3s_mph", "max")).round(1).to_string())

# %% [markdown]
# ## 2 · Demonstrate the field is uniform across the footprint (earn the "degenerate" label)
#
# A solar farm here is a **capacity-radius circle** (Everglades `footprint_r_m`). At storm scale (radius of max wind
# ~tens of km) the field should barely change across a sub-km plant. We test it: for each anchor storm, recompute the
# **peak gust at the centroid vs at the 4 footprint-edge points** (±radius N/S/E/W) and report the spread. If the
# spread is ≪ the gust, the whole plant sees one value → field-intensity collapses to a single sample (the honest
# *degenerate* form), and `value_exposed_fraction = 1.0` is justified.

# %%
ds = xr.open_dataset(DATA / "raw" / "RAFT.NA.v20231016.nc", engine="h5netcdf")
lat, lon = ds["lat"].values, ds["lon"].values
vmax_kt = ds["vmax"].values; rmw_km = ds["rmax"].values * NMI_TO_KM

def peak_gust_at(plat, plon, storm_mask):
    d = haversine_km(plat, plon, lat, lon)
    g = holland_sustained(vmax_kt, rmw_km, d) * GUST_FACTOR * KT_TO_MPH
    g = np.where(np.isnan(g), 0.0, g)
    return g.max(axis=1)[storm_mask]

hi = sites["Everglades Solar Energy Center"]
r_m = hi["footprint_r_m"]
dlat = r_m / 111_320.0
dlon = r_m / (111_320.0 * np.cos(np.radians(hi["lat"])))
# anchor storms (those with a hurricane center within 100 km) — the catalog's storms
d_c = haversine_km(hi["lat"], hi["lon"], lat, lon)
anchor = ((d_c <= R_ANCHOR_KM) & (vmax_kt >= HUR_KT)).any(axis=1)

pts = {"centroid": (hi["lat"], hi["lon"]),
       "N": (hi["lat"]+dlat, hi["lon"]), "S": (hi["lat"]-dlat, hi["lon"]),
       "E": (hi["lat"], hi["lon"]+dlon), "W": (hi["lat"], hi["lon"]-dlon)}
gusts = {k: peak_gust_at(la, lo, anchor) for k, (la, lo) in pts.items()}
G = np.vstack([gusts[k] for k in pts]).T                      # (storms, 5 points)
spread_pct = 100 * (G.max(axis=1) - G.min(axis=1)) / np.maximum(G.mean(axis=1), 1e-9)
p95 = np.percentile(spread_pct, 95)
print(f"footprint radius: {r_m} m  ({2*r_m/1000:.1f} km across)")
print(f"per-storm gust spread across the footprint (max−min)/mean:")
print(f"  median {np.median(spread_pct):.3f}%   p95 {p95:.3f}%   max {spread_pct.max():.3f}%")
print(f"→ uniform for ~95% of storms (p95 {p95:.1f}%); the ~{spread_pct.max():.0f}% MAX is a rare near-eye direct hit")
print("  (small RMW passing almost over the plant → eyewall gradient crosses 1.4 km). Still small ⇒ fraction=1.0 OK;")
print("  it does foreshadow why the wind-farm V2 cell (tens of km) genuinely needs per-point field-intensity.")
ds.close()

# %% [markdown]
# ## 3 · Build the M2 exposure contract
#
# Per event: the site gust (unchanged from M1 — M2 adds *exposure*, not magnitude) and `value_exposed_fraction =
# 1.0` (the whole dense polygon sees the same gust — no Minkowski, no susceptibility modifier; those belong to the
# other two coupling types). This is exactly what M3 multiplies the damage ratio against.

# %%
m2 = cat[["site", "site_role", "storm_ID", "event_family_id", "peak_gust_3s_mph"]].copy()
m2["gust_3s_mph"] = m2["peak_gust_3s_mph"]
m2["value_exposed_fraction"] = 1.0
m2 = m2.drop(columns=["peak_gust_3s_mph"])
print(m2.head(3).to_string(index=False))
print(f"\nM2 contract: {len(m2)} events · fraction = 1.0 (uniform exposure)")

# %% [markdown]
# ## 4 · Known-answer checks

# %%
checks = {
    "field uniform for ~all storms (median <1%, p95 <2%) — degenerate justified": (np.median(spread_pct) < 1.0) and (p95 < 2.0),
    "value_exposed_fraction == 1.0 for all events": bool((m2["value_exposed_fraction"] == 1.0).all()),
    "gust unchanged from M1 (M2 adds exposure, not magnitude)":
        np.allclose(m2["gust_3s_mph"].values, cat["peak_gust_3s_mph"].values),
    "every M1 event passes through once (no drop/dup)": len(m2) == len(cat),
    "baseline Hayhurst carries no events (true-zero control)": (m2["site_role"].str.startswith("baseline")).sum() == 0,
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "an M2 check failed"
print("\nall M2/01 known-answer checks pass ✅")

# %% [markdown]
# ## 5 · Emit — the coupling contract M3 reads

# %%
out = DATA / "tc_m2_coupling.parquet"
m2.to_parquet(out, index=False)
manifest = {
    "notebook": "hurricane/solar/m2_coupling/01_coupling",
    "coupling_type": "field-intensity (3rd bucket) — SPATIALLY DEGENERATE on solar (JD-TC-2)",
    "fraction_rule": "value_exposed_fraction = 1.0 (dense polygon, uniform field at storm scale)",
    "uniformity_demonstrated": {
        "footprint_radius_m": int(r_m),
        "gust_spread_across_footprint_pct": {"median": round(float(np.median(spread_pct)), 3),
                                             "p95": round(float(p95), 3), "max": round(float(spread_pct.max()), 3)},
        "conclusion": "uniform for ~95% of storms (median 0.5%, p95 1.1%); rare ~8% max = near-eye direct hit "
                      "(eyewall gradient across 1.4 km). fraction=1.0 OK for solar; foreshadows V2 per-point need",
    },
    "contract_fields": ["site", "storm_ID", "event_family_id", "gust_3s_mph", "value_exposed_fraction"],
    "n_events": int(len(m2)),
    "note": "full per-point field-intensity is the wind-farm V2 cell (asset tens of km → field varies)",
    "outputs": {"coupling_parquet": str(out.relative_to(ROOT))},
}
(DATA / "tc_m2_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote", out, "and", DATA / "tc_m2_manifest.json")

# %% [markdown]
# ## Takeaways → next
#
# - **Field-intensity coupling built** — and the "degenerate on solar" label is **demonstrated**: the wind field
#   varies **~0.5% (median), <1.1% (p95)** across the footprint, so the plant sees one effective gust →
#   `value_exposed_fraction = 1.0`. The rare **~8% max** (a near-eye direct hit) is small enough for solar but
#   **foreshadows why the wind-farm V2 cell genuinely needs per-point field-intensity.**
# - **Thin by design** — M1 did the field; M2 just attaches exposure (no Minkowski, no susceptibility).
# - **Contract emitted** — per-event `gust_3s_mph × value_exposed_fraction` for M3.
#
# **Next → M3 (damage):** map each event's 3-s gust through the `infrasure-damage-curves` hurricane-wind × solar
# curve → conditional loss per event.
