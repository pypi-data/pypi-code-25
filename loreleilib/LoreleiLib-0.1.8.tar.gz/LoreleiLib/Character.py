from LoreleiLib.Statistics import AttributeSet
from LoreleiLib.Objects import Living, Equipment, ArmorType, WeaponType, Item, EquipmentSlot, Weapon
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

    def __init__(self, name, character_race, character_class, level=1, experience=0):
        self.name = name # type: str
        self.character_race = character_race # type: CharacterRace
        self.character_class = character_class # type: CharacterClass
        self.inventory = [] # type: list

        super(Character, self).__init__(name, "A random traveller", level, AttributeSet())
        self.experience = experience # type: int
        self.nextLevel = CalculateNextLevelExperience(level)# type: int
        self.equipment = Equipment(self) # type: Equipment

        # Core + Equipment = Stats used for battle
        self.coreAttributes = AttributeSet(Strength=0, Constitution=0, Dexterity=0, Agility=0, Wisdom=0, Intelligence=0, Charisma=0) # type: AttributeSet
        self.buffs = [] # type: list

    def buildStats(self):
        self.attributes = AttributeSet()
        self.buildCoreAttributes()
        self.buildEquipmentAttributes()
        self.makeStatistics()

    def buildCoreAttributes(self):
        # Use alloted attributes
        for key, value in self.coreAttributes.__dict__.iteritems():
            setattr(self.attributes, key, value)

        # Add race attributes
        if self.character_race is not None:
            for key, value in self.character_race.attributes.__dict__.iteritems():
                setattr(self.attributes, key, value)

        # Add starting class attributes
        if self.character_class is not None:
            for key, value in self.character_class.startingAttributes.__dict__.iteritems():
                setattr(self.attributes, key, getattr(self.attributes, key) + value)

    def buildEquipmentAttributes(self):
        for key, value in self.equipment.__dict__.iteritems():
            if isinstance(value, Weapon):
                if key == "main_hand":
                    self.attributes.attackSpeed += value.attackSpeed
                elif key == "off_hand":
                    self.attributes.attackSpeed += (value.attackSpeed / 2)
            if key != "owner" and value is not None:
                for key2, value2 in value.attributes.__dict__.iteritems():
                    setattr(self.attributes, key2, getattr(self.attributes, key2) + value2)

    def makeStatistics(self):
        self.attributes.maxHealth += 10 + self.attributes.strength + self.attributes.constitution * 3
        self.attributes.maxMana += 5 + (self.attributes.intelligence +  self.attributes.wisdom * 3) / 2
        self.attributes.maxStamina += 5 + (self.attributes.strength * 2 + self.attributes.constitution * 2) / 2

        self.attributes.attack += int(self.attributes.strength * 1.5)
        self.attributes.defense += self.attributes.constitution * 2
        self.attributes.accuracy += 80 + self.attributes.dexterity / 3
        self.attributes.dodge += 1 + (self.attributes.agility-5) / 5
        self.attributes.critical += 1 + ((self.attributes.agility-5) / 10) + ((self.attributes.dexterity-5) / 10) - int(self.level / 10)
        self.attributes.attackSpeed -= 0.0 # - 0 TODO: Make formula

        self.attributes.magicAttack += int(self.attributes.intelligence * 1.5)
        self.attributes.magicDefense += self.attributes.wisdom * 2
        self.attributes.magicAccuracy += 80 + self.attributes.intelligence / 3
        self.attributes.magicDodge += 1 # - 0 TODO: Make formula
        self.attributes.magicCritical += (self.attributes.intelligence + self.attributes.wisdom) / 10 - int(self.level / 10)
        self.attributes.castSpeed = 1.0 # - 0 TODO: Make formula

        threatValue = int(self.attributes.constitution / 10 - 1)
        if threatValue < 0:
            threatValue = 0
        self.attributes.threat += threatValue

    def changeRace(self, race):
        # type: (CharacterRace) -> None
        self.character_race = race

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
            super(Character, self).damage(amount, attacker)

    def giveItem(self, item, announce=True):
        if item is not None:
            self.inventory.append(item)

    def equip(self, item, slot):
        unequipped = self.equipment.equip(item, slot)
        for item in unequipped:
            self.inventory.append(item)

    def unequip(self, slot):
        item = self.equipment.unequip(slot)
        if item is not None:
            self.inventory.append(item)