#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import base64

class ServerConfig:
    """
    This class represent the configuration used to communicate with your HostMyDocs server
    """

    def __init__(self, address: str, api_login: str, api_password: str, use_tls=True, port=443):
        """

        :param address: The url (or IP) of the targeted HostMyDocs server
        :param port: The port on the targeted HostMyDocs server
        :param api_login: The login for HostMyDocs REST API
        :param api_password: The password for HostMyDocs REST API
        :param use_tls: If true will use HTTPS protocol, else will use HTTP
        """
        self.port = port
        self.use_tls = use_tls
        self.api_password = api_password
        self.api_login = api_login
        self.address = address

    def get_server_url(self) -> str:
        """

        :return: The complete server URl use to call the HostMyDocsApi
        """
        return "{protocol}://{address}:{port}".format(
            protocol="https" if self.use_tls else "http",
            address=self.address,
            port=self.port
        )

    def get_credential_for_basic_auth(self) -> str:
        """

        :return: The credentials encoded for the basic authentication method
        """
        return base64.b64encode("{}:{}".format(self.api_login, self.api_password).encode()).decode()

