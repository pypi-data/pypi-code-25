# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


import inspect

import six


def function_key_generator(fn, namespace=None, to_str=six.text_type):
    """
    Return a function that generates a string
    key, based on a given function as well as
    arguments to the returned function itself.
    """
    # heavily inspired by dogpile.cache's function_key_generator (by Michael Bayer)
    if namespace is None:
        namespace = '%s:%s|r' % (fn.__module__, fn.__name__)
    else:
        namespace = '%s:%s|%s|r' % (fn.__module__, fn.__name__, namespace)

    args = inspect.getargspec(fn)
    has_self = args[0] and args[0][0] in ('self', 'cls')

    def generate_key(*args, **kw):
        if kw:
            raise ValueError(
                "sliding_rate_limiter's default key creation "
                "function does not accept keyword arguments.")
        if has_self:
            args = args[1:]

        return namespace + "|" + " ".join(map(to_str, args))
    return generate_key


_unit_multiplier = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 3600 * 24,
    'w': 3600 * 24 * 7,
    'y': 3600 * 24 * 365,
}


def parse_limit(limit):
    """
    Parses a limit string of the form <MAX>/<DURATION>, e.g.,
    5/s, 10/3m

    Acceptable units:
    * ms (milliseconds)
    * s(econds)
    * m(inutes)
    * h(ours)
    * d(ays)
    * w(eeks)
    * y(ears)

    :return: (MAX, DURATION in seconds)
    """
    try:
        max, duration = limit.split('/')

        max = int(max)

        if len(duration) == 1:
            duration_magnitude = 1
        else:
            duration_magnitude = int(duration[:-1])
        duration_unit = duration[-1]

        return max, duration_magnitude * _unit_multiplier[duration_unit]
    except Exception:
        raise ValueError('Invalid limit format (must be MAX/DURATION')
