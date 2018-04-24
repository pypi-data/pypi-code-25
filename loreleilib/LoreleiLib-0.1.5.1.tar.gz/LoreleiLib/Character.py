from Statistics import AttributeSet
from Objects import Living, Equipment, ArmorType, WeaponType
from CombatHelpers import CalculateNextLevelExperience, CalculateExperienceGain


class CharacterClass(object):

    def __init__(self, name, description, skillList, weaponList, armorList, starterSet=None):
        # type: (str, str, dict, list, list, list) -> None
        self.name = name # type: str
        self.description = description # type: str
        self.skillList = skillList # type: dict<int, list>
        self.weapons = weaponList # type: list<WeaponType>
        self.armor = armorList # type: list<ArmorType>
        self.starterSet = starterSet # type: list<str>


class CharacterRace(object):

    def __init__(self, name, description, attributes):
        # type: (str, str, AttributeSet) -> None
        self.name = name # type: str
        self.description = description # type: str
        self.attributes = attributes # type: AttributeSet


class Character(Living):

    def __init__(self, name, character_race, character_class):
        self.name = name # type: str
        self.character_race = character_race # type: CharacterRace
        self.character_class = character_class # type: CharacterClass
        self.inventory = [] # type: list

        super(Character, self).__init__(name, "A lonely traveller", 999, None)
        self.experience = 0 # type: int
        self.nextLevel = 1000 # type: int
        self.equipment = Equipment(self) # type: Equipment

        # Core + Equipment = Stats used for battle
        self.coreAttributes = AttributeSet(Strength=10, Constitution=10, Dexterity=10, Agility=10, Wisdom=10, Intelligence=10, Charisma=10) # type: AttributeSet
        self.buffs = [] # type: list

    def buildStats(self):
        self.buildCoreAttributes()
        # self.buildEquipmentAttributes()

    def buildCoreAttributes(self):
        for key, value in self.coreAttributes.__dict__.iteritems():
            setattr(self.attributes, key, value)

        if self.character_race is not None:
            for key, value in self.character_race.attributes.__dict__.iteritems():
                setattr(self.attributes, key, getattr(self.attributes, key) + value)

    def buildEquipmentAttributes(self):
        for key, value in self.equipment.__dict__.iteritems():
            setattr(self.attributes, key, getattr(self.attributes, key) + getattr(value.attributes, key))

    def load(self):
        self.loadCoreAttributes()
        self.loadEquipment()
        self.buildStats()

    def loadCoreAttributes(self):
        pass

    def loadEquipment(self):
        pass

    def giveReward(self, target):
        expGain = CalculateExperienceGain(target.level, self.level)
        if (expGain > 0):
            self.experience += expGain
            if self.experience > self.nextLevel:
                self.levelUp()

    def levelUp(self):
        self.level += 1
        self.experience -= self.nextLevel
        self.nextLevel = CalculateNextLevelExperience(self.level)

    def damage(self, amount, attacker):
        if attacker is not None:
            self.send('{} dealt {} damage to you'.format(attacker.name, amount))
            super(Living, self).damage(amount, attacker)

    def send(self, message):
        raise NotImplementedError