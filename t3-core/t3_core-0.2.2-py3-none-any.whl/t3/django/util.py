import sys
from os import environ, path
from functools import lru_cache


@lru_cache()
def get_base_dir():
    """
    Use DJANGO_SETTINGS_MODULE to determine where the root project lives
    This is used by Django's core code & is set in both manage.py & wsgi.py
    """
    _settings_module = environ.get('DJANGO_SETTINGS_MODULE', 'project.settings')
    _settings_file = sys.modules[_settings_module].__file__
    return path.dirname(path.dirname(path.abspath(_settings_file)))
