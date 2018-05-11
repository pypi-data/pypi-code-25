from LoreleiClient.Views.Modules.Common import Component
from LoreleiClient.UIObjects.Input import Box, ParagraphBox, ObservableValue
from LoreleiLib.Packets.Game.Room import RoomDetails


class RoomModule(Component):

    def __init__(self, x, y, connection):
        self.connection = connection
        self.roomDescription = ObservableValue("")
        super(RoomModule, self).__init__(x, y, self.makeView)

    def makeView(self):
        self.add_ui_object(ParagraphBox(self.x, self.y, 468, 300, 3, "Room Info", self.roomDescription, fontSize=24))

    def handleData(self, data):
        if isinstance(data, RoomDetails):
            self.handleRoomDetails(data)

    def handleRoomDetails(self, data):
        self.roomDescription.setValue(data.description)