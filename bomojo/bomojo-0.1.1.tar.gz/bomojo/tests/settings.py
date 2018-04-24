import os

import dj_database_url

SECRET_KEY = 'test-secret-key'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'movies',
    'matchups',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'bomojo.middleware.JSONMiddleware',
]

ROOT_URLCONF = 'bomojo.urls'

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Additional configuration options

DEFAULT_AVATAR_SIZE = 32
DEFAULT_AVATAR_STYLE = os.getenv('DEFAULT_AVATAR_STYLE', 'retro')
