#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created by Marsel Tzatzo on 04/12/2017.
"""
import logging

from requests import RequestException, request

from .models import NetworkError

logger = logging.getLogger(__name__)

class NetworkManagerException(Exception):
    def __init__(self, network_error):
        self.network_error = network_error


class NetworkManager(object):
    def __init__(self,
                 endpoint=None,
                 headers=None,
                 retries=None,
                 timeout=5):
        self.endpoint = endpoint
        self.headers = headers
        self.retries = retries or 3
        self.timeout = timeout

    @classmethod
    def ping(self, url, timeout=10):
        try:
            request('GET', url, timeout=timeout)
        except RequestException:
            return False
        return True

    @property
    def enabled(self):
        return not self.endpoint == None

    def bulk_post(self, listings):
        method = 'POST'
        network_errors = {}
        for listing in listings:
            try:
                self._request(method, self.endpoint, headers=self.headers, json=listing.data)
            except NetworkManagerException as ex:
                network_errors[listing.dasUniqueId] = ex.network_error
        return network_errors

    def bulk_delete(self, listings):
        """
        :param keys:        List of integers to delete.
        :return:            List of errors that occurred.
        """
        method = 'delete'
        network_errors = {}
        for listing in listings:
            url = "{0}{1}/".format(self.endpoint, listing.dasUniqueId)
            try:
                self._request(method, url, headers=self.headers)
            except NetworkManagerException as ex:
                network_errors[listing.dasUniqueId] = ex.network_error
        return network_errors

    def _request(self, method, url, headers, json=None):
        retries_count = 0
        while True:
            try:
                response = request(method, url, headers=headers, json=json)
                if response.status_code >= 400:
                    raise RequestException()
                break
            except RequestException:
                retries_count += 1
                if retries_count == self.retries:
                    network_error = NetworkError.factory(url=url, method=method, headers=headers, body=json)
                    raise NetworkManagerException(network_error)
