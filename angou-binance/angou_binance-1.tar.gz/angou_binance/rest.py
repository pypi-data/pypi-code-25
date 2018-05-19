from urllib.parse import urlencode
from datetime import datetime, timezone
from json.decoder import JSONDecodeError
import logging
import hmac
import hashlib
import requests


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


class RestError(Exception):
    def __init__(self, code, message):
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message


class RestSession:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'angou-binance-yo',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-MBX-APIKEY': api_key,
        })
        self.logger = logging.getLogger('angou_binance')

    def request(self, verb, path, signed=False, query=None, post=None):
        self.logger.debug('%s %s signed=%s query=%s post=%s', verb, path, signed, query, post)

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

        url = f'https://api.binance.com{path}?{query_string}'

        req = requests.Request(verb, url, data=post_string or None)
        prepared_req = self._session.prepare_request(req)
        resp = self._session.send(prepared_req)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if resp is not None and 400 <= resp.status_code < 600:
                try:
                    err_obj = resp.json()
                    raise RestError(code=err_obj['code'], message=err_obj['msg'])
                except (JSONDecodeError, KeyError):
                    pass
            raise ex
        else:
            return resp.json()
