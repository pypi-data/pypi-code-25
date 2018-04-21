SECRET_KEY = 'fake test key'
INSTALLED_APPS = [
    'packrat',
    'packrat.tests',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
    }
}
