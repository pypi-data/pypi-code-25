import re
import sys
import six
import pkgutil
import traceback
import importlib
from .__version__ import __version__


def list_modules(package):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        yield importlib.import_module('.' + modname, package.__name__)


def get_last_name(mod):
    name = mod.__name__.split('.')[-1]
    if name.endswith('_pb2'):
        name = re.sub('_pb2$', '', name)
    return name


try:
    from . import pb

    _self = sys.modules[__name__]
    for module in list_modules(pb):
        name = get_last_name(module)
        setattr(_self, name, module)
        if not hasattr(pb, name):
            setattr(pb, name, module)
        full_name = '.'.join([__name__, name])
        if full_name in sys.modules:
            raise KeyError('Module "{0}" is already set'.format(full_name))
        sys.modules[full_name] = module

except Exception:
    traceback.print_exc()
    raise
