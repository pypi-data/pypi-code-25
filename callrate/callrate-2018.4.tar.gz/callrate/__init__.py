from .callrate import CallRate


def call_rate(calls_count=7, seconds=10, wait=True):
    def decorator(func):
        call_rate_temp = CallRate(calls_count, seconds, wait)
        def wrapper(*args, **kargs):
            call_rate_temp()
            return func(*args, **kargs)
        return wrapper
    return decorator