"""Configuration des routes VEILLIA : admin, blog, API, SEO."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from veilliablog.sitemaps import sitemaps
from veilliablog.views import PageDetailView, robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    # API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # La veille possède son propre routeur, monté avant l'espace /api/v1/ général.
    path("api/v1/veille/", include("veillia_aggregator.api.urls")),
    path("api/v1/", include("veilliablog.api.urls")),
    # SEO
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    # Veille multi-sources (phase 2) puis blog (racine du site)
    path("", include("veillia_aggregator.urls")),
    path("", include("veilliablog.urls")),
    # Pages CMS à la racine (/a-propos/, /mentions-legales/, …) — en dernier ressort
    path("<slug:slug>/", PageDetailView.as_view(), name="page_root"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
