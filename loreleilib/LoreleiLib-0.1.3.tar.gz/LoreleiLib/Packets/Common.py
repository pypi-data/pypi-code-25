import cPickle


class Packet(object):

    def serialize(self):
        return cPickle.dumps(self)


class PacketResult(Packet):

    def __init__(self, success, message=None):
        self.success = success
        if message is None and success is False:
            message = "Something went wrong"
        if message is None and success is True:
            message = ''
        self.message = message


class PacketSet(Packet):

    def __init__(self, packets):
        self.packets = packets


class PlayerQuitPacket(Packet):
    def __init__(self):
        super(PlayerQuitPacket, self)