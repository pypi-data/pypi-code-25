from abc import abstractmethod

from pubcontrol.config import Config

import pluggy
import importlib
import sys

import pathlib
import logging

PROJECT_NAME = Config().NAME
hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


class PluginManager:

    _instance = None

    def __init__(self):
        if self._instance is None:
            PluginManager.refresh()

    def add_module(self, module_name):
        module = sys.modules[module_name]
        self.add_hookspecs(module)

    def add_class(self, spec_class):
        self.add_hookspecs(spec_class)

    def __getattr__(self, item):
        return getattr(self._instance, item)

    def __setattr__(self, key, value):
        setattr(self._instance, key, value)

    @staticmethod
    def refresh():
        name = Config().NAME
        pm = pluggy.PluginManager(name)
        setattr(PluginManager, '_instance', pm)


class PluginLoaderABC:

    """
    ABSTRACT BASE CLASS
    """
    @property
    @abstractmethod
    def plugin_manager(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def discover(self):
        pass


class SimplePluginLoader(PluginLoaderABC):

    def __init__(self):
        self.plugins = []
        self._loaded = []

        self.config = Config()

        self._pm = pluggy.PluginManager(self.config.NAME)

    @property
    def plugin_manager(self):
        return self._pm

    def load(self):
        for plugin in self.plugins:
            if plugin not in self._loaded:
                self.plugin_manager.register(plugin)
                self._loaded.append(plugin)

    def discover(self):
        pass

    def add(self, plugin):
        self.plugins.append(plugin)


class PluginLoader(PluginLoaderABC):

    def __init__(self):
        self.pm = PluginManager()
        self.logger = logging.getLogger(Config().NAME)
        self.already_added = []

    @property
    def plugin_manager(self):
        return self.pm

    def discover(self):
        """
        CHANGELOG

        Added 10.04.2018
        A method to discover all installed plugins to the pubcontrol system, by looking for modules with the prefix
        'pubcontrol_' in the sys.modules list

        Changed 11.04.2018
        Trying to get the plugins with the sys.modules has not worked because that list only contains modules that are
        already loaded, but the trick with the plugin discovery is that we need a tool for those modules we cannot load
        manually.
        Looping through all directories in the python path now and if one contains a package prefixed with puncontrol
        it will be imported

        :return:
        """
        for path in sys.path:
            path = pathlib.Path(path)
            for file in path.glob('*'):
                if 'pubcontrol_' in file.name and file.name not in self.already_added:
                    self.logger.info('[Plugin] Adding {} to the plugins'.format(file.name))
                    # The parent package needs to be imported first, before importing a child module
                    importlib.import_module(file.name)
                    module = importlib.import_module('.main', file.name)
                    self.plugin_manager.register(module.Plugin())

                    self.already_added.append(file.name)

    def load(self):
        self.discover()
