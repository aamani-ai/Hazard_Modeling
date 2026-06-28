"""hail — the hail peril pipeline (M0/M1).

Peril-specific side of the layered pipeline: it owns the MRMS source adapter (raw tile →
per-cell-day evidence) and, later, the M1 fit that emits the typed hazard-distribution boundary
object the shared `risk_engine` consumes. It imports `risk_engine` (for `io_base`), never the
reverse.

Phase B (this slice) extracts the M0 transform verbatim from
scripts/run_mrms_v1_m0_daily_evidence_batch.py — behaviour-preserving, proven by
tests/test_adapter_reproduces_m0.py.
"""

from . import config
from .mrms_m0 import (
    BatchContext,
    build_daily_panel,
    read_mrms_grib,
    native_points_to_cell_id,
    fetch_inventory_source,
    source_timestamp_from_name,
)

__all__ = [
    "config",
    "BatchContext",
    "build_daily_panel",
    "read_mrms_grib",
    "native_points_to_cell_id",
    "fetch_inventory_source",
    "source_timestamp_from_name",
]
