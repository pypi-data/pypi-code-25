from LoreleiLib.Packets.Common import Packet
from enum import Enum


class MessageType(Enum):

    # Person messages
    Global = 0
    Region = 1
    Local = 2 # Room
    Whisper = 3

    # System messages
    Combat = 4
    System = 5


class ChatPacket(Packet): pass


# Client message sent packet
class MessageSent(ChatPacket):

    def __init__(self, type, message, target=None):
        super(MessageSent)
        self.type = type
        self.message = message
        self.target = target # Target player


class MessageRecieved(ChatPacket):

    def __init__(self, type, message, sender=None, target=None):
        self.type = type
        self.message = message
        self.sender = sender
        self.target = target

    def __str__(self):
        if self.type in [MessageType.Combat, MessageType.System]:
            return "[{}] : {}".format(self.type.name, self.message)
        elif self.type in [MessageType.Whisper]:
            return "[{}] >> {}".format(self.sender, self.message)
        else:
            return "[{}] : {}".format(self.sender, self.message)