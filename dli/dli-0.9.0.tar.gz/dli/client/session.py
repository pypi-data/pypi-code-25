from dli.client.dli_client import DliClient

import urllib3
import requests

urllib3.disable_warnings()


def start_session(api_key, root_url):
    client = DliClient(api_key, root_url)
    return client
