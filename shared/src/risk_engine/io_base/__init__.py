"""io_base — shared GCS plumbing (de-duplicated from the M0 ingest + reconcile scripts).

Peril-/asset-agnostic. Uses google-cloud-storage when available, falling back to the gcloud CLI.
"""

from .gcs import (
    is_gcs_uri,
    split_gcs_uri,
    download_gcs_uri,
    upload_file_to_gcs,
    gcs_prefix_exists,
)

__all__ = [
    "is_gcs_uri",
    "split_gcs_uri",
    "download_gcs_uri",
    "upload_file_to_gcs",
    "gcs_prefix_exists",
]
