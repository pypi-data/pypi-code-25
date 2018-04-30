from typing import List

from enum import Enum


class RightAngleTrigFunction(Enum):
    Sin = 1
    Cos = 2
    Tan = 3
    Sec = 4
    Csc = 5
    Cot = 6


class RightAngleTrigSide(Enum):
    Nil = 0
    Opposite = 1
    Adjacent = 2
    Hypotenuse = 3


class AngleType(Enum):
    Degrees = 0
    Radians = 1


deg: List[str] = ["0", "30", "45", "60", "90",
                  "120", "135", "150", "180",
                  "210", "225", "240", "270",
                  "300", "315", "330", "360"]

rad: List[str] = ["0", "&pi;/6", "&pi;/4", "&pi;/3", "&pi;/2",
                  "2&pi;/3", "3&pi;/4", "5&pi;/6", "&pi;",
                  "7&pi;/6", "5&pi;/4", "4&pi;/3", "3&pi;/2",
                  "5&pi;/3", "7&pi;/4", "11&pi;/6", "2&pi;"]