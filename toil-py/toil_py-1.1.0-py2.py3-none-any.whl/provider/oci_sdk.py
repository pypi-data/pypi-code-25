# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for OCI library.
See https://pypi.python.org/pypi/openstacksdk for API details

"""
from __future__ import absolute_import

import logging

import oci

import toil.provider.base
from toil.framework import CloudException

logger = logging.getLogger(__name__)


class OciSdkLib(toil.provider.base.BaseProvider):
    """
    library for OCI functionality.
    """

    def __init__(self, toil, config):
        super(OciSdkLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create an OCI session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          3.session.Session
        """
        if profile in self.config:
            self.configure_proxy()
            # create a session
            return OciSession(self._toil, profile, self.config[profile])
        else:
            raise CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class OciSession(object):
    """
    provide open stack api access
    """

    def __init__(self, toil, profile, config):
        self._profile = profile
        self._config = config
        self._toil = toil

    def oci_config(self):

        config = {
            "user": self._config["user_ocid"],
            "key_file": self._config["key_file"],
            "fingerprint": self._config["fingerprint"],
            "tenancy": self._config["tenancy"],
            "region": self._config["region"],
            "log_requests": True
        }

        from oci.config import validate_config
        validate_config(config)

        return config

    def config(self):
        return self._config

    def paginate(self, operation, *args, **kwargs):
        while True:
            response = operation(*args, **kwargs)
            for value in response.data:
                yield value
            kwargs["page"] = response.next_page
            if not response.has_next_page:
                break

    def client(self, service):
        if service == "compute":
            return oci.core.compute_client.ComputeClient(self.oci_config())
        elif service == "identity":
            return oci.identity.identity_client.IdentityClient(self.oci_config())
        else:
            raise CloudException(
                "client '{service}' not supported".format(service=service))
