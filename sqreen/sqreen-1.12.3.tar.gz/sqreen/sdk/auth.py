# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Authentication sdk functions
"""

import logging
import traceback
from datetime import datetime

from ..actions import ACTION_STORE
from ..runtime_storage import runtime
from ..utils import is_string

LOGGER = logging.getLogger(__name__)


def auth_track(success, **user_identifiers):
    """ Register a successfull or failed authentication attempt (based on
    success boolean) for an user identified by the keyword-arguments.
    For example:

    auth_track(True, email="foobar@example.com") register a successfull
    authentication attempt for user with email "foobar@example.com".

    auth_track(False, user_id=42) register a failed authentication
    attempt for user with id 42.
    """
    pass


def signup_track(**user_identifiers):
    """ Register a new account signup identified by the keyword-arguments.
    For example:

    auth_track(email="foobar@example.com", user_id=42) register
    a new account signup for user identifed by email "foobar@example.com" or
    bu user id 42.
    """
    pass


def identify(auth_keys, traits=None):
    if traits is None:
        traits = {}
    runtime.observe('sdk', [
        'identify',
        datetime.utcnow(),
        auth_keys,
        traits,
    ], report=False)


_SQREEN_EVENT_PREFIX = 'sq.'
_TRACK_OPTIONS_FIELDS = frozenset([
    'properties',
    'user_identifiers',
    'timestamp',
])
_TRACK_PAYLOAD_SECTIONS = ('request', 'params', 'headers')


def track(event, options=None):
    if not is_string(event):
        raise TypeError("event name must be a string, not {}"
                        .format(event.__class__.__name__))
    if event.startswith(_SQREEN_EVENT_PREFIX):
        LOGGER.warning("Event names starting with %r are reserved, "
                       "event %r has been ignored",
                       _SQREEN_EVENT_PREFIX, event)
        return False
    if options is None:
        options = {}
    for option_key in list(options):
        if option_key not in _TRACK_OPTIONS_FIELDS:
            LOGGER.warning("Invalid option key %r, skipped", option_key)
            del options[option_key]
    if 'timestamp' not in options:
        timestamp = datetime.utcnow()
        options['timestamp'] = timestamp
    else:
        timestamp = options['timestamp']
        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp option must be a datetime object, not {}"
                            .format(event.__class__.__name__))
    action = ACTION_STORE.get_for_event(event)
    if action:
        LOGGER.debug("Stacktrace recorded by action %s for event %s",
                     action.iden, event)
        options['stacktrace'] = traceback.format_stack()
    runtime.observe('sdk', [
        'track',
        timestamp,
        event,
        options,
    ], payload_sections=_TRACK_PAYLOAD_SECTIONS, report=True)
    return True
