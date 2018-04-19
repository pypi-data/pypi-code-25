from functools import wraps
from urllib.parse import quote, urlparse

from minds.exceptions import AuthenticationError


def add_url_kwargs(url, **kwargs):
    """Add keyword parameters to url"""
    if not kwargs:
        return url
    url = url.strip('/')
    parsed = urlparse(url).query
    url += '&' if parsed else '?'
    for k, v in kwargs.items():
        if not k or not v:
            continue
        if k in parsed:
            continue
        url += f'{quote(str(k))}={quote(str(v))}&'
    return url.strip('&')


def requires_auth(func):
    """Decorator for that checks whether loggedin cookie is present in the current session"""

    @wraps(func)
    def new_func(self, *args, **kwargs):
        if not self.con.cookies['loggedin'] == '1':
            raise AuthenticationError(
                f'{type(self).__name__}.{func.__name__} requires authentication, call "authenticate" method first or provide username password kwars upon object creation')
        return func(self, *args, **kwargs)

    return new_func
