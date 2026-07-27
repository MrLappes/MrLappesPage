# PlatePal Recipe Wiki backend image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_PATH=/app/data/recipes.db

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY app ./app

# Run as an unprivileged user. The data dir is owned by that user so a fresh
# named volume mounted here inherits writable ownership.
RUN useradd --system --no-create-home --uid 1001 appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app/data

USER appuser

EXPOSE 8091

# Behind nginx (which sets X-Forwarded-For); a single worker is plenty for the
# admin-only write load and public reads hit SQLite in WAL mode.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8091", "--proxy-headers", "--forwarded-allow-ips", "*"]
