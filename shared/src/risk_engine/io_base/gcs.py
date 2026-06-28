"""GCS helpers, de-duplicated from ``run_mrms_v1_m0_daily_evidence_batch.py`` and
``reconcile_mrms_v1_m0_batches.py`` (where they were byte-for-byte copies). google-cloud-storage
when present; gcloud CLI fallback. No peril/asset knowledge — pure plumbing.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def is_gcs_uri(value) -> bool:
    return str(value).startswith("gs://")


def split_gcs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError(f"not a GCS URI: {uri}")
    rest = uri[5:]
    bucket, _, blob = rest.partition("/")
    if not bucket or not blob:
        raise ValueError(f"invalid GCS URI: {uri}")
    return bucket, blob


def download_gcs_uri(uri: str, local_path: Path) -> Path:
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from google.cloud import storage  # type: ignore

        bucket_name, blob_name = split_gcs_uri(uri)
        storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", uri, str(local_path)], check=True)
    return local_path


def upload_file_to_gcs(local_path: Path, destination_uri: str) -> None:
    try:
        from google.cloud import storage  # type: ignore

        bucket_name, blob_name = split_gcs_uri(destination_uri)
        storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))
    except Exception:
        subprocess.run(["gcloud", "storage", "cp", str(local_path), destination_uri], check=True)


def gcs_prefix_exists(uri: str) -> bool:
    try:
        from google.cloud import storage  # type: ignore

        bucket_name, prefix = split_gcs_uri(uri.rstrip("/") + "/_probe")
        prefix = prefix.rsplit("/", 1)[0].rstrip("/") + "/"
        return any(storage.Client().bucket(bucket_name).list_blobs(prefix=prefix, max_results=1))
    except Exception:
        result = subprocess.run(
            ["gcloud", "storage", "ls", f"{uri.rstrip('/')}/**"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode == 0
