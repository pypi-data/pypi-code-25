import os
import tempfile
import hashlib
from flask import request
from werkzeug.contrib.cache import NullCache, RedisCache, FileSystemCache


class FastFileSystemCache(FileSystemCache):
    def delete_wildard(self, key):
        key = self.make_safe_filename(key)
        key = os.path.join(self._path, key)
        for fname in self._list_dir():
            print(fname)
            print(fname.find(key))
            if fname.find(key) == 0:
                try:
                    os.remove(fname)
                except (IOError, OSError):
                    self._update_count(value=len(self._list_dir()))
                    return False
                else:
                    self._update_count(delta=-1)
        return True

    def delete(self, key, mgmt_element=False):  # noqa
        try:
            os.remove(self._get_filename(key))
        except (IOError, OSError):
            return False
        else:
            # Management elements should not count towards threshold
            if not mgmt_element:
                self._update_count(delta=-1)
        return True

    @staticmethod
    def make_safe_filename(s):
        def safe_char(c):
            if c.isalnum():
                return c
            else:
                return "_"
        return "".join(safe_char(c) for c in s).rstrip("_")

    def _get_filename(self, key):
        key = self.make_safe_filename(key)
        return os.path.join(self._path, key)


class FastNullCache(NullCache):
    @staticmethod
    def delete_wildard(key):
        return True

    def delete(self, key):
        return True


class FastRedisCache(RedisCache):

    def delete_wildard(self, key):
        from redis.connection import ResponseError
        try:
            self._client.eval(
                '''return redis.call('del', unpack(redis.call('keys', ARGV[1])))''', 0, '{}:*'.format(key))
        except ResponseError:
            pass
        return True

    def delete(self, key):  # noqa
        return self._client.delete(self.key_prefix + key)


class FastCache(object):
    @staticmethod
    def setup():
        cache_type = os.environ.get('CACHE_TYPE', 'null')
        if cache_type == 'redis':
            cache_host = os.environ.get('CACHE_REDIS_HOST', 'localhost')
            cache_port = os.environ.get('CACHE_REDIS_PORT', 6379)
            return FastRedisCache(host=cache_host, port=cache_port)
        elif cache_type == 'file':
            tmp_dir = tempfile.mkdtemp()
            return FastFileSystemCache(cache_dir=tmp_dir)
        else:
            return FastNullCache()

    @staticmethod
    def make_cache_key_request_args():
        """Create consistent keys for query string arguments.
        Produces the same cache key regardless of argument order, e.g.,
        both `?limit=10&offset=20` and `?offset=20&limit=10` will
        always produce the same exact cache key.
        """

        # Create a tuple of (key, value) pairs, where the key is the
        # argument name and the value is its respective value. Order
        # this tuple by key. Doing this ensures the cache key created
        # is always the same for query string args whose keys/values
        # are the same, regardless of the order in which they are
        # provided.
        args_as_sorted_tuple = tuple(
            sorted(
                (pair for pair in request.args.items(multi=True))
            )
        )
        # ... now hash the sorted (key, value) tuple so it can be
        # used as a key for cache. Turn them into bytes so that md5
        # will accept them
        args_as_bytes = str(args_as_sorted_tuple).encode()
        hashed_args = str(hashlib.md5(args_as_bytes).hexdigest())  # nosec
        return hashed_args
