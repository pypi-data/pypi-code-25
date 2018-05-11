from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.UIObjects.Input import Box, Label, LabelRightAligned, ObservableValue, IntValueBox


class AttributeComponent(Component):

    def __init__(self, x, y, character):
        self.character = character
        self.strength = ObservableValue(self.character.attributes.strength)
        self.constitution = ObservableValue(self.character.attributes.constitution)
        self.dexterity = ObservableValue(self.character.attributes.dexterity)
        self.agility = ObservableValue(self.character.attributes.agility)
        self.wisdom = ObservableValue(self.character.attributes.wisdom)
        self.intelligence = ObservableValue(self.character.attributes.intelligence)
        self.charisma = ObservableValue(self.character.attributes.charisma)
        super(AttributeComponent, self).__init__(x, y, self.setup)

    def setup(self):
        labelX = self.x + 40
        intValueX = labelX + 88
        spacing = 32
        y = self.y
        self.add_ui_object(Box(self.x, y, 180, 240, 3, "Attributes", fontSize=24))
        y += 10
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Strength :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26, self.strength, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Constitution :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.constitution, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Dexterity :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.dexterity, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Agility :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.agility, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Wisdom :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.wisdom, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Intelligence :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.intelligence, fontSize=24))
        y += spacing
        self.add_ui_object(LabelRightAligned(labelX, y, 80, 26, "Charisma :", fontSize=24))
        self.add_ui_object(IntValueBox(intValueX, y, 30, 26,  self.charisma, fontSize=24))

    def update(self):
        self.strength.setValue(self.character.attributes.strength)
        self.constitution.setValue(self.character.attributes.constitution)
        self.dexterity.setValue(self.character.attributes.dexterity)
        self.agility.setValue(self.character.attributes.agility)
        self.wisdom.setValue(self.character.attributes.wisdom)
        self.intelligence.setValue(self.character.attributes.intelligence)
        self.charisma.setValue(self.character.attributes.charisma)