"""Reads configuration-files."""

import os
import toml
import yaml
import json


class FileHandler(object):
    """Handler for configuration files."""

    def __init__(self):
        self._config_paths = ['.']
        self._config_name = "config"

    def add_config_path(self, path):
        """Adds a path to the list of paths where to search for configuration
        files.

        :param path     str     - relative or absolute path.
        """
        if path not in self._config_paths:
            self._config_paths.append(os.path.abspath(os.path.expanduser(path)))

    def set_config_paths(self, paths):
        """Sets the list of directories to search for configuration files.

        :param paths: list  - ['path_a', 'path_b', ..., 'path_n' ]
        """
        if not isinstance(paths, list) and not isinstance(paths, tuple):
            raise TypeError("must be of type list or tuple")
        self._config_paths = [os.path.abspath(os.path.expanduser(p)) for p in paths]

    def set_config_name(self, name):
        """Sets the basename of the configuration file.

        :param name     str     - basename of configuration file.
        """
        self._config_name = name

    def read_in_config(self):
        """Loads all occurrences of the config file in all configured paths.

        :return     dict    - {'config_key': 'value', ... }
        """
        c = {}
        for path in self._config_paths:
            if os.path.exists(path):
                config_file = os.path.join(path, self._config_name)

                if os.path.exists(config_file + '.toml'):
                    c.update(toml.load(config_file + '.toml'))

                elif os.path.exists(config_file + '.yml'):
                    c.update(yaml.load(open(config_file + '.yml')))

                elif os.path.exists(config_file + '.yaml'):
                    c.update(yaml.load(open(config_file + '.yaml')))

                elif os.path.exists(config_file + '.json'):
                    c.update(json.load(open(config_file + '.json')))

        return c
