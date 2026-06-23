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
# # Hurricane — M0 input data: the RAFT synthetic tropical-cyclone catalog (storm-resolved build source)
#
# **Peril:** Tropical cyclone / hurricane (WIND) · **Layer:** M0 (raw evidence) · method-neutral
#
# **Magnitude metric:** the hurricane wind peril's damage observable is the **3-second peak gust (mph)** at the site,
# synthesized in M1 from the Holland (1980) wind field on storm tracks. RAFT carries **max *sustained* wind (knots)**;
# the gust conversion is applied in M1. *(Storm surge and TC rainfall are hurricane's secondary perils — sourced as
# flood's coastal `[C]` / pluvial `[F]` and cross-linked via `event_family_id`, not modeled in this hurricane cell.)*
#
# **Data source:** **RAFT** — a North-Atlantic **synthetic tropical-cyclone catalog** (Zenodo, CC-BY-4.0): 40,000
# storms over 40 environmental years, each a storm object with identity (`storm_ID`), track, and intensity.
#
# **What this notebook does:** loads and characterizes the RAFT catalog — the **storm-resolved build source** for the
# whole pipeline ([JD-TC-3](../../../docs/plans/hurricane/decisions.md)). It fetches and caches the tracks file, reads
# the field dictionary (flagging that `vmax` is in **knots**, not m/s — the unit trap), measures the catalog's
# intensity distribution and spatial coverage, and documents that RAFT's raw genesis rate is a **~71× oversample** —
# so the physical per-site rate is calibrated to observed landfalls in M1, not taken from the raw catalog. It emits a
# per-storm summary (`tc_m0_raft_summary.parquet`) plus manifest. RAFT is the V1 catalog spine because it is
# storm-resolved (every event has identity), which a pre-integrated wind-RP grid is not — and only storm objects can
# found coastal flood via `event_family_id`. **No fields built, no losses** — that is M1+.
#
# > **Storm-resolved, not a rate-fit and not a surface.** RAFT is a synthetic catalog spanning many years, so the
# > **catalog itself carries the frequency** — but (see §3) its raw genesis rate is an oversample, and the physical
# > per-site rate is calibrated to observed landfalls in M1.
# >
# > Plan: [`m0_input_data.md`](../../../docs/plans/hurricane/m0_input_data.md) · layer-0:
# > [`00_hazard_definition.md`](../../../docs/plans/hurricane/00_hazard_definition.md) · Decisions:
# > [`decisions.md`](../../../docs/plans/hurricane/decisions.md) (JD-TC-3/4/7).

# %% [markdown]
# ## Source & provenance (pin it, cache it)
#
# The hurricane peril's **primary** sub-peril is **wind** — magnitude = the **3-s peak gust** — built from one
# storm-resolved source, named here up-front with access + caching:
#
# - **RAFT** — a North-Atlantic **synthetic tropical-cyclone catalog**. **Role:** the storm-resolved build source —
#   every event is an object with identity (`storm_ID` → the (now-active) `event_family_id`), carrying the track +
#   intensity M1's Holland wind field needs. **Access:** Zenodo (`zenodo.org/records/10392723`, concept DOI
#   `10.5281/zenodo.10392723`), **CC-BY-4.0**; downloaded once and **cached** at
#   `data/hurricane/raw/RAFT.NA.v20231016.nc` (≈154 MB) → re-runs are offline + idempotent. **Magnitude basis:**
#   `vmax` is in **knots (1-min sustained)** → M1 converts to the **3-s gust in mph** (× gust factor × 1.150779 —
#   the ATC-8 unit trap).
#
# ⚠️ **Caveats (carried):** RAFT's raw genesis rate is a **~71× oversample** — the *physical* per-site rate is
# calibrated to observed HURDAT2 landfalls in M1 (JD-TC-8), **not** taken from the raw catalog (§3); single basin
# (North Atlantic). **Reproducibility:** the per-storm summary is persisted to
# `data/hurricane/tc_m0_raft_summary.parquet` (+ `tc_m0_raft_manifest.json`).
#
# > **Secondary perils, cross-linked (not built here).** A hurricane also drives **storm surge** and **TC rainfall**;
# > by the reference these are the *same physics as flood* and are not re-catalogued — surge = flood's **coastal [C]**
# > (**NOAA SLOSH** MOMs / P-Surge → surge depth, ft), TC rainfall = flood's **pluvial [F]** (**NOAA Atlas 14** →
# > ponding depth). They attach to the hurricane wind event via the active `event_family_id` (one storm, counted
# > once — JD-TC-4/5) — flood coastal is built, so the cross-link is now active.

# %%
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import xarray as xr

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
RAW = ROOT / "data" / "hurricane" / "raw"
OUT = ROOT / "data" / "hurricane"
RAW.mkdir(parents=True, exist_ok=True)

# Unit conversions (RAFT is knots / nautical miles — see the field dictionary, §2)
KT_TO_MPH = 1.150779      # knots → mph   (the damage-curve unit)
KT_TO_MS = 0.514444       # knots → m/s
NMI_TO_KM = 1.852         # nautical mile → km
print("repo root:", ROOT)

# %% [markdown]
# ## Assumptions (this layer)
#
# **ATC-5** catalog = storm-resolved **RAFT** tracks (N. Atlantic; CC-BY-4.0) · **ATC-8** wind-unit guard — RAFT
# `vmax` is **knots → mph ×1.150779** (the live unit trap) · **ATC-9** RAFT's raw rate is a **~71× genesis
# oversample** → the per-site rate is calibrated to observed landfalls in M1 (not used raw here) · **ATC-17** input
# is self-serve public data. Full register:
# [`assumptions.md`](../../../docs/plans/hurricane/assumptions.md).

# %% [markdown]
# ## 1 · Fetch RAFT — North Atlantic tracks + intensity (Zenodo, CC-BY-4.0)
#
# Source: **RAFT** (Risk Analysis Framework for TCs), Zenodo concept DOI `10.5281/zenodo.10392723`. We pull the
# **tracks + intensity** file `RAFT.NA.v20231016.nc` (**~147 MB**) — the V1 wind spine. The **TC rainfall** lives
# in separate `RAFT_accum_rainfall_*.tar.gz` files (~16 GB total) and is the **deferred pluvial-TC slice**
# ([JD-TC-6](../../../docs/plans/hurricane/decisions.md)) — V1 wind never touches it.
#
# > **DOI-resolution gotcha (recorded for reproducibility):** the concept-record file-content URL 404s; the file is
# > served from the *versioned* record. We resolve the download URL from the Zenodo **API record listing** rather
# > than hardcoding a version (the "re-confirm the DOI at use-time" caveat, Hazard-Data-Ref §8).

# %%
RAFT_NC = RAW / "RAFT.NA.v20231016.nc"
RAFT_FNAME = "RAFT.NA.v20231016.nc"
RECORD_API = "https://zenodo.org/api/records/10392723"

if not RAFT_NC.exists():
    print("resolving RAFT download URL from Zenodo API …")
    rec = requests.get(RECORD_API, timeout=60).json()
    url = next(f["links"]["self"].replace("/content", "") for f in rec["files"] if f["key"] == RAFT_FNAME)
    # the versioned ?download=1 URL is the one that streams reliably
    rec_id = rec["id"]
    dl = f"https://zenodo.org/records/{rec_id}/files/{RAFT_FNAME}?download=1"
    print("downloading", dl)
    r = requests.get(dl, timeout=900); r.raise_for_status()
    RAFT_NC.write_bytes(r.content)
print("RAFT tracks file:", RAFT_NC, f"({RAFT_NC.stat().st_size/1e6:.1f} MB)")
assert RAFT_NC.read_bytes()[:4] == b"\x89HDF", "not a valid HDF5/NetCDF-4 file"

ds = xr.open_dataset(RAFT_NC, engine="h5netcdf")
print("\nDIMS:", dict(ds.sizes))
print("VARS:", list(ds.variables))

# %% [markdown]
# ## 2 · Field dictionary — every variable, with its base (the discipline)
#
# *Interpret every variable; the interpretation is the deliverable.* The structure is **2-D**: `(storms=40000,
# timesteps=120)` — a storm is a row, each timestep a **6-hourly** position (so 120 steps = up to 30 days; tracks
# are NaN-padded after they end).
#
# | Variable | Dims | Meaning | Units / base | ⚠ what it's NOT |
# |---|---|---|---|---|
# | `lat`, `lon` | (storm, step) | TC center, 6-hourly | degrees | — |
# | `vmax` | (storm, step) | **maximum sustained wind** | **knots** (1-min sustained) | **NOT m/s; NOT a 3-s gust** — gust factor + unit conv in M1 |
# | `mslp` | (storm, step) | minimum central pressure | hPa | lower = stronger |
# | `rmax` | (storm, step) | radius of maximum wind | **nautical miles** | a Holland input (→ km) |
# | `shear_x/y` | (storm, step) | 200–850 hPa wind shear | m/s | intensity-model driver, not a damage input |
# | `year` | (storm,) | **env-conditions year** (1979–2018) used to generate the storm | — | **NOT a calendar of when it "happened"** |
# | `basin_ID` | (storm,) | 1 = North Atlantic | — | single basin here |
# | `storm_ID` | (storm,) | TC id (from 0) | — | → the `event_family_id` (now active) |
#
# > **🔴 The live unit trap.** The Hazard-Data-Reference's generic note says "STORM wind is m/s (×2.237)". **RAFT is
# > different — `vmax` is in *knots*.** So the conversion to the damage-curve mph is **×1.150779**, and to m/s is
# > **×0.514444**. A silent "m/s" assumption here would understate gusts ~2×. (Recorded against
# > [ATC-8](../../../docs/plans/hurricane/assumptions.md).)

# %%
for v in ds.variables:
    da = ds[v]
    desc = da.attrs.get("description", da.attrs.get("long_name", ""))
    print(f"  {v:10s} {str(tuple(da.dims)):22s} {str(da.dtype):8s} units={da.attrs.get('units','—'):14s} {desc[:60]}")

# pull arrays once
lat, lon = ds["lat"].values, ds["lon"].values
vmax_kt, mslp, rmax_nmi = ds["vmax"].values, ds["mslp"].values, ds["rmax"].values
year, storm_id = ds["year"].values, ds["storm_ID"].values
n_storms = ds.sizes["storms"]
valid = ~np.isnan(lat)                                  # a real 6-hr position
steps_per_storm = valid.sum(axis=1)
print(f"\n{n_storms:,} storms · {ds.sizes['timesteps']} max timesteps · "
      f"median track length {np.median(steps_per_storm):.0f} steps (~{np.median(steps_per_storm)*6/24:.1f} days)")

# %% [markdown]
# ## 3 · 🔴 Frequency basis — the raw catalog rate is an OVERSAMPLE (the key M0 finding for M1)
#
# RAFT spans **40 environmental years (1979–2018)** with **~1000 storms per env-year** → 40,000 storms. But the
# **real** North Atlantic averages **~14 named storms/year** — so RAFT's ~1000/yr is a deliberate **genesis
# oversample** (it seeds many weak disturbances for tail resolution; the median peak below confirms most are weak).
#
# **Consequence for M1 (do not skip):** the *physical annual rate at a site* is **NOT** "1000/yr × p_hit". The rate
# must be obtained by **spatial + intensity filtering** of the catalog and then **calibrated against the observed
# landfall rate** near the site (IBTrACS/HURDAT2, notebook 02) — the catalog supplies the **conditional
# severity/geometry**, the observed record anchors the **rate**. This is the hurricane analogue of wind's SPC
# bias-correction discipline. (→ [ATC-9](../../../docs/plans/hurricane/assumptions.md), resolved in M1.)

# %%
u_year, c_year = np.unique(year, return_counts=True)
print(f"env-years: {u_year.min()}–{u_year.max()}  ({len(u_year)} years)")
print(f"storms per env-year: mean {c_year.mean():.0f}  (min {c_year.min()}, max {c_year.max()})")
print(f"  → vs real NA ~14 named storms/yr  ⇒  ~{c_year.mean()/14:.0f}× genesis oversample (weak seeds included)")
print(f"  ⇒ M1 must calibrate the per-site rate to observed landfalls, NOT use the raw catalog rate")

# %% [markdown]
# ## 4 · Intensity distribution — mostly weak, a resolved violent tail
#
# Per-storm **peak** sustained wind (the lifetime max of `vmax`). Saffir-Simpson is a **1-min sustained, knots**
# scale: TS 34–63 · Cat1 64–82 · Cat2 83–95 · Cat3 96–112 · Cat4 113–136 · Cat5 ≥137 kt. (These are *sustained*
# thresholds — the damage curve will use the **3-s gust**, higher, via the M1 gust factor.)

# %%
peak_kt = np.nanmax(np.where(valid, vmax_kt, np.nan), axis=1)
def cat(kt):
    bins = [34, 64, 83, 96, 113, 137]
    labels = ["TD(<34)", "TS", "Cat1", "Cat2", "Cat3", "Cat4", "Cat5"]
    return labels[np.searchsorted(bins, kt, side="right")]
cats = pd.Series([cat(k) for k in peak_kt]).value_counts()
order = ["TD(<34)", "TS", "Cat1", "Cat2", "Cat3", "Cat4", "Cat5"]
print("per-storm peak intensity (Saffir-Simpson, sustained kt):")
for c in order:
    n = int(cats.get(c, 0)); print(f"  {c:9s} {n:6,d}  ({100*n/n_storms:4.1f}%)  {'█'*int(60*n/n_storms)}")
print(f"\npeak vmax: median {np.nanmedian(peak_kt):.0f} kt ({np.nanmedian(peak_kt)*KT_TO_MPH:.0f} mph) · "
      f"p99 {np.nanpercentile(peak_kt,99):.0f} kt · max {np.nanmax(peak_kt):.0f} kt "
      f"({np.nanmax(peak_kt)*KT_TO_MPH:.0f} mph, {np.nanmax(peak_kt)*KT_TO_MS:.0f} m/s)")
n_major = int((peak_kt >= 96).sum())
print(f"major hurricanes (≥Cat3): {n_major:,} ({100*n_major/n_storms:.1f}%) — the tail that drives loss")

# %% [markdown]
# ## 5 · Spatial coverage + US-coast landfall illustration
#
# RAFT is the **North Atlantic** basin — confirm all four sites' region is covered, and illustrate the
# **landfall-relevant filtering** M1 will do per-site: how many storms reach **hurricane intensity (≥64 kt)** while
# inside a US Gulf/Atlantic-coast box (`lon −98…−65, lat 24…45`). This is *illustrative* (a coarse box, not a
# coastline); the **precise per-site collection radius** is applied in M1 once 03 locks the sites.

# %%
print(f"basin extent: lat {np.nanmin(lat):.1f}…{np.nanmax(lat):.1f}  lon {np.nanmin(lon):.1f}…{np.nanmax(lon):.1f}")
in_box = (lon >= -98) & (lon <= -65) & (lat >= 24) & (lat <= 45) & valid
hur = vmax_kt >= 64
storms_uscoast = ((in_box & hur).any(axis=1)).sum()
print(f"storms reaching ≥64 kt within the US-coast box: {storms_uscoast:,} "
      f"({100*storms_uscoast/n_storms:.1f}% of catalog)")
print(f"  → over 40 env-years that is ~{storms_uscoast/40:.0f}/yr of US-coast hurricanes in the oversampled catalog")
print("  (the per-site physical rate is set in M1 by radius-filtering + observed-landfall calibration)")

# %% [markdown]
# ## 6 · Known-answer checks (basics-spot-on)

# %%
checks = {
    "40,000 storms": n_storms == 40000,
    "single basin = North Atlantic (basin_ID all 1)": bool((ds["basin_ID"].values == 1).all()),
    "env-years span 1979–2018 (40)": (u_year.min() == 1979 and u_year.max() == 2018 and len(u_year) == 40),
    "vmax is knots (peak max ~173 kt, ~Cat5)": 150 <= np.nanmax(peak_kt) <= 200,
    "knots→mph gives plausible Cat5 gust basis (>190 mph at peak)": np.nanmax(peak_kt) * KT_TO_MPH > 190,
    "every storm has ≥1 valid track point": bool((steps_per_storm >= 1).all()),
    "stronger storms have lower mslp (vmax↔mslp anti-correlated)":
        np.corrcoef(peak_kt, np.nanmin(np.where(valid, mslp, np.nan), axis=1))[0, 1] < -0.7,
    "no rainfall variable in tracks file (it's the deferred 16 GB slice)": "rainfall" not in " ".join(ds.variables),
}
for k, v in checks.items():
    print(f"  {'✅' if v else '❌'}  {k}")
assert all(checks.values()), "a known-answer check failed"
print("\nall M0/01 known-answer checks pass ✅")

# %% [markdown]
# ## 7 · Emit — the per-storm catalog summary (the M1 build source)
#
# One row per storm: identity, env-year, genesis, lifetime peak intensity (kt + mph + m/s), min pressure, peak-time
# RMW, track length, and the US-coast-hurricane flag. This is the **asset-independent** summary M1 reads to build
# Holland fields and (after radius-filtering + calibration) the per-site rate. The raw `.nc` stays cached for the
# field build. **Wind in mph carried alongside knots so the unit base is never lost.**

# %%
# peak-time index per storm (argmax of vmax over valid steps)
vmax_valid = np.where(valid, vmax_kt, -1.0)
pk_idx = vmax_valid.argmax(axis=1)
rows = np.arange(n_storms)
genesis_step = np.argmax(valid, axis=1)                 # first valid step

summary = pd.DataFrame({
    "storm_ID": storm_id,
    "event_family_id": storm_id.astype("int64"),        # active cross-link key (JD-TC-4); = storm here
    "env_year": year,
    "genesis_lat": lat[rows, genesis_step],
    "genesis_lon": lon[rows, genesis_step],
    "n_steps": steps_per_storm,
    "lifetime_days": steps_per_storm * 6 / 24,
    "peak_vmax_kt": peak_kt,
    "peak_vmax_mph": peak_kt * KT_TO_MPH,
    "peak_vmax_ms": peak_kt * KT_TO_MS,
    "min_mslp_hpa": np.nanmin(np.where(valid, mslp, np.nan), axis=1),
    "rmax_at_peak_km": rmax_nmi[rows, pk_idx] * NMI_TO_KM,
    "peak_lat": lat[rows, pk_idx],
    "peak_lon": lon[rows, pk_idx],
    "uscoast_hurricane": (in_box & hur).any(axis=1),
})
out_path = OUT / "tc_m0_raft_summary.parquet"
summary.to_parquet(out_path, index=False)
print(f"wrote {out_path}  ({len(summary):,} storms × {summary.shape[1]} cols)")

manifest = {
    "notebook": "hurricane/m0_input_data/01_raft_catalog",
    "source": "RAFT North Atlantic synthetic TC catalog",
    "zenodo_concept_doi": "10.5281/zenodo.10392723",
    "file": RAFT_FNAME,
    "license": "CC-BY-4.0",
    "n_storms": int(n_storms),
    "env_years": [int(u_year.min()), int(u_year.max())],
    "n_env_years": int(len(u_year)),
    "raw_genesis_rate_per_year": float(c_year.mean()),
    "units": {"vmax": "knots (1-min sustained)", "rmax": "nautical_miles", "mslp": "hPa"},
    "unit_conversions": {"kt_to_mph": KT_TO_MPH, "kt_to_ms": KT_TO_MS, "nmi_to_km": NMI_TO_KM},
    "rainfall_in_this_file": False,
    "rainfall_note": "TC rainfall is in separate RAFT_accum_rainfall_*.tar.gz (~16 GB) — deferred pluvial-TC slice (JD-TC-6)",
    "key_findings": [
        "vmax is KNOTS not m/s (×1.150779 → mph) — live unit trap, ATC-8",
        "raw ~1000 storms/env-year is a genesis oversample vs real ~14/yr — M1 must calibrate per-site rate to observed landfalls (ATC-9)",
        f"{n_major} major (≥Cat3) storms ({100*n_major/n_storms:.1f}%)",
    ],
    "outputs": {"summary_parquet": str(out_path.relative_to(ROOT))},
}
man_path = OUT / "tc_m0_raft_manifest.json"
man_path.write_text(json.dumps(manifest, indent=2))
print("wrote", man_path)
ds.close()

# %% [markdown]
# ## Takeaways → next
#
# - **RAFT is reachable and storm-resolved** (40,000 N. Atlantic storms, 1979–2018 env-years) — the V1 catalog spine.
# - **`vmax` is in knots** (×1.150779 → the damage-curve mph) — the live unit trap, handled here.
# - **The raw catalog rate is an oversample** (~1000 vs ~14/yr) → M1 calibrates the per-site rate to **observed
#   landfalls** (02); the catalog supplies conditional severity/geometry.
# - **No rainfall here** — confirms the wind/rain scope split (the rain is the deferred 16 GB pluvial-TC slice).
# - Emitted `tc_m0_raft_summary.parquet` (per-storm) + manifest.
#
# **Next → [02_landfall_record](02_landfall_record.py):** bracket RAFT with
# **IBTrACS/HURDAT2** observed landfalls (the rate anchor + Holland validation targets) and the **STORM RP grid**
# cross-check.
