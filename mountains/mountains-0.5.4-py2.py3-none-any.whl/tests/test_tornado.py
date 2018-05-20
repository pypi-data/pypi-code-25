# -*- coding: utf-8 -*-
# created by restran on 2018/04/27
from __future__ import unicode_literals, absolute_import
import logging
import unittest
from tornado.gen import coroutine
from tornado import ioloop
from mountains.tornado import async_request

logger = logging.getLogger(__name__)


@coroutine
def main():
    url = 'http://127.0.0.1:8001'
    yield async_request('GET', url)


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
