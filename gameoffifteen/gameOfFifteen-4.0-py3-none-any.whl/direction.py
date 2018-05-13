from random import randint
from enum import Enum

class Direction(Enum):
    """Defines enumeration for move directions."""
    Left = 1
    Right = 2
    Up = 3
    Down = 4
    
    def getRandomDirection():
        """Gets a random direction."""
        direction = randint(1, 4)
        if direction == 1:
            return Direction.Left
        if direction == 2:
            return Direction.Right
        if direction == 3:
            return Direction.Up
        if direction == 4:
            return Direction.Down
        raise IndexError
    
