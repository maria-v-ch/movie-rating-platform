"""Test settings for the project."""

from .settings import *  # noqa: F403, F401

# Disable Prometheus metrics collection during tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if not app.startswith('django_prometheus')]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith('django_prometheus')]  # noqa: F405

# Database settings for tests - using regular PostgreSQL backend instead of Prometheus
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # Regular backend for tests
        "NAME": os.environ.get("DB_NAME", "postgres"),  # noqa: F405
        "USER": os.environ.get("DB_USER", "postgres"),  # noqa: F405
        "PASSWORD": os.environ.get("DB_PASSWORD") or os.environ.get("TEST_DB_PASSWORD"),  # noqa: F405
        "HOST": os.environ.get("DB_HOST", "localhost"),  # noqa: F405
        "PORT": os.environ.get("DB_PORT", "5432"),  # noqa: F405
        "TEST": {
            "NAME": "test_postgres",
            "SERIALIZE": False,
            "CREATE_DB": True,
            "DEPENDENCIES": [],
            "MIRROR": None,
            "CHARSET": "UTF8",
            "TEMPLATE": None,
            "PRESERVE_DB": False,
        },
        "CONN_MAX_AGE": 0,  # Disable persistent connections
        "CONN_HEALTH_CHECKS": False,
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",
        },
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
    }
}

# Use memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Disable debug mode
DEBUG = False

# Use fast password hasher
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# Custom test runner to handle database cleanup
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Disable Prometheus database instrumentation
DJANGO_PROMETHEUS_EXPORT_DATABASE_METRICS = False
DJANGO_PROMETHEUS_EXPORT_MIGRATIONS_METRICS = False
