import json
import os
import sys
import requests
import pytrello
from functools import wraps


def abort_authorization():
    sys.exit("""
Your key and token is not properly configured.

Please run command:

'pytrello configure'

to configure your key and token for Trello API.
""")


def get_key_and_token():
    package_dir = os.path.dirname(pytrello.__path__[0])
    config_json = os.path.join(package_dir, 'pytrello', 'config.json')
    try:
        config_dict = json.loads(open(config_json).read())

        for k, v in config_dict.items():
            if v is None:
                abort_authorization()
    except FileNotFoundError:
        abort_authorization()

    return config_dict['key'], config_dict['token']


def as_json(request_function):
    @wraps(request_function)
    def wrap(*args, **kwargs):
        r = request_function(*args, **kwargs)
        if r.status_code == requests.codes.ok:
            return json.loads(r.text)
        else:
            error_message = 'Error occurred in function %s: [%d] %s' \
                         % (request_function.__name__, r.status_code, r.reason)
            sys.exit(error_message)

    return wrap


def authorized(func):
    @wraps(func)
    def wrap(url, *args, payload=None, **kwargs):
        payload = payload if payload is not None else dict()
        payload['key'], payload['token'] = get_key_and_token()
        return func(url, *args, payload=payload, **kwargs)

    return wrap
