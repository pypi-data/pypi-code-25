from watchghost.config import Server
from watchghost.loggers import Logger
from watchghost.services import Service
from watchghost.watchers import Watcher

from . import add_check_result


def test_logger_should_no_hard_info_at_startup():
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=False
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)


def test_logger_should_no_hard():
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=False
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    add_check_result(watcher, 'critical')
    assert logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'warning')
    assert logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)


def test_logger_should_log():
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=True
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    add_check_result(watcher, 'warning')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'warning')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'warning')
    assert logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert logger.should_log(watcher)


def test_logger_should_hard_info_at_startup():
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=False
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert watcher.is_first_hard
    assert not logger.should_log(watcher)


def test_logger_should_not_log_on_false_positive():
    """
    When there is a not hard failed status and then a hard info status, the
    logger should not report the hard info status
    """
    logger = Logger(dict(
        type='Console', status=['info', 'warning', 'critical'], only_hard=True
    ))
    server = Server('server', {})
    service = Service('network.Ping')
    watcher = Watcher(server, service, {}, [logger])

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert watcher.is_first_hard
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'critical')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)

    add_check_result(watcher, 'info')
    assert not logger.should_log(watcher)
