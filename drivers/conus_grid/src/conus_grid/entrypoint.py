"""Run the full-CONUS hail×solar grid: M1 × canonical solar → the per-cell risk layer (Contract-2).

Local entrypoint (the Cloud Run task-indexed fanout, DD-G9, comes later for scale; ~30 min runs fine
locally). Reads the full M1 hazard layer + reconciled-M0 severe events, places the canonical 100 MW
solar asset at every served cell, runs M2→M3→M4 for both severity policies, and writes the gridded risk
layer + a summary + metadata.

Env overrides:
  HAZARD_CONUS_GRID_M1_RUN_ID, MRMS_M0_RECONCILED_RUN_ID, HAZARD_CONUS_GRID_RISK_RUN_ID,
  HAZARD_CONUS_GRID_MC_YEARS (default 250000), HAZARD_CONUS_GRID_CELL_LIMIT (testing: first N cells).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from hail.damage import hail_curve_cap, load_curve
from risk_engine.config import CANONICAL_RETURN_PERIODS

from conus_grid.canonical_assets import CANONICAL_SOLAR, MC_YEARS_DEFAULT, SEED, SEVERITY_POLICIES
from conus_grid.grid_driver import load_severe_events, run_grid


def repo_root() -> Path:
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "AGENTS.md").exists():
            return c
    raise FileNotFoundError("repo root (AGENTS.md) not found")


def main() -> int:
    root = repo_root()
    m1_run_id = os.environ.get("HAZARD_CONUS_GRID_M1_RUN_ID", "20260625_m1_mrms_only_qcd")
    m0_run_id = os.environ.get("MRMS_M0_RECONCILED_RUN_ID", "20260616T225000Z_m0_full_conus_reconciled")
    run_id = os.environ.get(
        "HAZARD_CONUS_GRID_RISK_RUN_ID",
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_m2_m4_conus_grid"),
    )
    mc_years = int(os.environ.get("HAZARD_CONUS_GRID_MC_YEARS", str(MC_YEARS_DEFAULT)))
    cell_limit = os.environ.get("HAZARD_CONUS_GRID_CELL_LIMIT")

    hail = root / "data" / "hazard_conus_grid" / "hail" / "v1_mrms_only"
    m1_parquet = hail / "m1_hazard_layer" / f"run_id={m1_run_id}" / "tables" / f"mrms_v1_m1_hazard_layer_{m1_run_id}.parquet"
    recon = hail / "m0_reconciled_daily_cell_evidence" / f"run_id={m0_run_id}"
    curve_path = root / "data" / "hail" / "damage_curves" / "hail_solar_asset_capex_weighted.json"

    out_root = root / "data" / "hazard_conus_grid" / "hail" / "solar" / "v1_mrms_only" / "m2_m4_conus_grid" / f"run_id={run_id}"
    table_dir = out_root / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    layer_parquet = table_dir / f"mrms_v1_hail_solar_conus_grid_risk_{run_id}.parquet"
    summary_csv = table_dir / f"mrms_v1_hail_solar_conus_grid_summary_{run_id}.csv"
    metadata_json = out_root / f"metadata_{run_id}.json"

    print(f"[conus-grid] run_id={run_id} mc_years={mc_years}", flush=True)
    m1 = pd.read_parquet(m1_parquet)
    if cell_limit:
        m1 = m1.head(int(cell_limit)).copy()
        print(f"[conus-grid] CELL_LIMIT={cell_limit} -> {len(m1)} cells (test run)", flush=True)
    cell_ids = set(m1["cell_id"].astype(int)) if cell_limit else None

    events = load_severe_events(recon, cell_ids=cell_ids)
    curve = load_curve(curve_path)
    print(f"[conus-grid] cells={len(m1):,} severe_events={len(events):,} curve_cap={hail_curve_cap(curve):.4f}", flush=True)

    out = run_grid(
        m1,
        events,
        CANONICAL_SOLAR,
        curve,
        severity_policies=SEVERITY_POLICIES,
        mc_years=mc_years,
        seed=SEED,
        return_periods=CANONICAL_RETURN_PERIODS,
        provenance={"risk_run_id": run_id, "m1_run_id": m1_run_id, "m0_reconciled_run_id": m0_run_id},
    )
    out.to_parquet(layer_parquet, index=False)

    # Per-policy summary (national = sum of per-cell EAL over the canonical-asset grid).
    summary_rows = []
    for policy in SEVERITY_POLICIES:
        sub = out.loc[out["severity_policy"] == policy]
        summary_rows.append(
            {
                "severity_policy": policy,
                "n_cells": int(sub["cell_id"].nunique()),
                "n_cells_eal_gt0": int((sub["eal_usd"] > 0).sum()),
                "national_eal_usd": float(sub["eal_usd"].sum()),
                "mean_eal_pct_tiv": float(sub["eal_pct_tiv"].mean()),
                "median_eal_pct_tiv": float(sub["eal_pct_tiv"].median()),
                "max_eal_pct_tiv": float(sub["eal_pct_tiv"].max()),
                "max_pml100_pct_tiv": float(sub["pml100_pct_tiv"].max()),
                "max_pml500_pct_tiv": float(sub["pml500_pct_tiv"].max()),
                "qa_all_pass": bool(sub["qa_checks_pass"].all()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(summary_csv, index=False)

    metadata = {
        "artifact_family": "mrms_v1_hail_solar_conus_grid_risk",
        "status": "created",
        "risk_run_id": run_id,
        "m1_run_id": m1_run_id,
        "m0_reconciled_run_id": m0_run_id,
        "source_set": "MRMS_ONLY",
        "version": "V1",
        "hazard": "hail",
        "asset_type": "solar",
        "canonical_asset": CANONICAL_SOLAR,
        "mc_years": mc_years,
        "seed": SEED,
        "return_periods": CANONICAL_RETURN_PERIODS,
        "count_model": "poisson_v1_default from M1",
        "severity_policies": SEVERITY_POLICIES,
        "damage_curve_id": curve.get("curve_id"),
        "n_cells": int(out["cell_id"].nunique()),
        "n_rows": int(len(out)),
        "cell_limit_applied": cell_limit,
        "summary": summary.to_dict(orient="records"),
        "outputs": {
            "risk_layer_parquet": str(layer_parquet.relative_to(root)),
            "summary_csv": str(summary_csv.relative_to(root)),
            "metadata_json": str(metadata_json.relative_to(root)),
        },
        "metrics_status": "provisional_conus_grid_not_reportable",
        "allowed_use": ["full-CONUS screening", "map visualization", "raw-vs-capped severity sensitivity"],
        "not_allowed_use": ["final calibrated hail climatology", "reportable EAL/PML/VaR/TVaR"],
        "caveats": [
            "MRMS-only operational-era record; raw/provisional MESH severity (raw + 100mm-cap sensitivity).",
            "Poisson v1 default frequency; canonical 100 MW solar at every cell (not real exposure).",
            "Footprint proxy is severe native-pixel area clipped to the 0.25-degree cell (1px~1km^2).",
        ],
    }
    metadata_json.write_text(json.dumps(metadata, indent=2, default=str) + "\n")

    print(f"[conus-grid] wrote {len(out):,} rows -> {layer_parquet.relative_to(root)}", flush=True)
    print(summary.to_string(index=False), flush=True)
    print("[conus-grid] DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
