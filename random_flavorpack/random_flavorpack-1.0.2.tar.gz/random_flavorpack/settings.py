'''
    Copyright 2018 SerialLab, CORP

    This file is part of RandomFlavorpack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l$+#s2al#vz27ai)q4of)#$oni9&lk&)=0%tnh_5donkkzddnm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'serialbox',
    'rest_framework',
    'random_flavorpack',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            #             os.path.join(os.path.dirname(__file__),
            #                          'serialbox/templates')
        ],
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
WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Or path to database file if using sqlite3.
        'NAME': os.environ.get('SERIALBOX_DB'),
        'USER': os.environ.get('SERIALBOX_USER'),
        'PASSWORD': os.environ.get('SERIALBOX_PASSWORD'),
        # Empty for localhost through domain sockets or           '127.0.0.1'
        # for localhost through TCP.
        'HOST': os.environ.get('SERIALBOX_DB_HOST', 'localhost'),
        # Set to empty string for default.
        'PORT': os.environ.get('SERIALBOX_DB_PORT', '5432'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = '/static/'

LOGGING_CONFIG = None

# import the django rest framework settings
from serialbox.serialbox_settings import REST_FRAMEWORK

