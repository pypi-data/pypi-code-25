import asyncio
from .log import logger


COMMAND_NAMES = [
    'auth', 'dbsize', 'flushdb', 'info', 'slaveof', 'list_allow_ip', 'add_allow_ip', 'del_allow_ip', 'list_deny_ip',
    'add_deny_ip', 'del_deny_ip', 'set', 'setx', 'setnx', 'expire', 'ttl', 'get', 'getset', 'del', 'incr', 'exists',
    'getbit', 'setbit', 'bitcount', 'countbit', 'substr', 'strlen', 'keys', 'rkeys', 'scan', 'rscan', 'multi_set',
    'multi_get', 'multi_del', 'hset', 'hget', 'hdel', 'hincr', 'hexists', 'hsize', 'hlist', 'hrlist', 'hkeys',
    'hgetall', 'hscan', 'hrscan', 'hclear', 'multi_hset', 'multi_hget', 'multi_hdel', 'zset', 'zget', 'zdel', 'zincr',
    'zexists', 'zsize', 'zlist', 'zrlist', 'zkeys', 'zscan', 'zrscan', 'zrank', 'zrrank', 'zrange', 'zrrange',
    'zclear', 'zcount', 'zsum', 'zavg', 'zremrangebyrank', 'zremrangebyscore', 'zpop_front', 'zpop_back', 'multi_zset',
    'multi_zget', 'multi_zdel', 'qpush_front', 'qpush_back', 'qpop_front', 'qpop_back', 'qpush', 'qpop', 'qfront',
    'qback', 'qsize', 'qclear', 'qget', 'qset', 'qrange', 'qslice', 'qtrim_front', 'qtrim_back', 'qlist', 'qrlist'
]

COMMANDS = {
    'hexists': lambda x, **kwargs: to_bool(def_p(x)),
    'hgetall': lambda x, **kwargs: list2dict(x, **kwargs),
    'multi_hget': lambda x, **kwargs: list2dict(x, **kwargs),
}


def def_p(value, **kwargs):
    # TODO: Temporary here for all commands
    # TODO: Some commands need to return a list even for a single value
    if len(value) == 1:
        value = value[0]
    return value


def list2dict(value, encoding='utf-8', binary=False, strict=False):
    try:
        return {
            opt_decode(value[i], encoding, strict): opt_decode(value[i + 1], encoding, strict) if not binary else value[i + 1]
            for i in range(0, len(value), 2)
        }
    except UnicodeDecodeError as exc:
        return exc


def to_bool(value):
    try:
        return int(value) == 1
    except ValueError as exc:
        return exc


def opt_decode(value, encoding, strict):
    if encoding is None:
        return value

    try:
        return value.decode(encoding)
    except UnicodeDecodeError:
        if not strict:
            return value
        raise


def set_result(fut, result, *info):
    if fut.done():
        logger.debug("Waiter future is already done %r %r", fut, info)
        assert fut.cancelled(), (
            "waiting future is in wrong state", fut, result, info)
    else:
        fut.set_result(result)


def set_exception(fut, exception):
    if fut.done():
        logger.debug("Waiter future is already done %r", fut)
        assert fut.cancelled(), (
            "waiting future is in wrong state", fut, exception)
    else:
        fut.set_exception(exception)


async def wait_ok(fut):
    await fut
    return True


def format_result(command, obj, **kwargs):
    processor = COMMANDS.get(command, def_p)
    return processor(obj, **kwargs)
