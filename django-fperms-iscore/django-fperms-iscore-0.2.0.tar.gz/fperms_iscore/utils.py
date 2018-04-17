import importlib

from django.apps import apps


CORE_MODULE_NAME = 'cores'


def get_iscore_class_str(cls):
    app_config = apps.get_containing_app_config(cls.__module__)
    core = cls.__name__
    return '{app_label}.{core}'.format(
        app_label=app_config.label,
        core=core,
    )


def get_iscore_class(class_str):
    app_label, core = class_str.rsplit('.', 1)
    core_module_path = '.'.join((app_label, CORE_MODULE_NAME))

    module = importlib.import_module(core_module_path)

    return getattr(module, core)
