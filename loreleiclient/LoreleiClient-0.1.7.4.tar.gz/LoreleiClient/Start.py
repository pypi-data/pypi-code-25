from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.internet.task import LoopingCall
from LoreleiClient.UI import UI
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.Packets.Common import Packet, PacketSet
import cPickle
import pygame


class Connection:

    def __init__(self, transport=None):
        self.transport = transport

    def sendLine(self, line):
        if self.transport is not None:
            if isinstance(line, Packet):
                line = line.serialize()
            self.transport.write(line)


class Listener(Protocol):

    def __init__(self):
        self.dataObject = ""

    def connectionMade(self):
        ui.set_connection(Connection(self.transport))

    def dataReceived(self, data):
        try:
            data = cPickle.loads(data)
        except Exception as err:
            self.dataObject += data
            try:
                data = cPickle.loads(self.dataObject)
                self.dataObject = ""
                # print "Unpickled Large Object"
            except Exception as err2:
                pass
                # print "Object not finished"

        if isinstance(data, PacketSet):
            for packet in data.packets:
                self.handlePacket(packet)
        else:
            self.handlePacket(data)

    def handlePacket(self, packet):
        ui.handle_data(packet)


class ClientFactory(ReconnectingClientFactory):

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.resetDelay()
        return Listener()

    def clientConnectionLost(self, connector, reason):
        if ui.running:
            ui.set_connection(None)
            connector.connect()
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)

    def stop(self):
        for user in ClientFactory.Users:
            user.transport.loseConnection()


pygame.init()
ui = UI(Connection())


def loadUp():
    ImageManager()
    pygame.display.set_icon(ImageManager.Images["icon"])


def ui_tick():
    if not ui.game_tick():
        reactor.stop()


def main():
    loadUp()
    reactor.connectTCP("104.0.149.42", 8123, ClientFactory())
    # reactor.connectTCP("localhost", 8123, ClientFactory())

    tick = LoopingCall(ui_tick)
    tick.start(1.0 / ui.DESIRED_FPS)
    try:
        reactor.run()
    except Exception as err:
        if err != "display Surface quit":
            print "REACTOR RUN FAILURE", err


if __name__ == "__main__":
    main()