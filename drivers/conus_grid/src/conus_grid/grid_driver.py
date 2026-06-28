"""The CONUS grid driver — M1 hazard layer × canonical asset → per-cell risk metrics (Contract-2).

For each served cell: take ``lambda_cell_raw`` from M1 and the cell's severe-day events from reconciled
M0, then run the shared engine per severity policy:

    M2 couple (hail areal) → M3 damage (capex-weighted curve) → M4 run_cell_risk → one risk row.

The per-cell M2–M4 math is the shared ``risk_engine.orchestration.run_cell_risk``; this driver only owns
the grid wiring (load M1 + events, place the canonical asset, fan over cells × policies, assemble rows).
Restricted to the smoke cells it reproduces the worked smoke metrics bit-for-bit (the gate); over all
13,085 served cells it produces the gridded risk layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from hail.coupling import COUPLING_BASIS, hail_event_p_hit
from hail.damage import hail_damage_ratio, load_curve
from risk_engine.config import CANONICAL_RETURN_PERIODS
from risk_engine.orchestration import run_cell_risk

from conus_grid.canonical_assets import MC_YEARS_DEFAULT, SEED, SEVERITY_POLICIES

# Reconciled-M0 columns the driver needs for M2 (areal coupling) + M3 (damage).
EVENT_COLUMNS = [
    "cell_id",
    "date",
    "severe_area_km2_approx",
    "n_native_pixels_observed",
    "mesh_max_mm",
    "hail_day_flag",
]


def load_severe_events(recon_root: str | Path, cell_ids: set[int] | None = None) -> pd.DataFrame:
    """Stream the reconciled-M0 daily partitions and return the severe cell-day event sample.

    Filters ``hail_day_flag == True`` (the M2/M3 events) per partition — and to ``cell_ids`` when given
    (the gate restricts to the smoke cells). Reads partition-by-partition with an explicit column list
    to dodge the ``date`` partition-inference dtype clash.
    """
    recon_root = Path(recon_root)
    files = sorted(recon_root.glob("date=*/part-000.parquet"))
    if not files:
        raise FileNotFoundError(f"no reconciled M0 partitions under {recon_root}")
    want = {int(c) for c in cell_ids} if cell_ids is not None else None

    frames: list[pd.DataFrame] = []
    for file in files:
        df = pq.ParquetFile(file).read(columns=EVENT_COLUMNS).to_pandas()
        sub = df.loc[df["hail_day_flag"].astype(bool)]
        if want is not None:
            sub = sub.loc[sub["cell_id"].isin(want)]
        if len(sub):
            frames.append(sub)

    events = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=EVENT_COLUMNS)
    events["date"] = pd.to_datetime(events["date"])
    return events


def _qa_flags(cell: pd.Series, policy_name: str) -> str:
    flags = [
        "mrms_only_v1",
        "conus_grid",
        "provisional_severity",
        "not_reportable",
        "poisson_v1_default",
        "raw_mrms_mesh_input",
        "cell_clipped_footprint_proxy",
    ]
    if bool(cell["zero_hail_flag"]):
        flags.append("zero_observed_severe_days")
    if str(cell["severity_magnitude_status"]) == "raw_mesh_tail_requires_qa":
        flags.append("severity_tail_requires_qa")
    if bool(cell.get("hard_artifact_flag", False)):
        flags.append("severity_hard_artifact_capped")
    elif bool(cell.get("severity_capped_flag", False)):
        flags.append("severity_physically_capped")
    if bool(cell.get("frequency_spike_flag", False)):
        flags.append("frequency_spike_held_out")
    if policy_name != "raw_mrms":
        flags.append("severity_cap_sensitivity")
    return ";".join(flags)


def _pct(value: float, tiv_usd: float) -> float:
    return value / tiv_usd if np.isfinite(value) else float("nan")


def run_grid(
    m1: pd.DataFrame,
    events: pd.DataFrame,
    asset: dict[str, Any],
    curve: dict[str, Any],
    *,
    severity_policies: dict[str, Any] = SEVERITY_POLICIES,
    mc_years: int = MC_YEARS_DEFAULT,
    seed: int = SEED,
    return_periods: list[int] = CANONICAL_RETURN_PERIODS,
    provenance: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Run M2–M4 for every cell in ``m1`` × every severity policy; return the Contract-2 risk layer.

    Args:
        m1: M1 hazard layer rows (one per cell; needs ``lambda_cell_raw`` + identity/QA fields).
        events: severe cell-day events from :func:`load_severe_events` (for the cells in ``m1``).
        asset: a canonical exposure profile (``CANONICAL_SOLAR``).
        curve: the loaded damage-curve artifact (subsystems).
        severity_policies, mc_years, seed, return_periods: run config (defaults match the worked smoke).
        provenance: optional run-id / curve-id strings stamped on every row.

    One row per ``(cell_id × severity_policy)``. Cells iterate in any order — each is independent and
    seeded by ``cell_id`` — so results are order-invariant.
    """
    asset_area = float(asset["asset_area_km2"])
    tiv = float(asset["tiv_usd"])
    capacity_kwp = float(asset["capacity_mw"]) * 1000.0
    prov = provenance or {}

    # Group events by cell, each in date order, so the engine's event sampling is reproducible.
    by_cell = {
        int(cid): g for cid, g in events.sort_values(["cell_id", "date"]).groupby("cell_id", sort=False)
    }

    rows: list[dict[str, Any]] = []
    for _, cell in m1.iterrows():
        cell_id = int(cell["cell_id"])
        lambda_cell = float(cell["lambda_cell_raw"])
        cell_events = by_cell.get(cell_id)
        n_events = 0 if cell_events is None else len(cell_events)

        if n_events:
            p_hit, _footprint, _bucket = hail_event_p_hit(cell_events, asset_area)
            mesh = cell_events["mesh_max_mm"].astype(float).to_numpy(dtype="float64")
        else:
            p_hit = np.array([], dtype="float64")
            mesh = np.array([], dtype="float64")

        for policy_name, policy in severity_policies.items():
            cap_mm = policy["cap_mm"]
            if n_events:
                mesh_for_damage = mesh if cap_mm is None else np.minimum(mesh, float(cap_mm))
                cond_loss = np.asarray(hail_damage_ratio(mesh_for_damage, curve), dtype="float64") * tiv
                p_hit_arr = p_hit
            else:
                cond_loss = np.array([], dtype="float64")
                p_hit_arr = np.array([], dtype="float64")

            rng = np.random.default_rng(seed + cell_id + (0 if policy_name == "raw_mrms" else 10_000_000))
            res = run_cell_risk(
                p_hit_arr,
                cond_loss,
                lambda_cell,
                mc_years,
                tiv,
                capacity_kwp,
                rng,
                return_periods,
            )

            row: dict[str, Any] = {
                "hazard": str(cell.get("hazard", "hail")),
                "asset_type": asset["asset_type"],
                "schema_version": "1.0",
                "model_version": "conus_grid_hail_solar_v1",
                "risk_run_id": prov.get("risk_run_id", ""),
                "m1_run_id": prov.get("m1_run_id", str(cell.get("m1_run_id", ""))),
                "m0_reconciled_run_id": prov.get("m0_reconciled_run_id", str(cell.get("input_m0_reconciled_run_id", ""))),
                "damage_curve_id": str(curve.get("curve_id", "")),
                "cell_id": cell_id,
                "lat_center": cell["lat_center"],
                "lon_center": cell["lon_center"],
                "state_abbr": cell["state_abbr"],
                "iso_rto": cell["iso_rto"],
                "capacity_mw": asset["capacity_mw"],
                "asset_area_km2": asset["asset_area_km2"],
                "tiv_usd": tiv,
                "tiv_usd_per_kwp": asset["tiv_usd_per_kwp"],
                "lambda_cell": lambda_cell,
                "lambda_cell_basis": "n_severe_hail_days / observed_years from MRMS-only M1",
                "freq_dist_used": "poisson_v1_default",
                "freq_fit_status": cell["freq_fit_status"],
                "severity_policy": policy_name,
                "severity_policy_description": policy["description"],
                "severity_magnitude_status": cell["severity_magnitude_status"],
                "size_dist_status": cell["size_dist_status"],
                "m2_coupling_basis": COUPLING_BASIS,
                "mc_years": mc_years,
                "n_observed_days": int(cell["n_observed_days"]),
                "n_observed_severe_hail_days": int(cell["n_severe_hail_days"]),
                "n_event_samples": int(n_events),
                "max_raw_mesh_mm_any_day": float(cell["max_mesh_mm_raw_any_day"]),
                "max_capped_mesh_mm_any_day": float(cell.get("max_mesh_mm_capped_any_day", cell["max_mesh_mm_raw_any_day"])),
                "physical_cap_mm": float(cell.get("physical_cap_mm", float("nan"))),
                "extreme_mesh_cell_day_count": int(cell["extreme_mesh_cell_day_count"]),
                "hard_artifact_flag": bool(cell.get("hard_artifact_flag", False)),
                "severity_capped_flag": bool(cell.get("severity_capped_flag", False)),
                "frequency_spike_flag": bool(cell.get("frequency_spike_flag", False)),
                "reportable_loss_eligible": bool(cell.get("reportable_loss_eligible", True)),
                "metrics_status": (
                    "provisional_conus_grid_frequency_spike_held_out"
                    if bool(cell.get("frequency_spike_flag", False))
                    else "provisional_conus_grid_not_reportable"
                ),
                "allowed_use": "full_conus_screening_and_m2_m4_with_tail_warnings",
                "not_allowed_use": "final calibrated hail climatology or reportable EAL/PML/VaR/TVaR",
                "qa_flags": _qa_flags(cell, policy_name),
            }
            row.update(res)
            row["cond_loss_mean_pct_tiv"] = _pct(res["cond_loss_mean_usd"], tiv)
            row["cond_loss_p50_pct_tiv"] = _pct(res["cond_loss_p50_usd"], tiv)
            row["cond_loss_p95_pct_tiv"] = _pct(res["cond_loss_p95_usd"], tiv)
            row["cond_loss_p99_pct_tiv"] = _pct(res["cond_loss_p99_usd"], tiv)
            row["cond_loss_max_pct_tiv"] = _pct(res["cond_loss_max_usd"], tiv)
            rows.append(row)

    return pd.DataFrame(rows)
