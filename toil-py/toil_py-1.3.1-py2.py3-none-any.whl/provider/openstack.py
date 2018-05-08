# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for OPEN_STACK library.
See https://api-explorer.scalr.com/ for API details
"""
from __future__ import absolute_import

import json
import logging
import re

import requests

import toil.provider.base
import toil
import toil.util.decorator

logger = logging.getLogger(__name__)


class OpenStackLib(toil.provider.base.BaseProvider):
    """
    Class for Scalr functionality.

    Properties :
      config: dict with configuration data
    """

    def __init__(self, toil, config):
        super(OpenStackLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create a Scalr session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          ScalrApiSession
        """
        if profile in self.config:
            self.configure_proxy()
            session = OpenStackApiSession(self._toil, profile, self.config[profile])
            return session
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class OpenStackApiSession(requests.Session):
    """
    uses the requests library for an http session
    """

    def __init__(self, toil, profile, config):
        self._profile = profile
        self._config = config
        self._toil = toil
        self._token = None
        self._token_x_subject = None
        self._authenticating = False
        self.URL_AUTH_TOKEN = "{end_point}/auth/tokens".format(end_point=self._config['auth_url'])
        self._services = {}
        super(OpenStackApiSession, self).__init__()
        self.get_auth_token()

    def prepare_request(self, request):
        """
        Ensures the url includes the config api.
        Implements Scalr signing requirements.
        Args:
          request (str):

        Returns: request
        """
        request = super(OpenStackApiSession, self).prepare_request(request)

        if not self._authenticating:
            request.headers.update({
                "X-Auth-Token": self._token_x_subject,
                "Content-Type": 'application/json'
            })

        logger.debug("URL: %s", request.url)

        return request

    def get_auth_token(self):
        """
        get a auth token from openstack
        Args:
          *args ():
          **kwargs ():

        Returns: requests.Response
        """

        self._authenticating = True

        auth_data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": self._config['user_domain'] if 'user_domain' in self._config else self._config[
                                    'domain']
                            },
                            "name": self._config['user'],

                            "password": self._config['password']
                        }
                    }
                },
                "scope": {
                    "project": {
                        "domain": {
                            "name": self._config['domain']
                        },
                        "name": self._config['project'],
                    }
                }
            }
        }

        # profile = prof,
        # user_agent = 'toil',
        # auth_url = self._config['auth_url'],
        # project_name = self._config['project'],
        # project_domain_name = self._config['domain'],
        # user_domain_name = self._config['domain'],
        # username = self._config['user'],
        # password = self._config['password']

        response = self.post(None, self.URL_AUTH_TOKEN, data=json.dumps(auth_data))

        self._authenticating = False

        json_response = response.json()
        self._token = json_response['token']
        self._token_x_subject = response.headers['x-subject-token']

        catalog = json_response['token']['catalog']

        for service in catalog:
            self._services[service['name']] = service

    def get_services(self):
        """
        Returns: Dictionary of services
        """
        return self._services

    # def request(self, *args, **kwargs):
    #   """
    #   request data from scalr, converts response to json
    #   Args:
    #     *args ():
    #     **kwargs ():
    #
    #   Returns: requests.Response
    #   """
    #   res = super(OpenStackApiSession, self).request(*args, **kwargs)
    #   logger.debug("%s - %s", " ".join(args), res.status_code)
    #   try:
    #     errors = res.json().get("errors", None)
    #     if errors is not None:
    #       for error in errors:
    #         logger.warning("API Error (%s): %s", error["code"], error["message"])
    #   except ValueError:
    #     logger.error("Received non-JSON response from API!")
    #   res.raise_for_status()
    #   logger.debug("Received response: %s", res.text)
    #   return res

    def list(self, service_name, url, service_type='public', **kwargs):
        """
        call the service until all data is collected
        Args:
          path (str):
          **kwargs ():

        Returns: List
        """
        data = []
        path = ''
        next_url = url

        body = self.get(service_name, url, service_type, **kwargs).json()
        regex = re.compile('[^a-zA-Z0-9]')

        while body is not None:
            next_url = None
            for body_key in body.keys():
                # looking for a key to match url.  for example: servers in /servers?limit=10
                if body_key in url:
                    page_data = body[body_key]
                    data.extend(page_data)
                elif regex.sub('', body_key) in regex.sub('', url):
                    # nova /v2.0/security-groups returns security_groups as body key
                    page_data = body[body_key]
                    data.extend(page_data)
                elif 'next' in body_key:
                    # looking for a next link, in case all data was not returned
                    # glance uses this style
                    next_url = self.get_service_url(service_name, body['next'], service_type)
                elif 'link' in body_key:
                    # looking for a next link, in case all data was not returned
                    # nova uses this style
                    links = body[body_key]
                    for link in links:
                        if 'rel' in link and link['rel'] == 'next':
                            next_url = link['href']
                            if 'https' not in next_url:
                                next_url = next_url.replace('http', 'https')

            if next_url is not None:
                body = self.get(None, next_url).json()
            else:
                body = None

        return data

    def create(self, service_name, url, service_type='public', **kwargs):
        return self.post(service_name, url, service_type, **kwargs)

    def fetch(self, service_name, url, service_type='public', **kwargs):
        return self.get(service_name, url, service_type, **kwargs)

    def delete(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).delete(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).delete(str(url), **kwargs)

    def post(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).post(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).post(url, **kwargs)

    def put(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).put(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).put(url, **kwargs)

    def patch(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).patch(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).patch(str(url), **kwargs)

    @toil.util.decorator.retry(3, requests.exceptions.RequestException)
    def get(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).get(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).get(str(url), **kwargs)

    @toil.util.decorator.retry(3, requests.exceptions.RequestException)
    def head(self, service_name, url, service_type='public', **kwargs):
        if service_name is not None:
            service_url = self.get_service_url(service_name, url, service_type)
            return super(OpenStackApiSession, self).head(service_url, **kwargs)
        else:
            return super(OpenStackApiSession, self).head(str(url), **kwargs)

    def get_service_url(self, service_name, url, service_type='public'):
        service_endpoint = None

        if service_name not in self._services:
            logger.debug("service '{service_name}' not defined in available services {services}".format(
                service_name=service_name, services=self._services.keys()))
            # raise toil.CloudException("service '{service_name}' not defined in available services {services}".format(service_name=service_name,services=self._services.keys()))
        else:
            for endpoint in self._services[service_name]['endpoints']:
                if endpoint['interface'] == service_type:
                    service_endpoint = endpoint
                    break

        if service_endpoint is not None:
            logger.debug(
                "service:{service_name} service_type:{service_type} url:{url})".format(service_name=service_name,
                                                                                       service_type=service_type,
                                                                                       url=service_endpoint['url']))
            # return service_endpoint['url'] + '/'  + service_name + url
            return service_endpoint['url'] + url
        else:
            logger.debug("service '{service_type} nterface not defined in {service_name}'")
            # raise toil.CloudException( "service '{service_type} nterface not defined in {service_name}'")

            url = "{end_point}{url}".format(end_point=self._config['auth_url'], url=url)
            return url
