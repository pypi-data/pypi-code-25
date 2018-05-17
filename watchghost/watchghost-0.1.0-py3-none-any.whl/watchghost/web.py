# WatchGhost, your invisible but loud monitoring pet
# Copyright © 2015 Kozea

from tornado.web import RequestHandler, url
from tornado.websocket import WebSocketHandler

from . import app


class route(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, cls):
        app.add_handlers(r'.*$', (url(self.url, cls, name=cls.__name__),))
        return cls


@route(r'/')
class Index(RequestHandler):
    def get(self):
        return self.render('index.html', servers=app.servers)


@route(r'/watcher/(?P<watcher_uuid>[0-9a-f-]+)')
class Watcher(RequestHandler):
    def get(self, watcher_uuid):
        for watchers in app.watchers.values():
            for watcher in watchers:
                if watcher.uuid == watcher_uuid:
                    return self.render('watcher.html', watcher=watcher)
        return self.send_error(404)


@route(r'/watcher/check_now/(?P<watcher_uuid>[0-9a-f-]+)')
class CheckNow(RequestHandler):
    async def get(self, watcher_uuid):
        for watchers in app.watchers.values():
            for watcher in watchers:
                if watcher.uuid == watcher_uuid:
                    await watcher.check(replan=False)
                    return self.redirect(
                        self.reverse_url('Watcher', watcher_uuid))
        return self.send_error(404)


@route(r'/websocket')
class WebSocket(WebSocketHandler):
    def open(self):
        app.websockets.append(self)

    def on_close(self):
        app.websockets.remove(self)
