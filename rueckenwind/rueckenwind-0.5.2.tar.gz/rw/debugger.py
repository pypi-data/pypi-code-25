# Copyright 2017 Florian Ludwig
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import, division, print_function, with_statement

import linecache
import weakref
import logging

from future.builtins import range
from tornado import util
import tornado.web

from rw import scope
from rw import gen
import rw.plugin
import rw.http
import rw.websocket

plugin = rw.plugin.Plugin(__name__)
LOG = logging.getLogger(__name__)
HANDLERS = []
TRACEBACKS = {}


class WebSocketHandler(rw.websocket.WebSocketHandler):
    @gen.coroutine
    def open(self):
        print('open')
        HANDLERS.append(weakref.ref(self))
        self.update_client()

    @gen.coroutine
    def on_message(self, message):
        print('on message')
        if message['type'] == 'get_tb':
            yield self.send_tb(message['id'])

    def update_client(self):
        return self.write_message({
            'type': 'update',
            'tbs': TRACEBACKS.keys(),
        })

    def send_tb(self, tb_id):
        return self.write_message({
            'type': 'tb',
            'tb': TRACEBACKS[tb_id]['data']
        })

    @gen.coroutine
    def on_close(self):
        HANDLERS.remove(weakref.ref(self))
        if not HANDLERS:
            LOG.debug('no more debugger online')
            while TRACEBACKS:
                TRACEBACKS.pop()

    def check_origin(self, origin):
        return origin == 'chrome-extension://opnmajfggcamecnphhpjkpdplggjnopj'


def tb_data(tb):
    frames = []
    result = {'stackFrames': frames}
    while tb:
        # format
        # https://github.com/Microsoft/vscode-debugadapter-node/blob/7fb3cf83dacbbb937c81448aabc06895a56a072a/protocol/src/debugProtocol.ts#L1197
        f = tb.tb_frame
        lineno = tb.tb_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        frames.append({
            'id': id(f),
            'filename': filename,
            'line': lineno,
            'name': name,
            'line': line,
            'presentationHint': 'normal',
        })
        tb = tb.tb_next
    return result


def handle_exception(handler, kwargs):
    if not handler._finished:
        kwargs['data'] = tb_data(kwargs['exc_info'][2])
        if HANDLERS:
            TRACEBACKS[id(kwargs)] = kwargs

        for handler_ref in HANDLERS[:]:
            handler = handler_ref()
            if handler:
                handler.update_client(kwargs)
            else:
                HANDLERS.remove(handler_ref)
        handler.finish('okay, lets start debugging')
    else:
        print('error')
        # TODO


@plugin.init
def init(scope):
    scope['rw.httpbase:handle_exception'] = handle_exception
