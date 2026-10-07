"""
VEILLIA - configuration globale.

Stratégie d'environnement:
  * developpement local : SQLite (aucun service externe requis)
  * production         : PostgreSQL 16 (+ pgvector en phase 2)

Bascule Postgres en definissant dans le fichier .env :
    DB_ENGINE=postgres
    DB_NAME=veillia  DB_USER=veillia  DB_PASSWORD=...
    DB_HOST=localhost  DB_PORT=5432
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-change-me-in-production-veillia",
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

# Applications installées

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Bibliothèques tierces
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    # Applications internes
    "core",
    "veilliablog",
    "veillia_aggregator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.PermanentRedirectMiddleware",
    "core.middleware.RequestTimingMiddleware",
]

if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de données

if os.environ.get("DB_ENGINE", "sqlite").lower() in {"postgres", "postgresql", "postgre"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "veillia"),
            "USER": os.environ.get("DB_USER", "veillia"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
            "OPTIONS": {"options": "-c search_path=public"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Validation des mots de passe

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Langue et fuseaux horaires

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Fichiers statiques et média

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Comptes

AUTH_USER_MODEL = "core.User"
LOGIN_URL = "veilliablog:login"
LOGIN_REDIRECT_URL = "veilliablog:home"
LOGOUT_REDIRECT_URL = "veilliablog:home"

SITE_ID = 1

# Identité du site

VEILLIA_NAME = os.environ.get("VEILLIA_NAME", "VEILLIA")
VEILLIA_TAGLINE = os.environ.get(
    "VEILLIA_TAGLINE", "Veille intelligente Data Science & Intelligence Artificielle"
)
VEILLIA_CONTACT_EMAIL = os.environ.get("VEILLIA_CONTACT_EMAIL", "contact@veillia.local")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "VEILLIA <no-reply@veillia.local>")

# Réglages métiers du blog

BLOG_POSTS_PER_PAGE = int(os.environ.get("BLOG_POSTS_PER_PAGE", "9"))
BLOG_RELATED_POSTS = 4
BLOG_SUMMARY_MAX_CHARS = 260
BLOG_NEWSLETTER_ENABLED = env_bool("BLOG_NEWSLETTER_ENABLED", True)

# Veille multi-sources (phase 2)

AGGREGATOR_ITEMS_PER_PAGE = int(os.environ.get("AGGREGATOR_ITEMS_PER_PAGE", "18"))
AGGREGATOR_USER_AGENT = os.environ.get(
    "AGGREGATOR_USER_AGENT",
    f"VeilliaBot/1.0 (+mailto:{VEILLIA_CONTACT_EMAIL})",
)
AGGREGATOR_TIMEOUT_SECONDS = int(os.environ.get("AGGREGATOR_TIMEOUT_SECONDS", "20"))

# Cache (recherche, pages chaudes)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "veillia-cache",
    }
}

# Django REST Framework

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("API_THROTTLE_ANON", "60/minute"),
        "user": os.environ.get("API_THROTTLE_USER", "240/minute"),
    },
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# Le throttle est inutile (voire contre-productif) pendant les tests.
if "test" in sys.argv:
    REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

SPECTACULAR_SETTINGS = {
    "TITLE": "VEILLIA API",
    "DESCRIPTION": "API du blog et de la veille Data Science / IA - phase 1 (CMS veilliablog).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Sécurité (production)

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"

# Journalisation

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {"level": "INFO", "propagate": True},
        "veilliablog": {"level": "DEBUG" if DEBUG else "INFO", "propagate": True},
    },
}
