import os
import logging
import requests

from urllib.parse import urljoin
from vuray.utils import build_user_agent

_logger = logging.getLogger(__name__)


VURAY_API_URL = os.environ.get('VURAY_API_URL', 'https://db.vuray.org/api/v1')
VURAY_API_KEY = os.environ.get('VURAY_API_KEY', None)
# TODO: Set guest user token to properly track stuff


class VurayApi:
    def __init__(self, api_url=VURAY_API_URL, api_key=VURAY_API_KEY, **kwargs):
        kwargs.setdefault('timeout', 30)

        self._url = api_url
        self._options = kwargs
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': build_user_agent(),
            'Authorization': 'Token {}' % api_key,
        })

    def _request(self, method, url, **kwargs):
        url = urljoin(self._url, url)
        options = {**self._options, **kwargs}

        # TODO: Pin certificate? https://www.owasp.org/index.php/Certificate_and_Public_Key_Pinning
        response = self._session.request(method, url, **options)

        # TODO: Check response properly
        response.raise_for_status()

        # TODO: Wrap potential JSONDecodeError properly
        return response.json()

    def _get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def check_package(self, manager, package_str):
        result = self._get('/{}/{}'.format(manager, package_str))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class VurayApiException(Exception):
    pass
