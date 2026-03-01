#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════
# entrypoint.sh  —  Railway start command: bash entrypoint.sh
# ══════════════════════════════════════════════════════════════════════════

# Force Python stdout/stderr to be unbuffered so Railway captures every line
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Force the correct settings module — never rely on Railway injecting this
export DJANGO_SETTINGS_MODULE=config.settings.production

echo "========================================"
echo " Weather Platform — Startup"
echo " DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo " PORT: ${PORT:-8000}"
echo "========================================"

# ── Validate required env vars before doing anything ─────────────────────
MISSING=""

if [ -z "$DJANGO_SECRET_KEY" ]; then
    MISSING="$MISSING\n  - DJANGO_SECRET_KEY"
fi
if [ -z "$DATABASE_URL" ]; then
    MISSING="$MISSING\n  - DATABASE_URL  (add a PostgreSQL plugin in Railway)"
fi
if [ -z "$REDIS_URL" ]; then
    MISSING="$MISSING\n  - REDIS_URL     (add a Redis plugin in Railway)"
fi

if [ -n "$MISSING" ]; then
    echo ""
    echo "ERROR: Missing required environment variables:"
    printf "$MISSING\n"
    echo ""
    echo "Go to Railway dashboard → your service → Variables tab and add them."
    exit 1
fi

echo "✓ All required environment variables are present"
echo ""

# ── Django system check ───────────────────────────────────────────────────
echo ">>> Running Django system check..."
python manage.py check --deploy 2>&1
CHECK_EXIT=$?
if [ $CHECK_EXIT -ne 0 ]; then
    echo ""
    echo "ERROR: Django system check failed (exit code $CHECK_EXIT)"
    echo "Fix the errors above, then redeploy."
    exit $CHECK_EXIT
fi
echo "✓ Django check passed"
echo ""

# ── Database migrations ───────────────────────────────────────────────────
echo ">>> Running migrations..."
python manage.py migrate --noinput 2>&1
MIGRATE_EXIT=$?
if [ $MIGRATE_EXIT -ne 0 ]; then
    echo ""
    echo "ERROR: migrate failed (exit code $MIGRATE_EXIT)"
    exit $MIGRATE_EXIT
fi
echo "✓ Migrations complete"
echo ""

# ── Static files ──────────────────────────────────────────────────────────
echo ">>> Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1
echo "✓ Static files collected"
echo ""

# ── Start Gunicorn ────────────────────────────────────────────────────────
echo ">>> Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile "-" \
    --error-logfile "-"