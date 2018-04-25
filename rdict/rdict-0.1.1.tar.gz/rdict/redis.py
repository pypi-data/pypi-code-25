from redis import Redis
import pickle


class RTypeRedis(Redis):
    def __getitem__(self, item):
        return KeyObject(self, item)

    def __setitem__(self, key, value):
        if value is None:
            self.__delitem__(key)
        if type(value) is list:
            self.delete(key)
            value = [pickle.dumps(v, pickle.HIGHEST_PROTOCOL) for v in value]
            self.lpush(key, *value)
        if type(value) is dict:
            self.delete(key)
            for k, v in value.items():
                k = pickle.dumps(k, pickle.HIGHEST_PROTOCOL)
                v = pickle.dumps(v, pickle.HIGHEST_PROTOCOL)
                self.hset(key, k, v)
        self.set(key, pickle.dumps(value, pickle.HIGHEST_PROTOCOL))

    def __delitem__(self, key):
        self.delete(key)

    def __contains__(self, item):
        return self.exists(item)


class KeyObject:
    def __init__(self, redis: Redis, key):
        self._redis = redis
        self._key = key

    def as_list(self):
        return self._redis.lrange(self._key, 0, -1)

    def as_value(self, default=None):
        v = self._redis.get(self._key)
        return pickle.loads(v) if v is not None else default

    def as_dict(self):
        result = {}
        for k, v in self._redis.hgetall(self._key).items():
            k = pickle.loads(k)
            v = pickle.loads(v)
            result[k] = v
        return result

    def as_object(self, default=None):
        v = self._redis.get(self._key)
        return pickle.loads(v) if v is not None else default

    def save_object(self, obj):
        v = pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)
        self._redis.set(self._key, v)
