# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for Chef library.
See https://docs.chef.io/chef_search.html for search details
"""
from __future__ import absolute_import
import logging
import toil.provider.base
import toil

logger = logging.getLogger(__name__)


class ChefLib(toil.provider.base.BaseProvider):
    """
    library for Chef functionality.

    Properties :
      config: dict with configuration data
    """

    def __init__(self, toil, config):
        super(ChefLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create a Chef session.

        Args:
          profile (str): profile defined in config to use

        Returns:
          ChefSession
        """

        if profile in self.config:
            self.configure_proxy()
            session = ChefSession(self._toil, profile, self.config[profile])
            return session
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class ChefSession(object):
    """
    provide chef api access
    """

    def __init__(self, toil, profile, config):
        self._config = config
        self._toil = toil
        self._api = self.__chef_api()

    def __chef_api(self, **kwargs):
        """
        Create a client api.

        Returns:
          A low-level client representing an CHEF service.
        """
        return ChefAPI(self._config['chef_server_url'], self._config['client_key'], self._config['user'],
                       version='0.10.8', headers={}, ssl_verify=self._config['ssl_verify'])

    def search(self, index, search_context='', **kwargs):
        """
        https://docs.chef.io/chef_search.html
        Args:
            index: chef index (client, DATA_BAG_NAME, environment, node, role)
            search_context: search pattern
            **kwargs:

        Returns:

        """
        return Search(index, search_context, api=self._api, **kwargs)

    def organizations(self):
        response = self._api.api_request("GET", "/organizations")
        return response

    def users(self):
        response = self._api.api_request("GET", "/users")
        return response

    def user(self, user_id):
        response = self._api.api_request("GET", "/users/{user}".format(user=user_id))
        return response

    def cookbooks(self):
        response = self._api.api_request("GET", "/cookbooks")
        return response

    def cookbook(self, cookbook, version=None):
        if version is not None:
            response = self._api.api_request("GET", "/cookbooks/{cookbook}/{version}".format(cookbook=cookbook,
                                                                                             version=version))
        else:
            response = self._api.api_request("GET", "/cookbooks/{cookbook}".format(cookbook=cookbook))
        return response
