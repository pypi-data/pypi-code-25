from LoreleiLib.Objects import Item, Living, Entity
from LoreleiLib.Character import Character
from enum import Enum


class MapDirection(Enum):

    North = 1
    East = 2
    South = 3
    West = 4


class MapExitDescriptions():

    def __init__(self, northId=None, eastId=None, southId=None, westId=None, northDescription=None, eastDescription=None, southDescription=None, westDescription=None):
        self.exits = {MapDirection.North: northId, MapDirection.East: eastId,
                       MapDirection.South: southId, MapDirection.West: westId}
        self.descriptions = {MapDirection.North: northDescription, MapDirection.East: eastDescription,
                             MapDirection.South: southDescription, MapDirection.West: westDescription}


class MapRegion(object):

    def __init__(self, uuid, name, description, creatures=None, materials=None):
        self.uuid = uuid
        self.name = name
        self.description = description
        self.creatures = creatures
        self.materials = materials


class MapTile(object):

    def __init__(self, uuid, x, y, mapRegion, description, exitDetails):
        # type: (uuid, int, int, MapRegion, str, MapExitDescriptions) -> None
        self.uuid = uuid
        self.x = x # Where the tile is in its region
        self.y = y # Where the tile is in its region
        self.region = mapRegion # What map region the tile is in
        self.description = description # Description to send the player when they enter
        self.exitDetails = exitDetails # Exit descriptions and rooms
        self.creatures = [] # List of Living Entities in the room
        self.players = [] # List of Players in the room
        self.items = [] # List of ItemDrops in the room

    def addEntity(self, entity):
        # type: (Entity) -> None
        if isinstance(entity, Living):
            if isinstance(entity, Character):
                self.add_player(entity)
            else:
                self.creatures.append(entity)
        if isinstance(entity, Item):
            self.items.append(entity)

    def removeEntity(self, entity, killed):
        # type: (Entity, bool) -> None
        if isinstance(entity, Living):
            if isinstance(entity, Character):
                self.remove_player(entity)
            else:
                self.remove_creature(entity, killed)
        if isinstance(entity, Item):
            self.items.append(entity)

    def add_player(self, player):
        # type: (Character) -> None
        self.players.append(player)
        self.modify_player(player)

    def remove_player(self, player):
        # type: (Character) -> None
        self.players.remove(player)

    def add_creature(self, living):
        # type: (Living) -> None
        self.creatures.append(living)

    def remove_creature(self, living, killed):
        # type: (Living, bool) -> None
        self.creatures.remove(living)

    def modify_player(self, player):
        # type: (Character) -> None
        pass # No modifications in a normal tile


class TrapTile(MapTile):

    def __init__(self, x, y, mapRegion, description, exitDetails, damage, trap_name):
        # type: (int, int, str, int) -> None
        self.damage = damage
        self.trap_name = trap_name

        super(MapTile, self).__init__(x, y, mapRegion, description, exitDetails)

    def modify_player(self, player):
        # type: (Character) -> None
        player.damage(self.damage, None)


# Example implementation of a trap room that has a specific trap name
class SpikesTrap(TrapTile):
    def __init__(self, x, y, description, damage):
        # type: (int, int, str, int) -> None
        super(TrapTile, self).__init__(x, y, description, damage, "Spikes")