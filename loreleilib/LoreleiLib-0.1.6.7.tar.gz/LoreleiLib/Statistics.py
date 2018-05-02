from enum import Enum
from LoreleiLib.Helpers import firstLetterLowercase
from collections import OrderedDict


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
    Accuracy = 5
    MagicAccuracy = 6
    Dodge = 7
    MagicDodge = 8
    Critical = 9
    Threat = 10
    AttackSpeed = 11
    CastSpeed = 12


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
        self.accuracy = 0
        self.magicAccuracy = 0
        self.dodge = 0
        self.magicDodge = 0
        self.critical = 0
        self.magicCritical = 0
        self.threat = 0
        self.attackSpeed = 0.0
        self.castSpeed = 0.0

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

    def getDict(self):
        attributeDict = OrderedDict()
        # Vitals
        attributeDict["Max Health"] = self.maxHealth
        attributeDict["Max Mana"] = self.maxMana
        attributeDict["Max Stamina"] = self.maxStamina

        # Physical
        attributeDict["P. Attack"] = self.attack
        attributeDict["P. Defense"] = self.defense
        attributeDict["Accuracy"] = self.accuracy
        attributeDict["Dodge"] = self.dodge
        attributeDict["Critical"] = self.critical
        attributeDict["Attack Speed"] = self.attackSpeed

        # Magical
        attributeDict["M. Attack"] = self.magicAttack
        attributeDict["M. Defense"] = self.magicDefense
        attributeDict["M. Accuracy"] = self.magicAccuracy
        attributeDict["Magic Dodge"] = self.magicDodge
        attributeDict["Magic Critical"] = self.magicCritical
        attributeDict["Cast Speed"] = self.castSpeed

        # Other
        attributeDict["Threat"] = self.threat
        return attributeDict

    def getViewDict(self):
        attributeDict = OrderedDict()
        # Vitals
        attributeDict["Vitals"] = OrderedDict()
        attributeDict["Vitals"]["Max Health"] = self.maxHealth
        attributeDict["Vitals"]["Max Mana"] = self.maxMana
        attributeDict["Vitals"]["Max Stamina"] = self.maxStamina

        # Physical
        attributeDict["Physical"] = OrderedDict()
        attributeDict["Physical"]["P. Attack"] = self.attack
        attributeDict["Physical"]["P. Defense"] = self.defense
        attributeDict["Physical"]["Accuracy"] = self.accuracy
        attributeDict["Physical"]["Dodge"] = self.dodge
        attributeDict["Physical"]["Critical"] = self.critical
        attributeDict["Physical"]["Attack Speed"] = self.attackSpeed

        # Magical
        attributeDict["Magical"] = OrderedDict()
        attributeDict["Magical"]["M. Attack"] = self.magicAttack
        attributeDict["Magical"]["M. Defense"] = self.magicDefense
        attributeDict["Magical"]["M. Accuracy"] = self.magicAccuracy
        attributeDict["Magical"]["M. Dodge"] = self.magicDodge
        attributeDict["Magical"]["M. Critical"] = self.magicCritical
        attributeDict["Magical"]["Cast Speed"] = self.castSpeed

        # Other
        attributeDict["Other"] = OrderedDict()
        attributeDict["Other"]["Enmity"] = self.threat
        return attributeDict

    def getNonZeroDict(self):
        attributeDict = OrderedDict()
        if self.maxHealth is not 0 and self.maxHealth is not None:
            attributeDict["Max Health"] = self.maxHealth
        if self.maxMana is not 0 and self.maxMana is not None:
            attributeDict["Max Mana"] = self.maxMana
        if self.maxStamina is not 0 and self.maxStamina is not None:
            attributeDict["Max Stamina"] = self.maxStamina

        if self.attack is not 0 and self.attack is not None:
            attributeDict["P. Attack"] = self.attack
        if self.defense is not 0 and self.defense is not None:
            attributeDict["P. Defense"] = self.defense
        if self.accuracy is not 0 and self.accuracy is not None:
            attributeDict["Accuracy"] = self.accuracy
        if self.dodge is not 0 and self.dodge is not None:
            attributeDict["Dodge"] = self.dodge
        if self.critical is not 0 and self.critical is not None:
            attributeDict["Critical"] = self.critical
        if int(self.attackSpeed) is not 0 and self.attackSpeed is not None and self.attackSpeed is not 0.0:
            attributeDict["Attack Speed"] = self.attackSpeed

        if self.magicAttack is not 0 and self.magicAttack is not None:
            attributeDict["M. Attack"] = self.magicAttack
        if self.magicDefense is not 0 and self.magicDefense is not None:
            attributeDict["M. Defense"] = self.magicDefense
        if self.magicDodge is not 0 and self.magicDodge is not None:
            attributeDict["M. Dodge"] = self.magicDodge
        if self.magicCritical is not 0 and self.magicCritical is not None:
            attributeDict["M. Critical"] = self.magicCritical
        if int(self.castSpeed) is not 0 and self.castSpeed is not None and self.castSpeed is not 0.0:
            attributeDict["Cast Speed"] = self.castSpeed

        if self.threat is not 0 and self.threat is not None:
            attributeDict["Enmity"] = self.threat

        return attributeDict

    def setValues(self, otherSet):
        # type: (AttributeSet) -> AttributeSet
        for key, value in vars(otherSet):
            self.__setattr__(key, value)
