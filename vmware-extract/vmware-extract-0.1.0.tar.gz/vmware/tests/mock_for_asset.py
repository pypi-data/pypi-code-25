"""
    Mocks several functions from asset/client.py
"""

import os
import vmware.extract.assets
import yaml
import logging.config
import requests
from requests.exceptions import ConnectionError, ChunkedEncodingError,ReadTimeout,ConnectTimeout
import pika

class MockAsset:

    logger = logging.getLogger('{}'.format(
            __name__
        ))

    @staticmethod
    def mock_publish_message(message):
        return

    @staticmethod
    def mock_ch_basic_publish_exception():
        raise Exception("Connection was closed")



    @staticmethod
    def mock_vsphere_exception(*args, **kwargs):
        class MockResponse:
            def __init__(self, data, status_code):
                self.content = data
                self.status_code = status_code

        return MockResponse("Expired Authentication", 401)

    @staticmethod
    def mock_azure_url_expired_auth(*args, **kwargs):
        class MockResponse:
            def __init__(self, data, status_code):
                self.content = data
                self.status_code = status_code

        return MockResponse("Expired Authentication", 401)

    @staticmethod
    def mock_azure_url_resource_not_found(*args, **kwargs):
        class MockResponse:
            def __init__(self, data, status_code):
                self.content = data
                self.status_code = status_code

        return MockResponse("Resource Not found", 404)

    @staticmethod
    def mock_utils_get_azure_token(*args, **kwargs):
        return '000000'

    @staticmethod
    def mock_utils_create_connection(*args, **kwargs):
        pass

    @staticmethod
    def mock_azure_write_data_exception(*args, **kwargs):
        cee = requests.exceptions.ChunkedEncodingError("Chunked Encoding Error")
        raise cee
