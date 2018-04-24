from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.internet.task import LoopingCall
from LoreleiClient.UI import UI
from LoreleiClient.Views.Login import LoginView
from LoreleiClient.Views.CharacterCreation import CharacterCreationView
from LoreleiLib.Packets.Common import Packet, PacketSet
from LoreleiLib.Packets.View import ViewPacket, ViewType
import cPickle
import pygame
pygame.init()

ui = UI()


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
                self.handlePacket(packet)
        else:
            self.handlePacket(data)

    def handlePacket(self, packet):
        if isinstance(packet, ViewPacket):
            if packet.viewType == ViewType.Login:
                ui.setView(LoginView())
            if packet.viewType == ViewType.CharacterCreation:
                ui.setView(CharacterCreationView())
        else:
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
            print 'Lost connection.  Reason:', reason
            print 'Retrying connectiong...'
            connector.connect()
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
        if err != "display Surface quit":
            print "REACTOR RUN FAILURE", err

if __name__ == "__main__":
    main()