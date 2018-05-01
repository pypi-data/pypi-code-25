"""Module to apply security schemes."""

# Copyright © 2017–2018 Paul Bryan.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import roax.context

from abc import ABC, abstractmethod
from roax.wsgi import Filter


class SecurityScheme:
    """Base class for security schemes."""

    def __init__(self, type, description):
        super().__init__()
        self.type = type
        self.description = description

    def json_encode(self):
        """Return the JSON representation of the security scheme."""
        result = {}
        result["type"] = self.type
        if self.description is not None:
            result["description"] = self.description
        return result

    def get_request(self):
        return roax.context.get("http_request")


class HTTPSecurityScheme(SecurityScheme):
    """Base class for HTTP authentication security scheme."""

    def __init__(self, scheme, **kwargs):
        super().__init__("http", **kwargs)
        self.scheme = scheme

    def json_encode(self):
        """Return the JSON representation of the security scheme."""
        result = super().json_encode()
        result["scheme"] = scheme
        return result


from base64 import b64decode
import binascii
class HTTPBasicSecurityScheme(HttpSecurityScheme):
    """Base class for HTTP basic authentication security scheme."""

    def __init__(self, **kwargs):
        super().__init__("basic", **kwargs)

    def handle(self, request, next):
        if request.authorization and request.authorization[0].lower() == "basic":
            try:
                username, password = b64decode(authorization[1]).decode().split(":", 1)
            except (binascii.Error, UnicodeDecodeError):
                pass
            self.authenticate(username, password)
        next.handle(request)

    @abstractmethod
    def authenticate(username, password):
        """Authenticate the user and indicate as much on the context stack."""
        pass


class APIKeySecurityScheme(SecurityScheme):
    """Base class for API key security scheme."""

    def __init(self, name, api_key_in, **kwargs):
        super().__init__("apiKey", **kwargs)
        self.name = name
        self.api_key_in = api_key_in

    def json_encode(self):
        """Return the JSON representation of the security scheme."""
        result = super().json_encode()
        result["name"] = self.name
        result["in"] = self.api_key_in
        return result

    def handle(self, request, next):
        if self.in_ == "query":
            api_key = request.GET.get(self.name)
        elif self.in_ == "header":
            api_key = request.headers.get(self.name)
        elif self.in_ == "cookie":
            api_key = request.cookies.get(self.name)
        else:
            raise SOMETHING
        self.authenticate(api_key)
        # with insert_context_here:
        return next.handle(request)

    def authenticate(api_key):
        raise NotImplementedError()


class SecurityRequirement:
    pass


class SecurityContext(Context):

    def __init__(self, scheme):
        self.scheme = scheme
