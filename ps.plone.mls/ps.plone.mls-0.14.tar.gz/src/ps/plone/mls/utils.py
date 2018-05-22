# -*- coding: utf-8 -*-
"""Different shared utilities."""

from plone import api
from plone.api.exc import InvalidParameterError
from ps.plone.mls import _
from zope.interface import Invalid

import re


check_email = re.compile(
    r'[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}').match

check_for_url = re.compile(
    r'http[s]?://').search


def validate_email(value):
    if value:
        if not check_email(value):
            raise Invalid(_(u'Invalid email address.'))
    return True


def contains_nuts(value):
    """Check for traces of nuts, like urls or other spammer fun things"""
    if value:
        if check_for_url(value):
            raise Invalid(_(u'No URLs allowed.'))
    return True


def merge_local_contact_info(settings=None, mapping=None, data=None):
    """Merge values of locally provided contact info."""
    keys_internal = [
        'force',
        'use_custom_info',
    ]

    # Clear any existing data.
    data.clear()

    for key, value in settings.items():
        if key in keys_internal:
            continue
        if value is None:
            continue
        mapped_key = mapping.get(key)
        if mapped_key is None:
            continue
        data[mapped_key] = value


def smart_truncate(content):
    """Truncate a string for some max length, but split at word boundary.

    Settings for `length` and `ellipsis` are taken from the Plone settings.
    In Plone 5 the `portal_properties` tool was removed and all settings
    have been migrated to the registry. Currently the setting for
    `ellipsis` has not yet been migrated. So we have to check for both
    settings individually.
    """
    if content is None:
        return

    try:
        enabled = api.portal.get_registry_record(
            'plone.mls.listing.interfaces.IMLSUISettings.truncate_texts',
        )
    except InvalidParameterError:
        return content

    if not enabled:
        return content

    try:
        length = api.portal.get_registry_record(
            'plone.mls.listing.interfaces.IMLSUISettings.truncate_length',
        )
    except InvalidParameterError:
        length = 320

    try:
        ellipsis = api.portal.get_registry_record('plone.ellipsis')
    except InvalidParameterError:
        try:
            props = api.portal.get_tool(name='portal_properties')
            ellipsis = props.site_properties.ellipsis
        except Exception:
            ellipsis = u'...'

    if len(content) > length:
        content = content[:length].rsplit(' ', 1)[0] + ellipsis
    return content
