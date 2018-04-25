import importlib


CORE_MODULE_NAME = 'cores'


def get_iscore_class_str(cls):
    path, _ = cls.__module__.rsplit('.{}'.format(CORE_MODULE_NAME), 1)
    core = cls.__name__
    return '{path}.{core}'.format(
        path=path,
        core=core,
    )


def get_iscore_class(class_str):
    app_label, core = class_str.rsplit('.', 1)
    core_module_path = '.'.join((app_label, CORE_MODULE_NAME))

    module = importlib.import_module(core_module_path)

    return getattr(module, core)
