# Project: OpenCLAW — Autonomous AI Research & Literary Agent 24/7
# Copyright (c) 2026 Francisco Angulo de Lafuente
# Author: Francisco Angulo de Lafuente
# ORCID: https://orcid.org/0009-0001-1634-7063
# Attribution recorded: 2026-11-05
# SPDX-License-Identifier: MIT

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p state

EXPOSE 8080

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

CMD ["python", "main.py", "run"]
