import os

# TODO XDG
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get('HOME')
if DATA_DIR:
    DATA_DIR = os.path.join(DATA_DIR, '.local', 'share', 'packrat')
else:
    DATA_DIR = BASE_DIR

# Doesn't matter; not actually used in packrat currently.
SECRET_KEY = 'w*02qouy7)(wsjoclx=lzs(ip*ca-r#t796t#er1m9b-&y+88*'

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
]

INSTALLED_APPS = [
    'packrat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'packrat.urls'

WSGI_APPLICATION = 'packrat.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'zxx'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True
