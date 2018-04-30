import uuid

from webob.cookies import CookieProfile
from zope.interface import implementer


from pyramid.authentication import _SimpleSerializer

from pyramid.compat import (
    bytes_,
    text_,
)
from pyramid.interfaces import ICSRFStoragePolicy
from pyramid.util import (
    strings_differ
)


__VERSION__ = '0.0.4'


# ==============================================================================


@implementer(ICSRFStoragePolicy)
class DualCookieCSRFStoragePolicy(object):
    """
    A re-implementation of Pyramid's CookieCSRFStoragePolicy.
    This policy runs separate csrf tokes on http and https connections.
    """
    _token_factory = staticmethod(lambda: text_(uuid.uuid4().hex))

    def __init__(
        self,
        cookie_name_secure='csrf_https',
        cookie_name_http='csrf_http',
        httponly=False, domain=None, max_age=None, path='/'
    ):
        serializer = _SimpleSerializer()
        self.cookie_name_secure = cookie_name_secure
        self.cookie_name_http = cookie_name_http
        self.cookie_profile_secure = CookieProfile(
            cookie_name=cookie_name_secure,
            secure=True,
            max_age=max_age,
            httponly=httponly,
            path=path,
            domains=[domain],
            serializer=serializer
        )
        self.cookie_profile_http = CookieProfile(
            cookie_name=cookie_name_http,
            secure=False,
            max_age=max_age,
            httponly=httponly,
            path=path,
            domains=[domain],
            serializer=serializer
        )

    def new_csrf_token(self, request):
        """ Sets a new CSRF token into the request and returns it. """

        def _token_secure():
            token = self._token_factory()
            request.cookies[self.cookie_name_secure] = token

            def _set_cookie(request, response):
                self.cookie_profile_secure.set_cookies(
                    response,
                    token,
                )
            request.add_response_callback(_set_cookie)
            return token

        def _token_http():
            token = self._token_factory()
            request.cookies[self.cookie_name_http] = token

            def _set_cookie(request, response):
                self.cookie_profile_http.set_cookies(
                    response,
                    token,
                )
            request.add_response_callback(_set_cookie)
            return token

        if request.scheme == 'https':
            token_http = _token_http()  # noqa
            token_secure = _token_secure()
            return token_secure

        # otherwise, set the https
        token_http = _token_http()
        return token_http

    def get_csrf_token(self, request):
        """ Returns the currently active CSRF token by checking the cookies
        sent with the current request."""
        if request.scheme == 'https':
            bound_cookies = self.cookie_profile_secure.bind(request)
        else:
            bound_cookies = self.cookie_profile_http.bind(request)
        token = bound_cookies.get_value()
        if not token:
            token = self.new_csrf_token(request)
        return token

    def check_csrf_token(self, request, supplied_token):
        """ Returns ``True`` if the ``supplied_token`` is valid."""
        expected_token = self.get_csrf_token(request)
        return not strings_differ(
            bytes_(expected_token), bytes_(supplied_token))

    def get_csrf_token_scheme(self, request, scheme):
        """this is a utility for testing"""
        if scheme not in ('https', 'http'):
            raise ValueError("unknown scheme")
        if scheme == 'https':
            if request.scheme != 'https':
                return None
            bound_cookies = self.cookie_profile_secure.bind(request)
            token = bound_cookies.get_value()
            return token
        bound_cookies = self.cookie_profile_http.bind(request)
        token = bound_cookies.get_value()
        return token
