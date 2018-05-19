from urllib.parse import urlparse
import logging
import requests
from . import auth_utils


class _BitmexNonceAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, r):
        nonce = auth_utils.generate_nonce()

        parsed_url = urlparse(r.url)
        path = parsed_url.path
        if parsed_url.query:
            path += '?' + parsed_url.query

        r.headers.update({
            'api-nonce': str(nonce),
            'api-signature': auth_utils.generate_signature(self.api_secret, r.method, path, nonce,
                                                           r.body or ''),
            'api-key': self.api_key,
        })

        return r


class RestError(Exception):
    def __init__(self, code, text, message=None):
        super().__init__(f'HTTP {code}: {message or ""}')
        self.code = code
        self.text = text
        self.message = message


class RestBadRequestError(RestError):
    pass


class RestRateLimitExceededError(RestError):
    def __init__(self, code, text, retry_after):
        super().__init__(code, text)
        self.retry_after = retry_after


class RestTemporaryDownError(RestError):
    pass


class RestSession:
    def __init__(self, domain, api_key, api_secret):
        self._base_url = f'https://{domain}/api/v1'
        self._session = requests.Session()
        self._session.headers.update({
            'user-agent': 'angou-bitmex-yo',
            'content-type': 'application/json',
            'accept': 'application/json',
        })
        self._auth = _BitmexNonceAuth(api_key, api_secret)
        self.logger = logging.getLogger('angou_bitmex')

    def request(self, verb, path, query=None, postdict=None):
        self.logger.debug('%s %s query=%s postdict=%s', verb, path, query, postdict)

        url = self._base_url + path

        req = requests.Request(verb, url, json=postdict, auth=self._auth, params=query)
        prepared_req = self._session.prepare_request(req)
        resp = self._session.send(prepared_req)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if resp is None:
                raise ex
            elif resp.status_code == 400:
                error = resp.json()['error']
                message = error['message'] if error else ''
                raise RestBadRequestError(resp.status_code, resp.text, message)
            elif resp.status_code == 429:
                retry_after = None
                try:
                    retry_after = int(resp.headers['Retry-After'])
                except (ValueError, KeyError):
                    pass
                raise RestRateLimitExceededError(resp.status_code, resp.text, retry_after)
            elif resp.status_code == 503:
                raise RestTemporaryDownError(resp.status_code, resp.text)
            else:
                raise RestError(resp.status_code, resp.text)
        else:
            return resp.json()
