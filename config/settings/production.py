# ══════════════════════════════════════════════════════════════════════════
# config/settings/production.py
# ══════════════════════════════════════════════════════════════════════════
import os
import dj_database_url
from .base import *  # noqa: F401, F403

DEBUG = False

# ── SECRET_KEY ────────────────────────────────────────────────────────────
# Using .get() instead of [] so the error message is clear in Railway logs
# (a bare KeyError gives no context at all)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "CRITICAL: DJANGO_SECRET_KEY env var not set. "
        "Add it in Railway → your service → Variables."
    )

# ── Hosts ─────────────────────────────────────────────────────────────────
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
ALLOWED_HOSTS = [h for h in [
    RAILWAY_DOMAIN,
    ".railway.app",
    ".up.railway.app",
    "localhost",
    "127.0.0.1",
] if h]

CSRF_TRUSTED_ORIGINS = [
    f"https://{RAILWAY_DOMAIN}",
    "https://*.railway.app",
    "https://*.up.railway.app",
]

# ── Database ──────────────────────────────────────────────────────────────
# Railway auto-injects DATABASE_URL when a PostgreSQL plugin is attached
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "CRITICAL: DATABASE_URL env var not set. "
        "Add a PostgreSQL plugin in Railway — it injects this automatically."
    )

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Redis ─────────────────────────────────────────────────────────────────
# Railway auto-injects REDIS_URL when a Redis plugin is attached
REDIS_URL = os.environ.get("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError(
        "CRITICAL: REDIS_URL env var not set. "
        "Add a Redis plugin in Railway — it injects this automatically."
    )

# ── Celery ────────────────────────────────────────────────────────────────
CELERY_BROKER_URL        = REDIS_URL
CELERY_RESULT_BACKEND    = REDIS_URL
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = "UTC"

# ── Django Channels (WebSockets) ──────────────────────────────────────────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts":    [REDIS_URL],
            "capacity": 1500,
            "expiry":   10,
        },
    }
}

# ── Static files — WhiteNoise ─────────────────────────────────────────────
# WhiteNoise must sit directly after SecurityMiddleware
_mw = list(MIDDLEWARE)  # noqa: F405
for _m in ("django.middleware.security.SecurityMiddleware",
           "whitenoise.middleware.WhiteNoiseMiddleware"):
    if _m in _mw:
        _mw.remove(_m)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + _mw

STATIC_URL  = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL  = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405

# ── HTTPS ─────────────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
SECURE_PROXY_SSL_HEADER        = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS            = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── API keys ──────────────────────────────────────────────────────────────
FCM_SERVER_KEY       = os.environ.get("FCM_SERVER_KEY", "")
WEATHER_API_KEY      = os.environ.get("WEATHER_API_KEY", "")
WEATHER_API_BASE_URL = os.environ.get(
    "WEATHER_API_BASE_URL", "https://api.openweathermap.org/data/2.5"
)

# ── Logging — force everything to stdout immediately ──────────────────────
LOGGING = {
    "version":                  1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module}: {message}",
            "style":  "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
            "stream":    "ext://sys.stdout",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django":            {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request":    {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.db.backends":{"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}