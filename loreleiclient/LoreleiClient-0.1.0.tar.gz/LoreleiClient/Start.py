from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.internet.task import LoopingCall
from LoreleiClient.UI import UI
from LoreleiLib.Packets.Common import Packet, PacketSet
import cPickle
import pygame
pygame.init()

ui = UI(reactor.stop)


def ui_tick():
    if not ui.game_tick():
        reactor.stop()


class Connection:

    def __init__(self, transport):
        self.transport = transport

    def sendLine(self, line):
        if isinstance(line, Packet):
            line = line.serialize()
        self.transport.write(line)


class Listener(Protocol):

    def connectionMade(self):
        ui.set_connection(Connection(self.transport))

    def dataReceived(self, data):
        try:
            data = cPickle.loads(data)
        except Exception as err:
            print err

        print data

        if isinstance(data, PacketSet):
            for packet in data.packets:
                ui.handle_data(packet)
        else:
            ui.handle_data(data)


class ClientFactory(ReconnectingClientFactory):

    def buildProtocol(self, addr):
        self.resetDelay()
        return Listener()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)


def main():
    reactor.connectTCP("104.0.149.42", 8123, ClientFactory())

    tick = LoopingCall(ui_tick)
    tick.start(1.0 / ui.DESIRED_FPS)
    try:
        reactor.run()
    except Exception as err:
        print err

if __name__ == "__main__":
    main()