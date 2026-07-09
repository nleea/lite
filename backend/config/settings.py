"""Django settings for the Lite Thinking backend.

Django is the token *issuer*: it signs JWTs with the shared HS256 key that the
FastAPI services validate. Passwords are hashed with Argon2.
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _env_list(key: str, default: str = "") -> list[str]:
    return [item.strip() for item in _env(key, default).split(",") if item.strip()]


SECRET_KEY = _env("DJANGO_SECRET_KEY", "insecure-dev-key")
DEBUG = _env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "rest_framework",
    "corsheaders",
    # local
    "apps.accounts",
    "apps.companies",
    "apps.products",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ── Database ──────────────────────────────────────────────────────────────
# Uses PostgreSQL when POSTGRES_HOST is set, otherwise SQLite for local dev.
if _env("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _env("POSTGRES_DB", "lite"),
            "USER": _env("POSTGRES_USER", "lite"),
            "PASSWORD": _env("POSTGRES_PASSWORD", "lite"),
            "HOST": _env("POSTGRES_HOST", "localhost"),
            "PORT": _env("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Auth ──────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

# Argon2 first: passwords are stored as Argon2 hashes (requirement f).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

# ── JWT (shared with FastAPI) ─────────────────────────────────────────────
# The SIGNING_KEY here is the SAME key FastAPI uses to validate. HS256.
SIMPLE_JWT = {
    "ALGORITHM": _env("JWT_ALGORITHM", "HS256"),
    "SIGNING_KEY": _env("JWT_SIGNING_KEY", SECRET_KEY),
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(_env("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "60"))
    ),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "sub",
    "TOKEN_TYPE_CLAIM": "token_type",
}

# ── Event broker (Redis Streams) ──────────────────────────────────────────
REDIS_HOST = _env("REDIS_HOST", "localhost")
REDIS_PORT = int(_env("REDIS_PORT", "6379"))
PRODUCT_EVENTS_STREAM = _env("PRODUCT_EVENTS_STREAM", "product-events")

# ── CORS (frontend) ───────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = DEBUG

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
