"""Test settings for the project."""

from .settings import *  # noqa: F403, F401

# Database settings for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD') or os.environ.get('TEST_DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_postgres',
            'SERIALIZE': False,
        },
        'CONN_MAX_AGE': 0,
    }
}

# Use memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configure throttling for tests
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Keep other settings
    'DEFAULT_THROTTLE_CLASSES': [],  # Disable throttling for tests
    'DEFAULT_THROTTLE_RATES': {}
}

# Use fast password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'CRITICAL',
    },
}

# Disable debug mode
DEBUG = False

# Configure templates for testing
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

# Disable CSRF for tests
MIDDLEWARE = [m for m in MIDDLEWARE if 'CSRFMiddleware' not in m]

# Cache settings for testing
CACHE_TTL = 60  # 1 minute for testing
CACHE_MIDDLEWARE_SECONDS = CACHE_TTL

# Test-specific settings
TEST_NON_SERIALIZED_APPS = ["movies", "reviews", "users"]

# Email settings for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# CSRF settings
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
