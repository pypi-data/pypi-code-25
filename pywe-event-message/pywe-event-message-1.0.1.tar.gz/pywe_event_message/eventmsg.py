# -*- coding: utf-8 -*-

from __future__ import unicode_literals


__all__ = ['parse_eventkey']


def parse_eventkey(eventkey, event='subscribe', key_cast_func=None):
    if not eventkey:
        return ''
    if event == 'subscribe':
        eventkey = eventkey.split('_')[-1]
    # SCAN etc.
    return key_cast_func(eventkey) if key_cast_func else eventkey
