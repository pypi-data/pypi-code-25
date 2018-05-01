import glob
from abc import ABCMeta
from importlib import import_module
from inspect import isclass
from os.path import basename, dirname, isfile


class SiteBase(object):
    DRIVER_PKG = None
    BASE_CLASS = None

    def __init__(self, cache_cls=False):
        self.CACHE = {}
        self.cache_cls = cache_cls

    def all_driver_class(self):
        driver_paths = dirname(self.DRIVER_PKG.__file__) + '/*.py'
        modules = glob.glob(driver_paths)

        output = set()

        for module_path in modules:
            filename = basename(module_path)

            if filename.startswith("_") or not filename.endswith(".py") or not isfile(module_path):
                continue

            module_name = filename.split('.')[0]

            module = import_module('.' + module_name, self.DRIVER_PKG.__name__)

            for k in dir(module):
                if k.startswith('_'):
                    continue

                cls = getattr(module, k)

                if cls is self.BASE_CLASS:
                    continue

                if isclass(cls) and issubclass(cls, self.BASE_CLASS):
                    output.add(cls)

        return output

    def register(self):
        for cls in self.all_driver_class():
            assert cls.get_name() not in self.CACHE, "class name duplicate! %s, %s" % (cls, self.CACHE[cls.get_name()])

            # TODO: Add cache_cls mode
            if self.cache_cls:
                self.CACHE[cls.get_name()] = cls
            else:
                self.CACHE[cls.get_name()] = cls()

        print self.CACHE

    def get_driver_by_name(self, name):
        return self.CACHE[name]

    def get_match_driver(self, crit):
        output = []

        for driver in self.all_drivers():
            if driver.match(crit):
                return driver

    def all_drivers(self):
        return self.CACHE.values()

    def all_driver_names(self):
        return self.CACHE.keys()
