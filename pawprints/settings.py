"""
Django settings for pawprints project.
"""
import os
import datetime
import channels.apps  # Don't remove this, it prevents a warning about Twisted
import raven
import json
import yaml
from huey import RedisHuey

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
SAML_FOLDER = os.path.join(BASE_DIR, 'saml')
CONFIG = {}

with open(os.path.join(BASE_DIR, 'config.yml')) as config:
    CONFIG = yaml.safe_load(config)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ["*"]
if 'TRAVIS' in os.environ:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]

if os.environ.get('SERVER_ENV', 'none') == 'test':
    DEBUG = True

if os.environ.get('SERVER_ENV', 'none') == 'prod':
    DEBUG = False
    ALLOWED_HOSTS = ["*"]

if os.environ.get('SERVER_ENV', 'none') == 'stage':
    DEBUG = False
    ALLOWED_HOSTS = ["sgstage.rit.edu"]


# Sentry Settings
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN', ''),
    'release': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

# Application definition

INSTALLED_APPS = [
    'channels',
    'raven.contrib.django.raven_compat',
    'profile.apps.ProfileConfig',
    'petitions.apps.PetitionsConfig',
    'send_mail.apps.SendMailConfig',
    'huey.contrib.djhuey',
    'django.contrib.auth',
    'django.contrib.postgres',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'compressor',
]

ALWAYS_EAGER = DEBUG
if os.environ.get('SERVER_ENV', 'none') == 'local':
    DEBUG = True
    ALWAYS_EAGER = False

# Settings for Huey task queue https://huey.readthedocs.io/en/latest/contrib.html#django


class PawPrintsRedisHuey(RedisHuey):
    def _get_task_metadata(self, task, error=False, include_data=False):  # Store job info
        return super(PawPrintsRedisHuey, self)._get_task_metadata(task, error, include_data=error)


HUEY = {
    'name': 'pawprints',  # Use db name for huey.
    'result_store': False,  # Do not store return values of tasks.
    'events': True,  # Consumer emits events allowing real-time monitoring.
    'store_none': False,  # If a task returns None, do not save to results.
    'always_eager': ALWAYS_EAGER,  # If DEBUG=True, run synchronously.
    'store_errors': True,  # Store error info if task throws exception.
    'blocking': False,  # Poll the queue rather than do blocking pop.
    'backend_class': 'pawprints.settings.PawPrintsRedisHuey',
    'connection': {
        'connection_pool': None,  # Definitely you should use pooling!
        # ... tons of other options, see redis-py for details.
        # Allow Redis config via a DSN.
        'url': os.environ.get('REDIS_URL', 'redis://redis:6379'),
    },
    'consumer': {
        'workers': 2,
        'worker_type': 'thread',
        'initial_delay': 0.1,  # Smallest polling interval, same as -d.
        'utc': True,  # Treat ETAs and schedules as UTC datetimes.
        'periodic': False,
        'scheduler_interval': 1,  # Check schedule every second, -s.
        'check_worker_health': True,  # Enable worker health checks.
        'health_check_interval': 1,  # Check worker health every second.
    },
}

AUTHENTICATION_BACKENDS = ['auth.auth_backend.SAMLSPBackend']

ASGI_APPLICATION = 'pawprints.routing.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379')],
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'log.ip_log_middleware.IPLogMiddleware',
]

ROOT_URLCONF = 'pawprints.urls'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pawprints/templates'), os.path.join(BASE_DIR, 'petitions/static'), os.path.join(BASE_DIR, "profile/static")],
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

#STATICFILES_DIRS = [STATIC_DIR, ]
WSGI_APPLICATION = 'pawprints.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Email settings

EMAIL_EMAIL_ADDR = os.environ.get('EMAIL_EMAIL_ADDR', '')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '')

STATIC_URL = '/static/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s : %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'verbose',
        },
        'rotate_file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/error.log'),
            'formatter': 'verbose',
            'maxBytes': 90000000,
            'backupCount': 10,
            'encoding': 'utf8'
        },
        'rotate_file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/info.log'),
            'formatter': 'verbose',
            'maxBytes': 90000000,
            'backupCount': 10,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        'pawprints': {
            'handlers': ['rotate_file_errors', 'sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['rotate_file_errors', 'sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'IPRequest': {
            'handlers': ['rotate_file_info'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

ANALYTICS = os.environ.get('GOOGLE_ID', '')

# Asset compression settings
COMPRESS_ENABLED = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    # css minimizer
    'compressor.filters.cssmin.CSSMinFilter'
]

# Secure configs
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
