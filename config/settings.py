"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ

# Initialize environ
env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [host.strip() for host in env.str("ALLOWED_HOSTS", default="localhost").split(",")]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",
    "django_filters",
    "django_prometheus",
    # Local apps
    "movies.apps.MoviesConfig",
    "users.apps.UsersConfig",
    "reviews.apps.ReviewsConfig",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# Using Prometheus-instrumented database backend for metrics collection
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": env("DB_NAME", default="movie_rating_db"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="db"),  # Using 'db' as default for Docker
        "PORT": env("DB_PORT", default="5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Security settings
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access to CSRF cookie
CSRF_USE_SESSIONS = False  # Store CSRF token in cookie instead of session
CSRF_COOKIE_SAMESITE = "Lax"  # Less strict SameSite policy
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
] + env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Update CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development


# Session Settings
SESSION_COOKIE_SECURE = not DEBUG  # Only use HTTPS in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"  # Less strict in development
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# HTML sanitization
BLEACH_ALLOWED_TAGS = ["p", "b", "i", "u", "em", "strong", "a"]
BLEACH_ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}
BLEACH_STRIP_TAGS = True

# CORS settings
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
#     "https://paragoni.space",
# ] + env.list('CORS_ALLOWED_ORIGINS', default=[])

# JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

AUTH_USER_MODEL = "users.User"

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "movies": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "reviews": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "users": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",  # Use service name from docker-compose
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Cache timeout settings
CACHE_TTL = 60 * 15  # 15 minutes
CACHE_MIDDLEWARE_SECONDS = CACHE_TTL

# Cache timeout for popular movies (12 hours)
POPULAR_MOVIES_CACHE_TIMEOUT = 60 * 60 * 12

# XSS Protection
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
