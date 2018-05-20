#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by restran on 2015/12/21

from __future__ import unicode_literals, absolute_import

import logging
import signal
import time

import tornado
import tornado.web
from tornado import ioloop, httpserver
from tornado.escape import native_str
from tornado.options import define, options

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__file__)

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1

define('host', default='127.0.0.1', help='run on the given host', type=str)
define('port', default=8001, help='run on the given port', type=int)


class ResourceHandler(tornado.web.RequestHandler):
    def get(self):
        content_type = self.request.headers.get('Content-Type')
        if content_type:
            self.set_header('Content-Type', content_type)

        self.write('get')

    def post(self):
        content_type = self.request.headers.get('Content-Type')
        if content_type:
            self.set_header('Content-Type', content_type)

        self.write(self.request.body)

    def head(self):
        self.get()

    def options(self):
        self.get()

    def put(self):
        self.write('put')

    def delete(self):
        self.write('delete')


def sig_handler(sig, frame):
    logging.warning('caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    logging.info('stopping http server')
    server.stop()

    logging.info('will shutdown in %s seconds...', MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
    io_loop = tornado.ioloop.IOLoop.instance()

    deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logging.info('shutdown')

    stop_loop()


def main():
    options.parse_command_line()
    handlers = [
        (r'/?', ResourceHandler),
    ]
    app = tornado.web.Application(handlers=handlers, debug=True)
    options.logging = native_str('DEBUG')
    options.parse_command_line()
    global server
    server = httpserver.HTTPServer(app, xheaders=True)
    server.listen(options.port, options.host)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    logger.info('api server is running on %s:%s' % (options.host, options.port))
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
