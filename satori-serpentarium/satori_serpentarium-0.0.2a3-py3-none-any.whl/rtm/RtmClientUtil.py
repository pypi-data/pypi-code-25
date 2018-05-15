import logging
import threading
import time
from typing import List

from retrying import retry
from satori.rtm import auth
from satori.rtm.client import Client

from serpentarium.logging.LoggingUtil import LoggingUtil


class RtmClientUtil:
    """
    Encapsulates creation and destruction of RTM clients
    """
    clients: List[Client] = []

    logger = LoggingUtil.get_logger("RTM util logger")

    @classmethod
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def get_client(cls, creds: dict) -> Client:
        """
        Creates a new client
        :param creds: credentials
        :return: client
        """

        cls.logger.info("Trying to create an RTM client.")

        client = Client(creds['endpoint'], creds['appkey'])
        cls.clients.append(client)

        client.start()

        while not client.is_connected() and not client.last_connecting_error():
            time.sleep(1)

        if not client.is_connected():
            cls.clients.remove(client)
            raise RuntimeError('Failed to connect to RTM')

        client = RtmClientUtil.authenticate(client, creds)

        return client

    @classmethod
    def dispose(cls) -> None:
        """
        Disposes all the clients ever created
        :return:
        """
        cls.logger.info("Disposing RTM clients")
        for client in cls.clients:
            try:
                client.dispose()
            except:
                logging.error("Failed to dispose RTM client")

    @staticmethod
    def validate_rtm_creds(creds: dict) -> None:
        """
        Validates RTM creds
        :param creds: credentials
        :return:
        """
        if creds['endpoint'] is None:
            raise ValueError("Please specify an RTM endpoint")
        if creds['appkey'] is None:
            raise ValueError("Please specify an RTM key")
        if creds['role'] is None:
            raise ValueError("Please specify an RTM role")
        if creds['secret'] is None:
            raise ValueError("Please specify an RTM secret")

    @staticmethod
    def authenticate(client: Client, creds: dict) -> Client:
        """
        Authenticates with RTM
        :param client: client
        :param creds: credentials
        :return:
        """
        auth_delegate = auth.RoleSecretAuthDelegate(creds['role'], creds['secret'])

        latch = threading.Event()

        def auth_callback(auth_result) -> None:
            if type(auth_result) == auth.Done:
                latch.set()
            else:
                raise ValueError("Can't connect to the RTM")

        client.authenticate(auth_delegate, auth_callback)
        latch.wait()

        return client
