# -*- coding: utf-8 -*-

import hmac
import hashlib
import base64

try:
    # Python 2 support
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def get_auth_code_digest(
        afrigis_key,
        afrigis_secret,
        service_name,
        query_params
):
    """
    Get Afrigis Auth Code by hashing the calling url with the secret key.
    """

    if not query_params:
        query_params = {}

    message = '{}/{}/{}'.format(
        urlencode(query_params),
        service_name,
        afrigis_key
    )

    # Hash Mac URL with auth secret for security
    digest = hmac.new(
        key=afrigis_secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha1
    ).digest()

    # Replace URL items which might cause problems
    authCode = base64.b64encode(digest).decode() \
        .replace('+', '-') \
        .replace('/', '_') \
        .replace('=', '')

    return authCode
