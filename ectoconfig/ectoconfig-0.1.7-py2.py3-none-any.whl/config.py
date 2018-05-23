"""Main Handler."""

from . import file, env

# HANDLER_ORDER controls which handlers get called in what order.
HANDLER_ORDER = ['file', 'env']


class Config(object):
    """Manager and entry-point class."""

    def __init__(self, name, **defaults):
        """
        :param name:        str     - the name of the app
        :param defaults:    dict    - defaults as dict
        """
        self._config = defaults
        self._handlers = {
            'file': file.FileHandler(),
            'env': env.EnvHandler(prefix=name),
        }

    def handler(self, name):
        return self._handlers[name]

    def add_config_path(self, path):
        """Adds a path to the list of directories ectoconfig searches for
        configuration files.

        :param path: str    - relative or absolute path to add
        """
        self.handler('file').add_config_path(path)

    def set_config_name(self, name):
        """Sets the basename of the configuration file.

        :param name:    str     - basename of the configuration file
        """
        self.handler('file').set_config_name(name)

    def set_env_prefix(self, prefix):
        """Sets a prefix for all environment variables to be considered as
        config.

        :param prefix:  str     - literal string prefix
                                  (i.e.: 'foo' for all 'FOO_' variables)
        """
        self.handler('env').set_prefix(prefix)

    def read_in_config(self):
        """Reads the configuration from all handlers.

        :returns dict
        """
        config = self._config.copy()
        for handler in HANDLER_ORDER:
            config.update(self._handlers[handler].read_in_config())
        return config
