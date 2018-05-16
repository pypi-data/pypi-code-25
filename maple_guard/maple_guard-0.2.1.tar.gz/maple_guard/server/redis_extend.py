# -*- coding: utf-8 -*-


class RedisExtend(object):
    """
    主要增加一些默认redis里面没带的功能
    """
    rds = None

    lua_limit_incrby = None

    # 累加，并判断累加的结果是否超过limit
    # 如果key不存在，则set limit ex timeout
    # 如果key存在，则 incrby limit
    # 最后判断结果是否超过 limit
    # KEYS[1]: key
    # ARGV[...]: increment limit timeout

    LUA_LIMIT_INCRBY_SCRIPT = '''
        local increment = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local timeout = tonumber(ARGV[3])
        local key = KEYS[1]

        local value = redis.call('GET', key)
        local result
        if not value then
            redis.call('SET', key, increment, 'EX', timeout)
            result = increment
        else
            result = redis.call('INCRBY', key, increment)
        end

        return result > limit
    '''

    def __init__(self, rds):
        self.rds = rds
        RedisExtend.register_scripts(self.rds)

    @classmethod
    def register_scripts(cls, rds):
        if cls.lua_limit_incrby is None:
            cls.lua_limit_incrby = rds.register_script(cls.LUA_LIMIT_INCRBY_SCRIPT)

    def limit_incrby(self, key, increment, limit, timeout):
        """
        限制的累加
        :param key:
        :param increment: 差值
        :param limit: 限制结果，必须>0
        :param timeout: 超时，必须>0
        :return:
        """
        keys = [key]
        args = [increment, limit, timeout]

        return self.lua_limit_incrby(
            keys=keys,
            args=args,
            client=self.rds
        )
