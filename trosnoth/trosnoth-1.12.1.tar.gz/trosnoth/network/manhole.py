# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2013 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import __builtin__
import os
import random
import logging

from rlcompleter import Completer

from twisted.conch import manhole
from twisted.conch import manhole_ssh
from twisted.conch.error import ConchError
from twisted.conch.ssh import keys
from twisted.cred import portal, checkers
from trosnoth.data import getPath, user
from twisted.internet import reactor
from twisted.internet.error import CannotListenError

from trosnoth.utils.twist import WeakCallLater


log = logging.getLogger(__name__)


class Manhole(manhole.ColoredManhole):

    tabCount = 0

    def sayHello(self):
        self.terminal.reset()
        self.terminal.write("\x1b[97mWelcome to \x1b[36mTrosnoth!\x1b[97m")
        self.terminal.nextLine()
        helper = self.namespace.get('helper')
        if helper:
            for line in helper.getBanner():
                self.terminal.write(line)
                self.terminal.nextLine()
        self.terminal.write('>>> ')

    def connectionMade(self):
        super(Manhole, self).connectionMade()
        WeakCallLater(0.1, self, 'sayHello')

    def keystrokeReceived(self, keyID, modifier):
        super(Manhole, self).keystrokeReceived(keyID, modifier)
        self.tabCount += 1 if keyID == "\t" else 0

    def handle_TAB(self):
        text = "".join(self.lineBuffer).split(' ')[-1]
        if len(text) == 0:
            # Bell character
            self.terminal.write("\a")
            return

        completer = Completer(self.namespace)

        if completer.complete(text, 0):
            allMatches = list(set(completer.matches))

            # Get rid of a bunch of cruft
            builtins = __builtin__.keys()
            matches = [x for x in allMatches
                       if x.strip('(') not in builtins and "__" not in x]
            matches.sort()

            # If there are no matches, ring the terminal bell
            # If there's only one match, autocomplete it
            # If there's more than one match, print a list of matches
            if len(matches) == 0:
                self.terminal.write("\a")
                return
            elif len(matches) == 1:
                length = len(text)
                self.lineBuffer = self.lineBuffer[:-length]
                self.lineBuffer.extend(matches[0])
                self.lineBufferIndex = len(self.lineBuffer)
            else:
                # Remove text before the last dot, for brevity
                if "." in matches[0]:
                    matches = [x[x.rfind(".") + 1:] for x in matches]
                self.terminal.nextLine()
                self.terminal.write(repr(matches))
                self.terminal.nextLine()
                self.terminal.write("%s%s" % (self.ps[self.pn], ""))

            self.terminal.eraseLine()
            self.terminal.cursorBackward(self.lineBufferIndex + 5)
            self.terminal.write(
                "%s%s" % (self.ps[self.pn], "".join(self.lineBuffer)))

        else:
            self.terminal.write("\a")


def getManholeFactory(namespace, password):
    realm = manhole_ssh.TerminalRealm()

    # If we don't do this, the server will generate an exception when
    # you resize the SSH window
    def windowChanged(self, size):
        pass

    realm.sessionFactory.windowChanged = windowChanged

    def getManhole(_):
        return Manhole(namespace)

    realm.chainedProtocolFactory.protocolFactory = getManhole
    p = portal.Portal(realm)

    # Username/Password authentication
    passwordDB = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    passwordDB.addUser('trosnoth', password)
    p.registerChecker(passwordDB)

    factory = manhole_ssh.ConchFactory(p)

    privatePath = getPath(user, 'authserver', 'manhole_rsa')
    if os.path.isfile(privatePath):
        factory.privateKeys[b'ssh-rsa'] = keys.Key.fromFile(privatePath)
    publicPath = privatePath + '.pub'
    if os.path.isfile(publicPath):
        factory.publicKeys[b'ssh-rsa'] = keys.Key.fromFile(publicPath)

    return factory


def startManhole(port, namespace, password=None):
    if password is None:
        password = ''.join(random.choice('0123456789') for i in range(6))

    factory = getManholeFactory(namespace, password)

    try:
        listeningPort = reactor.listenTCP(port, factory)
    except CannotListenError:
        log.error('Error starting manhole on port %d', port)
    except ConchError as e:
        log.error('Error starting manhole on port %d: %s', port, e.value)
    else:
        port = listeningPort.getHost().port
        log.warning(
            'SSH manhole started on port %d with password %r',
            port, password)