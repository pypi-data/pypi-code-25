from datetime import datetime, timedelta

from tornado.ioloop import IOLoop
from watchghost.config import Server
from watchghost.loggers import Logger
from watchghost.services import Service
from watchghost.watchers import Watcher


def test_log_console():
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=False
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    now = datetime.now()

    watcher.add_check_result(
        status='critical',
        response={},
        start=now - timedelta(seconds=2),
        end=now,
    )

    IOLoop.current().spawn_callback(logger.log(watcher))
