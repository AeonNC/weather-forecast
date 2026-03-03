
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse


def health_check(request):
    """
    Minimal health check — no DB, no auth, no middleware dependencies.
    Railway probes this every few seconds during startup.
    Must return 200 or the deployment is killed.
    """
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    # ← MUST be first — Railway hits this before anything else is warm
    path("health/", health_check),

    path("admin/",         admin.site.urls),
    path("api/auth/",      include("apps.users.urls")),
    path("api/weather/",   include("apps.weather.urls")),
    path("api/locations/", include("apps.locations.urls")),
]

# Rosetta only in DEBUG to avoid production import errors
if settings.DEBUG:
    try:
        urlpatterns += [path("rosetta/", include("rosetta.urls"))]
    except ImportError:
        pass

# Internationalised frontend routes
urlpatterns += i18n_patterns(
    path("", include("apps.weather.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)