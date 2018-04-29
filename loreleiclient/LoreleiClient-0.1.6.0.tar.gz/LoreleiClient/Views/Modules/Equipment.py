from LoreleiClient.UIObjects.Input import Box, Label, Image, ParagraphBox, ObservableValue
from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.Objects import EquipmentSlot, Weapon, Shield
from LoreleiLib.StringHelpers import wrap_multi_line
from collections import OrderedDict
import pygame as pg


class EquipmentHoverover:

    def __init__(self, x, y, item, fontSize=18):
        self.x = x
        self.y = y
        self.font = pg.font.Font(None, fontSize)
        self.fontSize = fontSize
        self.item = item
        self.stats = self.item.getTooltipInfo()
        self.box = None
        self.observable = None
        self.setup()

    def setup(self):
        size = [50, 0]
        totalText = ""
        for key, value in self.stats.iteritems():
            if isinstance(value, OrderedDict):
                for key2, value2 in value.iteritems():
                    nextText = "\t" + key2 + " : " + str(value2) + "\n"
                    nextSize = self.font.size(nextText)
                    if nextSize[0] > size[0]:
                        size[0] = nextSize[0]
                    size[1] += self.fontSize
                    totalText += nextText
            else:
                nextText = key + " : " + str(value) + "\n"
                nextSize = self.font.size(nextText)
                if nextSize[0] > size[0]:
                    size[0] = nextSize[0]
                size[1] += self.fontSize
                totalText += nextText

        if size[0] > 200:
            size[0] = 200
        size[1] = (self.fontSize * len(wrap_multi_line(totalText, self.font, size[0]))) + 16

        self.observable = ObservableValue(totalText)
        self.box = ParagraphBox(self.x, self.y, size[0], size[1], 3, self.item.name, self.observable, self.fontSize)

    def move(self, x, y):
        self.box.rect.x = x
        self.box.rect.y = y

    def draw(self, screen):
        self.box.draw(screen)


class EquipmentItemComponent:

    def __init__(self, x, y, slot, item):
        self.x = x
        self.y = y
        self.slot = slot
        self.item = item
        self.label = None
        self.image = None
        self.hover = False
        self.hoverRect = None
        self.hoverover = None
        self.setup()

    def setup(self):
        slotname = self.slot.name.lower()
        itemname = "<empty>"

        if self.slot == EquipmentSlot.Off_Hand:
            if isinstance(self.item, Weapon) and not isinstance(self.item, Shield):
                slotname = EquipmentSlot.Main_Hand.name.lower()

        if self.item is not None:
            itemname = self.item.name

        # Draw Slot Image
        self.image = Image(self.x + 10, self.y, slotname)
        # Draw Text
        self.label = Label(self.x + 52, self.y + 7, itemname, fontSize=18)

        if self.item is not None:
            self.hoverRect = pg.Rect(self.x, self.y, (self.label.rect.x + self.label.rect.w - self.x) + 32, 32)
            self.hoverover = EquipmentHoverover(self.x, self.y, self.item)

    def draw(self, screen):
        self.image.draw(screen)
        self.label.draw(screen)

        if self.hover:
            # draw the hover over
            if self.hoverover is not None:
                self.hoverover.draw(screen)

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.hoverRect is not None:
                if self.hoverRect.collidepoint(pg.mouse.get_pos()):
                    pos = pg.mouse.get_pos()
                    self.hoverover.move(pos[0]+20, pos[1]+20)
                    self.hover = True
                else:
                    self.hover = False


class EquipmentComponent(Component):

    def __init__(self, x, y, character, editable=False):
        self.character = character
        self.imageManager = ImageManager()
        self.editable = editable # If we want the player to be able to change equipment in this view
        super(EquipmentComponent, self).__init__(x, y, self.setup)

    def setup(self):
        spacing = 32
        x = self.x
        y = self.y
        self.add_ui_object(Box(x, y, 300, 374, 3, "Equipment")) # 32 * 11 = 352

        items = []

        y += 10
        for slot, item in self.character.equipment.getAllItems().iteritems():
            items.append(EquipmentItemComponent(x, y, slot, item))
            y += spacing

        for item in reversed(items):
            self.add_ui_object(item)

    def updateComponent(self):
        self.removeAll()
        self.setup()