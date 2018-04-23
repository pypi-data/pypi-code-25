from __future__ import absolute_import, print_function, unicode_literals

from django.apps import AppConfig
from roadies import handlers


class MyAppConfig(AppConfig):

    name = 'tests.myapp'

    def ready(self):
        handlers.autodiscover()
