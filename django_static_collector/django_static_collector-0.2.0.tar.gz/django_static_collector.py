# coding: utf-8

from __future__ import print_function

import os
import sys
import importlib
import json

from django.conf import settings
from django.core.management import execute_from_command_line


__version__ = '0.2.0'

# TODO
# - [ ] support OPTIONS as `./manage.py collectstatic [OPTIONS]`


allowed_installed_apps = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

allowed_key_prefixes = [
    'STATIC_',
    'STATICFILES_',
]

KEY_INSTALLED_APPS = 'INSTALLED_APPS'
KEY_APPS_WITH_STATIC = 'APPS_WITH_STATIC'


def main():
    debug = os.environ.get('DEBUG')

    # add cwd to path
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    if debug:
        print('os.getcwd():', cwd)
        print('sys.path:', sys.path)

    app_settings_module = sys.argv[1]
    app_settings = importlib.import_module(app_settings_module)

    config = dict(
        TITLE=getattr(app_settings, 'TITLE', 'default title'),
        DEBUG=True,
        SECRET_KEY='A-random-secret-key!',
    )

    installed_apps = []
    _installed_apps = getattr(app_settings, KEY_INSTALLED_APPS, [])
    for i in _installed_apps:
        if i in allowed_installed_apps:
            installed_apps.append(i)
    for i in getattr(app_settings, KEY_APPS_WITH_STATIC, []):
        if i not in installed_apps:
            installed_apps.append(i)
    config[KEY_INSTALLED_APPS] = installed_apps

    for k in dir(app_settings):
        for prefix in allowed_key_prefixes:
            if not k.startswith(prefix):
                continue
            v = getattr(app_settings, k, None)
            if v is None:
                continue
            config[k] = v

    if debug:
        print('settings: {}'.format(json.dumps(config, indent=2)))
    settings.configure(**config)

    print('\nStart collecting:')
    execute_from_command_line(['manage.py', 'collectstatic', '--no-input'])


if __name__ == '__main__':
    main()
