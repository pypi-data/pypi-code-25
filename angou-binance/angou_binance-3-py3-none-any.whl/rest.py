from urllib.parse import urlencode
from datetime import datetime, timezone
import logging
import hmac
import hashlib
import requests


LOGGER = logging.getLogger('angou_binance')


def _append_to_query_string(query, extra_params):
    if not query:
        return extra_params
    return f'{query}&{extra_params}'


def _generate_signature(secret, query, body):
    if isinstance(body, (bytes, bytearray)):
        body = body.decode('utf8')
    message = query + body
    signature = hmac.new(
        bytes(secret, 'utf8'),
        bytes(message, 'utf8'),
        digestmod=hashlib.sha256)
    return signature.hexdigest()


def _utc_timestamp():
    return datetime.now(tz=timezone.utc).timestamp()


class InvalidJSON(Exception):
    pass


class RestError(Exception):
    def __init__(self, code, message):
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message


class RestSession:
    def __init__(self, api_key, api_secret, timeout=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'angou-binance-yo',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'X-MBX-APIKEY': api_key,
        })

    def _get_query_and_body(self, signed=False, query=None, post=None):
        query_string = urlencode(query or {})
        post_string = urlencode(post or {})

        if signed:
            timestamp = int(_utc_timestamp() * 1000)
            query_string = _append_to_query_string(query_string, f'timestamp={timestamp}')

            signature = _generate_signature(self.api_secret, query_string, post_string)
            signature_string = f'signature={signature}'
            if post is None:
                query_string = _append_to_query_string(query_string, signature_string)
            else:
                post_string = _append_to_query_string(post_string, signature_string)

        return query_string, post_string

    def request(self, verb, path, signed=False, query=None, post=None):
        LOGGER.debug('%s %s signed=%s query=%s post=%s', verb, path, signed, query, post)
        query, body = self._get_query_and_body(signed, query, post)
        url = f'https://api.binance.com{path}?{query}'
        resp = self._session.request(verb, url, data=body or None, timeout=self.timeout)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            try:
                err_obj = resp.json()
            except ValueError:
                pass
            else:
                try:
                    raise RestError(code=err_obj['code'], message=err_obj['msg'])
                except KeyError:
                    pass
            raise
        else:
            try:
                return resp.json()
            except ValueError:
                raise InvalidJSON()
