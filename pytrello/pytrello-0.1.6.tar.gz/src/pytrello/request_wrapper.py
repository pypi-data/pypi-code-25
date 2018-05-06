import requests
import urllib.parse
from pytrello.decorators import as_json
from pytrello.decorators import authorized

ENDPOINT = 'https://api.trello.com/1/'


@authorized
@as_json
def get(uri, payload=None, **kwargs):
    url = urllib.parse.urljoin(ENDPOINT, uri.lstrip('/'))
    return requests.get(url.format(**kwargs), params=payload)


@authorized
@as_json
def post(uri, payload=None, **kwargs):
    url = urllib.parse.urljoin(ENDPOINT, uri.lstrip('/'))
    return requests.post(url.format(**kwargs), data=payload)


@authorized
@as_json
def delete(uri, payload=None, **kwargs):
    url = urllib.parse.urljoin(ENDPOINT, uri.lstrip('/'))
    return requests.delete(url.format(**kwargs), data=payload)


@authorized
@as_json
def put(uri, payload=None, **kwargs):
    url = urllib.parse.urljoin(ENDPOINT, uri.lstrip('/'))
    return requests.put(url.format(**kwargs), params=payload)
