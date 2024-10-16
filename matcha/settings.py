"""
Django settings for matcha project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import sys
from pathlib import Path

import pytz

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # NOSONAR
IS_PROD = False
WEBHOOK_ENABLED = False
IS_ONLINE = False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STACK_DIR = BASE_DIR.parent.parent
sys.path.append(str(STACK_DIR))

from lib.config import get_config  # noqa
config = get_config(os.path.join(BASE_DIR, 'config.yaml'))

TIMEZONE = pytz.timezone('Europe/Paris')
APPLICATION_NAME = 'matcha'


MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']

if IS_PROD:
    STATIC_ROOT = '/var/www/matcha/website/static'

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

LOG_DIR = os.path.join(BASE_DIR, 'log')
try:
    os.makedirs(LOG_DIR)
except OSError:
    pass

DEFAULT_CACHE_DIR = os.path.join(BASE_DIR, 'cache', 'default')
try:
    os.makedirs(DEFAULT_CACHE_DIR)
except OSError:
    pass

DISKCACHE_DIR = os.path.join(BASE_DIR, 'cache', 'diskcache')
try:
    os.makedirs(DISKCACHE_DIR)
except OSError:
    pass

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(LOG_DIR, 'mails')
try:
    os.makedirs(EMAIL_FILE_PATH)
except OSError:
    pass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'daphne',
    'corsheaders',
    'django_rq',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'wsock',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'matcha.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates", BASE_DIR / "machinery" / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'matcha.asgi.application'

# CACHES
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': DEFAULT_CACHE_DIR,
    },
    'diskcache': {
        'BACKEND': 'diskcache.DjangoCache',
        'LOCATION': DISKCACHE_DIR,
    },
    'djangocache': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
        "TIMEOUT": 60 * 60,
    }
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('db_name') or config.processes.core.backend.settings.db_name,
        'USER': os.getenv('db_user') or config.processes.core.backend.settings.db_user,
        'PASSWORD': os.getenv('db_password') or config.processes.core.backend.settings.db_password,
        'HOST': 'localhost',
        'PORT': ''
    }
}

# Channel layers :

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # "hosts": [("127.0.0.1", 6379)],
            'hosts': ["redis://127.0.0.1:6379/1"]
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = config.common.language_code
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Customatization

LOGIN_REDIRECT_URL = 'login'
LOGOUT_REDIRECT_URL = "core_home"
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

RQ_QUEUES = {
    'default': {
        'HOST': config.common.redis.host or 'localhost',
        'PORT': config.common.redis.port or 6379,
        'DEFAULT_TIMEOUT': config.common.redis.db.timeout or 360,
        'DB': config.common.redis.db.default or 1,
    },
    'populate': {
        'HOST': config.common.redis.host or 'localhost',
        'PORT': config.common.redis.port or 6379,
        'DEFAULT_TIMEOUT': config.common.redis.db.timeout or 360,
        'DB': config.common.redis.db.populate or 2,
    }
}

SCHEDULER_CONFIG = {
    'EXECUTIONS_IN_PAGE': 20,
    'DEFAULT_RESULT_TTL': 500,
    'DEFAULT_TIMEOUT': 300,  # 5 minutes
    'SCHEDULER_INTERVAL': 2,  # 2 seconds
}

SUGGESTION_RECIPIENTS = ['matcha@castoretpollux.com']

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = config.common.cookie_age

DEFAULT_PIPELINE = config.default_pipeline

LOCALE_PATHS = ['locale', 'core/locale', 'lib/locale', 'machinery/locale']

BACKEND_PROTOCOL = os.getenv('protocol') or config.processes.core.backend.settings.protocol
BACKEND_HOSTNAME = os.getenv('hostname') or config.processes.core.backend.settings.hostname
BACKEND_PORT = os.getenv('port') or config.processes.core.backend.settings.port
REPLICATE_API_TOKEN = config.processes.core.backend.settings.replicate_api_token
SEARCHAPP_BACKEND_URL = config.processes.core.search.computed.url
OLLAMA_BACKEND_URL = config.processes.core.backend.computed.ollama_url

# Optionnal URL (<=> depending on processes that have been activated or not)
try:
    SDXL_BACKEND_URL = config.processes.core.stablediffusionxl.computed.url
except AttributeError:
    SDXL_BACKEND_URL = None
try:
    WHISPER_BACKEND_URL = config.processes.contrib.whisper.computed.url
except AttributeError:
    WHISPER_BACKEND_URL = None

SMALL_LLM = config.common.small_llm
TITLE_LLM = config.common.title_llm
BIG_LLM = config.common.big_llm

DATETIME_FORMAT = config.common.datetime_format
SITE_ROOT = f'{BACKEND_PROTOCOL}://{BACKEND_HOSTNAME}:{BACKEND_PORT}'

ALLOWED_HOSTS.append(config.common.hostname)

# REST FRAMEWORK
CSRF_TRUSTED_ORIGINS = [
    SITE_ROOT,
    config.processes.core.frontend.computed.url
]

CORS_ALLOWED_ORIGINS = [
    config.processes.core.frontend.computed.url
]

SECRET_KEY = config.common.django_secret or 'keepyoursecretsecret'


# Allow settings override using a local settings file :

try:
    from .local import *  # noqa  # NOSONAR
except ImportError:
    pass
