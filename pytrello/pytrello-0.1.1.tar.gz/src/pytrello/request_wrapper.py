import requests
from pytrello.decorators import as_json
from pytrello.decorators import authorized


@authorized
@as_json
def get(url, payload=None, **kwargs):
    return requests.get(url.format(**kwargs), params=payload)


@authorized
@as_json
def post(url, payload=None, **kwargs):
    return requests.post(url.format(**kwargs), data=payload)


@authorized
@as_json
def delete(url, payload=None, **kwargs):
    return requests.delete(url.format(**kwargs))


@authorized
@as_json
def put(url, payload=None, **kwargs):
    return requests.put(url.format(**kwargs), params=payload)
