# This file is inspired by django-aullauth and derives substantially from it:
# https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/providers/__init__.py
from django.conf import settings
import importlib
from collections import OrderedDict


class ExchangeRegistry(object):

    def __init__(self):
        self.provider_map = OrderedDict()
        self.loaded = False

    def get_list(self):
        self.load()
        return [provider_cls for provider_cls in self.provider_map.values()]

    def register(self, cls):
        self.provider_map[cls.id] = cls

    def get_by_id(self, id):
        self.load()
        return self.provider_map[id]

    def as_choices(self):
        self.load()
        for provider_cls in self.provider_map.values():
            yield (provider_cls.id, provider_cls.name)

    def load(self):
        if not self.loaded:
            for app in settings.INSTALLED_APPS:
                try:
                    provider_module = importlib.import_module(
                        app + '.provider'
                    )
                except ImportError:
                    pass
                else:
                    for cls in getattr(
                        provider_module, 'providers', []
                    ):
                        self.register(cls)
            self.loaded = True


registry = ExchangeRegistry()
