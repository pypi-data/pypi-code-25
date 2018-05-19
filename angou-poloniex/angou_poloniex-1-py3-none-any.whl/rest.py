import logging
import requests
from . import auth_utils


class _PoloniexAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, r):
        r.headers.update({
            'Sign': auth_utils.generate_signature(self.api_secret, r.body or ''),
            'Key': self.api_key,
        })
        return r


class RestError(Exception):
    pass


class RestSession:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self._session = requests.Session()
        self._auth = _PoloniexAuth(api_key, api_secret)
        self.logger = logging.getLogger('angou_poloniex')

    def request(self, command, params=None):
        self.logger.debug('%s %s', command, params)

        params = params or {}
        params.update({
            'command': command,
            'nonce': auth_utils.generate_nonce(),
        })

        req = requests.Request('POST', 'https://poloniex.com/tradingApi',
                               data=params, auth=self._auth)
        r = self._session.send(self._session.prepare_request(req))
        r.raise_for_status()
        resp = r.json()

        if 'error' in resp:
            raise RestError(resp['error'])
        return resp
