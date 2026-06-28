# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Hazard (.venv 3.12)
#     language: python
#     name: hazard_modeling
# ---

# %% [markdown]
# # Hazard CONUS Grid — Hail × Solar — Risk Maps
#
# **Peril:** hail · **Asset:** canonical 100 MW solar · **Layer:** M2–M4 full-CONUS risk layer (view)
#
# A *viewing* notebook — it renders the full-CONUS gridded risk layer produced by the `conus_grid` driver
# (`drivers/conus_grid`) so we can see the geography and sanity-check the product. It reads the persisted
# risk layer and draws maps; it computes nothing new.
#
# ```
#   QC'd M1  ─► driver (M2 couple ─► M3 damage ─► M4 engine) ─► per-cell risk layer  ─► THESE MAPS
# ```
#
# **What to look for:** does the EAL/PML geography track the hail corridor (Plains/Upper-Midwest)? Do the
# frequency-spike cells (held out of reportable loss) cluster sensibly? Are raw-MESH and 100 mm-capped
# severity policies visually identical for solar (they should be — the damage curve saturates by ~100 mm)?
#
# > **Provisional.** `MRMS_ONLY`, V1, provisional severity — a screening view, not a reportable layer.

# %% [markdown]
# ## 0 — Load the risk layer

# %%
from __future__ import annotations

import glob
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib.colors import LogNorm

plt.rcParams.update({"axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130})


def repo_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise FileNotFoundError("repo root not found")


ROOT = repo_root()
# Default to the QC'd canonical grid; override with HAZARD_CONUS_GRID_RISK_RUN_ID (e.g. the pre-QC baseline).
RISK_RUN_ID = os.environ.get("HAZARD_CONUS_GRID_RISK_RUN_ID", "20260625_conus_grid_hail_solar_v1_qcd")
GRID_ROOT = ROOT / "data" / "hazard_conus_grid" / "hail" / "solar" / "v1_mrms_only" / "m2_m4_conus_grid" / f"run_id={RISK_RUN_ID}"
MAP_DIR = GRID_ROOT / "maps"

matches = sorted(glob.glob(str(GRID_ROOT / "tables" / "*risk*.parquet")))
if not matches:
    raise FileNotFoundError(f"no risk layer under {GRID_ROOT} — has the grid run finished?")
risk = pd.read_parquet(matches[0])
MAP_DIR.mkdir(parents=True, exist_ok=True)

# One policy's slice is one row per cell. Default view = the raw-MESH policy (the honest-severity policy
# differs only via the M1 cap, which is moot for solar loss); cap-100 used for the side-by-side.
HAS_QC = "frequency_spike_flag" in risk.columns
raw = risk[risk["severity_policy"] == "raw_mrms"].copy()
cap = risk[risk["severity_policy"] == "cap_100mm_sensitivity"].copy()

print("risk run:", RISK_RUN_ID)
print("rows:", len(risk), " cells:", risk["cell_id"].nunique(), " policies:", sorted(risk["severity_policy"].unique()))
print("QC columns present:", HAS_QC)

# %% [markdown]
# ## 1 — National summary (per severity policy)
#
# The grid places one canonical 100 MW solar plant at every served cell, so the "national EAL" is the sum
# of per-cell EAL across the grid — a comparable aggregate, not a portfolio of real assets.

# %%
rows = []
for policy, sub in risk.groupby("severity_policy"):
    row = {
        "severity_policy": policy,
        "cells": int(sub["cell_id"].nunique()),
        "cells_eal_gt0": int((sub["eal_usd"] > 0).sum()),
        "national_eal_usd_M": round(float(sub["eal_usd"].sum()) / 1e6, 2),
        "mean_eal_pct_tiv": round(float(sub["eal_pct_tiv"].mean()) * 100, 4),
        "median_eal_pct_tiv": round(float(sub["eal_pct_tiv"].median()) * 100, 4),
        "max_eal_pct_tiv": round(float(sub["eal_pct_tiv"].max()) * 100, 3),
        "max_pml100_pct_tiv": round(float(sub["pml100_pct_tiv"].max()) * 100, 3),
    }
    if HAS_QC:
        row["spike_cells_held_out"] = int(sub["frequency_spike_flag"].sum())
        row["hard_artifact_cells"] = int(sub["hard_artifact_flag"].sum())
    rows.append(row)
summary = pd.DataFrame(rows)
display(summary)
print("(EAL/PML shown as % of TIV; national EAL in $M = sum of per-cell EAL over the canonical-asset grid.)")

# %% [markdown]
# ## 2 — Maps
#
# CONUS scatter on the 0.25° cell centres. Grey = served cells with no/zero metric; colour = the metric.

# %%
def base_map(ax: plt.Axes, title: str) -> None:
    ax.set_title(title)
    ax.set(xlabel="Longitude", ylabel="Latitude", xlim=(-125.5, -66.0), ylim=(24.0, 50.5))
    ax.set_aspect("equal", adjustable="box")


def metric_map(frame: pd.DataFrame, metric: str, title: str, cbar_label: str, fname: str,
               *, scale: float = 1.0, cmap: str = "viridis", log: bool = False) -> Path:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.scatter(frame["lon_center"], frame["lat_center"], s=2.0, c="#dddddd", linewidths=0, alpha=0.5)
    hot = frame[frame[metric].fillna(0) > 0].copy()
    vals = hot[metric].to_numpy(dtype="float64") * scale
    norm = LogNorm(vmin=max(vals.min(), 1e-6), vmax=vals.max()) if (log and len(vals)) else None
    sc = ax.scatter(hot["lon_center"], hot["lat_center"], s=5, c=vals, cmap=cmap, norm=norm, linewidths=0, alpha=0.9)
    if len(hot):
        fig.colorbar(sc, ax=ax, shrink=0.78).set_label(cbar_label)
    base_map(ax, title)
    fig.tight_layout()
    path = MAP_DIR / fname
    fig.savefig(path, bbox_inches="tight")
    plt.show()
    return path


eal_map = metric_map(raw, "eal_pct_tiv", "Hail × Solar — EAL (% of TIV), raw-MESH policy",
                     "EAL (% of TIV)", f"conus_grid_eal_pct_tiv_{RISK_RUN_ID}.png", scale=100.0, cmap="magma")
pml_map = metric_map(raw, "pml100_pct_tiv", "Hail × Solar — PML₁₀₀ (% of TIV), raw-MESH policy",
                     "PML₁₀₀ (% of TIV)", f"conus_grid_pml100_pct_tiv_{RISK_RUN_ID}.png", scale=100.0, cmap="inferno")
lam_map = metric_map(raw, "lambda_cell", "Hail — severe-hail-day rate λ (severe days/yr)",
                     "λ (severe days/yr)", f"conus_grid_lambda_{RISK_RUN_ID}.png", cmap="plasma", log=True)

# %% [markdown]
# **Takeaway.** The EAL/PML maxima should sit in the central hail corridor; the broad gradient is the V1
# screening signal. λ is the asset-free frequency field these inherit.

# %% [markdown]
# ## 3 — QC overlays (capped severity · hard artifacts · frequency spikes held out)
#
# Only available when viewing the QC'd layer. Shows where the plausibility QC acted.

# %%
if HAS_QC:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.scatter(raw["lon_center"], raw["lat_center"], s=2.0, c="#e8e8e8", linewidths=0, alpha=0.5)
    capped = raw[raw["severity_capped_flag"] & ~raw["hard_artifact_flag"]]
    hard = raw[raw["hard_artifact_flag"]]
    spike = raw[raw["frequency_spike_flag"]]
    ax.scatter(capped["lon_center"], capped["lat_center"], s=10, c="#2b8cbe", linewidths=0,
               label=f"severity capped 203–300 mm ({len(capped)})")
    ax.scatter(hard["lon_center"], hard["lat_center"], s=14, c="#d7191c", linewidths=0,
               label=f"hard artifact ≥300 mm ({len(hard)})")
    ax.scatter(spike["lon_center"], spike["lat_center"], s=46, facecolors="none", edgecolors="black",
               linewidths=0.9, label=f"frequency spike, held out ({len(spike)})")
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    base_map(ax, "Plausibility QC — where the rule acted (raw-MESH policy)")
    fig.tight_layout()
    qc_map = MAP_DIR / f"conus_grid_qc_overlay_{RISK_RUN_ID}.png"
    fig.savefig(qc_map, bbox_inches="tight")
    plt.show()
    print(f"capped(203–300mm)={len(capped)}  hard_artifact(≥300mm)={len(hard)}  freq_spike_held_out={len(spike)}")
else:
    print("QC columns absent — viewing the pre-QC baseline. Re-run with the QC'd layer for these overlays.")

# %% [markdown]
# **Takeaway.** The hard-artifact and frequency-spike cells are flagged + (spikes) held out of reportable
# loss; their severity is capped at the physical ceiling. The hazard layer is physically honest.

# %% [markdown]
# ## 4 — Raw vs 100 mm-capped severity (solar): the magnitude tail is moot
#
# Per cell, EAL under the raw-MESH policy vs the 100 mm-cap policy. They cluster on the 1:1 line because the
# solar damage curve is ~99% saturated by 100 mm — so capping severity *barely* moves solar loss (a few %
# on cells with material EAL, not exactly zero).

# %%
merged = raw[["cell_id", "eal_pct_tiv"]].merge(
    cap[["cell_id", "eal_pct_tiv"]], on="cell_id", suffixes=("_raw", "_cap")
)
fig, ax = plt.subplots(figsize=(5.6, 5.6))
ax.scatter(merged["eal_pct_tiv_raw"] * 100, merged["eal_pct_tiv_cap"] * 100, s=6, alpha=0.4, color="crimson")
lim = float(max(merged["eal_pct_tiv_raw"].max(), merged["eal_pct_tiv_cap"].max()) * 100) or 1.0
ax.plot([0, lim], [0, lim], color="black", lw=1, ls="--", label="1:1")
ax.set(title="EAL — raw vs 100 mm-cap (solar)", xlabel="raw-MESH EAL (% TIV)", ylabel="100 mm-cap EAL (% TIV)")
ax.legend(fontsize=8)
fig.tight_layout()
policy_cmp = MAP_DIR / f"conus_grid_raw_vs_cap_eal_{RISK_RUN_ID}.png"
fig.savefig(policy_cmp, bbox_inches="tight")
plt.show()
absdiff = (merged["eal_pct_tiv_raw"] - merged["eal_pct_tiv_cap"]).abs()
material = merged["eal_pct_tiv_raw"] > 0.005  # EAL > 0.5% of TIV (tiny-EAL cells inflate relative diffs)
rel_material = float((absdiff[material] / merged.loc[material, "eal_pct_tiv_raw"]).max()) if material.any() else float("nan")
print(f"max ABSOLUTE EAL diff raw-vs-cap: {absdiff.max() * 100:.3f} %TIV points")
print(f"max RELATIVE EAL diff among material cells (EAL>0.5% TIV): {rel_material:.2%}  ({int(material.sum())} cells)")
print("(near-zero-EAL cells inflate the relative diff via tiny denominators; the absolute diff is the honest measure)")
print("=> solar loss is largely tail-insensitive (curve saturates ~100 mm), not exactly zero.")

# %% [markdown]
# ## 5 — Recap
#
# - The full-CONUS hail × solar risk layer renders as the comparable screening map family (EAL, PML, λ).
# - The QC'd hazard layer is physically honest (severity capped) and flags + holds out the frequency spikes.
# - Raw and 100 mm-cap severity are nearly identical for solar (~a few % on material cells) — the magnitude
#   tail is a minor, not dominant, loss driver.
# - Still provisional V1 (`MRMS_ONLY`, provisional severity); not a reportable layer.
