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
    Raw = 6


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
        elif self.type == MessageType.Whisper:
            return "[{}] >> {}".format(self.sender, self.message)
        elif self.type == MessageType.Raw:
            return self.message
        else:
            return "[{}] : {}".format(self.sender, self.message)


class WhisperSearchPlayer(ChatPacket):

    def __init__(self, search):
        self.searchString = search


class WhisperSearchPlayerResult(ChatPacket):

    def __init__(self, username):
        self.username = username