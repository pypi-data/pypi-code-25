import datetime
import functools
import json
import uuid
from hashlib import sha1
import logging
import os
import pickle
import random
import sys

from django.contrib.auth import authenticate
from django.core import management
from twisted.internet import reactor, defer
from twisted.internet.error import CannotListenError, ConnectError
from twisted.internet.protocol import (
    Factory, ClientCreator, Protocol, ProcessProtocol,
)
from twisted.protocols import amp
from twisted.python.failure import Failure

from trosnoth import data, dbqueue, rsa, murmur
from trosnoth.data import getPath, makeDirs, user
from trosnoth.djangoapp.models import (
    User, TrosnothUser, TrosnothServerSettings,
    TrosnothArena,
)
from trosnoth.network import authcommands
from trosnoth.network.manhole import startManhole
from trosnoth.network.networkDefines import serverVersion
from trosnoth.server import arenaamp
from trosnoth.settings import AuthServerSettings
from trosnoth.utils.event import Event
from trosnoth.utils.utils import timeNow, initLogging

log = logging.getLogger('authserver')

MAX_GAMES = 1
GAME_KIND = 'Trosnoth1'

GAME_VERIFY_TIME = 60


class AuthenticationProtocol(amp.AMP):
    '''
    Trosnoth authentication server which is used when running a game server
    which keeps track of users.
    '''

    def connectionMade(self):
        super(AuthenticationProtocol, self).connectionMade()
        self.user = None
        self.token = None
        log.info('New connection.')

    def connectionLost(self, reason):
        log.info('Connection lost.')

    @authcommands.GetPublicKey.responder
    def getPublicKey(self):
        return {
            'e': self.factory.pubKey['e'],
            'n': self.factory.pubKey['n'],
        }

    @authcommands.ListGames.responder
    def listGames(self):
        result = {
            'games': [{
                'id': arena.id,
                'game': GAME_KIND,
                'version': serverVersion,
                'name': arena.name,
            } for arena in TrosnothArena.objects.all() if arena.enabled]
        }
        return result

    @authcommands.ListOtherGames.responder
    def listOtherGames(self):
        d = self.factory.getRegisteredGames()

        @d.addCallback
        def gotGames(rGames):
            result = []
            for rGame in rGames:
                result.append({
                    'game': rGame.game,
                    'version': rGame.version,
                    'ip': rGame.host,
                    'port': rGame.port,
                })
            return {
                'games': result,
            }
        return d

    @authcommands.RegisterGame.responder
    def registerGame(self, game, version, port):
        host = self.transport.getPeer().host
        self.factory.registerGame(game, version, host, port)
        return {}

    @authcommands.CreateGame.responder
    def createGame(self, game):
        raise authcommands.CannotCreateGame()

    @authcommands.ConnectToGame.responder
    @defer.inlineCallbacks
    def connectToGame(self, id):
        if self.user is None:
            raise authcommands.NotAuthenticated()

        try:
            arenaProxy = yield self.factory.getArena(id, start=True)
        except (TrosnothArena.DoesNotExist, GameIsDisabled):
            raise authcommands.GameDoesNotExist()

        authTag = random.randrange(2**64)
        yield arenaProxy.amp.callRemote(
            arenaamp.RegisterAuthTag,
            username=self.user.username, authTag=authTag)
        nick = self.user.getNick()

        defer.returnValue({
            'port': arenaProxy.port,
            'authTag': authTag,
            'nick': nick,
        })

    @authcommands.GetSupportedSettings.responder
    def getSupportedSettings(self):
        settings = ['password']
        return {
            'result': settings,
        }

    @authcommands.SetPassword.responder
    def setUserPassword(self, password):
        if self.user is None:
            raise authcommands.NotAuthenticated()
        password = self._decodePassword(password)
        self.user.setPassword(password)
        return {}

    @authcommands.GetAuthToken.responder
    def getAuthToken(self):
        self.token = ''.join(str(random.randrange(256)) for i in range(16))
        return {
            'token': self.token
        }

    @authcommands.PasswordAuthenticate.responder
    def passwordAuthenticate(self, username, password):
        username = username.lower()
        password = self._decodePassword(password)
        if password is None:
            return {'result': False}    # Bad auth token used.

        d = self.factory.authManager.authenticateUser(username, password)

        @d.addCallback
        def authSucceeded(user):
            self.user = user
            return {'result': True}

        @d.addErrback
        def authFailed(failure):
            return {'result': False}

        return d

    @authcommands.CreateUserWithPassword.responder
    def createUserWithPassword(self, username, password):
        if self.factory.settings.allowNewUsers:
            nick = username
            username = username.lower()
            password = self._decodePassword(password)
            if password is None:
                return {'result': 'Authentication token failure.'}

            authMan = self.factory.authManager
            if authMan.checkUsername(username):
                return {'result': 'That username is taken.'}
            self.user = authMan.createUser(username, password, nick)
        else:
            return {'result': self.factory.settings.privateMsg}
        return {'result': ''}

    def _decodePassword(self, password):
        if self.token is None:
            return None
        token, self.token = self.token, None
        passwordData = rsa.decrypt(password, self.factory.privKey)
        if passwordData[:len(token)] != token:
            return None
        return passwordData[len(token):]

SALT = 'Trosnoth'


class AuthManager(object):
    '''
    Manages user accounts on the system.
    '''

    def __init__(self, dataPath):
        self.dataPath = dataPath
        self.tags = {}      # auth tag -> user id
        self.settings = AuthServerSettings(dataPath)

    def checkUsername(self, username):
        '''
        Returns True or False, depending on whether the given username is
        already in use.
        '''
        try:
            TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            return False
        return True

    def authenticateUser(self, username, password):
        '''
        If a username exists with the given password, returns the user,
        otherwise returns None.
        '''
        username = username.lower()
        try:
            trosnothUser = TrosnothUser.fromUser(username=username)
        except User.DoesNotExist:
            return defer.fail()

        if not trosnothUser.oldPasswordHash:
            # Just use Django auth
            djangoUser = authenticate(username=username, password=password)
            if djangoUser is None:
                return defer.fail(ValueError('Authentication failed'))
            if not djangoUser.is_active:
                return defer.fail(ValueError('User deactivated'))
            user = AuthenticatedUser(self, username)
        else:
            # Old Trosnoth auth, only exists for backward compatibility
            hash1 = sha1(SALT + password).digest()
            hash2 = bytes(trosnothUser.oldPasswordHash)
            if hash1 != hash2:
                return defer.fail(ValueError('Incorrect password'))

            # Put the password into Django
            trosnothUser.user.set_password(password)
            trosnothUser.user.save()
            trosnothUser.oldPasswordHash = ''
            trosnothUser.save()

            user = AuthenticatedUser(self, username)

        user.seen()
        return defer.succeed(user)

    def createUser(self, username, password, nick=None):
        username = username.lower()
        if self.checkUsername(username):
            raise ValueError('user %r already exists' % (username,))
        User.objects.create_user(username, password=password)

        user = AuthenticatedUser(self, username)
        user.setPassword(password)
        user.seen()
        if nick is not None:
            user.setNick(nick)
        return user

    def getNick(self, username):
        return TrosnothUser.fromUser(username=username).nick


class AuthenticationFactory(Factory):
    protocol = AuthenticationProtocol
    authManagerClass = AuthManager
    instance = None

    def __init__(self, dataPath=None, manholePassword=None):
        if dataPath is None:
            dataPath = getPath(data.user, 'authserver')
        makeDirs(dataPath)
        self.dataPath = dataPath
        self.manholePassword=None

        self.authManager = self.authManagerClass(dataPath)
        self.pubKey, self.privKey = self.loadKeys()
        self.registeredGames = []
        self.arenaProxies = {}
        self.arenaAMPListener = None

        self.onArenaStarting = Event(['proxy'])
        self.onArenaStopped = Event(['proxy'])

        AuthenticationFactory.instance = self

    @property
    def settings(self):
        return self.authManager.settings

    def loadKeys(self):
        '''
        Loads public and private keys from disk or creates them and saves them.
        '''
        keyPath = os.path.join(self.dataPath, 'keys')
        try:
            pub, priv = pickle.load(open(keyPath, 'rb'))
        except IOError:
            pub, priv = rsa.newkeys(self.settings.keyLength)
            pickle.dump((pub, priv), open(keyPath, 'wb'), 2)

        return pub, priv

    @defer.inlineCallbacks
    def registerGame(self, game, version, host, port):
        '''
        Registers a remote game with this server.
        '''
        settings = TrosnothServerSettings.get()
        if not settings.allowRemoteGameRegistration:
            return

        rGame = RegisteredGame(game, version, host, port)
        result = yield rGame.verify()
        if result:
            log.info('Registered game on %s:%s', host, port)
            self.registeredGames.append(rGame)
        else:
            log.info('Failed to connect to game on %s:%s', host, port)
            raise authcommands.PortUnreachable()

    def getRegisteredGames(self):
        '''
        Returns a list of registered games which are running.
        '''
        if len(self.registeredGames) == 0:
            return defer.succeed([])

        result = []
        d = defer.Deferred()
        remaining = [len(self.registeredGames)]

        def gameVerified(success, rGame):
            if success:
                result.append(rGame)
            else:
                self.registeredGames.remove(rGame)

            remaining[0] -= 1
            if remaining[0] == 0:
                d.callback(result)

        for rGame in self.registeredGames:
            rGame.verify().addCallback(gameVerified, rGame)

        return d

    @defer.inlineCallbacks
    def getArena(self, arenaId, start=False):
        if not isinstance(arenaId, int):
            raise TypeError(
                'Expected numeric arenaId, not {!r}'.format(arenaId))
        try:
            result = self.arenaProxies[arenaId]
        except KeyError:
            if not start:
                raise
            result = ArenaProcessProtocol(
                arenaId, token=self.getNewArenaToken(),
            )
            if not result.processDied:
                self.arenaProxies[arenaId] = result
                result.onExit.addListener(self._arenaExited)
                self.onArenaStarting(result)
            log.error('Starting arena #%s', arenaId)
            yield result.start(self.getArenaAMPPort(), self.manholePassword)
        else:
            if not result.ready:
                yield result.onReady.waitOrRaise()
        defer.returnValue(result)

    def _arenaExited(self, proxy, reason):
        log.error('Arena #%s exited', proxy.arenaId)
        if self.arenaProxies.get(proxy.arenaId):
            del self.arenaProxies[proxy.arenaId]
            self.onArenaStopped(proxy)
        proxy.onExit.removeListener(self._arenaExited)

    @defer.inlineCallbacks
    def teardown(self):
        # Give a fraction of a second for the message to get through
        # the the children have ended, then send a kill signal.
        d = defer.Deferred()
        reactor.callLater(0.1, d.callback, None)
        yield d

        yield defer.DeferredList([
            p.killProcess() for p in self.arenaProxies.values()])

    def getNewArenaToken(self):
        if self.arenaAMPListener is None or \
                self.arenaAMPListener.disconnecting:
            self.startArenaAMPListener()
        return uuid.uuid4().hex

    def matchArenaToken(self, ampProtocol, token):
        for arenaProxy in self.arenaProxies.values():
            if arenaProxy.token and arenaProxy.token == token:
                ampProtocol.arena = arenaProxy
                arenaProxy.matchedToken(ampProtocol)
                if not any(p.token for p in self.arenaProxies.values()):
                    self.stopArenaAMPListener()
                return True
        return False

    def getArenaAMPPort(self):
        return self.arenaAMPListener.getHost().port

    def startArenaAMPListener(self, port=0, interface='127.0.0.1'):
        factory = Factory.forProtocol(ArenaAMPProtocol)
        factory.authFactory = self
        self.arenaAMPListener = reactor.listenTCP(
            port, factory, interface=interface)
        factory.stopFactory = functools.partial(
            self._arenaAMPFactoryStopped, self.arenaAMPListener)

    def stopArenaAMPListener(self):
        if self.arenaAMPListener and not self.arenaAMPListener.disconnecting:
            self.arenaAMPListener.stopListening()

    def _arenaAMPFactoryStopped(self, listener):
        if listener == self.arenaAMPListener:
            self.arenaAMPListener = None

    @defer.inlineCallbacks
    def sendArenaRequest(self, arenaId, request, **kwargs):
        arena = yield self.getArena(arenaId)
        result = yield arena.amp.callRemote(request, **kwargs)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def shutDownArena(self, arenaId):
        arena = yield self.getArena(arenaId)
        yield arena.killProcess()

    @defer.inlineCallbacks
    def getArenaInfo(self, arenaId):
        try:
            arena = yield self.getArena(arenaId)
        except KeyError:
            arenaRecord = TrosnothArena.objects.get(id=arenaId)
            if not arenaRecord.enabled:
                status = 'DISABLED'
            else:
                status = 'not running'

            defer.returnValue({
                'status': status,
                'paused': False,
                'players': 0,
                'blue': {'shots': True, 'caps': True},
                'red': {'shots': True, 'caps': True},
            })

        defer.returnValue({
            'status': arena.status,
            'paused': arena.paused,
            'players': arena.players,
            'blue': arena.teamInfo[0],
            'red': arena.teamInfo[1],
        })


class GameIsDisabled(Exception):
    pass


class ArenaProcessProtocol(ProcessProtocol):
    def __init__(self, arenaId, token):
        self.arenaId = arenaId
        self.token = token
        self.amp = None
        self.port = None
        self.processDied = False
        self.startCalled = False
        self.ready = False
        self.onReady = Event(['result'])
        self.onExit = Event(['protocol', 'reason'])
        self.onInfoChanged = Event(['proxy'])

        self.status = 'starting up...'
        self.players = 0
        self.paused = False
        self.teamInfo = [
            {'shots': True, 'caps': True},
            {'shots': True, 'caps': True},
        ]

    def start(self, ampPort, manholePassword=None):
        if self.startCalled:
            raise RuntimeError('Cannot start ArenaProcessProtocol twice')
        self.startCalled = True
        result = self.onReady.waitOrRaise()

        arenaRecord = TrosnothArena.objects.get(id=self.arenaId)
        if not arenaRecord.enabled:
            raise GameIsDisabled('This arena is disabled')
        self.port = arenaRecord.gamePort

        cmd = self.getArenaCommand() + [str(self.arenaId), str(ampPort),
            '--profile']
        if manholePassword:
            cmd.extend(['--password', manholePassword])
        reactor.spawnProcess(
            self, cmd[0], cmd, env=None, childFDs={0: 'w', 1: 1, 2: 2})
        return result

    def setInfo(self, status=None, players=None, paused=None):
        if status is not None:
            self.status = status
        if players is not None:
            self.players = players
        if paused is not None:
            self.paused = paused
        self.onInfoChanged(self)

    @defer.inlineCallbacks
    def setTeamAbility(self, teamIndex, ability, value):
        yield self.amp.callRemote(
            arenaamp.SetTeamAbility,
            teamIndex=teamIndex, ability=ability,
            valueJSON=json.dumps(value))
        abilityKey = {
            'aggression': 'shots',
            'zoneCaps': 'caps'
        }.get(ability)
        if abilityKey:
            self.teamInfo[teamIndex][abilityKey] = value

    @staticmethod
    def getArenaCommand():
        # TODO: make this work under py2exe on windows
        import trosnoth.server
        path = os.path.dirname(trosnoth.server.__file__)
        return [sys.executable, os.path.join(path, 'arena.py')]

    def matchedToken(self, ampProtocol):
        if self.processDied:
            return
        self.token = None
        self.amp = ampProtocol
        self.ready = True
        self.onReady(None)

    @defer.inlineCallbacks
    def connectionMade(self):
        self.processDied = False
        self.ready = False
        self.transport.write(self.token + '\n')

        for i in range(30):
            d = defer.Deferred()
            reactor.callLater(0.5, d.callback, None)
            yield d

            if self.ready:
                return
            if self.processDied:
                break

        self.killProcess()

        self.onReady(Failure(
            RuntimeError('Child process did not complete initialisation')))

    @defer.inlineCallbacks
    def killProcess(self):
        try:
            if self.processDied:
                return

            self.transport.signalProcess('TERM')

            for i in range(3):
                d = defer.Deferred()
                reactor.callLater(1, d.callback, None)
                yield d
                if self.processDied:
                    return

            self.transport.signalProcess('KILL')
        except Exception:
            log.exception('Error while killing child process')

    def ampConnectionLost(self):
        if not self.processDied:
            log.warning('Lost AMP connection to arena #%s', self.arenaId)
            self.killProcess()

    def processExited(self, reason):
        self.processDied = True
        self.onExit(self, reason)


class ArenaAMPProtocol(amp.AMP):
    '''
    Local AMP connection from Arena process.
    '''
    arena = None

    def connectionMade(self):
        super(ArenaAMPProtocol, self).connectionMade()
        self.authFactory = self.factory.authFactory

    def connectionLost(self, reason):
        if self.arena:
            self.arena.ampConnectionLost()

    def locateResponder(self, name):
        '''
        Overriden to refuse all commands that arrive before ArenaListening.
        '''
        if self.arena is not None:
            # Pass through to super from now on.
            self.locateResponder = super(ArenaAMPProtocol, self).locateResponder
            return self.locateResponder(name)
        if name == 'ArenaListening':
            return super(ArenaAMPProtocol, self).locateResponder(name)
        return self.notYetListening

    def notYetListening(self, *args, **kwargs):
        raise arenaamp.NotYetListening()

    @arenaamp.ArenaListening.responder
    def arenaListening(self, token):
        if self.arena:
            raise arenaamp.AlreadyCalled()
        if not self.authFactory.matchArenaToken(self, token):
            self.transport.loseConnection()
        return {}

    @arenaamp.SetArenaInfo.responder
    def setArenaInfo(self, status=None, players=None, paused=None):
        self.arena.setInfo(status, players, paused)
        return {}


class RegisteredGame(object):
    '''
    Represents a remote game that has been registered with this server.
    '''

    def __init__(self, game, version, host, port):
        self.game = game
        self.version = version
        self.host = host
        self.port = port
        self.lastVerified = 0
        self.running = True

    @defer.inlineCallbacks
    def verify(self):
        '''
        If more than GAME_VERIFY_TIME has passed since the last verification,
        connects to the game to check whether it is still running. Returns a
        deferred whose callback will be executed with True or False depending
        on whether the game is still running.
        '''
        t = timeNow()
        if t - self.lastVerified < GAME_VERIFY_TIME:
            defer.returnValue(self.running)
            return
        self.lastVerified = t

        try:
            yield ClientCreator(reactor, Protocol).connectTCP(
                self.host, self.port, timeout=5)
        except ConnectError:
            self.running = False
            defer.returnValue(False)
            return

        self.running = True
        defer.returnValue(True)


class AuthenticatedUser(object):
    '''
    Represents a user which has been authenticated on the system.
    '''

    def __init__(self, authManager, username):
        self.authManager = authManager
        self.username = username = username.lower()

    def __eq__(self, other):
        if (isinstance(other, AuthenticatedUser) and other.username ==
                self.username):
            return True
        return False

    def __hash__(self):
        return hash(self.username)

    def getNick(self):
        return TrosnothUser.fromUser(username=self.username).nick

    def setNick(self, nick):
        @dbqueue.add
        def writeNickToDB():
            user = TrosnothUser.fromUser(username=self.username)
            if nick != user.nick:
                user.nick = nick
                user.save()

    def setPassword(self, password):
        # Don't put DB write in a queue as user will expect it to take place
        # immediately.
        user = User.objects.get(username=self.username)
        user.set_password(password)
        user.save()
        trosnothUser = TrosnothUser.fromUser(pk=user.pk)
        trosnothUser.oldPasswordHash = ''
        trosnothUser.save()

    def seen(self):
        now = datetime.datetime.now()
        @dbqueue.add
        def writeSeenTimeToDB():
            user = TrosnothUser.fromUser(username=self.username)
            user.lastSeen = now
            user.save()


def startServer(
        port=6787, dataPath=None, manholePort=6799, password=None,
        webPort=None):

    # Ensure that the authserver directories exist
    authDir = getPath(user, 'authserver', 'accounts')
    makeDirs(authDir)

    # Ensure that any database migrations have happened
    management.call_command('migrate')

    # If murmur communication is enabled, try to connect
    if murmur.init() == 'initialised':
        reactor.addSystemEventTrigger(
            'before', 'shutdown', murmur.tearDownRooms)

    dbqueue.init()

    pf = AuthenticationFactory(dataPath, password)


    namespace = {}
    namespace['authFactory'] = pf
    startManhole(manholePort, namespace, password)

    if webPort is not None:
        from trosnoth.web.server import startWebServer
        startWebServer(pf, webPort)

    try:
        reactor.listenTCP(port, pf)
    except CannotListenError:
        log.error('Error listening on port %d.', port)
    else:
        log.info(
            'Started Trosnoth authentication server on port %d.', port)
        reactor.addSystemEventTrigger('before', 'shutdown', pf.teardown)
        reactor.run()


def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        '-p', '--port', action='store', dest='port', default=6787,
        help='which port to run the authentication server on')
    parser.add_option(
        '-D', '--datapath', action='store', dest='dataPath', default=None,
        help='where to store the authentication server data')
    parser.add_option(
        '-m', '--manhole', action='store', dest='manholePort',
        default=6799, help='which port to run the manhole on')
    parser.add_option(
        '--password', action='store', dest='manholePassword', default=None,
        help='the password to use for the manhole')
    parser.add_option(
        '-w', '--webport', action='store', dest='webPort', default='8080',
        help='the port on which to launch the web service. '
        'Default is 8080. To disable web service, use --webport= with no '
        'parameter.')
    parser.add_option(
        '-d', '--debug', action='store_true', dest='debug',
        help='show debug-level messages on console')
    parser.add_option(
        '-l', '--log-file', action='store', dest='logFile',
        help='file to write logs to')
    parser.add_option(
        '--profile', action='store_true', dest='profile',
        help='dump kcachegrind profiling data to trosnoth.log')

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error('no arguments expected')

    initLogging(options.debug, options.logFile)

    if not options.webPort:
        webPort = None
    else:
        try:
            webPort = int(options.webPort)
        except ValueError:
            options.error('Invalid port: %r' % (options.webPort,))

    kwargs = dict(
        port=int(options.port), dataPath=options.dataPath,
        manholePort=int(options.manholePort),
        password=options.manholePassword, webPort=webPort,
    )

    if options.profile:
        runWithProfiling(**kwargs)
    else:
        startServer(**kwargs)


def runWithProfiling(**kwargs):
    import cProfile
    from trosnoth.utils.profiling import KCacheGrindOutputter
    prof = cProfile.Profile()

    try:
        prof.runcall(startServer, **kwargs)
    except SystemExit:
        pass
    finally:
        kg = KCacheGrindOutputter(prof)
        with open('server.log', 'wb') as f:
            kg.output(f)



if __name__ == '__main__':
    main()
