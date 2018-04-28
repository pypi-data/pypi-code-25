from LoreleiClient.UIObjects.Input import Box, Label, Image
from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.Objects import EquipmentSlot, Weapon, Shield


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
        self.add_ui_object(Box(x, y, 300, 374, 3, "Equipment"))

        y += 10
        for slot, item in self.character.equipment.getAllItems().iteritems():
            slotname = slot.name.lower()
            itemname = "<empty>"

            if slot == EquipmentSlot.Off_Hand:
                if isinstance(item, Weapon) and not isinstance(item, Shield):
                    slotname = EquipmentSlot.Main_Hand.name.lower()

            if item is not None:
                itemname = item.name

            # Draw Slot Image
            if self.imageManager.Images.has_key(slotname):
                self.add_ui_object(Image(x + 10, y, slotname))
            # Draw Text
            self.add_ui_object(Label(x+52, y + 7, itemname, fontSize=18))
            y += spacing

    def update(self):
        self.removeAll()
        self.setup()