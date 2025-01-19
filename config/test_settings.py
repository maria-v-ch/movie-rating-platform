"""Test settings for the project."""

from .settings import *  # noqa: F403, F401

# Disable Prometheus metrics collection during tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if not app.startswith('django_prometheus')]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith('django_prometheus')]  # noqa: F405

# Database settings for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 0,  # disable persistent connections
        'OPTIONS': {
            'connect_timeout': 5,
        },
    }
}

# Disable any background tasks or async operations during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

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
