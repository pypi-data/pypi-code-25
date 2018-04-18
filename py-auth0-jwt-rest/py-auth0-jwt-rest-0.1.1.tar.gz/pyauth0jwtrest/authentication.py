import base64

from django.contrib.auth.backends import RemoteUserBackend, get_user_model
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from pyauth0jwtrest.settings import jwt_api_settings, auth0_api_settings
from pyauth0jwtrest.utils import get_auth0_public_key

jwt_decode_handler = jwt_api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = jwt_api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

import logging
logger = logging.getLogger(__name__)


class Auth0JSONWebTokenAuthentication(JSONWebTokenAuthentication, RemoteUserBackend):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """

    def authenticate(self, request):
        """
        You should pass a header of your request: clientcode: web
        This function initialize the settings of JWT with the specific client's informations.
        """

        jwt_api_settings.JWT_ALGORITHM = auth0_api_settings.ALGORITHM
        jwt_api_settings.JWT_AUDIENCE = auth0_api_settings.CLIENT_ID
        jwt_api_settings.JWT_AUTH_HEADER_PREFIX = auth0_api_settings.JWT_AUTH_HEADER_PREFIX

        # RS256 Related configurations
        if auth0_api_settings.ALGORITHM.upper() == "HS256":
            if auth0_api_settings.CLIENT_SECRET_BASE64_ENCODED:
                jwt_api_settings.JWT_SECRET_KEY = base64.b64decode(
                    auth0_api_settings.CLIENT_SECRET.replace("_", "/").replace("-", "+")
                )
            else:
                jwt_api_settings.JWT_SECRET_KEY = auth0_api_settings.CLIENT_SECRET

        # If RS256, call the utility method to load the public cert from Auth0
        elif auth0_api_settings.ALGORITHM.upper() == "RS256":
            jwt_api_settings.JWT_PUBLIC_KEY = get_auth0_public_key(auth0_api_settings.DOMAIN)

        return super(Auth0JSONWebTokenAuthentication, self).authenticate(request)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """

        UserModel = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        # Attempt to create/find user
        user = None
        if auth0_api_settings.CREATE_USERS:

            # Check for email property, and if so assign it to both username and email
            if auth0_api_settings.USERNAME_FIELD == 'email':
                user, created = UserModel.objects.get_or_create(username=username, email=username)
            else:
                user, created = UserModel._default_manager.get_or_create(**{
                    UserModel.USERNAME_FIELD: username
                })
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                msg = _('Invalid signature.')
                raise exceptions.AuthenticationFailed(msg)
                # RemoteUserBackend behavior:
                # pass

        return user if self.user_can_authenticate(user) else None

