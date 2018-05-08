# -*- coding: utf-6 -*-
"""
Example custom service
"""
import logging
import toil.util.decorator
import toil.provider.base
import toil

logger = logging.getLogger(__name__)


class ExampleLib(toil.provider.base.BaseProvider):
    """
    Class example

    Properties :
      config: dict with configuration data
    """

    def __init__(self, toil, config):
        super(ExampleLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create session.

        Args:
          profile (str): the profile defined in config to use

        Returns:
          Session
        """
        if profile in self.config:
            self.configure_proxy()
            session = ExampleSession(self,
                                     api_url=self.config[profile]['api_url'],
                                     api_key_id=self.config[profile]['api_key_id'],
                                     api_key_secret=self.config[profile]['api_key_secret']
                                     )
            return session
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class ExampleSession(object):
    """
    example
    """

    def __init__(self, client, api_url, api_key_id, api_key_secret):
        self.client = client
        self.api_url = api_url
        self.api_key_id = api_key_id
        self.api_key_secret = api_key_secret
        super(ExampleSession, self).__init__()

    def list(self, path, **kwargs):
        return []

    def create(self, *args, **kwargs):
        return {}

    def fetch(self, *args, **kwargs):
        return {}

    def delete(self, *args, **kwargs):
        return {}

    def post(self, *args, **kwargs):
        return {}

    @toil.util.decorator.retry(3, Exception)
    def get(self, url, **kwargs):
        return {}
