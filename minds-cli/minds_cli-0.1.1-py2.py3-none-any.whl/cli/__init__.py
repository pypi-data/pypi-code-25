from functools import wraps
import sys

from click import echo

from minds import Minds
from minds.exceptions import AuthenticationError


def get_api(ctx) -> Minds:
    minds = ctx.obj.get('minds')
    if minds:
        return minds
    return Minds(ctx.obj['profile'])


def requires_auth(func):
    """Decorator for that checks whether API is logged in"""

    @wraps(func)
    def new_func(ctx, *args, **kwargs):
        try:
            if not get_api(ctx).is_authenticated:
                echo(f'{func.__name__} requires authentication, see --help', err=True)
                sys.exit(1)
        except AuthenticationError as e:
            echo(e.args[0], err=True)
            sys.exit(1)
        return func(ctx, *args, **kwargs)

    return new_func


def print_response(*keys, everything=False):
    """
    :param everything:
    :param incl_status:
    :param keys:
    :return:
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            resp = function(*args, **kwargs)
            if not isinstance(resp, dict):
                return resp
            if resp['status'] != 'success' or everything:
                echo(resp)
                return resp
            for key in keys:
                modifiers = []
                if isinstance(key, tuple):
                    key, *modifiers = key
                try:
                    subkeys = key.split(':')
                    value = resp
                    for key in subkeys:
                        value = value[key]
                    for modify in modifiers:
                        value = modify(value)
                    echo(value)
                except KeyError:
                    echo(f'{key}: response not found')

            return resp

        return wrapper

    return real_decorator


