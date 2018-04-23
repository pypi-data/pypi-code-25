from __future__ import absolute_import, print_function, unicode_literals

import functools
from django.apps import apps
from django.utils import module_loading, six


def autodiscover(*args):
    module_loading.autodiscover_modules('handlers', *args)


class Handler(object):

    _handler = None

    def __init__(self, func):
        functools.wraps(func)(self)
        self._handler = func

    def __call__(self, *args, **kwargs):
        return self._handler(*args, **kwargs)

    def connect(self, signal, **kwargs):
        sender = kwargs.pop('sender', None)
        if isinstance(sender, six.string_types):
            sender = apps.get_model(sender)
        signal.connect(self._handler, sender=sender, **kwargs)

    def disconnect(self, signal, **kwargs):
        # https://docs.djangoproject.com/en/2.0/topics/signals/#disconnecting-signals
        sender = kwargs.pop('sender', None)
        if isinstance(sender, six.string_types):
            sender = apps.get_model(sender)
        return signal.disconnect(self._handler, sender=sender, **kwargs)


def handler(*args, **kwargs):
    if len(args) == 1 and callable(args[0]):
        return Handler(args[0])

    def decorator(func):
        wrapped = Handler(func)
        wrapped.connect(*args, **kwargs)
        return wrapped

    return decorator
