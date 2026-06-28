"""Canonical risk-metric ladders — pinned once (resolves the RP-200 discrepancy; DD-G12).

Every driver references these, so a ladder change is one edit, not three notebooks. The canonical
return-period ladder includes **200** because ``PML_200 = VaR_99.5`` is a named readout (the smoke
code always used it; ``output_schema.md`` had simply omitted it).

These mirror ``risk_engine.engine.metrics`` DEFAULT_* exactly. Phase C will make ``metrics`` import
these instead of carrying its own defaults; until then they are kept identical and the driver passes
``return_periods=CANONICAL_RETURN_PERIODS`` while letting the VaR/TVaR/PML ladders default in
``metrics`` (so the engine output matches the worked smoke bit-for-bit).
"""

from __future__ import annotations

CANONICAL_RETURN_PERIODS = [2, 5, 10, 25, 50, 100, 200, 250, 500]
CANONICAL_VAR_CONFIDENCES = [0.95, 0.99, 0.995, 0.996, 0.998]
CANONICAL_TVAR_CONFIDENCES = [0.95, 0.99]
CANONICAL_PML_RETURN_PERIODS = [100, 200, 250, 500]
