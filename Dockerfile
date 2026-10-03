FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

RUN python -m pip install --upgrade pip \
    && pip wheel --wheel-dir /wheels ".[postgres]"


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VANTAWAVE_ENV=production \
    VANTAWAVE_HOST=0.0.0.0 \
    VANTAWAVE_PORT=8000 \
    VANTAWAVE_LOG_FORMAT=json

RUN addgroup --system vantawave \
    && adduser --system --ingroup vantawave --home /app vantawave

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-index --find-links=/wheels vantawave-ml psycopg

COPY alembic.ini ./
COPY alembic ./alembic
COPY docs ./docs
COPY scripts ./scripts

RUN mkdir -p /app/artifacts \
    && chown -R vantawave:vantawave /app

USER vantawave

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=3)"

CMD ["python", "-m", "uvicorn", "vantawave.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
