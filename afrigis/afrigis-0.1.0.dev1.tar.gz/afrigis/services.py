# -*- coding: utf-8 -*-
from .url_creator import create_full_url
from .exceptions import AuthenticationFailedException
import json

from urllib.parse import urlencode
from urllib import request as urllib_request

AFRIGIS_REST_URL = 'https://siebel.vodacom.co.za/rest/2/'

# Service Constants
AFRIGIS_GEOCODE_SERVICE = 'intiendols.basic.geocode.details.2'


def geocode(
        afrigis_key,
        afrigis_secret,
        address_id,
        afrigis_rest_uri=AFRIGIS_REST_URL,
):
    # Edge cases to make sure the library is used in the correct way
    if not afrigis_key or type(afrigis_key) != str or not afrigis_key.strip():
        raise ValueError('`afrigis_key` must be a valid string')

    if not afrigis_secret \
            or type(afrigis_secret) != str \
            or not afrigis_secret.strip():
        raise ValueError('`afrigis_secret` must be a valid string')

    if not address_id or type(address_id) != str or not address_id.strip():
        raise ValueError('`address_id` must be a valid string')

    query_parameters = {
        'ils_reference': address_id.encode(),
        'ils_groups': 'address_component',
    }

    base_url = create_full_url(
        afrigis_key=afrigis_key,
        afrigis_secret=afrigis_secret,
        afrigis_base_uri=afrigis_rest_uri,
        service_name=AFRIGIS_GEOCODE_SERVICE,
        query_parameters=query_parameters,
    )

    full_url = base_url + '/?' + urlencode(query_parameters)

    info_url = urllib_request.urlopen(full_url)

    result = info_url.read().decode()

    if info_url.getcode() == 200:
        response = json.loads(result)
        if response.get('statusCode', 200) == 401:
            raise AuthenticationFailedException

        return response
