# syntax=docker/dockerfile:1

FROM python:3.10-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src/requirements.txt /build/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /build/requirements.txt


FROM python:3.10-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

RUN groupadd --system app && \
    useradd --system --gid app --home-dir /app app && \
    mkdir -p /app/reports/screenshots && \
    chown -R app:app /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app src/ /app/src/
COPY --chown=app:app data/schemas/feature_schema.json /app/data/schemas/feature_schema.json
COPY --chown=app:app tests/ /app/tests/

USER app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)" || exit 1


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "--worker-tmp-dir", "/tmp", "--no-control-socket", "src.app:app"]
