from dappmx.info import LIB_VERSION
from dappmx.error import DappError
import requests
import urllib
import json

VALID_API_VERSIONS = [
    "1",
]


class APIClient(object):

    @classmethod
    def request(cls, method, endpoint, params=None, _api_version=None,
                _merchant_id=None, _api_key=None, _is_sandbox=None):

        if _api_version is None:
            _api_version = VALID_API_VERSIONS[0]
        else:
            if _api_version not in VALID_API_VERSIONS:
                raise DappError(code=-1105, msg="Invalid Api version.")

        _api_version = "v{}".format(_api_version)

        if _merchant_id is None:
            from dappmx import merchant_id
            _merchant_id = merchant_id

        if _api_key is None:
            from dappmx import api_key
            _api_key = api_key

        if _is_sandbox is None:
            from dappmx import is_sandbox
            _is_sandbox = is_sandbox

        if _merchant_id is None:
            raise DappError(code=-1101, msg='No Merchant Id.')

        if _api_key is None:
            raise DappError(code=-1102, msg='No Api Key.')

        if _is_sandbox is None:
            raise DappError(code=-1103, msg="Wrong enviroment.")

        absolute_url = "{}{}/{}".format(get_base_url(_is_sandbox), _api_version, endpoint)

        headers = {
            'User-Agent': 'Dapp Python/%s' % (LIB_VERSION,),
            'content-type': 'application/json',
        }

        if method == 'GET':
            if params is not None:
                try:
                    absolute_url = "%s?%s" % (absolute_url, urllib.parse.urlencode(params, True))
                except AttributeError:
                    absolute_url = "%s?%s" % (absolute_url, urllib.urlencode(params, True))
            data = ''
        else:
            if params is None:
                params = ''
            data = json.dumps(params)

        body = requests.request(method, absolute_url,
                                headers=headers, data=data,
                                timeout=30,
                                auth=(_merchant_id, _api_key))

        headers = body.headers
        headers['status'] = str(body.status_code)
        body = body.content
        try:
            body = str(body, 'utf-8')
        except TypeError:
            body = str(body)

        if headers['status'] == '200':
            response_body = json.loads(body)
            rc = int(response_body["rc"])
            if rc < 0:
                raise DappError(json_error=response_body)
            return response_body.get('data', None)
        else:
            raise DappError(code=-1104, msg='Unexpected response.')


def get_base_url(is_sandbox):
    if is_sandbox:
        base_url = 'https://sandbox.dapp.mx/'
    else:
        base_url = 'https://api.dapp.mx/'

    return base_url

