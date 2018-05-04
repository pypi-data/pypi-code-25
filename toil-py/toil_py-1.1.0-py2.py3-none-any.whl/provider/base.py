# -*- coding: utf-8 -*-
"""
Provides base functionality for providers.
"""
import logging
import abc
import os
import toil.config

logger = logging.getLogger(__name__)


class BaseProvider(object):
    """
    Base class to provide common provider behavior.

    Properties :
      config: dict with configuration data
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, toil, config):
        logger.debug("config={config}".format(config=config))
        self._config = config
        self._toil = toil

    @property
    def toil(self):
        return self._toil

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @abc.abstractmethod
    def session(self, profile='default'):
        """
        Create session.
        All providers must implement this method.

        Args:
          profile (): the profile defined in config to use

        Returns:
          AppRepoSession
        """
        return NotImplemented

    def profiles(self):
        """
        return a list of profiles supported by provider

        Returns: List
        """
        # list comprehension
        return [x for x in self._config.keys() if x not in toil.config.util.COMMON_CONFIG_ITEMS]

    def configure_proxy(self):
        """
        Configure a proxy if necessary by setting environment variables.

        Returns: None
        """
        if 'proxy' in self.config:
            os.environ['http_proxy'] = self.config['proxy']
            os.environ['https_proxy'] = self.config['proxy']
