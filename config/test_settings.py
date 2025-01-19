"""Test settings for the project."""

from .settings import *  # noqa: F403, F401

# Completely disable Prometheus
INSTALLED_APPS = [app for app in INSTALLED_APPS if not app.startswith('django_prometheus')]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith('django_prometheus')]  # noqa: F405

# Database settings for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # noqa: F405
        'HOST': os.environ.get('DB_HOST', 'db'),  # noqa: F405
        'PORT': os.environ.get('DB_PORT', '5432'),  # noqa: F405
        'CONN_MAX_AGE': 0,  # disable persistent connections
        'ATOMIC_REQUESTS': False,
        'OPTIONS': {
            'connect_timeout': 5,
            'application_name': 'django_tests',
        },
        'TEST': {
            'NAME': 'test_postgres',
            'SERIALIZE': False,
            'MIRROR': None,
            'DEPENDENCIES': [],
            'CREATE_DB': True,
            'CREATE_USER': False,
            'CHARSET': None,
            'COLLATION': None,
            'PRESERVE_DB': False,
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

# Disable Prometheus completely
DJANGO_PROMETHEUS_EXPORT_DATABASE_METRICS = False
DJANGO_PROMETHEUS_EXPORT_MIGRATIONS_METRICS = False
DJANGO_PROMETHEUS_ENABLE_METRICS = False
PROMETHEUS_METRICS_EXPORT_PORT = None
PROMETHEUS_METRICS_EXPORT_ADDRESS = None

# Use test runner that properly closes connections
TEST_RUNNER = 'config.test_runner.CustomTestRunner'
