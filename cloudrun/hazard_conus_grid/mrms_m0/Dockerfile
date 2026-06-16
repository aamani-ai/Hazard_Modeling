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

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

COPY run_mrms_v1_m0_daily_evidence_batch.py /app/run_mrms_v1_m0_daily_evidence_batch.py

ENTRYPOINT ["python", "/app/run_mrms_v1_m0_daily_evidence_batch.py"]
