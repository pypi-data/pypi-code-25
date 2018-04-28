from LoreleiLib.Statistics import AttributeSet
from LoreleiLib.Objects import Living, Equipment, ArmorType, WeaponType, Item, EquipmentSlot
from LoreleiLib.CombatHelpers import CalculateNextLevelExperience, CalculateExperienceGain


class CharacterClass(object):

    def __init__(self, name, description, skillList, weaponList, armorList, starterSet=None,
                 startingAttributes=AttributeSet(Strength=10, Constitution=10, Dexterity=10, Agility=10, Intelligence=10, Wisdom=10, Charisma=10)):
        # type: (str, str, dict, list, list, list, AttributeSet, dict) -> None
        self.name = name # type: str
        self.description = description # type: str
        self.skillList = skillList # type: dict<int, list>
        self.weapons = weaponList # type: list<WeaponType>
        self.armor = armorList # type: list<ArmorType>
        self.startingAttributes = startingAttributes # type: AttributeSet
        self.starterSet = starterSet # type: list<str>
        self.starterEquipment = [] # type: dict<EquipmentSlot, Item>

    def getFullDescription(self):
        descrip = self.description + "\n\n"
        descrip += "Weapons : "
        for weaponType in self.weapons:
            descrip += weaponType.name.replace("_", " ") + ", "
        descrip = descrip[:-2]
        descrip += "\n\n"
        descrip += "Armor : "
        for armorType in self.armor:
            descrip += armorType.name.replace("_", " ") + ", "
        descrip = descrip[:-2]
        return descrip


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

        super(Character, self).__init__(name, "", 1, AttributeSet())
        self.experience = 0 # type: int
        self.nextLevel = 1000 # type: int
        self.equipment = Equipment(self) # type: Equipment

        # Core + Equipment = Stats used for battle
        self.coreAttributes = AttributeSet(Strength=0, Constitution=0, Dexterity=0, Agility=0, Wisdom=0, Intelligence=0, Charisma=0) # type: AttributeSet
        self.buffs = [] # type: list

    def buildStats(self):
        self.buildCoreAttributes()
        self.buildEquipmentAttributes()

    def buildCoreAttributes(self):
        for key, value in self.coreAttributes.__dict__.iteritems():
            setattr(self.attributes, key, value)

        if self.character_class is not None:
            for key, value in self.character_class.startingAttributes.__dict__.iteritems():
                setattr(self.attributes, key, getattr(self.attributes, key) + value)

    def changeRace(self, race):
        # type: (CharacterRace) -> None
        self.character_race = race
        self.coreAttributes = race.attributes

    def buildEquipmentAttributes(self):
        for key, value in self.equipment.__dict__.iteritems():
            if key != "owner" and value is not None:
                for key2, value2 in value.attributes.__dict__.iteritems():
                    setattr(self.attributes, key2, getattr(self.attributes, key2) + value2)

    def load(self):
        self.loadCoreAttributes()
        self.loadEquipment()
        self.buildStats()

    def loadCoreAttributes(self):
        # Load attributes from database
        pass

    def loadEquipment(self):
        # Load equipment from database
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
            super(Character, self).damage(amount, attacker)

    def send(self, message):
        raise NotImplementedError

    def giveItem(self, item, announce=True):
        if item is not None:
            self.inventory.append(item)
            if announce:
                self.send("You have received a(n) {}".format(item.name))

    def equip(self, item, slot):
        unequipped = self.equipment.equip(item, slot)
        for item in unequipped:
            self.inventory.append(item)

    def unequip(self, slot):
        item = self.equipment.unequip(slot)
        if item is not None:
            self.inventory.append(item)