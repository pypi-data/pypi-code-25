from LoreleiLib.Packets.Common import Packet
from LoreleiLib.Map import MapTile, MapExitDescriptions, MapDirection
from LoreleiLib.Character import Character
from LoreleiLib.Objects import Creature, Item


class RoomPacket(Packet): pass


class RoomDetails(RoomPacket):

    def __init__(self, room):
        # type: (MapTile) -> None
        self.regionName = room.region.name # type: str
        self.description = room.description # type: str
        self.items = room.items # type: list<Item>
        self.players = room.players # type: list<Character>
        self.creatures = room.creatures # type: list<Creature>
        self.exitDetails = room.exitDetails # type: MapExitDescriptions


class RoomChange(RoomPacket):

    def __init__(self, direction):
        # type: (MapDirection) -> None
        self.direction = direction