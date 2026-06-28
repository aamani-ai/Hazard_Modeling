FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libeccodes0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build context is the repo root (see .dockerignore). Install runtime deps first — these also
# satisfy the shared/ + pipelines/ packages, which are then installed with --no-deps.
COPY cloudrun/hazard_conus_grid/mrms_m0/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# The shared risk engine + the hail pipeline (the M0 ingest now imports these).
COPY shared /app/shared
COPY pipelines/hail /app/pipelines/hail
RUN python -m pip install --no-cache-dir --no-deps /app/shared /app/pipelines/hail

# The M0 daily-evidence batch entrypoint.
COPY scripts/run_mrms_v1_m0_daily_evidence_batch.py /app/run_mrms_v1_m0_daily_evidence_batch.py

ENTRYPOINT ["python", "/app/run_mrms_v1_m0_daily_evidence_batch.py"]
