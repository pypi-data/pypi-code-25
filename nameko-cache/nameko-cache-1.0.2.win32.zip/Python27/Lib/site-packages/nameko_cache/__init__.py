from hashlib import md5
from cPickle import dumps
from functools import wraps, partial
from inspect import getmodule


def cached(func=None, timeout=60, redis_attr='cache', key_prefix=None):
    if not func:
        return partial(cached, timeout=timeout, redis_attr=redis_attr, key_prefix=key_prefix)

    module_name = getmodule(func).__name__
    func_name = func.__name__

    @wraps(func)
    def decorated_function(service, *args, **kwargs):
        args_key = md5(dumps((args, kwargs))).hexdigest()
        key = '{0}_cache_{1}.{2}.{3}'.format(key_prefix or '', module_name, func_name, args_key)
        redis = getattr(service, redis_attr)
        val = redis.get(key)
        if val:
            return val
        val = func(service, *args, **kwargs)
        redis.set(key, val, ex=timeout)
        return val

    return decorated_function


def delete_cached(func, args=None, kwargs=None, redis_attr='cache', key_prefix=None):
    module_name = getmodule(func).__name__
    func_name = func.__name__
    service = func.__self__
    args_key = md5(dumps((args or [], kwargs or {}))).hexdigest()
    key = '{0}_cache_{1}.{2}.{3}'.format(key_prefix or '', module_name, func_name, args_key)
    redis = getattr(service, redis_attr)
    return redis.delete(key)
