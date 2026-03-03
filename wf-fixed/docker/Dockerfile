# ══════════════════════════════════════════════════════════════════════════
# docker/Dockerfile
# ══════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# App source
COPY . .

# Collect static at build time (uses dummy vars — not real secrets)
RUN SECRET_KEY=buildtime-placeholder \
    ALLOWED_HOSTS=localhost \
    DEBUG=False \
    REDIS_URL=redis://localhost:6379 \
    python manage.py collectstatic --noinput --settings=config.settings.base

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]