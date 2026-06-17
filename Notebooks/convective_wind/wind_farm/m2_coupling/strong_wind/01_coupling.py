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
# # Wind → convective wind → **strong wind** · M2 — coupling (site-conditioned, p_hit ≈ 1)
#
# **Sub-peril:** strong / straight-line wind [W] (of the convective-wind peril) · **Layer:** M2 (coupling) ·
# **Bucket:** site-conditioned.
#
# This is the **deliberately thin** fork — and the thinness is *correct*, not a shortcut. Strong wind is a **broad
# swath**: when a severe-wind event reaches the region, the whole spread-out farm is inside it — there is **no
# hit-or-miss to thin** (`p_hit ≈ 1`). And M1 already read the **per-site** rate + severity off the ASCE
# return-period surface, so the spatial coupling was *already done upstream*. M2's job is the **honest handoff**:
# pass the M1 profile through unchanged, with **no spatial factor** — exactly **wildfire's M2 reused**.
#
# Sibling fork (the areal one): [`m2_coupling/tornado/01_coupling`](../../m2_coupling/tornado/01_coupling.ipynb).
#
# > Plan: [`m2_coupling.md`](../../../../../docs/plans/convective_wind/m2_coupling.md) · the site-conditioned bucket:
# > [`discussion/convective_wind/02`](../../../../../docs/extra/discussion/convective_wind/02_coupling_buckets_and_wind.md) ·
# > reuses wildfire's [`m2_coupling`](../../../../wildfire/solar/m2_coupling/01_coupling.ipynb).

# %% [markdown]
# ## 0 · Intent & scope
#
# **Does:** confirm strong wind is **site-conditioned** — `p_hit = 1`, `exposure_fraction = 1`, **no spatial
# factor** — pass the M1 per-site `λ` + bounded-Gumbel severity through unchanged, and emit the coupling contract.
# **Documents the thinness** rather than manufacturing coupling that isn't there (the wildfire discipline, [DD-WN-4](../../../../../docs/plans/convective_wind/decisions.md)).
#
# **Does NOT:** apply a Minkowski / `λ_collection · p` factor (that's the *tornado* fork — strong wind has no
# "miss"); build the damage curve (M3) or sample loss (M4).
#
# > **Why this layer barely moves a number.** Strong wind's *catastrophic-damage* contribution is **≈ 0** (gusts
# > stay below IEC survival — AWN-31, [discussion/convective_wind/01 §7a](../../../../../docs/extra/discussion/convective_wind/01_scope_and_sub_peril_taxonomy.md)).
# > So this is a thin coupling **× a ≈0-damage curve** — we still carry it end-to-end (the honest small number +
# > the M3 known-answer check), but the *material* strong-wind impact (operational disruption + fatigue) is the
# > **deferred disruption track**, not this damage track.

# %% [markdown]
# ## Assumptions (this layer)
#
# - **AWN-20** — strong-wind coupling = **site-conditioned** (bucket 3): broad swath, no areal "miss"; the asset
#   reads its **local RP gust**; **no spatial factor** (`λ_asset = λ` from M1, unchanged); reuses wildfire's thin M2.
# - **AWN-22** — **single-site only**: strong wind is broad-swath-correlated across a portfolio, but V1 models one
#   site at a time, so **portfolio correlation is documented + deferred** (EAL right; portfolio tail not yet modeled).
# - **AWN-31** — strong-wind damage ≈ 0 (this coupling × ≈0 curve); disruption/degradation deferred.
#
# Register: [`assumptions.md`](../../../../../docs/plans/convective_wind/assumptions.md).

# %% [markdown]
# ## 1 · The bucket — site-conditioned, why `p_hit ≈ 1`, why thin is correct
#
# A derecho / downburst / synoptic high-wind event is a **broad swath** — *"affects whole regions and every
# asset."* There is no finite footprint that might land elsewhere and miss you: if the swath reaches your region,
# your farm is inside it and reads its **local gust**. So:
#
# - **`p_hit ≈ 1`** — no Bernoulli hit/miss, no Minkowski overlap, **no `λ_collection · p` thinning.** (Contrast
#   tornado, where `p_hit` is tiny and the loss is a swept *fraction*.)
# - **The spatial integration already happened upstream.** M1 read `λ` and the severity straight off the ASCE
#   return-period **surface** (profile-assembly) — the surface *is* the per-site profile, all events pre-integrated.
#   So M2 has nothing to spatially couple; it just **declares** the site-conditioned handoff.
# - **We document the thinness; we do not invent coupling.** A thin M2 here is the *correct* shape, not a gap —
#   the wildfire lesson ([learning-09](../../../../../docs/learning_logs/09_pre_integrated_vs_extracted_catalog.md)).

# %%
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _repo_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise FileNotFoundError("repo root (AGENTS.md) not found")


ROOT = _repo_root()
DATA_DIR = ROOT / "data" / "convective_wind"
ASSETS = [
    {"slug": "traverse_wind_ok", "name": "Traverse Wind Energy Center", "role": "proving (high-wind)"},
    {"slug": "shepherds_flat_or", "name": "Shepherds Flat", "role": "baseline (low-wind)"},
]
print(f"repo root: {ROOT}")

# %% [markdown]
# ## 2 · Load the M1 strong-wind catalog (the profile we pass through)

# %%
for a in ASSETS:
    m1 = json.loads((DATA_DIR / f"{a['slug']}_wind_m1_manifest.json").read_text())
    sw = m1["strong_wind"]
    a["lambda_m1"] = sw["frequency_process_params"]["lambda_per_yr"]
    a["fano"] = sw["frequency_process_params"]["fano_factor"]
    a["severity"] = sw["severity_distribution"]        # Gumbel/exponential (ξ≈0), capped at L
    a["tiv"] = m1["tiv_usd"]
    print(f"{a['name']:30s}: M1 strong-wind λ={a['lambda_m1']:.3f}/yr · fano={a['fano']} · "
          f"severity ξ={a['severity']['xi']} (Gumbel/exp) · TIV ${a['tiv']/1e6:.0f}M")

# %% [markdown]
# ## 3 · The site-conditioned handoff — pass through, no spatial factor

# %%
for a in ASSETS:
    a["p_hit"] = 1.0
    a["exposure_fraction"] = 1.0
    a["lambda_asset"] = a["lambda_m1"]                  # UNCHANGED — no thinning (site-conditioned)
    print(f"{a['name']:30s}: p_hit={a['p_hit']} · exposure={a['exposure_fraction']} · "
          f"λ_asset={a['lambda_asset']:.3f}/yr  (== M1 λ, no spatial factor)")
print("\n→ No Minkowski, no λ_collection·p. The asset reads its local RP gust (M1); the whole farm is in the swath.")
print("  Portfolio correlation across multiple farms (broad-swath → correlated) is documented + DEFERRED (AWN-22).")

# %% [markdown]
# ## 4 · Known-answer checks (basics spot-on)

# %%
for a in ASSETS:
    checks = {
        "p_hit == 1 (no hit-or-miss)": a["p_hit"] == 1.0,
        "exposure_fraction == 1 (whole farm in the swath)": a["exposure_fraction"] == 1.0,
        "λ_asset == M1 λ (no thinning / no spatial factor)": a["lambda_asset"] == a["lambda_m1"],
        "severity is Gumbel/exp ξ≈0 (passthrough, not re-fit)": abs(a["severity"]["xi"]) < 1e-6,
    }
    print(f"{a['name']}:")
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    assert all(checks.values()), f"{a['slug']} failed a strong-wind M2 check"
print("\nall known-answer checks PASS — the site-conditioned handoff is thin and correct (no manufactured coupling).")

# %% [markdown]
# ## 5 · Emit the strong-wind coupling contract (→ M3/M4)

# %%
for a in ASSETS:
    rec = pd.DataFrame([{"asset": a["slug"], "sub_peril": "strong_wind", "coupling_bucket": "site_conditioned",
                         "lambda_asset_per_yr": round(a["lambda_asset"], 4), "fano_factor": a["fano"],
                         "p_hit": 1.0, "exposure_fraction": 1.0}])
    out_pq = DATA_DIR / f"{a['slug']}_wind_m2_strongwind_coupling.parquet"
    rec.to_parquet(out_pq, index=False)
    manifest = {
        "layer": "M2", "source": "m2_coupling/strong_wind/01_coupling", "peril": "wind", "sub_peril": "strong_wind",
        "coupling_bucket": "site_conditioned (no hit-or-miss; no spatial factor)",
        "asset": {k: a[k] for k in ("slug", "name", "role")},
        "frequency": {"lambda_asset_per_yr": round(a["lambda_asset"], 4), "fano_factor": a["fano"],
                      "process": "poisson", "thinning": "NONE — site-conditioned, λ_asset = M1 λ unchanged"},
        "p_hit": 1.0, "exposure_fraction": 1.0,
        "conditional_severity": a["severity"],          # passthrough from M1 (Gumbel/exp, ξ≈0, capped at L)
        "tiv_usd": a["tiv"],
        "portfolio_correlation": "documented, DEFERRED (broad-swath correlated across farms; single-site V1, AWN-22)",
        "damage_note": "strong-wind damage ≈0 (AWN-31): this thin coupling feeds a ≈0 curve in M3; disruption/degradation deferred",
    }
    (DATA_DIR / f"{a['slug']}_wind_m2_strongwind_coupling_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(f"wrote {out_pq.relative_to(ROOT)} · λ_asset={a['lambda_asset']:.3f}/yr (p_hit=1) + manifest")

# %% [markdown]
# ### Findings & open questions (→ M3 / M4)
#
# - **Site-conditioned confirmed**: `p_hit = 1`, `exposure = 1`, `λ_asset = M1 λ` (0.90/yr Traverse · 0.36/yr
#   Shepherds Flat) — **no spatial factor**, the wildfire-thin handoff. The asset reads its local RP gust.
# - **This is a thin coupling × a ≈0-damage curve** (AWN-31): strong wind carries through M3/M4 end-to-end but
#   contributes ≈0 catastrophic loss (the honest small number + the M3 known-answer check). Its *material* impact —
#   operational disruption + fatigue — is the **deferred disruption track**, not this damage track.
# - **Portfolio correlation** (broad swath → correlated across farms) is **documented + deferred** (AWN-22) — V1 is
#   single-site, so the portfolio tail is not yet modeled (EAL is right).
# - **(M3/M4)** the conditional loss = `DR(local gust) × TIV` (full exposure, no swept fraction); M4 samples
#   `N ~ Poisson(λ_asset)` events/yr and combines with tornado into one annual-loss distribution — EAL additive,
#   tail off the joint ([discussion/convective_wind/04](../../../../../docs/extra/discussion/convective_wind/04_aggregation_and_double_counting.md)).
