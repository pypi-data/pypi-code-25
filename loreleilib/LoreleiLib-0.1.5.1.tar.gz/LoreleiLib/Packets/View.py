from LoreleiLib.Packets.Common import Packet
from enum import Enum


class ViewType(Enum):
    Login = 0
    CharacterCreation = 1


class ViewPacket(Packet):

    def __init__(self, viewType):
        # type: (ViewType) -> None
        self.viewType = viewType