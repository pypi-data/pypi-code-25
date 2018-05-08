import json

import redis

from generator.caches.base import SVGCache


class RedisCache(SVGCache):
    def __init__(self, host, port=6379, db=0):
        self._redis = redis.StrictRedis(host=host, port=port, db=db)

    @staticmethod
    def _make_key(parameters):
        hashed_parameters = json.dumps(parameters, sort_keys=True)
        return f'svgcache-{hashed_parameters}'

    def get(self, parameters):
        key = self._make_key(parameters)
        return self._redis.get(key)

    def add(self, parameters, png_bytes):
        key = self._make_key(parameters)
        self._redis.set(key, png_bytes)
