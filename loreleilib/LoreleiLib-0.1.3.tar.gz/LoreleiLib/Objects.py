from Statistics import AttributeSet
from threading import Timer
from enum import Enum
from random import randint
from CombatHelpers import CalculateThreatGain, CalculateExperienceGain, CalculatePhysicalDamage, CalculateNextLevelExperience


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
        self.weight = float
        super(Item, self).__init__(name, description, level)


class Weapon(Item):

    def __init__(self, name, description, level, value, weight, damage, attack_speed, weapon_type, attributes=None):
        # type: (str, str, int, float, float, str, float, int, AttributeSet) -> None
        self.damage = damage # str
        self.attack_speed = attack_speed
        self.weapon_type = weapon_type
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


class Shield(Weapon):

    def __init__(self, name, description, level, value, weight, damage, attack_speed, attributes=None):
        # type: (str, str, int, float, float, str, float, AttributeSet) -> None
        super(Shield, self).__init__(name, description, level, value, weight, damage, attack_speed, WeaponType.Shield, attributes)


class WeaponType(Enum):
    Dagger = 1
    Sword = 2
    Axe = 3
    Mace = 4
    Shield = 5
    Staff = 6
    Two_Handed_Sword = 7
    Two_Handed_Axe = 8
    Two_Handed_Mace = 9
    Bow = 10
    Spear = 11


class WeaponSlot(Enum):
    Main_Hand = 1
    Off_Hand = 2


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
    Light = 1
    Medium = 2
    Heavy = 3
    Plate = 4


class Armor(Item):

    def __init__(self, name, description, level, value, weight, armor_slot, attributes):
        # type: (str, str, int, float, float, EquipmentSlot, AttributeSet) -> None
        self.armor_slot = armor_slot
        self.attributes = attributes
        super(Armor, self).__init__(name, description, level, value, weight)


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
            if item.weapon_type > 5:
                unequipping.append("main_hand")
                unequipping.append("off_hand")
            else:
                if (slot == 1):
                    unequipping.append("main_hand")
                elif item.weapon_type == 5 or slot == 2: #Shield or attempting to dual wield
                    unequipping.append("off_hand")
        if isinstance(item, Armor):
            unequipping.append(item.armor_slot.name.lower())
        return unequipping

    def equip(self, item, slot):
        for item in self.checkSlot(item, slot):
            if item is not None:
                pass


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
            living.damage(CalculatePhysicalDamage(self.attributes, target.attributes), self)

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
