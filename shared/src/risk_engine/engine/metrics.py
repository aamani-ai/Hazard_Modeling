"""Exceedance metrics read off the annual loss vectors.

Extracted verbatim (behaviour-preserving) from the hail x solar smoke notebook
``exceedance_metrics`` (L529-578). Two leaks parameterized: the return-period / VaR / TVaR / PML
ladders become arguments (defaulting to the notebook's values), and the per-kWp normalization
takes an explicit ``capacity_kwp`` instead of referencing the solar canonical asset.

The metric identity holds by construction: ``PML_T = VaR_(1 - 1/T)`` (both read off the same AEP
exceedance curve); AEP and OEP are kept as separate frames. Every monetary metric carries both a
``_usd`` and a ``_pct_tiv`` form.
"""

from __future__ import annotations

import numpy as np

DEFAULT_RETURN_PERIODS = [2, 5, 10, 25, 50, 100, 200, 250, 500]
DEFAULT_VAR_CONFIDENCES = [0.95, 0.99, 0.995, 0.996, 0.998]
DEFAULT_TVAR_CONFIDENCES = [0.95, 0.99]
DEFAULT_PML_RETURN_PERIODS = [100, 200, 250, 500]


def exceedance_metrics(
    aep: np.ndarray,
    oep: np.ndarray,
    tiv_usd: float,
    capacity_kwp: float,
    return_periods: list[int] | None = None,
    var_confidences: list[float] | None = None,
    tvar_confidences: list[float] | None = None,
    pml_return_periods: list[int] | None = None,
) -> dict[str, float]:
    """All EAL / AEP / OEP / VaR / TVaR / PML fields (USD and %TIV) for one cell x asset."""
    return_periods = DEFAULT_RETURN_PERIODS if return_periods is None else return_periods
    var_confidences = DEFAULT_VAR_CONFIDENCES if var_confidences is None else var_confidences
    tvar_confidences = DEFAULT_TVAR_CONFIDENCES if tvar_confidences is None else tvar_confidences
    pml_return_periods = DEFAULT_PML_RETURN_PERIODS if pml_return_periods is None else pml_return_periods

    out: dict[str, float] = {}
    out["eal_usd"] = float(np.mean(aep))
    out["eal_pct_tiv"] = out["eal_usd"] / tiv_usd
    out["eal_usd_per_kwp_yr"] = out["eal_usd"] / capacity_kwp
    out["zero_loss_fraction"] = float(np.mean(aep == 0))

    for rp in return_periods:
        q = 1.0 - 1.0 / rp
        aep_q = float(np.quantile(aep, q))
        oep_q = float(np.quantile(oep, q))
        out[f"aep_loss_rp{rp}_usd"] = aep_q
        out[f"oep_loss_rp{rp}_usd"] = oep_q
        out[f"aep_loss_rp{rp}_pct_tiv"] = aep_q / tiv_usd
        out[f"oep_loss_rp{rp}_pct_tiv"] = oep_q / tiv_usd

    for c in var_confidences:
        label = str(c).replace("0.", "")
        aep_q = float(np.quantile(aep, c))
        oep_q = float(np.quantile(oep, c))
        out[f"var_aep_{label}_usd"] = aep_q
        out[f"var_oep_{label}_usd"] = oep_q
        out[f"var_aep_{label}_pct_tiv"] = aep_q / tiv_usd
        out[f"var_oep_{label}_pct_tiv"] = oep_q / tiv_usd

    for c in tvar_confidences:
        label = str(c).replace("0.", "")
        threshold = float(np.quantile(aep, c))
        tail = aep[aep >= threshold]
        out[f"tvar_aep_{label}_usd"] = float(tail.mean()) if len(tail) else 0.0
        out[f"tvar_aep_{label}_pct_tiv"] = out[f"tvar_aep_{label}_usd"] / tiv_usd

    out["var95_usd"] = out["var_aep_95_usd"]
    out["var95_pct_tiv"] = out["var_aep_95_pct_tiv"]
    out["var99_usd"] = out["var_aep_99_usd"]
    out["var99_pct_tiv"] = out["var_aep_99_pct_tiv"]
    out["tvar95_usd"] = out["tvar_aep_95_usd"]
    out["tvar95_pct_tiv"] = out["tvar_aep_95_pct_tiv"]
    out["tvar99_usd"] = out["tvar_aep_99_usd"]
    out["tvar99_pct_tiv"] = out["tvar_aep_99_pct_tiv"]

    for rp in pml_return_periods:
        out[f"pml{rp}_usd"] = out[f"aep_loss_rp{rp}_usd"]
        out[f"pml{rp}_pct_tiv"] = out[f"aep_loss_rp{rp}_pct_tiv"]
        out[f"pml_aep_rp{rp}_usd"] = out[f"aep_loss_rp{rp}_usd"]
        out[f"pml_aep_rp{rp}_pct_tiv"] = out[f"aep_loss_rp{rp}_pct_tiv"]
        out[f"pml_oep_rp{rp}_usd"] = out[f"oep_loss_rp{rp}_usd"]
        out[f"pml_oep_rp{rp}_pct_tiv"] = out[f"oep_loss_rp{rp}_pct_tiv"]

    return out
