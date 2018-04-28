from enum import Enum
from LoreleiLib.Helpers import firstLetterLowercase


# If you add a value to these enums
# Add the matching camel cased name to Attributes for type intellisense
class Vital(Enum):
    Health = 1
    Mana = 2
    Stamina = 3


class Attribute(Enum):
    Strength = 1
    Constitution = 2
    Dexterity = 3
    Agility = 4
    Wisdom = 5
    Intelligence = 6
    Charisma = 7


class Statistic(Enum):
    Attack = 1
    MagicAttack = 2
    Defense = 3
    MagicDefense = 4
    Dodge = 5
    MagicDodge = 6
    Critical = 7
    Threat = 8


class AttributeSet(object):

    def __init__(self, **kwargs):
        # Vitals
        self.health = 0
        self.maxHealth = 0
        self.mana = 0
        self.maxMana = 0
        self.stamina = 0
        self.maxStamina = 0

        # Attributes
        self.strength = 0
        self.constitution = 0
        self.dexterity = 0
        self.agility = 0
        self.wisdom = 0
        self.intelligence = 0
        self.charisma = 0

        # Stats
        self.attack = 0
        self.magicAttack = 0
        self.defense = 0
        self.magicDefense = 0
        self.dodge = 0
        self.magicDodge = 0
        self.critical = 0
        self.threat = 0

        allowed = []
        for vital in Vital:
            allowed.append(vital.name)
        for attribute in Attribute:
            allowed.append(attribute.name)
        for stat in Statistic:
            allowed.append(stat.name)

        for key, value in kwargs.iteritems():
            if key in allowed:
                self.__setattr__(firstLetterLowercase(key), value)
