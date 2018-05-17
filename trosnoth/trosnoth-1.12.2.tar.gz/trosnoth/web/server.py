import json
import logging
import mimetypes

from django.contrib.staticfiles import finders
from twisted.internet import defer, reactor
from twisted.web import resource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource

from trosnoth.djangoapp.models import TrosnothArena
from trosnoth.server.wsgi import application
from trosnoth.utils.twist import WeakLoopingCall
from trosnoth.web.site import PageSet, ServerState, Resources


log = logging.getLogger(__name__)

pages = PageSet()


@pages.addPage('homepipe')
@defer.inlineCallbacks
def homepipe(state, request):
    sendData = yield state.getInitialEvents()
    request.write(sendData)
    while True:
        s = yield state.waitForEvent()
        if s is not None:
            request.write(s)


class WebServer(ServerState):
    instance = None

    def __init__(self, authFactory, serverPort):
        ServerState.__init__(self, pages)
        self.authFactory = authFactory
        self.serverPort = serverPort
        self.nextEventListeners = []
        self._loop = WeakLoopingCall(self, 'keepEventPipeAlive')
        self._loop.start(5, False)

        for arenaProxy in authFactory.arenaProxies.values():
            self.arenaStarting(arenaProxy)
        authFactory.onArenaStarting.addListener(self.arenaStarting)
        authFactory.onArenaStopped.addListener(self.arenaStopped)

        WebServer.instance = self

    @defer.inlineCallbacks
    def getInitialEvents(self):
        bits = []
        for arena in TrosnothArena.objects.all():
            players = 0
            paused = False
            if arena.enabled:
                try:
                    arenaProxy = yield self.authFactory.getArena(arena.id)
                except KeyError:
                    status = 'not yet started'
                else:
                    status = arenaProxy.status
                    players = arenaProxy.players
                    paused = arenaProxy.paused
            else:
                status = 'disabled'

            bits.append('arena({}, {}, {}, {});'.format(
                json.dumps(arena.id),
                json.dumps(status),
                json.dumps(players),
                json.dumps(paused),
            ))
        defer.returnValue('\n'.join(bits) + '\n')

    def waitForEvent(self):
        d = defer.Deferred()
        self.nextEventListeners.append(d)
        return d

    def transmitEvent(self, jsCommand):
        listeners = self.nextEventListeners
        self.nextEventListeners = []
        for d in listeners:
            d.callback(jsCommand + '\n')

    def keepEventPipeAlive(self):
        '''
        To make sure that a reverse proxy doesn't close connections due to
        inactivity.
        '''
        self.transmitEvent('')

    def arenaStarting(self, arenaProxy):
        arenaProxy.onInfoChanged.addListener(self.arenaInfoChanged)
        self.arenaInfoChanged(arenaProxy)

    def arenaStopped(self, arenaProxy):
        arenaProxy.onInfoChanged.removeListener(self.arenaInfoChanged)

    def arenaInfoChanged(self, arenaProxy):
        self.transmitEvent('arena({}, {}, {}, {});'.format(
            json.dumps(arenaProxy.arenaId),
            json.dumps(arenaProxy.status),
            json.dumps(arenaProxy.players),
            json.dumps(arenaProxy.paused),
        ))


class WSGIRoot(resource.Resource):
    def __init__(self, wsgi, *args, **kwargs):
        resource.Resource.__init__(self)
        self.wsgi = wsgi

    def getChild(self, child, request):
        request.prepath.pop()
        request.postpath.insert(0, child)
        return self.wsgi

    def render(self, request):
        return self.wsgi.render(request)


class DjangoStatic(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        localPath = finders.find('/'.join(request.postpath))
        if not localPath:
            return File.childNotFound.render(request)

        return File(localPath).render_GET(request)


def startWebServer(authFactory, port):
    mimetypes.types_map.update({
        '.trosrepl': 'application/octet-stream',
    })

    root = WSGIRoot(
        WSGIResource(reactor, reactor.getThreadPool(), application))
    root.putChild('static', DjangoStatic())
    root.putChild('poll', Resources(WebServer(authFactory, None)))
    factory = Site(root)
    reactor.listenTCP(port, factory)
