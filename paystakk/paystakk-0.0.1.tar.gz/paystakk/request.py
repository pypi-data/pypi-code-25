import requests

from paystakk.auth import BearerTokenAuth


class PaystackRequest(object):
    """
        This encapsulates the request sent to Paystack API endpoints. It
        prepares requests before sending to Paystack's server.

        This class should not be used directly. Instead use it to compose
        "Paystack feature classes" like `Transaction`, `PaymentPage`, etc.
        """
    def __init__(self, **kwargs):
        self.req_headers = kwargs.get(
            'req_headers',
            {'Content-Type': 'application/json'}
        )
        self._auth = kwargs.get('request_auth_cls', BearerTokenAuth)(**kwargs)
        self.api_url = 'https://api.paystack.co'

    @property
    def auth(self):
        return self._auth

    @property
    def headers(self):
        return self.req_headers

    def get(self, url, payload=None, **kwargs):
        """
        Send a GET request to Paystack's server
        :param url: Paystack's API URL ('https://api.paystack.co')
        :param payload: JSON Payload to add to request

        """
        timeout = kwargs.get('timeout', 5)

        res = requests.get(
            url=url, params=payload, timeout=timeout, headers=self.headers,
            auth=self.auth
        )

        return res.json()

    def post(self, url, json, **kwargs):
        timeout = kwargs.get('timeout', 5)

        res = requests.post(
            url=url, json=json, timeout=timeout, headers=self.req_headers,
            auth=self.auth
        )

        if res.status_code in [requests.codes.created, requests.codes.ok]:
            return res.json()
        else:
            res.raise_for_status()

    @staticmethod
    def put(url, data, **kwargs):
        timeout = kwargs.get('timeout', 0.001)
        r = requests.put(url=url, data=data, timeout=timeout)
        return r
