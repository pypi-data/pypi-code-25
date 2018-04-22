from functools import wraps

import sys

from click import echo

from minds import Minds
from minds.exceptions import AuthenticationError

__author__ = """Bernardas Ališauskas"""
__email__ = 'bernardas.alisauskas@pm.me'
__version__ = '0.1.1'

def get_api(ctx, **minds_kwargs) -> Minds:
    minds = ctx.obj.get('minds')
    if minds:
        return minds
    return Minds(ctx.obj['profile'], **minds_kwargs)


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
