#!/usr/bin/env python3

# WatchGhost, your invisible but loud monitoring pet
# Copyright © 2015 Kozea

import asyncio
import logging
import os

from tornado.options import options, parse_command_line, parse_config_file
from tornado.platform.asyncio import AsyncIOMainLoop
from utils import reload
from watchghost import app, config, web  # noqa

AsyncIOMainLoop().install()

if __name__ == '__main__':
    parse_command_line()
else:
    parse_config_file(
        os.environ.get('WATCHGHOST_CONFIG', '/etc/watchghost.conf'))

log = logging.getLogger('watchghost')
log.setLevel(logging.DEBUG if options.debug else logging.ERROR)

config.read()

if __name__ == '__main__':
    log.debug('Listening to http://%s:%i' % (options.host, options.port))
    app.listen(options.port)
    loop = asyncio.get_event_loop()
    if options.reload or options.debug:
        loop.run_until_complete(reload.start_file_watcher(options))
    loop.run_forever()
