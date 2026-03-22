# Base stage - build dependencies
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN pip install uv && uv pip install --system -t /install -r pyproject.toml


# Runtime stage - hardened image
FROM dhi.io/python:3.13-debian12

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8

WORKDIR /app

USER 65532:65532

# Copy Python dependencies only (no build tools needed at runtime)
COPY --chown=65532:65532 --from=builder /install /opt/python/lib/python3.13/site-packages
COPY --chown=65532:65532 . .

EXPOSE 8001
