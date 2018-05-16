# -*- coding: utf-8 -*-

__version__ = '0.2.1'

import re
import sys
import logging
import logging.config

from supervisor import childutils


logger = logging.getLogger('svdog')


class SVDog(object):
    excludes = None

    def __init__(self, config=None):
        if hasattr(config, 'LOGGING'):
            logging.config.dictConfig(config.LOGGING)

        self.excludes = getattr(config, 'EXCLUDES', None)

        self.stdin = sys.stdin
        self.stdout = sys.stdout

    def run(self):
        logger.info('running')

        while True:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)

            if not payload.endswith('\n'):
                payload = payload + '\n'

            pheaders, pdata = childutils.eventdata(payload)

            process_name = pheaders.get('processname')

            if process_name and self.excludes and list(filter(lambda x: re.match(x, process_name), self.excludes)):
                childutils.listener.ok(self.stdout)
                continue

            logger.error('%s\n%s', headers, payload)
            childutils.listener.ok(self.stdout)
