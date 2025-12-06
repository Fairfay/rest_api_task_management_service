import os
import structlog
import logging
from pathlib import Path

from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

INTERNAL_IPS = [
    '0.0.0.0',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'django_structlog',
    'drf_standardized_errors',
    'django.contrib.postgres',
    'django_telegram_logging',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.celery',
    'health_check.contrib.celery_ping',
    'health_check.contrib.redis',

    'identity.apps.IdentityConfig',
    'payouts.apps.PayoutsConfig',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
]

ROOT_URLCONF = 'server.urls'

# default template--------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# стандартная конфигурация без asgi--------------------------------------
WSGI_APPLICATION = 'server.wsgi.application'

# default database--------------------------------------
DATABASES = {
    "default": {
        'ENGINE': config('POSTGRES_ENGINE'),
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT'),
    }
}

# default password validation--------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# datetime server-----------------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

DATETIME_FORMAT = '%Y-%m-%d %H:%M'

USE_I18N = True

USE_TZ = True

# static and media-----------------------------------------------------------

STATIC_URL = 'static/'

STATIC_ROOT = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'identity.User'

# more settings in Debug---------------------------------------------------

if DEBUG is True:
    DRF_STANDARDIZED_ERRORS = {
        "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True
    }

    INSTALLED_APPS += [
        'debug_toolbar',
        'nplusone.ext.django',
    ]

    MIDDLEWARE.insert(0, 'nplusone.ext.django.NPlusOneMiddleware')

    MIDDLEWARE += [
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'query_counter.middleware.DjangoQueryCounterMiddleware',
        'querycount.middleware.QueryCountMiddleware',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.AllowAny',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 100,
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'EXCEPTION_HANDLER': 'drf_standardized_errors.handler.exception_handler',
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.AllowAny',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 100,
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        ),
        'EXCEPTION_HANDLER': 'drf_standardized_errors.handler.exception_handler',
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }

# monitoring dublicate------------------------------------------------------------------------

QUERYCOUNT = {
    'THRESHOLDS': {
        'MEDIUM': 50,
        'HIGH': 200,
        'MIN_TIME_TO_LOG': 0,
        'MIN_QUERY_COUNT_TO_LOG': 0
    },
    'IGNORE_REQUEST_PATTERNS': [],
    'IGNORE_SQL_PATTERNS': [],
    'DISPLAY_DUPLICATES': None,
    'RESPONSE_HEADER': 'X-DjangoQueryCount-Count'
}

NPLUSONE_LOGGER = logging.getLogger('nplusone')
NPLUSONE_LOG_LEVEL = logging.WARN

# logging----------------------------------------------------------------------

TELEGRAM_LOGGING_TOKEN = config('TELEGRAM_BOT_TOKEN')
TELEGRAM_LOGGING_CHAT = config('TELEGRAM_LOGGING_CHAT')
TELEGRAM_LOGGING_EMIT_ON_DEBUG = config('TELEGRAM_LOGGING_EMIT_ON_DEBUG', cast=bool)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_formatter':{
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'json_file': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'logs/json.log',
            'formatter': 'json_formatter',
        },
        'telegram': {
            'level': 'ERROR',
            'class': 'django_telegram_logging.handler.TelegramHandler'
        },
    },
    'loggers': {
        'nplusone': {
            'handlers': ['console'],
            'level': 'WARN',
        },
        'django_structlog': {
            "handlers": ["json_file", 'telegram', 'console'],
            "level": "INFO",
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['console', 'telegram']
        }
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# telegram------------------------------------------------------------------------

TELEGRAM_BOT_NAME = config('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')

# cors------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG
}

if config('USE_HTTPS', cast=bool):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [
        '^health/',
    ]
    SECURE_REDIRECT_EXEMPT += config('SECURE_REDIRECT_EXEMPT', cast=Csv())

# celery------------------------------------------------------------------------
REDIS_URL = config('CELERY_BROKER_URL')
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_BROKER_CONNECTION_RETRY = True
FLOWER_USER = config('FLOWER_USER')
FLOWER_PSW = config('FLOWER_PSW')
FLOWER_BASIC_AUTH = [f"{FLOWER_USER}:{FLOWER_PSW}"]

# redis cache-----------------------------------------------------------------
# лучше подключить rabbitMQ как брокер, а redis для кешей
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': CELERY_BROKER_URL,
    }
}

# swagger, redoc--------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'SERVE_PERMISSIONS': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ],
    'SERVE_AUTHENTICATION': [
        'rest_framework.authentication.BasicAuthentication',
    ],
}
