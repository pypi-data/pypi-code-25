from functools import wraps, partial
from urlparse import urlparse, parse_qs

from pony.orm import db_session as db_session_
from nameko.extensions import DependencyProvider


__all__ = ["PonySession"]


def parse_connection_string(conn_str):
    uri = urlparse(conn_str)
    result = dict(provider='postgres' if uri.scheme == 'postgresql' else uri.scheme)

    if result['provider'] == 'sqlite':
        result.update(filename=uri.path[1:])
    elif result['provider'] in ('mysql', 'postgres'):
        result.update(host=uri.hostname,
                      port=uri.port,
                      user=uri.username,
                      password=uri.password,
                      database=uri.path[1:],
                      **parse_qs(uri.query))
    elif result['provider'] == 'oracle':
        result.update(user=uri.username, password=uri.password, dsn='{0}/{1}'.format(uri.hostname, uri.path[1:]))
    else:
        raise NotImplemented('provider `{}` not support'.format(result['provider']))

    return result


class PonySession(DependencyProvider):
    def __init__(self, db, config_key='DATABASE_URI'):
        self.db = db
        self.config_key = config_key

    def __call__(self, func=None, attr='db_session'):
        if not func:
            return partial(self, attr=attr)

        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not hasattr(args[0], attr):
                raise ValueError('service must have a Pony dependency named `%s`' % attr)
            with getattr(args[0], attr):
                return func(*args, **kwargs)
        return decorated_function

    def get_dependency(self, worker_ctx):
        if self.db.provider is None:
            self.db.bind(**parse_connection_string(worker_ctx.config.get(self.config_key)))
            self.db.generate_mapping()

        return db_session_
