# ══════════════════════════════════════════════════════════════════════════
# config/settings/production.py
# ══════════════════════════════════════════════════════════════════════════
import os
import dj_database_url
from .base import *  # noqa

DEBUG = False

# ── SECRET_KEY ────────────────────────────────────────────────────────────
# Use .get() so the error message is clear in Railway logs
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable is not set. "
        "Add it in Railway → your service → Variables tab."
    )

# ── Allowed hosts ─────────────────────────────────────────────────────────
RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
ALLOWED_HOSTS = [h for h in [
    RAILWAY_DOMAIN,
    '.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
] if h]

CSRF_TRUSTED_ORIGINS = [
    f'https://{RAILWAY_DOMAIN}',
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# ── Database ──────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Add a PostgreSQL plugin in Railway — it injects this automatically."
    )

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Redis ─────────────────────────────────────────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# ── Celery ────────────────────────────────────────────────────────────────
CELERY_BROKER_URL        = REDIS_URL
CELERY_RESULT_BACKEND    = REDIS_URL
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'UTC'

# ── Django Channels (WebSockets) ──────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts':    [REDIS_URL],
            'capacity': 1500,
            'expiry':   10,
        },
    }
}

# ── Static files — WhiteNoise ─────────────────────────────────────────────
_base_mw = [m for m in MIDDLEWARE if m not in (  # noqa: F821
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + _base_mw

STATIC_URL  = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # noqa: F821
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # noqa: F821

# ── HTTPS / SSL ───────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS            = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ── API Keys ──────────────────────────────────────────────────────────────
FCM_SERVER_KEY       = os.environ.get('FCM_SERVER_KEY', '')
WEATHER_API_KEY      = os.environ.get('WEATHER_API_KEY', '')
WEATHER_API_BASE_URL = os.environ.get(
    'WEATHER_API_BASE_URL', 'https://api.openweathermap.org/data/2.5'
)

# ── Logging ───────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root':    {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {
            'handlers':  ['console'],
            'level':     os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}