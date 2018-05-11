from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.UIObjects.Input import Box, LabelRightAligned, Label


class StatisticsComponent(Component):

    def __init__(self, x, y, character):
        self.character = character
        super(StatisticsComponent, self).__init__(x, y, self.setup)

    def setup(self):
        self.add_ui_object(Box(self.x, self.y, 886, 200, 3, "Statistics", fontSize=24))
        spacing = 28
        labelX = self.x + 64
        intValueX = labelX + 88

        viewDict = self.character.attributes.getViewDict()
        for section, valueDict in viewDict.iteritems():
            y = self.y + 4
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 28, section, fontSize=24, underlined=True))
            y += spacing
            for key, value in valueDict.iteritems():
                self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, key + " : ", fontSize=24))
                self.add_ui_object(Label(labelX + 80, y, value, fontSize=24))
                y += spacing
            labelX += 200


    def updateComponent(self):
        self.removeAll()
        self.setup()