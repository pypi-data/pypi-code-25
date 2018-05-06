import os
import pytrello
import yaml
from functools import wraps
import pytrello.request_wrapper as request


def get_api_info(api_name):
    package_dir = os.path.dirname(pytrello.__path__[0])
    api_yaml = os.path.join(package_dir, 'pytrello', 'api', 'api.yaml')
    api_info = yaml.load(open(api_yaml))
    return api_info[api_name]


def run_api(api_name, **kwargs):
    api_info = get_api_info(api_name)
    uri = api_info['uri']
    request_type = api_info['request_type']

    # Prepare payloads.
    if 'parameters' in api_info:
        parameters = api_info['parameters']
        payload = dict()
        print(kwargs)
        for parameter in parameters:
            payload[parameter] = kwargs.get(parameter, None)
    else:
        payload = None

    if request_type == 'GET':
        r = request.get(uri, payload=payload, **kwargs)
    elif request_type == 'POST':
        r = request.post(uri, payload=payload, **kwargs)
    elif request_type == 'PUT':
        r = request.put(uri, payload=payload, **kwargs)
    elif request_type == 'DELETE':
        r = request.delete(uri, payload=payload, **kwargs)

    return r


def basic_api(api_func):
    @wraps(api_func)
    def wrap(*args, **kwargs):
        r = run_api(api_func.__name__, *args, **kwargs)
        return r

    return wrap
