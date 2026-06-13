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
# # Wildfire → Solar · M2 — Coupling *(a deliberately thin layer)*
#
# **Peril:** Wildfire · **Layer:** M2 (coupling) · assets: Hayhurst (low-fire) + Matrix (high-fire).
#
# M2 turns M1's per-asset hazard profile into the **coupled handoff** M3/M4 consume. For a **site-conditioned**
# peril this is **thin** — and that thinness is a *finding*, documented here, not a gap to paper over. The
# value of this notebook is **clear assumptions + why it's thin + what improves later**.
#
# > Plan: [`docs/plans/wildfire/m2_coupling.md`](../../../../docs/plans/wildfire/m2_coupling.md) · How it works:
# > [`discussion/wildfire/03`](../../../../docs/extra/discussion/wildfire/03_m2_site_conditioned_coupling.md) ·
# > Assumptions [AW-25–28](../../../../docs/plans/wildfire/assumptions.md).

# %% [markdown]
# ## 1 · Why M2 is thin (the finding)
#
# Hail's M2 was heavy: a Minkowski overlap `(√F+√s)²/A` computing a per-event hit probability against the
# asset polygon. **Wildfire has no such step**, for two compounding reasons:
#
# 1. **FSim pre-integrated the events** — there's no event set to overlap; the hazard is a per-cell field
#    ([learning_logs/09](../../../../docs/learning_logs/09_pre_integrated_vs_extracted_catalog.md)).
# 2. **Site-conditioned → no spatial factor** — there is no "miss"; the rate comes from the site directly
#    (methodology). M1 already produced `(λ, kW/m severity)` **at the asset footprint**.
#
# So **M1 did the coupling that M2 does for hail.** M2's V1 work is small:
#
# | M2 V1 job | V1 choice |
# |---|---|
# | **On-site source / oozing** | burnable footprint (M1's FSim severity already excludes non-burnable). Oozing is **moot at 270 m** (a pixel spans array + surrounding fuel); acute only at WRC 30 m (our cross-check). Surrounding-ring fallback only if a footprint is *entirely* non-burnable — neither asset. |
# | **Exposure fraction** | **1.0 — whole-site on a fire** (partial-burn deferred, AW-28). |
# | **Susceptibility** | **embed `d = 10 m`** (the M3 curve's reference; explicit per-site `d` deferred, AW-27). |
# | **Handoff** | emit `(λ, conditional kW/m severity, exposure)` — same schema M3/M4 consume. |
#
# **What's deferred (named):** fire-front sweep (partial burn, explicit `d`/`t`, real tail) · explicit
# site-feature `d` (defensible space/fences, via site data/imagery) · currency adjustment (stale FSim vintage)
# · heat-flux/temperature curves. M2's honest job is to **emit the clean handoff and flag exactly what it
# embeds vs defers.**

# %%
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd


def _repo_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise FileNotFoundError("repo root not found")


ROOT = _repo_root()
DATA_DIR = ROOT / "data" / "wildfire"
ASSETS = [("hayhurst_texas_solar", "Hayhurst Texas Solar", "baseline (low-fire)"),
          ("matrix_pleasant_valley", "Matrix Pleasant Valley", "proving (high-fire)")]

EXPOSURE_FRACTION = 1.0      # V1: whole-site on a fire (partial-burn deferred — AW-28)
SUSCEPTIBILITY_D_M = 10.0    # V1: the M3 curve's embedded reference distance (explicit per-site d deferred — AW-27)

# %% [markdown]
# ## 2 · Load M1 (the per-asset hazard profile) + the M0 oozing flag
#
# M1 already gives `(λ, kW/m severity)`. We also pull the M0 **WRC** oozing flag (30 m) purely to *document*
# the resolution nuance — the M1 severity itself is FSim 270 m over the burnable footprint, so the on-site
# hazard is already sourced from real fuel.

# %%
prof = {}
for slug, name, role in ASSETS:
    m1 = json.loads((DATA_DIR / f"{slug}_wildfire_m1_manifest.json").read_text())
    sev = pd.read_parquet(DATA_DIR / f"{slug}_wildfire_m1_catalog.parquet")
    wrc = json.loads((DATA_DIR / f"{slug}_wildfire_m0_wrc_manifest.json").read_text())
    prof[slug] = {
        "name": name, "role": role,
        "lambda_per_yr": m1["frequency_process_params"]["lambda_per_yr"],
        "fano": m1["frequency_process_params"]["fano_factor"],
        "severity": sev,                                  # flame_class_ft, midpoint_ft, intensity_kwm, prob_given_fire
        "mean_kwm": m1["conditional_mean_intensity_kwm"],
        "tiv_usd": m1["asset"].get("tiv_usd"),
        "footprint": m1["footprint"],
        "oozed_30m": wrc["checks"]["oozing_at_asset_pixel"],
    }
    print(f"{name:24s} ({role}): λ={prof[slug]['lambda_per_yr']:.5f}/yr · mean|fire={prof[slug]['mean_kwm']:.0f} kW/m "
          f"· WRC-30m oozed@pixel={prof[slug]['oozed_30m']} · footprint: {prof[slug]['footprint']}")

# %% [markdown]
# ## 3 · On-site source / oozing — confirm the hazard comes from real fuel
#
# **The resolution nuance (AW-15):** WRC **30 m** *oozes* BP onto developed pixels while suppressing intensity
# — Hayhurst's array pixel showed this. But our **severity spine is FSim 270 m**, where a pixel spans the array
# *and* its surroundings, so the burnable-footprint mean already reflects real fuel. So the oozing is **moot
# for the spine**; we only fall back to a surrounding ring if a footprint is *entirely* non-burnable.

# %%
for slug, name, _ in ASSETS:
    sev = prof[slug]["severity"]
    burnable_ok = float(sev["prob_given_fire"].sum()) > 0.999      # M1 severity is a valid (Σ=1) burnable distribution
    on_site_source = ("burnable footprint (FSim 270 m — surrounding fuel included; oozing moot)"
                      if burnable_ok else "SURROUNDING RING fallback (footprint entirely non-burnable)")
    prof[slug]["on_site_source"] = on_site_source
    flag = "⚠ WRC-30m pixel was oozed → if we ever use the 30 m layer for severity, source from a ring" if prof[slug]["oozed_30m"] else "—"
    print(f"{name:24s}: severity Σ={sev['prob_given_fire'].sum():.3f} (burnable ✓) · on-site source = {on_site_source}\n"
          f"{'':26s} note: {flag}")

# %% [markdown]
# ## 4 · Exposure fraction — whole-site on a fire (V1)
#
# When a fire occurs, V1 assumes the **whole site** is exposed (`exposure_fraction = 1.0`). Partial-burn — a
# contiguous front taking only part of a large site — needs a **fire-front sweep** (explicit which-cells-burn),
# which also fixes the PML/tail; **deferred** (AW-28). For our single, modest-footprint sites this is a
# reasonable V1 simplification (a fire reaching the site largely burns it).

# %%
print(f"exposure_fraction = {EXPOSURE_FRACTION}  (whole-site on a fire; partial-burn / contiguous-front correlation deferred — fire-front sweep, AW-28)")

# %% [markdown]
# ## 5 · Susceptibility — embed `d = 10 m` (V1)
#
# Susceptibility (how the same intensity does more/less damage) lives in the **distance `d`** from the fire
# front to the asset: more defensible space / fences / fire breaks → larger effective `d` → less heat flux
# (`q = 0.35·I/d`, a **line source ∝ 1/d**) → curve thresholds shift up. V1 **embeds the M3 curve's `d = 10 m`**
# for everyone; explicit per-site `d` (from site data / imagery) is **deferred** (AW-27). *Pre-build: fix the
# damage-curve doc's `I/d²`→`I/d` (AW-17).*

# %%
print(f"susceptibility: embedded d = {SUSCEPTIBILITY_D_M} m (M3 curve reference). Explicit per-site d "
      "(defensible space / fences) deferred — AW-27. Heat flux for a fire FRONT is ∝ 1/d (line source), "
      "NOT 1/d² (fix the curve doc — AW-17).")

# %% [markdown]
# ## 6 · Emit the coupled handoff (per asset)
#
# The M2 → M3/M4 contract: `λ` (count rate) + the **conditional kW/m severity** × `exposure_fraction`. No
# spatial factor, no `p_hit` overlap — occurrence × conditional intensity × whole-site exposure.

# %%
for slug, name, role in ASSETS:
    p = prof[slug]
    coupled = p["severity"][["flame_class_ft", "intensity_kwm", "prob_given_fire"]].copy()
    coupled["exposure_fraction"] = EXPOSURE_FRACTION
    out_pq = DATA_DIR / f"{slug}_wildfire_m2_coupled.parquet"
    coupled.to_parquet(out_pq, index=False)
    summary = {
        "layer": "M2", "candidate": "01_coupling", "peril": "wildfire", "coupling_type": "site_conditioned",
        "asset": {"slug": slug, "name": name, "role": role, "tiv_usd": p["tiv_usd"]},
        "thin_layer": True,
        "why_thin": "FSim pre-integrated the events + site-conditioned (no spatial factor) → M1 produced (λ, kW/m severity) at the asset; no Minkowski overlap.",
        "contract_for_M3_M4": {
            "lambda_per_yr": p["lambda_per_yr"], "fano_factor": p["fano"],
            "exposure_fraction": EXPOSURE_FRACTION,
            "susceptibility_d_m": SUSCEPTIBILITY_D_M,
            "severity": "conditional kW/m distribution (see m2_coupled.parquet / M1 catalog)",
            "conditional_mean_intensity_kwm": p["mean_kwm"],
        },
        "on_site_source": p["on_site_source"], "oozed_wrc_30m_pixel": p["oozed_30m"],
        "no_spatial_factor": True,
        "deferred": ["fire-front sweep (partial burn, explicit d/t, real PML tail) — AW-28",
                     "explicit per-site susceptibility d (defensible space/fences, via site data/imagery) — AW-27",
                     "currency adjustment for stale FSim vintage — AW-25/26",
                     "heat-flux / temperature curves (need explicit d, t) — Gen 3"],
    }
    (DATA_DIR / f"{slug}_wildfire_m2_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {out_pq.relative_to(ROOT)} + summary  ·  λ={p['lambda_per_yr']:.5f}/yr · exposure={EXPOSURE_FRACTION} · d={SUSCEPTIBILITY_D_M}m")

# %% [markdown]
# ## 7 · Verification (basics spot-on)

# %%
for slug, name, _ in ASSETS:
    p = prof[slug]
    sev = p["severity"]
    assert abs(sev["prob_given_fire"].sum() - 1.0) < 1e-4, "severity must sum to 1 (M1 probs stored to 6 dp)"
    assert 0.0 <= EXPOSURE_FRACTION <= 1.0
    m1_lambda = json.loads((DATA_DIR / f"{slug}_wildfire_m1_manifest.json").read_text())["frequency_process_params"]["lambda_per_yr"]
    assert abs(p["lambda_per_yr"] - m1_lambda) < 1e-12, "no spatial factor — λ must pass through unchanged from M1"
    print(f"{name:24s}: Σseverity=1 ✓ · exposure∈[0,1] ✓ · λ unchanged from M1 ✓ (no spatial factor)")
print("\n→ M2 confirms the site-conditioned coupling: λ passes through (no thinning), severity carried, "
      "exposure=whole-site, susceptibility embedded. The interface out matches hail's — standard interface, "
      "specialized (here, minimal) physics.")

# %% [markdown]
# ## 8 · Carry forward → M3
#
# M3 (solar damage) maps the coupled **kW/m** intensity → a **BoS-weighted damage ratio** (curves from
# `infrasure-damage-curves`), then `loss = DR × exposure_fraction × TIV`. The thinness here means the new work
# resumes at M3 (the curve) and M4 (the shared engine) — exactly as the M0–M4 structure intends.

# %%
print("M2 COMPLETE (both assets) — a thin, fully-documented site-conditioned coupling.")
print("Carried forward → M3: conditional kW/m severity × exposure=1.0, per asset, for the BoS-weighted damage curve.")
