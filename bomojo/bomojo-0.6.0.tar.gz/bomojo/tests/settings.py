import dj_database_url

SECRET_KEY = 'test-secret-key'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'bomojo.movies',
    'bomojo.matchups',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'bomojo.middleware.JSONMiddleware',
]

# Tests extend the default URL config to expose a login endpoint.
ROOT_URLCONF = 'bomojo.tests.urls'

# This is necessary to support testing views that require authentication.
LOGIN_URL = '/login/'

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres@127.0.0.1:5432/bomojo_test')
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
