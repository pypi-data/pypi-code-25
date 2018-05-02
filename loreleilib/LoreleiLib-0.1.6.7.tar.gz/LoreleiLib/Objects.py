from LoreleiLib.Statistics import AttributeSet
from collections import OrderedDict
from threading import Timer
from enum import Enum
from random import randint
from LoreleiLib.CombatHelpers import CalculateThreatGain, CalculatePhysicalDamage


class RarityType(Enum):
    Common = 1 # White
    Uncommon = 2 # Green
    Rare = 3 # Blue
    Epic = 4 # Purple
    Legendary = 5 # Orange


class WeaponType(Enum):
    Dagger = 1
    Sword = 2
    Axe = 3
    Mace = 4
    OneHanded = 5 # Used for dual wield checks
    Shield = 6
    TwoHanded = 7
    Staff = 8
    Two_Handed_Sword = 9
    Two_Handed_Axe = 10
    Two_Handed_Mace = 11
    Bow = 12
    Spear = 13


class EquipmentSlot(Enum):
    Main_Hand = 1
    Off_Hand = 2
    Head = 3
    Chest = 4
    Hands = 5
    Legs = 6
    Feet = 7
    Ring1 = 8
    Ring2 = 9
    Necklace = 10
    Bracelets = 11


class ArmorType(Enum):
    Cloth = 1
    Leather = 2
    Chain = 3
    Plate = 4
    Accessory = 5


class Entity(object):

    def __init__(self, name, description, level):
        # type: (str, str, int) -> None
        self.level = level
        self.name = name
        self.description = description
        self.room = None

    def move(self, room):
        # type: (object) -> None
        self.room = room
        room.addEntity(self)


class Item(Entity):

    def __init__(self, name, description, level, value, weight):
        # type: (str, str, int, float, float) -> None
        self.value = value
        self.weight = weight
        super(Item, self).__init__(name, description, level)


class Weapon(Item):

    def __init__(self, name, description, level, value, weight, damage, attack_speed, weapon_type, attributes=None,
                 weaponSlot=EquipmentSlot.Main_Hand):
        # type: (str, str, int, float, float, str, float, WeaponType, AttributeSet, EquipmentSlot) -> None
        self.damage = damage # str
        self.attackSpeed = attack_speed
        self.weaponType = weapon_type
        self.weaponSlot = weaponSlot
        if attributes is None:
            attributes = AttributeSet()
        self.attributes = attributes
        super(Weapon, self).__init__(name, description, level, value, weight)

    def calculate_damage(self):
        pieces = self.damage.split(' ')
        for i in range(0, len(pieces)):
            if 'd' in pieces[i]:
                dice_info = pieces[i].split('d')
                rolls = int(dice_info[0])
                sides = int(dice_info[1])

                total = 0
                for x in range(0, rolls):
                    total += randint(1, sides)

                pieces[i] = total

        formula = ''
        for piece in pieces:
            formula += str(piece)

        print formula
        value = int(eval(formula))
        if value < 1:
            value = 1

        return value

    def getTooltipInfo(self):
        info = OrderedDict()
        info["Description"] = self.description
        if self.level > 1:
            info["Level"] = self.level
        if self.value is not 0:
            info["Value"] = self.value
        info["Weight"] = self.weight
        info["Weapon Type"] = self.weaponType.name.replace('_', ' ')
        if self.damage is not "":
            info["Damage"] = self.damage
        if self.attackSpeed is not 0 and self.attackSpeed is not 0.0:
            info["Attack Speed"] = self.attackSpeed
        info["Bonuses"] = self.attributes.getNonZeroDict()
        return info


class Shield(Weapon):

    def __init__(self, name, description, level, value, weight, damage, attack_speed, attributes=None):
        # type: (str, str, int, float, float, str, float, AttributeSet) -> None
        super(Shield, self).__init__(name, description, level, value, weight, damage, attack_speed, WeaponType.Shield,
                                     attributes, weaponSlot=EquipmentSlot.Off_Hand)


class Armor(Item):

    def __init__(self, name, description, level, value, weight, armorSlot, armorType, attributes):
        # type: (str, str, int, float, float, EquipmentSlot, ArmorType, AttributeSet) -> None
        self.armorSlot = armorSlot
        self.armorType = armorType
        self.attributes = attributes
        super(Armor, self).__init__(name, description, level, value, weight)

    def getTooltipInfo(self):
        info = OrderedDict()
        info["Description"] = self.description
        if self.level > 1:
            info["Level"] = self.level
        if self.value is not 0:
            info["Value"] = self.value
        info["Weight"] = self.weight
        info["Armor Type"] = self.armorType.name.replace('_', ' ')
        info["Armor Slot"] = self.armorSlot.name.replace('_', ' ')
        info["Bonuses"] = self.attributes.getNonZeroDict()
        return info


class ItemDrop(object):

    def __init__(self, item, room, owner):
        # type: (Item, object, Entity) -> None
        self.item = item
        self.room = room
        self.owner = owner
        self.pickup_timer_delay = Timer(15.0, self.remove_owner)
        self.pickup_timer_delay.start()

    def pickup(self, entity):
        if self.can_pickup(entity):
            entity.inventory.append(self.item)
            self.pickup_timer_delay.cancel()

    def can_pickup(self, entity):
        if self.owner is None or self.owner is entity:
            return True
        return False

    def remove_owner(self):
        self.owner = None
        for player in self.room.players:
            player.send("Dropped '{}' is no longer protected".format(self.item.name))


class Equipment(object):

    def __init__(self, owner):
        self.owner = owner
        self.main_hand = None # type: Weapon
        self.off_hand = None # type: Weapon
        self.head = None # type: Armor
        self.chest = None # type: Armor
        self.hands = None # type: Armor
        self.legs = None # type: Armor
        self.feet = None # type: Armor
        self.ring1 = None # type: Armor
        self.ring2 = None # type: Armor
        self.necklace = None # type: Armor
        self.bracelets = None # type: Armor

    def checkSlot(self, item, slot):
        # type: (Item, int) -> list
        unequipping = []
        if isinstance(item, Weapon):
            if item.weaponType.value > WeaponType.TwoHanded.value:
                unequipping.append("main_hand")
                unequipping.append("off_hand")
            else:
                if (slot == 1):
                    unequipping.append("main_hand")
                elif item.weaponType.value == WeaponType.Shield.value or slot == EquipmentSlot.Off_Hand.value: #Shield or attempting to dual wield
                    unequipping.append("off_hand")
        if isinstance(item, Armor):
            unequipping.append(item.armorSlot.name.lower())
        return unequipping

    def equip(self, item, slot=None):
        # Returns item(s) previously equipped
        # type: (Item, EquipmentSlot) -> Item
        if item is None:
            return []
        unequipped = []
        for itemSlot in self.checkSlot(item, slot):
            unequipped.append(self.unequip(itemSlot))

        setattr(self, slot.name.lower(), item)
        self.updateOwner()

        return unequipped

    def unequip(self, slot):
        item = getattr(self, slot, None)
        if item is not None:
            setattr(self, slot, None)
            self.updateOwner()
            return item
        return None

    def updateOwner(self):
        if self.owner is not None:
            if hasattr(self.owner, "buildStats"):
                self.owner.buildStats()

    def getAllItems(self):
        equipment = OrderedDict()
        equipment[EquipmentSlot.Main_Hand] = self.main_hand
        equipment[EquipmentSlot.Off_Hand] = self.off_hand
        equipment[EquipmentSlot.Head] = self.head
        equipment[EquipmentSlot.Chest] = self.chest
        equipment[EquipmentSlot.Hands] = self.hands
        equipment[EquipmentSlot.Legs] = self.legs
        equipment[EquipmentSlot.Feet] = self.feet
        equipment[EquipmentSlot.Ring1] = self.ring1
        equipment[EquipmentSlot.Ring2] = self.ring2
        equipment[EquipmentSlot.Necklace] = self.necklace
        equipment[EquipmentSlot.Bracelets] = self.bracelets
        return equipment


class Living(Entity):

    def __init__(self, name, description, level, attributes):
        # type: (str, str, int, AttributeSet) -> None
        self.level = level # type: int
        if attributes is None:
            attributes = AttributeSet()
        self.attributes = attributes # type: AttributeSet
        super(Living, self).__init__(name, description, level)

    def isAlive(self):
        # type: () -> bool
        return self.attributes.health > 0

    def isDead(self):
        return not self.isAlive()

    def attack(self, target):
        # type: (Living) -> None
        if isinstance(target, Living):
            living = target
            # TODO : Calculate damage from equipment or damage moves
            living.damage(CalculatePhysicalDamage(4, self.attributes, target.attributes), self)

    def damage(self, amount, attacker):
        # type: (int, Living) -> None
        self.attributes.health -= amount
        if not self.isAlive():
            # Give damager exp
            pass


class Creature(Living):

    def __init__(self, name, description, level, attributes):
        # type: (str, str, int, AttributeSet) -> None
        self.target = None # type: Living
        self.threat_table = {} # type: dict
        super(Creature, self).__init__(name, description, level, attributes)

    # Do server tick
    def tick(self):
        if self.target is not None:
            pass

    def damage(self, amount, attacker):
        # type: (int, Living) -> None
        self.threat_table[attacker.name] = self.threat_table.get(attacker.name, 0.0) + \
                                           CalculateThreatGain(amount, attacker.attributes)
        super(Creature, self).damage(amount, attacker)


class Monster(Creature):

    def __init__(self, name, description, level, attributes):
        # type: (str, str, int, AttributeSet) -> None
        super(Monster, self).__init__(name, description, level, attributes)

    def tick(self):
        pass
