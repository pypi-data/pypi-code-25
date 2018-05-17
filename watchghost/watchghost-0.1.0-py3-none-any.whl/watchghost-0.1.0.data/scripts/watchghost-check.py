#!python

# WatchGhost check : check a single service against a server
# Copyright © 2015 Hashbang

import logging
import os

from tornado.ioloop import IOLoop
from tornado.options import (
    define,
    options,
    parse_command_line,
    parse_config_file
)
from tornado.platform.asyncio import AsyncIOMainLoop
from watchghost import app, config

AsyncIOMainLoop().install()

define('hostname', type=str, help="the hostname to check")
define('watcher', type=str, help="the watcher to use")


if __name__ == '__main__':
    parse_command_line()
else:
    parse_config_file(
        os.environ.get('WATCHGHOST_CONFIG', '/etc/watchghost.conf')
    )

log = logging.getLogger('watchghost')
log.setLevel(logging.DEBUG if options.debug else logging.ERROR)

config.read()

if __name__ == '__main__':
    watchers = app.watchers[options.watcher]
    for watcher in watchers:
        if watcher.server.name == options.hostname:
            IOLoop.current().run_sync(watcher.check)
