import requests

from dli.client.context import Context
from dli.client.dataset_functions import DatasetFunctions
from dli.client.package_functions import PackageFunctions
from dli.client.pandas_client.pandas_functions import PandasFunctions


class AuthenticationFailure(Exception):
    GENERIC_ERROR_MESSAGE = (
        'Please verify that your API key is correct and has not expired'
    )

    def __init__(self, response):
        self.response = response

    def __str__(self):
        if self.response.text:
            return self.response.text
        return AuthenticationFailure.GENERIC_ERROR_MESSAGE


class DliClient(PackageFunctions, DatasetFunctions, PandasFunctions):
    def __init__(self, api_key, api_root):
        auth_key = self._get_auth_key(api_key, api_root)
        self.ctx = Context(api_key, api_root, auth_key)

    @staticmethod
    def _get_auth_key(api_key, api_root):
        key = api_key
        auth_header = "Bearer {}".format(key)
        start_session_url = "{}/start-session".format(api_root)  # TODO: Siren
        r = requests.post(start_session_url, headers={"Authorization": auth_header})
        if r.status_code != 200:
            raise AuthenticationFailure(r)
        return r.text

    def get_root_siren(self):
        return self.ctx.get_root_siren()
