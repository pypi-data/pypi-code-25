from functools import wraps
from urlparse import urlparse, parse_qs

from pony.orm import *
from nameko.extensions import DependencyProvider


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
    def __init__(self, db):
        self.db = db

    def get_dependency(self, worker_ctx):
        if self.db.provider is None:
            self.db.bind(**parse_connection_string(worker_ctx.config.get('DATABASE_URI')))
            # self.db.generate_mapping(create_tables=True)
            self.db.generate_mapping()

        return db_session


def db_session(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not hasattr(args[0], 'db_session'):
            raise ValueError('service must have a PonySession dependency named `db_session`')
        with args[0].pony_session:
            return func(*args, **kwargs)

    return decorated_function
