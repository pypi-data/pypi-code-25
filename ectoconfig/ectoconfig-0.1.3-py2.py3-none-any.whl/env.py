"""Reads environment variables."""

import os
from . import dotenv


class EnvHandler(object):
    """Handler for environment variables."""

    def __init__(self, prefix='', dot_env_override=False):
        self._prefix = prefix
        self._dot_env_override = dot_env_override

    def set_prefix(self, prefix):
        """Sets the lookup prefix.

        If the prefix is not an emtpy string, only environment variables who's
        names start with the prefix, directly followed by an underscore, will
        be considered by this handler.

        The prefix is automatically lower-cased and appended with an
        underscore.

        :param prefix: str      - the literal variable prefix
                                  (i.e. 'foo' for all 'FOO_' variables)
        """
        self._prefix = prefix

    def set_dot_env_override(self, override):
        """Controls whether or not to allow dot-env files to override
        pre-existing environment variables.

        :param override: bool   - True if dot-env files should overwrite
        """
        if not isinstance(override, bool):
            raise TypeError('must be of type bool')
        self._dot_env_override = override

    def load_dot_env(self):
        """Loads a dot-env file into the environment if found."""

        handler = dotenv.DotEnvHandler()
        config = handler.read_in_config()
        for k in config:
            if k in os.environ and not self._dot_env_override:
                continue
            os.environ[k] = config[k]

    def read_in_config(self):
        """Loads all occurrences of matching env variables."""

        def get_with_prefix(prefix):    # pragma: no cover
            """Gets all variables starting with a prefix.

            The given prefix is automatically upper-cased and appended with an
            underscore.

            :param prefix: str  - literal string prefix.
            """
            c = {}
            prefix = prefix.upper() + '_'
            c.update({
                key[len(prefix):].lower(): value
                for (key, value) in os.environ.items()
                if key.startswith(prefix)
            })
            return c

        def get_without_prefix():   # pragma: no cover
            """Gets all environment variables."""
            c = {}
            c.update({
                key.lower(): value
                for (key, value) in os.environ.items()
            })
            return c

        self.load_dot_env()
        if self._prefix:
            return get_with_prefix(self._prefix)
        else:
            return get_without_prefix()
