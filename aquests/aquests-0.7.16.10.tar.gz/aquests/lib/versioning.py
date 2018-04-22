import warnings
from functools import wraps

def deprecated (f):
    @wraps(f)
    def wrapper (was, *args, **kwargs):
        warnings.simplefilter ('default')
        warnings.warn (
           "f.__name__ will be deprecated",
            DeprecationWarning
        )
        return f (was, *args, **kwargs)
    return wrapper