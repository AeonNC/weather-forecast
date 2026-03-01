import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = [
    os.environ.get("RAILWAY_PUBLIC_DOMAIN", "*"),
    "*.railway.app",
]

# Database — Railway injects DATABASE_URL automatically
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
    )
}

# Redis — for Celery and Channels
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# Static files — WhiteNoise serves them directly from Django
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ... your existing middleware
]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# FCM — store key in Railway env vars
FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY", "")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")