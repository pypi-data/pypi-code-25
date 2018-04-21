import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO XDG package?
# TODO pkg_resources?
DATA_DIR = os.path.join(os.environ.get(
    'XDG_DATA_HOME',
    os.path.join(
        os.environ['HOME'],
        '.local',
        'share',
    )
), 'packrat')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Doesn't matter; not actually used in packrat currently.
SECRET_KEY = 'not used'

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
