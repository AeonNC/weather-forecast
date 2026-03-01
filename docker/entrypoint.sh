#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# entrypoint.sh  —  place at project root, set as Railway start command:
#   bash entrypoint.sh
# ══════════════════════════════════════════════════════════════════════════
set -e

echo "=== Weather Platform — Starting up ==="

# Validate env vars EARLY so Railway logs show the exact problem
if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "ERROR: DJANGO_SECRET_KEY is not set. Add it in Railway → Variables."
    exit 1
fi
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set. Add a PostgreSQL plugin in Railway."
    exit 1
fi

echo ">>> Running migrations..."
python manage.py migrate --noinput

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo ">>> Starting Gunicorn..."
exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -